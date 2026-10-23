---
title: "Training 17 - dbt with Snowflake"
description: "dbt DAGs, building models (RAW -> STG -> SILVER -> GOLD), dbt tests, Dynamic Table TARGET_LAG, Snowflake MFA for dbt, and interview narrative advice."
sidebar:
  order: 17
---

Teacher: Evan Flint

Syllabus Day 18 (per file numbering) - topic: dbt with Snowflake - DAGs, building models (RAW -> STG -> SILVER -> GOLD), and dbt tests. Also: Dynamic Table `TARGET_LAG` follow-up, Snowflake MFA for dbt, and interview narrative advice.

# Training 17

# Agent Generated Notes (from Class Recording)

Source: `transcriptions/Training 17 – 2026-10-05 14-22-06/transcript.md` (2h49m). Roughly the first hour was lost to a Snowflake permissions error in the UI and an MFA authentication problem connecting dbt to Snowflake. The actual dbt lesson runs from about 01:41 to 02:28. Homework: `homework/submission/alexjackson_training-17-homework/`. Runnable local copy of the class project: `class-demos/dbt-orders/`.

---

## Dynamic Tables: what `TARGET_LAG` actually means

Teacher's definition: "You specify a time frame where you're saying we are keeping this table no more than about X amount of time behind the upstream table." ... "Target lag is a target, not a guarantee."

**Expanded:** On Friday's demo new rows appeared instantly only because the data was tiny. With a real load, the refresh takes time, and `TARGET_LAG` is the freshness *goal* Snowflake schedules around. It is not a cron schedule (a student compared it to one): Snowflake decides when to start refreshes based on the lag, past refresh durations, and the dependency chain, and it skips work if nothing changed upstream.

What happens if a refresh would take 10 minutes but the target lag is 5:

| Snowflake does | Snowflake does NOT do |
|---|---|
| Lets the target be exceeded (best effort) | Fail the job ("a target of 5 min and an actual of 6 min failing the job makes zero sense") |
| Finishes the refresh that's already running | Automatically scale up the warehouse. More compute costs the customer money, so a human has to decide that |
| Reschedules future refreshes; may skip/defer one so the chain can keep up | |
| Coordinates upstream/downstream refreshes in the chain | |
| **Records that the target was missed** (so engineers get alerted) | |

When the target is being met, Snowflake is still busy, but only scheduling and monitoring: tracking freshness, refreshing proactively, coordinating dependencies.

When it's missed repeatedly, the fix is a human decision: give it a bigger warehouse, make the SQL more efficient, or **accept that the target is unrealistic**. ("You can't have a target lag of five minutes if you're ingesting 50 million rows.")

Teacher's framing on when Dynamic Tables fit: data that is reliable and whose schema doesn't change. The transformations then apply automatically as soon as data lands upstream, so nobody has to manually run dbt for Silver, check it, then do Gold.

---

## What "DAG" means in dbt vs Spark vs Airflow

Teacher's definition: "When we're talking about DAGs, what we're talking about is a structure in which we have multiple steps and you can only go from one step to the next step and you can never go back."

| Tool | What the DAG describes | Level |
|---|---|---|
| **Spark** | Stages of transformations and actions in the physical execution plan | Low level (execution) |
| **Airflow** | Tasks in a workflow, e.g. call an API → save to a directory → upload to S3 → run Terraform | High level (orchestration) |
| **dbt** | Models and their dependencies (who `ref()`s whom), e.g. `raw.orders → stg_orders → silver_orders → order_total` | Data transformation lineage |

- **A node in the dbt DAG = one dbt model** (plus sources, tests, etc.). Each model holds the logic that moves data one step, for example from Bronze into Silver.
- **dbt doesn't know what Bronze/Silver/Gold mean.** Those names are a convention. Other companies say raw / processing / processed, or staging / intermediate / marts. The DAG resembles the medallion layers only because we designed the models that way.
- Evan's conclusion after the break: "for all practical purposes" the dbt DAG *is* the movement of data up through the lakehouse layers.

