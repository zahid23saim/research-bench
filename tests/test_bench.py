import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from common import is_correct, parse_date  # noqa: E402
from grade import grade  # noqa: E402
from validate import check_task, validate  # noqa: E402


def good_task(**over):
    t = {
        "id": "T1",
        "question": "Who was the release manager for Python 3.8?",
        "answer": "Łukasz Langa",
        "answer_type": "exact",
        "aliases": ["Lukasz Langa"],
        "primary_sources": [{"url": "https://peps.python.org/pep-0569/", "quote": "3.8 Release Manager: Łukasz Langa"}],
        "reasoning_path": ["find the release schedule PEP", "read the release manager field"],
        "why_hard": "two hops",
    }
    t.update(over)
    return t


def write_jsonl(rows):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
    f.close()
    return f.name


class MatchingTests(unittest.TestCase):
    def test_exact_ignores_case_accents_and_punctuation(self):
        t = good_task()
        self.assertTrue(is_correct(t, "lukasz langa"))
        self.assertTrue(is_correct(t, "Łukasz Langa."))
        self.assertFalse(is_correct(t, "Guido van Rossum"))
        self.assertFalse(is_correct(t, ""))

    def test_date_formats(self):
        t = good_task(answer="2019-10-14", answer_type="date")
        for s in ("2019-10-14", "14 October 2019", "October 14, 2019", "14-Oct-2019", "Monday, 2019-10-14"):
            self.assertTrue(is_correct(t, s), s)
        self.assertFalse(is_correct(t, "2019-10-15"))
        self.assertIsNone(parse_date("sometime in 2019"))

    def test_number_tolerance(self):
        t = good_task(answer="1,250", answer_type="number", tolerance=5)
        self.assertTrue(is_correct(t, "1253"))
        self.assertFalse(is_correct(t, "1300"))


class ValidatorTests(unittest.TestCase):
    def test_good_task_passes(self):
        self.assertEqual(check_task(good_task(), set()), [])

    def test_catches_common_mistakes(self):
        bad = good_task(
            question="Who is currently the release manager, as mentioned above?",
            primary_sources=[{"url": "https://en.wikipedia.org/wiki/Python", "quote": ""}],
            reasoning_path=["one hop"],
        )
        problems = " | ".join(check_task(bad, {"T1"}))
        for expected in ("duplicate id", "relative time", "self-contained", "secondary source", "exact quote", "at least 2 steps"):
            self.assertIn(expected, problems)

    def test_examples_file_is_valid(self):
        self.assertEqual(validate([str(ROOT / "tasks" / "examples.jsonl")]), 0)


class GraderTests(unittest.TestCase):
    def test_grade_counts_missing_answers_as_failures(self):
        tasks = write_jsonl([good_task(), good_task(id="T2", answer="2019-10-14", answer_type="date")])
        run = write_jsonl([{"id": "T1", "answer": "Lukasz Langa"}, {"id": "X9", "answer": "?"}])
        try:
            results, unknown = grade(tasks, run)
            self.assertEqual([(r[0], r[1]) for r in results], [("T1", True), ("T2", False)])
            self.assertEqual(unknown, ["X9"])
        finally:
            os.unlink(tasks)
            os.unlink(run)

    def test_attempted_only_skips_unanswered_tasks(self):
        tasks = write_jsonl([good_task(), good_task(id="T2", answer="2019-10-14", answer_type="date")])
        run = write_jsonl([{"id": "T1", "answer": "Lukasz Langa"}])
        try:
            results, _ = grade(tasks, run, attempted_only=True)
            self.assertEqual([(r[0], r[1]) for r in results], [("T1", True)])
        finally:
            os.unlink(tasks)
            os.unlink(run)


if __name__ == "__main__":
    unittest.main()
