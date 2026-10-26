---
title: "Training 28 Homework"
description: "Homework assignment for Training 28: ADF and Databricks Medallion."
sidebar:
  order: 28
---

:::note
The assignment prompt as given in class. Related notes: [Training 28](/training-notes-site/notes/training-28/).
:::

## Homework - Training 28 (Assignment)

Homework Assignment: Azure Data Factory & Databricks — Citi Bike Pipeline
Topic: Data Ingestion, Medallion Architecture, PySpark, and Delta Lake
Estimated time: 2–3 hours, including reading and hands-on work
Priority: Completing the working pipeline is more important than extensive theoretical reading.

### Objective
Today, we demonstrated how to migrate data from AWS S3 into Azure Data Lake Storage Gen2 (ADLS Gen2) using Azure Data Factory, then process that data in Azure Databricks using PySpark and Delta Lake.
Your homework is to reproduce the basic pipeline in your own Azure environment and become familiar with the concepts behind the services.
By the end, you should have a working Bronze → Silver → Gold pipeline, with data stored in Delta tables and at least one analytical query against the Gold layer.

### Part 1 — Theory and Reading (Approximately 30–45 minutes)
Focus on understanding what each service does, why we use it, and how the services fit together. You do not need to memorize every configuration option.

#### A. Azure Data Factory (10–15 minutes)
Read: Microsoft Learn — Introduction to Azure Data Factory
- Pipelines: How ADF organizes and orchestrates data workflows.
- Activities: What a Copy Activity does and how it differs from a transformation.
- Linked Services: How ADF connects to external systems such as AWS S3 and ADLS Gen2.
- Datasets: How datasets identify the files and data structures used by activities.
- Integration Runtime: What executes ADF activities and transfers data.
- Managed Identities and RBAC: How ADF authenticates to Azure Storage without storing account keys.

Think about why we used ADF to transfer data from AWS S3 to Azure rather than writing a custom Python transfer script.

#### B. Azure Databricks and Apache Spark (10–15 minutes)
Read: Microsoft Learn — What is Azure Databricks?
- What Databricks provides on top of Apache Spark.
- The difference between Spark DataFrames and ordinary Pandas DataFrames.
- What Spark drivers, executors, and clusters do.
- Why Spark uses lazy evaluation.
- What a Databricks notebook is and how it runs PySpark code.
- How Databricks reads data directly from ADLS Gen2.

You should understand why Spark is useful for distributed data processing, even though our Citi Bike dataset is relatively small.

#### C. Delta Lake, Medallion Architecture, and Unity Catalog (10–15 minutes)
Read: Microsoft Learn — Medallion Architecture; What is Delta Lake?; What is Unity Catalog?
- Bronze: Raw or minimally processed data.
- Silver: Cleaned, validated, and deduplicated data.
- Gold: Business-oriented aggregations and analytical tables.
- Delta Lake: How Delta adds ACID transactions, schema enforcement, and table history to data lakes.
- Unity Catalog: How Databricks manages access to catalogs, schemas, tables, and external storage.
- External volumes: How Unity Catalog can provide access to files physically stored in ADLS Gen2.

You do not need to study advanced Delta optimization or Unity Catalog administration yet.

### Part 2 — Hands-On Pipeline (Approximately 90–120 minutes)

#### Step 1 — AWS S3 to Azure ADLS Gen2
Using Azure Data Factory:
- Verify that your Citi Bike source data exists in your AWS S3 bucket.
- Create or verify an ADF linked service for AWS S3.
- Create or verify an ADF linked service for ADLS Gen2.
- Configure source and destination datasets.
- Create a pipeline containing a Copy Activity.
- Copy your Citi Bike JSON data from S3 into your ADLS Gen2 container.
- Verify that the activity succeeds and the files appear in Azure Storage.
- Preserve the source directory structure where practical.

Expected result: Citi Bike JSON files are accessible in your ADLS Gen2 storage account.
If you already completed this successfully during class, you do not need to rebuild it.

#### Step 2 — Connect Databricks to ADLS Gen2
- Verify that Unity Catalog is available.
- Configure or verify the Azure Databricks Access Connector.
- Ensure its managed identity has the necessary storage permissions.
- Create a Unity Catalog storage credential.
- Create an external location pointing to your ADLS Gen2 container.
- Create an external volume for accessing the source files.
- Use a Databricks notebook to list and read the JSON files.

