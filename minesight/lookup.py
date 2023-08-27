import asyncio
import json
import re
import bs4
import httpx
from rich.progress import Progress
from rich import print
from jsonpath_ng import parse
from rich.console import Console
from rich.tree import Tree
from minesight.utils import parse_date_with_formats
import pkg_resources

NEXT_JSON_SCRIPT_SELECTOR = "script#__NEXT_DATA__"

def check_profile_exists(type, value, response):
    checks = {
        "matchURL": lambda: re.search(value, str(response.url)) is not None,
        "status": lambda: str(response.status_code) == value,
        "matchBodyError": lambda: not re.search(value, response.text),
        "jsonEmptyError": lambda: response.json() not in [{}, []]
    }
    return checks.get(type, lambda: False)()

def clean_html_text(text):
    return re.sub(' +', ' ', text.replace("\n", " ").strip())

def collect_field(response_type, field, response):
    if response_type == "html":
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        elements = soup.select(field)
        cleaned_texts = [clean_html_text(el.get_text(separator=' ')) for el in elements]
        return cleaned_texts if len(cleaned_texts) > 1 else (cleaned_texts[0] if cleaned_texts else None)

    json_data = get_json_data(response, response_type)
    jsonpath_expr = parse(field)
    matches = [match.value for match in jsonpath_expr.find(json_data)]
    return matches[0] if matches else None

def get_json_data(response, response_type):
    if response_type == "json":
        return response.json()
    if response_type == "nextJson":
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        script = soup.select_one(NEXT_JSON_SCRIPT_SELECTOR)
        if script:
            return json.loads(script.string).get("props", {}).get("pageProps", {})
    return {}

async def fetch_site_data(site, inputs, debug=False):
    fields = []
    profileUrl = None

    async def do_request(request):
        nonlocal profileUrl

        if request.get("isProfileUrl"):
            profileUrl = request["requestUrl"].format(**inputs)
        
        headers = request.get("headers", {})
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(request["requestUrl"].format(**inputs), follow_redirects=True, headers=headers)

        if check_profile_exists(request.get("profileExistsType"), request.get("profileExistsValue"), response):
            sub_request = request.get("subRequest", None)
            if sub_request:
                jsonPathExpr = parse(request["passToSubRequest"])
                pass_to_sub_request = [match.value for match in jsonPathExpr.find(response.json())]
                if pass_to_sub_request:
                    inputs["subParameter"] = pass_to_sub_request[0]
                    await do_request(sub_request)

            for field in request["fields"]:
                field_value = collect_field(request.get("responseType"), field["selectorOrPath"], response)
                if field_value is None:
                    continue
                
                field_data = {
                    "name": field["name"],
                    "value": field_value,
                    "note": field.get("note", ""),
                    "type": field.get("type", None),
                    "dateFormats": field.get("dateFormats", None)
                }

                content_match = field.get("contentMatch", None)
                if content_match and isinstance(field_value, str) and re.search(content_match, field_value):
                    field_data["value"] = re.search(content_match, field_value).group(1)
                
                fields.append(field_data)

    try:
        for request in site.get("requests", []):
            await do_request(request)

        if fields:
            return {
                "name": site.get("name"),
                "profileUrl": profileUrl,
                "fields": fields
            }
    except Exception as e:
        if debug:
            raise e

async def run(username: str, uuid: str, dash_uuid: str, debug: bool):
    inputs = {
        "username": username.lower(),
        "uuid": uuid,
        "dash_uuid": dash_uuid,
    }

    data_path = pkg_resources.resource_filename(__name__, "sites.json")
    with open(data_path, "r") as f:
        sites = json.load(f)

    print(f":mag: Fetching data for [cyan bold]{username}[/cyan bold] ([bold]{uuid}[/bold])")

    results = await fetch_data_for_sites(sites, inputs, debug)

    display_results(results, len(sites), username)


async def fetch_data_for_sites(sites, inputs, debug):
    tasks = [fetch_site_data(site, inputs, debug) for site in sites]
    results = []

    with Progress() as progress:
        task_progress = progress.add_task("[cyan]Fetching data...", total=len(tasks))
        for future in asyncio.as_completed(tasks):
            result = await future
            if result:
                results.append(result)
            progress.update(task_progress, advance=1)

    return results


def display_results(results, total_sites, username):
    console = Console()
    tree = Tree(f"[bold]Results for [cyan]{username}[/cyan] on [cyan]{len(results)}[/cyan] sites[/bold] (out of [cyan]{total_sites}[/cyan] checked)")
    last_activity = {"server": None, "date": None}

    for server in results:
        server_node = tree.add(f"[bold yellow1]{server['name']}[/bold yellow1]\n[dim white]{server['profileUrl']}[/dim white]")
        for field in server["fields"]:
            process_and_add_field_to_node(field, server_node, last_activity, server)

    console.print(tree)

    if last_activity["date"]:
        print(f"\n:alarm_clock: Last activity: [bold]{last_activity['date']}[/bold] on [bold]{last_activity['server']}[/bold]")


def process_and_add_field_to_node(field, server_node, last_activity, server):
    field_name, field_value = field["name"], field["value"]

    if field.get("type") == "date":
        field_value = process_date_field(field_value, field.get("dateFormats"), last_activity, server["name"])

    field_value = format_field_value(field_value)

    note = field.get("note", "")
    field_label = f"[bold]{field_name}[/bold] {f'[magenta]{note}[/magenta]' if note else ''}"

    field_node = server_node.add(field_label)
    if isinstance(field_value, list):
        for item in field_value:
            item_value = format_field_value(item)
            field_node.add(item_value)
    else:
        field_node.add(field_value)


def process_date_field(value, date_formats, last_activity, server_name):
    parsed_date = parse_date_with_formats(str(value), date_formats)
    if parsed_date:
        if not last_activity["date"] or parsed_date > last_activity["date"]:
            last_activity["date"] = parsed_date
            last_activity["server"] = server_name
        return f"[dark_orange]{parsed_date}[/dark_orange]"
    return f"{value} [dark_orange](!)[/dark_orange]"

def format_field_value(value):
    if isinstance(value, bool):
        return "[green]Yes[/green]" if value else "[red]No[/red]"
    if isinstance(value, int):
        return f"[yellow]{value}[/yellow]"
    if isinstance(value, dict):
        return ', '.join(f"[deep_sky_blue1]{k}[/deep_sky_blue1]: {v}" for k, v in value.items() if v)
    return value
