---
title: "Beyond the Barcode: Building a parkrun Analytics Engine and What It Taught Me About Data Governance"
date: 2026-09-02
category: "Projects"
tags:
  - Data Visualisation
  - Data Quality
  - Data Modelling
  - Architecture
  - Just for Fun
description: "How a weekend side project extracting and normalising parkrun data revealed core lessons about self-service analytics, edge-case reconciliation, and the subtle danger of biased metric design."
featured: false
---

## Introduction

Every Saturday morning at 9:00 AM across the UK, hundreds of thousands of runners, joggers, and walkers assemble in public parks for parkrun. It is one of the most successful community health movements in modern history. It is also, beneath the surface, an enormous operational data capture exercise.

A unique barcode is scanned at the end of the event, matched to a finish token position, synced against stopwatch timer files (now from a phone), and published onto a centralised website within hours, or at my juniors event normally by 9:30am!

As a runner who has spent years running, walking, and volunteering at these events, I appreciate the simplicity of the output. But as a data professional, I find the native reporting frustrating, I want to break it down in hundreds of different ways! The official profile gives you a chronological table of finishes, a list of course personal bests (PBs), and a high-level summary of volunteer roles.

What it does not easily show you are the deeper, more nuanced analytical dimensions:

- How does a hilly, muddy trail event compare to a pancake-flat tarmac promenade when evaluating true physical effort? (Recently for me, harder courses are faster!)
- What was the actual longevity of your personal bests — how many days and events did a hard-won time withstand before falling?
- How does your volunteer contribution genuinely stack up against your running participation, particularly when you fulfil multiple duties on a single morning?
- Where does a given performance sit historically in the context of that specific calendar month across your entire running career? Totally not because my monthly PBs are generally easier to beat than my all time PB.

To answer these questions, I built a **parkrun Story Visualiser**: an interactive, single-file browser application designed to extract, model, cleanse, and visualise individual parkrun journeys.

What began as a light-hearted home project quickly evolved into a self lesson in data ingestion constraints, schema reconciliation, metric bias, and user-defined dimensional modelling (if you want AI to put snazzy names on it).

Here is what I built, how it works, and the broader data architecture and lessons that emerged along the way. This post is much more about the fun I had along the way than anything else.

