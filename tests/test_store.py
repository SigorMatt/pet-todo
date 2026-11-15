import json
import os
import tempfile
import unittest
from unittest import mock

from todo import store


class StoreTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name
        self.path = os.path.join(self.dir, "todo.json")

    def test_default_path_uses_env(self):
        with mock.patch.dict(os.environ, {"TODO_FILE": self.path}):
            self.assertEqual(store.default_path(), self.path)

    def test_default_path_falls_back_to_cwd_file(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("TODO_FILE", None)
            self.assertEqual(store.default_path(), "todo.json")

    def test_missing_file_loads_empty(self):
        self.assertEqual(store.load(self.path), {"next_id": 1, "items": []})

    def test_non_json_raises_store_error_with_path(self):
        with open(self.path, "w") as f:
            f.write("not json {")
        with self.assertRaises(store.StoreError) as cm:
            store.load(self.path)
        self.assertEqual(cm.exception.path, self.path)

    def test_save_round_trips(self):
        data = {"next_id": 2, "items": [{"id": 1, "text": "buy milk", "done": False}]}
        store.save(self.path, data)
        self.assertEqual(store.load(self.path), data)
        self.assertEqual(os.listdir(self.dir), ["todo.json"])

    def _assert_failed_write_keeps_original(self, target):
        original = {"next_id": 2, "items": [{"id": 1, "text": "old", "done": False}]}
        store.save(self.path, original)
        with open(self.path, "rb") as f:
            before = f.read()
        with mock.patch(target, side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                store.save(self.path, {"next_id": 3, "items": []})
        with open(self.path, "rb") as f:
            self.assertEqual(f.read(), before)
        self.assertEqual(json.loads(before), original)
        self.assertEqual(os.listdir(self.dir), ["todo.json"])

    def test_failed_dump_leaves_original_and_no_temp(self):
        self._assert_failed_write_keeps_original("todo.store.json.dump")

    def test_failed_replace_leaves_original_and_no_temp(self):
        self._assert_failed_write_keeps_original("todo.store.os.replace")


if __name__ == "__main__":
    unittest.main()
