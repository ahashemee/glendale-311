---
name: work-task-card
description: Work a task card from docs/tasks/ end to end in the glendale-311-equity repo – branch, setup, the card's steps, the checks in docs/ANALYSIS_STANDARDS.md, outputs, findings.md, the CHANGELOG line and a PR from the template. Use when a teammate says "start my card", "work iter2-02", "continue my task", "what's next on my card", or names a card ID or card file.
---

# Work a task card

The card is the brief. This skill wraps it in the repo's workflow; it never overrides what the card says. When a card and `docs/ANALYSIS_STANDARDS.md` disagree, the card wins for that task and the difference goes in `findings.md`.

## 0. Load context (once per session)

1. Read `CLAUDE.md`, then `docs/PROJECT.md` sections 2, 6 and 9, `docs/DATA_DICTIONARY.md` and `docs/ANALYSIS_STANDARDS.md`.
2. Read the whole card in `docs/tasks/`. Note its owner, reviewer, dates, inputs, outputs (exact file names and columns) and definition of done.
3. Check the card's row in `docs/tasks/README.md` and `git log --oneline -10` to see what's already done. Don't re-profile data the docs already describe.
4. Tell the user in two lines: the outcome and the first step. Ask only if the card leaves a real gap.

## 1. Branch and setup

- `git checkout main && git pull`, then `git checkout -b feature/<short-name>` using the name on the card (or `feature/iterN-topic`). If the branch exists, check it out and pull instead.
- `pip install -r requirements.txt`.
- Confirm `data/cleaned/glendaleone_clean.csv` exists; if not, point the user to `data/cleaned/README.md` (team Drive download). Never fetch or commit raw data for card work.
- Create the notebook `notebooks/iterN_topic_owner.ipynb` and the folder `outputs/iterN/<topic>/` named on the card.

## 2. Do the steps

- Follow the card's steps in order. Paste code blocks as given; start from the standard load block (`docs/ANALYSIS_STANDARDS.md` section 2) where the card does.
- Compare every printed result with the card's expected value. If one is far off, stop and help the user post it under Problems in the group chat; don't "fix" the data.
- Write the planned test in a markdown cell above the cell that runs it.
- Anything the card marks "propose first" or "ask before doing" goes to Ma'el before you do it.

## 3. Run the checks

Work through `docs/ANALYSIS_STANDARDS.md` and record results in the notebook:
- Section 5 (EDA checks) – filter log adds up, grain, uniqueness, 6 districts, ranges.
- Section 6 (statistics rules) – effect size leads, exact p, n = 6 is descriptive, no causal words.
- Section 7 (chart standard and chart checks) – finding in the title, bars from zero, one hue, source note, 200 dpi.
- Section 8 (QA checklist) – these boxes get ticked in the PR body.
Plus the checks listed on the card itself.

## 4. Outputs and findings.md

- Every file in the card's Outputs table exists in `outputs/iterN/<topic>/` with exactly those columns.
- `findings.md` follows `docs/ANALYSIS_STANDARDS.md` section 4: the findings with numbers and comparisons, caveats (`[uncertain]` where unverified, "association, not cause"), and the filter log.
- Restart the kernel and Run All once; it must finish without errors.

## 5. Commit and open the PR

Run the `log-change` skill: clear notebook outputs, add the CHANGELOG line, update findings, fill the PR body from `.github/PULL_REQUEST_TEMPLATE.md`. Then push and open a draft PR titled `[iterN-NN] topic – Owner`, with the card's reviewer. Mark it ready only when every definition-of-done box on the card is ticked. Never merge; Ma'el merges.

After the PR merges, if a finding changes the story, run `update-findings`.
