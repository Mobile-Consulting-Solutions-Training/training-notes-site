---
title: "Training 21 Homework"
description: "Homework assignment for Training 21: Cloud Networking for Glue and Redshift."
sidebar:
  order: 21
---

:::note
The assignment prompt as given in class. Related notes: [Training 21](/training-notes-site/notes/training-21/).
:::

## Homework - Training 21 (Assignment)

**Class:** Training 21 (Day 22, Fri Oct 9 2026) · **Due:** next class (Mon Oct 12)

Evan, in class:

> I don't want to unnecessarily stress you guys out, and I know that you've already got a lot on your plate. Not all of you are at the point that I am at. And so basically your homework is going to be to try and get as close to where I've gotten to as possible. And since you all now have EventBridge permissions, you can run the ingestion pipeline over the weekend and enrich the data that you're working with. That would be a useful thing for you to be able to do as well.

Where Evan got to: Bronze (Lambda + EventBridge every 5 min) → Silver (Glue) → Redshift `public.citibike_station_snapshot` (Glue job via Glue connection, VPC S3 endpoint) → Gold star schema (`gold.dim_station`, `gold.dim_date`, `gold.fact_station_snapshot`) → validation queries → analytical queries.

Reference: the six ChatGPT session links Evan posted in the Teams chat (main pipeline lesson, SQL design patterns, TRUNCATE etc., dim-before-fact, IAM permissions, networking).

### Official wording

> Homework for the weekend is to develop the pipeline that you have built on your side to the full extent that it was in class: you should have the ingestion job able to run in Lambda, which will get the data into S3; EMR and Glue jobs to get the data from bronze to silver, then silver to gold. [Transcript unclear: "if you only do this in [one of them], you don't need to do it in both."] Then once it's in gold, make sure that it's in a star schema, and then do some basic analytical queries on it in order to answer natural-language questions about what the data can tell us. Basically, make it so that on your side it looks like it does on my side.

Checklist:
1. Ingestion job running in **Lambda** → **S3** Bronze (scheduled with EventBridge; run it over the weekend to collect more data)
2. **Bronze → Silver** with EMR Serverless *or* Glue (you don't need both)
3. **Silver → Gold** in Redshift
4. Gold organized as a **star schema** (dimension + fact tables)
5. **Analytical queries** answering natural-language questions about the data
