---
title: "Training 30 Homework"
description: "Homework assignment for Training 30: Delta Lake, Auto Loader and MLflow."
sidebar:
  order: 30
---

:::note
The assignment prompt as given in class. Related notes: [Training 30](/training-notes-site/notes/training-30/).
:::

## Homework Assignment — Databricks & MLflow

Training 30 (Thu Oct 22, 2026). Teacher: Evan Flint.

**Topics:** Delta Lake, Auto Loader, Lakeflow Jobs, MLflow
**Estimated technical homework time:** 45–60 minutes
**Main priority:** Professional profile narratives

---

### Part 1 — Professional Profile Narratives (Main Assignment)

Your primary assignment is to continue developing and refining your professional profiles in preparation for technical interviews.

Focus on the following:

- **Professional Summary:** Prepare a clear, natural introduction describing your data engineering experience, technical strengths, and areas of specialization.
- **Project Narratives:** Develop or improve at least two detailed project stories, including:
  - Business problem and project objective
  - Architecture and technology stack
  - Your specific responsibilities and technical contributions
  - Challenges encountered and how you addressed them
  - Business impact and measurable results, where available
- **Interview Readiness:** Practice explaining each project conversationally, without simply reciting your resume.

**Deliverable:** Updated professional summary and two project narratives. Be prepared to present and discuss them in class.

Your narratives should accurately reflect your experience and be detailed enough to support technical follow-up questions.

---

### Part 2 — Databricks Reading (15–20 Minutes)

Review the following topics using Databricks documentation or other reliable technical resources.

#### 1. Delta Lake

- What is Delta Lake, and how does it differ from ordinary Parquet storage?
- What is Delta Lake Time Travel?
- What is the difference between `RESTORE`, `MERGE`, and `VACUUM`?

#### 2. Auto Loader

- What problem does Auto Loader solve?
- What is the purpose of `cloudFiles`?
- Why are checkpoints important for incremental ingestion?

#### 3. Lakeflow Jobs

- What is a Databricks Job?
- How do task dependencies work?
- What happens to downstream tasks when an upstream task fails?

Suggested reading: Delta Lake documentation, Auto Loader documentation, Lakeflow Jobs documentation.

---

### Part 3 — MLflow Reading (10–15 Minutes)

Review the following concepts:

- What is MLflow, and why is it useful?
- What is the difference between an MLflow experiment and a run?
- What are parameters, metrics, and artifacts?
- What is the purpose of the MLflow Model Registry?
- How does Databricks integrate MLflow into its workspace?

Suggested reading: MLflow Tracking, MLflow on Azure Databricks.

---

### Part 4 — Short Technical Exercises (15–20 Minutes)

Complete the following four exercises. Brief written answers or code snippets are sufficient.

#### Exercise 1 — Delta Lake Time Travel

Suppose a Delta table named `orders` has three versions:

| Version | Change |
|---|---|
| 0 | Original data |
| 1 | Updated customer records |
| 2 | Accidental deletion of several records |

Write SQL statements to:

1. Query the data as it existed in Version 1.
2. Restore the table to Version 1.

#### Exercise 2 — Auto Loader

Review the following code:

```python
df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .load("/Volumes/catalog/schema/landing/")
)
```

Answer:

1. What does `cloudFiles` do?
2. What would happen if 100 new JSON files arrived in the landing directory?
3. Why should the streaming write use a checkpoint?

#### Exercise 3 — Lakeflow Jobs

A Databricks Job has the following tasks:

```
Bronze Ingestion
      |
      v
Silver Transformation
      |
      v
Gold Aggregation
```

Answer:

1. What happens if the Silver task fails?
2. Why should Gold depend on Silver?
3. Name one reason a failed task might succeed when retried.

#### Exercise 4 — MLflow

Consider this code:

```python
import mlflow

with mlflow.start_run():
    mlflow.log_param("max_depth", 5)
    mlflow.log_metric("accuracy", 0.92)
```

Answer:

1. What does `start_run()` do?
2. Is `max_depth` a parameter or a metric?
3. What does the value `0.92` represent?
4. Where can you view this information in Databricks?

---

### Part 5 — Optional Hands-on Practice

For students who have additional time:

1. Open your Databricks workspace.
2. Create a Python notebook.
3. Create an MLflow experiment.
4. Log a sample parameter and metric.
5. Locate the experiment in the Databricks MLflow UI.

You do not need to train a machine learning model for this assignment.

---

### Submission Expectations

**Required:**

- Updated professional summary
- Two improved project narratives
- Short answers to the four technical exercises

**Optional:**

- MLflow experiment demonstration

**Priority:** Spend most of your available preparation time on your professional profiles and project narratives. The Databricks and MLflow exercises are intended to reinforce today's lessons, not to become a major project.

Be prepared to explain your project architecture, technical decisions, and personal contributions during the next class.
