---
title: Study Guide - Day 33
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 33: Fabric Direct Lake and Event Hubs Streaming"
sidebar:
  order: 330
---

Study Guide - Day 33 (source: notes/Training 33.md)

Note: built for verbal-quiz prep. The flashcards (Part 3) are phrased the way a quiz question would be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Direct Lake.** A Power BI storage mode only in Fabric: the semantic model reads Delta/Parquet files in **OneLake** directly, with no import copy and no live SQL. It's the **default** for lakehouse semantic models, so the previous day's model was already Direct Lake. Compared with **Import** (copy, refresh, fast) and **DirectQuery** (live SQL, slower), it gives Import-like speed with near-live freshness.

**DAX.** Power BI's formula language; "a combination of SQL with pandas syntax". **Measures** are evaluated at query time in the filter context: `Total Encounters = SUM('t'[total_encounters])`, `Readmission Rate = DIVIDE(SUM(...), SUM(...), 0)`. `DIVIDE` avoids divide-by-zero errors. Click **New measure** every time, or you overwrite the selected one. **Cards** show single KPIs.

**Mirroring.** "Making it so that the data in the SQL database is going to be continuously available in the Fabric environment." Continuous **CDC** replication into OneLake Delta tables, with no pipelines. Attempt: the DB had been deleted → **restored** from a restore point (slower than creating a new one) → system-assigned **managed identity** on the SQL logical server (portal → CLI → REST API) → blocked: "cannot mirror a SQL database with the managed identity **across tenants**". Abandoned.

**Event Hubs.** Azure's managed streaming broker; "works pretty much the same [as Kafka], except that you've got less junk to manage". **Namespace** ≈ cluster, **event hub** ≈ topic, partitions, consumer groups. Setup: Basic namespace → event hub `patient-events` → **shared access policies** `hospital-producer` (Send) and `hospital-consumer` (Listen), following least privilege → connection strings as environment variables.

**Producer and Consumer.** `pip install azure-eventhub` in a venv. The producer's `while True` loop generates a fake event → `create_batch` → `add` → `send_batch` → `sleep(2)`. The consumer's `receive(on_event=...)` first read the **backlog**, then one event every 2 seconds, like Kafka. Portal **Data Explorer → View events** shows events.

**Graceful Shutdown.** `while True` runs until stopped manually or by a failure. That's good for streaming, since data can arrive any time. A graceful exit: `try/except KeyboardInterrupt` (Ctrl+C), SIGTERM handlers, stop conditions, `flush()`/`close()`, checkpoint offsets.

**Eventstream.** Fabric item that ingests streams with no code. Source = Azure Event Hubs, using the **consumer (Listen)** key. Preview is a snapshot; Publish → Live view. Left schema-aware eventstream disabled.

**Eventhouse and KQL.** Eventhouse `hospital_real_time` with a default **KQL database**. Eventstream destination → Eventhouse (JSON). The table appeared via **Get data → existing eventstream**. KQL pipes: `t | take 10`, `| count`, `| summarize count() by event_type | order by ... desc`, `bin(ts, 1m)` + `| render timechart`. Dashed names need `['name']`. **Real-Time Dashboard** generated from the time-series query.

**Lakehouse Bronze.** A second eventstream destination → lakehouse table `bronze_patient_events`. The node must be connected or you get "operation is missing input". **Hot path** (Eventhouse, seconds) + **cold path** (lakehouse, medallion).

**Streaming Notebook.** "No default context" → attach the lakehouse and **set as default lakehouse**. Silver events (types, validate, dedup) → unified table joined with batch encounters → gold: facility (with `net_admissions` = admissions − discharges), 5-minute **tumbling window** timeline, diagnosis. `SELECT TOP` fails in PySpark cells, so use `display(df.limit(10))`.

**Streaming Semantic Model.** "Source tables do not exist or access was denied" → just retry. Measures: Total Streaming Events, Admissions, Discharges, Transfers, `Net Admissions = [Total Admissions] - [Total Discharges]`.

**Big Picture.** "Everything in all of these different systems is ultimately the same process. It's just being dressed up in different ways." Kafka = Kinesis = Event Hubs = Pub/Sub; the differences are features like Direct Lake and mirroring.

**Interview Prep.** The SME document's five questions: stopping bad data spreading, unexpected schema changes, SCDs, NoSQL vs warehouse, protecting payment data. Answer each with STAR tied to your profile.

---

# Part 2: Cheat Sheet

## Power BI Modes
- Import = copy + refresh · DirectQuery = live SQL · Direct Lake = read OneLake Delta directly (Fabric default)

