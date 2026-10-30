---
title: Day 32 Vocabulary
description: Glossary of terms and definitions from the Training 32 notes.
sidebar:
  order: 32
---

Vocabulary — Study Guide Day 32

Source: notes/Training 32.md

## Class Admin and Final Project
- **Looker** — Google's BI and dashboard tool with a LookML modelling layer; comes up in interviews more than Streamlit.
- **Power BI** — Microsoft's BI and dashboard tool, built into Fabric.
- **Streamlit** — A free, open-source Python framework for quick data apps and dashboards.
- **Cost alert** — A cloud billing setting that notifies you when spend reaches a threshold.
- **Scheduling / automation** — Running a pipeline automatically on a timer or trigger; nice to have in the final project, but not required.
- **Multi-cloud** — A pipeline that uses services from more than one cloud provider.
- **Terraform** — An infrastructure-as-code tool that defines cloud resources in config files and applies them.

## Microsoft Fabric
- **Microsoft Fabric** — Microsoft's all-in-one SaaS analytics platform bundling Data Factory, Spark, warehousing, real-time analytics and Power BI on OneLake.
- **SaaS (Software as a Service)** — Software delivered as a managed online service rather than infrastructure you run yourself.
- **Talend / Pentaho / Informatica** — Commercial data-integration platforms that Fabric competes with.
- **Fabric capacity** — The paid compute pool (F SKU) that all Fabric workloads run on; about $8,400/month for the size shown.
- **Capacity overage protection** — A Fabric capacity option that covers usage spikes; not needed for demos.
- **Free trial capacity** — A temporary Fabric capacity that Fabric can start automatically when you first create an item.
- **Tenant** — An organization's Microsoft Entra ID directory; admins and resources across tenants can block capacity creation.
- **Workspace (Fabric)** — A container for Fabric items such as lakehouses, notebooks, pipelines and reports.
- **Item (Fabric)** — Any object created in a workspace, such as a lakehouse, notebook, copy job, semantic model or report.

## OneLake and Storage
- **Azure Blob Storage** — Azure's flat object storage, the foundation layer.
- **ADLS Gen2 (Azure Data Lake Storage Gen2)** — Blob Storage plus a hierarchical namespace.
- **Hierarchical namespace** — Real directories and files, as on a local file system, enabling atomic renames and folder ACLs.
- **Flat namespace** — Storage where "folders" are only key prefixes, as in S3.
- **OneLake** — Fabric's tenant-wide logical data lake on ADLS Gen2, adding a unified namespace, catalog and governance.
- **Unified namespace** — Working with data from many buckets or workspaces as one environment.
- **Unified data platform** — A platform, like Snowflake or Fabric, combining storage, compute, governance and analytics in one product.
- **Lakehouse (Fabric)** — A Fabric item with a Tables area (Delta) and a Files area (raw files) plus a SQL endpoint.
- **Tables area** — The part of a lakehouse holding managed Delta tables.
- **Files area** — The part of a lakehouse holding raw files of any format.
- **Delta table** — A table stored as Parquet files plus a transaction log, the default format in Fabric.
- **Cosmos DB** — Azure's proprietary NoSQL database service.

## Fabric UI Areas
- **OneLake catalog** — The Fabric area for browsing and managing all data items in the tenant.
- **Govern tab** — The catalog view with insights and recommended actions across domains, workspaces and items.
- **Domain / subdomain** — Groupings of workspaces by business area, used for governance.
- **Secure tab** — The catalog view of access and admin rights.
- **Monitor** — Fabric's job runs view, filtered by time and item type.
- **Real-Time hub** — The Fabric area for streaming sources, event subscriptions and alerts.
- **Fabric events** — Events generated inside Fabric, such as job, OneLake, workspace item and capacity events.
- **Business events** — Any events in your Fabric environment that you can access and subscribe to.
- **Alerts (Real-Time hub)** — Rules that notify you when certain events occur.
- **Schema registry** — A store of versioned message schemas so consumers can apply the right schema to each message.
- **Schema evolution** — Handling changes to a data schema over time without breaking the pipeline.
- **Event schema set** — Fabric's registry entry grouping schemas for event data.
- **Workloads** — Packaged Fabric experiences and tutorials, such as data engineering.
- **Deployment pipelines** — Fabric's CI/CD feature for promoting items from dev to test to prod.
- **CI/CD** — Continuous integration and continuous delivery: automated testing and deployment of changes.
- **Fabric functions** — Serverless code in Fabric, ported from Azure Functions and similar to AWS Lambda.
- **Copilot** — Microsoft's AI assistant in Power BI and Fabric; needs a paid tier.

