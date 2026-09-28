# Iteration 1 Proposal — Glendale 311 / Code Compliance Equity Analysis

*CIS 450 Group Project — answers below reflect what the team agreed on in our meeting, organized against the assignment's required proposal content.*

## 1. Introduction of the team

Our team is a four-person group in ASU's CIS 450 capstone class: Ma'el Hashemee, Akshara Annu, Shenoy Gladwin, and Shamie Reyes. For this iteration, work is split as follows:

- **Shenoy** — team introduction, organization background, and how we obtained our data
- **Akshara** — problem statement, and building/refining the presentation
- **Ma'el** — process and tools, meeting notes, and generating the presentation
- **Shamie** — current challenges and how we plan to overcome them

## 2. Introduction of the organization

We are working with the **City of Glendale, Arizona**, specifically its **Office of Organizational Performance / Data team**. Our client contact is **Stephen Gushue**, who brought this project to the class.

The subject of the project is **GlendaleOne**, the City's 311 non-emergency service request system, alongside the City's related **Code Compliance** case system. In the client's own words:

> "GlendaleOne is the City of Glendale's 311 service where residents can provide feedback and requests for issues they are experiencing. It is a part of our objective of greater transparency and improving the lives of the people we serve every day."

The City gave us two full datasets (GlendaleOne External Requests and Code Compliance Cases, together over 160,000 records) plus twelve demographic/income workbooks — one population file and one demographic file for each of Glendale's six Council Districts. The sponsor was very responsive and had data ready for us immediately, which puts us in a strong position compared to some of the other project groups.

## 3. The problem the organization wants addressed

The City's core interest is **service equity across its six Council Districts** — whether residents across Glendale are being served, and are reporting problems, in comparable ways. The sponsor's email framed this as five questions:

1. Are the request counts distributed equitably based on Council District populations?
2. What are the top 10 (or so) request types, and how do they differ between GlendaleOne requests and Code Compliance requests?
3. What are the probabilities of certain request types coming from each district?
4. What are the similarities and disparities in request counts and types across districts?
5. Any other items of interest the City may not already be seeing.

As a group, we agreed to approach this as one combined problem rather than several disconnected ones, since the questions build on each other: **are 311 and code compliance requests distributed across districts in proportion to population, and do the *types* of requests a district generates reflect its population's characteristics?**

For this first iteration, we scoped that down to three concrete questions we can act on right away, with room to add more variables (income, language, renter vs. owner, age) in later iterations:

1. **How many requests are received per district, normalized by population** (requests per 1,000 residents)?
2. **What are the most frequently repeated request types per district?**
3. **How quickly are requests resolved per district**, relative to the response targets the City sets for each request type?

The sponsor made clear he wants to see *how* we plan to approach the problem for this iteration, not a finished solution — we'll refine based on his and the professor's feedback each round. That said, our goal is to go beyond pure description and offer a real recommendation once we've done the analysis (e.g., "district X has unusually high per-capita requests for reason Y — the City should/shouldn't reallocate resources accordingly").

## 4. Sample of what our output will look like

For this iteration, our planned output is a set of exploratory visualizations built around the three questions above:

- A **bar chart** showing total requests per district, and requests per 1,000 residents, side by side, to make the population-normalized comparison visible at a glance.
- A **choropleth / heat map** of Glendale's six districts, shaded by request rate, with GlendaleOne requests and Code Compliance cases shown separately since they behave differently.
- A **trend chart** showing request volume by district over time, using the historical data the City gave us (2020–2024) plus their projected figures through 2031.

These are our starting visuals for the population/volume question. In later iterations we plan to layer in additional variables — income, language spoken, renter vs. owner status — to explain *why* districts differ, and to explore response-time equity (whether some districts wait longer than the City's own published targets).

## 5. Steps to produce this output

**Data sources:**
- **GlendaleOne External Requests** and **Code Compliance Cases** — the City's two request datasets, downloaded from its public ArcGIS data feeds.
- **Twelve Esri demographic/income workbooks**, two per Council District (six districts total), covering population, income, household size, age, language, disability status, housing tenure, and more.
- Historical data spans 2020–2024, with the City's own projections through 2031.

**Software / tools:**
- **Python** (pandas for data cleaning and analysis) — the team agreed this is straightforward exploratory analysis, not machine learning, so Python is more than sufficient.
- **Geopandas** for mapping districts to the data and building the heat maps (Ma'el has prior experience with this from his Barrett honors thesis).
- We may bring in **Claude/ChatGPT** to help generate analysis scripts as needed.

**Process:**
1. Clean and join the two request datasets to their respective Council Districts.
2. Normalize request counts by district population to get a per-1,000-residents rate — this controls for the fact that districts simply have different numbers of people.
3. Identify the most common request types within each district and compare across districts.
4. Measure how long requests take to resolve per district, relative to the City's published response-time targets for each request type.
5. Visualize all of the above (bar charts, heat map, trend chart) and use the results to decide which single variable (income, language, tenure, etc.) looks like the strongest explanatory factor to dig into for the next iteration.
6. Use whatever patterns emerge here to identify underserved areas or underreporting — i.e., places where residents may not be filing requests even though issues exist — as a "level two" analysis once the basic volume picture is established.

We intentionally kept the scope of this iteration narrow (population only) because it's easier to expand scope later than to cut it down after committing to too much.

## 6. Current challenges and how we'll overcome them

**Challenge: turning good data into a meaningful conclusion.** We have a lot of raw data, but the data itself won't clearly announce "here's something significant" — any explanation we propose (e.g., "district X reports less because of language barriers" or "because residents are busier") is ultimately an assumption sitting on top of another assumption. Right now we don't have a way to independently verify *why* a pattern exists, only that it exists.

**How we'll address it:** We plan to talk to both the professor and Stephen (our sponsor) about how rigorously we need to support our assumptions — whether that means running statistical tests to check that a pattern isn't due to chance, or simply being explicit in our presentation about which claims are grounded in the data versus which are our best-guess interpretation. The goal is to make sure any explanation we offer is reasoned from evidence, not just a plausible-sounding story.

## 7. Anticipated future problems

- **Distinguishing correlation from explanation.** Even after we find that certain districts report more or less per capita, we may not be able to cleanly prove *why* — multiple variables (income, language, housing tenure, general busyness) could plausibly explain the same pattern, and the data may not let us isolate one cause.
- **Scope management.** The City gave us a large amount of data and several possible angles (population, income, request type, response time, underreporting). We'll need to consciously narrow to the highest-value questions each iteration rather than trying to answer everything at once.
- **Measuring what isn't in the data.** One of our more interesting ideas — figuring out whether certain neighborhoods systematically under-report problems relative to how many issues likely exist — is hard to measure directly, since by definition we only see requests that were filed, not the ones that weren't.
- **Getting sponsor input on interpretation.** Some open questions (e.g., how to interpret a lack of reporting, or which population figures the City itself considers authoritative) will likely need direct clarification from Stephen before we can finalize our approach for later iterations.
