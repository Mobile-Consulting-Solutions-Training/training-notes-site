---
title: Study Guide - Day 35
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 35: Dataflow, BigQuery and Looker Studio"
sidebar:
  order: 350
---

Study Guide - Day 35 (source: notes/Training 35.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Presentation Dates.** **Practice run Monday Nov 2**, **final capstone presentations Friday Nov 6**. Tomorrow (Fri Oct 30) is ML fundamentals and MLflow; days 44–45 are flexible extension and marketing. Interviewers ask about Looker/BI only lightly; they care more about BigQuery and Dataflow.

**AI on a Pipeline.** For a data app, usually run a SQL query and put the results in the prompt. Use RAG (embeddings + vector DB) only when you need to keep asking about a body of unstructured content.

**Profile Cleanup.** Aerospike and Couchbase (NoSQL document databases) slipped into some generated skills lists. Remove both. GCP alternatives if needed: **Bigtable** (wide-column, low-latency) or **Firestore/Firebase** (app-facing documents).

**Dataflow Setup.** Workers run as the default Compute Engine service account `<project-number>-compute@developer.gserviceaccount.com`; it needs `roles/dataflow.worker`, `roles/storage.objectAdmin`, and BigQuery roles when writing to BigQuery.

**Bronze → Silver Job.** Read Bronze JSON, `FlatMap(extract_stations)` (try/except on bad docs, `continue` past stations missing ID/lat/lon, `yield` typed dicts), `Map(json.dumps)`, write JSON Lines. `parse_known_args()` splits your own options from Beam's pipeline options, so the same script runs anywhere.

**Local Then Cloud.** Download one sample, run with `--runner DirectRunner` (a failure costs $0), then `--runner DataflowRunner` with project, region, temp/staging GCS paths, job name, `e2-standard-2` workers, num/max workers, `--save_main_session`. Each job took ~4–5 minutes. The console graph shows one box per labeled step.

**Beam Is an API.** Beam is the SDK, Dataflow the managed runner. (Evan guessed Dataflow's engine is Spark-based; it's actually Google's own engine. Beam can *also* run on Spark.)

**Same Pipeline Everywhere.** Ingest to object storage → process Bronze/Silver/Gold → warehouse → BI/AI. On-prem HDFS/Spark/Hive; AWS S3/Glue or EMR/Redshift; Azure ADLS via ADF/Databricks or Synapse; GCP GCS via STS/Dataflow or Dataproc/BigQuery/Looker.

**BigQuery Gold.** The GCP service asked about most, but "just another data warehouse". Created `dim_station` and `fact_station_snapshot` with `CREATE TABLE IF NOT EXISTS` (partition by date, cluster by station for cost). Project → dataset → table.

**Silver → Gold Job.** Read Silver → `Map(parse_station)` → `Filter` None → key by station → `CombinePerKey(newest_station)` → `beam.Values()` → `WriteToBigQuery` with `FILE_LOADS`, `CREATE_NEVER`, `WRITE_TRUNCATE`. Bug: a two-argument combine function → "missing 1 required positional argument: 'b'"; `CombinePerKey` with a plain function passes one iterable. Fixed, tested locally, resubmitted as a new job. Cost tab: $0.00.

**Key, Combine, Drop Key.** Per-key operations need (key, value) tuples; remove the key afterwards. Same idea as the old Spark RDD `reduceByKey`/`combineByKey`. Kafka messages also have a key (the producer sets it; the offset is separate).

**Graph Steps and Branching.** One pipeline step = one graph stage; it's a DAG. Keep steps separate for monitoring (Dataflow fuses them internally anyway). Prefer separate pipelines per target (warehouse vs NoSQL) for modularity: decommission by turning off a schedule, not rewriting code. Kill switches belong at or before Bronze ingestion.

**Status to Fact Table.** Two more jobs: station status Bronze → Silver (17,633 records), then Silver → `fact_station_snapshot`. Summary: 2 snapshots, 17,149 rows, 2,519 stations, total 235,884 bikes, but a **1970** first snapshot = epoch-zero timestamps that a quality check should catch.

**Views and QUALIFY.** `v_station_latest`: `QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY snapshot_ts DESC) = 1`, joined to `dim_station`, with rounded availability percent. QUALIFY filters on window functions like HAVING filters on aggregates.

**Looker Studio.** Blank report → Add data → BigQuery → view. Three scorecards (count distinct stations, sum bikes available, average availability). Aggregation is changed on the metric chip, not the dimension. The map: an `ST_GEOGPOINT` field gave "invalid dimension"; fix was a text `"lat,lon"` field via `CONCAT`, **refresh fields** on the data source, set type to Geo → Latitude, Longitude, then recreate the bubble map (size = bikes available, color = availability %, tooltip = station name).

**Cleanup.** Make sure nothing billable is left running (streaming jobs, clusters). Evan's AWS demos cost well over $100.

**Narrative Q&A.** Migrations (STS/DMS) don't transform. A loan risk-scoring algorithm belongs to data science/finance/app teams; the data engineer lands the decision data via a producer → broker → Bronze, keeps it queryable and available to compliance. Company-internal tools (e.g. PayPal's Gimel): know what they do, treat them as a black box. Learn Beam only if your narratives are GCP.

---

# Part 2: Cheat Sheet

## Dataflow
- Worker SA = `<num>-compute@developer.gserviceaccount.com` · roles: dataflow.worker, storage.objectAdmin, bigquery.dataEditor
- DirectRunner first → DataflowRunner · temp/staging in GCS · e2-standard-2 · max_num_workers caps cost
- `parse_known_args()` → your args vs pipeline args · `--save_main_session` ships globals to workers

## Beam Patterns
- FlatMap to explode · Filter for validation · Map(lambda x: (key, x)) → CombinePerKey → Values
- CombinePerKey(fn) with a plain function: fn gets an iterable
- WriteToBigQuery: FILE_LOADS · CREATE_NEVER · WRITE_TRUNCATE / WRITE_APPEND

## BigQuery
- Project → dataset → table · PARTITION BY DATE(ts) · CLUSTER BY key
- Latest per key: `QUALIFY ROW_NUMBER() OVER (PARTITION BY k ORDER BY ts DESC) = 1`
- `SAFE_DIVIDE` avoids divide-by-zero · watch for 1970 timestamps

## Looker Studio
- Blank report → Add data → BigQuery · aggregation on metric chips
- Map: text "lat,lon" → refresh fields → Geo type → new bubble map

## Design Rules
- One pipeline per target · kill switch before Bronze · DE owns data movement, not the scoring model

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: When are the practice run and the final presentations?
A: The practice run is Monday, November 2, and the final presentations are Friday, November 6.

Q: How should a data app feed fresh pipeline data to an AI model?
A: Usually by running a SQL query and putting the results in the prompt. RAG with a vector database is only worth it when you need to keep querying a body of unstructured content.

Q: Which service account do Dataflow workers run as, and what roles does it need?
A: The project's default Compute Engine service account. It needs the Dataflow worker role, storage object admin for the buckets, and BigQuery data editor and job user roles if it writes to BigQuery.

Q: How do you run the same Beam script locally and on Dataflow?
A: Change the runner flag. DirectRunner runs it on your machine; DataflowRunner submits it to GCP along with project, region, temp and staging locations and worker settings.

Q: Why test with the DirectRunner first?
A: It runs on your laptop, so bugs cost nothing, and a Dataflow job takes minutes just to start workers.

Q: What does parse_known_args do in a Beam script?
A: It separates the options you defined, like input and output, from everything else, which gets passed to Beam as pipeline options like runner and project.

Q: Is Beam an execution engine?
A: No. Beam is the programming model and SDK. A runner like Dataflow, Spark or Flink actually executes the pipeline.

Q: What's the common shape of a pipeline on every cloud?
A: Ingest into object storage, process the data up through bronze, silver and gold, load gold into a warehouse, and connect BI or AI tools on top.

Q: Why add a key and then remove it in a Beam pipeline?
A: Per-key transforms like CombinePerKey need key-value pairs. You key by something like station ID, combine to keep the newest record per station, then drop the key with Values before writing.

Q: Why did the silver-to-gold job fail with "missing 1 required positional argument b"?
A: The combine function took two arguments, but CombinePerKey with a plain function passes it one iterable of values. Rewriting it to take the iterable and return the newest record fixed it.

Q: What do CREATE_NEVER and WRITE_TRUNCATE mean in WriteToBigQuery?
A: CREATE_NEVER means the table must already exist. WRITE_TRUNCATE replaces the table's contents on each run, so reruns don't duplicate data.

Q: Does each step in Beam code show up in the Dataflow graph?
A: Yes, each labeled step is a box in the job graph, which is a directed acyclic graph. Dataflow may fuse steps internally, but the labels help with monitoring and debugging.

Q: Should one pipeline write to both a warehouse and a NoSQL store?
A: Usually build two dedicated pipelines. If one target is decommissioned, you just turn off its schedule instead of changing and redeploying shared code.

Q: How do you get the latest row per key in BigQuery?
A: Use QUALIFY with ROW_NUMBER over a partition by the key ordered by timestamp descending, and keep row number one.

Q: What does QUALIFY do?
A: It filters on the result of a window function, the way HAVING filters on aggregates.

Q: How do you cut BigQuery table scan costs?
A: Partition by date, cluster by commonly filtered columns, and select only the columns you need.

Q: The data showed a first snapshot in 1970. What does that mean?
A: Some timestamps were zero or missing and got converted to the Unix epoch. A silver or gold quality check should reject or null those.

Q: How do you connect Looker Studio to BigQuery?
A: Create a blank report, add data, pick the BigQuery connector, then choose the project, dataset and table or view.

Q: How did the bubble map finally work in Looker Studio?
A: By making a text field of latitude comma longitude in a BigQuery view, refreshing the data source's fields, setting that field's type to geo latitude-longitude, and recreating the chart.

Q: Is building a loan risk-scoring algorithm a data engineer's job?
A: No. That belongs to data scientists, finance and application developers. The data engineer makes the input data available and lands the decisions in the stream and the warehouse for analytics and compliance.

Q: How much should you know about a company's internal data tools?
A: What they are and what they do. Beyond that, it's reasonable to say you ingested data from them and treated them as a black box.
