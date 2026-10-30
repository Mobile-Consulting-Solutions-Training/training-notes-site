---
title: Day 33 Vocabulary
description: Glossary of terms and definitions from the Training 33 notes.
sidebar:
  order: 33
---

Vocabulary — Study Guide Day 33

Source: notes/Training 33.md

## Direct Lake and Power BI
- **Semantic model** — Power BI's data model of tables, relationships and measures behind reports.
- **Storage mode** — A table property that sets how a semantic model gets data: Import, DirectQuery or Direct Lake.
- **Import mode** — Data is copied into the model and refreshed on a schedule; fast but only as fresh as the last refresh.
- **DirectQuery** — Each visual sends a live query to the source; fresh but slower and puts load on the source.
- **Direct Lake** — A Fabric-only mode that loads column data straight from OneLake Delta files; near Import speed with near-live freshness.
- **DirectQuery fallback** — Direct Lake switching to DirectQuery when a table is too large or is a SQL view.
- **Model view** — The semantic model editor view showing tables and their properties.
- **Report** — A canvas of visuals built on a semantic model.
- **Card visual** — A visual that shows a single KPI number.
- **Clustered bar chart** — A visual comparing values across categories.
- **Line chart** — A visual showing a trend over time.

## DAX
- **DAX (Data Analysis Expressions)** — Power BI's formula language for measures and calculated columns.
- **Measure** — A named calculation evaluated at query time in the current filter context.
- **Calculated column** — A column computed row by row and stored in the model.
- **Filter context** — The set of filters (from slicers, axes and rows) applied when a measure is evaluated.
- **SUM** — DAX aggregation adding a column's values.
- **DIVIDE** — DAX safe division that returns an alternate result instead of a divide-by-zero error.
- **DISTINCTCOUNT** — DAX aggregation counting unique values.
- **Measure referencing measures** — A measure built from other measures, such as `[Total Admissions] - [Total Discharges]`.

## Mirroring and Azure SQL
- **Mirroring (Fabric)** — Continuous replication of a database into OneLake Delta tables, keeping it available in Fabric without pipelines.
- **CDC (Change Data Capture)** — Capturing inserts, updates and deletes from a database's log to replicate changes.
- **Mirrored Azure SQL Database** — The Fabric item type for mirroring an Azure SQL database.
- **Deleted database restore** — Restoring a dropped Azure SQL database from a restore point within the retention period.
- **Restore point / point-in-time restore** — A past moment you can restore a database to.
- **SQL logical server** — The Azure resource holding Azure SQL databases, logins, firewall rules and identities.
- **SQL databases vs SQL Server databases (portal)** — Azure SQL managed databases versus databases on SQL Server instances, including Azure Arc.
- **Managed identity** — An Azure-managed identity for a resource, used to authenticate without stored secrets.
- **System-assigned identity** — A managed identity tied to one resource's lifecycle.
- **User-assigned identity** — A standalone managed identity that can be shared across resources.
- **Principal ID** — The object ID of an identity in Entra ID.
- **Cross-tenant restriction** — Mirroring with a managed identity can't work when the SQL server and Fabric are in different tenants.
- **REST API update** — Changing an Azure resource by calling the Azure Resource Manager API directly.
- **Organizational account** — Signing in with your Entra ID work account instead of a SQL login.

## Azure Event Hubs
- **Azure Event Hubs** — Azure's managed, partitioned event-streaming broker, Kafka-compatible.
- **Event Hubs namespace** — The Event Hubs container, equivalent to a Kafka cluster.
- **Event hub** — One stream in a namespace, equivalent to a Kafka topic.
- **Partition** — An ordered subdivision of an event hub for parallelism.
- **Consumer group** — A named view of the stream with its own read positions; `$Default` by default.
- **Message retention** — How long events are kept in the event hub.
- **Capture** — An Event Hubs feature that auto-writes events to storage; disabled in class.
- **Cleanup policy (Delete)** — Events are deleted after the retention period.
- **Basic tier** — The cheapest Event Hubs pricing tier.
- **Shared access policy** — A named key with Send, Listen and/or Manage claims.
- **Send / Listen / Manage claims** — Permissions to publish events, read events, or do both plus manage entities.
- **Least privilege** — Granting only the permissions a role needs.
- **Connection string** — Endpoint plus key name and key that SDK clients use; a secret.
- **Data Explorer (Event Hubs)** — The portal view for browsing events in a partition.
- **Broker** — The middle layer that stores and serves events between producers and consumers.

