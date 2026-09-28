### Card iter2-04 – Iteration 2 storyline and section copy – Akshara

**File:** `docs/tasks/iter2-04-storyline.md`
**Owner:** Akshara · **Reviewer:** Ma'el · **Type:** S (story) · **Estimate:** 3.5 h (2–5 h)
**Checkpoints:** outline posted by **Thu 2026-10-08**; full section copy by **Wed 2026-10-14** · **Hard or soft:** hard (content freeze is Fri 2026-10-16)
**Questions:** Ma'el in the group chat, any time.

**Why this matters.** The Iteration 2 grade is 10 points: Summary, Preliminary analysis, Visualization, Style, and Progress since Iteration 1. The analysis earns only part of that. The story decides whether the class sees progress and a clear direction. You proposed the HTML format and framed the problem last time, so you own the arc.

**Outcome.** `outputs/iter2/story/storyline.md` gives, section by section, what we say, which chart goes where, who speaks, and the transition line into the next section. Ma'el builds the HTML page from it on Oct 15–16.

**The brief: the rubric, word for word**
- *Summary of problem:* "clearly and succinctly provided a summary of the project."
- *Preliminary analysis:* "results of a preliminary analysis that is appropriate for the problem... interpretation accurate and clear... clear direction on the next steps."
- *Data visualization:* "aided in supporting the preliminary analysis... aesthetically pleasing and easy to interpret."
- *Presentation style:* "visually appealing... presented very professionally... did not appear unprepared."
- *Progress from prior iteration:* "clear and substantial progress since the last iteration."
- The assignment asks you to cover what we set out to do, whether expectations were met or changed, whether scope changed, and current challenges with plans to overcome them.

**Constraints (true limits)**
- The format is an HTML scrolling page, the same as Iteration 1.
- Every number comes from an analyst's `findings.md`. Until those exist, write `[[TBD: short-name]]` (e.g. `[[TBD: q1_top_vs_bottom_rate]]`), and Ma'el fills the tokens on Oct 14.
- Explain the scope change honestly. Iteration 1 promised "time to close vs City targets", but the targets table isn't downloaded yet, so Iteration 2 compares each request with the typical time for its type.
- Say "is associated with", never "causes". Talk about technical and data challenges only, and never criticize the City or the sponsor.
- Talk length: [uncertain; ask the professor or check Canvas] – plan for 10 minutes until confirmed.
- Every teammate presents the part they built.

**Preferences (optional; your call)**
- One idea: open with the "reporting-propensity paradox" question as the hook.
- Keep the Iteration 1 visual style so progress reads as continuity.

**Autonomy:** decide-and-tell on structure, wording, order and visual flow. Propose first before cutting any analysis from the talk.

**Steps**
1. Re-read the Iteration 1 HTML deck in the team Drive. List the 3 things we promised.
2. Draft the outline in `storyline.md`, one heading per section: Hook → Summary of problem → What we set out to do vs what we did (progress) → Finding 1: propensity gap → Finding 2: time-to-close → Context: trend → Challenges and how we'll handle them → Next steps for the final. Post it in the group chat by Thu 10-08.
3. For each section, write 2–4 sentences of speaker copy, the chart file it uses (`q1_rate_by_district.png`, `ttc_pct_slower_by_district.png` and so on), the speaker's name, and a one-line transition into the next section.
4. Swap placeholder tokens for real numbers only after the analyst PRs merge. Otherwise, leave them for Ma'el.
5. Commit on branch `feature/iter2-story`, open a PR and assign Ma'el, by Wed 10-14.

**Definition of done**
- [ ] Every rubric criterion maps to at least one section (write the criterion name in brackets next to the heading).
- [ ] Every section has copy, a chart (or "none"), a speaker and a transition.
- [ ] Every number is either from a `findings.md` or a `[[TBD]]` token.
- [ ] The scope-change paragraph is present.
- [ ] The PR is open with Ma'el as reviewer.
