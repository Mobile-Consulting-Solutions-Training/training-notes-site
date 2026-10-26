---
title: Day 29 Vocabulary
description: Glossary of terms and definitions from the Training 29 notes.
sidebar:
  order: 29
---

Vocabulary — Study Guide Day 29

Source: notes/Training 29.md, walkthroughs/Walkthrough - Training 29 (Elasticsearch, Lakeflow and Profile Narratives).md

## Elasticsearch and OpenSearch
- **Elasticsearch** — A combination of a search engine and a NoSQL document database, built on Apache Lucene, that stores JSON and searches it search-engine style rather than with SQL.
- **Apache Lucene** — The open-source Java search library underneath Elasticsearch that builds and queries the inverted index.
- **NoSQL document store** — A database that stores flexible-schema documents (such as JSON) instead of fixed rows and columns.
- **Index (Elasticsearch)** — A named collection of JSON documents in Elasticsearch, roughly the equivalent of a table.
- **Document** — One JSON record stored in an Elasticsearch index.
- **Inverted index** — A lookup from every word to the documents containing it, like a book's index, which makes full-text search fast.
- **Full-text search** — Searching the words inside text fields for fuzzy, ranked matches instead of exact column values.
- **Relevance score** — The ranking value Elasticsearch gives each matching document, used to sort results by how well they match.
- **Query DSL** — Elasticsearch's JSON-based query language, sent over a REST API instead of SQL.
- **REST API** — An HTTP-based interface where requests and responses (here JSON) are sent to resource URLs.
- **AWS OpenSearch** — The AWS version of Elasticsearch, forked from the last open-source Elasticsearch release after Elastic's 2021 license change.
- **Amazon OpenSearch Service** — The managed AWS service that runs OpenSearch clusters for you.
- **Fork** — A separate project created by copying an existing codebase and developing it independently.
- **Vector search** — Finding stored embeddings nearest to a query embedding, used for semantic search.
- **Vector database** — A store for embeddings that supports nearest-vector search, the role OpenSearch plays in RAG pipelines.
- **Embedding** — A numeric vector representing the meaning of text or other content.
- **RAG (Retrieval-Augmented Generation)** — A pattern where relevant documents are retrieved (e.g. via vector search) and passed to an LLM to ground its answer.

## The ELK Stack
- **ELK stack** — Elasticsearch, Logstash and Kibana, used together for log analytics: collect, store/search and visualize.
- **Log analytics** — Collecting logs from many servers, storing them searchably and analyzing them on dashboards.
- **Logstash** — The ingestion pipeline in front of Elasticsearch that reads data, parses/transforms it into structured JSON and ships it out (it does not itself store data).
- **Input / Filter / Output (Logstash stages)** — Logstash's three stages: read from a source, transform the data, send it to a destination.
- **grok** — A Logstash filter that parses unstructured log lines into named structured fields.
- **Beats** — Lightweight agents installed on servers that collect and ship data to Logstash or Elasticsearch.
- **Filebeat** — The Beat that ships lines from files such as log files.
- **Metricbeat** — The Beat that ships system and service metrics such as CPU, memory and database stats.
- **Packetbeat** — The Beat that ships network traffic data such as HTTP request latency.
- **Heartbeat** — The Beat that runs uptime checks against URLs or services.
- **Kibana** — ELK's web-based visualization tool that queries Elasticsearch and draws searches, charts and dashboards.
- **Index pattern / data view** — The Kibana setting that points Kibana at one or more Elasticsearch indexes.
- **Discover (Kibana)** — The Kibana view for searching and filtering raw documents.
- **Visualize (Kibana)** — The Kibana feature for building charts such as line, bar, pie, map and heat map.
- **Dashboard (Kibana)** — A page combining several Kibana charts that refreshes live and is shareable by URL.
- **Elastic Stack** — The modern name for the ELK family once Beats were added.
- **OpenSearch Dashboards** — The AWS fork of Kibana used with OpenSearch.
- **QuickSight** — AWS's managed BI service, playing the role on top of Redshift that Kibana plays on Elasticsearch.
- **JVM (Java Virtual Machine)** — The runtime that Elasticsearch and Logstash run on, so they need a JDK installed.
- **JRuby** — A Ruby implementation on the JVM, used for Logstash plugins.

