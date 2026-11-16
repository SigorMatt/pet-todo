"""Tests for todo.cli: add, list, done, remove and error handling."""

import contextlib
import datetime
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from todo import cli, store

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CliTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = os.path.join(tmp.name, "todo.json")
        patcher = mock.patch.dict(os.environ, {"TODO_FILE": self.path})
        patcher.start()
        self.addCleanup(patcher.stop)

    today = None

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv), today=self.today)
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


    def _write_top_id(self, top):
        data = {"next_id": 1, "items": [{"id": top, "text": "a", "done": False}]}
        self.write(json.dumps(data))

    def test_add_up_to_max_id_saves_a_loadable_file(self):
        self._write_top_id(store.MAX_ID - 1)
        self.assertEqual(
            self.run_cli("add", "b"), (0, "added {}\n".format(store.MAX_ID), ""))
        data = store.load(self.path)
        self.assertEqual(data["next_id"], store.MAX_ID + 1)
        self.assertEqual([i["id"] for i in data["items"]],
                         [store.MAX_ID - 1, store.MAX_ID])

    def test_add_above_max_id_no_more_ids_and_saves_nothing(self):
        for next_id in (1, store.MAX_ID + 1):
            with self.subTest(next_id=next_id):
                self.write(json.dumps({"next_id": next_id, "items": [
                    {"id": store.MAX_ID, "text": "a", "done": False}]}))
                with open(self.path, "rb") as f:
                    before = f.read()
                self.assertEqual(
                    self.run_cli("add", "b"),
                    (1, "", "todo: no more ids\n"))
                with open(self.path, "rb") as f:
                    self.assertEqual(f.read(), before)
                self.assertEqual(self.run_cli("list"), (0, "{} [ ] a\n".format(store.MAX_ID), ""))


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


