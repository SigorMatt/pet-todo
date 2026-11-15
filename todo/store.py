"""Load and save the to-do list; the only module that touches the file."""

import json
import os
import stat
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
    data["next_id"] = max(data["next_id"], _fresh_id(data["items"]))
    return data


def _fresh_id(items):
    """The lowest ID above every stored one, and at least 1."""
    return max((item["id"] for item in items), default=0) + 1


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


def _file_mode(path):
    """Mode for the saved file: path's current bits, else 0666 masked by the umask."""
    try:
        return stat.S_IMODE(os.stat(path).st_mode)
    except FileNotFoundError:
        umask = os.umask(0)
        os.umask(umask)
        return 0o666 & ~umask


def save(path, data):
    """Write data to path atomically: a temp file in the same directory, then os.replace.

    A symlinked path is resolved first, so the link stays and its target is replaced.
    """
    target = os.path.realpath(path)
    directory = os.path.dirname(target)
    mode = _file_mode(target)
    fd, tmp = tempfile.mkstemp(prefix=".todo-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            os.chmod(tmp, mode)
            json.dump(data, f)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    _fsync_directory(directory)


def _fsync_directory(directory):
    """Flush the rename to disk where the platform allows it; best effort."""
    try:
        fd = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)