## Working on a Data Engineering Team
- **DevOps** — The team handling infrastructure, CI/CD, deployments and permissions, which overlaps with pipeline work.
- **Data science team** — The team that consumes data engineers' data and features to build models.
- **Stakeholder** — Anyone in the company with a job-related interest in your project who is not on the tech team (e.g. head of marketing).
- **Non-technical stakeholders** — The business people whose decisions your data drives, the safe interview phrase for stakeholders.
- **QA (Quality Assurance)** — Testing work, done by your own team or a dedicated team, checking that code changes don't break the pipeline.
- **QA engineer** — A testing specialist across many tech stacks who runs tests and alerts the owning team when something fails.
- **Pull request (PR)** — A proposed code change submitted for review, which a reviewer can approve or reject with a note.
- **UAT environment (User Acceptance Testing)** — The testing environment where PRs are tested before reaching production.
- **Unit test** — A test of one function with tiny inline inputs, run in CI/CD on every PR.
- **Integration test** — A test that sends a small test dataset with deliberate, predictable flaws through several pipeline stages to check they work together.
- **CI/CD (Continuous Integration / Continuous Delivery)** — The automated pipeline that tests and deploys code changes.
- **PyTest** — A Python testing framework used for both unit and integration tests.
- **Code coverage** — The percentage of lines of code that have tests written for them.
- **SonarQube** — A code-quality framework often integrated into CI/CD to check code coverage automatically.

## Profile Narratives and Interviews
- **Data migration project** — Moving data from a source to a destination, changing it only as needed to fit the target environment.
- **ETL workload migration** — Moving the processing jobs themselves to a new platform, as opposed to moving only the data.
- **Schema validation** — Checking that columns and data types match between source and destination systems.
- **Hive** — A Hadoop SQL data warehouse tool, a common on-prem migration source.
- **External table** — A table whose definition points at data files stored outside the database.
- **HDFS (Hadoop Distributed File System)** — Hadoop's distributed storage layer for raw files.
- **HBase** — A Hadoop NoSQL wide-column database.
- **BigQuery** — Google Cloud's serverless data warehouse.
- **Data masking** — Hiding or obscuring sensitive column values from users who shouldn't see them.
- **Policy tags (BigQuery)** — BigQuery labels attached to columns to enforce column-level access and masking policies.
- **Dataplex Universal Catalog (Data Catalog)** — Google Cloud's metadata and governance catalog where policy tags are managed.
- **Data governance** — Controlling data access and protection through masking, roles, permissions and policies.
- **Cyber security team** — The team responsible for deep security, which data engineers support on the data side.
- **Screening round** — A short first interview with a non-technical person or an AI interviewer asking basic profile questions.
- **Round 2 / 3 (technical round)** — The interview where a technical person probes your last project's tech, challenges and fixes; it usually decides the job.
- **Row count validation** — Checking that the number of rows loaded matches the expected count from the source.
- **ETL (Extract, Transform, Load)** — Transforming data on a separate system before loading it into the target; still valid and widely used.
- **ELT (Extract, Load, Transform)** — Loading raw data into the target first and transforming it there; considered more modern.
- **Datadog** — A monitoring tool producing internal dashboards, which data engineers may feed with pipelines.
- **GraphQL** — An API query language that does the same basic job as REST for data interviews.
- **Kill switch / circuit breaker** — An orchestration-side control that stops a pipeline or dependency when something goes wrong.
- **Feature flag** — A configuration toggle that turns functionality on or off without redeploying code.
- **Airflow sensor** — An Airflow operator that waits for a condition (such as a file arriving) before downstream tasks run.
- **Live coding test** — An interview exercise of basic Python, such as spotting a missing `return`.
- **HackerRank-style challenge** — An online algorithm coding test, often unrelated to the actual job.

