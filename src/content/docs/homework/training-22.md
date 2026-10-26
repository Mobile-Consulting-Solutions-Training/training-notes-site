---
title: "Training 22 Homework"
description: "Homework assignment for Training 22: Warehouse Design and AWS Streaming."
sidebar:
  order: 22
---

:::note
The assignment prompt as given in class. Related notes: [Training 22](/training-notes-site/notes/training-22/).
:::

Homework Assignment: Real-Time Data Engineering with AWS Kinesis, Lambda, Glue, and Aurora
Topic: Streaming Data Pipelines, Schema Management, Database Integration, and Cloud Cost Optimization
Estimated time: 2–3 hours
Submission: Written answers and two short Python/SQL exercises
Total: 100 points
Assignment Overview
In today's class, we developed a real-time data pipeline using New York City's Citi Bike station availability data.
Our architecture was:
AWS Lambda → Amazon Kinesis Data Streams → AWS Glue Streaming → Amazon Aurora PostgreSQL
The Lambda function retrieved station information from an external API and published JSON records to Kinesis. AWS Glue consumed those records using Spark Structured Streaming, transformed them into a consistent schema, and inserted them into Aurora PostgreSQL.
We also encountered several realistic data engineering challenges involving schema inference, IAM permissions, streaming checkpoints, database authentication, and AWS resource costs.
This homework focuses primarily on understanding the architectural decisions and engineering principles behind the pipeline.
You are not required to create AWS resources, deploy a pipeline, or incur any cloud charges.
Part 1: Streaming Architecture and Core Concepts (25 points)
Reading
Read the following AWS documentation:
What is Amazon Kinesis Data Streams?
AWS Lambda Developer Guide
Streaming ETL jobs in AWS Glue
Questions
1. Batch processing versus streaming (5 points)
Explain the difference between batch processing and streaming data processing. Describe one situation where batch processing would be preferable and another where streaming would be preferable.
2. Understanding our architecture (5 points)
Explain the responsibility of each component in our Citi Bike pipeline:
AWS Lambda
Amazon Kinesis Data Streams
AWS Glue Streaming
Amazon Aurora PostgreSQL
3. Producers and consumers (5 points)
In the context of Kinesis, define a producer and a consumer. Identify the producer and consumer in our pipeline.
Can multiple consumers independently process the same Kinesis stream? Explain.
4. Why use Kinesis? (5 points)
Why not simply have the Lambda function insert data directly into PostgreSQL?
Discuss at least three advantages of placing Kinesis between data ingestion and database processing.
5. Data retention and durability (5 points)
Research how Kinesis retains records.
What happens if the Glue consumer stops running for several hours? Can it resume processing records that arrived during that period? Under what conditions might data be lost?
Part 2: AWS Glue, Spark, and Schema Management (25 points)
Reading
AWS Glue streaming connections
Spark Structured Streaming Programming Guide
PySpark JSON Functions
Questions
6. Microbatch processing (5 points)
What is a microbatch?
Our Glue job used a 30-second processing window. Explain how microbatching works and why it can be preferable to processing each individual record separately.
7. Schema inference versus explicit schemas (5 points)
During class, our Glue job repeatedly failed because Spark could not identify columns such as station_id.
Explain the difference between automatic schema inference and explicitly defining a schema.
Why might an explicit schema be preferable in a production streaming pipeline?
8. Understanding a schema failure (5 points)
Our logs contained:
BATCH 0: columns=[]
AnalysisException:
UNRESOLVED_COLUMN.WITHOUT_SUGGESTION
Explain what this error means.
Why was the problem not necessarily caused by malformed JSON in Kinesis?
9. Streaming checkpoints (5 points)
What is a streaming checkpoint?
Explain how checkpoints help a streaming application recover from failures. What problems could arise if a developer deletes a checkpoint and restarts a consumer from the beginning of the stream?
10. Delivery guarantees (5 points)
Research the concepts of:
At-most-once processing
At-least-once processing
Exactly-once processing
Explain the differences.
Our Glue job inserted records into PostgreSQL using ordinary SQL INSERT statements. What could happen if a batch was successfully inserted but the streaming job failed before its checkpoint was committed?
Part 3: Databases, Security, and Cloud Operations (20 points)
Reading
Amazon Aurora User Guide
IAM database authentication
AWS IAM roles
AWS Cost Explorer
Questions
11. Aurora versus standard PostgreSQL (5 points)
What is Amazon Aurora?
Explain how Aurora differs from running PostgreSQL on your own EC2 instance. Discuss at least two benefits and one potential disadvantage.
12. IAM authentication (5 points)
Our Glue job generated a temporary IAM database authentication token rather than storing a permanent database password in the Python script.
Explain how this improves security.
What IAM and database permissions are necessary for this approach to work?
13. Continuous resource costs (5 points)
Compare the billing behavior of the following AWS services:
Lambda
Kinesis Data Streams
AWS Glue Streaming
Aurora Serverless
Redshift Serverless
Which resources might continue generating charges even when no new data is arriving?
14. Operational troubleshooting (5 points)
Imagine your streaming pipeline successfully processed 2,500 records, but no additional records appear in PostgreSQL.
Describe how you would determine whether:
The Lambda function stopped executing.
Kinesis stopped receiving records.
Glue stopped consuming records.
Aurora rejected database writes.
Identify at least one AWS diagnostic tool or metric for each stage.
Part 4: Short Coding Exercises (20 points)
These exercises can be completed locally. No AWS account is required.
Exercise 1: Python JSON Processing (10 points)
Consider the following Kinesis record:
record = {
    "station_id": "0ddb965d-95ef-4ce3-bde6-81a56ac1fbd2",
    "num_bikes_available": 11,
    "num_docks_available": 16,
    "last_reported": 1791833794,
    "ingested_at": "2026-10-12T19:39:03.312735+00:00"
}
Write a Python function named transform_station(record) that:
Extracts the station ID.
Extracts the number of available bikes and docks.
Calculates the total station capacity as the sum of available bikes and docks.
Calculates the percentage of available capacity occupied by bikes.
Returns the results as a dictionary.
Handles the case where the calculated capacity is zero without raising a division-by-zero exception.
Expected output for this example:
{
    "station_id": "0ddb965d-95ef-4ce3-bde6-81a56ac1fbd2",
    "capacity": 27,
    "bike_percentage": 40.74
}
Round the percentage to two decimal places.
Exercise 2: PostgreSQL Analytical SQL (10 points)
Assume our Aurora database contains the following table:
CREATE TABLE station_stream (
    station_id VARCHAR(100),
    num_bikes_available INTEGER,
    num_docks_available INTEGER,
    last_reported BIGINT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Write SQL queries to answer these questions:
A. How many total records have been inserted into the table?
B. How many distinct stations appear in the data?
C. What is the average number of available bikes across all recorded observations?
D. Which five stations have the highest average number of available bikes?
E. For each station, retrieve only its most recent observation, using last_reported to determine which observation is newest. Use a window function.
Part 5: Architecture and Design Challenge (10 points)
Scenario
A city transportation agency wants to monitor 10,000 bicycle stations across multiple cities. Each station sends updated availability information every 30 seconds.
The agency wants:
Near-real-time dashboards
Historical trend analysis
Reliable processing during temporary database outages
Minimal duplicate records
Reasonable operating costs
15. Design a scalable solution (10 points)
Write approximately 300–500 words describing how you would design this system.
Address the following:
Would you use Kinesis, and why?
Would you continue using Lambda for ingestion?
How would you organize the streaming processing layer?
Would you store all historical observations in PostgreSQL, S3, or both?
How would you prevent duplicate observations?
How would you handle database outages?
What would you monitor to detect problems?
How would you control AWS costs?
You may use a simple architecture diagram, but it is optional.
Submission Requirements
Submit one document containing:
Answers to Questions 1–15.
Python code for Exercise 1.
SQL queries for Exercise 2.
A 300–500-word architectural design response for Part 5.
Grading criteria:
Category    Points
Streaming architecture and fundamentals    25
Spark, Glue, and schema management    25
Databases, security, and operations    20
Python and SQL exercises    20
Architecture design challenge    10
Total    100
Learning Objectives
By completing this assignment, you should be able to explain how streaming pipelines differ from batch pipelines, identify the responsibilities of producers and consumers, understand the importance of explicit schemas and checkpoints, reason about delivery guarantees, and evaluate the operational and financial tradeoffs of cloud-based streaming architectures.
The emphasis is on understanding why the architecture works and how to troubleshoot it, rather than simply reproducing the AWS configuration demonstrated in class.
