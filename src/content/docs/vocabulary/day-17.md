---
title: Day 17 Vocabulary
description: Glossary of terms and definitions from the Training 17 notes.
sidebar:
  order: 17
---

Vocabulary — Study Guide Day 17

Source: notes/Training 17.md

## Dynamic Tables and TARGET_LAG
- **Dynamic table** — A Snowflake table that stores a query result Snowflake keeps refreshed automatically.
- **TARGET_LAG** — A time frame saying the table is kept no more than about that far behind its upstream table; a target, not a guarantee.
- **Best effort** — Snowflake lets the target be exceeded rather than failing the refresh.
- **Upstream table** — A source table that a model or dynamic table depends on.
- **Downstream** — Objects that depend on and are refreshed after a given table.
- **Dependency chain** — The ordered upstream/downstream refreshes Snowflake coordinates.
- **Cron schedule** — A fixed time-based job schedule, which `TARGET_LAG` is not.
- **Missed target** — A refresh that exceeded `TARGET_LAG`, which Snowflake records so engineers can be alerted.
- **Scale up** — Giving a workload a bigger warehouse; Snowflake never does this automatically for dynamic tables.

## DAGs
- **DAG (Directed Acyclic Graph)** — A structure of steps where you can only go from one step to the next and never go back.
- **Spark DAG** — Low-level stages of transformations and actions in the physical execution plan.
- **Airflow DAG** — High-level tasks in an orchestrated workflow.
- **dbt DAG** — Models and their dependencies, showing data transformation lineage.
- **Node (dbt DAG)** — One dbt model (or source, test, etc.) in the graph.
- **Lineage** — The path data takes from source through each transformation.
- **Staging / intermediate / marts** — An alternative layer-naming convention to Bronze / Silver / Gold.
- **Medallion layers** — The Bronze, Silver and Gold convention, which dbt itself doesn't know about.

## Connecting dbt to Snowflake
- **dbt (data build tool)** — An ELT modeling framework that transforms data inside the warehouse and also does testing.
- **Adapter** — The dbt plugin for a specific warehouse, e.g. postgres or snowflake.
- **profiles.yml** — File in `~/.dbt/` holding connection credentials and targets.
- **dbt_project.yml** — File holding project settings such as model paths and materializations.
- **Target (dbt)** — A named connection profile entry, including the schema dbt builds into.
- **dbt debug** — Tests dbt's configuration and warehouse connection.
- **dbt init** — Creates a new dbt project with default files.
- **MFA (Multi-Factor Authentication)** — Login requiring a second factor beyond the password.
- **TOTP (Time-based One-Time Password)** — A 6-digit code that changes every 30–60 seconds, e.g. from Google Authenticator.
- **authenticator: username_password_mfa** — profiles.yml setting for password plus MFA login, used with the password kept.
- **ALLOW_CLIENT_MFA_CACHING** — Snowflake account parameter allowing clients to cache an MFA token.
- **MFA token caching** — Storing an MFA token locally so later connections don't need a new code.
- **snowflake.connector** — Snowflake's Python connector library.
- **passcode** — Connector parameter that passes the current MFA code.
- **Snowflake CLI (`snow`)** — Snowflake's command-line tool, storing connections in `config.toml`.
- **USE ROLE / USE SCHEMA** — Statements setting the session's active role or schema.
- **Session context** — The role, database and schema a session is using, which can cause UI-only permission errors.
- **Fully qualified name** — An object name written as `DATABASE.SCHEMA.TABLE`.

## Building dbt Models
- **Model** — A dbt `.sql` file holding the logic that moves data one step.
- **DESCRIBE TABLE** — Shows a table's columns and types.
- **Source (dbt)** — An existing warehouse table registered to dbt in YAML, not created by dbt.
- **source()** — Jinja function referencing a registered source, e.g. `{{ source('raw', 'orders') }}`.
- **ref()** — Jinja function referencing another model, which builds the DAG.
- **dbt ls --resource-type source** — Lists the sources dbt knows about.
- **Staging model** — The first model that selects from a raw source.
- **dbt compile** — Turns Jinja into plain SQL with real `DATABASE.SCHEMA.TABLE` names without running it.
- **dbt run** — Builds models in the warehouse.
- **--select** — Flag limiting a dbt command to specific models.
- **+ (graph operator)** — Prefix in `--select +model` meaning the model and everything upstream of it.
- **Materialization** — How dbt builds a model; the `dbt init` default is a view.
- **Gold model** — A business-level aggregate model, e.g. `order_total`.
- **invalid identifier** — Snowflake error for a column name that doesn't exist.
- **GROUP BY** — Groups rows for aggregation; every non-aggregated selected column must match it.
- **Jinja** — A templating format that `dbt compile` turns into SQL Snowflake understands; also used in Flask and Django.

## dbt Tests
- **dbt test (concept)** — Essentially a query looking for bad records: 0 bad rows passes, any bad rows fail.
- **dbt test (command)** — Runs all tests, or one model's tests with `--select`.
- **data_tests** — YAML key under a column listing its tests.
- **not_null** — Test that a column has no nulls.
- **unique** — Test that a column has no duplicate values.
- **accepted_values** — Test that a column only contains values from a given list.
- **YAML** — Indentation-based config format; tests under the wrong key are silently not found.
- **Data test** — A test that checks the values in the table, not the column definitions.
- **Delta Live Tables** — Databricks' native declarative pipeline feature that does a similar job to dbt.

## Interview Notes
- **Project narrative** — The story of your pipeline architecture (source → ingestion → processing → storage) interviewers ask about.
