---
title: Course Roadmap
description: 45-day syllabus mapped to Training N.md notes files
---

Course Roadmap (source: notes/slides/Data_Engineering_Student_Syllabus.pdf)

Note: file numbering offset - "Training 0.md" (the first session) already covered the syllabus's Day 1 content. So Training N.md corresponds to Syllabus Day (N+1).

| Training File | Syllabus Day | Topic | Coverage |
|---|---|---|---|
| Training 0.md | Day 1 | Data Engineering Fundamentals | Data lifecycle, ETL/ELT, batch vs streaming, OLTP/OLAP, data lake/warehouse, idempotency, error handling |
| Training 1.md | Day 2 | Linux & Shell Scripting | Filesystem, permissions, grep/awk/sed, processes, cron, shell automation and operational logs |
| Training 2.md | Day 3 | Python + Pandas | Functions, exceptions, logging, file I/O, JSON/CSV, DataFrames, filtering, joins, and small ETL |
| Training 3.md | Day 4 | Git Workflow | Branching, commits, PRs, merge conflicts, code review, repository discipline and release basics |
| Training 4.md | Day 5 | CI/CD for Data Eng. | Build/test/deploy flow, pipeline YAML, PR validation, environments, secrets, rollback and patterns |
| Training 5.md | Day 6 | SQL Fundamentals | Joins, aggregations, CTEs, window functions, subqueries, query plans, indexing and interview prep |
| Training 6.md | Day 7 | Data Warehouse Concepts | Facts, dimensions, grain, surrogate keys, SCD1/SCD2, star/snowflake schemas, and medallion architecture |
| Training 7.md | Day 8 | Distributed Systems + HDFS | Horizontal scaling, fault tolerance, CAP basics, HDFS blocks/replication, NameNode/DataNode concepts |
| Training 8.md | Day 9 | Hive + Spark Intro | Metastore, tables, partitioning, Parquet/ORC, Hadoop-to-Spark evolution, Spark driver/executors/DAG |
| Training 9.md | Day 10 | Spark Advanced | Execution plans, transformations, joins, shuffle, caching, skew, optimization and performance tuning |
| Training 10.md | Day 11 | Scala Fundamentals | val/var, functions, collections, functional concepts and reading Spark-oriented Scala code |
| Training 11.md | Day 12 | Scala Advanced | Deep dive into advanced Scala constructs and their application in data engineering workloads |
| Training 12.md | Day 13 | Incremental Loads & Spark Scala | Collections with Spark patterns, incremental patterns, watermarks, CDC, MERGE and upsert operations |
| Training 13.md | Day 14 | Kafka + Lab | Brokers, topics, partitions, offsets, producer/consumer implementation, retries, and troubleshooting |
| Training 14.md | Day 15 | MongoDB + Spark Streaming | Document model, indexing basics, Spark streaming integration and semi-structured data patterns |
| Training 15.md | Day 16 | Spark Structured Streaming | Micro-batch, windowing, stateful processing, checkpoints, late data handling and Kafka integration |
| Training 16.md | Day 17 | Snowflake Introduction | Architecture, virtual warehouses, storage/compute separation, caching, Time Travel and cloning |
| Training 17.md | Day 18 | Snowflake Advanced | RBAC, masking, row access, performance tuning, pruning, clustering, sizing and cost controls |
| Training 18.md | Day 19 | dbt (Data Build Tool) | Sources, models, DAG, materializations, tests, incremental models, snapshots, docs and lineage |
| Training 19.md | Day 20 | AWS Intro + IAM + S3 | Regions, IAM users/roles/policies, least privilege, S3 versioning, lifecycle, and data-lake patterns |
| Training 20.md | Day 21 | EC2 + Lambda | Compute basics, security groups, serverless event-driven processing, triggers, retries, and logging |
| Training 21.md | Day 22 | AWS Glue | Glue crawlers, catalog, jobs, Spark ETL integration, schema handling, and job bookmarks |
| Training 22.md | Day 23 | EMR + Redshift Intro | EMR architecture, operational patterns; Redshift architecture, COPY, distribution/sort strategies |
| Training 23.md | Day 24 | Redshift + Kinesis + RDS | Warehouse optimization, streaming ingestion with Kinesis, and relational-source patterns with RDS |
| Training 24.md | Day 25 | Step Functions + DMS | Workflow orchestration, state machines, retries; database migration, replication, and CDC patterns |
| Training 25.md | Day 26 | Terraform (IaC) | Infrastructure as Code, providers, resources, state, reusable modules, and deployment controls |
| Training 26.md | Day 27 | Apache Airflow | DAGs, operators, dependencies, sensors, XCom, retries, catchup, backfill and failure handling |
| Training 27.md | Day 28 | Azure Entra ID + ADLS Gen2 | Azure identity/RBAC, storage accounts, hierarchical namespaces, security, and data-lake patterns |
| Training 28.md | Day 29 | Databricks Intro | Workspace/compute, Spark integration, jobs, notebooks, Delta fundamentals, medallion architecture |
| Training 29.md | Day 30 | Databricks Advanced | Delta MERGE, schema enforcement/evolution, optimization, performance, cost, and security patterns |
| Training 30.md | Day 31 | ADF + Unity Catalog | ADF pipelines, activities, triggers plus Databricks governance concepts, catalogs, schemas, lineage |
| Training 31.md | Day 32 | Microsoft Fabric (Day 1) | OneLake, Lakehouse, Data Warehouse, Data Factory and overall Fabric architecture breakdown |
| Training 32.md | Day 33 | Microsoft Fabric (Day 2) | Direct Lake, mirroring, governance/integration patterns and deep hands-on application |
| Training 33.md | Day 34 | Synapse + Event Hubs | Synapse serverless/dedicated/Spark concepts plus Azure streaming/event ingestion with Event Hubs |
| Training 34.md | Day 35 | Presentation | Trainee presentations and review of architectural concepts covered throughout the core platform weeks |
| Training 35.md | Day 36 | GCP: BigQuery + Pub/Sub | Cloud Storage, BigQuery architecture, partitioning, clustering, Pub/Sub topics and streaming patterns |
| Training 36.md | Day 37 | Dataflow + Dataproc | Apache Beam pipelines, transforms; Dataproc Spark/Hadoop and service-selection comparison |
| Training 37.md | Day 38 | ML Fundamentals & MLFlow | ML lifecycle, features/labels, train/test, MLFlow experiments, runs, metrics, and model registry |
| Training 38.md | Day 39 | RAG & Vector Data Eng. | Chunking, embeddings, vector stores, ingestion pipelines, metadata, lineage, and retrieval architecture |
| Training 39.md | Day 40 | Production Break/Fix | Deliberately break pipelines, detect incidents, diagnose root causes, recover, and document RCAs |
| Training 40.md | Day 41 | Open Table Formats & Contracts | Iceberg/Hudi concepts, ACID, schema evolution, data catalogs, PII, and producer-consumer contracts |
| Training 41.md | Day 42 | Data Mesh & MDM | Domain ownership, data products, hubs-links-satellites, golden records, and architecture awareness |
| Training 42.md | Day 43 | Kubernetes for Data Eng. | Containers, pods, deployments, services, and where Kubernetes appears in managed data platforms |
| Training 43.md | Day 44 | Flexible Extension | Time reserved for advanced mock interviews, specific topic review, and technical interview preparation |
| Training 44.md | Day 45 | Marketing Readiness | Final preparations for the job market, resume review, behavioral alignment, and graduation activities |

## Week Breakdown
- Week 1 (Days 1-5): Engineering Foundations
- Week 2 (Days 6-10): SQL & Distributed Systems
- Week 3 (Days 11-15): Scala & Streaming
- Week 4 (Days 16-20): Streaming, Snowflake & dbt
- Week 5 (Days 21-25): AWS Data Engineering
- Week 6 (Days 26-30): Platform Engineering & Databricks
- Week 7 (Days 31-35): Azure Analytics & Microsoft Fabric
- Week 8 (Days 36-40): GCP, ML & AI-Ready Data Eng.
- Week 9 (Days 41-45): Modern Architecture & Readiness
