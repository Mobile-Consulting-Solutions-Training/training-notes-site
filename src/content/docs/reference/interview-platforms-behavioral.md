---
title: "Interview Questions: Platforms and Behavioral"
description: "Interview questions with the class answer, a corrected expanded answer and a short answer to say out loud: Databricks, DBT / Snowflake, Apache Airflow, Machine Learning, Agile, Soft Skills Questions, Project Experience Questions."
sidebar:
  order: 15
---

Each question has three parts: **A. (Class answer)**, the answer from the class question bank as given; **Expanded**, a corrected and fuller explanation (starting with **Correction:** when the class answer was wrong); and **Say it out loud**, a short answer for the interview itself. Start with the [traps to unlearn](/training-notes-site/reference/interview-prep/#traps-to-unlearn).

## Databricks


**Q. What is databricks?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Databricks is a cloud **data and AI platform** built by the original creators of Apache Spark. It popularized the **lakehouse**: data stays in your cloud object storage (S3, ADLS, GCS) as open **Delta Lake** tables, and one platform covers data engineering, SQL analytics, streaming and machine learning. Main parts:

| Part | Role |
|---|---|
| Workspace + notebooks | Collaborative development |
| Compute | All-purpose and job clusters, serverless compute, SQL warehouses |
| **Delta Lake** | ACID table format on object storage |
| **Unity Catalog** | Central governance: permissions, lineage, discovery |
| **Lakeflow** (Jobs, Declarative Pipelines / DLT, Connect) | Orchestration, declarative ETL, ingestion |
| MLflow, Mosaic AI | ML lifecycle and generative AI |

See [Training 4 notes](/training-notes-site/notes/training-4/) ("Databricks (The Lakehouse)"), [Training 29 notes](/training-notes-site/notes/training-29/) ("Databricks Lakeflow (Spark Declarative Pipelines)") and [Training 31 notes](/training-notes-site/notes/training-31/).

**Say it out loud:** "Databricks is a data and AI platform from the creators of Spark. It runs managed Spark and SQL on Delta Lake tables in your own cloud storage, the lakehouse model, with Unity Catalog for governance and Lakeflow for pipelines and jobs."

---

**Q. What is a notebook?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A notebook is an interactive document made of **cells** that mix runnable code, its output (tables, charts) and markdown text. In **Databricks**, notebooks are attached to a cluster, support several languages in one notebook with **magic commands** (`%python`, `%sql`, `%scala`, `%md`, `%run` to include another notebook), have a ready-made `spark` session, `display()` for results, real-time collaboration and Git integration (Repos/Git folders), and can be scheduled as **jobs**. Jupyter is the open-source equivalent. For production, keep shared logic in tested modules and use notebooks as thin entry points.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("When do you use Lakeflow vs. a regular Databricks notebook?").

**Say it out loud:** "A notebook is an interactive document of code cells, results and text. In Databricks it's attached to a cluster, can mix Python, SQL and Scala with magic commands, and can be scheduled as a job."

---

**Q. Which languages can you use with Databricks?**

**A. (Class answer)** *(no answer given)*

**Expanded:** **Python (PySpark), SQL, Scala and R**, mixed in one notebook with `%python`, `%sql`, `%scala` and `%r`. Java works for JAR jobs. SQL is also used through **Databricks SQL** warehouses, and Python dominates for data engineering and ML.

**Say it out loud:** "Python, SQL, Scala and R, and you can mix them in one notebook with magic commands. I mostly use PySpark and SQL."

---

**Q. What platforms can you use Databricks on?**

**A. (Class answer)** *(no answer given)*

**Expanded:** The three major clouds: **AWS, Microsoft Azure (Azure Databricks, a first-party Azure service) and Google Cloud**. The control plane is run by Databricks, while the data (and, in the classic setup, the compute) stays in **your** cloud account. Serverless compute runs in Databricks' account. There's also a free edition for learning.

**Say it out loud:** "AWS, Azure, where it's a native Azure service called Azure Databricks, and Google Cloud. The data stays in your own cloud storage."

---

**Q. What is a delta table**

**A. (Class answer)** *(no answer given)*

**Expanded:** A Delta table is a table stored in **Delta Lake format**: **Parquet data files plus a `_delta_log/` folder** of JSON commit files (with periodic Parquet checkpoints) that record every change. The log is the source of truth for which files make up the table at each version, which gives:
- **ACID transactions** (concurrent readers and writers are safe, failed writes leave no partial data)
- **`MERGE`, `UPDATE`, `DELETE`** on files in object storage
- **Time travel** (`VERSION AS OF`, `TIMESTAMP AS OF`) and `DESCRIBE HISTORY`
- **Schema enforcement** and opt-in **schema evolution**
- Maintenance: `OPTIMIZE` (compact small files), Z-ordering or liquid clustering, `VACUUM` (remove old files)

It is the default table format in Databricks.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("Delta Lake Operations") and [Training 13 notes](/training-notes-site/notes/training-13/) ("Delta and Iceberg").

**Say it out loud:** "A Delta table is Parquet files plus a transaction log in `_delta_log`. The log gives ACID transactions, MERGE and updates, time travel and schema enforcement on top of object storage."

---

**Q. What is a delta live table**

**A. (Class answer)** *(no answer given)*

**Expanded:** Delta Live Tables (DLT), now called **Lakeflow Declarative Pipelines** (and contributed to open-source Spark as **Spark Declarative Pipelines**), is Databricks' **declarative ETL framework**. You define **what** each table should contain, in SQL or Python, and the framework works out the dependency graph, orchestration, retries, infrastructure and incremental processing.

```python
import dlt
@dlt.table
@dlt.expect_or_drop("valid_bikes", "bikes >= 0")       # data quality expectation
def silver_status():
    return dlt.read_stream("bronze_status").select("station_id", "bikes", "ts")
```

Key features: **streaming tables** (incremental ingestion, often with Auto Loader) and **materialized views**, **expectations** (warn, drop or fail on bad rows), automatic lineage, `APPLY CHANGES` / `AUTO CDC` for CDC and SCD Type 1/2.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("What is Lakeflow?", "Databricks Lakeflow (Spark Declarative Pipelines)" and "Are DLT and dbt the same thing?").

**Say it out loud:** "Delta Live Tables, now Lakeflow Declarative Pipelines, is Databricks' declarative ETL framework. I declare each table as a SQL or Python query with data quality expectations, and it handles dependencies, orchestration and incremental processing, including CDC into SCD tables."

---

**Q. Describe the features of Delta Format**

**A. (Class answer)**

Delta is a data format that is primarily used in Databricks. It is very similar to Parquet format. It's structured, it's columnar, and it's compressed. One feature that it has which Parquet does not have is called time travel. Time travel allows us to query not just the most current version of the data, but also any past versions of the data.

**Expanded:**

**Correction:** Delta is not just "a data format similar to Parquet". It is a **table format**: the data files **are** Parquet (columnar, compressed), plus a **`_delta_log` transaction log**. The log is what provides the features Parquet alone doesn't have, and time travel is only one of them. Delta is also open source (Linux Foundation) and readable outside Databricks (Spark, Trino, Flink, Athena, Snowflake and others).

| Feature | What it gives you |
|---|---|
| ACID transactions | Safe concurrent writes, no half-written tables |
| `MERGE` / `UPDATE` / `DELETE` | Upserts and CDC on object storage |
| Time travel | Query or restore older versions |
| Schema enforcement + evolution | Rejects bad writes; `mergeSchema` adds columns deliberately |
| Unified batch + streaming | A table can be a streaming source and sink |
| Change Data Feed | Row-level change stream for downstream CDC |
| Performance | Data skipping with file statistics, `OPTIMIZE`, Z-order / liquid clustering, deletion vectors |

Its main competitor is **Apache Iceberg** (also Apache Hudi). Delta's UniForm can expose Delta tables to Iceberg readers.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("Delta Lake Operations") and [Training 13 notes](/training-notes-site/notes/training-13/) ("Delta and Iceberg").

**Say it out loud:** "Delta is a table format: Parquet data files plus a transaction log. The log adds what plain Parquet lacks: ACID transactions, MERGE and deletes, time travel, schema enforcement and evolution, and one table for both batch and streaming."

---

**Q. What is DBFS**

**A. (Class answer)** *(no answer given)*

**Expanded:** DBFS (Databricks File System) is a **file system abstraction** in a Databricks workspace that maps paths like `dbfs:/...` onto cloud object storage, so notebooks can use file paths. It includes the **DBFS root** (storage created with the workspace) and **mounts** (pointing at your own S3/ADLS buckets). Status: Databricks now **discourages DBFS root and mounts for data**. The recommended approach is **Unity Catalog volumes** (`/Volumes/catalog/schema/volume/...`) for files and **external locations** for direct cloud paths, which are governed by Unity Catalog permissions.

**Say it out loud:** "DBFS is Databricks' file system layer that maps `dbfs:/` paths onto cloud object storage. Today Databricks recommends Unity Catalog volumes and external locations instead of the DBFS root and mounts, because those are governed."

---

**Q. What is Delta Lake**

**A. (Class answer)** *(no answer given)*

**Expanded:** Delta Lake is the **open-source storage layer / table format** (originally from Databricks, now a Linux Foundation project) that brings **ACID transactions** and table features to data lakes on object storage. Delta tables (Parquet + `_delta_log`) are its unit. It's the foundation of the lakehouse: warehouse-style reliability (transactions, `MERGE`, schema enforcement, time travel) on cheap open storage, readable by many engines. See "What is a delta table" and "Describe the features of Delta Format" above for the features.

How the transaction log makes writes atomic: a writer adds new Parquet files, then commits by atomically creating the next numbered JSON file in `_delta_log`. Readers only see files listed in committed log entries, so a failed write is invisible. Conflicting concurrent commits are detected (optimistic concurrency) and retried or rejected.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("How does Delta Lake give ACID transactions on object storage?").

**Say it out loud:** "Delta Lake is an open-source table format that adds a transaction log on top of Parquet files in object storage, which gives ACID transactions, MERGE, time travel and schema enforcement. It's what turns a data lake into a lakehouse."

---

**Q. What's the medallion architecture**

**A. (Class answer)** *(no answer given)*

**Expanded:** The medallion architecture organizes a lakehouse into **layers of increasing quality**:

| Layer | Contents | Typical work |
|---|---|---|
| **Bronze** | Raw data as ingested, append-only, with ingestion metadata (load time, source file) | Land data, keep full history for replay |
| **Silver** | Cleaned, validated, de-duplicated, conformed data, with types fixed and joins done | Data quality rules, de-duplication, `MERGE`/CDC, SCD |
| **Gold** | Business-level aggregates and dimensional models | Star schemas, KPIs, feature tables for BI and ML |

Benefits: you can **rebuild** downstream layers from Bronze, each layer has a clear purpose and owner, and quality checks sit between layers. It's a design pattern (popularized by Databricks), not a product, and it applies equally to S3 + Glue + Redshift, as in the class's Citi Bike pipeline.

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Medallion Architecture") and [Training 8 notes](/training-notes-site/notes/training-8/) ("The Lesson Plan: Medallion Migration + First Real ETL Pipeline").

**Say it out loud:** "Medallion architecture layers the data: Bronze holds raw ingested data, Silver holds cleaned, de-duplicated and conformed data, and Gold holds business-ready aggregates and star schemas. Since Bronze keeps the raw history, the later layers can always be rebuilt."

---

**Q. What's a data lakehouse**

**A. (Class answer)** *(no answer given)*

**Expanded:** A lakehouse combines a **data lake's cheap, open storage** with a **data warehouse's reliability and performance**. Data lives in object storage in open formats, and an **open table format** (Delta Lake, Iceberg, Hudi) adds ACID transactions, schema enforcement, time travel and fast queries, plus a catalog for governance (Unity Catalog, Glue, Polaris). The same tables then serve BI/SQL, data engineering, streaming and ML, without copying data into a separate warehouse.

| | Data lake | Data warehouse | Lakehouse |
|---|---|---|---|
| Storage | Cheap object storage, open files | Proprietary, managed | Cheap object storage, open table formats |
| ACID / updates | No | Yes | Yes |
| Data types | Any | Structured | Any |
| Workloads | ML, exploration | BI, SQL | Both |

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Data Lakehouse vs Data Warehouse") and [Training 18 notes](/training-notes-site/notes/training-18/) ("S3 in the Lakehouse").

**Say it out loud:** "A lakehouse puts warehouse features, ACID transactions, schema enforcement and fast SQL, directly on cheap open storage using table formats like Delta Lake or Iceberg, so one copy of the data serves both BI and machine learning."

---


## DBT / Snowflake


**Q. What is DBT?**

**A. (Class answer)** *(no answer given)*

**Expanded:** dbt (data build tool, written lowercase) is the **"T" in ELT**: it transforms data **inside the warehouse** using **SQL `SELECT` statements** (models) plus Jinja templating. You write a model per table; dbt compiles it, works out dependencies from `ref()` calls (a DAG), and builds tables or views in order.

| Feature | Meaning |
|---|---|
| Models + `ref()` | SQL files that build on each other; dbt orders them automatically |
| Materializations | `view`, `table`, `incremental`, `ephemeral` |
| Tests | `unique`, `not_null`, `accepted_values`, `relationships`, plus custom tests |
| Sources, seeds, snapshots | Declared raw tables, CSV lookups, SCD Type 2 history |
| Docs + lineage | Generated documentation site with the DAG |

dbt doesn't extract or load data, and it doesn't schedule itself: an orchestrator (Airflow, dbt Cloud jobs) runs it. It brings software practices (Git, tests, CI) to SQL.

See [Training 15 notes](/training-notes-site/notes/training-15/) ("dbt (data build tool)") and [Training 17 notes](/training-notes-site/notes/training-17/) ("Building the models (the actual dbt demo)", "dbt Tests" and "Snowflake Advanced and dbt Essentials (interview core)").

**Say it out loud:** "dbt is the transformation layer of ELT. I write each table as a SQL select, dbt resolves the dependencies through `ref()`, builds them in order in the warehouse, and runs tests like unique and not-null. It brings version control and testing to SQL."

---

**Q. What is Snowflake?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Snowflake is a cloud **data platform / warehouse** offered as SaaS on AWS, Azure and GCP. Its signature design is **separation of storage and compute**, in three layers:

| Layer | Role |
|---|---|
| Storage | Data in compressed columnar **micro-partitions** in cloud object storage |
| Compute | **Virtual warehouses**: independent clusters you size and pause |
| Cloud services | Metadata, optimizer, security, transactions |

Key features: **Time Travel** (query or restore past data, 1 day by default and up to 90 days on Enterprise), **zero-copy cloning**, secure **data sharing**, semi-structured data in `VARIANT` columns, Snowpipe (continuous loading), Streams + Tasks and **Dynamic Tables** for pipelines, Snowpark (Python/Java/Scala in Snowflake). Billing is per credit-second of warehouse time plus storage.

See [Training 16 notes](/training-notes-site/notes/training-16/) ("Snowflake Architecture (interview core)" and "Time Travel"), [Training 15 notes](/training-notes-site/notes/training-15/) and [Training 4 notes](/training-notes-site/notes/training-4/) ("Snowflake (Separated Storage & Compute)").

**Say it out loud:** "Snowflake is a cloud data warehouse that separates storage from compute: data sits in columnar micro-partitions in object storage, and independent virtual warehouses query it, so teams don't compete for resources. It also offers time travel, zero-copy cloning and data sharing."

---

**Q. What's a virtual warehouse in Snowflake**

**A. (Class answer)** *(no answer given)*

**Expanded:** A virtual warehouse is a **cluster of compute** that runs queries and DML. It isn't storage. Key points:
- **Sizes** X-Small to 6X-Large; each step up **doubles** the compute and the credits per hour.
- **Auto-suspend** when idle and **auto-resume** on the next query, billed per second (60-second minimum each time it starts).
- Separate warehouses for separate workloads (ETL, BI, data science) so they don't slow each other down, all reading the same data.
- **Multi-cluster warehouses** (Enterprise edition) add clusters automatically for many concurrent users. Scale **up** (bigger size) for heavy queries, **out** (more clusters) for concurrency.

See [Training 15 notes](/training-notes-site/notes/training-15/) ("Virtual Warehouses: the Main Processing Engine").

**Say it out loud:** "A virtual warehouse is Snowflake's compute: a cluster that runs queries, sized from X-Small up, each size doubling the power and cost. It auto-suspends when idle, and we give each workload its own warehouse so ETL doesn't slow down dashboards. Scale up for heavy queries, out for concurrency."

---


## Apache Airflow


**Q. What is airflow?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Apache Airflow is an open-source **workflow orchestration** platform. Pipelines are written as **Python code (DAGs)**, and Airflow **schedules** them, runs tasks in **dependency order**, **retries** failures, sends alerts and shows history in a web UI. Components: **scheduler** (decides what runs when), **executor** and **workers** (run the tasks: Local, Celery, Kubernetes executors), **web server** (UI), **metadata database** (state of every run), and in Airflow 3 a separate DAG processor and API server. Airflow **orchestrates** work; it isn't meant to process big data itself. Tasks call Spark, Glue, dbt or SQL to do the heavy work. Managed options: MWAA (AWS), Cloud Composer (GCP), Astronomer.

See [Training 26 notes](/training-notes-site/notes/training-26/) ("What is Apache Airflow, and what are its parts?") and [Training 23 notes](/training-notes-site/notes/training-23/) ("Orchestration").

**Say it out loud:** "Airflow is an open-source orchestrator where pipelines are Python DAGs. It schedules them, runs tasks in dependency order, retries failures and shows everything in a UI, while the heavy processing happens in tools like Spark, Glue or dbt that the tasks trigger."

---

**Q. What is a DAG?**

**A. (Class answer)** *(no answer given)*

**Expanded:** In Airflow, a DAG (directed acyclic graph) is a **workflow definition**: a set of **tasks** plus the **dependencies** between them, with no cycles, along with its **schedule**, start date and default settings (retries, owner). Each scheduled run is a **DAG run**, and each task in it is a **task instance**.

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=False)
def citibike_pipeline():
    @task
    def extract(): return "s3://bucket/bronze/2026-01-01/"
    @task
    def transform(path): ...
    transform(extract())          # extract >> transform
