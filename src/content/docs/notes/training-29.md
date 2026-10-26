---
title: "Training 29 - Elasticsearch, ELK and Lakeflow"
description: "Elasticsearch and AWS OpenSearch, the ELK stack, working on a data engineering team, profile narratives for interviews, and Databricks Lakeflow declarative pipelines."
sidebar:
  order: 29
---

Teacher: Evan Flint

Syllabus Day 30 (per file numbering; Wed Oct 21). Sources: class notes.

---

# Elasticsearch / AWS OpenSearch

Q. What is Elasticsearch?

A. (Teacher's definition) Elasticsearch is very unique because it is a combination of a search engine and a nosql database. It's based on the Apache Lucene search engine. It accepts JSON data in its NoSQL database, and provides methods for searching through this JSON data in the style of a search engine rather than a SQL query tool. Probably the most famous use case for Elasticsearch is Ebay - it powers their internal search engine.

Expanded: Most databases make you ask exact questions ("give me rows where `city = 'Boston'`"). Elasticsearch is built to answer *fuzzy* questions the way Google does: "find documents about *red running shoes*", ranked by how relevant each one is. It does both jobs at once:

- **NoSQL document store:** you send it JSON documents and it keeps them, grouped into an **index** (roughly a table).
- **Search engine:** when a document comes in, Lucene builds an **inverted index**: a lookup from every word to the documents containing it, the same way a book's index maps words to page numbers. That's why full-text search over millions of documents is fast.

You query it with a JSON-based query language (the Query DSL) over a REST API, not with SQL, and results come back sorted by a **relevance score**.

| | Relational DB (SQL) | Elasticsearch |
|---|---|---|
| Data shape | Rows and columns, fixed schema | JSON documents, flexible schema |
| Grouping | Table | Index |
| Query style | Exact match (`WHERE col = value`) | Full-text, fuzzy, ranked by relevance |
| Query language | SQL | JSON Query DSL over REST |
| Engine underneath | Database engine (B-tree indexes) | Apache Lucene (inverted index) |
| Classic use | Transactions, reporting | Site search (eBay), log search, vector/semantic search |

Q. What is AWS OpenSearch?

A. (From Evan's Amazon project outline) The AWS version of Elasticsearch.

Expanded: In 2021 Elastic changed Elasticsearch's license, so AWS **forked** the last open-source version and named it **OpenSearch**. (In 2024 Elastic added the open-source AGPL license as an option again, but OpenSearch remains a separate project.) **Amazon OpenSearch Service** is the managed version: AWS runs the cluster, and you send it data and queries. It also supports **vector search**, which is why it shows up as the vector database in RAG pipelines (see Training 22): embeddings are stored next to the text, and a question is answered by finding the nearest vectors.

---

# The ELK Stack

Q. What is the ELK stack?

A. (Teacher's definition) Elasticsearch is one part of the ELK stack. The L is for Logstash. The K is for Kibana.

Expanded: ELK is three tools that are almost always used together for **log analytics**: collecting logs from many servers, storing them somewhere searchable, and looking at them on dashboards.

| Letter | Tool | Job in the stack |
|---|---|---|
| **E** | Elasticsearch | Stores and indexes the data; runs the searches |
| **L** | Logstash | Collects data, parses and transforms it, and ships it into Elasticsearch |
| **K** | Kibana | Web UI: search, charts and dashboards on top of Elasticsearch |
| (+) | Beats | Small agents installed on servers that send data to Logstash or Elasticsearch |

Flow: **Beats → Logstash → Elasticsearch → Kibana**. Because Beats were added later, the whole family is now often called the **Elastic Stack**. On AWS the equivalent is OpenSearch Service with **OpenSearch Dashboards** (the Kibana fork).

---

Q. What is Logstash?

A. (Teacher's definition) Logstash is a storage tool that makes it easy to use the search engine to search through log data. It also contains other tools that make it easier for Elasticsearch to access other services, which are called beats. Commonly used beats include FileBeat (for accessing files) and MetricBeat (for accessing analytics services).

Expanded: Strictly speaking, Logstash doesn't *store* data (Elasticsearch does that). It's the **pipeline** in front of Elasticsearch, working in three stages:

1. **Input:** read from a source (log files, Beats, Kafka, S3, databases).
2. **Filter:** turn messy log lines into structured JSON. For example, the **grok** filter splits `127.0.0.1 - GET /cart 500` into fields `ip`, `method`, `path`, `status`.
3. **Output:** send the clean JSON into Elasticsearch (or elsewhere).

It's the ELK equivalent of the Transform step in ETL.

**Beats** are lightweight agents you install on each server. They don't transform much; they just collect and ship data to Logstash or straight to Elasticsearch.

| Beat | What it ships | Example |
|---|---|---|
| **Filebeat** | Lines from files (log files) | Tail `/var/log/nginx/access.log` on every web server |
| **Metricbeat** | System and service metrics | CPU, memory and disk every 10 s; MySQL or Kafka stats |
| Packetbeat | Network traffic | HTTP request latency between services |
| Heartbeat | Uptime checks | Ping a URL every minute, record up/down |

---

Q. What is Kibana?

A. (Teacher's definition) Kibana is ELK's visualization tool. You put data into Elasticsearch, and that data is automatically made available for visualizations to be created in Kibana. Kibana comes with a convenient web-based interface, so the visualizations that you create are pre-configured to be served on a website.

Expanded: Kibana is the "look at it" layer. It doesn't store anything itself. It's a web app that sends queries to Elasticsearch and draws the results. Once data is in an Elasticsearch index, you point Kibana at it (an **index pattern / data view**) and can immediately:

- **Discover:** search and filter raw documents (for example, every log line with `status: 500` in the last hour).
- **Visualize:** build charts (line, bar, pie, maps, heat maps).
- **Dashboards:** combine charts on one page that refreshes live. Because Kibana is already a web server, a dashboard is shareable by URL with no extra hosting.

It plays the same role in ELK that **QuickSight** plays on top of Redshift in Evan's Amazon outline, or Looker Studio on BigQuery.

| | Kibana | QuickSight / Looker Studio / Power BI |
|---|---|---|
| Reads from | Elasticsearch only | Many sources (warehouses, files, DBs) |
| Strength | Real-time log and event search, operational dashboards | Business reporting and KPIs |
| Hosting | Its own web server (part of the stack) | Managed SaaS |
| AWS equivalent | OpenSearch Dashboards | — |

Q. What language is the ELK stack written in?

A. (Teacher's definition) The ELK stack is 100% written in JavaScript.

Expanded: Only part of that is true. **Kibana** is JavaScript/TypeScript (Node.js on the server, React in the browser). **Elasticsearch** and **Logstash** run on the **JVM** (Java), and Logstash's plugins are written in Ruby (JRuby). **Beats** are written in **Go**. So you'll install a JDK-based service when you run Elasticsearch or Logstash, even though the UI you touch is JavaScript.

| Component | Language |
|---|---|
| Elasticsearch | Java (on Apache Lucene, also Java) |
| Logstash | Java + JRuby |
| Kibana | JavaScript / TypeScript (Node.js, React) |
| Beats | Go |

---

# Elasticsearch Follow-ups & Class Logistics

Only what Evan said or confirmed in class.

## Class logistics

- **Profiles are due this Friday** (Oct 23). Evan asked each student to explain the first project on their profile; next week the focus moves hard into **interview prep**.
- **Final presentations moved off this Friday** so people can focus on profiles. Evan is confirming one date with the program coordinator tomorrow. Capstones: brainstorming has been homework for three days; nobody has built infrastructure yet.
- **Company names on profiles stay the same** (decided above Evan). If a company is a bad fit for your story, a change can be requested, but sales has to approve it.
- **Vendors sometimes rewrite your most recent project** to match a client's job description. Evan confirmed this happens in big data too, and it's harder than in mobile because a tech change means a whole new narrative. His example: a student with Citibank on their CV being prepared for a Mastercard project; because the companies work closely together, the story needs very specific, accurate-sounding details.

---

## Elasticsearch: why eBay, not Google

Q. Why is eBay the classic Elasticsearch use case, and why wouldn't Google use it?

A. (Evan, in class) Google searches the entire internet, every server, no matter who owns it. eBay only searches its own auction listings. Every listing is created through eBay's listing form, so that form's data can simply be saved as JSON into Elasticsearch, and the search bar on eBay's site searches that JSON.

Expanded: Elasticsearch fits when **you own and control all the documents being searched**: product catalogs, listings, support articles, logs from your own servers. It isn't a web crawler. The data has to be pushed into it first.

| | Google | eBay |
|---|---|---|
| What's searched | The whole internet | Only eBay's own listings |
| Where the data comes from | Crawling other people's servers | eBay's own listing-creation form |
| Data format | Anything | Structured JSON per listing |
| Elasticsearch fit | ❌ Not designed for this | ✅ Push each listing as a JSON document, search it |

## Why Elasticsearch isn't in the course

Evan used to teach it, but Elasticsearch jobs come up "once in a blue moon". When they do, the client wants an **expert**, and the training can't make everyone an expert in something rare in job listings. Evan also said his own knowledge of Logstash isn't deep ("a little bit boring to learn about"). So for interviews, know what each ELK piece does, and don't claim deep Elasticsearch expertise.

---

# Working on a Data Engineering Team

Q. Who do data engineers work with day to day?

A. (Evan, in class) Among tech teams, mostly **DevOps** and **data science**, because data engineering responsibilities often bleed into both of those worlds. Outside tech, you work with **stakeholders**.

| Team | Why data engineers work with them |
|---|---|
| DevOps | Infrastructure, CI/CD, deployments, permissions overlap with pipeline work |
| Data science | They consume your data and features; you productionize their models' inputs |
| QA (sometimes) | Test your pipelines (see below) |
| Non-technical stakeholders | The business people whose decisions your data drives |

Q. What is a stakeholder?

A. (Evan, in class) An umbrella term for anybody in the company who has a job-related interest in your project but is not on the tech team. Example: on a marketing data project that brings data from various websites into a warehouse, the head of marketing (or a senior marketing VP overseeing the data side) is a stakeholder, because the analysis drives their decisions. The same goes for HR, finance, accounting or any other department. Saying **"non-technical stakeholders"** will usually fly in an interview.

---

Q. What does QA do on a data engineering team?

A. (Evan, in class) QA can be a separate team or something your own team does. If you're assigned QA, you review pull requests and test them, usually in the **UAT environment**, to see whether the updated code breaks any part of the pipeline. If there's a problem, you reject the PR with a note explaining why, and the author fixes it before submitting again. A dedicated QA team's whole job is testing other people's code: running the tests and checking that the infrastructure still works and the code runs as expected.

Expanded: A **QA engineer** is a testing specialist across many tech stacks, not a data engineering specialist. If a test fails they may not be able to fix it; they'll alert the data engineering team. Evan never worked anywhere with a dedicated QA team: every data engineering team he was on did its own QA. That's a safe default for your interview narrative.

| | Your team does QA | Dedicated QA team |
|---|---|---|
| Who reviews | Teammates review each other's PRs | QA engineers |
| Where tested | UAT environment | UAT environment |
| Failing test | Reviewer rejects the PR with a note | QA alerts the data engineers |
| Evan's experience | ✅ Every team he worked on | Never had one |

---

Q. Are there integration tests for data pipelines?

A. (Evan, in class) Yes. Integration tests are commonly run as part of the CI/CD pipeline, but there should also be an integration test suite outside CI/CD for general testing of the infrastructure, because there are many pieces that have to work together. They're written in the **same testing framework as unit tests** (e.g. PyTest), just in a different style. Typically the test creates a **small test data object** and sends it through each stage of the pipeline to check the expected things happen. The test data usually has **predictable flaws** built in, and is small enough not to waste time or money. Ideally the suite runs as fast as possible, though that isn't always possible.

| | Unit test | Integration test |
|---|---|---|
| Scope | One function | Several pipeline stages / services together |
| Data | Tiny inline inputs | Small test dataset with known, deliberate flaws |
| Where it runs | CI/CD on every PR | CI/CD **and** a standalone suite |
| Framework | PyTest | PyTest (same framework, different style) |
| Example | `clean_status()` drops negative bike counts | Test file lands in Bronze → Glue → Silver has the bad rows removed → Gold totals correct |

Q. What is code coverage?

A. (Evan, in class) The percentage of lines of code that have tests written for them. It's checked automatically; **SonarQube** is a framework often integrated into the CI/CD pipeline for this.

Expanded: Evan's first major assignment at **JPMorgan Chase** (late 2019 to late 2020, before AI tools) was raising a very large application (about 1.5 GB of code) from **20% to 75%** coverage. Writing tests for other people's code meant reading undocumented code to work out what it should do. It took months, and the test suite went from about **5 minutes to 45 minutes**. Today, Claude Code could likely write those tests in under an hour. A classmate said that at PayPal nearly every unit test was written by Claude Code. Takeaway for interviews: big codebases mean slow test suites, coverage targets are often set by the org (75% was the bar), and AI-assisted test writing is now normal.

---

# Homework & ELK Follow-ups

Only what Evan said or confirmed in class.

## Homework (assigned at end of class)

- **Main:** write as detailed a story as you can for the **first project on your profile** (for Alex: Amazon / Project Kuiper; see `profile/Amazon Project Outline.md`).
- **Reading:** a little about **Spark Declarative Pipelines** (Lakeflow / DLT).
- Evan will spend the **first hour of upcoming classes** going through each student's profile narrative.

## ELK follow-ups

- **Why Evan says ELK is "all JavaScript":** ELK is web-oriented. JSON comes from JavaScript and is how websites usually talk to each other, so a web-and-search tool fits naturally with JavaScript. (Only Kibana is actually JavaScript; see the language table above.)
- **What you need to know:** everyone should understand what Elasticsearch is, but hands-on isn't required, since those jobs are uncommon. **Alex specifically:** OpenSearch is on your profile, so be able to talk about the part you used: the **vector database engine in AWS OpenSearch** (Bedrock embeddings stored and searched there for the RAG workload).

---

# Profile Narratives & Interviews

## Migration projects

Q. What is a data migration project, and what does the work look like?

A. (Evan, in class) Moving data from a source to a destination. There's no real processing stage: the data is only changed as far as needed to fit the target environment. They're ideal consultant work: very important to the company, but the company doesn't want the engineers long term, so it hires people who know the data and the tech for exactly as long as the migration lasts.

Expanded: Evan's example is the **American Bureau of Shipping** moving from **GEMS** (Oracle) to **Fusion** (Oracle Cloud). Day to day, the engineers are:

- validating the schema and checking data types;
- tracking down columns that exist in one system but not the other (e.g. the data lives in a different table in the new system);
- proving the data in the destination matches the source, just reshaped for the destination's framework.

| Fact | Detail |
|---|---|
| Rough size estimate | **~6 months per 1 PB** migrated (Evan's rule of thumb, not an industry standard figure) (400 PB is a multi-year-scale effort; depends on team size and infrastructure) |
| Typical source (on-prem Hadoop, still running in 2026) | **Hive**, possibly with external tables, raw files on **HDFS**, or **HBase** (mention any Hadoop-stack tools your narrative lists) |
| Target example | BigQuery, which follows the same data warehouse rules as Redshift, Delta Lake, Synapse or Hive |
| Masking on BigQuery | Column-level data masking policies, using BigQuery **policy tags** and the **Data Catalog / Dataplex Universal Catalog** |
| Governance | Matters **more** in migrations: the old database's roles and permissions must be replicated in the new one |
| ETL workload migration | Different from a data migration: you're moving the *processing jobs*, not just the data |

## Security & governance in interviews

Q. Do data engineering interviews ask about security?

A. (Evan, in class) Rarely in a standard interview. Some cloud interviews ask a couple of questions, usually framed as **data governance**: masking, granting permissions, roles and policies. Data engineers need a basic understanding (databases have users, roles and permissions), but deep security is the **cyber security** team's job; you work with them on the data side. Governance questions are more likely if your project is a migration.

## How the interview rounds work

| Round | What happens | How to prepare |
|---|---|---|
| Screening | Ideally a ~5-minute call with a non-technical person; increasingly an AI interview with quiz questions | Basic facts about your profile |
| Round 1 | Mostly quiz questions (often a list written by an engineer, read by a non-technical person) | Evan's interview Q&A document, reading assignments |
| Round 2 / 3 | A **technical person** asks about your last project: what you built, which technologies, what challenges you hit, how you solved them, the human-level story | **Real stories**. This round decides the job |

Q. Why does Evan keep pushing hands-on building?

A. (Evan, in class) People who only memorize quiz answers fall apart in round 2, because the interviewer immediately sees they've never done the work. Interviewers want stories of things you've actually done, like the pain of setting up your own cloud permissions, or a **row count validation failure** loading into Redshift and the checks you ran to figure it out. Evan recommends everyone **rebuild their most recent profile project on a small scale**; it makes talking about it natural.

Expanded: Your Training 24/28 work is exactly this kind of material. The Training 24 Glue Save overwriting your incremental script, the doubled landing COPY (15,112 rows vs 7,556 unique), and Training 28's `ADLSGen2ForbiddenError` blocked on a missing RBAC role are real problem-and-fix stories.

## Other profile questions Evan answered

| Question | Evan's answer |
|---|---|
| Is ETL outdated? | No. ETL is still a totally valid way to build a pipeline and plenty run in production. ELT is just considered more modern. If ETL serves the company, leave it |
| Typical team size? | Anything: a one-person team, four people, or one of 20. Evan's own: 3 architects (Adobe Experience Cloud, WebMD pipeline), a 10-person team (JPMorgan Chase), and a remote team under one project owner (Anthem, Teradata SQL → Redshift SQL) |
| Is every project "big data"? | No. Evan has heard interviews describing 25 MB a day arriving as an emailed Excel file, all the way up to massive migrations |
| Datadog on a profile? | You build the pipelines that deliver data to Datadog, which is a monitoring tool producing internal dashboards. It only matters a lot if you used it to monitor the migration |
| GraphQL vs. REST? | Same basic job; just call them APIs. Data interviews don't go deep on GraphQL, but it's a legitimate data engineering topic |
| Kill switch / circuit breaker / feature flags? | Yes, on the **orchestration** side. Airflow sensors in a profile imply you did this in **Airflow** |
| A business change in the news (e.g. Southwest switching to assigned seating)? | Great narrative material: a new seat column all the way through the pipeline, plus update logic for seat changes and overbooking. It justifies ingestion, warehouse and processing work |
| Capstone on GCP instead of AWS/Azure? | Fine, as long as the pipeline executes. Encouraged if BigQuery matches your interview narrative |
| Bomb an interview? | Doesn't mean you're out. Evan was later hired by the same Anthem interviewer who'd criticized his SQL answer the first time |

## Coding tests

- **Live coding** is basic Python: e.g. a function missing its `return` statement ("what's wrong?"), or a function that returns one thing, another, or both depending on conditions. Live coding won't involve DLT.
- **HackerRank-style** challenges do show up and often have nothing to do with the job. Some platforms (Evan named **Glider**) track head and eye movement.

---

# Databricks Lakeflow (Spark Declarative Pipelines)

Q. What is Lakeflow?

A. (Evan, in class) One of the hot topics in data engineering right now. It's known by **three names**: **Lakeflow**, **Spark Declarative Pipelines**, and **Delta Live Tables (DLT)**. Today's lab rebuilt yesterday's Citi Bike notebook pipeline (Bronze → Silver → Gold) as a Lakeflow pipeline, because this environment is what interview questions are about.

| Setting | Value in the lab |
|---|---|
| Where | **Jobs & Pipelines** → **ETL pipeline** |
| Name / file | `citibike_lakeflow_demo` / `lakeflow_demo.py` |
| Language | Python |
| Pipeline mode | **Triggered** (runs once when started), not **Continuous** |
| Compute | Serverless |
| Destination | Catalog (the workspace's default) + a target schema |

Expanded: **One-line answer:** a framework where you declare tables and views and their data quality rules in Python or SQL, and the engine works out the dependency order, incremental processing, checkpoints and retries.

Strictly, "Lakeflow" is Databricks' umbrella name for three products, and only one of them is the declarative pipelines framework:

| Lakeflow product | What it does | Formerly |
|---|---|---|
| **Lakeflow Connect** | Managed ingestion connectors (databases, SaaS apps) | (new) |
| **Lakeflow Declarative Pipelines** | Declarative ELT pipelines: `@dp.table`, expectations | Delta Live Tables (DLT) |
| **Lakeflow Jobs** | Orchestration: tasks, dependencies, schedules, retries | Databricks Workflows |

The open-source core of declarative pipelines was donated to Apache Spark as **Spark Declarative Pipelines** (Spark 4.1), which is why the import is `from pyspark import pipelines as dp`.

---

Q. What is Databricks Auto Loader?

A. (Evan, in class) A service designed for **incremental loading**, occasionally asked about in interviews. Every time new data arrives, it picks up only what's new since the last load, the same idea as the AWS incremental pipeline (EventBridge → Lambda → S3, Step Functions → Glue Bronze → Silver → Gold). You turn it on by using `cloudFiles` as the `readStream` format.

Expanded: Auto Loader **tracks which files it has already processed**, and Lakeflow manages the streaming state and **checkpointing** for you, so there's no manual `writeStream` checkpoint to configure. That's the Databricks equivalent of the checkpoint table you built by hand in Training 24.

```python
from pyspark import pipelines as dp     # newer name; older code uses: import dlt
from pyspark.sql import functions as F

@dp.table                                # streaming table
def bronze_station_raw():
    return (spark.readStream.format("cloudFiles")       # = Auto Loader
            .option("cloudFiles.format", "json")
            .schema(station_schema)                      # explicit schema (see the fix below)
            .load(source_path)
            .withColumn("source_file", F.col("_metadata.file_path"))
            .withColumn("ingested_at", F.current_timestamp()))
```

| Notebook pipeline (Training 28) | Lakeflow pipeline (today) |
|---|---|
| `spark.read.json(...)` + `saveAsTable` | `@dp.table` returning a `readStream` |
| You run cells in order | Lakeflow works out the dependency order (Bronze → Silver → Gold) |
| Manual checks for nulls/negatives | `@dlt.expect_or_drop(...)` decorators |
| Re-reads all files each time | Auto Loader only reads new files |

---

Q. What is a decorator in Python?

A. (Student answer Evan confirmed) Functionality added to an existing function without modifying its existing behavior. You recognize it by the `@` symbol on the line above a `def`.

Expanded: In Lakeflow the decorators are what make an ordinary function into a pipeline object. Evan's way to read them: a decorated function is like a SQL `CREATE TABLE AS`, and each `withColumn` is like one column line in the `SELECT`.

| Decorator | Meaning |
|---|---|
| `@dp.table` | Streaming table (used for Bronze with Auto Loader) |
| `@dp.materialized_view` | Materialized view (used for Silver and Gold) |
| `@dlt.expect_or_drop("name", "condition")` | Data quality rule: rows failing the condition are **dropped** |
| `@dlt.expect(...)` | Same check but only **records** violations (rows kept) |

In the lab (with the class runtime), `dp` (pipelines) had no `expect_or_drop`, so the fix was `import dlt` and `@dlt.expect_or_drop`. Newer runtimes may expose expectations under `dp` too; check the current docs before quoting this in an interview. The editor still red-underlined the import, but it worked.

---

Q. What's the difference between a table, a view and a materialized view?

A. (Evan, in class)

- A **table** is durable: it stays saved across logouts and restarts.
- A **view** looks like a table (schema, rows, columns) but is really the result of a query (`CREATE VIEW AS SELECT ...`).
- A **materialized view** stores the query's results so they persist and are fast to read. It doesn't re-query on every read; it's only updated when you refresh it after the source changes. It's good for small, aggregated subsets you reference often.

Expanded: One refinement to Evan's explanation. Only **temporary** views disappear when your session ends. A regular `CREATE VIEW` saved in a catalog (like Unity Catalog) stays defined permanently, but stores **no data**, so it re-runs its query every time you read it. A materialized view **stores the results** and is refreshed on demand. In Lakeflow, the pipeline does that refresh each run.

| | Stores data? | Survives logout? | Freshness |
|---|---|---|---|
| Table | ✅ | ✅ | Whatever was written |
| Temporary view | ❌ (query only) | ❌ Session only | Re-runs query each read |
| View (saved in catalog) | ❌ (query only) | ✅ | Re-runs query each read |
| Materialized view | ✅ (cached results) | ✅ | As of last refresh |

---

## Silver and Gold in the lab

**Silver (`silver_station_clean`, materialized view):**
- Three expectations: `valid_station_id` (`station_id IS NOT NULL`), `valid_bike_count` (`num_bikes_available >= 0`), and `valid_dock_count` (`num_docks_available >= 0`). A station can have zero bikes, never negative.
- Explodes the nested `data.stations`, pulls fields to top-level columns with `station.station_id` dot syntax, then `cast` + `alias`, and converts the timestamp.
- Finishes with `dropDuplicates(["station_id", "snapshot_ts"])`.

**Gold (`gold_hourly_availability`, materialized view):**
- Compute `snapshot_hour`.
- Window by `station_id, snapshot_hour`, ordered by snapshot time and source file descending; `row_number() = 1` keeps the latest reading.
- Then `groupBy(snapshot_hour)`: `countDistinct(station_id)`, `sum` bikes, `sum` docks, `avg` bikes.

This is the same logic as your Training 28 notebook Gold and the Redshift Gold.

Evan's result row (Oct 16, 8 PM): 2,518 stations, 33,473 bikes, 32,728 docks, 13.29 avg.

## Debugging the pipeline (what failed and why)

| Error | Cause | Fix |
|---|---|---|
| Silver: "Failed to read dataset `...default.bronze_station_raw` … could not be resolved" | Downstream symptom: **Bronze failed first** | Find the *first* traceback (the Bronze one) |
| Bronze: Auto Loader can't find any JSON files | Wrong `source_path`: files were under the landing folder, not `station_status` | Correct the path |
| "Can't extract value from data: need a complex type" | Auto Loader **inferred** `data` as a string, so `.stations` can't be exploded | Pass an explicit `StructType` schema with `.schema(station_schema)` |
| Orange warning in the editor | Performance hint, not an error | Ignore; run the pipeline |

Q. What are `StructType` / `StructField`?

A. (Evan, in class) Spark SQL types for describing a schema. A **StructType** is the struct (an object of named fields); a **StructField** represents one column. `ArrayType`, `StringType`, `LongType`, `BooleanType` are Spark's data types. Nested JSON means nesting them: a StructType with field `data` (a StructType) holding `stations` (an ArrayType of StructTypes of StructFields). It used to take 20–30 minutes to type out by hand; AI writes it now.

Evan's lesson on working in a dev environment: be somewhat cautious, not totally. In dev or a test cluster it's fine to experiment, and the orange "error" turned out not to be one.

---

Q. When do you use Lakeflow vs. a regular Databricks notebook?

A. (Evan, in class) Databricks can be an all-in-one platform: ingest, process, move, and serve data for BI or AI. **Lakeflow is strictly for ELT-style transformations.** Notebooks use classic Spark code that tells the system **how** to do the work. Declarative pipelines get closer to how SQL was meant to be: you say **what** you want and the system figures out how.

Expanded (correction): Lakeflow as a whole isn't only for transformations. Lakeflow **Declarative Pipelines** is the ELT-transformation part; Lakeflow **Connect** does ingestion and Lakeflow **Jobs** does orchestration (see the table under "What is Lakeflow?").

Evan's history: before big data, SQL was declarative. MapReduce handled internet-scale data but had to be written in Java, step by step. Ever since, big data has pushed back toward SQL-like code that reads like an English sentence. DLT / ELT syntax is the most modern version of that. It's called "declarative" because it's a compromise: as close to fully declarative as Python can get, but still with extra syntax (decorators).

## DLT vs. dbt

Q. Are DLT and dbt the same thing?

A. (Evan, in class) No. They're one letter apart but completely different. **DLT** (Delta Live Tables) is **exclusive to Databricks**. **dbt** (data build tool) is tightly integrated with Snowflake but works with Databricks, Redshift, BigQuery, Hive, Postgres and more.

Expanded (correction): this is now outdated. Databricks donated the declarative pipelines framework to Apache Spark in 2025 as **Spark Declarative Pipelines**, so the core runs on open-source Spark 4.1+. The *managed* product (serverless compute, the expectations UI, the event log, Lakeflow Connect/Jobs) is still Databricks-only.

| | DLT / Lakeflow | dbt |
|---|---|---|
| Runs on | Managed Lakeflow: Databricks only. Open-source core: Apache Spark 4.1+ (Spark Declarative Pipelines) | Snowflake (designed for it), Databricks, Redshift, BigQuery, Postgres, … |
| Language | Python (decorators) or SQL | SQL models + YAML config |
| Data quality | `expect` / `expect_or_drop` decorators | dbt tests |
| Evan's take | More syntax than needed | Almost nothing superfluous; every line is a column, a transformation, an alias |

Evan's opinion, the same reason he prefers **YAML over JSON** for config: the best syntax has nothing in it that isn't needed. dbt was built around Snowflake because older systems couldn't spare the compute to do transformations inside the warehouse. Snowflake's compute made in-warehouse ELT practical, part of the shift from ETL (Spark on a separate system) to ELT.

---

# Delta Lake Operations (roadmap topic, not taught in class)

Q. How does Delta Lake give ACID transactions on object storage?

A. (Not covered in class.) Through the **transaction log**, the `_delta_log/` folder next to the Parquet data files.

Expanded: every write adds a numbered JSON commit file (`00000000000000000010.json`) listing the data files it added and removed. Every 10 commits or so, Delta writes a Parquet **checkpoint** of the whole table state, so readers don't replay thousands of JSON files. A reader's view of the table is "whatever the log says is current", so a half-finished write is invisible until its commit file exists. Two writers race to create the next commit number, and the loser retries or fails (optimistic concurrency). Delta Lake is open source (Linux Foundation); Databricks adds managed features on top.

**Interview line:** "A Delta table is Parquet files plus a transaction log. Each commit is a JSON file in `_delta_log` saying which files were added or removed, so readers only see committed versions. That log is what gives ACID, time travel and schema enforcement on S3 or ADLS."

---

Q. How do you upsert into Delta, and do SCD Type 2?

A. (Not covered in class.) `MERGE INTO`, the same idea as the Redshift MERGE in Training 24.

```sql
MERGE INTO silver.stations AS t
USING updates AS s
ON t.station_id = s.station_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

Expanded: for **SCD Type 2** (keep history), the dimension has `is_current`, `valid_from`, `valid_to`. One MERGE does both steps if the source contains each changed row twice: once with the real key (to **close** the old row: `WHEN MATCHED AND t.is_current AND <attributes differ> THEN UPDATE SET is_current = false, valid_to = s.effective_ts`) and once with a NULL merge key (so it never matches and is **inserted** as the new current row). As with Redshift, the source must have at most one row per key per MERGE, so deduplicate first.

---

Q. Schema enforcement vs schema evolution?

A. (Not covered in class.)

| | Schema enforcement (default) | Schema evolution (opt-in) |
|---|---|---|
| Behavior | A write whose columns or types don't match the table is **rejected** | New columns are **added** to the table schema |
| How | Automatic | `.option("mergeSchema", "true")` on the write; for MERGE, `spark.databricks.delta.schema.autoMerge.enabled = true` (or `MERGE WITH SCHEMA EVOLUTION`) |
| Why | Stops bad data silently corrupting Silver/Gold | Lets sources add fields without a manual `ALTER TABLE` |

---

Q. What is time travel?

A. (Not covered in class.) Querying or restoring an older version of a table from the log.

```sql
DESCRIBE HISTORY silver.stations;                         -- versions, operations, who, when
SELECT * FROM silver.stations VERSION AS OF 12;
SELECT * FROM silver.stations TIMESTAMP AS OF '2026-10-20';
RESTORE TABLE silver.stations TO VERSION AS OF 12;         -- roll back a bad load
```

Uses: auditing, reproducing a report as of a date, undoing a bad write. It only reaches back as far as the data files still exist (see VACUUM).

---

Q. OPTIMIZE vs Z-ORDER vs liquid clustering, and what does VACUUM do?

A. (Not covered in class.)

| Command | What it does | Note |
|---|---|---|
| `OPTIMIZE t` | Compacts many small files into fewer large ones (~1 GB) | Fixes the small-files problem from streaming / frequent appends |
| `OPTIMIZE t ZORDER BY (col)` | Compacts and co-locates rows with similar `col` values, so data skipping reads fewer files | Rewrites everything each time; set at query time |
| **Liquid clustering** (`CLUSTER BY (col)`) | Replaces partitioning + Z-ORDER. Clustering is incremental, and the keys can be changed later without rewriting the table | The current Databricks recommendation for new tables; can't be combined with partitioning or Z-ORDER |
| `VACUUM t` | Deletes data files no longer referenced by the log and older than the retention period (default **7 days**) | After VACUUM, time travel to versions older than the retention fails. Never set retention below the longest-running query or stream |

**Interview line:** "OPTIMIZE compacts small files, Z-ORDER co-locates data on filter columns, liquid clustering is the newer incremental replacement for partitioning plus Z-ORDER, and VACUUM deletes old unreferenced files, which saves storage but limits how far back time travel can go."

Also worth knowing: **Change Data Feed** (`delta.enableChangeDataFeed = true`) records row-level inserts/updates/deletes per version, so downstream jobs can read only the changes (`table_changes('t', 12)`), the Delta equivalent of CDC (Training 24).

---

Q. How does Auto Loader handle schema changes?

A. (Not covered in class beyond the explicit-schema fix above.) Auto Loader infers the schema on first run and stores it at `cloudFiles.schemaLocation`. When new columns appear, `cloudFiles.schemaEvolutionMode` decides what happens.

| Mode | On a new column |
|---|---|
| `addNewColumns` (default) | Stream stops once, schema is updated, and the restarted stream includes the column |
| `rescue` | Schema never changes; unexpected fields go into the `_rescued_data` column |
| `failOnNewColumns` | Stream fails until you update the schema |
| `none` | New columns are ignored |

Auto Loader vs `COPY INTO`: both load only new files. `COPY INTO` is a simple, idempotent SQL command for thousands of files; Auto Loader is a streaming source that scales to millions of files and handles schema evolution.

Medallion architecture itself: see Training 0 / Training 5. Unity Catalog (`catalog.schema.table`, GRANTs, row filters, column masks) is roadmap Day 31.

---

# Interview-ready from today

| Question | Your one-line answer |
|---|---|
| Explain the Delta transaction log | JSON commits plus Parquet checkpoints in `_delta_log`; readers see only committed versions, which gives ACID and time travel |
| OPTIMIZE vs Z-ORDER vs liquid clustering | Compaction; co-location on filter columns; incremental, changeable clustering that replaces partitioning + Z-ORDER |
| VACUUM risk | Deletes unreferenced files older than 7 days by default, so time travel past that breaks |
| Delta MERGE / SCD2 | MERGE on the business key; for SCD2, close the current row and insert the new version in one MERGE |
| Schema enforcement vs evolution | Mismatched writes are rejected by default; `mergeSchema` / autoMerge adds new columns on purpose |
| Auto Loader vs COPY INTO | Both incremental; Auto Loader streams, scales to millions of files and evolves schema |
| What is Lakeflow? | Databricks' umbrella for Connect (ingestion), Declarative Pipelines (formerly DLT) and Jobs (orchestration) |
| Table vs view vs materialized view | Table stores data; view stores only a query; materialized view stores the query's results until refreshed |
