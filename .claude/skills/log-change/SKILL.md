---
name: log-change
description: Pre-commit and pre-PR ritual for the glendale-311-equity repo – clear notebook outputs, add the CHANGELOG line, make sure findings.md and docs/FINDINGS.md are current, and fill the PR body from the template. Use before any commit or push, or when the user says "commit this", "open the PR", "log this change", "ready for review", or when CI fails on the changelog or notebooks-clean check.
---

# Log a change

Every change in this repo is notated. CI blocks a PR that lacks a `CHANGELOG.md` line or has notebook outputs, so run this before every commit and every PR.

## 1. Clear notebook outputs

```bash
jupyter nbconvert --clear-output --inplace notebooks/<file>.ipynb
python .github/scripts/check_notebooks_clean.py      # must print "0 not clean"
```

## 2. Check what's staged

- `git status` and `git diff --stat`. Nothing from `data/raw/`, no `data/cleaned/glendaleone_clean.csv`, no file over 5 MB, no personal contact columns (`docs/PROJECT.md` 6.15).
- Only the task's own paths change: its notebook, `outputs/iterN/<topic>/`, plus `CHANGELOG.md` and (if needed) `docs/FINDINGS.md`, `CLAUDE.md`.

## 3. Add the CHANGELOG line

Under the current iteration heading in `CHANGELOG.md`, at the top of the list:

```
- YYYY-MM-DD (Name) [iterN] what changed (path) – why
```

Today's date, the owner's first name, the iteration (`[setup]` for repo work tied to none), the path touched, an en dash, then the reason in a few words. One line per meaningful change.

## 4. Findings

- The task's `outputs/iterN/<topic>/findings.md` reflects this change (findings, caveats, filter log; `docs/ANALYSIS_STANDARDS.md` section 4).
- If the change produces or changes a finding the reviewer has agreed, run `update-findings`.

## 5. Commit message and PR body

- Commit message: `<type>: <what>` with type one of `feat`, `fix`, `docs`, `chore`, `ci`, e.g. `feat: iter2 district time-to-close table`.
- PR body: copy `.github/PULL_REQUEST_TEMPLATE.md` and fill it in – task file, what changed, why, the checkboxes (tick only what is true), and the reviewer named in the task file.

## Writing rules for anything committed

Association language only, `[uncertain]` on unverified facts, numbers recomputed from code (never from `docs/PROJECT.md` section 7), and an en dash (–) where an em dash would go.