## Databricks Lakeflow (Spark Declarative Pipelines)
- **Lakeflow (Spark Declarative Pipelines / Delta Live Tables / DLT)** — Databricks' declarative pipeline framework for ELT transformations, known by all three names.
- **Jobs & Pipelines** — The Databricks menu where an ETL pipeline is created.
- **Triggered mode** — A pipeline mode that runs once each time it is started.
- **Continuous mode** — A pipeline mode that keeps running and processes data as it arrives.
- **Serverless compute** — Compute that Databricks provisions and manages automatically for the pipeline.
- **Medallion architecture (Bronze / Silver / Gold)** — Layering data as raw (Bronze), cleaned (Silver) and aggregated business-ready (Gold).
- **Auto Loader** — A Databricks service for incremental loading that tracks which files it has processed and picks up only new ones.
- **cloudFiles** — The `readStream` format name that turns on Auto Loader.
- **readStream** — The Spark Structured Streaming API for reading data as a stream.
- **Incremental loading** — Processing only the data that is new since the last load.
- **Checkpointing** — Saving streaming progress state so a stream resumes where it left off; Lakeflow manages it for you.
- **`_metadata.file_path`** — A hidden file-metadata column giving the source file path of each row.
- **Decorator** — A Python feature, written as `@name` above a `def`, that adds functionality to a function without modifying its existing behavior.
- **`@dp.table`** — The Lakeflow decorator that defines a streaming table, used for Bronze with Auto Loader.
- **`@dp.materialized_view`** — The Lakeflow decorator that defines a materialized view, used for Silver and Gold.
- **Expectation** — A Lakeflow data-quality rule declared as a decorator on a table definition.
- **`@dlt.expect_or_drop`** — An expectation decorator that drops rows failing the condition.
- **`@dlt.expect`** — An expectation decorator that only records violations and keeps the rows.
- **`import dlt`** — The older Lakeflow Python module name, still needed in the lab for `expect_or_drop`.
- **Streaming table** — A table that is incrementally appended from a streaming source.
- **Table** — A durable object that stores data and survives logouts and restarts.
- **View** — A saved query that looks like a table but stores no data and re-runs its query on every read; a catalog view persists, only temporary views end with the session.
- **Temporary view** — A view that exists only for the current session.
- **Materialized view** — A view that stores its query results so reads are fast, updated only when refreshed (each run in Lakeflow).
- **Unity Catalog** — Databricks' catalog for tables, views and their governance.
- **explode** — A Spark function that turns each element of an array into its own row.
- **cast / alias** — Spark column methods that change a column's data type and rename it.
- **dropDuplicates** — A Spark method removing duplicate rows based on the given columns.
- **Window function / row_number()** — Numbering rows within a partition by an order, used with `row_number() = 1` to keep the latest reading.
- **countDistinct** — A Spark aggregate counting unique values in a column.
- **StructType** — A Spark SQL type describing a struct (an object of named fields), used to define a schema.
- **StructField** — A Spark SQL type representing one column (field) inside a StructType.
- **ArrayType / StringType / LongType / BooleanType** — Spark data types for arrays, strings, 64-bit integers and booleans.
- **Explicit schema** — A schema passed with `.schema(...)` instead of letting Spark infer it, avoiding wrong inferred types.
- **Schema inference** — Spark guessing column types from the data, which can wrongly read nested JSON as a string.
- **Declarative programming** — Stating what result you want and letting the system work out how, like SQL and Lakeflow.
- **Imperative (procedural) code** — Code that tells the system step by step how to do the work, like classic Spark notebooks.
- **MapReduce** — Hadoop's original Java-based, step-by-step framework for processing internet-scale data.
- **dbt (data build tool)** — A SQL-plus-YAML transformation tool built around Snowflake that also runs on Databricks, Redshift, BigQuery, Postgres and more.
- **dbt tests** — dbt's data-quality checks, the counterpart of Lakeflow expectations.
- **Snowflake** — A cloud data warehouse whose compute made in-warehouse ELT practical.
- **YAML** — A configuration format Evan prefers over JSON for having nothing superfluous.