class DueTest(CliTestCase):
    def read_json(self):
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def test_add_with_due_stores_date_and_list_shows_it(self):
        self.assertEqual(
            self.run_cli("add", "buy milk", "--due", "2026-11-20"), (0, "added 1\n", ""))
        self.assertEqual(self.read_json()["items"], [
            {"id": 1, "text": "buy milk", "done": False, "due": "2026-11-20"}])
        self.assertEqual(
            self.run_cli("list"), (0, "1 [ ] buy milk (due 2026-11-20)\n", ""))

    def test_due_before_text_also_works(self):
        self.assertEqual(
            self.run_cli("add", "--due", "2024-02-29", "leap"), (0, "added 1\n", ""))
        self.assertEqual(self.read_json()["items"][0]["due"], "2024-02-29")

    def test_items_without_due_show_no_suffix(self):
        self.run_cli("add", "buy milk")
        self.run_cli("add", "walk dog", "--due", "2026-12-01")
        self.assertNotIn("due", self.read_json()["items"][0])
        self.assertEqual(
            self.run_cli("list"),
            (0, "1 [ ] buy milk\n2 [ ] walk dog (due 2026-12-01)\n", ""))

    def test_list_all_shows_due_on_done_items(self):
        self.run_cli("add", "buy milk", "--due", "2026-11-20")
        self.run_cli("add", "walk dog")
        self.run_cli("done", "1")
        self.assertEqual(self.run_cli("list"), (0, "2 [ ] walk dog\n", ""))
        self.assertEqual(
            self.run_cli("list", "--all"),
            (0, "1 [x] buy milk (due 2026-11-20)\n2 [ ] walk dog\n", ""))

    def test_due_survives_done_and_remove_saves(self):
        self.run_cli("add", "a", "--due", "2026-11-20")
        self.run_cli("add", "b")
        self.run_cli("done", "1")
        self.run_cli("remove", "2")
        self.assertEqual(self.read_json()["items"], [
            {"id": 1, "text": "a", "done": True, "due": "2026-11-20"}])

    def test_bad_date_exits_1_and_leaves_file_unchanged(self):
        self.run_cli("add", "keep", "--due", "2026-11-20")
        with open(self.path, "rb") as f:
            before = f.read()
        bad = ("2026-13-01", "2026-02-30", "tomorrow", "2026-1-5", "",
               "20261120", "2026-11-20T00:00", " 2026-11-20", "2026-11-20\n",
               "\uff12\uff10\uff12\uff16-11-20", "2025-02-29", "2026-00-10")
        for value in bad:
            with self.subTest(value=value):
                self.assertEqual(
                    self.run_cli("add", "x", "--due", value),
                    (1, "", "todo: bad date {}\n".format(value)))
                with open(self.path, "rb") as f:
                    self.assertEqual(f.read(), before)

    def test_dash_due_value_is_a_bad_date_not_a_usage_error(self):
        self.run_cli("add", "keep")
        with open(self.path, "rb") as f:
            before = f.read()
        for value in ("-2026-11-20", "-x", "--", "-h", "--help", "-1", "--due"):
            for flag in ("--due", "--du", "--d"):
                for argv in (["add", "x", flag, value], ["add", flag, value, "x"]):
                    with self.subTest(argv=argv):
                        self.assertEqual(
                            self.run_cli(*argv),
                            (1, "", "todo: bad date {}\n".format(value)))
                        with open(self.path, "rb") as f:
                            self.assertEqual(f.read(), before)

    def test_dash_text_and_due_after_double_dash_still_work(self):
        self.assertEqual(
            self.run_cli("add", "--due", "2026-11-20", "--", "-text"),
            (0, "added 1\n", ""))
        self.assertEqual(self.run_cli("add", "--", "--due"), (0, "added 2\n", ""))
        self.assertEqual(
            self.run_cli("list"),
            (0, "1 [ ] -text (due 2026-11-20)\n2 [ ] --due\n", ""))

    def test_due_with_no_value_is_a_usage_error(self):
        code, out, err = self.run_cli("add", "x", "--due")
        self.assertEqual((code, out), (1, ""))
        self.assertTrue(err.startswith("todo: "))
        self.assertNotIn("bad date", err)
        self.assertFalse(os.path.exists(self.path))

    def test_bad_date_on_missing_file_creates_nothing(self):
        self.assertEqual(
            self.run_cli("add", "x", "--due", "tomorrow"),
            (1, "", "todo: bad date tomorrow\n"))
        self.assertFalse(os.path.exists(self.path))

    def test_stored_bad_due_cannot_read(self):
        item = {"id": 1, "text": "a", "done": False}
        for due in (20261120, None, True, ["2026-11-20"], "2026-13-01",
                    "2026-02-30", "tomorrow", "2026-1-5", "20261120"):
            for argv in (["list"], ["list", "--all"], ["add", "b"], ["done", "1"]):
                with self.subTest(due=due, argv=argv):
                    self.write(json.dumps({"next_id": 2, "items": [dict(item, due=due)]}))
                    with open(self.path, "rb") as f:
                        before = f.read()
                    self.assertEqual(
                        self.run_cli(*argv),
                        (1, "", "todo: cannot read {}\n".format(self.path)))
                    with open(self.path, "rb") as f:
                        self.assertEqual(f.read(), before)


