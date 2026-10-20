"""Check every task against the authoring rules in README.md.

Usage: python scripts/validate.py tasks/tasks.jsonl [more.jsonl ...]
Exits 1 if any task has a problem.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import ANSWER_TYPES, load_jsonl, parse_date, parse_number  # noqa: E402

REQUIRED = ("id", "question", "answer", "answer_type", "primary_sources", "reasoning_path", "why_hard")
SECONDARY_HOSTS = ("wikipedia.org", "reddit.com", "quora.com", "medium.com")
RELATIVE_TIME = re.compile(r"\b(currently|current|now|today|latest|this year|recent(ly)?)\b", re.I)
POINTERS = re.compile(r"\b(see above|as mentioned|mentioned earlier|the above)\b", re.I)


def check_task(task, seen_ids):
    problems = []
    for key in REQUIRED:
        if key not in task or task[key] in ("", [], None):
            problems.append(f"missing '{key}'")
    tid = task.get("id")
    if tid in seen_ids:
        problems.append(f"duplicate id '{tid}'")
    kind = task.get("answer_type")
    if kind not in ANSWER_TYPES:
        problems.append(f"answer_type must be one of {sorted(ANSWER_TYPES)}")
    elif kind == "date" and parse_date(task.get("answer", "")) is None:
        problems.append("answer is not a parseable date (use YYYY-MM-DD)")
    elif kind == "number" and parse_number(task.get("answer", "")) is None:
        problems.append("answer is not a number")
    q = task.get("question", "")
    if RELATIVE_TIME.search(q):
        problems.append("question uses relative time (pin a date so the answer can't change)")
    if POINTERS.search(q):
        problems.append("question points elsewhere ('see above'); make it self-contained")
    sources = task.get("primary_sources") or []
    if not isinstance(sources, list):
        problems.append("primary_sources must be a list")
        sources = []
    for i, src in enumerate(sources, 1):
        url = (src or {}).get("url", "")
        if not url.startswith(("http://", "https://")):
            problems.append(f"primary source {i}: missing or invalid url")
        if any(h in url for h in SECONDARY_HOSTS):
            problems.append(f"primary source {i}: {url} is a secondary source, not a primary one")
        if not (src or {}).get("quote", "").strip():
            problems.append(f"primary source {i}: add the exact quote that contains the answer")
    if len(task.get("reasoning_path") or []) < 2:
        problems.append("reasoning_path should have at least 2 steps (single-hop questions are too easy)")
    return problems


def validate(paths):
    total_bad = 0
    for path in paths:
        seen = set()
        try:
            rows = load_jsonl(path)
        except (OSError, ValueError) as e:
            print(f"ERROR {e}")
            total_bad += 1
            continue
        if not rows:
            print(f"{path}: no tasks yet")
        for line, task in rows:
            problems = check_task(task, seen)
            seen.add(task.get("id"))
            if problems:
                total_bad += 1
                for p in problems:
                    print(f"FAIL {path}:{line} [{task.get('id', '?')}] {p}")
            else:
                print(f"ok   {path}:{line} [{task['id']}]")
    return total_bad


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(1 if validate(sys.argv[1:]) else 0)
