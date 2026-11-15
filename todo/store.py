"""Load and save the to-do list; the only module that touches the file."""

import json
import os
import tempfile


class StoreError(Exception):
    """The list file at ``path`` could not be read."""

    def __init__(self, path, message=None):
        self.path = path
        super().__init__(message or "cannot read {}".format(path))


def default_path():
    """Return $TODO_FILE if set, else ./todo.json."""
    return os.environ.get("TODO_FILE") or "todo.json"


def load(path):
    """Return the list stored at path; a missing file gives an empty list."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"next_id": 1, "items": []}
    except (OSError, ValueError) as exc:
        raise StoreError(path) from exc
    if not _valid(data):
        raise StoreError(path)
    return data


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_item(item):
    return (
        isinstance(item, dict)
        and _is_int(item.get("id"))
        and isinstance(item.get("text"), str)
        and isinstance(item.get("done"), bool)
    )


def _valid(data):
    """True if data has the list's shape: an int next_id and a list of items."""
    return (
        isinstance(data, dict)
        and _is_int(data.get("next_id"))
        and isinstance(data.get("items"), list)
        and all(_valid_item(item) for item in data["items"])
    )


def save(path, data):
    """Write data to path atomically: a temp file in the same directory, then os.replace."""
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".todo-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
