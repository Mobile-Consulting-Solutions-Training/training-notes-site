---
title: Cloud Services Compared
description: AWS vs Azure vs GCP vs Databricks and open source, one row per job, linked to the day each was covered.
sidebar:
  order: 3
---

The same jobs show up on every cloud under different names. Each row below is one job in a data pipeline, with the service that does it on each platform. The **Class** column links to the days where it came up. The services marked **bold** are the ones the course used hands-on.

A map like this is a memory aid, not a one-to-one match: equivalents differ in features, pricing and limits. When an interviewer asks "have you used X?", the best answer names the equivalent you *did* use and the difference that matters.

## Storage and data lake

| Job | AWS | Azure | GCP | Databricks / open source | Class |
|---|---|---|---|---|---|
| Object storage (the data lake) | **S3** | **ADLS Gen2** (Blob Storage + hierarchical namespace) | Cloud Storage (GCS) | HDFS (on-prem) | [6](/training-notes-site/notes/training-6/), [18](/training-notes-site/notes/training-18/), [19](/training-notes-site/notes/training-19/), [27](/training-notes-site/notes/training-27/), [28](/training-notes-site/notes/training-28/) |
| Table format on the lake | Iceberg (S3 Tables, Glue) | Delta (Fabric OneLake) | Iceberg (BigLake) | **Delta Lake**, Iceberg, Hudi | [5](/training-notes-site/notes/training-5/), [27](/training-notes-site/notes/training-27/), [30](/training-notes-site/notes/training-30/) |
| Metadata catalog | Glue Data Catalog | Unity Catalog, Purview | Dataplex / BigLake metastore | **Unity Catalog**, Hive metastore | [8](/training-notes-site/notes/training-8/), [18](/training-notes-site/notes/training-18/), [27](/training-notes-site/notes/training-27/), [28](/training-notes-site/notes/training-28/) |
| Governance (permissions, lineage, masking) | Lake Formation | Purview, Unity Catalog | Dataplex, policy tags | **Unity Catalog** | [27](/training-notes-site/notes/training-27/), [29](/training-notes-site/notes/training-29/), [30](/training-notes-site/notes/training-30/) |
| Path you give Spark | `s3://` (`s3a://` on open-source Hadoop) | `abfss://<container>@<account>.dfs.core.windows.net/` | `gs://` | `/Volumes/<catalog>/<schema>/<volume>/` | [27](/training-notes-site/notes/training-27/), [28](/training-notes-site/notes/training-28/) |

## Compute and processing

| Job | AWS | Azure | GCP | Databricks / open source | Class |
|---|---|---|---|---|---|
| Virtual machine | **EC2** | Virtual Machines | Compute Engine | — | [18](/training-notes-site/notes/training-18/), [24](/training-notes-site/notes/training-24/) |
| Serverless functions | **Lambda** | Functions | Cloud Run functions | — | [19](/training-notes-site/notes/training-19/), [22](/training-notes-site/notes/training-22/), [26](/training-notes-site/notes/training-26/) |
| Containers | ECS / Fargate, EKS, **ECR** (registry) | Container Apps, AKS, ACR | Cloud Run, GKE, Artifact Registry | **Docker**, Kubernetes | [3](/training-notes-site/notes/training-3/), [19](/training-notes-site/notes/training-19/) |
| Batch Spark (managed) | **Glue**, **EMR** / EMR Serverless | **Azure Databricks**, Synapse Spark pools | Dataproc | **Databricks**, Apache Spark | [7](/training-notes-site/notes/training-7/), [20](/training-notes-site/notes/training-20/), [22](/training-notes-site/notes/training-22/), [28](/training-notes-site/notes/training-28/) |
| SQL transformations (ELT) | Redshift SQL, Glue | Databricks SQL, Synapse | BigQuery SQL, Dataform | **dbt**, Lakeflow Declarative Pipelines | [15](/training-notes-site/notes/training-15/), [17](/training-notes-site/notes/training-17/), [29](/training-notes-site/notes/training-29/) |
| Low-code / visual ETL | Glue Studio | **Data Factory** (Data Flows) | Cloud Data Fusion | — | [28](/training-notes-site/notes/training-28/) |

## Streaming