---

## Connecting dbt to Snowflake (the MFA problem)

The demo project (`dbt_test`) was originally pointed at **local Postgres** (`dbt debug` showed `Registered adapter: postgres`). Switching it to Snowflake:

1. **Connection details go in `~/.dbt/profiles.yml`, not `dbt_project.yml`.** Evan first pasted the connection block into `dbt_project.yml` and got `property ... is not allowed`. `dbt_project.yml` holds project settings (model paths, materializations). `profiles.yml` holds credentials and targets.
2. `dbt debug` failed with: *"Failed to authenticate with MFA when TOTP is required."* The account has Google Authenticator MFA, and the 6-digit code changes every 30–60 seconds, so it can't go in a file.
3. What finally worked:
   - In profiles.yml: `authenticator: username_password_mfa` **and keep the `password`**. Removing the password gave "password is empty". A misspelled `password:` key also caused a failure.
   - In Snowsight (as an admin role): `ALTER ACCOUNT SET ALLOW_CLIENT_MFA_CACHING = TRUE;`
   - Ran a small Python script (`test.py`, using `snowflake.connector` with `passcode=<current 6-digit code>`) **while the code was still valid**. This caches the MFA token locally.
   - Then `dbt debug` → connection OK. Evan shared that script with the class: put in your own credentials plus the current authenticator code, run it, then run `dbt debug`.
4. A student's alternative: the Snowflake CLI (`snow`) keeps connections in `config.toml`. Set the authenticator there and store the password in that file.

Other gotchas from the same hour:
- **Snowsight runs only the statement under the cursor** when you click ▶. Use the dropdown arrow next to it to "run all" (this is why the `USE ROLE`/`USE SCHEMA` lines appeared not to work).
- A permissions error in the UI but not the CLI usually means the UI session is using a different role, database or schema context.
- `snow sql` remembers its default database (`DEMO_DB`). **Fully qualify** names (`DE_CLASS.DBT_DEV.ORDER_TOTAL`) when querying dbt output from the CLI.

---

## Building the models (the actual dbt demo)

`RAW.ORDERS` columns (confirmed with `DESCRIBE TABLE`): `ORDER_NUMBER, ORDER_DATE, EXPECTED_RECEIVING_DATE, SHIPPING_DATE, STATUS`. The AI-generated staging model initially used `customer_id`/`amount`, which don't exist. **Always check the real schema before trusting generated SQL.**

Steps, in order:

| Step | Command / file | Notes |
|---|---|---|
| Check the source is registered | `dbt ls --resource-type source` | Lists sources dbt knows about. `RAW.ORDERS` already existed in Snowflake; **dbt did not create it** |
| Staging model | `models/staging/stg_orders.sql` → `select ... from {{ source('raw', 'orders') }}` | "The key line is `from source raw orders`" |
| Compile first | `dbt compile` | Turns the Jinja (`{{ source(...) }}`, `{{ ref(...) }}`) into plain Snowflake SQL with real `DATABASE.SCHEMA.TABLE` names |
| Run | `dbt run` / `dbt run --select silver_orders` | Staging built as a **view** |
| Run with upstream | `dbt run --select +silver_orders` | `+` before the name = the model **and everything upstream of it** |
| Gold model | `models/gold/order_total.sql` → `count(*) as order_count, avg(days_to_ship)` from `{{ ref('silver_orders') }}` | |

**Evan's exact code** (read off the video frames): `class-demos/training-17-evan-dbt/`. Note that his `silver_orders` reads `source('raw','orders')` directly rather than `ref('stg_orders')`, so his real DAG was `RAW → STG` and `RAW → SILVER → ORDER_TOTAL`. Every model was a **view**, because his `dbt_project.yml` was the untouched `dbt init` default.

