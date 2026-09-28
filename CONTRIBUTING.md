# Contributing

How the four of us work in this repo. Claude Code sessions follow the same rules via `CLAUDE.md`.

## 1. One card, one branch, one PR

Every piece of work is a card in `docs/tasks/` with exactly one owner and one named reviewer.

1. Update `main` and branch off it:
   ```bash
   git checkout main && git pull
   git checkout -b feature/<short-name>        # e.g. feature/iter2-propensity
   ```
2. Set up once: `pip install -r requirements.txt`, then download `glendaleone_clean.csv` from the team Drive into `data/cleaned/` (see `data/cleaned/README.md`).
3. Work in `notebooks/iterN_topic_owner.ipynb`. Write outputs only to `outputs/iterN/<topic>/`. Follow `docs/ANALYSIS_STANDARDS.md`.
4. Before every commit: clear notebook outputs, add a CHANGELOG line, update `findings.md` (sections 3 to 5 below).
5. Push and open a **draft PR** by the card's draft date. Title: `[iterN-NN] topic – Owner`. Fill in every part of the PR template and assign the reviewer named on the card.
6. The reviewer comments within 24 h of being asked. Fix, push, and mark the PR ready when every definition-of-done box on the card is ticked.
7. Ma'el merges once the reviewer approves and both CI checks pass. Nobody pushes to `main` directly.

Never commit `data/raw/` or `data/cleaned/glendaleone_clean.csv` (`.gitignore` blocks both), and never force-push over someone else's work. Git trouble (conflicts, a data file committed by mistake): stop and tell Ma'el; he fixes it on a call.

## 2. Check-ins: Mon and Thu in the group chat

Post by 21:00 every Monday and Thursday, even when nothing moved:

```
Progress: what's done since the last post (a file, table or chart, not "worked on it")
Plans: what's next, before the next check-in
Problems: what's blocking you, and who can unblock it (or "none")
```

It should take 30–60 seconds to read. If you are stuck for more than 30 minutes, post it under Problems right away; don't wait for the next check-in. Silence is read as a red flag, so a short "no change" post beats no post.

### Missed deadlines and handoffs

- **At the due time:** Ma'el checks in the same evening: what's done, what's left. No blame.
- **Grace window of 24 h:** finish, or post the partial work as a draft PR.
- **After 24 h:** the remaining work is reassigned. What's done is merged or saved, and the owner writes a handoff:
  ```
  Goal: one line, what the card was for
  Done: each item with its file path
  In progress: what's half-done, and where
  Blocked: what's blocking it, and who can unblock it
  Open decisions: the question / the options / the owner's lean / what forces the choice
  ```
  Don't invent decisions that weren't made; write "not decided" instead. The new owner gets a follow-up card that says what's done, what remains and what went wrong, rather than a copy of the old card.
- It is recorded in the retro as a process issue (card too big? unclear step? overloaded week?), never as a verdict on a person.

## 3. Write a CHANGELOG line

Every PR adds at least one line to `CHANGELOG.md`; CI fails the PR otherwise. Add it under the current iteration heading, at the top:

```
- YYYY-MM-DD (Name) [iterN-NN] what changed (path) – why
```

Example: `- 2026-10-08 (Shenoy) [iter2-02] Added the district time-to-close table and tests (outputs/iter2/time_to_close/) – first cut for the draft PR`

One line per meaningful change; a PR can add several. A PR that truly needs no line (for example a typo fix) can carry the `no-changelog` label, which only Ma'el applies.

## 4. Update `docs/FINDINGS.md`

When your PR produces or changes a finding:

1. Write the finding in your `outputs/iterN/<topic>/findings.md` first (number, comparison, caveats, filter log).
2. In `docs/FINDINGS.md`, add an entry under **Validated findings** once the reviewer agrees, using the entry format in that file: the finding, the evidence path, the card, the window and denominator, caveats, and which hypothesis it bears on.
3. Tag anything not verified `[uncertain]`. Use association language only.
4. If the finding changes the story, propose the edit to the **Direction (living)** section of `CLAUDE.md` in the same PR and bump its "last updated" date. Ma'el decides at review.

## 5. Clear notebook outputs

CI fails a PR if any notebook under `notebooks/` has outputs or execution counts. Before committing:

```bash
jupyter nbconvert --clear-output --inplace notebooks/<your_notebook>.ipynb
```

(Or in Jupyter: Kernel → Restart & Clear Output, then save.)

## 6. Writing style

- Number anything that reaches a slide from code in this repo, never from `docs/PROJECT.md` section 7.
- "Is associated with", never "causes".
- Mark unverified facts `[uncertain]`.
- Where an em dash would go, type an en dash (–); otherwise a plain hyphen.

Questions go to Ma'el in the group chat.
