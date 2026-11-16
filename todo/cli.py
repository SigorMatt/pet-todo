"""Parse arguments, call the store and print results."""
# Drill (M6 rehearsal): an owner change pushed after the review; the gate must refuse it until it is reviewed.

import argparse
import datetime
import re
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
    """No stored item has the well-formed ID ``raw``."""

    def __init__(self, raw):
        self.raw = raw
        super().__init__("no item {}".format(raw))


class BadIdError(Exception):
    """``raw`` is not a well-formed ID (D-3); the message shows its first 20 characters."""

    def __init__(self, raw):
        self.raw = raw
        super().__init__("bad id {}".format(raw[:20]))


class NoMoreIdsError(Exception):
    """The next ID would pass store.MAX_ID (D-3)."""

    def __init__(self):
        super().__init__("no more ids")


class BadDateError(Exception):
    """``raw`` is not a real date in the form YYYY-MM-DD."""

    def __init__(self, raw):
        self.raw = raw
        super().__init__("bad date {}".format(raw))


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError(message)


def _build_parser():
    parser = _Parser(prog="todo", description="A small command-line to-do list.")
    commands = parser.add_subparsers(dest="command", metavar="command")
    commands.required = True

    add = commands.add_parser("add", help="add an open item")
    add.add_argument("text", help="what to do")
    add.add_argument("--due", metavar="YYYY-MM-DD", help="the item's due date")

    lst = commands.add_parser("list", help="list open items by ID")
    lst.add_argument("--all", action="store_true", help="include done items")
    lst.add_argument("--overdue", action="store_true",
                     help="only open items due before today")

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


# D-3: 1 to 19 ASCII decimal digits, no leading zero.
_ID = re.compile(r"[1-9][0-9]{0,18}")


def parse_id(raw):
    """Return the ID argument raw as an int, or raise BadIdError if it isn't well formed.

    Well formed means 1 to 19 ASCII decimal digits with no leading zero (D-3).
    A well-formed ID above store.MAX_ID is returned as is: it simply names no item.
    """
    if not _ID.fullmatch(raw):
        raise BadIdError(raw)
    return int(raw)


def _find(data, item_id):
    """Return the index of the item whose ID is item_id (an int from parse_id)."""
    for index, item in enumerate(data["items"]):
        if item["id"] == item_id:
            return index
    raise NoItemError(str(item_id))


def _cmd_add(args, path):
    if args.due is not None and not store.is_iso_date(args.due):
        raise BadDateError(args.due)
    data = store.load(path)
    item_id = data["next_id"]
    if item_id > store.MAX_ID:
        raise NoMoreIdsError()
    item = {"id": item_id, "text": args.text, "done": False}
    if args.due is not None:
        item["due"] = args.due
    data["items"].append(item)
    data["next_id"] = item_id + 1
    _save(path, data)
    print("added {}".format(item_id))


def _is_overdue(item, today):
    """True if item is open and its due date is before today."""
    if item["done"] or "due" not in item:
        return False
    return datetime.date.fromisoformat(item["due"]) < today


def _cmd_list(args, path):
    data = store.load(path)
    for item in sorted(data["items"], key=lambda i: i["id"]):
        if item["done"] and not args.all:
            continue
        if args.overdue and not _is_overdue(item, args.today):
            continue
        mark = "x" if item["done"] else " "
        due = " (due {})".format(item["due"]) if "due" in item else ""
        print("{} [{}] {}{}".format(item["id"], mark, item["text"], due))


def _cmd_done(args, path):
    item_id = parse_id(args.id)
    data = store.load(path)
    item = data["items"][_find(data, item_id)]
    if not item["done"]:
        item["done"] = True
        _save(path, data)
    print("done {}".format(item["id"]))


def _cmd_remove(args, path):
    item_id = parse_id(args.id)
    data = store.load(path)
    item = data["items"].pop(_find(data, item_id))
    _save(path, data)
    print("removed {}".format(item["id"]))


_COMMANDS = {
    "add": _cmd_add,
    "list": _cmd_list,
    "done": _cmd_done,
    "remove": _cmd_remove,
}


_ID_COMMANDS = ("done", "remove")


def _protect_id(argv):
    """Mark a lone argument after done/remove as positional: it is always the ID.

    So ``-x``, ``-h`` and ``--help`` there are IDs, not options.
    """
    if len(argv) == 2 and argv[0] in _ID_COMMANDS and argv[1].startswith("-"):
        return [argv[0], "--", argv[1]]
    return argv


# Spellings argparse accepts for add's --due (it allows unique prefixes).
_DUE_FLAGS = ("--d", "--du", "--due")


def _protect_due(argv):
    """Glue the value after add's --due onto it, so ``--due -x`` means ``--due=-x``.

    Argparse would read a dash-led value as an option and report a usage error;
    glued, it reaches the date check and prints ``bad date``. Scanning stops at
    ``--``, after which everything is text. A trailing --due is left alone.
    """
    if not argv or argv[0] != "add":
        return argv
    out = [argv[0]]
    rest = argv[1:]
    while rest:
        token = rest.pop(0)
        if token == "--":
            out.append(token)
            out.extend(rest)
            break
        if token in _DUE_FLAGS and rest:
            out.append("--due=" + rest.pop(0))
        else:
            out.append(token)
    return out


def main(argv=None, today=None):
    """Run the todo command line; return the exit status.

    ``today`` (a ``datetime.date``) is the date ``list --overdue`` compares
    against; it defaults to ``datetime.date.today()``.
    """
    if argv is None:
        argv = sys.argv[1:]
    if today is None:
        today = datetime.date.today()
    try:
        args = _build_parser().parse_args(_protect_due(_protect_id(list(argv))))
    except UsageError as exc:
        print("todo: {}".format(exc), file=sys.stderr)
        return 1
    args.today = today
    try:
        _COMMANDS[args.command](args, store.default_path())
    except store.StoreError as exc:
        print("todo: cannot read {}".format(exc.path), file=sys.stderr)
        return 1
    except (WriteError, NoItemError, BadIdError, NoMoreIdsError, BadDateError) as exc:
        print("todo: {}".format(exc), file=sys.stderr)
        return 1
    return 0
