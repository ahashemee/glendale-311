---
name: update-findings
description: Fold an analysis result into docs/FINDINGS.md in the glendale-311-equity repo with its evidence path, tag it [uncertain] where warranted, and propose the matching edit to the Direction (living) section of CLAUDE.md. Use when a card's findings.md is reviewed or merged, when a result supports or weakens a working hypothesis, or when the user says "add this to findings", "update findings", "does this change the story".
---

# Update findings

`docs/FINDINGS.md` is the team's current state of knowledge, and the Direction section of `CLAUDE.md` is what every Claude session reads first. Both change only by PR, and only from evidence in the repo.

## 1. Gather the evidence

- Read the card's `outputs/iterN/<topic>/findings.md` and the CSV or chart behind each number.
- Confirm the result meets `docs/ANALYSIS_STANDARDS.md` sections 3 and 8: the window and denominator are named, the filter log adds up, one number was checked a second way. If not, stop and say what's missing.
- Only fold in results the reviewer has agreed with. Draft results stay in the card's own `findings.md`.

## 2. Write the entry

Add it under **Validated findings** in `docs/FINDINGS.md`, newest first, using the entry format shown in that file:

- One sentence with the number and its comparison ("X files N requests per 1,000 residents per year vs Y citywide").
- Evidence: the path to the card's `findings.md` and the file that holds the number.
- Card ID, merge date, window and denominator.
- Caveats: n = 6 where relevant, ACS margins of error, exclusions. Tag anything not verified `[uncertain]`.
- Which working hypothesis (H1, H2, H3) it bears on, and whether it supports it, weakens it or is unclear. Update that hypothesis's tag if the evidence warrants (`[unvalidated]` → `[supported]` or `[weakened]`), never to "proven".

Association language only ("is associated with", "lines up with"); never "causes" or "drives". Never copy a number from `docs/PROJECT.md` section 7. Use an en dash (–) where an em dash would go.

## 3. Propose the Direction edit

If the finding changes the story, draft the edit to **Direction (living)** in `CLAUDE.md`:
- Update the hypothesis lines and the "Validated findings" line.
- Bump "Last updated" to today's date.
- Keep `CLAUDE.md` under 150 lines.

Show the proposed Direction diff to the user and put it in the same PR, flagged for Ma'el in the PR body ("Direction edit proposed"). Ma'el decides at review; never merge it yourself.

## 4. Log it

Add a `CHANGELOG.md` line (see the `log-change` skill), e.g. `- YYYY-MM-DD (Name) [iter2-01] Added F-01 on the propensity gap (docs/FINDINGS.md) – reviewed result from iter2-01`.
