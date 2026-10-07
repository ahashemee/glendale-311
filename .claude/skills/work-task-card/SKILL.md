---
name: work-task-card
description: Work a task from docs/tasks/ end to end in the glendale-311-equity repo – branch, setup, the analysis within docs/ANALYSIS_STANDARDS.md, outputs, findings.md, the CHANGELOG line and a PR. Use when a teammate says "start my task", "work on my iteration 2 tasks", "continue my task", "what's next for me", or names their task file.
---

# Work a task

The task file says what to produce and what Ma'el is looking for. `docs/ANALYSIS_STANDARDS.md` says how. This skill joins the two with the repo's workflow.

## 0. Load context (once per session)

1. Read `CLAUDE.md`, then `docs/PROJECT.md` sections 2, 6 and 9, `docs/DATA_DICTIONARY.md` and `docs/ANALYSIS_STANDARDS.md`.
2. Read the user's task file in `docs/tasks/iterN-<name>.md` and the team dates in `docs/tasks/README.md`. Note the tasks, due dates and the "What I'm looking for" bullets; those bullets are the acceptance test.
3. Check `git log --oneline -10` for what's already done. Don't re-profile data the docs already describe.
4. Tell the user in two lines: which task is next and what it should produce. Ask only if the task file leaves a real gap.

## 1. Branch and setup

- `git checkout main && git pull`, then `git checkout -b feature/iterN-<topic>`. If the branch exists, check it out and pull instead.
- `pip install -r requirements.txt`.
- Confirm `data/cleaned/glendaleone_clean.csv` exists; if not, point the user to `data/cleaned/README.md` (team Drive download). Never fetch or commit raw data.
- Notebook: `notebooks/iterN_topic_owner.ipynb`. Outputs: the folder named in the task file under `outputs/iterN/`.

## 2. Do the work

- Start from the standard load block (`docs/ANALYSIS_STANDARDS.md` section 2) and its filters. Choose the method yourself within the standards; the task file names the method only where it matters.
- Keep the "What I'm looking for" bullets open and check each one against the result before moving on.
- Write the planned test in a markdown cell above the cell that runs it. Effect size first, exact p, association language only.
- If a number looks wrong or a filter removes far more than expected, stop and help the user post it under Problems in the group chat; don't "fix" the data.

## 3. Checks, outputs and findings.md

- Run the EDA, statistics and chart checks in `docs/ANALYSIS_STANDARDS.md` sections 5 to 7 and record them in the notebook.
- `findings.md` in the outputs folder: the findings with numbers and comparisons, the caveats (`[uncertain]` where unverified, "association, not cause"), the filter log.
- Restart the kernel and Run All once; it must finish without errors.

## 4. Commit and open the PR

Run the `log-change` skill: clear notebook outputs, add the CHANGELOG line, fill the PR body from `.github/PULL_REQUEST_TEMPLATE.md`. Push and open a draft PR titled `[iterN] topic – Owner` with the reviewer named in the task file. Mark it ready when the task is done and every "What I'm looking for" bullet is met. Never merge; Ma'el merges.

After the PR merges, if a finding changes the story, run `update-findings`.
