---
title: "Deep Dive - Star Schema (Facts and Dimensions)"
description: "Why a star schema looks the way it does, using the Citi Bike Gold tables as the running example."
sidebar:
  order: 211
---

Built from Training 21 (Oct 9), where Evan built `gold.fact_station_snapshot`, `gold.dim_station` and `gold.dim_date` in Redshift Serverless. Theory first covered in [Training 5 notes](/training-notes-site/notes/training-5/) (dimensional modeling, normalization, surrogate keys, SCD). This file goes deep on **why** the design looks the way it does, using the Citi Bike tables as the running example.

**How to use this:** sections 1–4 are the core reasoning. Read them carefully. Sections 5–9 are the details interviewers probe. Section 10 applies everything to our Citi Bike model, including what Evan simplified. Section 12 is a self-check.

---

## 1. The problem a star schema solves

Every analytical question has the same anatomy:

> "What was the **average bikes available** (*measure*) **per station** (*dimension*) **on weekday mornings** (*dimension*) **last month** (*dimension*)?"

- **Measures** are numbers produced by a business event or observation. You aggregate them (sum, average, count, min, max).
- **Context** is everything you slice, filter and group *by*: who, what, where, when, how.

Source systems (apps, APIs, OLTP databases) aren't organized this way. They're organized to **record events quickly and correctly**: many small tables, no repeated data, optimized for inserting one order or updating one customer. That's the right design for an app and the wrong one for analysis:

| What analysts need | What an OLTP schema gives them |
|---|---|
| Scan millions of rows and aggregate | Optimized for touching one row at a time |
| Simple queries a BI tool can generate | 8–15 table joins to answer one question |
| Consistent definitions ("what's a weekend?", "what's an active station?") | Each analyst re-derives them, and gets different answers |
| History ("what was the capacity *then*?") | Usually only the current value, overwritten in place |

**Dimensional modeling** (Ralph Kimball, *The Data Warehouse Toolkit*, 1996) redesigns the data around the questions instead of the transactions. The **star schema** is its physical shape.

---

## 2. The two kinds of tables

### Fact tables: "what happened / what was measured"

- One row per **event or measurement** at a declared **grain**.
- Columns are **foreign keys** to dimensions + **numeric measures** (+ maybe a few degenerate dimensions, see §8).
- **Narrow and very long:** few columns, millions to billions of rows. It's the table that grows.
- Example: `fact_station_snapshot`: one row per station per 5-minute snapshot. `bikes_available`, `docks_available`, `utilization_pct`...

### Dimension tables: "the context"

- One row per **thing being described** (a station, a date, a customer, a product).
- Columns are **descriptive attributes**, mostly text, used in `WHERE`, `GROUP BY` and chart labels.
- **Wide and short:** many columns, relatively few rows (hundreds to millions).
- Example: `dim_station`: one row per station. `station_name`, `capacity` (and ideally lat/lon, borough, neighborhood...).

| | Fact | Dimension |
|---|---|---|
| Answers | How much / how many | Who / what / where / when / how |
| Typical columns | Keys + numbers | Text attributes + a key |
| Shape | Narrow, very long | Wide, short |
| Changes | Constantly **appended** | Occasionally **updated** |
| Used in a query as | `SUM()`, `AVG()`, `COUNT()` | `WHERE`, `GROUP BY`, labels |
| Citi Bike | `fact_station_snapshot` | `dim_station`, `dim_date` |

The name comes from the diagram: the fact table in the center, each dimension joined directly to it like the points of a star.

```
                 dim_station
                      │
   dim_time ──── fact_station_snapshot ──── dim_date
                      │
                 dim_weather (future)
```

---

## 3. Why separate them? The seven concrete benefits

### 3.1 No repeated descriptions (storage + correctness)

Without dimensions, every 5-minute row repeats "W 180 St & Fort Washington Ave, capacity 24". At full scale: 2,500 stations × 288 snapshots/day = **720,000 rows/day**, each repeating ~60 bytes of text = ~43 MB/day of pure repetition, ~16 GB/year. With a dimension, the fact row carries a key of a few bytes and the name is stored **once**.

More importantly: **if the name is stored once, it can only be wrong in one place.**

### 3.2 Changes happen in one row

Citi Bike renames a station or adds 6 docks. One-big-table: update every historical row (millions), or the names disagree between old and new rows. Star: update **one** row in `dim_station` (or add a new version: see SCD in §6).

### 3.3 Business logic is computed once, reused everywhere

