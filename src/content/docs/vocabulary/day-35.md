---
title: Day 35 Vocabulary
description: Glossary of terms and definitions from the Training 35 notes.
sidebar:
  order: 35
---

Vocabulary — Study Guide Day 35

Source: notes/Training 35.md

## Capstone
- **Practice run** — A rehearsal of capstone presentations, set for Monday, Nov 2.
- **Final presentations** — Capstone presentations, set for Friday, Nov 6.

## AI and Databases
- **Prompt with query results** — Running a SQL query and putting its results into an AI prompt, the simple way to give a model fresh data.
- **RAG (Retrieval-Augmented Generation)** — Retrieving relevant chunks from a vector store and adding them to a prompt.
- **Vector database** — A database that stores embeddings for similarity search.
- **Aerospike** — A NoSQL document database (also mentions graph and vector), removed from the profiles.
- **Couchbase** — A NoSQL document-oriented JSON database, removed from the profiles.
- **Bigtable** — GCP's wide-column NoSQL database for very high-throughput, low-latency key lookups.
- **Firebase / Firestore** — Google's app-facing NoSQL document database platform.
- **Memorystore** — GCP's managed in-memory Redis service.

## Dataflow
- **Service account** — A non-human GCP identity that services run as.
- **Compute Engine default service account** — `<project-number>-compute@developer.gserviceaccount.com`, which Dataflow workers run as by default.
- **roles/dataflow.worker** — The IAM role letting worker VMs run Dataflow work.
- **roles/storage.objectAdmin** — The IAM role for reading and writing objects in GCS.
- **roles/bigquery.dataEditor** — The IAM role for writing BigQuery tables.
- **Project number** — The numeric ID of a GCP project, separate from the project ID.
- **parse_known_args** — An argparse method that splits declared options from the rest, which go to Beam's pipeline options.
- **PipelineOptions** — The Beam object holding runner, project, region and other execution settings.
- **temp_location** — The GCS folder for a Dataflow job's temporary files.
- **staging_location** — The GCS folder where the job's code and packages are uploaded.
- **worker_machine_type** — The VM type for Dataflow workers, e.g. e2-standard-2.
- **e2-standard-2** — A Compute Engine machine type with 2 vCPUs.
- **num_workers / max_num_workers** — The starting worker count and the autoscaling ceiling for a Dataflow job.
- **save_main_session** — A Beam option that pickles global imports and variables so workers can use them.
- **Job graph** — The Dataflow console view of a pipeline's steps as a DAG.
- **Fusion** — Dataflow's optimization that merges consecutive steps to run together on a worker.
- **Cost tab** — The Dataflow job page tab showing the job's estimated cost.
- **Job metrics** — The Dataflow job page tab showing workers, throughput and resource use over time.
- **JSON Lines (JSONL)** — A file format with one JSON object per line.
- **Shards** — The number of output files a Beam write produces.

## Beam Patterns
- **yield** — Python keyword that emits values one at a time from a generator, used in FlatMap functions.
- **continue** — Python keyword that skips to the next loop iteration.
- **Key-value pair** — A two-element tuple whose first element is the key, needed by per-key transforms.
- **CombinePerKey** — Aggregates values per key; with a plain function, the function receives an iterable of values.
- **beam.Values()** — A transform that drops the keys from key-value pairs.
- **WriteToBigQuery** — The Beam sink that writes rows into a BigQuery table.
- **FILE_LOADS** — A WriteToBigQuery method that stages files in GCS and runs a BigQuery load job.
- **CREATE_NEVER** — A create disposition requiring the BigQuery table to already exist.
- **WRITE_TRUNCATE** — A write disposition that replaces the table's contents on each run.
- **WRITE_APPEND** — A write disposition that adds rows to the existing table.
- **Tagged outputs (dead-letter)** — A Beam pattern that routes bad records to a separate output.
- **Branching** — Applying more than one transform to the same PCollection.
- **Kill switch** — A configuration flag that turns a data source or market off, best applied at or before Bronze ingestion.
- **Modularity** — Designing separate pipelines per task so one can be changed or retired without touching the others.
- **DAG (Directed Acyclic Graph)** — Ordered steps that never loop back, as in Spark, Airflow and Dataflow.

## BigQuery
- **Dataset (BigQuery)** — A group of tables in a project and location, like a schema.
- **Slot** — BigQuery's unit of query compute.
- **On-demand pricing** — BigQuery billing per TB scanned by queries.
- **Partitioned table** — A table split by a column such as date, so filters skip whole partitions.
- **Clustered table** — A table sorted by chosen columns so filters read fewer blocks.
- **dim_station** — The station dimension table: ID, name, coordinates, capacity.
- **fact_station_snapshot** — The fact table of bikes and docks available per station per snapshot.
- **QUALIFY** — A SQL clause that filters on window function results.
- **ROW_NUMBER()** — A window function numbering rows within a partition.
- **SAFE_DIVIDE** — A BigQuery function that returns NULL instead of an error on divide-by-zero.
- **ST_GEOGPOINT** — A BigQuery function that builds a geography point from longitude and latitude.
- **CREATE OR REPLACE VIEW** — Defines or redefines a saved query as a view.
- **Epoch zero (1970)** — The Unix timestamp 0, which shows up when a timestamp is missing or zero.

## Looker Studio
- **Data source** — A connection from a Looker Studio report to a table or view.
- **Scorecard** — A chart showing a single KPI number.
- **Dimension** — A field used to group or label data.
- **Metric** — A field that is aggregated (sum, average, count distinct).
- **Aggregation** — How a metric is combined, set on the metric chip.
- **Display name** — The label shown for a field in a chart.
- **Refresh fields** — Re-reading a data source's schema after the underlying view changes.
- **Geo → Latitude, Longitude** — The Looker Studio field type for "lat,lon" text used in maps.
- **Bubble map** — A Google Maps chart with circles sized and colored by metrics.
- **Tooltip** — Text shown when hovering over a chart element.

## Narratives
- **Buy now, pay later (BNPL)** — Short-term point-of-sale loans paid in installments.
- **Hard credit pull** — A credit check that can lower a credit score if done often.
- **Producer / broker / consumer** — The streaming roles that send, store and read messages.
- **Gimel** — A PayPal-internal data access layer that appears in some profiles.
- **Black box** — A system you use through its inputs and outputs without needing to know its internals.