[If you want to have a look, go here.](https://garymanleydata.github.io/MyDataHub/myParkrunBreakdown.html)


---

## The Problem: Data Trapped in Silos Behind Rigid Interfaces

The native parkrun profile interface operates primarily as an operational record of event participation rather than an analytical engine.

If you want to understand trends or benchmark your journey, you quickly run into three structural challenges.

### 1. Fragmentation of Operational Views

Your full running history lives on an `/all/` subpath, whilst your volunteer summary lives on the root profile page.

Historical year-by-year volunteering credits are not surfaced as an accessible aggregate time-series. Though this is available from the official parkrun app, which most volunteers will have. 

### 2. Terrain: The Pancake vs Mountain Fallacy

An 18:30 on a windy gravel trail with 120 metres of climbing is treated identically to an 18:30 on a sheltered, tarmac seaside promenade.

There is no native mechanism to adjust for course difficulty or assign a handicap to evaluate equivalent effort.

### 3. Pace and Position Bias

The standard reporting emphasises outright finishing positions and speed personal bests.

For slower participants, masters runners, or those recovering from injury, finish positions alone fail to tell the story of consistency, age-graded quality, or multi-year dedication.

I wanted a self-contained dashboard where any participant — whether they run 16 minutes or 60 minutes, whether they have completed 10 runs or 800 runs — could drop in their data and immediately see their story brought to life.

---

## Context & Architecture: Client-Side Pragmatism vs Over-Engineering

When designing personal projects, the initial engineering instinct is often to over-architect: spin up a headless browser container, deploy Python scraping pipelines on a cloud server, dump the output into an operational database, and point a business intelligence tool at the semantic layer. I know because I did think of doing it!

I deliberately rejected that architecture for two reasons: **ethical stewardship and accessibility**.

### Respecting Community Infrastructure

parkrun is a free, volunteer-led charity. Hammering their web servers with programmatic API scrapers, Selenium headless bots, or high-frequency automated batch jobs is poor community etiquette.

Furthermore, their front-end architecture is protected by Cloudflare and aggressive bot detection. Firing off sequential HTTP requests across dozens of pages will rightly get an IP address throttled or banned.

### Zero-Friction Portability

If an analytics tool requires Docker containers, Python environments, and database credentials, nobody else will ever use it.

I wanted a zero-install, zero-infrastructure architecture: a single, self-contained html file incorporating Tailwind CSS for design, Chart.js for data visualisation, and PapaParse for CSV ingestion (if needed), with data persisted locally in the user's browser via the Web Storage API. My natural land is SQL and Python so I did have helped from AI on a few aspects of this problem. 

To solve the ingestion challenge without hitting servers, I turned to the browser bookmarklet.

By having the user navigate to their own authenticated profile page and execute a browser bookmarklet, the browser's own JavaScript engine extracts the table directly from the DOM and writes a structured JSON payload directly to the user's clipboard.

Here is the lightweight bookmarklet logic I developed to extract the full running history from `/all/`:

```javascript
javascript:(function(){
    const rows = document.querySelectorAll('table tbody tr');

    if(!rows.length){
        alert('No parkrun table found on this page!');
        return;
    }

    const data = Array.from(rows).map(row => {
        const cells = row.querySelectorAll('td');

        if(cells.length < 6) return null;

        return {
            event: cells[0]?.innerText.trim(),
            date: cells[1]?.innerText.trim(),
            runNumber: cells[2]?.innerText.trim(),
            position: cells[3]?.innerText.trim(),
            time: cells[4]?.innerText.trim(),
            ageGrade: cells[5]?.innerText.trim()
        };
    }).filter(Boolean);

    const jsonString = JSON.stringify(data, null, 2);

    navigator.clipboard.writeText(jsonString).then(() => {
        alert(`Successfully extracted ${data.length} runs!\n\nCopied to clipboard.`);
    }).catch(err => {
        alert('Clipboard access failed. Check your browser console.');
    });
})();
```

And similarly, for the volunteering summary table located on the runner's profile root page:

```javascript
javascript:(function(){
    const tables = document.querySelectorAll('table');
    let volTable = null;

    tables.forEach(t => {
        if(t.innerText.toLowerCase().includes('volunteer')){
            volTable = t;
        }
    });

    if(!volTable){
        alert('No volunteer table found on this page!');
        return;
    }

    const rows = volTable.querySelectorAll('tr');
    const volunteering = [];

    rows.forEach(row => {
        const cells = Array.from(
            row.querySelectorAll('th, td')
        ).map(c => c.innerText.trim());

        if(cells.length >= 2){
            volunteering.push({
                role: cells[0],
                count: cells[1]
            });
        }
    });

    const jsonString = JSON.stringify(volunteering, null, 2);

    navigator.clipboard.writeText(jsonString).then(() => {
        alert(`Successfully extracted ${volunteering.length} volunteer entries!\n\nCopied to clipboard.`);
    });
})();
```

The user copies the output from parkrun, pastes it into the dashboard, and the entire analytical model renders in milliseconds.

No servers, no data leakage, no security risks, and almost zero operational load on parkrun's infrastructure.

---

## Data Cleansing, Reconciliation & Schema Design

Once the raw data lands in the browser, the real data engineering work begins.

In enterprise data systems, raw data is rarely analysis-ready. This project was a classic reminder that even simple domain datasets contain complex edge cases.

![Demo of dasboard](/Blog/static/images/parkrunData.png)


### 1. The Multi-Role Aggregation Trap

One of the most interesting data modelling challenges lay in volunteering data.

When I extracted the volunteer summary table, I encountered an apparent mathematical contradiction:

```json
[
    { "role": "Run Director", "count": "129" },
    { "role": "Timekeeper", "count": "28" },
    { "role": "Results Processor", "count": "143" },
    { "role": "Pre-event Setup", "count": "99" },
    { "role": "Total Credits", "count": "364" }
]
```

If you sum the individual role counts across duties like Run Director, Results Processor, and Pre-event Setup, the total exceeds 800 occasions.

Yet the official Total Credits was exactly 364. Typical for an RD...

To someone unfamiliar with the operational reality, this looks like bad data.

In reality, it reflects an important real-world business rule: a participant can perform multiple volunteer roles on a single event day, but receives only one official volunteer credit towards their milestone clubs.

For example, an individual might arrive at 8:00 AM for Pre-event Setup, oversee the event at 9:00 AM as Run Director, and sit down at 10:30 AM to process results.

That represents three distinct role duties fulfilled, but only a single credit day.

If the analytical model had simply summed the role counts to derive milestone progress — for example V25, V50, V100, V250 — or calculate the Volunteer-to-Run (V:R) ratio, the metrics would have been completely corrupted.

I had to decouple the data model into two separate entities:

- **Role Duties (Occasions):** The discrete count of volunteer tasks performed across official duties.
- **Volunteer Credit Days:** The official single-credit days derived from the explicit Total Credits metric and mapped against historical calendar years.

This is a deceptively simple example of why understanding the business process behind a metric is often more important than the calculation itself. Something we come across daily at my work with part of the NHS. 

---

### 2. Schema Normalisation & Taxonomy Mapping

Raw role strings extracted from web tables suffer from label drift.

Depending on how parkrun's legacy systems render specific roles, labels do not always match the official roles recognised today.

Examples included:

- `"Barcode Scanning"` needed mapping to the official title `"Barcode Scanner"`
- `"Finish Token Support"` mapped to `"Finish Tokens"`
- `"Event Day Course Check"` mapped to `"Course Check"`
- `"Pacer (5k only)"` mapped to `"Pacer"`
- `"Backup Timer"` mapped to `"Timekeeper"`

I implemented a dictionary mapper that reconciles incoming messy strings into a clean, canonical A–Z taxonomy.

This helps ensure everything is configured correctly and allows for some basic data lineage without manually trawling through code, as we all know how much fun that can be!

```javascript
const ROLE_NAME_MAP = {
    'barcode scanning': 'Barcode Scanner',
    'finish token support': 'Finish Tokens',
    'event day course check': 'Course Check',
    'pacer (5k only)': 'Pacer',
    'backup timer': 'Timekeeper',
    'volunteer coordinator': 'Volunteer Co-ordinator',
    'volunteer co-ordinator': 'Volunteer Co-ordinator'
};
```

---

## Engineering the Metric: The Course Difficulty Handicap

In business intelligence, one of the most dangerous things an analyst can do is present an unadjusted metric that implies comparability where none exists.

Comparing branch revenues without adjusting for local population size, or comparing sales velocity without adjusting for seasonality, produces flawed insights.

In running analytics, finish time is subject to the exact same trap.

Running 20:00 at a flat seaside promenade is not the same physical accomplishment as running 20:00 through ankle-deep winter mud on an undulating cross-country trail.

To solve this, I designed a **Course Difficulty & Handicap Engine**.

### The Multiplier vs Seconds Debate

My initial architectural instinct was to apply a percentage multiplier:

```text
Normalised Seconds = Raw Seconds / Multiplier
```

For example, treating a pancake-flat course as 1.00x, an undulating park path as 1.04x, and a hilly cross-country trail as 1.08x.

While mathematically elegant, user feedback and practical testing revealed a significant flaw: **mental model friction**.

Runners do not think in percentage multipliers.

They do not say:

> "This course felt about 4.2% slower today."

They say:

> "This course is worth about 30 seconds compared to a flat track."

I scrapped the percentage multiplier and refactored the engine to use an explicit user-defined handicap in seconds:

```text
Normalised Seconds = max(1, Raw Seconds - Handicap Seconds)
```

The implementation became:

```javascript
const handicapSecs = parseInt(
    courseHandicaps[latestRun.venue],
    10
) || 0;

const normalizedSeconds = Math.max(
    1,
    latestRun.timeSeconds - handicapSecs
);

const normalizedTimeStr =
    formatSecondsToTime(normalizedSeconds);
```

By allowing the runner to assign a specific handicap in seconds to each venue — for example +0s for a flat promenade, +20s for gentle undulations, +45s for a hilly trail — the dashboard recalculates a Normalised Career Rank alongside their Raw Speed Rank.

Suddenly, an athlete's 34th fastest raw performance of all time reveals itself as their 2nd best physiological effort when the severe terrain handicap is factored in.

That is the difference between raw reporting and contextual business intelligence.

---

## Inclusivity in Metric Design: De-Biasing the Dashboard

Data visualisations carry subtle, often subconscious biases introduced by the people who design them.

This project offered a textbook case of how easily an analyst's personal perspective can inadvertently alienate end users.

### The Elite Bias Trap

When I initially designed the Finish Position Analysis tab, I structured the headline target milestone cards around podium finishes:

- Stretch Target: P1 Finishes (#1)
- Secondary Target: Top 3 Finishes
- Base Target: Top 10 Finishes

For a runner regularly competing at the front of a field, this feels natural.

But parkrun is explicitly not a race.

Millions of parkrunners take part every week who have no aspiration — and no physiological possibility — of ever finishing in the Top 10.

For a participant finishing 250th in a field of 500, a dashboard tracking "Podiums" is uninspiring and irrelevant.

### The Refactoring to Inclusivity

I made two structural changes to democratise the metric layer.

#### 1. User-Configurable Rank Targets

Rather than hardcoding 1, 3, and 10, the configuration panel allows users to specify any arbitrary thresholds, such as:

- Top 50
- Top 100
- Top 250

#### 2. The Age Grade (%) Mode Switch

Position is heavily dependent on who else happens to turn up on a given morning.

Age grading, which measures your speed as a percentage against the world-record pace for your gender and age, is the great leveller.

I added a global toggle allowing users to switch the entire performance engine from Position tracking to Age Grade tracking:

```javascript
if (targetMode === 'ageGrade') {
    document.getElementById('posLabelStretch').innerText =
        `Stretch Target (≥ ${tGradePrimary.toFixed(1)}%)`;

    document.getElementById('posLabelSecondary').innerText =
        `Secondary Target (≥ ${tGradeSecondary.toFixed(1)}%)`;

    document.getElementById('posLabelBase').innerText =
        `Base Target (≥ ${tGradeBase.toFixed(1)}%)`;
} else {
    document.getElementById('posLabelStretch').innerText =
        tPrimary === 1
            ? 'Stretch Target (P1 Finishes)'
            : `Stretch Target (Top ${tPrimary})`;

    document.getElementById('posLabelSecondary').innerText =
        `Secondary Target (Top ${tSecondary})`;

    document.getElementById('posLabelBase').innerText =
        `Base Target (Top ${tBase})`;
}
```

### Removing Patronising Classifications

When implementing the age grade breakdown, I initially considered adopting the traditional World Masters Athletics taxonomy:

- ≥ 80% — National Class
- 70–79% — Regional Class
- 60–69% — Club Standard

I quickly discarded this.

Categorising someone with an age grade of 42% as "Recreational" or "Beginner" introduces unnecessary, patronising labels.

The entire point of self-service data is **empowerment, not gatekeeping**.

I restructured the breakdown into completely neutral 5% buckets:

- ≥ 90%
- 85–89.9%
- 80–84.9%
- Continuing down to < 30%

Only the non-zero buckets relevant to that individual are rendered.

Whether someone's personal target is achieving 45% or 85%, the dashboard celebrates their progression with equal statistical dignity.

---

## What Broke: Three Real-World Bugs and What They Taught Me

Nobody builds software or data pipelines without hitting bugs.

Three specific issues occurred during this build that mirror classic enterprise data delivery challenges.

### 1. The Double-Download Event Listener Leak

When implementing the JSON backup export feature for volunteer data, users reported that clicking the download button caused the browser to trigger two identical file downloads every time.

**The root cause:** In an early iteration, the event listener for the export button was placed inside the `renderVolunteerInputs()` function.

Every time a user changed a volunteer role counter or reloaded data, the function re-rendered the UI and attached a new click listener to the existing DOM button.

After two renders, there were two listeners stacked on the same element. Clicking it fired the export logic twice.

**The fix:** I decoupled one-time application initialisation handlers (`initVolunteerBackupHandlers()`) from state-driven UI re-rendering functions.

In enterprise BI, this is the equivalent of inadvertently spawning duplicate DAG tasks or orchestrating parallel pipelines because a trigger was defined inside a dynamic query loop.

---

### 2. The Hardcoded Presentation Header

When I refactored the dashboard to allow user-defined position targets, the headline tiles and the charts updated immediately.

However, looking at the Annual Competitive Progression matrix, the column headers remained stubbornly frozen on:

- P1 FINISHES (#1)
- TOP 3
- TOP 10

The underlying data calculation had correctly updated to evaluate the user's custom numbers, but the presentation layer had been hardcoded in static HTML.

This is a classic reporting pitfall: **decoupling metadata from presentation**.

If your presentation layer does not dynamically consume the underlying metric definition parameters, you present correct calculations under false labels — which is worse than presenting an outright error because it creates silent misinformation.

Adding dynamic DOM ID hooks (`posAnnThPrimary`, `posAnnThSecondary`, `posAnnThBase`) resolved the issue.

---

### 3. The Scope Failure Crash

During a rapid code iteration, an accidental dangling line outside of a function definition broke the JavaScript lexical scope during page compilation.

The entire script failed to parse, causing a complete freeze on page load:

- No tabs responded
- Inputs were dead
- No charts rendered

In a single-file application, there is no microservice isolation.

If your entry-point script fails, the entire application dies.

It was a sharp reminder of the necessity of rigorous syntax validation, linting, and boundary isolation before shipping changes into production.

---

## The Saturday Consistency Heatmap & PB Longevity

With the foundation stable, I implemented two features that provide genuine analytical depth.

### 1. The 52-Week Saturday Attendance Heatmap

Modelled after GitHub's iconic contribution matrix, this renders all 52 Saturdays of any selected calendar year.

Each tile represents a weekend.

The visualisation distinguishes between:

- Missed weekends
- Attendance credits
- Events where the runner achieved a personal best

It computes:

- Annual attendance rates
- Annual distance
- Longest weekly streaks

within that calendar year.

This transforms an abstract list of dates into an intuitive visual story of winter resilience and summertime consistency.

### 2. The PB Longevity Timeline

A traditional PB board only shows your fastest time today.

The PB Longevity Engine models the historical journey.

It:

- Tracks every record you have ever held chronologically from your debut.
- Calculates **Reign in Days** — how many days elapsed before that record fell.
- Calculates **Reign in parkruns** — how many events you ran before you were able to beat that mark.
- Identifies **Barrier Breakthroughs** — the exact date and venue where you first broke sub-30, sub-25, sub-20, or surpassed 60%, 70%, or 75% age grading.

Seeing that a personal best you set in 2018 stood for 1,420 days and 68 parkruns before finally falling provides a profound sense of achievement that a single static time on a profile page can never convey.

---

## The Bigger Data Leadership Lessons

Building a fun browser project on a Saturday afternoon might seem worlds away from managing multi-million-pound data platforms, designing corporate governance frameworks, or leading data teams.

But the underlying principles of good data stewardship are universal.


## Practical Takeaways for Data Professionals


### Audit Your Dashboards for Privilege and Bias

You know what, I could have put different things here but for the leader this one stands out. Look at the visual hierarchy of your reporting.

Does it only celebrate the top 5% of performers? Are you catering to everyone without disrupting the dashboard?

Designing inclusive tiers and neutral categorical buckets drives higher engagement and better cultural outcomes.

---

## Conclusion

Data is at its best when it connects people to their own journeys.

By taking raw parkrun results and subjecting them to sound data modelling, handicap normalisation, and inclusive metric design, a simple list of finishing times transforms into a rich personal biography.

Whether you are modelling enterprise customer journeys in Microsoft Fabric or visualising weekend running milestones in a browser, the fundamentals never change:

**Respect your source data, question your metric assumptions, design for your entire user base, and always test your boundary conditions.**

---