## Hospital Scenario and Azure SQL
- **Synthetic data** — Generated fake data used because real medical records are not public.
- **Azure SQL Database** — Azure's managed SQL Server database service.
- **SQL logical server** — The Azure container that holds Azure SQL databases, logins and firewall rules.
- **Query editor (preview)** — The Azure portal's built-in SQL editor for Azure SQL databases.
- **MS SQL extension** — The VS Code extension for connecting to and querying SQL Server and Azure SQL.
- **Command palette** — VS Code's Ctrl/Cmd+Shift+P command search, used to run "MS SQL: Execute Query".
- **SQL authentication** — Logging into a SQL database with a SQL username and password.
- **SQL dialect** — A vendor's variant of SQL, such as T-SQL, Oracle SQL or PostgreSQL.
- **T-SQL** — Microsoft's SQL dialect used by SQL Server, Azure SQL, Synapse and Fabric.
- **SELECT TOP n** — T-SQL syntax for returning the first n rows, equivalent to `LIMIT n`.
- **LIMIT** — The row-limit clause used by Postgres, MySQL, Spark SQL, DuckDB and others.
- **FETCH FIRST n ROWS ONLY** — The ANSI and Oracle row-limit syntax.
- **Conditional count** — `SUM(CASE WHEN condition THEN 1 ELSE 0 END)` to count matching rows alongside a total.
- **Federated query** — Querying several sources in place without copying the data first.

## Ingestion
- **Azure Data Factory (ADF)** — Azure's data integration and orchestration service.
- **Copy activity** — An ADF step that copies data from a source dataset to a sink dataset.
- **Source / sink dataset** — The ADF definitions of where data is read from and written to.
- **Linked service** — The ADF connection definition holding a source's endpoint and credentials.
- **Trigger now** — Running an ADF pipeline once on demand.
- **Throughput** — The rate of data copied per second, shown in run details.
- **Copy job (Fabric)** — A Fabric item that copies data from one source to a destination.
- **Full copy** — Copying all source data each run, as opposed to incremental copy.
- **Column mapping** — Matching source columns and types to destination columns and types.
- **SAS token** — A Shared Access Signature granting time-limited access to Azure Storage.
- **Service principal** — An application identity in Entra ID (tenant ID + client ID + secret) used for automated authentication.
- **Access key / secret key (AWS)** — IAM credentials used by the S3 connector.
- **S3 URI vs HTTPS URL** — `s3://bucket/key` versus `https://bucket.s3.region.amazonaws.com`; Fabric's S3 connector wanted the HTTPS form.

## Notebook Transformations
- **Fabric notebook** — A Spark notebook in Fabric with `spark` predefined, similar to Databricks.
- **Attach lakehouse** — Adding a lakehouse to a notebook's Explorer so its tables can be read by name.
- **saveAsTable** — A Spark method that writes a DataFrame as a managed table.
- **dropDuplicates** — A Spark method that removes duplicate rows by key columns.
- **Validity check** — A filter that drops impossible records, such as discharge before admission.
- **source_hospital column** — A lineage column recording which source each row came from.
- **Window function** — A calculation over a group of related rows defined by partition and order.
- **partitionBy / orderBy (Window)** — Define which rows form each window and their order.
- **lag** — A window function that returns a value from the previous row in the window.
- **datediff** — A function returning the number of days between two dates.
- **30-day readmission** — A patient re-admitted within 30 days of a previous discharge, a standard hospital quality metric.
- **Length of stay** — Days between admission and discharge.
- **Enriched DataFrame** — Silver data with added calculated columns, used to build gold.
- **Grain** — What one row of a table represents, such as per hospital, per diagnosis or per month.

## Power BI in Fabric
- **Semantic model** — Power BI's data model of tables, relationships and measures that reports use.
- **Report** — A canvas of visuals built on a semantic model.
- **Direct Lake** — Power BI mode that reads OneLake Delta files directly; the default for lakehouse models.
- **Visualizations pane** — Where you pick a visual type and fill its axis wells.
- **Data pane** — Where you tick or drag fields into a visual.
- **Clustered bar chart** — Horizontal bars comparing categories.
- **Line chart** — A visual showing a value's trend over time.
- **Tooltip field** — An extra value shown when hovering over a visual.
- **Data labels** — Values printed on the bars or points of a visual.
- **ICD-10 J18.9** — The diagnosis code for pneumonia, unspecified; the most common code in the demo data.

## Interview and Narratives
- **Profile narrative** — A STAR-style project story tied to a role in your profile.
- **Kinesis Data Streams** — The AWS streaming service, suited to device telemetry.
- **Spark Structured Streaming** — Spark's streaming API for processing data continuously.
- **EMR** — AWS's managed Spark and Hadoop cluster service.
- **Telemetry** — Data a device emits continuously about its operation.
- **Predictive maintenance** — Using equipment data to schedule repairs before a part fails.
- **SME (Subject Matter Expert)** — A domain expert who helps make narratives technically solid.