"Is it a weekend?", "Is it rush hour?", "Which borough is this station in?", "Is it a holiday?" With a star, these are **columns** in a dimension, computed once at load time. Every analyst, dashboard and ML feature uses the same definition. Without one, each query re-implements `EXTRACT(DOW ...) IN (0, 6)`, and sooner or later someone gets it wrong (Sunday is 0 in Redshift, 7 in ISO).

### 3.4 Simple, predictable queries

Every question has the same shape: **start at the fact, join the dimensions you need, group by their attributes, aggregate the measures.**

```sql
SELECT d.day_name, s.station_name, AVG(f.bikes_available) AS avg_bikes
FROM fact_station_snapshot f
JOIN dim_date    d ON f.date_key    = d.date_key
JOIN dim_station s ON f.station_key = s.station_key
WHERE d.is_weekend = FALSE
GROUP BY d.day_name, s.station_name;
```

An analyst learns the pattern once. A **BI tool** (QuickSight, Tableau, Power BI) can generate it automatically: drag a measure onto the chart and dimension attributes onto the axes and filters. These tools are literally designed around stars.

### 3.5 Fast on columnar MPP warehouses

- The fact is **narrow**: a query reads only the few columns it needs (columnar storage), and they compress extremely well (repeated small integers).
- Dimensions are **small**: Redshift can copy each one to every node (`DISTSTYLE ALL`), so joins never move data across the network.
- Predictable joins (fact → dimension on one key) are what query optimizers handle best ("star join" optimization).

### 3.6 Consistent answers across the company ("one version of the truth")

When `dim_station` is the single place a station is defined, the operations dashboard, the finance report and the data science model all count the same stations the same way. The **conformed dimension** idea (§7) extends this across many fact tables.

### 3.7 History handled deliberately

A fact row records *what happened at that time*. Dimensions can keep **versions** (SCD Type 2) so you can ask "how full was this station *when it had 24 docks* vs *after it was expanded to 30*?" A one-big-table design usually only has the current value.

---

## 4. Grain: the single most important decision

**Grain = what exactly one row of the fact table represents.** Declare it in one sentence *before* choosing any columns.

| Fact table | Grain |
|---|---|
| `fact_station_snapshot` | One row per **station** per **snapshot time** (every 5 minutes) |
| A sales fact | One row per **line item** on a receipt |
| A trips fact (future Citi Bike) | One row per **bike trip** |

Why it matters:

- **It determines the dedup key.** Evan's fact load deduplicated on `(station_id, snapshot_ts)` → 100 rows; `dim_station` deduplicated on `station_id` → 97 rows. Same source, different grains, different counts. That's correct.
- **Every measure must be true at that grain.** `bikes_available` is a fact about one station at one moment, so it belongs. `capacity` is a fact about the station, not the moment, so it belongs in `dim_station` (which is exactly why Evan moved it out).
- **Mixed grains cause double counting.** If some rows were per-snapshot and others daily summaries, any `SUM` would be meaningless.
- **Choose the finest (atomic) grain you can.** You can always roll 5-minute data up to hourly or daily; you can never break a daily summary back down into 5-minute data.

**Kimball's 4-step design process:**

1. **Pick the business process** (station availability monitoring).
2. **Declare the grain** (station × 5-minute snapshot).
3. **Identify the dimensions** (station, date, time of day; later weather, holiday).
4. **Identify the facts/measures** (bikes, e-bikes, docks available; utilization; flags).

---

## 5. Types of fact tables, and which one Citi Bike is

| Type | One row per | Measures are | Example |
|---|---|---|---|
| **Transaction** | Event (happens once) | Usually fully additive | A bike trip, a sale, a click |
| **Periodic snapshot** | Entity per regular time period | Often **semi-additive** | **Station status every 5 min** ← ours; daily bank balance; nightly inventory |
| **Accumulating snapshot** | Process instance, updated as it moves through milestones | Durations, milestone dates | An order: placed → shipped → delivered |
| **Factless** | Event or coverage with no numeric measure | Just `COUNT(*)` | Student attended class; station was *scheduled* for maintenance |

`fact_station_snapshot` is a **periodic snapshot fact**: it records the *state* of every station at regular intervals. That has a big consequence for how you aggregate it:

### Additivity: the trap in our data

| Kind | Can you SUM it across... | Example |
|---|---|---|
| **Additive** | Every dimension | Trip count, revenue, minutes ridden |
| **Semi-additive** | Some dimensions, **not time** | **`bikes_available`**, account balance, inventory level |
| **Non-additive** | Nothing; recompute from parts | **`utilization_pct`**, ratios, averages, unit price |