citibike_pipeline()
```

See [Training 26 notes](/training-notes-site/notes/training-26/) ("What do a DAG, operators and TaskFlow look like?").

**Say it out loud:** "In Airflow, a DAG is a Python-defined workflow: tasks plus their dependencies with no cycles, and a schedule. Each scheduled execution is a DAG run, and I set dependencies with `>>` or by passing TaskFlow outputs."

---

**Q. How is an Airflow DAG different from a Spark DAG?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Same math concept, very different roles:

| | Airflow DAG | Spark DAG |
|---|---|---|
| Who writes it | You, explicitly, in Python | Spark builds it automatically from your transformations |
| Nodes are | Tasks (run a Glue job, a SQL query, a dbt build) | Operations/RDDs, grouped into stages at shuffles |
| Scope | A whole workflow across many systems | One Spark job's execution plan |
| Purpose | Orchestration: when, in what order, retries | Execution: how to compute the result in parallel |
| Time scale | Runs on a schedule (minutes to hours) | Exists for the duration of one job |

A single Airflow task can submit a Spark job, which then builds its own Spark DAG.

See [Training 17 notes](/training-notes-site/notes/training-17/) (the section on what "DAG" means in dbt vs Spark vs Airflow).

**Say it out loud:** "An Airflow DAG is a workflow I write that orchestrates tasks across systems on a schedule. A Spark DAG is the execution plan Spark builds automatically from my transformations. An Airflow task can launch a Spark job, which then has its own DAG."

---

**Q. What is an operator?**

**A. (Class answer)** *(no answer given)*

**Expanded:** An operator is a **template for one kind of task** in Airflow. You instantiate it with parameters, and each instance becomes a task in a DAG.

| Kind | Examples |
|---|---|
| Action operators | `BashOperator`, `PythonOperator` (or the `@task` decorator), `EmptyOperator` |
| Provider operators | `GlueJobOperator`, `EmrServerlessStartJobOperator`, `S3CopyObjectOperator`, `SQLExecuteQueryOperator`, `SparkSubmitOperator`, `KubernetesPodOperator` |
| **Sensors** (a special operator) | Wait for a condition: `S3KeySensor`, `ExternalTaskSensor`. Use `mode="reschedule"` or deferrable versions so waiting doesn't hold a worker slot |
| Transfer operators | Move data between systems (`S3ToRedshiftOperator`) |

Operators come from **provider packages** (`apache-airflow-providers-amazon`, etc.).

See [Training 26 notes](/training-notes-site/notes/training-26/) ("What do a DAG, operators and TaskFlow look like?" and "What are sensors, XCom and retries?").

**Say it out loud:** "An operator is a reusable template for one type of task, like `PythonOperator`, `BashOperator` or `GlueJobOperator`. Each instance in a DAG is a task, and sensors are special operators that wait for something, like a file landing in S3."

---

**Q. Which operators have you used?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Answer with operators that match your pipeline story and say what each one did. A believable AWS set:
- `PythonOperator` / `@task` for API ingestion into S3.
- `S3KeySensor` to wait for the day's file.
- `GlueJobOperator` (or `EmrServerlessStartJobOperator`) to run the Bronze → Silver Spark job.
- `SQLExecuteQueryOperator` (or `RedshiftDataOperator`) for the Gold-layer SQL.
- `BashOperator` to run `dbt build`.
- An `on_failure_callback` or `SnsPublishOperator` for alerts.

**Say it out loud:** "I've used `PythonOperator` and TaskFlow tasks for API ingestion, `S3KeySensor` to wait for files, `GlueJobOperator` to run the Spark transformations, a SQL operator for the Redshift load, and `BashOperator` to run dbt, with failure callbacks for alerts."

---

**Q. What are XCOMs?**

**A. (Class answer)** *(no answer given)*

**Expanded:** XComs ("cross-communications") let Airflow tasks **pass small pieces of data to each other**. A task pushes a value (any return value of a `PythonOperator` or `@task` is pushed automatically), and a later task pulls it (`ti.xcom_pull(task_ids="extract")`, or simply by passing TaskFlow outputs as arguments). They're stored in the **metadata database**, so they're for **small metadata** (a file path, a row count, a batch ID), not datasets. Pass large data by writing it to S3 and sending the path through XCom (or configure a custom object-storage XCom backend).

See [Training 26 notes](/training-notes-site/notes/training-26/) ("What are sensors, XCom and retries?").

**Say it out loud:** "XComs let Airflow tasks pass small values to each other, like a file path or row count, stored in Airflow's metadata database. For actual data I write to S3 and pass only the path."

---


## Machine Learning


**Q. What is the K Nearest Neighbors Algorithm**

**A. (Class answer)** *(no answer given)*

**Expanded:** KNN is a simple **supervised** machine learning algorithm for **classification and regression**. To predict a new point, it finds the **k closest training points** by a distance measure (Euclidean, Manhattan, cosine) and takes a **majority vote** (classification) or the **average** (regression) of their labels. It's "lazy": there's no training step, just storing the data, so prediction is the expensive part (comparing against all points; approximate nearest neighbor indexes speed this up). Key choices: **k** (small k overfits, large k underfits; pick by cross-validation) and **feature scaling** (normalize features, otherwise large-scale features dominate the distance). Weaknesses: slow on large data and poor in very high dimensions (the curse of dimensionality). Related: **vector search** in RAG systems is nearest-neighbor search over embeddings.

**Say it out loud:** "KNN predicts a new point from the k most similar training points, by majority vote for classification or the average for regression. There's no real training step, but you must scale the features and choose k carefully, and it gets slow on large data. Vector search is the same nearest-neighbor idea."

---

**Q. What is linear regression**

**A. (Class answer)** *(no answer given)*

**Expanded:** Linear regression is a **supervised** algorithm that predicts a **continuous** target as a weighted sum of input features plus an intercept: `y = b0 + b1*x1 + ... + bn*xn`. It fits the weights by minimizing the **sum of squared errors** (ordinary least squares), solved directly or by gradient descent. Evaluate it with **R²**, RMSE or MAE. Assumptions: a linear relationship, independent errors with constant variance (homoscedasticity), little **multicollinearity** between features. Extensions: **Ridge** (L2) and **Lasso** (L1) regularization to reduce overfitting. For classification, **logistic regression** is the counterpart. It's easy to interpret, since each coefficient is the change in y per unit change of that feature with the others held constant.

**Say it out loud:** "Linear regression predicts a continuous value as a weighted sum of the features, fitting the weights by minimizing squared error. It's simple and interpretable, each coefficient shows a feature's effect, and Ridge or Lasso add regularization."

---


## Agile


**Q. What should you say when asked about agile in an interview?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Show that you've **worked in** Agile, not just define it. Agile is an iterative approach: deliver working software in **short iterations**, get feedback, adapt. The most common framework is **Scrum**:

| Element | What it is |
|---|---|
| Sprint | A fixed 1–2 week iteration |
| Ceremonies | Sprint planning, **daily stand-up**, sprint review (demo), **retrospective** |
| Roles | Product Owner (priorities), Scrum Master (process), the development team |
| Artifacts | Product backlog, sprint backlog, user stories with story points, tracked in **Jira** |

**Kanban** is the alternative: continuous flow with WIP limits, common for data teams with lots of ad hoc requests. Good answer structure: the framework, the sprint length, your part in the ceremonies, how data work became stories (for example "as an analyst I need daily station availability in Gold"), and one example of adapting based on feedback.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("Working on a Data Engineering Team").

**Say it out loud:** "We worked in two-week Scrum sprints: planning, daily stand-ups, a demo at sprint review and a retrospective, with stories tracked in Jira. I'd pick up stories like building a new Gold table, demo it to the stakeholders, and adjust based on their feedback the next sprint."

---


## Soft Skills Questions

:::tip[Make these your own]
The sample answers are built on the class Citi Bike project. Use them for structure, then answer with your own projects and words: interviewers notice rehearsed answers, and the follow-up questions go deep into whatever you claim.
:::


**Q. I have one bucket that holds 5 liters, and another bucket that holds 8 liters. How many buckets do I have?**

**A. (Class answer)** *(no answer given)*

**Expanded:** It's a listening test: **two buckets**. The capacities are a distraction, intended to see whether you jump into solving a classic water-jug puzzle instead of answering the question that was asked. Answer simply and confidently. If it seems like they want the puzzle, you can ask whether they'd like you to also solve for measuring a specific amount.

**Say it out loud:** "Two buckets."

---

**Q. What is your favorite computer operating system and why?**

**A. (Class answer)** *(no answer given)*

**Expanded:** There's no wrong choice; they want a reasoned, technical opinion. **Linux** is a strong answer for data engineering: servers, EMR, containers and most cloud services run on it, and the shell, cron, SSH and package managers are daily tools. A good structure: choice → two concrete reasons from your work → a fair note about the alternatives. macOS is also reasonable (Unix-based, good terminal), as is Windows with WSL2.

See [Training 1 notes](/training-notes-site/notes/training-1/) ("Unix & Linux Background").

**Say it out loud:** "Linux, because nearly everything I deploy runs on it: EC2, EMR and Docker containers, and the shell tools like grep, cron and SSH make me fast. Day to day I use a Mac, which gives me a Unix terminal with a desktop."

---

**Q. I have data in a csv file and I want to put it into an excel spreadsheet. How would I do that?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Give the simple answer first, then show you know the gotchas and an automated option:
1. **Simplest:** open the CSV in Excel, or use **Data → From Text/CSV** (Power Query). That lets you set the delimiter, encoding (UTF-8) and column types, then save as `.xlsx`.
2. **Gotchas:** leading zeros dropped from IDs and ZIP codes, long numbers turned into scientific notation, dates misread (set those columns to Text), and Excel's limit of **1,048,576 rows** per sheet.
3. **Automated:**

```python
import pandas as pd
pd.read_csv("data.csv", dtype={"zip": str}).to_excel("data.xlsx", index=False)   # needs openpyxl
```

**Say it out loud:** "For a one-off I'd use Excel's Data, From Text/CSV import so I can set types and keep leading zeros, then save as xlsx. If it's repeated, a two-line pandas script: `read_csv`, then `to_excel`. And I'd check it's under Excel's million-row limit."

---

**Q. What are your career goals?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Show ambition that fits **this** role. A good structure: **short term** (become a strong contributor here: own pipelines end to end, deepen in the company's stack), **medium term** (grow into senior: design architecture, mentor others, own data quality and reliability), and a **genuine interest** (streaming, lakehouse design, data for AI). Tie it to what the company does. Avoid answers that sound like you'll leave soon or that you want a different job (data science, management right away).

**Say it out loud:** "In the next couple of years I want to become someone who can own pipelines end to end here, from ingestion to the warehouse, and get deep in this stack. Longer term I'd like to grow into a senior engineer who designs data platforms and mentors others, especially around streaming and lakehouse architecture."

---

**Q. Name a person who you look up to, and tell me why you look up to them**

**A. (Class answer)** *(no answer given)*

**Expanded:** They're assessing your **values**, so the "why" matters more than the who. Choose someone you can speak about sincerely (a mentor, family member, former manager or a public figure) and name **one or two specific qualities** with an example, such as persistence, curiosity or helping others learn. Connect it lightly to how you work. Avoid divisive political figures. A tech example works well, such as Linus Torvalds (who built Linux and Git) or Grace Hopper (who pioneered compilers and making programming accessible), but only if you can say something real about them.

**Say it out loud:** "I look up to Grace Hopper. She pushed for programming languages that read like English when people said computers could only do arithmetic, and she was famous for teaching. That mix of practical innovation and making things understandable for others is what I aim for."

---

**Q. What is your favorite food, sports team, or tv show, and why?**

**A. (Class answer)** *(no answer given)*

**Expanded:** This is a rapport and communication check. There's no right answer: be **genuine, brief and positive**, give one specific reason, and maybe one sentence that shows some personality. Keep it short (about 20–30 seconds), avoid anything controversial, and it's fine to turn it back to a light question to the interviewer.

**Say it out loud:** "Probably a good bowl of ramen. I like that something that looks simple has so many details behind it, the broth can take a whole day. Kind of like a good data pipeline, actually."

---

**Q. What is the most interesting thing to you about data?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Show genuine curiosity tied to the job. Strong angles: turning messy raw data into something people **trust and use** for decisions; the engineering challenge of **scale** (systems that process millions of events reliably); data as the foundation for **AI**; or how much a small modeling choice (the grain, a slowly changing dimension) changes the answers people get. Give a short example from your own project.

**Say it out loud:** "What interests me most is how raw, messy data becomes something people trust enough to make decisions with. In my Citi Bike project, the raw feed was just JSON snapshots, but after modeling it into a star schema we could answer which stations run empty and when, which is useful for rebalancing bikes."

---


## Project Experience Questions

:::tip[Make these your own]
The sample answers are built on the class Citi Bike project. Use them for structure, then answer with your own projects and words: interviewers notice rehearsed answers, and the follow-up questions go deep into whatever you claim.
:::


**Q. What is the source of the data?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Be specific: **what system**, **what format**, **how you accessed it**, **how much and how often**. Kinds of sources: REST APIs, relational databases (through JDBC or CDC), event streams (Kafka, Kinesis), files (CSV/JSON from partners via S3 or SFTP), SaaS tools (Salesforce), logs. Mention access details that show real experience: authentication, pagination, rate limits, schema changes, late data.

**Say it out loud:** "The source was the Citi Bike GBFS REST API, JSON feeds for station information and station status, refreshed about every minute. We polled it on a schedule and landed the raw JSON in S3."

---

**Q. What is the destination of the data?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Name the final store **and who uses it**: a warehouse (Redshift, Snowflake, BigQuery), lakehouse tables (Delta/Iceberg in S3), an operational database, a search index, or a feature store. Mention the data model (star schema), the consumers (BI dashboards, analysts, ML models, applications) and the freshness they needed (daily, hourly, near-real-time).

**Say it out loud:** "The destination was a star schema in Redshift, the Gold layer, with a station-status fact table and station and date dimensions. Analysts queried it and a Streamlit dashboard read from it, refreshed incrementally on a schedule."

---

**Q. What happens to the data between when you obtain it and when you are finished with it?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Walk through the layers and **name the transformations**: land raw data unchanged (**Bronze**, partitioned by date, kept for replay) → clean and conform (**Silver**: flatten nested JSON, cast types, standardize timestamps and time zones, de-duplicate, validate, handle nulls and bad records, apply CDC with `MERGE`) → model and aggregate for consumers (**Gold**: dimensions with surrogate keys, facts at a defined grain, aggregates). Also mention **data quality checks** between layers, **incremental** processing (only new data), **idempotency** (safe reruns), and orchestration and monitoring around it.

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Medallion Architecture") and [Training 24 notes](/training-notes-site/notes/training-24/) ("Key Concepts").

**Say it out loud:** "Raw JSON lands unchanged in a Bronze layer in S3. A Spark job flattens it, fixes types, de-duplicates and validates it into Silver Parquet. Then SQL builds the Gold star schema incrementally with a MERGE. There are row count and null checks between layers, and every step is idempotent so reruns are safe."

---

**Q. Talk about a problem you had in a previous project**

**A. (Class answer)** *(no answer given)*

**Expanded:** Use **STAR**: **Situation** (context), **Task** (your responsibility), **Action** (what *you* did, step by step: how you diagnosed it and the fix), **Result** (measurable outcome and what you learned). Pick a real technical problem with a clear diagnosis: data skew, small files, a schema change that broke a job, an IAM or networking error, duplicates from retries, a slow query. Spend most of the time on the **Action**.

See [Training 22 notes](/training-notes-site/notes/training-22/) ("Debugging the Glue streaming job: four errors") and [Training 21 notes](/training-notes-site/notes/training-21/) ("Why Glue and Redshift share a VPC").

**Say it out loud:** "Our Glue job writing to Redshift kept timing out. I checked the logs and saw it was a networking issue, not the code: Glue couldn't reach Redshift or S3 from its subnet. I put the Glue connection in the same VPC as Redshift and added an S3 gateway endpoint, then fixed the IAM permissions that showed up next, and after that the load ran reliably. I learned to check networking and permissions first with managed services."

---

**Q. Tell me about a disagreement that you have had with a colleague and how you resolved it**

**A. (Class answer)** *(no answer given)*

**Expanded:** They want to see **respect, listening, data-driven decisions and a good outcome**. Use STAR. Pick a **technical** disagreement (a tool choice, a design, a code review comment), not a personal conflict. Show that you understood their view, tested the options with **evidence** (a benchmark, a prototype, cost numbers), reached a decision together (or escalated properly), and kept a good working relationship. Never blame or make the other person look bad. Being open to being wrong is a plus.

**Say it out loud:** "A teammate wanted to orchestrate our pipeline with cron scripts on an EC2 instance, and I preferred Step Functions. Rather than argue, we listed what we needed: retries, alerts and visibility, and I built a small prototype. Seeing failed steps and retries in the console convinced us both, and we agreed to keep his simpler approach for one ad hoc job. We kept working well together."

---

**Q. How did you communicate with stakeholders?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Show a **regular rhythm** and **adapting to the audience**: requirement sessions at the start (what decisions the data supports, freshness and definitions), sprint demos, status updates in stand-ups or Slack/Teams, Jira tickets, and documentation (data dictionaries, dbt docs). Key skills to mention: translating technical issues into **business impact** ("the dashboard will be 2 hours late this morning" rather than "the Glue job hit a connection timeout"), agreeing on **metric definitions**, raising risks early, and confirming understanding in writing.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("Who do data engineers work with day to day?" and "What is a stakeholder?").

**Say it out loud:** "We met at the start to agree on the questions, the metric definitions and the freshness they needed, then I demoed progress every sprint and gave updates in Teams. When something broke, I explained it in terms of impact, what's late and when it'll be fixed, rather than technical details."

---

**Q. Who were the stakeholders in your last project?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A stakeholder is anyone **affected by or with an interest in** the project's outcome. Name them by **role and what they needed**: business users and analysts (dashboards, trustworthy metrics), data scientists (clean features), product owner or manager (priorities, timelines), source system owners (access, change notices), platform, DevOps and security (infrastructure, IAM, compliance), and leadership (cost and value).

See [Training 29 notes](/training-notes-site/notes/training-29/) ("What is a stakeholder?").

**Say it out loud:** "The main stakeholders were the operations analysts who used the dashboard to plan bike rebalancing, the product owner who set priorities, the cloud and security team who managed our AWS access, and the data scientists who used the Silver data for forecasting."

---

**Q. Describe the architecture of your previous project**

**A. (Class answer)** *(no answer given)*

**Expanded:** Describe it as a **diagram in words**, layer by layer, naming the **why** behind each choice: sources → ingestion (batch or streaming) → storage layers (Bronze/Silver/Gold) → processing engines → warehouse or serving → orchestration → infrastructure as code and CI/CD → security (IAM, VPC, secrets) → monitoring. Mention the scale (data volume, frequency), one key design decision and its trade-off (for example Glue vs EMR, or batch vs streaming), and one thing you'd improve.

See [Training 24 notes](/training-notes-site/notes/training-24/) ("The final architecture" and "Design details worth knowing").

**Say it out loud:** "It was a batch lakehouse on AWS: Python ingestion from an API into S3 Bronze, Glue Spark jobs to Silver Parquet, and a Redshift Serverless Gold star schema loaded incrementally, all orchestrated by Step Functions on an EventBridge schedule and deployed with Terraform. We chose Glue over EMR because the volume was modest and we didn't want to manage clusters. Next I'd add data quality tests between layers."

---

**Q. What's the most interesting project you've worked on?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Pick the project you can discuss most deeply and are **genuinely enthusiastic** about. Explain the **problem and why it mattered**, your **specific role**, the **interesting technical challenge** (streaming, scale, a tricky modeling or performance issue, AI on top of data), and the **result**. Enthusiasm and clear ownership matter more than size.

See [Training 25 notes](/training-notes-site/notes/training-25/) ("The Text-to-SQL Chatbot (main demo)") and [Training 14 notes](/training-notes-site/notes/training-14/) ("Market Data Lab: Spark vs. Flink on One Dashboard").

**Say it out loud:** "The most interesting was adding a text-to-SQL chatbot on top of our Redshift star schema with Amazon Bedrock. Users could ask questions in plain English, and the hard part was getting the model to generate correct SQL for our schema, which meant giving it the table definitions and validating the queries. It made the data usable by people who don't write SQL."

---

**Q. (For any project that involves streaming data) - how many messages per second were you processing?**

**A. (Class answer)**

A normal number for messages streamed per second in Kafka is between 1,000 and 2,000.

**Expanded:** Treat the teacher's figure as a **rule of thumb for a believable answer**, not a real norm. Real systems range from a few messages per second to **millions** per second (large Kafka deployments at big tech companies). What matters is that your number is **consistent with the rest of your story**: the partition count, the consumer setup, the message size, daily volume and the cost. Check the arithmetic: 1,500 messages/second × 1 KB ≈ 1.5 MB/s, about 130 GB/day, and about 130 million messages/day. Be ready for follow-ups: peak vs average, how many partitions or shards, consumer lag, latency, and how you'd scale if traffic grew 10x.

See [Training 14 notes](/training-notes-site/notes/training-14/) ("Market Data Demo: Measuring Micro-Batch Latency") and [Training 22 notes](/training-notes-site/notes/training-22/) ("MSK vs Kinesis").

**Say it out loud:** "On average around 1,500 messages a second, peaking at about 5,000, each under 1 KB. We had a topic with 12 partitions and a Spark Structured Streaming job with 30-second micro-batches, and kept consumer lag under a minute. To scale further we'd add partitions and executors."

