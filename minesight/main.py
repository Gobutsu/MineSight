import argparse
from minesight.mojang import uuid_from_username, username_from_uuid, dash_uuid
from minesight.lookup import run
from rich import print
import asyncio

def parse_arguments():
    parser = argparse.ArgumentParser(description="MineSight by Gobutsu")
    parser.add_argument("-u", "--username", help="Username to search")
    parser.add_argument("-id", "--id", help="UUID to search")
    parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")
    args = parser.parse_args()
    args.parser = parser
    return args

def handle_username(username, debug_mode):
    user_id = uuid_from_username(username)
    if user_id:
        asyncio.run(run(username, user_id, dash_uuid(user_id), debug_mode))
    else:
        print(":x: Username not found")

def handle_id(user_id, debug_mode):
    username = username_from_uuid(user_id)
    if username:
        asyncio.run(run(username, user_id, dash_uuid(user_id), debug_mode))
    else:
        print(":x: ID not found")

def main():
    args = parse_arguments()

    if args.username:
        handle_username(args.username, args.debug)
    elif args.id:
        handle_id(args.id, args.debug)
    else:
        args.parser.print_usage()