| Job | AWS | Azure | GCP | Databricks / open source | Class |
|---|---|---|---|---|---|
| Event stream (log of messages) | **Kinesis Data Streams**, MSK (managed Kafka) | **Event Hubs** (Kafka endpoint) | Pub/Sub | **Kafka** | [12](/training-notes-site/notes/training-12/), [13](/training-notes-site/notes/training-13/), [22](/training-notes-site/notes/training-22/), [31](/training-notes-site/notes/training-31/) |
| Stream processing | **Glue streaming**, Managed Service for Apache Flink | Stream Analytics, Databricks | Dataflow (Apache Beam) | **Flink**, **Spark Structured Streaming** | [13](/training-notes-site/notes/training-13/), [14](/training-notes-site/notes/training-14/), [22](/training-notes-site/notes/training-22/) |
| Incremental file ingestion | Glue job bookmarks | Databricks Auto Loader | — | **Auto Loader** (`cloudFiles`) | [20](/training-notes-site/notes/training-20/), [29](/training-notes-site/notes/training-29/), [30](/training-notes-site/notes/training-30/) |
| Change data capture / migration | **DMS** | Database Migration Service | Datastream, Database Migration Service | Debezium | [24](/training-notes-site/notes/training-24/), [28](/training-notes-site/notes/training-28/), [30](/training-notes-site/notes/training-30/) |

## Orchestration and scheduling

| Job | AWS | Azure | GCP | Databricks / open source | Class |
|---|---|---|---|---|---|
| Workflow orchestration | **Step Functions**, MWAA (managed Airflow) | **Data Factory** | Cloud Composer (managed Airflow), Workflows | **Lakeflow Jobs**, Airflow | [23](/training-notes-site/notes/training-23/), [24](/training-notes-site/notes/training-24/), [28](/training-notes-site/notes/training-28/), [30](/training-notes-site/notes/training-30/) |
| Schedules and event triggers | **EventBridge** (Scheduler, rules) | Data Factory triggers, Event Grid | Cloud Scheduler, Eventarc | Job triggers (schedule, file arrival) | [19](/training-notes-site/notes/training-19/), [24](/training-notes-site/notes/training-24/), [30](/training-notes-site/notes/training-30/) |
| Infrastructure as code | CloudFormation, CDK | Bicep / ARM templates | Deployment Manager | **Terraform** | [23](/training-notes-site/notes/training-23/), [24](/training-notes-site/notes/training-24/), [26](/training-notes-site/notes/training-26/) |

## Warehouses and databases

| Job | AWS | Azure | GCP | Databricks / open source | Class |
|---|---|---|---|---|---|
| Cloud data warehouse | **Redshift** (Serverless) | **Synapse** dedicated SQL pools, Fabric Warehouse | BigQuery | Databricks SQL warehouses, **Snowflake** | [15](/training-notes-site/notes/training-15/), [16](/training-notes-site/notes/training-16/), [20](/training-notes-site/notes/training-20/), [21](/training-notes-site/notes/training-21/), [31](/training-notes-site/notes/training-31/) |
| SQL directly on lake files | Athena, Redshift Spectrum | Synapse **serverless SQL** | BigQuery external tables | Databricks SQL, Trino | [18](/training-notes-site/notes/training-18/), [31](/training-notes-site/notes/training-31/) |
| Relational (OLTP) database | **RDS / Aurora** PostgreSQL | Azure Database for PostgreSQL, Azure SQL | Cloud SQL, AlloyDB | **PostgreSQL** | [4](/training-notes-site/notes/training-4/), [9](/training-notes-site/notes/training-9/), [22](/training-notes-site/notes/training-22/) |
| NoSQL document / key-value | DynamoDB, DocumentDB | Cosmos DB | Firestore, Bigtable | **MongoDB** | [13](/training-notes-site/notes/training-13/), [18](/training-notes-site/notes/training-18/) |
| Search and log analytics | **OpenSearch** | Azure AI Search | — | **Elasticsearch** (ELK) | [29](/training-notes-site/notes/training-29/) |

## Security and operations

