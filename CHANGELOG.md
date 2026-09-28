# Changelog

All notable changes to this repo, in the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Every PR adds at least one line; CI fails a PR that doesn't touch this file.

Line format, newest first within each section:

```
- YYYY-MM-DD (Name) [iterN-NN] what changed (path) – why
```

Use the card ID in the brackets; use `[setup]` for repo or tooling work that belongs to no card. Put a line under **Unreleased** while the PR is open for work that isn't tied to the current iteration; iteration work goes under that iteration's heading.

## Unreleased

## Iteration 2

- 2026-09-28 (Ma'el) [setup] Added the contribution guide and PR template, and documented the changelog format (CONTRIBUTING.md, .github/PULL_REQUEST_TEMPLATE.md, CHANGELOG.md) – every change is notated the same way
- 2026-09-28 (Ma'el) [setup] Added the living brief for Claude Code sessions (CLAUDE.md) – teammates' agents read the same questions, direction, rules and gotchas before working
- 2026-09-28 (Ma'el) [setup] Added the five Iteration 2 task cards, the card status table and the roadmap (docs/tasks/, docs/ROADMAP.md) – every teammate finds their card, dates, check-ins and risks in the repo
- 2026-09-28 (Ma'el) [setup] Copied the project docs into docs/ and added the team standards, decision log and findings file (docs/) – one place for context, with emails, the Gmail link and the distribution list removed
- 2026-09-28 (Ma'el) [setup] Added the cleaning script, the two small ACS tables and the data-landscape scripts (src/clean_data.py, data/cleaned/, src/landscape/) – the cleaning pipeline now runs from the repo root and teammates get the demographic inputs with the clone
- 2026-09-28 (Ma'el) [setup] Rewrote ignore rules and added scipy, seaborn and statsmodels (.gitignore, requirements.txt) – keep raw and large cleaned data out of git, share project skills, and cover the libraries the Iteration 2 cards use
