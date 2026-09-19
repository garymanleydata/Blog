---
title: "Taskmaster"
date: 2026-09-12
category: "Technical"
tags:
  - Data Leadership
  - Data 
  - Technical
  - Personal Development
description: "Review of a fun home project"
featured: false
---

Community-maintained wikis are a goldmine of niche observational data, but they are notoriously hostile to automated data engineering pipelines. Tables that look visually coherent to human readers frequently rely on complex HTML display hacks—such as nested `colspan` groupings, inherited vertical `rowspan` attributes, and irregular sub-task rows—that quickly break standard tabular parsers.

I recently engineered (with the help of AI, of course) an automated pipeline and data workbench for the TV series *Taskmaster*. A show I think is great fun and has some fun data. The goal was straightforward: scrape and validate every individual task attempt, scoring anomaly, disqualification, and bonus point across the twenty+ series, model the dataset into a star schema, and serve an interactive analytical dashboard without managing a paid backend or database server.

Here is an architectural walkthrough of the engineering challenges encountered, the dimensional modeling decisions, and how in-browser SQLite WebAssembly (`sql.js`) can replace traditional server-side reporting stacks for lightweight public datasets. Just for fun, would not work on complex or large datasets but great for this. 

---

## 1. Ingestion

Extracting data from the Fandom MediaWiki Parse API (`api.php`) avoids browser anti-bot mechanisms, but the underlying MediaWiki HTML table structures introduce several failure modes for standard scrapers:

1. **Header Drift and False Columns:**  
   Episode headers and task summaries frequently sit alongside contestant columns. A naive column-index mapping will easily mistake a prize task description or an episode broadcast date for an additional contestant.
2. **Asymmetric Solo Tasks and Negative Points:**  
   Tasks like solo secret objectives or point deductions (such as chocolate-eating penalties yielding `-5` points) break standard regex lookups expecting positive integer scorelines.
3. **The Multi-Part `rowspan` Trap:**  
   Multi-part tasks frequently span several rows. In Series 9, Episode 4 (Ed Gamble’s alphabet task) and Series 19, Episode 9 (Mathew Baynton’s magic moustache secret task), a contestant was awarded a single score that visually spanned two or three table rows via `<td rowspan="2">` or `<td rowspan="3">`. Naive parsers either duplicate the awarded points on every sub-row or overwrite the prior task entirely.

### Building a 2D HTML Coordinate Grid Engine

To handle irregular spans deterministically, the scraper builds an in-memory 2D Cartesian coordinate grid (`expand_table_with_metadata`) before evaluating scoring rules:

```python
def expand_table_with_metadata(v_table) -> list[list[dict]]:
    """Expands an HTML table into a 2D coordinate grid of cell dictionaries.
    Tracks whether a cell was explicitly declared on that row or inherited via rowspan.
    """
    v_grid = []
    v_rowspans = {}  # {col_idx: (remaining_rows, cell_dict)}

    for v_tr in v_table.find_all("tr"):
        v_row = []
        v_col_idx = 0
        v_cells = v_tr.find_all(["td", "th"])
        v_cell_iter = iter(v_cells)

        while True:
            # Handle active vertical rowspans inherited from preceding rows
            if v_col_idx in v_rowspans:
                v_remaining, v_inherited_dict = v_rowspans[v_col_idx]
                v_row.append({
                    "text": v_inherited_dict["text"],
                    "is_inherited_rowspan": True,
                    "raw_cell": v_inherited_dict["raw_cell"],
                })
                if v_remaining > 1:
                    v_rowspans[v_col_idx] = (v_remaining - 1, v_inherited_dict)
                else:
                    del v_rowspans[v_col_idx]
                v_col_idx += 1
                continue

            try:
                v_cell = next(v_cell_iter)
            except StopIteration:
                break

            v_text = clean_text(v_cell.get_text(separator=" ", strip=True))
            v_colspan = int(v_cell.get("colspan", 1))
            v_rowspan = int(v_cell.get("rowspan", 1))

            v_cell_dict = {
                "text": v_text,
                "is_inherited_rowspan": False,
                "raw_cell": v_cell,
            }

            for _ in range(v_colspan):
                v_row.append(v_cell_dict)
                if v_rowspan > 1:
                    v_rowspans[v_col_idx] = (v_rowspan - 1, v_cell_dict)
                v_col_idx += 1

        if v_row:
            v_grid.append(v_row)

    return v_grid

```

By tagging each cell with an `is_inherited_rowspan` flag, the parser can distinguish between:

* **Distinct scorable events:** A row declaring newly entered explicit scores (such as Series 2, Episode 2's bonus pizza task).
* **Display continuations:** A row inheriting a previous cell's value where the score must evaluate to `0` to prevent duplicate point allocation.

---

## 2. Dimensional Modelling, well sort of

A single wide, denormalised extract is inefficient for client-side analytical querying. Storing repeated strings (e.g. 60-word task descriptions) across five contestants per task bloats JSON payload sizes and wastes memory in browser environments.

To optimise data transfer and query performance, the flat scrape is refactored into a dimensional star schema:

```text
                     ┌──────────────────┐
                     │   dim_series     │
                     ├──────────────────┤
                     │ * series_id (PK) │
                     │   episode_count  │
                     └─────────┬────────┘
                               │ 1:N
┌──────────────────┐           │           ┌──────────────────┐
│  dim_contestant  │           │           │     dim_task     │
├──────────────────┤           ▼           ├──────────────────┤
│ * contestant_id  │◄────┐ ┌────────┐ ┌───►│ * task_id (PK)   │
│   contestant_name│     │ │        │ │    │   series_id      │
│   series_id      │     │ │        │ │    │   episode_num    │
└──────────────────┘     │ │        │ │    │   task_num       │
                         │ │        │ │    │   task_description
                         │ │        │ │    │   task_type      │
                         │ │        │ │    │   is_tiebreaker  │
                         │ │        │ │    └──────────────────┘
                         │ │        │ │
                   ┌─────┴─┴────────┴─┴─────┐
                   │    fact_task_scores    │
                   ├────────────────────────┤
                   │ * score_id (PK)        │
                   │   task_id (FK)         │
                   │   contestant_id (FK)   │
                   │   series_id            │
                   │   episode_num          │
                   │   points               │
                   │   is_dq                │
                   │   is_ep_winner         │
                   └────────────────────────┘

```


## 3. Automation: Unattended Ingestion via GitHub Actions

To ensure the data remains evergreen while new series broadcast, the ingestion and transformation scripts run via GitHub Actions on a daily cron schedule (`.github/workflows/workflow.yml`):

1. **Environment Setup:** Spins up a lightweight Ubuntu container with Python 3.11.
2. **Scrape Execution:** Runs `scripts/scrape_taskmaster.py` with polite request throttling (`1.0s` sleep intervals) and 3-stage exponential backoff to handle transient network issues cleanly.
3. **Schema Transformation:** Runs `scripts/build_star_schema.py` to compile `star_schema.json`, `telemetry.csv`, and a validation summary `series_summary.csv`.
4. **Git Automation:** Evaluates `git diff`—if new episode records were parsed, the action commits the updated data payload back to the `main` branch with `[skip ci]`, automatically triggering a zero-downtime deployment on GitHub Pages.

---

## 4. Serving: In-Browser SQLite WebAssembly & Visual Pivots

Traditional web applications rely on server-side databases (such as PostgreSQL or serverless MySQL) paired with an API layer (Node, FastAPI) to power analytical dashboards. For read-heavy datasets under 100,000 records, this adds unnecessary operational overhead, connection limits, and hosting costs.

Instead, the client application runs **SQLite compiled to WebAssembly (`sql.js`)** directly inside the user's browser.

### Loading the Engine Client-Side

When the user visits the page, JavaScript initialises the WASM database instance, creates the relational tables in browser memory, and hydrates them from `star_schema.json`:

```javascript
async function initSQLite() {
    const SQL = await initSqlJs({
        locateFile: file => `[https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/$](https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/$){file}`
    });
    db = new SQL.Database();

    db.run(`
        CREATE TABLE dim_series (series_id INTEGER PRIMARY KEY, episode_count INTEGER);
        CREATE TABLE dim_contestant (contestant_id INTEGER PRIMARY KEY, series_id INTEGER, contestant_name TEXT);
        CREATE TABLE dim_task (task_id INTEGER PRIMARY KEY, series_id INTEGER, episode_num INTEGER, task_num INTEGER, task_description TEXT, task_type TEXT, is_tiebreaker INTEGER);
        CREATE TABLE fact_task_scores (score_id INTEGER PRIMARY KEY, task_id INTEGER, contestant_id INTEGER, series_id INTEGER, episode_num INTEGER, points INTEGER, is_dq INTEGER, is_ep_winner INTEGER);
    `);
}

```

Every user action—filtering a series, switching tabs, or selecting a task category—executes ANSI SQL directly against in-memory SQLite tables, returning query results in sub-millisecond execution times.

```sql
SELECT 
    c.contestant_name,
    SUM(f.points) as total_points,
    ROUND(CAST(SUM(f.points) AS FLOAT) / COUNT(f.score_id), 2) as pts_per_task,
    COUNT(f.score_id) as tasks_attempted,
    COUNT(DISTINCT CASE WHEN f.is_ep_winner = 1 THEN f.episode_num END) as ep_wins,
    SUM(f.is_dq) as dq_count
FROM fact_task_scores f
JOIN dim_contestant c ON f.contestant_id = c.contestant_id
JOIN dim_task t ON f.task_id = t.task_id
WHERE f.series_id = 14
GROUP BY c.contestant_id, c.contestant_name
ORDER BY total_points DESC;

```

---

## 5. Architectural Takeaways

Most of the tech used in this was outside my area of expertise, so I relied heavily on AI and guiding it to the solution I required. As always be careful when using AI and make sure you validate the output you get. Much like this blog post, AI build the basics based on the code and problems we faced and I added some human touches and fixes. AI really does love the word telemetry.

*The complete interactive dashboard, visual pivot studio, and datasets are hosted live at [garymanleydata.github.io/TaskmasterSite](https://garymanleydata.github.io/TaskmasterSite/?utm_source=gemini).*

```

```