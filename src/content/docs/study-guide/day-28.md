---
title: Study Guide - Day 28
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 28: ADF and Databricks Medallion"
sidebar:
  order: 280
---

Study Guide - Day 28 (source: notes/Training 28.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**The Azure Pipeline.** The core of most Azure pipelines is **ADLS Gen2 + Azure Data Factory + Databricks** (Synapse later). Today's version is multi-cloud: Citi Bike Bronze JSON in **S3** → ADF **Copy activity** → ADLS Gen2 `bronze` container → Unity Catalog **external volume** → Databricks notebook → Bronze, Silver and Gold **Delta tables**. The AWS mapping: S3 → ADLS, Lambda/Step Functions → ADF, Glue/EMR → Databricks, Parquet → Delta, IAM → Entra ID + RBAC + managed identities.

**Final-Project Data.** Use real data, and go bigger: 40 KB is for learning, hundreds of MB is a start, **5-10 GB** is ideal for a live demo, production is hundreds of GB to TB. Kaggle and NYC taxi data were suggested. AWS, Azure or multi-cloud are all fine. Watch for the **small-files problem**: repartition to fewer, larger files (about 128 MB to 1 GB each).

**ADF Building Blocks.** **Pipeline** (group of activities), **activity** (one step: data movement like Copy, transformation like Data Flow or a Databricks Notebook, control flow like ForEach), **linked service** (the connection and authentication to a system), **dataset** (a pointer to specific data inside a linked service), **integration runtime** (the compute that moves the bytes: Azure IR, self-hosted IR, Azure-SSIS IR), **trigger** (schedule, tumbling window, storage event, manual). The **Copy activity** copies source → **sink**, optionally converting format, with no real transformation. Large database moves use **DMS** (Database Migration Service); bulk files use AzCopy or Data Box.

**Connecting ADF.** **S3 linked service**: a dedicated read-only IAM user with an inline policy (`ListBucket` and `GetBucketLocation` on the bucket ARN, `GetObject` on `bucket/*`). A key posted in chat is still a live credential: prefer Key Vault and rotate. **ADLS linked service**: the factory's **system-assigned managed identity** plus a **Storage Blob Data Contributor** role on the storage account. It failed with a 403 until the role assignment **propagated** (minutes). **Control plane** roles (Contributor) manage the account; **data plane** roles (Storage Blob Data ...) read and write the files.

**The Copy Pipeline.** `pl_copy_citibike_s3_to_adls` with a Copy data activity, **Binary** datasets (copy bytes as-is), Recursively, **Preserve hierarchy**. Validate → Debug → **Publish all**. Errors: unpublished linked service, `citibike` in the file-name field instead of the directory field, the storage account typed as a folder (sink = container only), the portal browsing as your own user (you need a data role too), and student bucket ARNs missing from the policy. Once set up, it's re-runnable and schedulable. ADF storage event triggers watch Azure storage only, not S3.

**Databricks + Unity Catalog.** Create a workspace (Premium tier for UC); new workspaces are **automatically UC-enabled**. Connecting to ADLS takes four steps: **Access Connector** (owns a managed identity) → Storage Blob Data Contributor on the storage account → UC **storage credential** → **external location** (`abfss://` path + credential) → **external volume** read at `/Volumes/<catalog>/<schema>/<volume>/`. A managed volume keeps files in UC's own storage. Users exist at the **account** level and must also be added to each **workspace**.

**Notebooks and Reading.** Cells in Python, SQL, Scala, R or Markdown; switch with magic commands (`%sql`, `%md`). `spark` and `dbutils` are predefined. Run cells in order (a skipped cell gave a `NameError`). Read with `/Volumes/...` or `abfss://` paths, not `https://`. Use `multiLine` for multi-line JSON documents and `recursiveFileLookup` for nested folders. Schemas per layer: `<catalog>.bronze`, `.silver`, `.gold`.

**Bronze.** `F.explode("data.stations")` turns one row with an array into one row per station; `select("station.*")` turns struct fields into columns. Add `snapshot_epoch`, `_metadata.file_path` and `ingested_at`. Write `format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(...)`: 3,098,269 rows. Without `overwriteSchema`, Delta's **schema enforcement** rejects a changed schema.

**Silver.** Cast types (with `.alias` to restore names), `from_unixtime` + `to_timestamp` for the snapshot time, filter null station IDs and negative counts, `dropDuplicates(["station_id", "snapshot_epoch"])`. About 7,500 rows removed. **Long** is a 64-bit integer, not a string. Keep station IDs as **strings** (UUID and legacy formats). `DESCRIBE HISTORY` shows version 0 as **CREATE OR REPLACE TABLE AS SELECT**, the same logic a dbt table model runs. Every write adds a version (time travel).

**Gold.** Aggregates for analytics: one row per hour for the whole network. A window `partitionBy("station_id", "hour").orderBy(snapshot_time desc)` with `row_number() = 1` keeps **one snapshot per station per hour**, so totals aren't counted several times. Then `groupBy("hour")` with stations reporting, total bikes, total docks and average bikes per station. Lowest-bike hours were around 9-10 PM, but check `stations_reporting` before concluding. Bikes and docks mirror each other because a ride takes a bike out and frees a dock.

**Interviews.** ADF and Databricks are central to many interviews. Databricks is the same across clouds: notebook and Spark code don't change, only the cloud authorization setup. Spark is the open-source engine; Databricks is the managed platform around it (notebooks, serverless, Delta, UC, Jobs/Lakeflow, SQL warehouses, MLflow, Photon).

---

# Part 2: Cheat Sheet

## ADF
- Pipeline · activity · linked service (connection) · dataset (pointer) · IR (compute) · trigger
- Activities: movement (Copy) · transformation (Data Flow, Notebook, Stored Procedure) · control (ForEach, If, Wait)
- IRs: Azure (default AutoResolve) · self-hosted (on-prem) · Azure-SSIS
- Studio tabs: Home · Author · Monitor · Manage · Validate → Debug → Publish all
- Binary dataset = copy bytes · Preserve hierarchy · directory field vs file-name field
- DMS = whole databases · AzCopy / Data Box = bulk files · ADF = pipelines and moderate copies

## Permissions
- S3 policy: bucket ARN for ListBucket/GetBucketLocation · `bucket/*` for GetObject
- Managed identity + Storage Blob Data Contributor · RBAC propagation takes minutes
- Control plane (Contributor/Owner) vs data plane (Storage Blob Data Reader/Contributor/Owner)
- `az role assignment create --assignee-object-id ... --role ... --scope <storage-account-id>`

## Databricks + UC
- Access Connector → role on storage → storage credential → external location → external volume
- `/Volumes/<catalog>/<schema>/<volume>/` · `abfss://` ok · `https://` no
- `catalog.schema.table` · account vs workspace users · magic commands `%sql %python %md`

## Medallion Code
- Bronze: `explode("data.stations")` · `select("station.*")` · `_metadata.file_path` · `current_timestamp()`
- Write: `format("delta").mode("overwrite").option("overwriteSchema","true").saveAsTable()`
- Silver: `cast` + `alias` · `from_unixtime` / `to_timestamp` · filters · `dropDuplicates([...])`
- Gold: `date_trunc("hour")` · window + `row_number() = 1` · `groupBy("hour").agg(...)`
- Validate: `UNION ALL` row counts · `DESCRIBE HISTORY` · `DESCRIBE DETAIL`

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is a Copy activity in Azure Data Factory?
A: The most basic ADF activity. It copies data from a source dataset to a sink dataset, and can convert formats, but it doesn't do real transformations.

Q: What's the difference between a linked service and a dataset?
A: A linked service is the connection and authentication to a system, like a database connection. A dataset points to specific data inside it, like a folder, file and format, similar to a table name over that connection.

Q: What is an integration runtime?
A: The compute that runs ADF activities and actually moves the data. The Azure IR is managed in the cloud, a self-hosted IR reaches on-prem or private networks, and the Azure-SSIS IR runs SSIS packages.

Q: What are the three kinds of ADF activities?
A: Data movement, like Copy; data transformation, like Data Flow, a Databricks notebook or a stored procedure; and control flow, like ForEach, If Condition and Wait.

Q: When would you use DMS instead of ADF?
A: For migrating whole databases with little or no transformation, including ongoing change replication. ADF is for pipelines and moderate copies, and AzCopy or Data Box are for bulk files.

Q: Why use a managed identity for ADF to reach ADLS?
A: Azure manages the identity's credentials, so no keys or passwords are stored anywhere. You just grant it an RBAC role like Storage Blob Data Contributor on the storage account.

Q: Why did the ADLS connection still fail right after granting the role?
A: Azure role assignments take a few minutes to propagate. After waiting, with no other change, the test passed.

Q: What's the difference between the control plane and the data plane?
A: The control plane is managing the resource itself, like creating or configuring a storage account, with roles like Contributor. The data plane is reading and writing the files inside, which needs a Storage Blob Data role.

Q: What's the most common S3 policy mistake?
A: Putting object actions on the bucket ARN. ListBucket and GetBucketLocation go on the bucket ARN, but GetObject needs the bucket ARN with slash star for the objects.

Q: Why use a Binary dataset for the raw copy?
A: Binary copies the bytes as-is without parsing them. That's the right choice for a raw Bronze copy and the fastest option.

Q: Why go through all the ADF setup just to copy files?
A: Once it's set up, the pipeline is re-runnable and schedulable with a trigger, and it's often how the company wants it done.

Q: How does Databricks read ADLS under Unity Catalog?
A: An Access Connector owns a managed identity, which gets a Storage Blob Data role on the storage account. A storage credential records it, an external location pairs it with an abfss path, and an external volume or tables sit on that location.

Q: What's the difference between an external and a managed volume?
A: An external volume governs files that stay in your own ADLS path. A managed volume keeps the files in Unity Catalog's managed storage, so there's no storage permission setup.

Q: What does explode do?
A: It turns each element of an array column into its own row. Then select with struct dot star turns the struct's fields into top-level columns.

Q: Why use multiLine when reading the Citi Bike JSON?
A: Each file is one JSON document spread over many lines, not one JSON object per line, which is what Spark expects by default.

Q: What does overwriteSchema do?
A: It allows a write to change the table's columns or types. Without it, Delta's schema enforcement rejects a write that doesn't match the existing schema.

Q: What is a long in Spark?
A: A 64-bit integer, BIGINT. It's not a string. It's the safe type for epoch timestamps.

Q: Which duplicate does dropDuplicates keep?
A: It keeps one row per unique combination of the listed columns, but which one survives isn't guaranteed. If it matters, use a window with row_number.

Q: How do you keep the latest row per key?
A: Use row_number over a window partitioned by the key and ordered by timestamp descending, then keep rows where it equals one.

Q: Why did Gold keep only one snapshot per station per hour?
A: A station can report several times in an hour. Summing all of them would count the same bikes several times, so one snapshot per station per hour gives a true point-in-time total.

Q: What goes in Bronze, Silver and Gold?
A: Bronze is raw data plus load metadata, Silver is cleaned, typed and deduplicated data, and Gold is business-level aggregates for analytics.

Q: Why does DESCRIBE HISTORY say CREATE OR REPLACE TABLE AS SELECT?
A: An overwrite saveAsTable is logically the same as a CTAS replace. It's the same logic a SQL ELT tool like dbt runs, and every write adds a version for time travel.

Q: What does Delta add over plain Parquet?
A: ACID transactions, schema enforcement, a transaction log with version history for time travel, and MERGE, UPDATE and DELETE.

Q: Is Azure Databricks different from Databricks on AWS?
A: The notebook and Spark code are the same. Only the cloud integration and authorization setup differ.

Q: What's the difference between Spark and Databricks?
A: Spark is the open-source distributed processing engine. Databricks is a managed platform built around it by Spark's creators, adding notebooks, serverless compute, Delta Lake, Unity Catalog, jobs and Photon.

Q: How big should a final-project dataset be?
A: Real data, ideally a few gigabytes. Around 5 GB is good for a live demo: big enough to make you think about size, small enough to run in minutes.
