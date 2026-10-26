---
title: "Training 11 Homework"
description: "Homework assignment for Training 11: Postgres to Hive with Scala Spark."
sidebar:
  order: 11
---

:::note
The assignment prompt as given in class. Related notes: [Training 11](/training-notes-site/notes/training-11/).
:::

Your homework is to:

If your postgres -> hive pipeline is not working right now, make it fully functional
Fix the issue with deduplication - you should be able to run generate_sales.py, then run the spark job, then select from the silver table in Hive, and note that the row count has increased AND that no duplicate records have been added
