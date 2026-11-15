"""Parse arguments, call the store and print results."""

import argparse
import sys

from todo import store


class UsageError(Exception):
    """A command line that could not be parsed."""


class WriteError(Exception):
    """The list file at ``path`` could not be written."""

    def __init__(self, path):
        self.path = path
        super().__init__("cannot write {}".format(path))


class NoItemError(Exception):
    """No stored item has the ID ``raw`` (or ``raw`` is not an integer)."""

    def __init__(self, raw):
        self.raw = raw
        super().__init__("no item {}".format(raw))


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError(message)


def _build_parser():
    parser = _Parser(prog="todo", description="A small command-line to-do list.")
    commands = parser.add_subparsers(dest="command", metavar="command")
    commands.required = True

    add = commands.add_parser("add", help="add an open item")
    add.add_argument("text", help="what to do")

    lst = commands.add_parser("list", help="list open items by ID")
    lst.add_argument("--all", action="store_true", help="include done items")

    done = commands.add_parser("done", help="mark an item done")
    done.add_argument("id", help="the item's ID")

    remove = commands.add_parser("remove", help="delete an item")
    remove.add_argument("id", help="the item's ID")
    return parser


def _save(path, data):
    try:
        store.save(path, data)
    except OSError as exc:
        raise WriteError(path) from exc


def _find(data, raw):
    """Return the index of the item whose ID is the integer in raw."""
    try:
        item_id = int(raw)
    except ValueError:
        raise NoItemError(raw) from None
    for index, item in enumerate(data["items"]):
        if item["id"] == item_id:
            return index
    raise NoItemError(raw)


def _cmd_add(args, path):
    data = store.load(path)
    item_id = data["next_id"]
    data["items"].append({"id": item_id, "text": args.text, "done": False})
    data["next_id"] = item_id + 1
    _save(path, data)
    print("added {}".format(item_id))


def _cmd_list(args, path):
    data = store.load(path)
    for item in sorted(data["items"], key=lambda i: i["id"]):
        if item["done"] and not args.all:
            continue
        mark = "x" if item["done"] else " "
        print("{} [{}] {}".format(item["id"], mark, item["text"]))


def _cmd_done(args, path):
    data = store.load(path)
    item = data["items"][_find(data, args.id)]
    if not item["done"]:
        item["done"] = True
        _save(path, data)
    print("done {}".format(item["id"]))


def _cmd_remove(args, path):
    data = store.load(path)
    item = data["items"].pop(_find(data, args.id))
    _save(path, data)
    print("removed {}".format(item["id"]))


_COMMANDS = {
    "add": _cmd_add,
    "list": _cmd_list,
    "done": _cmd_done,
    "remove": _cmd_remove,
}


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
    except (WriteError, NoItemError) as exc:
        print("todo: {}".format(exc), file=sys.stderr)
        return 1
    return 0