## DAX
- `SUM`, `DIVIDE(a,b,0)`, measures from measures · New measure each time · cards for KPIs

## Mirroring
- CDC into OneLake · needs managed identity · same tenant · deleted DB → restore (slow)

## Event Hubs
- Namespace / event hub / partition / consumer group · Send vs Listen policies · connection string = secret
- `EventHubProducerClient.create_batch/send_batch` · `EventHubConsumerClient.receive`
- New consumer reads backlog first · Data Explorer → View events

## Fabric Real-Time
- Eventstream (source Event Hubs, Listen key) → Eventhouse/KQL DB → KQL queryset → Real-Time Dashboard
- Second destination → lakehouse bronze → notebook silver/gold → semantic model

## KQL
- `take`, `count`, `where`, `summarize ... by`, `order by`, `bin()`, `render timechart`, `['dash-name']`

## Gotchas
- Set default lakehouse · connect destination nodes · retry semantic model after writes · PySpark ≠ T-SQL

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is Direct Lake?
A: A Power BI storage mode in Fabric where the semantic model reads the Delta files in OneLake directly, so you get near Import-mode speed without copying data or running live SQL queries.

Q: Compare Import, DirectQuery and Direct Lake.
A: Import copies data into the model and needs refreshes, but it's fast. DirectQuery sends live queries to the source, which is fresh but slower. Direct Lake reads OneLake files directly, so it's fast and fresh, but only in Fabric.

Q: What is DAX?
A: Power BI's formula language for measures and calculated columns. It looks a bit like SQL aggregations with pandas-style table and column references.

Q: What is a measure?
A: A named calculation evaluated at query time for whatever filters a visual applies, so the same measure gives a total on a card and per-category values in a chart.

Q: Why use DIVIDE instead of the slash operator?
A: DIVIDE handles division by zero by returning an alternate value you choose, like zero, instead of an error.

Q: What is mirroring in Fabric?
A: Continuous replication of an operational database, like Azure SQL, into OneLake as Delta tables using change data capture, so the data is always available in Fabric without building pipelines.

Q: Why did mirroring fail in class?
A: The SQL server and Fabric were in different tenants, and mirroring with a managed identity can't cross tenants. It's an architectural restriction, not a missing permission.

Q: What is a managed identity?
A: An identity Azure creates and manages for a resource so it can authenticate to other services without stored passwords. A system-assigned one lives and dies with the resource.

Q: Map Event Hubs terms to Kafka.
A: A namespace is like a Kafka cluster, an event hub is like a topic, and both have partitions and consumer groups.

Q: Why create separate Send and Listen policies?
A: Least privilege. The producer can only send and the consumer can only read, so a leaked key does less damage.

Q: Why did the consumer print a burst of events first?
A: Event Hubs retained the events sent before the consumer started. A new consumer reading from the beginning processes that backlog first, then new events as they arrive, just like Kafka.

Q: When does a while True loop stop?
A: Only when it's stopped manually or by an external failure. For streaming that's desirable, because data can arrive at any time.

Q: What is a graceful shutdown?
A: Stopping a producer or consumer cleanly: catching Ctrl+C or SIGTERM, flushing buffered messages, closing the client and committing offsets, so nothing is lost or reprocessed.

Q: What is a Fabric Eventstream?
A: A no-code Fabric item that ingests a stream from a source like Event Hubs and routes it to destinations like an Eventhouse or a lakehouse.

Q: What is an Eventhouse?
A: Fabric's real-time analytics store, based on Azure Data Explorer. It holds KQL databases optimized for time-series event data.

Q: What is KQL?
A: Kusto Query Language, a read-only language where you start with a table and pipe rows through operators like where, summarize, order by and render.

Q: Why send the same stream to both an Eventhouse and a lakehouse?
A: It's the hot and cold path pattern. The Eventhouse gives live dashboards in seconds, and the lakehouse bronze table feeds the medallion pipeline for joined, historical analytics.

Q: A Fabric notebook says no default context exists. What do you do?
A: Attach the lakehouse in the Explorer and set it as the default lakehouse, so table names resolve.

Q: What does net admissions mean in the gold table?
A: Admissions minus discharges, roughly how many patients are currently admitted.

Q: What did Evan say is the real difference between all these platforms?
A: Not much. It's the same process dressed up differently: Kafka, Kinesis, Event Hubs and Pub/Sub all stream, and notebooks are notebooks. The differences are specific features like Direct Lake and mirroring.

Q: How do you stop bad data from spreading?
A: Validate between bronze and silver with not-null, range and duplicate checks, quarantine failures, use data quality gates that stop the pipeline, and alert on them.
