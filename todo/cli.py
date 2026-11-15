"""Parse arguments, call the store and print results."""

import argparse
import sys

from todo import store


class UsageError(Exception):
    """A command line that could not be parsed."""


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError(message)


def _build_parser():
    parser = _Parser(prog="todo", description="A small command-line to-do list.")
    commands = parser.add_subparsers(dest="command", metavar="command")
    commands.required = True

    add = commands.add_parser("add", help="add an open item")
    add.add_argument("text", help="what to do")

    commands.add_parser("list", help="list open items by ID")
    return parser


def _cmd_add(args, path):
    data = store.load(path)
    item_id = data["next_id"]
    data["items"].append({"id": item_id, "text": args.text, "done": False})
    data["next_id"] = item_id + 1
    store.save(path, data)
    print("added {}".format(item_id))


def _cmd_list(args, path):
    data = store.load(path)
    for item in sorted(data["items"], key=lambda i: i["id"]):
        if item.get("done"):
            continue
        print("{} [ ] {}".format(item["id"], item["text"]))


_COMMANDS = {"add": _cmd_add, "list": _cmd_list}


def main(argv=None):
    """Run the todo command line; return the exit status."""
    if argv is None:
        argv = sys.argv[1:]
    try:
        args = _build_parser().parse_args(argv)
    except UsageError as exc:
        print("todo: {}".format(exc), file=sys.stderr)
        return 1
    try:
        _COMMANDS[args.command](args, store.default_path())
    except store.StoreError as exc:
        print("todo: cannot read {}".format(exc.path), file=sys.stderr)
        return 1
    return 0
