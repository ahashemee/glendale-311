# Iteration 3 – Shamie

**Reviewer:** Ma'el · **Questions:** group chat, any time. Ask early.
How-to (load block, filters, chart rules): `docs/ANALYSIS_STANDARDS.md`. Notebook `notebooks/iter3_signatures_shamie.ipynb`; outputs go in `outputs/iter3/signatures/`.

## Tasks
| # | Task | Due |
|---|---|---|
| 1 | Post the three load-block counts (106,795 / 106,617 / 104,274) in the chat, plus one line on what stopped your Iteration 2 PR. | Wed 2026-11-18 21:00 |
| 2 | District request signatures (H2): do districts differ in the mix of request types, with and without Trash/Recycle? Post your first results table in the chat. | Thu 2026-11-19 21:00 |
| 3 | Check-in in the chat: done, left, blocked. Then hand in the finished piece: chi-square of district by request-type group, residual heatmap, Cramér's V, and what the residuals say about Assistance Programs. | Fri 2026-11-20 21:00 · **Fri 2026-11-20 23:59 (hard)** |
| 4 | Read the frozen deck and flag errors in the chat · rehearsal (one timed run) · present your part in class. | Sun 2026-11-22 15:00 · Sun 2026-11-22 18:00 · Mon 2026-11-23 |
| 5 | If time: both probability tables (type mix within each district, and district mix within each type). | Fri 2026-11-20 23:59 |
| 6 | If time: the limited-English column – what is it a share of? Restate the F-02 line or keep its caveat. | Fri 2026-11-20 23:59 |
| 7 | If time: district-similarity dendrogram (which districts file alike). | Fri 2026-11-20 23:59 |

Rows 5–7 are extras I may cut at the Fri 2026-11-20 21:00 check-in, last row first.

## What I'm looking for
- Does the equity signal sit in the mix of request types rather than in how many requests a district files, and is Assistance Programs concentrated in particular districts?
- Trash/Recycle is about half of all requests, so show every result with and without it. Six districts cannot show cause: write "lines up with", never "causes".
- If a date slips I check in that evening. After the hard date there are 12 hours of grace (to Sat 2026-11-21 12:00); after that the rest is cut or reassigned. You are second on this: ping me if I have not posted by Sat 2026-11-21 13:00 what is cut or reassigned. If the spatial join goes ahead, read its diff.
- Hand-in: a PR titled `[iter3] signatures – Shamie` (with a CHANGELOG line), OR the same files in [team Drive hand-in folder](https://drive.google.com/drive/folders/1AaF5CQWegTUGp6CNEyF4Se7mAMDvCIFw) if git gets in the way – either counts, and I land Drive hand-ins. Done means the notebook runs top to bottom, a cell writes every output file, and `findings.md` is filled in with numbered findings.