**Where did the tables go?** dbt built them in the **`DBT_DEV` schema** (the schema set in the profile's target), not in `DE_CLASS.SILVER`. So: `select * from DE_CLASS.DBT_DEV.STG_ORDERS`.

**Bug worth remembering:** Gold failed with `invalid identifier ORDER_ID`. Evan had changed `order_id → order_number` in the `SELECT` but not in the `GROUP BY`. Re-running `dbt compile` didn't help because the bug was in the source file.

The class `order_total` grouped by `order_number`, so every count was 1. Evan said it wasn't meaningful data, but it showed valid SQL running end to end. The homework fixes this with `shipping_stats`, which groups by `STATUS`.

### Jinja
Teacher's definition: Jinja templating is "a format that is going to be used to identify the database, which is understood by `dbt compile`, and then it's made into the correct format that Snowflake is going to be able to understand."
- Jinja is **not dbt-specific**. It's also used in web development (Python back ends like Flask and Django render HTML with it).

---

## dbt Tests

Teacher's definition: "A dbt test is essentially a query that's looking for bad records." 0 bad rows = PASS, any bad rows = FAIL.

**dbt is not a testing framework.** Evan said people who haven't taken a dbt class often think it is, because testing is the most widely taught part. dbt is an ELT modeling framework that also does testing.

Tests are added in YAML under `columns: → data_tests:`:

```yaml
sources:
  - name: raw
    database: DE_CLASS
    schema: RAW
    tables:
      - name: orders
        columns:
          - name: order_number
            data_tests:
              - not_null
              - unique
          - name: status
            data_tests:
              - not_null
              - accepted_values:
                  values: ['Shipped', 'Cancelled', 'Resolved', 'On Hold', 'Disputed', 'In Process']
```

- `dbt test` runs all tests. `dbt test --select silver_orders` runs tests for one model. Run output: *"Found 3 models, 5 tests, 2 sources"*.
- Silver tests added: `order_number` not_null and unique, plus `days_to_ship`.
- Indentation matters: tests under the wrong key are silently not found (Evan's first `--select` found "nothing to do").

### Live demo: making a test fail on purpose
1. `UPDATE DE_CLASS.RAW.ORDERS SET STATUS = 'banana' WHERE ORDER_NUMBER = ...;`
2. `dbt test` → **still passed**, because only `not_null` and `unique` existed and "banana" breaks neither. *A test can only catch what you defined.*
3. Added an `accepted_values` test on `status` → `dbt test` → **FAIL** ("banana" isn't Shipped / Cancelled / Resolved / On Hold / Disputed / In Process).
4. `UPDATE ... SET STATUS = 'Shipped'` → `dbt test` → PASS.

**Q (student): do tests check the schema or the data?** The **data**. The banana test inspected the values in the table, not the column definitions.

**Q (student): if Silver is already cleaned, where should tests go?** Ideally all the validity rules are tested at the Bronze/source layer, but it's good practice to also test Silver and Gold "because unforeseen events happen all the time." Tests are a formal definition of what valid data looks like.

---

## Industry / Interview Notes

- **dbt + Snowflake:** very common together but not required. Evan estimates 80–90% of dbt usage is with Snowflake; the rest is Redshift, BigQuery, Synapse, and occasionally Databricks. He finds Databricks odd because Delta Live Tables does the same job natively.
- **Narrative advice:** if your project narrative mentions Snowflake, also mention dbt, and vice versa. Don't invent "dbt with Postgres" unless there's a specific reason.
- **Data engineering interviews are narrative-driven** (unlike mobile, where you know you'll be asked about Kotlin):
  - Every project's architecture is different, so interviewers ask about *your* pipeline: source → ingestion → processing → storage, and **which part you had the biggest impact on**. Pick the part you know best.
  - The most recent project matters most, then the second most recent, and so on. Be able to speak about **every** project on your CV, because some interviewers ask about an old one to check you're telling the truth.
  - Big-picture architecture matters more than exact SQL syntax in interviews. Facilitators can help with details.
- **Coding clinics** are currently aimed at absolute beginners (list comprehensions, iteration vocabulary). If you're already comfortable in Python, focus on knowing your pipeline architecture.

**Next class:** AWS.
