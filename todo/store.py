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
    if not isinstance(data, dict):
        raise StoreError(path)
    return data


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
