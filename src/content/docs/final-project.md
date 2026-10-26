---
title: Final Project
description: Everything for the final-project presentation in one place - requirements, choosing a dataset, architecture options, a slide outline, and a checklist.
tableOfContents:
  maxHeadingLevel: 2
---

Each student designs and builds an original data pipeline on their own dataset, then presents it to company management. These are the requirements from class, plus a slide outline and checklist to work from.

:::caution[Check the date with Evan]
The presentation date wasn't final as of Training 31 (Fri Oct 23). Evan was confirming it with the program coordinator; the latest guidance was to be ready to present on **Monday**. AWS permissions were also revoked company-wide at that point, so if you're blocked on AWS you may switch your project to Azure.
:::

## Requirements

From [Training 27](/training-notes-site/notes/training-27/) and [Training 28](/training-notes-site/notes/training-28/):

| Requirement | What Evan said |
|---|---|
| **Your own data** | Not the Citi Bike data everyone already used. Find a source, investigate it, analyze it, and work out the code it needs |
| **Real and bigger** | Real data, not a generated CSV. Bigger is better: gigabytes, not kilobytes (see the size guide below) |
| **Platform** | AWS, Azure, or multi-cloud, whichever suits your data. AWS-only is fine if you're behind on Azure |
| **Architecture** | A multi-layer lakehouse: **Bronze, Silver and Gold** |
| **Core content** | The pipeline itself: **ingestion**, **processing**, **storage**, and the **analytics** that answer your main question |
| **Audience** | Company management, "who are not necessarily technical" |
| **Style** | "More of a research pitch rather than a developer pitch." Open with a **high concept**, e.g. weather patterns that could affect a company's shipments |
| **Length** | About 5 to 10 minutes; longer is fine if it's good information |
| **Deliverables** | The working pipeline plus a slide presentation (PowerPoint or any slideshow tool) |

## Choosing a dataset

| Size | Evan's take |
|---|---|
| 40 KB CSV | Good for learning the ropes, too small for the project |
| ~200 MB (e.g. MovieLens 32M ratings) | "Not even big data", but hundreds of MB is a start |
| **5–10 GB** | The target. About 5 GB is ideal for a live demo: minutes of processing, not hours |
| Hundreds of GB to TB | What production looks like |

**Where to look:** [Kaggle](https://www.kaggle.com/datasets) (free account), NYC TLC taxi trip records (big, and pairs well with Citi Bike), public APIs that update often (good for showing incremental loads), and government open-data portals.

**Ideas students raised in class:** unemployment vs assistance-program data with a lag analysis, MovieLens ratings, theme-park wait times, open-source dependency risk, retail transactions.

**Pick data that answers a question.** The high concept comes first ("which neighborhoods are under-served by bike docks at rush hour?"), then the data that can answer it.

## Architecture options

Reuse what you built in class. The [pipeline diagrams](/training-notes-site/reference/pipeline-diagrams/) show each one end to end.

| Layer | AWS (Trainings 19–26) | Azure (Trainings 27–31) |
|---|---|---|
| Ingestion | Lambda on an EventBridge schedule, or Kinesis for streams | Data Factory Copy activity, or Event Hubs for streams |
| Bronze | S3, raw files as received | ADLS Gen2 `bronze` container |
| Processing | Glue (PySpark) | Databricks notebooks, Auto Loader |
| Silver | S3 Parquet | Delta tables |
| Gold | Redshift star schema | Delta Gold tables, Synapse serverless SQL |
| Orchestration | Step Functions, Terraform | Lakeflow Jobs or Data Factory |
| Analytics | Streamlit, Bedrock text-to-SQL | Power BI, Databricks charts |

Show at least one thing beyond a straight copy: incremental loading with a checkpoint, data-quality checks in Silver, a star schema in Gold, or orchestration that runs on a schedule.

## Suggested slide outline

About 8–10 slides for a 10-minute talk:

| # | Slide | Time | What to say |
|---|---|---|---|
| 1 | **The question** | 1 min | The high concept in one sentence, and why the business cares |
| 2 | **The data** | 1 min | Source, size, how often it updates, what one record looks like |
| 3 | **Architecture** | 1.5 min | One diagram, left to right: ingestion → Bronze → Silver → Gold → analytics |
| 4 | **Ingestion and Bronze** | 1 min | How data arrives and lands raw, and why you keep it raw |
| 5 | **Silver** | 1 min | The cleaning: types, nulls, duplicates, and how many rows each rule removed |
| 6 | **Gold** | 1 min | The tables shaped for the question (aggregates, star schema) |
| 7 | **The answer** | 1.5 min | The charts and what they mean for the business. This is what management remembers |
| 8 | **Problems and fixes** | 1 min | One or two real problems you hit and how you solved them. Interviewers love these too |
| 9 | **What's next** | 0.5 min | How it would scale, or what you'd add with more time |

Tips for a non-technical audience: lead with the answer, not the tools; one idea per slide; name a tool only when you say what it does ("Glue, which cleans the data"); show numbers they can feel ("2.5 million readings a week").

## Checklist

**Build**
- [ ] Dataset chosen, size checked, question written down
- [ ] Bronze: raw data landing automatically or with one command
- [ ] Silver: cleaning rules, with row counts before and after
- [ ] Gold: tables that answer the question
- [ ] At least one chart or dashboard
- [ ] Re-run it once end to end and confirm it doesn't duplicate data (idempotent)
- [ ] Screenshots of each stage, in case the live demo fails

**Present**
- [ ] Slides follow the outline above
- [ ] The architecture diagram fits on one slide
- [ ] One real problem-and-fix story
- [ ] Timed run-through under 10 minutes
- [ ] Ready for "why did you choose X over Y?" for each tool

## Questions to expect

| Question | Have ready |
|---|---|
| Why this dataset? | The business question it answers |
| Why this platform / tool? | One reason per tool, e.g. "Databricks because Auto Loader handles new files incrementally" |
| How would it handle 100× the data? | Partitioning, incremental loads, scaling the compute (Glue workers, cluster size) |
| What happens if a run fails halfway? | Checkpoints, idempotent loads (MERGE), retries in the orchestrator |
| How do you know the data is right? | Silver validation rules and row-count checks between layers |
| What would you do next? | Scheduling, alerts, more sources, a dashboard for the business |

The same project is your best interview story: see [Interview Prep](/training-notes-site/reference/interview-prep/).
