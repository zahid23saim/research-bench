"""Shared helpers: loading JSONL and normalizing answers for comparison."""

import json
import re
import unicodedata
from datetime import datetime, date

ANSWER_TYPES = {"exact", "number", "date"}

_DATE_FORMATS = (
    "%Y-%m-%d", "%d %B %Y", "%B %d, %Y", "%B %d %Y", "%d %b %Y", "%b %d, %Y",
    "%d-%b-%Y", "%d/%m/%Y", "%Y/%m/%d",
)


def load_jsonl(path):
    """Return a list of (line_number, object). Raises ValueError on bad JSON."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                rows.append((n, json.loads(line)))
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{n}: invalid JSON ({e.msg})") from None
    return rows


def norm_text(s):
    """Lowercase, strip accents and punctuation, collapse whitespace."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ł", "l").replace("Ł", "L")
    s = re.sub(r"[^\w\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def parse_number(s):
    m = re.search(r"-?\d[\d,]*\.?\d*", str(s))
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", ""))
    except ValueError:
        return None


def parse_date(s):
    s = re.sub(r"\s+", " ", str(s).strip().rstrip("."))
    s = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", s)
    s = re.sub(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),? ", "", s)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def is_correct(task, given):
    """True if `given` matches the task's answer under its answer_type."""
    kind = task.get("answer_type", "exact")
    if given is None or str(given).strip() == "":
        return False
    if kind == "number":
        got, want = parse_number(given), parse_number(task["answer"])
        return got is not None and want is not None and abs(got - want) <= float(task.get("tolerance", 0))
    if kind == "date":
        got, want = parse_date(given), parse_date(task["answer"])
        return got is not None and got == want
    accepted = {norm_text(task["answer"])} | {norm_text(a) for a in task.get("aliases", [])}
    return norm_text(given) in accepted
