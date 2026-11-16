"""P2-1 c1: concurrent `add` runs in separate processes never lose an item or reuse an ID (D-4)."""

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RUNS = 50

# Each worker waits for the start file, so both begin together, then runs
# `python3 -m todo add` RUNS times and prints one JSON line per run.
WORKER = r"""
import json, os, subprocess, sys, time
go, name, runs = sys.argv[1], sys.argv[2], int(sys.argv[3])
deadline = time.monotonic() + 30
while not os.path.exists(go):
    if time.monotonic() > deadline:
        sys.exit("worker {}: start file never appeared".format(name))
    time.sleep(0.001)
for i in range(runs):
    r = subprocess.run(
        [sys.executable, "-m", "todo", "add", "{} {}".format(name, i)],
        capture_output=True, text=True,
    )
    print(json.dumps({"code": r.returncode, "out": r.stdout, "err": r.stderr}), flush=True)
"""


class ConcurrentAddTest(unittest.TestCase):
    def test_two_processes_adding_50_each_leave_100_distinct_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "todo.json")
            go = os.path.join(tmp, "go")
            env = dict(os.environ, TODO_FILE=path)
            workers = [
                subprocess.Popen(
                    [sys.executable, "-c", WORKER, go, name, str(RUNS)],
                    cwd=ROOT, env=env, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True,
                )
                for name in ("a", "b")
            ]
            time.sleep(0.2)  # let both workers start and reach the wait loop
            open(go, "w").close()

            results = []
            for worker in workers:
                out, err = worker.communicate(timeout=300)
                self.assertEqual(worker.returncode, 0, err)
                runs = [json.loads(line) for line in out.splitlines()]
                self.assertEqual(len(runs), RUNS)
                results.extend(runs)

            failures = [r for r in results if r["code"] != 0]
            self.assertEqual(failures, [])
            added = sorted(int(r["out"].split()[1]) for r in results)
            self.assertEqual(added, list(range(1, 2 * RUNS + 1)))

            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            ids = [item["id"] for item in data["items"]]
            self.assertEqual(len(ids), 2 * RUNS)
            self.assertEqual(len(set(ids)), 2 * RUNS)
            texts = {item["text"] for item in data["items"]}
            expected = {"{} {}".format(n, i) for n in ("a", "b") for i in range(RUNS)}
            self.assertEqual(texts, expected)


if __name__ == "__main__":
    unittest.main()