class OverdueTest(CliTestCase):
    today = datetime.date(2026, 11, 15)

    def write_items(self, items):
        self.write(json.dumps({"next_id": 10, "items": items}))

    def item(self, item_id, due=None, done=False):
        item = {"id": item_id, "text": "t{}".format(item_id), "done": done}
        if due is not None:
            item["due"] = due
        return item

    def test_past_due_open_item_is_shown(self):
        self.write_items([self.item(1, "2026-11-14")])
        self.assertEqual(
            self.run_cli("list", "--overdue"), (0, "1 [ ] t1 (due 2026-11-14)\n", ""))

    def test_due_today_is_hidden(self):
        self.write_items([self.item(1, "2026-11-15")])
        self.assertEqual(self.run_cli("list", "--overdue"), (0, "", ""))

    def test_future_due_is_hidden(self):
        self.write_items([self.item(1, "2026-11-16"), self.item(2, "2027-01-01")])
        self.assertEqual(self.run_cli("list", "--overdue"), (0, "", ""))

    def test_no_due_is_hidden(self):
        self.write_items([self.item(1)])
        self.assertEqual(self.run_cli("list", "--overdue"), (0, "", ""))

    def test_done_past_due_is_hidden(self):
        self.write_items([self.item(1, "2026-11-01", done=True)])
        self.assertEqual(self.run_cli("list", "--overdue"), (0, "", ""))

    def mixed(self):
        self.write_items([
            self.item(5, "2025-12-31"),
            self.item(2, "2026-11-15"),
            self.item(4, "2026-11-01", done=True),
            self.item(1, "2026-11-14"),
            self.item(3),
            self.item(6, "2026-12-01"),
        ])

    def test_overdue_lists_in_id_order(self):
        self.mixed()
        self.assertEqual(
            self.run_cli("list", "--overdue"),
            (0, "1 [ ] t1 (due 2026-11-14)\n5 [ ] t5 (due 2025-12-31)\n", ""))

    def test_all_overdue_same_as_overdue(self):
        self.mixed()
        expected = self.run_cli("list", "--overdue")
        for argv in (["list", "--all", "--overdue"], ["list", "--overdue", "--all"]):
            with self.subTest(argv=argv):
                self.assertEqual(self.run_cli(*argv), expected)

    def test_empty_output_when_none_overdue(self):
        for items in ([], [self.item(1, "2026-11-15"), self.item(2),
                           self.item(3, "2026-01-01", done=True)]):
            with self.subTest(items=items):
                self.write_items(items)
                self.assertEqual(self.run_cli("list", "--overdue"), (0, "", ""))
        os.remove(self.path)
        self.assertEqual(self.run_cli("list", "--overdue"), (0, "", ""))

    def test_today_is_injected(self):
        self.write_items([self.item(1, "2026-11-15")])
        self.today = datetime.date(2026, 11, 16)
        self.assertEqual(
            self.run_cli("list", "--overdue"), (0, "1 [ ] t1 (due 2026-11-15)\n", ""))

    def test_today_defaults_to_date_today(self):
        self.write_items([self.item(1, "2026-11-15")])
        fake = mock.Mock(wraps=datetime.date)
        fake.today.return_value = datetime.date(2026, 11, 16)
        fake.fromisoformat = datetime.date.fromisoformat
        with mock.patch("todo.cli.datetime.date", fake):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = cli.main(["list", "--overdue"])
        self.assertEqual((code, out.getvalue()), (0, "1 [ ] t1 (due 2026-11-15)\n"))


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
    def test_well_formed_unknown_id_is_no_item(self):
        self.run_cli("add", "buy milk")
        with open(self.path, "rb") as f:
            before = f.read()
        for command in ("done", "remove"):
            for raw in ("2", "9" * 19, str(store.MAX_ID)):
                with self.subTest(command=command, raw=raw):
                    self.assertEqual(
                        self.run_cli(command, raw),
                        (1, "", "todo: no item {}\n".format(raw)),
                    )
        with open(self.path, "rb") as f:
            self.assertEqual(f.read(), before)

    def test_help_still_shows_help(self):
        for argv in (["-h"], ["--help"], ["add", "-h"], ["list", "-h"],
                     ["add", "--help"], ["list", "--help"]):
            with self.subTest(argv=argv):
                with self.assertRaises(SystemExit) as cm:
                    self.run_cli(*argv)
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