- `SUM(bikes_available)` across **stations** at one snapshot = total bikes docked citywide at that moment. ✅ Meaningful.
- `SUM(bikes_available)` across **time** for one station = adding 9:00 + 9:05 + 9:10... ❌ Meaningless (the same bikes counted again and again). Use `AVG`, `MIN`, `MAX`, or the last value of the period.
- `AVG(utilization_pct)` across stations gives every station equal weight, so a 5-dock station counts as much as a 60-dock one. The correct citywide utilization is `SUM(bikes_in_use) / SUM(capacity)`, recomputed from additive parts. For that reason, warehouses often store the **components** (bikes, docks, capacity) and compute ratios at query time.

This is one of the most common real-world modeling bugs, and a great interview point.

---

## 6. Dimension design in depth

### 6.1 Natural keys vs surrogate keys

| | Natural (business) key | Surrogate key |
|---|---|---|
| What | The ID from the source (`station_id = "66db237e-0aca..."`) | A warehouse-generated integer (1, 2, 3...) |
| Evan's model | ✅ Used today, "deliberately simple" | Not yet |
| Pros | No lookup needed when loading facts | Small, fast joins; independent of the source; **required for SCD Type 2** (one station can have several versions) |
| Cons | Can be long strings (slower joins); the source might reuse or change IDs; can't hold history versions | Loading facts needs a lookup (natural key → current surrogate key) |

In Redshift: `station_key BIGINT IDENTITY(1,1)` generates surrogate keys automatically.

### 6.2 Slowly Changing Dimensions (SCD): what happens when a description changes

Station 123 is expanded from 24 to 30 docks on Nov 1.

| Type | What you do | Result | Use when |
|---|---|---|---|
| **Type 0** | Never change it | Capacity stays 24 forever | Attributes that must never change (original install date) |
| **Type 1** | Overwrite | Capacity = 30, history lost; October's utilization now computed against 30 (wrong) | Corrections (fixing a typo), or history doesn't matter |
| **Type 2** | Add a new row (new surrogate key) with `valid_from`, `valid_to`, `is_current` | Two rows: 24 (until Oct 31) and 30 (from Nov 1). Old facts point to the old version | You need history to stay accurate ← **the default for analytics** |
| **Type 3** | Add a "previous value" column | `capacity = 30, previous_capacity = 24` | Only one prior value matters |

Type 2 dimension example:

| station_key | station_id | station_name | capacity | valid_from | valid_to | is_current |
|---|---|---|---|---|---|---|
| 17 | 66db... | W 180 St & Fort Washington Ave | 24 | 2024-03-01 | 2026-10-31 | false |
| 912 | 66db... | W 180 St & Fort Washington Ave | 30 | 2026-11-01 | 9999-12-31 | true |

Facts loaded in October carry `station_key = 17`; facts from November carry `912`. Every report is automatically correct for its period. dbt implements this with **snapshots** (Training 17).

### 6.3 The date dimension (and why it's pre-filled)

`dim_date` is the most reused dimension in any warehouse. A full one has one row per calendar day for many years (10 years ≈ 3,650 rows, which is tiny) and lots of ready-made attributes:

| Column | Example | Why |
|---|---|---|
| `date_key` | 20261008 | Smart integer key: readable, sortable, fast |
| `full_date` | 2026-10-08 | Real DATE type |
| `day_of_week` / `day_name` | 4 / Thursday | Weekday patterns |
| `is_weekend` | false | Commuter vs leisure usage |
| `is_holiday` / `holiday_name` | false | Holidays behave like weekends |
| `week_of_year`, `month_name`, `quarter`, `year` | 41, October, Q4, 2026 | Roll-ups |
| `fiscal_period` | FY27-P01 | Business calendars differ from the calendar year |

**Pre-filling it** (rather than `SELECT DISTINCT` from the data, as we did today) matters because:
- Days with **no data** still appear in reports (a gap shows as zero, not a missing bar).
- Holiday/fiscal attributes can't be derived from timestamps; they're business reference data.

Evan's version only had 2 rows because the data only covers Oct 7–8. Fine for a demo; production would generate the full calendar once.

### 6.4 Separate date and time-of-day dimensions

Bike availability is driven by **time of day** (rush hours). Rather than one huge date-time dimension (365 × 288 = 105,120 rows/year), warehouses use:

- `dim_date` (one row per day), and
- `dim_time` (one row per minute or 5-minute slot of a day: 288 rows with `hour`, `is_rush_hour`, `day_part = 'Morning'`).

Then "weekday morning rush hour" is a simple filter on two small dimensions.

---

## 7. Conformed dimensions and the bus matrix

Imagine Citi Bike later adds a **trips** fact (one row per ride) next to our **station snapshot** fact. If both use the **same** `dim_station` and `dim_date`, they're **conformed dimensions**, and you can compare across business processes ("drill across"):

> "At stations that ran empty most often, how many trips started there?"

| Business process → / Dimension ↓ | Station snapshots | Trips | Maintenance |
|---|---|---|---|
| dim_date | ✅ | ✅ | ✅ |
| dim_time | ✅ | ✅ | |
| dim_station | ✅ | ✅ (start + end, see role-playing) | ✅ |
| dim_bike | | ✅ | ✅ |
| dim_rider_type | | ✅ | |

That grid is Kimball's **bus matrix**, the plan for an enterprise warehouse built one star at a time that all fit together.

---

## 8. Special dimension patterns (interview vocabulary)

| Pattern | What it is | Citi Bike example |
|---|---|---|
| **Role-playing dimension** | One dimension joined several times in different roles | A trip has a **start station** and an **end station**: both join `dim_station` (as `start_station_key`, `end_station_key`) |
| **Degenerate dimension** | A dimension key with no dimension table, kept on the fact | A `trip_id` or receipt number stored on the fact row |
| **Junk dimension** | Several low-cardinality flags combined into one small dimension | `is_empty`, `is_full`, `is_operational` combinations (8 rows) instead of 3 flag columns on billions of rows |
| **Mini-dimension** | Fast-changing attributes split out of a big dimension | Station status categories that change daily |
| **Outrigger** | A dimension that references another dimension | `dim_station → dim_neighborhood` (a small step toward snowflaking) |
| **Bridge table** | Handles many-to-many | A station belonging to several service zones |

---

## 9. Star vs the alternatives

### 9.1 Star vs snowflake

A **snowflake** normalizes the dimensions themselves: `dim_station → dim_neighborhood → dim_borough`.

| | Star | Snowflake |
|---|---|---|
| Dimension structure | Flat (borough is a column on `dim_station`) | Split into sub-tables |
| Joins per query | Fewer | More |
| Storage | Slightly more (borough name repeated per station) | Slightly less |
| Query simplicity / BI friendliness | Better | Worse |
| When to choose | **Default** | Very large dimensions with deep hierarchies, or when sub-dimensions are shared and maintained separately |

Dimensions are small, so the storage saved by snowflaking is usually trivial, while the extra joins cost every query. That's why the star is the default.

### 9.2 Star vs normalized 3NF (Inmon)

| | 3NF (OLTP / Inmon EDW) | Star (Kimball) |
|---|---|---|
| Goal | No redundancy; fast, safe writes | Fast, simple reads |
| Joins | Many | Few |
| Users | Applications, integration layer | Analysts, BI tools |

**Inmon** builds a normalized enterprise warehouse first and derives stars ("data marts") from it. **Kimball** builds conformed stars directly. Many companies do a mix: normalized or raw layers underneath (Bronze/Silver), stars on top (Gold).

### 9.3 Star vs One Big Table (OBT / wide denormalized table)

Modern columnar warehouses (Redshift, Snowflake, BigQuery) are so good at scanning wide tables that some teams pre-join everything into one wide table per use case:

| | Star | One Big Table |
|---|---|---|
| Query | Needs joins | No joins; easiest for analysts |
| Changes to descriptions | One row | Rebuild/update the whole table |
| History (SCD) | Natural | Hard |
| Reuse across use cases | High (conformed dims) | Low (one table per use case) |
| Common pattern | Star as the **source of truth** | OBTs **built from** the star for specific dashboards |

### 9.4 Data Vault (for completeness)

Hubs (business keys), links (relationships) and satellites (descriptive history). Very flexible for integrating many changing sources and auditing, but not query-friendly, so stars are usually built **on top** of it for reporting.

---

## 10. Our Citi Bike model: what Evan built, and how a production version would look

### 10.1 What exists now (Training 21)

