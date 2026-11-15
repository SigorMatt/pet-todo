"""Tests for todo.cli: add, list, done, remove and error handling."""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from todo import cli

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CliTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = os.path.join(tmp.name, "todo.json")
        patcher = mock.patch.dict(os.environ, {"TODO_FILE": self.path})
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def write(self, text):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)


class AddTest(CliTestCase):
    def test_first_add_prints_id_1_and_creates_file(self):
        self.assertFalse(os.path.exists(self.path))
        self.assertEqual(self.run_cli("add", "buy milk"), (0, "added 1\n", ""))
        with open(self.path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["next_id"], 2)
        self.assertEqual(data["items"], [{"id": 1, "text": "buy milk", "done": False}])

    def test_second_add_prints_id_2(self):
        self.run_cli("add", "buy milk")
        self.assertEqual(self.run_cli("add", "walk dog"), (0, "added 2\n", ""))


class ListTest(CliTestCase):
    def test_lists_items_in_id_order(self):
        self.run_cli("add", "buy milk")
        self.run_cli("add", "walk dog")
        self.assertEqual(
            self.run_cli("list"), (0, "1 [ ] buy milk\n2 [ ] walk dog\n", "")
        )

    def test_sorts_by_id_whatever_the_file_order(self):
        self.write(json.dumps({"next_id": 3, "items": [
            {"id": 2, "text": "walk dog", "done": False},
            {"id": 1, "text": "buy milk", "done": False},
        ]}))
        self.assertEqual(
            self.run_cli("list"), (0, "1 [ ] buy milk\n2 [ ] walk dog\n", "")
        )

    def test_missing_file_prints_nothing(self):
        self.assertEqual(self.run_cli("list"), (0, "", ""))
        self.assertFalse(os.path.exists(self.path))

    def test_empty_list_prints_nothing(self):
        self.write(json.dumps({"next_id": 1, "items": []}))
        self.assertEqual(self.run_cli("list"), (0, "", ""))


class DoneTest(CliTestCase):
    def setUp(self):
        super().setUp()
        self.run_cli("add", "buy milk")
        self.run_cli("add", "walk dog")

    def test_done_prints_id_and_saves(self):
        self.assertEqual(self.run_cli("done", "1"), (0, "done 1\n", ""))
        with open(self.path, encoding="utf-8") as f:
            items = json.load(f)["items"]
        self.assertEqual([i["done"] for i in items], [True, False])

    def test_list_hides_done_and_all_shows_x(self):
        self.run_cli("done", "1")
        self.assertEqual(self.run_cli("list"), (0, "2 [ ] walk dog\n", ""))
        self.assertEqual(
            self.run_cli("list", "--all"),
            (0, "1 [x] buy milk\n2 [ ] walk dog\n", ""),
        )

    def test_done_twice_is_not_an_error(self):
        self.run_cli("done", "2")
        self.assertEqual(self.run_cli("done", "2"), (0, "done 2\n", ""))
        self.assertEqual(
            self.run_cli("list", "--all"),
            (0, "1 [ ] buy milk\n2 [x] walk dog\n", ""),
        )


class RemoveTest(CliTestCase):
    def setUp(self):
        super().setUp()
        self.run_cli("add", "buy milk")
        self.run_cli("add", "walk dog")

    def test_remove_prints_id_and_deletes(self):
        self.assertEqual(self.run_cli("remove", "1"), (0, "removed 1\n", ""))
        self.assertEqual(self.run_cli("list", "--all"), (0, "2 [ ] walk dog\n", ""))

    def test_remove_done_item(self):
        self.run_cli("done", "2")
        self.assertEqual(self.run_cli("remove", "2"), (0, "removed 2\n", ""))
        self.assertEqual(self.run_cli("list", "--all"), (0, "1 [ ] buy milk\n", ""))

    def test_ids_not_reused_after_removing_highest(self):
        self.run_cli("remove", "2")
        self.assertEqual(self.run_cli("add", "feed cat"), (0, "added 3\n", ""))
        self.run_cli("remove", "3")
        self.run_cli("remove", "1")
        self.assertEqual(self.run_cli("add", "water plants"), (0, "added 4\n", ""))
        self.assertEqual(self.run_cli("list"), (0, "4 [ ] water plants\n", ""))


