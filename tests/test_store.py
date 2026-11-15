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

    def test_wrong_shape_raises_store_error(self):
        item = {"id": 1, "text": "x", "done": False}
        bad = [
            [],
            {},
            {"items": []},
            {"next_id": 1},
            {"next_id": "3", "items": []},
            {"next_id": True, "items": []},
            {"next_id": 1, "items": {}},
            {"next_id": 2, "items": [1]},
            {"next_id": 2, "items": [{"text": "x", "done": False}]},
            {"next_id": 2, "items": [dict(item, id="1")]},
            {"next_id": 2, "items": [dict(item, text=3)]},
            {"next_id": 2, "items": [dict(item, done="no")]},
            {"next_id": 2, "items": [{"id": 1, "text": "x"}]},
        ]
        for data in bad:
            with self.subTest(data=data):
                with open(self.path, "w") as f:
                    json.dump(data, f)
                with self.assertRaises(store.StoreError) as cm:
                    store.load(self.path)
                self.assertEqual(cm.exception.path, self.path)

    def test_extra_keys_are_allowed(self):
        data = {"next_id": 2, "items": [
            {"id": 1, "text": "x", "done": True, "due": "2026-11-20"}]}
        with open(self.path, "w") as f:
            json.dump(data, f)
        self.assertEqual(store.load(self.path), data)

    def test_save_round_trips(self):
        data = {"next_id": 2, "items": [{"id": 1, "text": "buy milk", "done": False}]}
        store.save(self.path, data)
        self.assertEqual(store.load(self.path), data)
        self.assertEqual(os.listdir(self.dir), ["todo.json"])

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symlinks")
    def test_save_through_symlink_updates_target(self):
        real = os.path.join(self.dir, "real.json")
        store.save(real, {"next_id": 1, "items": []})
        os.symlink("real.json", self.path)
        data = {"next_id": 2, "items": [{"id": 1, "text": "x", "done": False}]}
        store.save(self.path, data)
        self.assertTrue(os.path.islink(self.path))
        self.assertEqual(os.readlink(self.path), "real.json")
        with open(real, encoding="utf-8") as f:
            self.assertEqual(json.load(f), data)
        self.assertEqual(sorted(os.listdir(self.dir)), ["real.json", "todo.json"])

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symlinks")
    def test_save_through_dangling_symlink_creates_target(self):
        sub = os.path.join(self.dir, "sub")
        os.mkdir(sub)
        os.symlink(os.path.join(sub, "real.json"), self.path)
        data = {"next_id": 1, "items": []}
        store.save(self.path, data)
        self.assertTrue(os.path.islink(self.path))
        self.assertEqual(os.listdir(sub), ["real.json"])
        self.assertEqual(store.load(self.path), data)

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