class BadIdTest(CliTestCase):
    def setUp(self):
        super().setUp()
        for text in ("a", "b", "c"):
            self.run_cli("add", text)
        with open(self.path, "rb") as f:
            self.before = f.read()

    def assert_bad_ids(self, raws):
        for command in ("done", "remove"):
            for raw in raws:
                with self.subTest(command=command, raw=raw):
                    self.assertEqual(
                        self.run_cli(command, raw),
                        (1, "", "todo: bad id {}\n".format(raw[:20])),
                    )
                    with open(self.path, "rb") as f:
                        self.assertEqual(f.read(), self.before)

    def test_malformed_ids(self):
        self.assert_bad_ids(("01", "001", "0", "", "-1", "1.0", "1.5", "abc", "1e3"))

    def test_id_must_be_plain_ascii_digits(self):
        self.assert_bad_ids((" 1", "1 ", "+2", "1\n", "1_0",
                             "\u0663", "\u0661\u0662", "\uff11", "\uff12"))

    def test_dash_id_is_bad_id_not_an_option(self):
        self.assert_bad_ids(("-x", "-1", "--all", "-", "--", "-1x"))

    def test_help_flag_after_done_or_remove_is_a_bad_id(self):
        self.assert_bad_ids(("-h", "--help"))

    def test_too_many_digits(self):
        self.assert_bad_ids(("1" * 20, "1" * 5000, "0" * 4400 + "1"))

    def test_message_cuts_value_to_20_characters(self):
        code, out, err = self.run_cli("done", "1" * 5000)
        self.assertEqual((code, out, err), (1, "", "todo: bad id {}\n".format("1" * 20)))

    def test_bad_id_checked_before_file_is_loaded(self):
        self.write("not json")
        for command in ("done", "remove"):
            with self.subTest(command=command):
                self.assertEqual(self.run_cli(command, "01"), (1, "", "todo: bad id 01\n"))
        os.remove(self.path)
        for command in ("done", "remove"):
            with self.subTest(command=command, missing=True):
                self.assertEqual(self.run_cli(command, "abc"), (1, "", "todo: bad id abc\n"))
        self.assertFalse(os.path.exists(self.path))

    def test_parse_id_helper(self):
        self.assertEqual(cli.parse_id("1"), 1)
        self.assertEqual(cli.parse_id(str(store.MAX_ID)), store.MAX_ID)
        self.assertEqual(cli.parse_id("9" * 19), int("9" * 19))
        for raw in ("0", "01", "", "1" * 20, "\u0661"):
            with self.subTest(raw=raw):
                with self.assertRaises(cli.BadIdError):
                    cli.parse_id(raw)


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


class BadTextTest(CliTestCase):
    """D-2: add rejects bad text before loading, leaving the file unchanged."""

    def assert_bad_text(self, text):
        # With a missing file: rejected, and the file is not created.
        self.assertEqual(self.run_cli("add", text), (1, "", "todo: bad text\n"))
        self.assertFalse(os.path.exists(self.path))
        # With an existing file: rejected, and the file is byte-identical.
        self.write('{"next_id": 2, "items": [{"id": 1, "text": "a", "done": false}]}')
        with open(self.path, "rb") as f:
            before = f.read()
        self.assertEqual(self.run_cli("add", text), (1, "", "todo: bad text\n"))
        with open(self.path, "rb") as f:
            self.assertEqual(f.read(), before)

    def test_empty(self):
        self.assert_bad_text("")

    def test_spaces_only(self):
        self.assert_bad_text("   ")

    def test_newline(self):
        self.assert_bad_text("buy\nmilk")

    def test_carriage_return(self):
        self.assert_bad_text("buy\rmilk")

    def test_tab(self):
        self.assert_bad_text("buy\tmilk")

    def test_nul(self):
        self.assert_bad_text("buy\x00milk")

    def test_del(self):
        self.assert_bad_text("buy\x7fmilk")

    def test_next_line_u0085(self):
        self.assert_bad_text("buy\x85milk")

    def test_surrogate_escaped_bytes(self):
        # How Python decodes argv bytes that aren't valid UTF-8.
        self.assert_bad_text(b"buy \xff milk".decode("utf-8", "surrogateescape"))

    def test_bad_text_with_due_is_bad_text(self):
        self.assertEqual(self.run_cli("add", "a\nb", "--due", "2026-11-20"),
                         (1, "", "todo: bad text\n"))
        self.assertFalse(os.path.exists(self.path))

    def test_check_text_helper(self):
        cli.check_text("buy milk")
        with self.assertRaises(cli.BadTextError):
            cli.check_text("\n")