| Job | AWS | Azure | GCP | Databricks / open source | Class |
|---|---|---|---|---|---|
| Identity and sign-in | **IAM**, IAM Identity Center | **Entra ID** | Cloud IAM, Cloud Identity | Databricks account users and groups | [18](/training-notes-site/notes/training-18/), [27](/training-notes-site/notes/training-27/) |
| Permissions | **IAM policies** (identity + resource policies) | **Azure RBAC** role assignments | IAM roles | Unity Catalog `GRANT`s | [18](/training-notes-site/notes/training-18/), [20](/training-notes-site/notes/training-20/), [27](/training-notes-site/notes/training-27/), [28](/training-notes-site/notes/training-28/) |
| Identity for a service (no keys) | **IAM role** | **Managed identity** | Service account | Access Connector (Azure) | [19](/training-notes-site/notes/training-19/), [27](/training-notes-site/notes/training-27/), [28](/training-notes-site/notes/training-28/) |
| Secrets | **Secrets Manager** | Key Vault | Secret Manager | Databricks secret scopes | [21](/training-notes-site/notes/training-21/) |
| Private network | **VPC**, subnets, security groups | VNet, subnets, NSGs | VPC | — | [18](/training-notes-site/notes/training-18/), [21](/training-notes-site/notes/training-21/) |
| Logs and metrics | **CloudWatch** | Azure Monitor, Log Analytics | Cloud Logging / Monitoring | Datadog, ELK | [20](/training-notes-site/notes/training-20/), [22](/training-notes-site/notes/training-22/), [30](/training-notes-site/notes/training-30/) |
| Resource grouping | Account, tags, CloudFormation stack | Subscription, **resource group** | Project | Workspace | [27](/training-notes-site/notes/training-27/) |

## Analytics and AI

| Job | AWS | Azure | GCP | Databricks / open source | Class |
|---|---|---|---|---|---|
| BI dashboards | QuickSight | **Power BI** | Looker, Looker Studio | **Streamlit**, Tableau | [19](/training-notes-site/notes/training-19/), [24](/training-notes-site/notes/training-24/), [27](/training-notes-site/notes/training-27/) |
| Hosted LLMs | **Bedrock** | Azure OpenAI / AI Foundry | Vertex AI (Gemini) | Ollama (local), Hugging Face | [25](/training-notes-site/notes/training-25/) |
| Vector store for RAG | **S3 Vectors**, OpenSearch | Azure AI Search | Vertex AI Vector Search | pgvector, Databricks Vector Search | [25](/training-notes-site/notes/training-25/), [30](/training-notes-site/notes/training-30/) |
| ML lifecycle | SageMaker | Azure Machine Learning | Vertex AI | **MLflow** | [30](/training-notes-site/notes/training-30/) |
| All-in-one analytics platform | — | **Microsoft Fabric** | — | Databricks, Snowflake, Palantir Foundry | [27](/training-notes-site/notes/training-27/) |

---

## Pairs people mix up

| Pair | The difference |
|---|---|
| IAM vs Entra ID | AWS IAM does identity *and* permissions. Azure splits them: Entra ID says who you are, RBAC says what you can do |
| IAM role vs managed identity | The same idea: an identity a service uses with temporary credentials, so no keys in code |
| AWS account vs Azure subscription vs GCP project | All three are the billing and access boundary that resources live in |
| Resource group vs VPC | A resource group is a management folder (delete it to delete everything inside). The Azure VPC is a VNet |
| Kinesis vs Kafka vs Event Hubs | All are partitioned event logs. Kinesis uses **shards**, Kafka and Event Hubs use **partitions**. Event Hubs accepts Kafka clients |
| Glue vs EMR vs Databricks | All run Spark. Glue is serverless and AWS-only, EMR gives you the cluster, Databricks adds notebooks, Delta, Unity Catalog and jobs on any cloud |
| Step Functions vs Data Factory vs Airflow | All orchestrate. Data Factory also copies data (Copy activity); Airflow is code-first Python DAGs |
| Redshift vs Synapse vs BigQuery vs Snowflake | All are MPP SQL warehouses. BigQuery and Snowflake separate storage and compute most fully; Synapse adds Spark pools |
| Athena vs Synapse serverless SQL | Both run SQL straight over files in the lake and charge per data scanned |
| Delta vs Iceberg | Both are open table formats (Parquet + a metadata log). Delta is Databricks-native; Iceberg is the vendor-neutral default elsewhere |
| ETL vs ELT | ETL transforms before loading (Glue, PySpark into Postgres). ELT loads raw first and transforms inside the platform (dbt, Databricks SQL) |

## Interview lines

| Question | Answer |
|---|---|
| "Have you used Azure?" when you've mostly used AWS | "Mostly AWS, but the patterns carry over: S3 maps to ADLS Gen2, IAM roles to managed identities, Glue to Databricks, Redshift to Synapse. I've built the Citi Bike pipeline on both" |
| Why would a company go multi-cloud? | Acquisitions, a best-of-breed service on another cloud, regulatory or customer requirements, or avoiding lock-in. It costs more in networking and identity setup |
| What stays the same across clouds? | The lakehouse pattern (Bronze, Silver, Gold), Spark and SQL code, open table formats, orchestration DAGs and the idea of least-privilege service identities |
| What changes? | Identity and permissions, networking, service names and pricing. That's where most setup time goes |
