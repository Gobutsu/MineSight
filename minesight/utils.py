from datetime import datetime, timedelta
import locale

def parse_relative_date(date_str):
    try:
        if "il y a" in date_str.lower():
            _, num, unit = date_str.split(" ")[2:5]
        else:
            num, unit = date_str.split(" ")[:2]
        num = int(num)

        units_mapping = {
            ("hour", "hours", "heure", "heures"): "hours",
            ("day", "days", "jour", "jours"): "days",
            ("week", "weeks", "semaine", "semaines"): "weeks",
            ("month", "months", "mois"): "months",
            ("year", "years", "an", "ans", "année", "années"): "years"
        }

        for key, value in units_mapping.items():
            if unit in key:
                if value == "months":
                    current_date = datetime.now()
                    month = current_date.month - num
                    year = current_date.year
                    while month <= 0:
                        month += 12
                        year -= 1
                    return current_date.replace(year=year, month=month)
                elif value == "years":
                    return datetime.now() - timedelta(days=num*365)
                else:
                    return datetime.now() - timedelta(**{value: num})
        return None
    except Exception as e:
        print(e, date_str)
        return None

def parse_absolute_date(date_str, lang):
    try:
        if lang == 'fr':
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        return datetime.strptime(date_str, "%d %B %Y")
    except ValueError:
        return None
    finally:
        locale.setlocale(locale.LC_TIME, 'C')

def parse_date_with_formats(date_str, format_list):    
    for fmt in format_list:
        if fmt == 'unknown':
            return None
        elif fmt == 'relative':
            result = parse_relative_date(date_str)
            if result:
                return result
        elif fmt == 'DD Month YYYY':
            for lang in ['en', 'fr']:
                result = parse_absolute_date(date_str, lang)
                if result:
                    return result
        elif fmt == 'timestamp':
            try:
                temp_date_str = date_str
                if len(temp_date_str) > 10:
                    temp_date_str = temp_date_str[:10]
                return datetime.fromtimestamp(int(temp_date_str))
            except ValueError:
                pass
        else:
            format_translation = {
                'YYYY': '%Y',
                'YY': '%y',
                'MM': '%m',
                'DD': '%d',
                'HH': '%H',
                'mm': '%M',
                'ss': '%S',
                'SSS': '%f',
            }
            date_str_modified = date_str.replace('h', ':')
            for non_standard, standard in format_translation.items():
                fmt = fmt.replace(non_standard, standard)

            try:
                return datetime.strptime(date_str_modified, fmt)
            except ValueError:
                continue

    return None