# Texts D-2 accepts; each must list as exactly one line.
ACCEPTED_TEXTS = [
    "buy milk",
    "café über журнал 漢字",
    "party \U0001F389\U0001F468‍\U0001F469‍\U0001F467",
    "[x] looks done",
    "2 [ ] looks like another item",
    "  leading and trailing  ",
    "line separator",
    "para separator",
]


class OneLinePerItemTest(CliTestCase):
    """P2-2 c2: list prints exactly one line per item for accepted text."""

    def test_each_accepted_text_lists_as_one_line(self):
        for n, text in enumerate(ACCEPTED_TEXTS, start=1):
            with self.subTest(text=text):
                self.assertEqual(self.run_cli("add", text),
                                 (0, "added {}\n".format(n), ""))
        code, out, err = self.run_cli("list")
        self.assertEqual((code, err), (0, ""))
        expected = "".join("{} [ ] {}\n".format(n, t)
                           for n, t in enumerate(ACCEPTED_TEXTS, start=1))
        self.assertEqual(out, expected)
        self.assertEqual(out.count("\n"), len(ACCEPTED_TEXTS))

    def test_done_items_with_due_list_as_one_line(self):
        for text in ACCEPTED_TEXTS:
            self.run_cli("add", text, "--due", "2026-11-20")
        self.run_cli("done", "1")
        code, out, err = self.run_cli("list", "--all")
        self.assertEqual((code, err), (0, ""))
        lines = out.split("\n")
        self.assertEqual(lines[-1], "")
        self.assertEqual(len(lines) - 1, len(ACCEPTED_TEXTS))
        for n, (line, text) in enumerate(zip(lines, ACCEPTED_TEXTS), start=1):
            mark = "x" if n == 1 else " "
            self.assertEqual(line, "{} [{}] {} (due 2026-11-20)".format(n, mark, text))


class TextSubprocessTest(CliTestCase):
    """Bad argv bytes and strict-UTF-8 stdout through the real entry point (L-3)."""

    def run_module(self, *argv):
        env = dict(os.environ, TODO_FILE=self.path,
                   PYTHONIOENCODING="utf-8:strict", LC_ALL="C.UTF-8")
        return subprocess.run(
            [sys.executable, "-m", "todo"] + list(argv),
            cwd=ROOT, env=env, capture_output=True, timeout=30,
        )

    def test_non_utf8_argv_is_bad_text(self):
        r = self.run_module(b"add", b"buy \xff\xfe milk")
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (1, b"", b"todo: bad text\n"))
        self.assertFalse(os.path.exists(self.path))
        self.write('{"next_id": 1, "items": []}')
        with open(self.path, "rb") as f:
            before = f.read()
        r = self.run_module(b"add", b"\xc3\x28")
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (1, b"", b"todo: bad text\n"))
        with open(self.path, "rb") as f:
            self.assertEqual(f.read(), before)

    def test_list_on_strict_utf8_stdout_does_not_crash(self):
        for n, text in enumerate(ACCEPTED_TEXTS, start=1):
            r = self.run_module("add", text)
            self.assertEqual((r.returncode, r.stdout, r.stderr),
                             (0, "added {}\n".format(n).encode(), b""))
        r = self.run_module(b"add", b"bad \xff")
        self.assertEqual(r.returncode, 1)  # rejected, so nothing stored
        r = self.run_module("list")
        self.assertEqual((r.returncode, r.stderr), (0, b""))
        expected = "".join("{} [ ] {}\n".format(n, t)
                           for n, t in enumerate(ACCEPTED_TEXTS, start=1))
        self.assertEqual(r.stdout.decode("utf-8"), expected)


if __name__ == "__main__":
    unittest.main()
