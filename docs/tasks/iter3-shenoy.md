# Iteration 3 – Shenoy

**Reviewer:** Ma'el · **Questions:** group chat, any time. Ask early.
How-to (load block, filters, chart rules): `docs/ANALYSIS_STANDARDS.md`. Notebook `notebooks/iter3_code_compliance_shenoy.ipynb`; outputs go in `outputs/iter3/code_compliance/`.

## Tasks
| # | Task | Due |
|---|---|---|
| 1 | Post the three load-block counts (106,795 / 106,617 / 104,274) in the chat, plus one line on what held up your Iteration 2 PR. | Wed 2026-11-18 21:00 |
| 2 | Code Compliance, citywide: the top case types against GlendaleOne's top request groups, as a share and per 1,000 residents. You need two files I put on Drive by Wed 2026-11-18 21:00 (the filtered Code Compliance file and the request-type catalog). If they are not there, start row 6 instead and say so in the chat. Post your first results table. | Thu 2026-11-19 21:00 |
| 3 | Check-in in the chat: done, left, blocked. Then hand in the finished citywide comparison. | Fri 2026-11-20 21:00 · **Fri 2026-11-20 23:59 (hard)** |
| 4 | Read the frozen deck and flag errors in the chat · rehearsal (one timed run) · present your part in class. | Sun 2026-11-22 15:00 · Sun 2026-11-22 18:00 · Mon 2026-11-23 |
| 5 | If time: the same by district (cases per 1,000 residents and type mix). Only if I post the district file by Thu 2026-11-19 21:00; if I post "no-go", skip it. | Fri 2026-11-20 23:59 |
| 6 | If time: Residential - Container Damaged requests per 1,000 residents by district against median household income (does the F-02 income pattern come from this one type?). | Fri 2026-11-20 23:59 |
| 7 | If time: share of closed requests past their type's escalation time, by district and request group, with the unmatched types reported. | Fri 2026-11-20 23:59 |

Rows 5–7 are extras I may cut at the Fri 2026-11-20 21:00 check-in, last row first.

## What I'm looking for
- Do the problems reported to Code Compliance look like the ones residents report through GlendaleOne? Say how many code cases you could not place in a request group.
- Six districts cannot show cause: write "lines up with", never "causes". For row 7 say "past the escalation time", not "late" – we have not confirmed it is the City's target.
- If a date slips I check in that evening. After the hard date there are 12 hours of grace (to Sat 2026-11-21 12:00); after that the rest is cut or reassigned.
- Hand-in: a PR titled `[iter3] code_compliance – Shenoy` (with a CHANGELOG line), OR the same files in [team Drive hand-in folder](https://drive.google.com/drive/folders/1AaF5CQWegTUGp6CNEyF4Se7mAMDvCIFw) if git gets in the way – either counts, and I land Drive hand-ins. Done means the notebook runs top to bottom, a cell writes every output file, and `findings.md` is filled in with numbered findings.
