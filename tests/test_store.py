import contextlib
import io
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

    def test_duplicate_ids_raise_store_error(self):
        item = {"id": 1, "text": "a", "done": False}
        bad = [
            {"next_id": 1, "items": [item, dict(item, text="b")]},
            {"next_id": 5, "items": [item, dict(item, id=2), dict(item, done=True)]},
        ]
        for data in bad:
            with self.subTest(data=data):
                self._write(data)
                with self.assertRaises(store.StoreError) as cm:
                    store.load(self.path)
                self.assertEqual(cm.exception.path, self.path)

    def test_ids_above_max_raise_store_error(self):
        item = {"id": 1, "text": "a", "done": False}
        huge = int("9" * 4300)
        bad = [
            {"next_id": 1, "items": [dict(item, id=store.MAX_ID + 1)]},
            {"next_id": 1, "items": [item, dict(item, id=huge)]},
            {"next_id": store.MAX_ID + 2, "items": []},
            {"next_id": huge, "items": []},
        ]
        for data in bad:
            with self.subTest(next_id=data["next_id"] > store.MAX_ID):
                self._write(data)
                with self.assertRaises(store.StoreError) as cm:
                    store.load(self.path)
                self.assertEqual(cm.exception.path, self.path)

    def test_next_id_up_to_max_plus_one_is_allowed(self):
        data = {"next_id": store.MAX_ID + 1, "items": [
            {"id": store.MAX_ID, "text": "a", "done": False}]}
        self._write(data)
        self.assertEqual(store.load(self.path), data)

    def test_ids_up_to_max_are_allowed(self):
        self._write({"next_id": 1, "items": [
            {"id": store.MAX_ID, "text": "a", "done": False}]})
        self.assertEqual(store.load(self.path)["next_id"], store.MAX_ID + 1)

    def test_add_and_done_with_huge_stored_id_report_cannot_read(self):
        from todo import cli
        data = {"next_id": 1, "items": [
            {"id": 1, "text": "a", "done": False},
            {"id": int("9" * 4300), "text": "b", "done": False}]}
        self._write(data)
        with open(self.path, "rb") as f:
            before = f.read()
        for argv in (["add", "c"], ["done", "1"]):
            with self.subTest(argv=argv):
                out, err = io.StringIO(), io.StringIO()
                with mock.patch.dict(os.environ, {"TODO_FILE": self.path}), \
                        contextlib.redirect_stdout(out), \
                        contextlib.redirect_stderr(err):
                    self.assertEqual(cli.main(argv), 1)
                self.assertEqual(out.getvalue(), "")
                self.assertEqual(
                    err.getvalue(), "todo: cannot read {}\n".format(self.path))
                with open(self.path, "rb") as f:
                    self.assertEqual(f.read(), before)

    def test_remove_with_duplicate_ids_reports_cannot_read(self):
        from todo import cli
        data = {"next_id": 1, "items": [{"id": 1, "text": "a", "done": False},
                                        {"id": 1, "text": "b", "done": False}]}
        self._write(data)
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, {"TODO_FILE": self.path}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(cli.main(["remove", "1"]), 1)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "todo: cannot read {}\n".format(self.path))
        with open(self.path) as f:
            self.assertEqual(json.load(f), data)

    def test_extra_keys_are_allowed(self):
        data = {"next_id": 2, "items": [
            {"id": 1, "text": "x", "done": True, "due": "2026-11-20"}]}
        with open(self.path, "w") as f:
            json.dump(data, f)
        self.assertEqual(store.load(self.path), data)

    def _write(self, data):
        with open(self.path, "w") as f:
            json.dump(data, f)

    def test_valid_due_is_loaded_and_kept_on_save(self):
        data = {"next_id": 3, "items": [
            {"id": 1, "text": "x", "done": False, "due": "2024-02-29"},
            {"id": 2, "text": "y", "done": True}]}
        self._write(data)
        loaded = store.load(self.path)
        self.assertEqual(loaded, data)
        store.save(self.path, loaded)
        self.assertEqual(store.load(self.path), data)
        with open(self.path) as f:
            self.assertEqual(json.load(f), data)

    def test_non_string_or_non_iso_due_raises_store_error(self):
        item = {"id": 1, "text": "x", "done": False}
        for due in (20261120, 2026.1, None, False, ["2026-11-20"], {"d": 1},
                    "", "2026-13-01", "2026-02-30", "2025-02-29", "tomorrow",
                    "2026-1-5", "20261120", "2026-11-20T10:00", "2026-11-20 ",
                    "2026-W47-1"):
            with self.subTest(due=due):
                self._write({"next_id": 2, "items": [dict(item, due=due)]})
                with self.assertRaises(store.StoreError) as cm:
                    store.load(self.path)
                self.assertEqual(cm.exception.path, self.path)

    def test_is_iso_date(self):
        for value in ("2026-11-20", "2024-02-29", "0001-01-01", "9999-12-31"):
            with self.subTest(value=value):
                self.assertTrue(store.is_iso_date(value))
        for value in ("2026-13-01", "2026-02-30", "tomorrow", "2026-1-5",
                      "0000-01-01", "2026-11-20\n", "\u0662026-11-20", 20261120):
            with self.subTest(value=value):
                self.assertFalse(store.is_iso_date(value))

    def test_low_next_id_is_repaired_above_stored_ids(self):
        items = [{"id": 3, "text": "x", "done": False},
                 {"id": 1, "text": "y", "done": True}]
        for next_id in (1, 3, 0, -5):
            with self.subTest(next_id=next_id):
                self._write({"next_id": next_id, "items": items})
                self.assertEqual(store.load(self.path)["next_id"], 4)

    def test_next_id_below_one_is_repaired_with_no_items(self):
        for next_id in (0, -1):
            with self.subTest(next_id=next_id):
                self._write({"next_id": next_id, "items": []})
                self.assertEqual(store.load(self.path)["next_id"], 1)

    def test_item_ids_below_one_raise_store_error(self):
        item = {"id": 2, "text": "a", "done": False}
        for bad_id in (0, -1, -3):
            for next_id in (-4, 0, 1, 5):
                with self.subTest(id=bad_id, next_id=next_id):
                    self._write({"next_id": next_id,
                                 "items": [item, dict(item, id=bad_id)]})
                    with self.assertRaises(store.StoreError) as cm:
                        store.load(self.path)
                    self.assertEqual(cm.exception.path, self.path)

    def test_item_id_one_is_allowed(self):
        self._write({"next_id": 0, "items": [{"id": 1, "text": "a", "done": False}]})
        self.assertEqual(store.load(self.path)["next_id"], 2)

    def test_higher_next_id_is_kept(self):
        data = {"next_id": 9, "items": [{"id": 3, "text": "x", "done": False}]}
        self._write(data)
        self.assertEqual(store.load(self.path), data)

    def test_add_after_hand_edited_next_id_gets_fresh_id(self):
        from todo import cli
        self._write({"next_id": 1, "items": [{"id": 3, "text": "x", "done": False}]})
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"TODO_FILE": self.path}), \
                contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["add", "new"]), 0)
        self.assertEqual(out.getvalue(), "added 4\n")
        ids = [item["id"] for item in store.load(self.path)["items"]]
        self.assertEqual(sorted(ids), [3, 4])

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

    def _mode(self, path):
        return os.stat(path).st_mode & 0o7777

    @unittest.skipUnless(os.name == "posix", "needs POSIX permissions")
    def test_save_keeps_existing_permissions(self):
        for mode in (0o644, 0o640, 0o600):
            with self.subTest(mode=oct(mode)):
                store.save(self.path, {"next_id": 1, "items": []})
                os.chmod(self.path, mode)
                store.save(self.path, {"next_id": 2, "items": []})
                self.assertEqual(self._mode(self.path), mode)

    @unittest.skipUnless(os.name == "posix", "needs POSIX permissions")
    def test_new_file_gets_default_mode_from_umask(self):
        for umask, mode in ((0o022, 0o644), (0o027, 0o640), (0o002, 0o664)):
            with self.subTest(umask=oct(umask)):
                old = os.umask(umask)
                try:
                    store.save(self.path, {"next_id": 1, "items": []})
                finally:
                    os.umask(old)
                self.assertEqual(self._mode(self.path), mode)
                os.unlink(self.path)

    def test_save_fsyncs_temp_file_before_rename(self):
        calls = []
        real_fsync, real_replace = os.fsync, os.replace

        def fsync(fd):
            size = os.fstat(fd).st_size
            calls.append(("fsync", size))
            return real_fsync(fd)

        def replace(src, dst):
            calls.append(("replace", None))
            return real_replace(src, dst)

        data = {"next_id": 2, "items": [{"id": 1, "text": "x", "done": False}]}
        with mock.patch("todo.store.os.fsync", side_effect=fsync), \
                mock.patch("todo.store.os.replace", side_effect=replace):
            store.save(self.path, data)
        names = [name for name, _ in calls]
        self.assertIn("replace", names)
        first_replace = names.index("replace")
        before = [size for name, size in calls[:first_replace] if name == "fsync"]
        expected = len(json.dumps(data)) + 1
        self.assertIn(expected, before, calls)
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