```
                       dim_station (97 rows)
                 station_id PK (natural key)
                 station_name, capacity
                              │
                              │ station_id
                              ▼
                 fact_station_snapshot (100 rows)
   station_id, date_key, snapshot_ts,
   bikes_available, ebikes_available, docks_available,
   utilization_pct, is_empty, is_full, is_operational
                 DISTKEY + SORTKEY
                              ▲
                              │ date_key (20261008)
                              │
                       dim_date (2 rows)
   date_key, calendar_date, year/month/day number, day_of_week
```

Grain: station × snapshot. Loaded with ELT SQL (`TRUNCATE` + `INSERT ... SELECT`, `QUALIFY ROW_NUMBER() = 1`, `SELECT DISTINCT`). Validated with counts, orphan check and duplicate check.

### 10.2 What was simplified, and the production version

| Today (deliberately simple) | Production | Why |
|---|---|---|
| Natural key `station_id` | Surrogate `station_key` + `station_id` kept as an attribute | Enables SCD2; smaller join key |
| `dim_station` overwritten each load (Type 1) | SCD Type 2 with `valid_from` / `valid_to` / `is_current` | Capacity changes shouldn't rewrite history |
| `dim_station`: name + capacity | + lat, lon, borough, neighborhood, region, station type, has_kiosk | More ways to slice ("which borough runs empty?") |
| `dim_date` from `SELECT DISTINCT` (2 rows) | Pre-generated calendar, 10+ years, with holidays and weekend flags | Gaps show as zero; holiday analysis |
| No time-of-day dimension | `dim_time` (288 five-minute slots, `is_rush_hour`, `day_part`) | Rush-hour analysis is the core question |
| `TRUNCATE` + full reload | **Incremental** load of new snapshots only (MERGE / append + dedup), driven by the 5-minute schedule | Full reloads don't scale to billions of rows |
| `utilization_pct` stored | Store capacity-related parts; compute ratios at query time (or store both, but aggregate correctly) | Non-additive measure trap |
| Validation by hand | dbt tests / Glue Data Quality that fail the pipeline | Catch bad loads automatically |
| (Not yet) | `fact_trip` sharing `dim_station` (role-playing start/end) + `dim_date` | Drill across processes |

### 10.3 Redshift physical design for this star

| Table | Distribution | Sort key | Why |
|---|---|---|---|
| `fact_station_snapshot` | `DISTKEY(station_id)` (or `station_key`) | `SORTKEY(snapshot_ts)` or `(date_key, station_id)` | Joins to `dim_station` stay on one node; time-range filters skip blocks |
| `dim_station` | `DISTSTYLE ALL` | `station_id` | Small → a full copy on every node, so joins never move data |
| `dim_date` | `DISTSTYLE ALL` | `date_key` | Tiny, joined by every query |