```python
landing_path = (
    "/Volumes/<catalog>/<schema>/<volume>/"
)
display(dbutils.fs.ls(landing_path))
```

```python
df = (
    spark.read
    .option("multiLine", "true")
    .option("recursiveFileLookup", "true")
    .json("<your-source-path>")
)
df.printSchema()
display(df.limit(10))
```

Replace the placeholders with your own catalog, schema, volume, and source path.

#### Step 3 — Create a Bronze Delta table
Use PySpark to read the source JSON files and write their contents to a Bronze Delta table.
For station-status data, flatten the nested station array into individual records.
Include useful metadata such as the source filename and ingestion timestamp.

```python
bronze_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(
        "<catalog>.bronze.station_status"
    )
```

You may use the code demonstrated in class, adapting it to your own data.
Expected result: A Bronze Delta table visible in Databricks Catalog Explorer.

#### Step 4 — Transform Bronze into Silver
- Casting important columns to appropriate data types.
- Removing records with missing station IDs.
- Filtering invalid values, such as negative bicycle counts.
- Deduplicating station observations using an appropriate station ID and timestamp combination.
- Converting timestamps into useful Spark timestamp columns.

Write the result as a Delta table.
Expected result: A cleaned Silver table containing valid station observations.

#### Step 5 — Aggregate Silver into Gold
Create at least one Gold Delta table using the Silver data (e.g. hourly bicycle availability across the network). Metrics:
- Hour of observation.
- Number of stations reporting.
- Total available bicycles.
- Total available docks.
- Average available bicycles per station.

If multiple snapshots exist for the same station during an hour, use the latest observation for that station in that hour before calculating network totals.
Expected result: A Gold Delta table containing hourly station availability metrics.

#### Step 6 — Perform an analytical query

```sql
SELECT *
FROM <catalog>.gold.hourly_network_availability
ORDER BY total_bikes_available ASC
LIMIT 5;
```

This identifies the hours with the lowest recorded bicycle availability, although the number of reporting stations should also be considered when interpreting the results.
Optionally, create a simple Databricks visualization showing bicycle availability over time.

### Part 3 — Short Written Questions (2–4 sentences each)
1. What is the difference between an ADF Linked Service and an ADF Dataset?
2. What is the purpose of an Integration Runtime?
3. Why did we use a managed identity to access ADLS Gen2?
4. What is the difference between Bronze, Silver, and Gold data?
5. What advantages does Delta Lake provide compared with ordinary JSON or Parquet files?
6. What is the role of Unity Catalog, and how does an external volume relate to ADLS Gen2?

### Part 4 — Submission Requirements
1. **Pipeline evidence** — screenshots: a successful ADF Copy Activity; Bronze, Silver, and Gold tables in Catalog Explorer; output of at least one SQL query against Gold.
2. **Notebook** — the Bronze → Silver → Gold notebook (export or accessible workspace link).
3. **Written answers** — the six theory questions.
4. **Status** — fully operational, partially complete, or blocked, plus unresolved issues.

### Important: Access and Permissions Problems
Several students encountered Azure RBAC, Databricks workspace permissions, managed identity, and AWS S3 access issues during class.
If you encounter an access or permissions problem, reach out to me rather than spending hours troubleshooting it independently.
Send me the exact error message, the resource name involved, and the step you were attempting.
You are not expected to solve administrator-level permission problems on your own. Continue with whichever portions of the assignment you can complete while access is being resolved.

### Optional Challenges (Only if You Finish Early)
- Use Delta Lake DESCRIBE HISTORY to inspect your table's transaction history.
- Demonstrate Delta Lake time travel after updating a table.
- Create a line chart showing hourly bicycle availability.
- Research how Delta MERGE can maintain a table containing only the latest status of each station.
- Consider how you would replace the full batch overwrite with incremental processing using Databricks Auto Loader.

### Final Expectations
AWS S3 → Azure Data Factory → ADLS Gen2 → Databricks Bronze → Silver → Gold → SQL Analytics

Focus on getting the basic architecture working, understanding what each component does, and being able to explain the transformations you performed. We will build on this foundation in the next class with more advanced Databricks and Azure features.
