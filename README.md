# research-bench

A small BrowseComp / SimpleQA-style benchmark: questions that are **hard to find but easy to verify**, each with a **primary-sourced answer key**, plus tooling to grade model answers and review where a model's search went wrong.

- `tasks/tasks.jsonl`: the benchmark questions (one JSON object per line)
- `tasks/examples.jsonl`: two fully worked examples showing the expected quality
- `scripts/validate.py`: checks every task against the authoring rules below
- `scripts/grade.py`: scores a model's answers against the keys (CI-friendly exit code)
- `reviews/TEMPLATE.md`: template for diagnosing a failed model trajectory
- `tests/`: unit tests for the validator and grader (standard library only)

## Authoring rules

A task is only accepted if it meets all of these:

1. **Single, unambiguous answer.** One correct answer (aliases allowed: "Łukasz Langa" / "Lukasz Langa"). If two readings of the question are possible, rewrite it.
2. **Hard to find.** The answer should not be the first search result for the question. Good tasks need 2+ hops (find entity A, then use a fact about A to find B) or a document a casual search won't surface.
3. **Easy to verify.** Once found, a reviewer can confirm the answer in under a minute from the cited source.
4. **Primary-sourced.** At least one primary source (the official document, filing, record, or original publication) with an exact quote containing the answer. Wikipedia and news summaries can help you find the source but are not the key.
5. **Time-stable.** The answer won't change (no "current CEO", no live counts). If it could change, the question pins a date ("as of the 2019 release").
6. **Self-contained.** The question carries every detail needed; no "see above".

## Writing a task, step by step

1. **Question.** Pick a verifiable fact, then describe the entity indirectly so a solver needs 2+ hops, where each hop depends on the answer to the previous one. Don't name the starting document directly.
2. **Answer and evidence.** Record the single gold answer, plus the URL and exact quote for every hop.
3. **Loophole check.** Could two answers be defended? If so, tighten the wording. If the answer could change over time, add an "as of" date.
4. **`reasoning_path`.** The hops in order.
5. **`why_hard`.** The specific mistake you expect a model to make (for example, confusing one person's different roles across documents).
6. **Format.** Follow `tasks/examples.jsonl`; EX01 and EX02 show the standard.

Then run `validate.py`, and ask a model the question with browsing on. If it gets it right instantly, make the question harder.

## Task format

```json
{
  "id": "T001",
  "question": "…",
  "answer": "…",
  "answer_type": "exact | number | date",
  "aliases": ["…"],
  "tolerance": 0,
  "primary_sources": [{"url": "https://…", "quote": "exact text containing the answer", "accessed": "YYYY-MM-DD", "hop": 1}],
  "reasoning_path": ["hop 1 …", "hop 2 …"],
  "why_hard": "…",
  "author": "…"
}
```

- `exact`: case-, accent- and punctuation-insensitive match against `answer` or any alias.
- `number`: numeric match within `tolerance`.
- `date`: matched as a calendar date (accepts `2019-10-14`, `14 October 2019`, `October 14, 2019`, `14-Oct-2019`).

## Usage

```bash
python scripts/validate.py tasks/tasks.jsonl
python scripts/grade.py tasks/tasks.jsonl runs/<model>.jsonl
python -m unittest discover tests
```

A run file has one line per task: `{"id": "T001", "answer": "…"}`. The grader prints per-task PASS/FAIL, the score, and exits non-zero if any task fails.

## Reviewing failures

For each failed task, copy `reviews/TEMPLATE.md` to `reviews/<task-id>-<model>.md` and record the model's search trajectory, the first wrong step, and the root cause:

| Code | Failure | Example |
|---|---|---|
| WS | Wrong source | Trusted a forum post over the official document |
| PS | Premature stop | Answered from hop 1 without doing hop 2 |
| EC | Entity confusion | Mixed up two similarly named people or PEPs |
| MR | Misread source | Found the right page, extracted the wrong field |
| OI | Outdated information | Used a superseded version of the document |
| HC | Hallucinated citation | Cited a URL or quote that does not exist |
| RF | Refusal / gave up | Said it could not find the answer |

## Results

| Model | Date | Score | Main failure modes |
|---|---|---|---|
| _(add runs here)_ | | | |
