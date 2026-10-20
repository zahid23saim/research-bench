# Trajectory review: EX02 · example-run (illustrative)

This is a worked example of the review format, using the sample answers in `runs/example-run.jsonl`. Real reviews should paste the model's actual search log.

**Question:** Who was the release manager for the first Python version that included assignment expressions (the 'walrus operator', :=)?

**Expected answer:** Łukasz Langa  **Model answer:** Guido van Rossum

## Trajectory

| # | Action (search query / page opened) | What the model concluded |
|---|---|---|
| 1 | search: "walrus operator python release manager" | Results dominated by the PEP 572 controversy and Guido stepping down |
| 2 | opened PEP 572 | Saw Guido van Rossum among the authors and as BDFL at the time |
| 3 | (no further search) | Answered "Guido van Rossum" |

## First wrong step

Step 3. The model stopped after one document and treated "a prominent person on PEP 572" as "the release manager".

## Root cause

Code: **PS** (premature stop), with **EC** (entity confusion: author or BDFL mistaken for release manager).

Why: the question needs a second hop. PEP 572 only gives the version (3.8); the release manager is in PEP 569, the 3.8 release schedule.

## Would a better question have prevented it?

No. The question names the role ("release manager") explicitly, so the failure is the model's, not ambiguity in the question.