class NoItemTest(CliTestCase):
    def test_unknown_or_non_integer_id(self):
        self.run_cli("add", "buy milk")
        with open(self.path, encoding="utf-8") as f:
            before = f.read()
        for command in ("done", "remove"):
            for raw in ("2", "0", "-1", "abc", "1.5", ""):
                with self.subTest(command=command, raw=raw):
                    self.assertEqual(
                        self.run_cli(command, raw),
                        (1, "", "todo: no item {}\n".format(raw)),
                    )
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), before)

    def test_id_must_be_plain_ascii_digits(self):
        for text in ("a", "b", "c"):
            self.run_cli("add", text)
        with open(self.path, encoding="utf-8") as f:
            before = f.read()
        for command in ("done", "remove"):
            for raw in (" 1", "1 ", "+2", "\u0663", "1_0", "\uff11"):
                with self.subTest(command=command, raw=raw):
                    self.assertEqual(
                        self.run_cli(command, raw),
                        (1, "", "todo: no item {}\n".format(raw)),
                    )
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), before)

    def test_dash_id_is_no_item_not_an_option(self):
        self.run_cli("add", "buy milk")
        for command in ("done", "remove"):
            for raw in ("-x", "-1", "--all", "-", "--", "-1x"):
                with self.subTest(command=command, raw=raw):
                    self.assertEqual(
                        self.run_cli(command, raw),
                        (1, "", "todo: no item {}\n".format(raw)),
                    )

    def test_help_still_shows_help(self):
        for command in ("done", "remove"):
            for flag in ("-h", "--help"):
                with self.subTest(command=command, flag=flag):
                    with self.assertRaises(SystemExit) as cm:
                        self.run_cli(command, flag)
                    self.assertEqual(cm.exception.code, 0)

    def test_unknown_id_on_missing_file(self):
        for command in ("done", "remove"):
            with self.subTest(command=command):
                self.assertEqual(
                    self.run_cli(command, "1"), (1, "", "todo: no item 1\n")
                )
        self.assertFalse(os.path.exists(self.path))

    def test_removed_id_is_unknown(self):
        self.run_cli("add", "buy milk")
        self.run_cli("remove", "1")
        for command in ("done", "remove"):
            with self.subTest(command=command):
                self.assertEqual(
                    self.run_cli(command, "1"), (1, "", "todo: no item 1\n")
                )


class ErrorTest(CliTestCase):
    def test_list_on_non_json_file(self):
        self.write("not json{")
        self.assertEqual(
            self.run_cli("list"), (1, "", "todo: cannot read {}\n".format(self.path))
        )

    def test_add_on_non_json_file_leaves_it_alone(self):
        self.write("not json{")
        self.assertEqual(
            self.run_cli("add", "buy milk"),
            (1, "", "todo: cannot read {}\n".format(self.path)),
        )
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "not json{")

    def test_wrong_shape_file(self):
        for text in ("{}", '{"next_id": "3", "items": []}'):
            for argv in (["list"], ["add", "x"]):
                with self.subTest(text=text, argv=argv):
                    self.write(text)
                    self.assertEqual(
                        self.run_cli(*argv),
                        (1, "", "todo: cannot read {}\n".format(self.path)),
                    )

    def test_add_into_missing_directory_cannot_write(self):
        path = os.path.join(os.path.dirname(self.path), "no", "such", "t.json")
        with mock.patch.dict(os.environ, {"TODO_FILE": path}):
            self.assertEqual(
                self.run_cli("add", "x"),
                (1, "", "todo: cannot write {}\n".format(path)),
            )

    def test_any_oserror_on_save_cannot_write(self):
        for exc in (PermissionError("ro"), OSError(28, "No space left on device")):
            with self.subTest(exc=exc):
                with mock.patch("todo.store.os.replace", side_effect=exc):
                    self.assertEqual(
                        self.run_cli("add", "x"),
                        (1, "", "todo: cannot write {}\n".format(self.path)),
                    )

    def test_oserror_on_read_cannot_read(self):
        os.mkdir(self.path)
        for argv in (["list"], ["add", "x"]):
            with self.subTest(argv=argv):
                self.assertEqual(
                    self.run_cli(*argv),
                    (1, "", "todo: cannot read {}\n".format(self.path)),
                )

    def test_usage_errors_exit_1_with_message(self):
        for argv in ([], ["frobnicate"], ["add"], ["list", "extra"],
                     ["done"], ["remove"], ["done", "1", "2"]):
            with self.subTest(argv=argv):
                code, out, err = self.run_cli(*argv)
                self.assertEqual((code, out), (1, ""))
                self.assertTrue(err.startswith("todo: "), err)


class SubprocessTest(CliTestCase):
    def run_module(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "todo", *args],
            cwd=ROOT, env=dict(os.environ, TODO_FILE=self.path),
            capture_output=True, text=True, timeout=30,
        )

    def test_add_then_list(self):
        r = self.run_module("add", "buy milk")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "added 1\n", ""))
        self.assertTrue(os.path.exists(self.path))
        r = self.run_module("list")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "1 [ ] buy milk\n", ""))

    def test_done_remove_and_unknown_id(self):
        self.run_module("add", "buy milk")
        r = self.run_module("done", "1")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "done 1\n", ""))
        r = self.run_module("list", "--all")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "1 [x] buy milk\n", ""))
        r = self.run_module("remove", "1")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "removed 1\n", ""))
        r = self.run_module("done", "1")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (1, "", "todo: no item 1\n"))

    def test_usage_error(self):
        r = self.run_module("bogus")
        self.assertEqual((r.returncode, r.stdout), (1, ""))
        self.assertTrue(r.stderr.startswith("todo: "), r.stderr)

    def test_cannot_read(self):
        self.write("nope")
        r = self.run_module("list")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stderr, "todo: cannot read {}\n".format(self.path))

    def test_cannot_write(self):
        path = os.path.join(os.path.dirname(self.path), "no", "such", "t.json")
        r = subprocess.run(
            [sys.executable, "-m", "todo", "add", "x"],
            cwd=ROOT, env=dict(os.environ, TODO_FILE=path),
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual((r.returncode, r.stdout), (1, ""))
        self.assertEqual(r.stderr, "todo: cannot write {}\n".format(path))


if __name__ == "__main__":
    unittest.main()