Remember: PK/FK constraints in Redshift are **not enforced** (they're optimizer hints), which is why validation queries are part of the load.

---

## 11. Analytical queries this model answers ("queries that tell a story")

```sql
-- 1. Which stations are empty most often?
SELECT s.station_name,
       AVG(CASE WHEN f.is_empty THEN 1.0 ELSE 0 END) AS pct_time_empty
FROM gold.fact_station_snapshot f
JOIN gold.dim_station s ON f.station_id = s.station_id
GROUP BY s.station_name
ORDER BY pct_time_empty DESC
LIMIT 10;

-- 2. Weekday vs weekend availability (semi-additive measure → AVG, not SUM)
SELECT CASE WHEN d.day_of_week IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
       AVG(f.bikes_available) AS avg_bikes_available
FROM gold.fact_station_snapshot f
JOIN gold.dim_date d ON f.date_key = d.date_key
GROUP BY 1;

-- 3. Citywide bikes docked at each snapshot (SUM across stations is valid)
SELECT f.snapshot_ts, SUM(f.bikes_available) AS bikes_docked_citywide
FROM gold.fact_station_snapshot f
GROUP BY f.snapshot_ts
ORDER BY f.snapshot_ts;

-- 4. Correct citywide utilization (recompute the ratio from additive parts)
SELECT f.snapshot_ts,
       1 - SUM(f.bikes_available)::FLOAT / NULLIF(SUM(s.capacity), 0) AS citywide_utilization
FROM gold.fact_station_snapshot f
JOIN gold.dim_station s ON f.station_id = s.station_id
GROUP BY f.snapshot_ts;

-- 5. Big stations that still run empty (dimension attribute as a filter)
SELECT s.station_name, s.capacity, SUM(CASE WHEN f.is_empty THEN 1 ELSE 0 END) AS empty_snapshots
FROM gold.fact_station_snapshot f
JOIN gold.dim_station s ON f.station_id = s.station_id
WHERE s.capacity >= 40
GROUP BY s.station_name, s.capacity
HAVING SUM(CASE WHEN f.is_empty THEN 1 ELSE 0 END) > 0;
```

(Column names follow today's model; check the exact names in the query editor's sidebar. With only 100 rows the results are illustrative, not meaningful. That's why Evan wants more data loaded next week.)

---

## 12. Common mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Grain not declared / mixed grains | Double-counted totals | Write the grain sentence first; one grain per fact |
| Summing a semi-additive measure over time | Absurd totals (millions of "bikes") | `AVG`/`MIN`/`MAX`/last value over time |
| Averaging ratios | Small stations distort citywide numbers | Store additive parts, recompute ratios |
| Descriptions on the fact table | Huge fact, inconsistent names | Move them to a dimension (Evan moved `capacity`) |
| Fact loaded before its dimension | Orphaned facts silently dropped by inner joins | Load dims first; run the orphan check; use an "Unknown" member row (key -1) for late-arriving dimensions |
| Overwriting dimension history (Type 1) when history matters | Past reports change after an update | SCD Type 2 |
| Date dimension built only from data | Gaps disappear from charts | Pre-generate the calendar |
| Joining fact to fact directly | Fan-out (row multiplication) | Aggregate each fact to a common grain first, then join on conformed dimensions |

---

## 13. Interview answers

**"Why use a star schema?"**
"It separates measurable events into a narrow fact table at a declared grain, and descriptive context into dimension tables. That removes repetition, puts business definitions in one place, keeps history manageable through slowly changing dimensions, and gives every analytical query the same simple shape: one fact, a few joins, group by dimension attributes. It's also what columnar MPP warehouses and BI tools are optimized for."

**"What's the grain of your fact table and why does it matter?"**
"In my Citi Bike project, one row per station per five-minute snapshot: a periodic snapshot fact. The grain decides the dedup key, which measures are valid, and prevents double counting. I chose the atomic grain so it can roll up to hourly or daily."

**"What's a semi-additive measure?"**
"A measure you can sum across some dimensions but not time, like bikes available or an account balance. Summing stations at one moment is fine; summing the same station over time isn't, so you average or take the period-end value."

**"Star vs snowflake?"**
"Snowflake normalizes dimensions into sub-tables to save a little space but adds joins. Dimensions are small, so the star is usually the better trade: simpler and faster queries."

**"How do you handle a station's capacity changing?"**
"SCD Type 2: a new dimension row with a new surrogate key and effective dates, so older facts still point at the old capacity and historical utilization stays correct."

---

## 14. Self-check

<details><summary>1. In one sentence, what's the grain of fact_station_snapshot?</summary>

One row per station per five-minute snapshot time.
</details>

<details><summary>2. Why did capacity move from the fact table to dim_station?</summary>

It describes the station, not the moment. It doesn't change every snapshot, so storing it on each fact row repeats it and makes changes painful.
</details>

<details><summary>3. Why does dim_station have 97 rows but the fact table 100?</summary>

Different grains: one row per station vs one per station per snapshot. Three stations appeared in two snapshots.
</details>

<details><summary>4. Is SUM(bikes_available) for one station across a whole day meaningful? What should you use?</summary>

No. It's semi-additive over time. Use AVG, MIN, MAX or the last value of the day.
</details>

<details><summary>5. What's an orphaned fact and how do you find one?</summary>

A fact row whose dimension key has no matching dimension row. Find it with `LEFT JOIN dim ... WHERE dim.key IS NULL`.
</details>

<details><summary>6. Why doesn't Redshift stop you from inserting an orphan or duplicate?</summary>

Primary and foreign keys in Redshift are informational only, not enforced.
</details>

<details><summary>7. What type of fact table is ours, and what would a trips table be?</summary>

Ours is a periodic snapshot. A trips table is a transaction fact.
</details>

<details><summary>8. Why would you need a surrogate key for dim_station?</summary>

To keep several versions of the same station (SCD Type 2), and for smaller, faster join keys independent of the source system.
</details>

<details><summary>9. What's a role-playing dimension? Give a Citi Bike example.</summary>

One dimension used in several roles: a trip's start station and end station both join dim_station.
</details>

<details><summary>10. Why pre-generate dim_date instead of SELECT DISTINCT from the data?</summary>

So days with no data still appear (gaps show as zero), and holiday/fiscal attributes that can't be derived from timestamps can be included.
</details>
