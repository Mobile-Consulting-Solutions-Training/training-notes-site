---
title: "Training 25 Homework"
description: "Homework assignment for Training 25: AI on the Pipeline."
sidebar:
  order: 25
---

:::note
The assignment prompt as given in class. Related notes: [Training 25](/training-notes-site/notes/training-25/).
:::

## Homework - Training 25 (Assignment)

Data Engineering Pipelines, Amazon Bedrock, and AI-Generated SQL

**Due:** Tomorrow's class  
**Focus:** Pipeline development, SQL analytics, and an introduction to generative AI with Amazon Bedrock  
**Estimated time:** 60–90 minutes of reading and exercises, plus continued pipeline development

### Objective

Today we demonstrated how Amazon Bedrock can be integrated with a Streamlit application to translate natural-language questions into SQL, execute approved queries against Amazon Redshift, and explain the returned results.

This assignment introduces the concepts behind that functionality while reinforcing the data engineering principles we've been studying.

#### Important: Prioritize your existing pipeline

**Your first priority is to continue building, debugging, and improving the AWS data pipeline you've been working on in class.**

Do not abandon your existing project to build an AI chatbot.

By tomorrow, you should focus on making meaningful progress toward a functioning end-to-end pipeline, including ingestion, transformation, storage, and querying.

**You are NOT expected to implement Amazon Bedrock, build a chatbot, or reproduce the instructor's Streamlit AI functionality by tomorrow.**

The AI-related material is primarily for conceptual understanding. We will work toward implementing it after your underlying pipelines are sufficiently developed.

---

### Part 1 — Continue Your Existing Data Pipeline

**Priority: Highest**

Continue working on your existing AWS pipeline using the services and architecture you've been developing.

Depending on your current progress, concentrate on the following:

- **Ingestion:** Ensure data is being collected successfully through your ingestion process, such as Lambda, Kinesis, or another source.
- **Bronze layer:** Verify that raw data is arriving in S3 and is organized appropriately.
- **Silver layer:** Use AWS Glue or Spark to clean, transform, deduplicate, and standardize records.
- **Gold layer:** Build meaningful analytical tables in Redshift, including fact and dimension tables where appropriate.
- **Orchestration:** Continue developing your Step Functions workflow and any necessary scheduling.
- **Validation:** Confirm that records are moving through the pipeline correctly and that the output is suitable for analytical queries.

You do not need to finish every component by tomorrow. Focus on resolving existing blockers and advancing the pipeline.

#### Deliverable

Be prepared to explain:

1. Which components of your pipeline are currently working?
2. What did you accomplish since the previous class?
3. What is the next component you need to build?
4. What technical problem is currently preventing further progress, if any?
5. What evidence have you collected that your pipeline is producing correct data?

Bring relevant AWS console screenshots, CLI output, SQL queries, or logs to demonstrate your progress.

---

### Part 2 — Reading: Analytical SQL and Data Warehousing

**Estimated time: 20 minutes**

Review the following concepts. You should understand what each does and when it is useful, but you do not need to memorize every syntax detail.

#### A. Fact tables and dimension tables

Review the difference between:

- Fact tables, which record measurable events or observations.
- Dimension tables, which describe entities such as stations, products, or customers.
- The *grain* of a fact table: what exactly one row represents.
- How fact tables are joined to dimension tables.

For example, in our Citi Bike project, a station dimension contains station information, while a snapshot fact table contains repeated observations of bike availability over time.

**Think about:** Why might a query joining these tables return the same station name many times?

#### B. Window functions

Review these SQL functions:

- `ROW_NUMBER()`
- `RANK()`
- `LAG()`
- `AVG() OVER (...)`

Pay particular attention to `PARTITION BY` and `ORDER BY` inside window functions.

Learn how Amazon Redshift's `QUALIFY` clause can filter the results of a window function.

**Think about:** How could you retrieve only the most recent observation for each station?

#### C. Aggregation and time-series analysis

Review:

- `GROUP BY`
- `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`
- `CASE WHEN`
- Date and timestamp grouping
- The difference between individual observations and aggregated results

**Think about:** Why would summing bike availability across every snapshot in a day produce a misleading number?

Suggested reading:

- [Amazon Redshift — Window functions](https://docs.aws.amazon.com/redshift/latest/dg/c_Window_functions.html)
- [Amazon Redshift — QUALIFY clause](https://docs.aws.amazon.com/redshift/latest/dg/r_QUALIFY_clause.html)

---

### Part 3 — Reading: Introduction to Amazon Bedrock

**Estimated time: 15 minutes**

Amazon Bedrock is an AWS service that provides access to foundation models through managed APIs.

Unlike training a model from scratch, an application can send instructions and context to an existing model and receive a generated response.

Our classroom demonstration used Bedrock to translate questions about Citi Bike data into Redshift SQL.

Review these concepts:

**1. Foundation models**

What is a foundation model, and how does it differ from a traditional application with explicitly programmed rules?

**2. Prompt engineering**

How can instructions and examples influence the SQL a model generates?

**3. Context and schema grounding**

Why is it important to provide the model with the actual database tables, columns, and relationships?

**4. Hallucinations**

Why might a model generate SQL referencing columns that do not exist?

**5. Human approval**

Why should generated SQL be reviewed before execution?

Suggested reading:

- [Amazon Bedrock — Getting started](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html)
- [Amazon Bedrock — Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-call.html)

You are not required to create a Bedrock resource or invoke a model for this assignment.

---

### Part 4 — Short Practical SQL Exercises

**Estimated time: 20–30 minutes**

Complete these exercises using your own project's tables wherever possible.

If your Redshift tables are not ready, write the SQL using the table structures you intend to create. You may use the Citi Bike examples as a reference.

#### Exercise 1 — Basic aggregation

Write a query that groups records by an entity and calculates:

- Total number of records
- Average value of a numeric field
- Maximum value of that field

Explain what each result represents.

#### Exercise 2 — Latest record per entity

Write a query that returns only the most recent record for each entity.

Use `ROW_NUMBER()` with `PARTITION BY`, followed by `QUALIFY` or a common table expression (CTE).

For example, return the most recent bike availability observation for every station.

#### Exercise 3 — Detect duplicates

Write a query that identifies records sharing the same expected business key.

For Citi Bike, the intended snapshot grain is:

`station_id + snapshot_timestamp`

Use `GROUP BY`, `COUNT(*)`, and `HAVING COUNT(*) > 1`.

Explain how duplicate records might enter an AWS data pipeline.

#### Exercise 4 — Analytical question

Choose one question that your own data warehouse should eventually be able to answer.

Write the SQL needed to answer it, or describe which tables and columns would be required.

Examples:

- Which products generated the most revenue?
- Which customers placed the most orders?
- Which stations had the highest average utilization?
- How did transaction volume change by day?

---

### Part 5 — Conceptual Questions: AI and Data Engineering

**Estimated time: 10–15 minutes**

Answer each question in approximately 2–4 sentences.

1. Why does a text-to-SQL application need information about the database schema?
2. What should an AI system do when a user asks a question requiring data that doesn't exist in the database?
3. Why is a database's fact-table grain important when generating SQL?
4. What is the difference between an SQL syntax error and a hallucinated column name?
5. Why might a developer choose a smaller, less expensive foundation model for a SQL-generation application?
6. What are the advantages of separating SQL generation, user approval, query execution, and result interpretation into distinct steps?
7. Why should the database credentials used by an AI application have read-only permissions?

---

### Part 6 — Optional Challenge: Design an AI Interface for Your Pipeline

**Optional — do not prioritize this over pipeline development.**

Imagine that your existing pipeline is complete and its analytical tables are available in Redshift.

Describe how you could add an AI-powered interface that allows users to ask questions about the data in ordinary English.

Include:

- Two example questions users might ask.
- The Redshift tables and columns required to answer them.
- How you would provide the schema to Amazon Bedrock.
- How you would validate generated SQL before execution.
- How Streamlit could display both query results and an AI-generated explanation.

A simple architecture diagram or short written explanation is sufficient.

**You do not need to implement this functionality.**

---

### What to Bring to Tomorrow's Class

#### Required

- [ ] Evidence of progress on your existing AWS pipeline.
- [ ] A clear description of your next development steps and current blockers.
- [ ] SQL solutions or draft queries for the four practical exercises.
- [ ] Short answers to the seven conceptual questions.
- [ ] Basic familiarity with Bedrock, window functions, and schema-grounded SQL generation.

#### Optional

- [ ] A proposed AI interface for your own pipeline.
- [ ] Additional SQL queries demonstrating analytical capabilities.

### Evaluation Priorities

| Area | Priority |
|---|---|
| Progress on your existing AWS pipeline | **Highest** |
| Ability to explain and validate your data | High |
| Understanding analytical SQL | High |
| Understanding Bedrock and AI-generated SQL | Moderate |
| Implementing a working AI chatbot | Not required |

#### Final reminder

**The purpose of this assignment is not to build an AI application overnight.**

A useful AI analytics application depends on a reliable underlying data pipeline. If ingestion is broken, transformations are incomplete, or the analytical tables are poorly designed, the AI system will not produce reliable answers.

Continue developing your existing pipeline first. The Bedrock chatbot is a future extension of that work, not a replacement for it.