## Producer and Consumer Code
- **Virtual environment (venv)** — An isolated Python environment for a project's packages.
- **azure-eventhub** — The Python SDK for Azure Event Hubs.
- **EventHubProducerClient** — The SDK client that sends events.
- **EventData** — The SDK object wrapping one event's body.
- **create_batch / send_batch** — Create an event batch, then send it in one call.
- **EventHubConsumerClient** — The SDK client that receives events.
- **on_event callback** — The function called for each received event.
- **starting_position "-1"** — Read from the beginning of the retained stream.
- **Backlog** — Retained events that a newly connected consumer reads first.
- **Environment variable** — A value set in the shell that code reads at runtime, used for secrets.
- **while True loop** — An infinite loop that runs until stopped manually or by a failure.
- **time.sleep** — Pauses the loop; here one event every two seconds.
- **Graceful shutdown** — Stopping a stream cleanly: flush, close, checkpoint.
- **KeyboardInterrupt** — The Python exception raised by Ctrl+C.
- **SIGTERM** — The termination signal sent by Docker, Kubernetes or systemd to stop a process.
- **flush / close** — Send buffered messages / release the client's connections.
- **Checkpoint** — A saved consumer position so a restart resumes where it left off.

## Fabric Real-Time Intelligence
- **Eventstream** — A Fabric no-code item that ingests, routes and lightly transforms streams.
- **Schema-aware eventstream** — A preview option for schema-managed streams, relevant to schema evolution.
- **Edit mode / Live view** — Eventstream modes for designing the flow and watching it run after publishing.
- **Publish** — Activating eventstream changes.
- **Destination** — Where an eventstream sends data, such as an Eventhouse or a lakehouse.
- **Eventhouse** — Fabric's real-time analytics store, based on Azure Data Explorer.
- **KQL database** — A time-series optimized database inside an Eventhouse.
- **KQL queryset** — Saved KQL queries against a KQL database.
- **Real-Time Dashboard** — An auto-refreshing dashboard whose tiles run KQL queries.
- **Azure Data Explorer (ADX)** — Azure's fast analytics service for log and time-series data, the engine behind Eventhouse.

## KQL
- **KQL (Kusto Query Language)** — A read-only, pipe-based query language for ADX, Fabric and Log Analytics.
- **Pipe operator (|)** — Passes rows from one KQL operator to the next.
- **take** — Returns a number of rows, like LIMIT.
- **count** — Returns the row count.
- **where** — Filters rows.
- **summarize ... by** — Aggregates by group, like GROUP BY.
- **order by / sort by** — Sorts rows.
- **bin()** — Rounds timestamps into fixed buckets for time series.
- **render timechart** — Draws a time chart from a query result.
- **Bracket-quote names** — `['patient-events']` syntax for identifiers containing dashes.

## Lakehouse Streaming Medallion
- **Hot path / cold path** — A real-time store for live views alongside a lakehouse for historical, joined analytics.
- **bronze_patient_events** — The lakehouse table receiving raw streaming events.
- **Default lakehouse** — The lakehouse a Fabric notebook resolves table names against.
- **"No default context exists"** — The Fabric notebook error when no default lakehouse is set.
- **Unified table** — Silver batch encounters joined with a summary of streaming events.
- **Tumbling window** — Fixed, non-overlapping time buckets, created with `F.window(ts, "5 minutes")`.
- **Net admissions** — Admissions minus discharges, approximately the current in-patients.
- **display()** — The notebook function for showing a DataFrame as a table.

## Interview Prep
- **STAR method** — Situation, Task, Action, Result structure for answers.
- **Architecture at a glance** — A summary diagram or description of a project's pipeline for a narrative.
- **Slowly changing dimension (SCD)** — A dimension whose attributes change over time; Type 1 overwrites, Type 2 keeps history rows.
- **Data quality gate** — A check that stops bad data from moving to the next layer.
- **Quarantine table** — Where rows failing validation are stored for review.
- **Tokenization / masking** — Replacing or hiding sensitive values such as card numbers.
- **PCI-DSS** — The security standard for handling payment card data.
- **Key Vault / KMS** — Azure and AWS key and secret management services.
