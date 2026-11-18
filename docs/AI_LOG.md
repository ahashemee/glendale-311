# AI prompting-session log

The City of Glendale asked the team to document each AI prompting session: the model, the effort level, the reasoning trail, and any drift or wrong output that was caught. One entry per session, newest first. Each person logs their own sessions. Keep an entry short; point to files rather than pasting them.

Entry template:

```
## YYYY-MM-DD – who – what the session was for
- Model and effort:
- What it was asked to do:
- Reasoning trail (files that hold it):
- Key decisions, and who made them:
- Drift, wrong claims or tool trouble caught:
- What a person checked by hand:
```

## 2026-11-17 – Ma'el – Iteration 2 doc fixes, root-cause review and the Iteration 3 plan

- **Model and effort:** Claude Fable 5.2 as orchestrator, effort level high, in Claude Code. It planned, decided and reviewed; subagents did the reading, auditing, drafting and editing. 14 subagent runs: 1 Haiku (file inventory), 11 Sonnet (claims table, iteration 2 outcome, skill comparison, iteration 3 requirements, doc audit, doc edits, two evidence checks, debate record, work breakdown, task-file drafts), 2 Opus (the two debaters). No subagent ran on Fable. Three agents were reused by follow-up message rather than re-spawned.
- **What it was asked to do:** four phases with a checkpoint after each of the last three. (0) Map the project docs. (1) Find and fix doc inconsistencies left from Iteration 2. (2) Find the root causes of Iteration 2's late delivery before re-planning. (3) Plan Iteration 3 and write the task files.
- **Reasoning trail:** kept outside the repo in `PM drafts/iter3-plan/` – `context-map/` (five files and a README), `doc-audit.md` (36 inconsistencies, each with its decision), `evidence/E1` and `E2`, `ROOT_CAUSE.md` (seven why-chains, four root causes), `debate/` (two rounds from each side), `DEBATE.md` (record plus the decision), `decomposition.md`, `PLAN.md`.
- **Key decisions, and who made them:**
  - Ma'el approved the doc-fix list at checkpoint A, including a pointer in `ANALYSIS_STANDARDS.md` to the 2026-10-18 type-control decision.
  - The orchestrator named four root causes: the plan reached the repo after its own dates; setup and the repo step were never tested before a deadline; everyone was planned at or over capacity with the overflow going to Ma'el; commitments only Ma'el held had no second person.
  - Both debaters converged on one plan and both recommended cutting Code Compliance. The orchestrator did not accept the cut because it conflicted with Ma'el's stated scope. Ma'el ruled: plan everything, cut later.
  - The orchestrator's first decision (a day-2 setup gate, rotating peer checks) was withdrawn once Ma'el gave the due date, five days out. Ma'el chose to keep reviewing everything himself and to own the spatial join.
  - Ma'el approved the plan, three DECISIONS rows and this file at checkpoint C, and told the orchestrator to commit and push the branch.
- **Drift, wrong claims or tool trouble caught:**
  - The local checkout was on a stale branch, 15 commits behind `main`. Two subagents reported it; the orchestrator confirmed it with git before any edit. Edits were made on a new branch from `main`.
  - A context-map line said `docs/meetings/` did not exist. That was true only on the stale checkout; corrected.
  - The claims table said `main` was "5 PR merges ahead". It is 4 PRs and 15 commits. The audit subagent caught it.
  - The claims table listed several numbers as conflicts (row counts, no-district counts, the window end date). The audit showed they are different bases that reconcile, not conflicts.
  - The iteration 2 outcome map counted Shamie's hand-in as 7 CSV and 6 PNG files; a later check found 5 CSV and 7 PNG.
  - The orchestrator overstated its own subagent count by one in two status updates and corrected it.
  - The work-breakdown subagent assumed rotating peer checks, because its brief was written before Ma'el chose otherwise. `PLAN.md` overrides it.
  - Hour estimates in the plan are ranges carried over from superseded Iteration 2 cards or marked uncertain; none is a measurement.
  - Tool trouble: the repo folder is synced by iCloud, and most of the files inside `.git` had been evicted, so git froze for several minutes until they were downloaded again.
- **What was checked by hand:** the orchestrator read the full uncommitted diff after each edit pass and spot-checked nine audit rows against `main`. Ma'el answered every checkpoint. Not checked by a person: the evidence files' line citations beyond those spot checks, and the hour ranges.
- **Left open:** why each analyst's work started when it did in Iteration 2 (the retro rows are blank; the Wed 2026-11-18 post asks for one line each). The must-land tasks are roughly double regular weekly hours; Ma'el accepted that knowingly.
