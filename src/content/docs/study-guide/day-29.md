---
title: Study Guide - Day 29
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 29: Elasticsearch, the ELK Stack, and Databricks Lakeflow"
sidebar:
  order: 290
---

Study Guide - Day 29 (source: notes/Training 29.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Elasticsearch.** A combination of a search engine and a NoSQL database, built on **Apache Lucene**. It stores JSON documents in **indexes** and searches them like a search engine (full-text, fuzzy, ranked by **relevance score**) using a JSON Query DSL over REST, not SQL. Fast because Lucene builds an **inverted index** (word → documents). Classic use: **eBay's** site search, because eBay owns every listing and can push each one in as JSON; Google crawls the whole internet, which Elasticsearch isn't built for. **AWS OpenSearch** is AWS's fork after Elastic's 2021 license change; OpenSearch Service is managed and supports **vector search**, which is why it appears as the vector database in RAG pipelines.

**The ELK Stack.** For log analytics: **E**lasticsearch (stores, indexes, searches), **L**ogstash (input → filter, e.g. **grok** parsing → output; the pipeline in front, not storage), **K**ibana (web UI: Discover, Visualize, Dashboards, shareable by URL). **Beats** are lightweight shippers (Filebeat for log files, Metricbeat for metrics, Packetbeat, Heartbeat). Flow: Beats → Logstash → Elasticsearch → Kibana; now called the Elastic Stack. Evan said it's all JavaScript; actually only Kibana is (Elasticsearch and Logstash are Java/JVM, Beats are Go). ES jobs are rare and want experts, so know the pieces but don't claim deep expertise.

**Working on a DE Team.** Data engineers mostly work with **DevOps** and **data science**, plus **non-technical stakeholders** (anyone with a job interest in the project outside tech, like a head of marketing). **QA** may be a separate team or your own: review PRs and test in **UAT**, rejecting with a note if something breaks. Evan's teams always did their own QA.

**Testing Pipelines.** **Integration tests** run in CI/CD and as a standalone suite, written in the same framework as unit tests (PyTest): send a small test dataset with **predictable flaws** through each stage and check the results. **Code coverage** = % of lines with tests, often checked by **SonarQube**. Evan raised a huge app from 20% to 75% at JPMorgan; the suite went from 5 to 45 minutes. AI now writes many tests.

**Migration Projects.** Moving data from source to destination with only the changes needed to fit the target: validate schemas and types, find columns that moved, prove the data matches. Ideal consultant work. Rough size: ~6 months per petabyte. Common sources: Hive, HDFS, HBase. **Governance matters more**: replicate roles and permissions; masking on BigQuery uses policy tags. Migrating ETL workloads (jobs) differs from migrating data.

**Interviews.** Security is rarely asked except as **data governance** (masking, roles, permissions). Rounds: screening (often AI), round 1 quiz questions, round 2/3 a technical person asks about your last project (what you built, challenges, fixes); this decides the job. Memorized answers fall apart there, so rebuild your profile project small and collect real problem-and-fix stories. ETL isn't outdated. Team sizes and data volumes vary widely. Feature flags/kill switches belong to orchestration. Live coding is basic Python. Bombing one interview doesn't end you.

**Databricks Lakeflow.** One hot topic with three names: **Lakeflow**, **Spark Declarative Pipelines**, **Delta Live Tables (DLT)**. Created under Jobs & Pipelines → ETL pipeline; **Triggered** (once) vs **Continuous** mode; serverless compute. **Auto Loader** = incremental loading with `readStream.format("cloudFiles")`; it tracks processed files and Lakeflow manages checkpoints (the hand-built Training 24 checkpoint, automated). Lakeflow works out the dependency order.

**Decorators.** Functionality added to a function without changing it, marked with `@`. `@dp.table` (streaming table, Bronze), `@dp.materialized_view` (Silver, Gold), `@dlt.expect_or_drop(name, condition)` (drop failing rows), `@dlt.expect` (record only). A decorated function reads like `CREATE TABLE AS`.

**Table vs View vs Materialized View.** Table: stores data, durable. View: a saved query, stores no data, re-runs on every read (temporary views vanish with the session). Materialized view: stores results, refreshed on demand (Lakeflow refreshes each run).

**The Lab.** Silver: expectations (station_id not null, bikes ≥ 0, docks ≥ 0), explode `data.stations`, cast, `dropDuplicates`. Gold: latest reading per station per hour with `row_number() = 1`, then hourly totals. Errors: Silver failing was a symptom of **Bronze failing first** (find the first traceback); wrong `source_path`; "need a complex type" because Auto Loader inferred `data` as a string → explicit **`StructType`/`StructField`** schema.

**Lakeflow vs Notebook vs dbt.** Lakeflow is strictly for ELT transformations and is **declarative** (say what you want); notebooks are imperative Spark (say how). DLT is Databricks-only (Python decorators or SQL, expectations); **dbt** works on many warehouses (SQL + YAML, tests) and has less extra syntax.

---

# Part 2: Cheat Sheet

## Search and Logs
- Elasticsearch = search engine + NoSQL · Lucene inverted index · JSON docs in indexes · relevance score
- eBay (own data) vs Google (crawl) · OpenSearch = AWS fork, vector search
- ELK: Elasticsearch · Logstash (input/filter/output, grok) · Kibana (dashboards) · Beats (Filebeat, Metricbeat)
- Languages: Java (ES, Logstash) · JS (Kibana) · Go (Beats)

## Team and Testing
- DevOps · data science · non-technical stakeholders · QA in UAT
- Integration tests: small flawed dataset through every stage, PyTest · coverage via SonarQube

## Migrations
- Validate schema, types, moved columns, matching data · ~6 months/PB · governance + masking

## Interviews
- Screening → quiz round → technical story round (decides)
- Rebuild your project small · real problem + fix stories

## Lakeflow
- Lakeflow = Spark Declarative Pipelines = DLT · Triggered vs Continuous
- Auto Loader: `cloudFiles` · tracks files + checkpoints
- `@dp.table` · `@dp.materialized_view` · `@dlt.expect_or_drop` · `@dlt.expect`
- Table / view / materialized view · explicit `StructType` for nested JSON · fix the first error first

## Comparisons
- Lakeflow (declarative, Databricks only) vs notebook (imperative) vs dbt (SQL + YAML, many warehouses)

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is Elasticsearch?
A: A search engine combined with a NoSQL database, built on Apache Lucene. It stores JSON documents and searches them like a search engine, ranked by relevance, instead of with exact SQL queries.

Q: Why is Elasticsearch fast at full-text search?
A: Lucene builds an inverted index, a lookup from every word to the documents that contain it, like the index at the back of a book.

Q: Why does eBay use Elasticsearch but Google doesn't?
A: eBay only searches its own listings, which it can push into Elasticsearch as JSON. Google searches the whole internet by crawling other people's servers, which Elasticsearch isn't designed for.

Q: What is AWS OpenSearch?
A: AWS's fork of Elasticsearch, made after Elastic changed its license. The managed service also does vector search, so it's often the vector database in RAG pipelines.

Q: What does each part of the ELK stack do?
A: Elasticsearch stores and searches the data, Logstash collects and transforms it on the way in, and Kibana is the web interface for searching and building dashboards. Beats are small agents that ship data from servers.

Q: Does Logstash store data?
A: No. It's the pipeline in front of Elasticsearch: it reads input, parses and transforms it, for example with grok, and outputs it to Elasticsearch, which does the storing.

Q: What language is the ELK stack written in?
A: Mixed. Elasticsearch and Logstash run on Java, Kibana is JavaScript, and Beats are written in Go.

Q: What is a stakeholder?
A: Anyone in the company with a job-related interest in your project who isn't on the tech team, like the head of marketing for a marketing data project.

Q: What does QA do on a data engineering team?
A: Reviews pull requests and tests them, usually in the UAT environment, to see if the change breaks the pipeline. If it does, they reject it with a note so the author can fix it.

Q: How do you write an integration test for a data pipeline?
A: Create a small test dataset with known, deliberate flaws, send it through every stage of the pipeline, and check that each stage did what it should, using the same framework as unit tests, like PyTest.

Q: What is code coverage?
A: The percentage of lines of code that have tests. It's usually checked automatically in CI/CD, for example with SonarQube.

Q: What does the day-to-day work on a data migration look like?
A: Validating schemas and data types, tracking down columns that live somewhere else in the new system, and proving the data in the destination matches the source.

Q: Why does governance matter more in a migration?
A: The old system's roles, permissions and masking rules have to be recreated in the new one, or data ends up exposed or inaccessible.

Q: Which interview round usually decides the job?
A: The technical round where someone asks about your last project: what you built, what broke and how you fixed it. Memorized quiz answers don't get you through it, real experience does.

Q: What are the three names for Databricks' declarative pipelines?
A: Lakeflow, Spark Declarative Pipelines and Delta Live Tables.

Q: What is Auto Loader?
A: Databricks' incremental loading feature. Using cloudFiles as the readStream format, it only picks up new files since the last run and tracks what it has processed, with Lakeflow managing the checkpoints.

Q: What is a Python decorator?
A: Something that adds functionality to a function without changing its existing behavior, written with an @ on the line above the def. In Lakeflow, decorators turn functions into tables, views and data-quality rules.

Q: What's the difference between expect and expect_or_drop?
A: expect_or_drop removes rows that fail the condition. expect keeps the rows and only records the violations.

Q: What's the difference between a view and a materialized view?
A: A view is a saved query that stores no data and re-runs every time you read it. A materialized view stores its results and is only updated when it's refreshed.

Q: Silver failed saying Bronze couldn't be resolved. Where do you look?
A: At the first error. Silver's failure was a symptom of Bronze failing first, so you fix the Bronze traceback.

Q: Why did the class need an explicit StructType schema?
A: Auto Loader inferred the nested data field as a string, so stations couldn't be exploded. An explicit schema with StructType and StructField told Spark the real nested structure.

Q: What's the difference between Lakeflow and dbt?
A: Lakeflow, or DLT, only runs on Databricks and uses Python decorators or SQL with expectations. dbt works on many warehouses, especially Snowflake, and uses SQL models with YAML and dbt tests.
