"""Grade a model's answers against the answer keys.

Usage: python scripts/grade.py [--attempted] tasks/tasks.jsonl runs/<model>.jsonl
A run file has one line per task: {"id": "T001", "answer": "..."}.
Missing answers count as failures, unless --attempted is given, which grades
only the tasks the run answered (for partial runs). Exits 1 if any task fails.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import is_correct, load_jsonl  # noqa: E402


def grade(tasks_path, run_path, attempted_only=False):
    tasks = {t["id"]: t for _, t in load_jsonl(tasks_path)}
    answers = {r["id"]: r.get("answer") for _, r in load_jsonl(run_path)}
    if attempted_only:
        tasks = {tid: t for tid, t in tasks.items() if tid in answers}
    results = []
    for tid, task in tasks.items():
        given = answers.get(tid)
        ok = is_correct(task, given)
        results.append((tid, ok, given, task["answer"]))
    unknown = sorted(set(answers) - set(tasks))
    return results, unknown


def main(argv):
    attempted_only = "--attempted" in argv
    args = [a for a in argv[1:] if a != "--attempted"]
    if len(args) != 2:
        print(__doc__)
        return 2
    results, unknown = grade(args[0], args[1], attempted_only)
    for tid, ok, given, want in results:
        if ok:
            print(f"PASS {tid}")
        else:
            shown = "<no answer>" if given in (None, "") else repr(given)
            print(f"FAIL {tid}: got {shown}, expected {want!r}")
    for tid in unknown:
        print(f"WARN answer for unknown task id {tid!r} ignored")
    passed = sum(ok for _, ok, _, _ in results)
    print(f"\nScore: {passed}/{len(results)}")
    return 0 if results and passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
