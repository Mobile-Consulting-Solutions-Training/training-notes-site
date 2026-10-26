---
title: Study Guide - Day 17
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 17: dbt with Snowflake"
sidebar:
  order: 170
---

Study Guide - Day 17 (source: notes/Training 17.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**TARGET_LAG, Properly.** "Keeping this table no more than about X behind the upstream table." It's a target, not a guarantee, and not a cron schedule: Snowflake decides when to refresh from the lag, past refresh times and the dependency chain, and skips work if nothing changed. If a refresh takes longer than the target, Snowflake lets the target be exceeded, finishes the running refresh, reschedules, coordinates the chain and **records the miss**. It does **not** fail the job or scale up the warehouse automatically (that costs money, so a human decides). Fixes: bigger warehouse, better SQL, or a realistic target. Dynamic Tables suit reliable data with a stable schema.

**DAG in dbt vs Spark vs Airflow.** A DAG is steps you can only move forward through. Spark: stages of the physical execution plan (low level). Airflow: tasks in a workflow (orchestration). dbt: models and their `ref()` dependencies (transformation lineage). A dbt node = one model. dbt doesn't know what Bronze/Silver/Gold mean; that's a naming convention.

**Connecting dbt to Snowflake.** Credentials go in `~/.dbt/profiles.yml`, not `dbt_project.yml` (project settings). MFA blocked `dbt debug` ("Failed to authenticate with MFA when TOTP is required"). Fix: `authenticator: username_password_mfa` and keep the password; `ALTER ACCOUNT SET ALLOW_CLIENT_MFA_CACHING = TRUE`; run a small `snowflake.connector` script with the current passcode to cache the token; then `dbt debug` works. Snowsight's ▶ runs only the statement under the cursor. UI vs CLI permission differences usually mean a different role/database/schema context. Fully qualify names from `snow sql`.

**Building the Models.** Check the real schema first (`DESCRIBE TABLE`): AI-generated SQL used columns that didn't exist. `dbt ls --resource-type source` lists sources (dbt didn't create `RAW.ORDERS`). Staging: `select ... from {{ source('raw', 'orders') }}`. `dbt compile` turns Jinja into plain SQL. `dbt run`, `dbt run --select silver_orders`, `--select +silver_orders` (model plus everything upstream). Gold `order_total` from `{{ ref('silver_orders') }}`. Output landed in the profile's **`DBT_DEV`** schema, all as views (default config). Bug: column renamed in SELECT but not GROUP BY → `invalid identifier`.

**Jinja.** A templating format that `dbt compile` turns into the SQL Snowflake understands (`{{ source() }}`, `{{ ref() }}`). Not dbt-specific; also used in Flask and Django.

**dbt Tests.** "A query that's looking for bad records": 0 rows = pass. dbt is an ELT modeling framework that also tests, not a testing framework. Tests in YAML under `columns: → data_tests:` (`not_null`, `unique`, `accepted_values`, `relationships`). `dbt test`, `dbt test --select model`. Indentation errors make tests silently disappear. Demo: setting a status to "banana" passed until an `accepted_values` test was added; a test only catches what you defined. Tests check data, not schema. Test at the source and also at Silver and Gold.

**Industry and Interview Notes.** Most dbt use is with Snowflake (~80-90%). If your story mentions Snowflake, mention dbt too. DE interviews are narrative-driven: explain your pipeline (source → ingestion → processing → storage) and where you had the biggest impact, for every project on your CV, starting with the most recent. Big-picture architecture matters more than exact syntax.

---

# Part 2: Cheat Sheet

## TARGET_LAG
- Target, not guarantee, not cron · may be exceeded · miss recorded
- No auto-fail, no auto-scale · fix: bigger warehouse, better SQL, realistic target

## DAGs
- Spark = execution stages · Airflow = workflow tasks · dbt = model lineage via `ref()`
- Layer names are convention only

## dbt + Snowflake Setup
- `~/.dbt/profiles.yml` = credentials · `dbt_project.yml` = project config
- MFA: `username_password_mfa` + password · `ALLOW_CLIENT_MFA_CACHING = TRUE` · cache token, then `dbt debug`

## Commands
- `dbt debug` · `dbt ls --resource-type source` · `dbt compile` · `dbt run`
- `--select model` · `--select +model` (with upstream) · `dbt test` · `dbt build`

## Models
- `{{ source('raw','orders') }}` for raw tables · `{{ ref('model') }}` between models
- Output in the target schema (e.g. `DBT_DEV`) · default materialization = view
- Check real columns before trusting generated SQL

## Tests
- `not_null` · `unique` · `accepted_values` · `relationships` in YAML `data_tests:`
- Pass = zero bad rows · only catches what you define · watch indentation

## Interviews
- Explain your pipeline end to end + your biggest impact · every project on the CV

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What does TARGET_LAG actually mean?
A: It's how far behind the upstream table you're willing to let the dynamic table get. It's a target Snowflake schedules refreshes around, not a guarantee and not a cron schedule.

Q: What happens if a refresh takes longer than the target lag?
A: Snowflake lets the target be exceeded, finishes the refresh, reschedules the next ones and records the miss. It doesn't fail the job or scale up the warehouse, because that costs money and is a human decision.

Q: How do you fix a target lag that's missed repeatedly?
A: Give it a bigger warehouse, make the SQL more efficient, or accept that the target isn't realistic for the data volume.

Q: How is a DAG different in dbt, Spark and Airflow?
A: In Spark it's the stages of the execution plan. In Airflow it's the tasks in a workflow. In dbt it's the models and which ones reference which, so it shows how data moves through the transformations.

Q: Does dbt know what Bronze, Silver and Gold mean?
A: No. Those are naming conventions. The DAG looks like the medallion layers only because we design the models that way.

Q: Where do Snowflake credentials go in a dbt project?
A: In profiles.yml in the .dbt folder of your home directory. dbt_project.yml holds project settings like model paths and materializations.

Q: How did the class get dbt past Snowflake MFA?
A: By setting the authenticator to username_password_mfa while keeping the password, turning on client MFA caching for the account, and running a small connector script with the current code to cache the token. Then dbt debug worked.

Q: What's the difference between source and ref in dbt?
A: Source points to a raw table that already exists in the warehouse and that dbt didn't build. Ref points to another dbt model and tells dbt the build order.

Q: What does dbt compile do?
A: It turns the Jinja in your models, like source and ref, into plain SQL with real database, schema and table names.

Q: What does the plus sign in dbt run --select +silver_orders mean?
A: Build that model and everything upstream of it.

Q: Why did the class's models end up in DBT_DEV?
A: dbt builds into the schema set in the profile's target, and that was DBT_DEV.

Q: What is a dbt test?
A: A query that looks for bad records. If it returns zero rows the test passes; any rows and it fails.

Q: Why did setting a status to "banana" still pass the tests at first?
A: Only not_null and unique tests existed, and banana breaks neither. A test can only catch what you defined, so it failed once an accepted_values test was added.

Q: Do dbt tests check the schema or the data?
A: The data. They inspect the actual values in the table.

Q: Where should dbt tests go?
A: Ideally at the source layer, but it's good practice to test Silver and Gold too, because unexpected things happen.

Q: What do data engineering interviewers usually ask about?
A: Your projects' pipelines: the source, ingestion, processing and storage, and which part you had the biggest impact on. Be ready to talk about every project on your CV.
