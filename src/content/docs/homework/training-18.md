---
title: "Training 18 Homework"
description: "Homework assignment for Training 18: AWS Cloud Fundamentals."
sidebar:
  order: 18
---

:::note
The assignment prompt as given in class. Related notes: [Training 18](/training-notes-site/notes/training-18/).
:::

## Homework - Training 18 (Assignment)

## AWS Big Data Fundamentals — Homework

### Objective
This assignment reviews the major AWS services discussed in class and how they fit together in a modern cloud data architecture. The emphasis is on understanding which AWS service solves which problem and how the services interact.

### Part 1 — Core AWS Concepts
Answer each question in 2–4 sentences.

1. What is an AWS Region? Why might a company choose one region instead of another?
2. What is IAM (Identity and Access Management)?
3. Explain the difference between:
   - IAM user
   - IAM role
   - IAM policy
4. What is a VPC (Virtual Private Cloud)? Why would an organization place resources such as EC2 instances inside a VPC?
5. What does serverless mean? What is the major advantage of serverless services compared with infrastructure that must remain running continuously?

### Part 2 — Storage and Compute
Answer each question in 2–4 sentences.

#### S3
1. What type of storage system is Amazon S3?
2. What is an S3 bucket?
3. Suppose you are designing a medallion architecture using:
   - Bronze
   - Silver
   - Gold

   Describe what type of data belongs in each layer.
4. Describe one way that three S3 buckets could be used to implement this architecture.

#### EC2 and EBS
1. What is Amazon EC2?
2. What problem does EBS (Elastic Block Store) solve for an EC2 instance?
3. Explain why S3 and EBS serve different purposes even though both provide storage.
4. Why might accessing GPU-enabled EC2 instances require additional AWS quota?

### Part 3 — Big Data Processing

#### EMR
1. What does EMR stand for?
2. What AWS infrastructure is normally used underneath an EMR cluster?
3. Give an example of a workload where EMR might make sense.

#### AWS Glue
1. What is AWS Glue?
2. What is a DPU (Data Processing Unit)?
3. Why does Glue allow developers to think less about individual servers or cluster nodes?
4. Consider these two workloads:
   - **Workload A:** Data continuously arrives and must be processed throughout the day.
   - **Workload B:** A large CSV file arrives in S3 once every night and requires 15 minutes of Spark processing.

   Which workload is a more natural candidate for EMR, and which is a more natural candidate for Glue? Explain why.

### Part 4 — Data Warehousing and Databases

#### Redshift
1. What is Amazon Redshift?
2. What does MPP (Massively Parallel Processing) mean?
3. What is the purpose of the Redshift COPY command?
4. Explain one advantage of Redshift Serverless compared with maintaining a continuously running provisioned Redshift cluster.
5. Research question: What similarities exist between Amazon Redshift Serverless and Google BigQuery?

#### RDS
1. What is Amazon RDS?
2. Why might an application running on EC2 use RDS instead of storing its application data directly on the EC2 instance?
3. Name at least three relational database engines available through Amazon RDS.

### Part 5 — Athena, Glue and Schema-on-Read
This section is particularly important because these services are commonly used together.

Answer the following:
1. What is Amazon Athena?
2. Does Athena store the actual data that it queries?
3. Explain schema-on-read in your own words.
4. What does a Glue Crawler do?
5. What information is stored in the Glue Data Catalog?
6. How is the Glue Data Catalog conceptually related to the Hive Metastore?
7. Suppose the following file arrives:

   `S3 → s3://company-bronze/orders/orders.csv`

   Explain how the following components could work together to make this data queryable:

   `S3 → Glue Crawler → Glue Data Catalog → Athena`

### Part 6 — Event-Driven Architecture
Amazon EventBridge allows actions to be triggered when events occur.

Consider this scenario:

A company receives a new sales file in an S3 bucket every evening. When the file arrives, the company wants AWS to automatically begin processing it.

Answer:
1. What role could EventBridge play?
2. What AWS service could process the file without maintaining a continuously running cluster?
3. Where could the processed data be stored?
4. How could Athena later query that data?

### Part 7 — Architecture Challenge
Design a simple AWS data pipeline with the following requirements:

A company receives CSV sales files periodically. The files need to be stored permanently, cleaned with Spark, and made available to analysts through SQL.

Use at least five of the following AWS technologies:

S3, IAM, VPC, EC2, EBS, EMR, Glue, Glue Crawler, Glue Data Catalog, Athena, Redshift, RDS, EventBridge

Draw a simple architecture diagram.

For example, your diagram can use a format such as:

`Source → Service → Service → Storage → Analytics`

Under the diagram, write one short paragraph explaining why you selected those services.

### Part 8 — Short Research
Research Amazon SageMaker and answer the following:
1. What is SageMaker primarily designed to do?
2. How is SageMaker different from AWS Glue?
3. What role can GPUs play in SageMaker?
4. Give one example of an AI or machine-learning workload that would benefit from GPU compute.

### Submission
Submit one document containing:
- Answers to Parts 1–6 and Part 8
- Your architecture diagram for Part 7
- Your explanation of the architecture

Keep answers concise. The objective is not to memorize every AWS feature, but to demonstrate that you understand what each major service does and how AWS services can be combined into a data platform.
