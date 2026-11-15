"""Tests for todo.cli: add, list and error handling."""

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

    def test_usage_errors_exit_1_with_message(self):
        for argv in ([], ["frobnicate"], ["add"], ["list", "extra"]):
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

    def test_usage_error(self):
        r = self.run_module("bogus")
        self.assertEqual((r.returncode, r.stdout), (1, ""))
        self.assertTrue(r.stderr.startswith("todo: "), r.stderr)

    def test_cannot_read(self):
        self.write("nope")
        r = self.run_module("list")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stderr, "todo: cannot read {}\n".format(self.path))


if __name__ == "__main__":
    unittest.main()
