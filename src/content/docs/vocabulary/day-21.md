---
title: Day 21 Vocabulary
description: Glossary of terms and definitions from the Training 21 study guide.
sidebar:
  order: 21
---

Vocabulary — Study Guide Day 21

## Cloud Networking
- **VPC (Virtual Private Cloud)** — A logically isolated virtual network within AWS.
- **Subnet** — A range of IP addresses within a VPC, located in one Availability Zone.
- **Availability Zone (AZ)** — An isolated data center location within a region.
- **CIDR block** — The IP range of a VPC or subnet, e.g. `10.0.0.0/16`.
- **Route table** — Rules determining where network traffic is sent.
- **Public subnet** — A subnet whose route table sends internet traffic to an Internet Gateway.
- **Private subnet** — A subnet with no route from the internet.
- **Internet Gateway** — Provides an internet route for appropriately configured public resources.
- **NAT Gateway** — Allows resources in private subnets to initiate outbound connections through a public subnet.
- **VPC Endpoint** — Private connectivity to supported AWS services without internet access.
- **Gateway endpoint** — Free VPC endpoint type for S3 and DynamoDB, added to route tables.
- **Interface endpoint (PrivateLink)** — Paid VPC endpoint type that places a network interface in your subnet.
- **Security Group** — A stateful virtual firewall controlling allowed traffic to a resource.
- **Network ACL (NACL)** — A stateless subnet-level firewall with allow and deny rules.
- **Stateful** — Replies to allowed traffic are automatically allowed back.
- **ENI (Elastic Network Interface)** — A virtual network card giving a resource an IP in a subnet.
- **Self-referencing security group rule** — An inbound rule allowing traffic from the same security group, so Glue workers can talk to each other.
- **Port 5439** — Redshift's default port.

## Security and Access
- **Authentication** — Verifying who you are before granting access to a system.
- **Authorization** — Deciding what an authenticated identity is allowed to do.
- **put-role-policy** — CLI command attaching an inline policy to a role.
- **simulate-principal-policy** — CLI command testing whether a role would be allowed an action, without doing it.
- **sqlworkbench** — IAM action prefix for Redshift Query editor v2.
- **tag:GetResources** — Permission the query editor uses to list workgroups.
- **AWS Secrets Manager** — Service storing credentials encrypted, read by services at runtime, with rotation and auditing.
- **Parameter Store** — Systems Manager feature for config and secrets, without built-in rotation.
- **GRANT** — SQL command giving a database user permissions on a schema or table.
- **PUBLIC (in GRANT)** — Every database user, not the internet.
- **Federated user** — Database user created from an IAM identity when connecting through the query editor.

## SQL Clauses and Commands
- **WHERE** — Filters rows before aggregation.
- **HAVING** — Filters groups after aggregation.
- **QUALIFY** — Filters window-function results.
- **Window function** — Function computed over a set of rows related to the current row, marked by `OVER`.
- **ROW_NUMBER()** — Window function giving each row in a partition a unique sequential number.
- **PARTITION BY** — Restarts a window function's calculation for each group.
- **SELECT DISTINCT** — Returns only rows that aren't identical duplicates.
- **DELETE** — Removes chosen rows, row by row.
- **TRUNCATE** — Removes all rows quickly, keeping the table structure.
- **DROP TABLE** — Removes the table entirely.
- **UNION ALL** — Combines result sets, keeping duplicates.
- **UNION** — Combines result sets, removing duplicates.
- **CASE WHEN** — SQL's conditional (if/else) expression.
- **NULLIF(a, b)** — Returns NULL if a equals b, otherwise a; prevents division by zero.
- **EXTRACT** — Pulls a part (year, month, day, hour, DOW) out of a date or timestamp.
- **TO_CHAR** — Formats a date or number as text.
- **CAST** — Converts a value to another data type.
- **CONVERT_TIMEZONE** — Redshift function converting a timestamp between time zones.
- **information_schema.columns** — System view listing table columns (Redshift has no DESCRIBE).
- **Alias** — A short name for a table or column, e.g. `f` for the fact table.

## Dimensional Modeling
- **Star schema** — A central fact table joined directly to dimension tables.
- **Fact table** — Stores measurable observations and foreign keys to dimensions.
- **Dimension table** — Stores descriptive attributes that give facts context.
- **Grain** — What exactly one row of a fact table represents.
- **Schema (Redshift)** — A namespace for tables inside a database, e.g. `gold`.
- **Natural key** — An identifier from the source system, e.g. `station_id`.
- **Surrogate key** — A warehouse-generated integer key.
- **date_key** — Integer date identifier in `YYYYMMDD` form, e.g. 20261008.
- **Referential integrity** — Every foreign key value matches a row in the referenced table.
- **Orphaned fact** — A fact row whose dimension key has no matching dimension row.
- **Anti-join** — `LEFT JOIN ... WHERE right.key IS NULL`, finding rows with no match.
- **Informational constraint** — Redshift primary/foreign key that isn't enforced.
- **DISTKEY** — Column deciding which node/slice each row is stored on.
- **SORTKEY** — Column(s) deciding the order rows are stored on disk.
- **Semi-additive measure** — Can be summed across some dimensions but not time, e.g. bikes available.
- **Data profiling** — Checking row counts, distinct keys, ranges and nulls before modeling.

## Loading and Analytics
- **ELT** — Load first, transform inside the warehouse with SQL.
- **ETL** — Transform before loading into the warehouse.
- **Idempotent load** — A load that gives the same result if rerun, e.g. TRUNCATE + INSERT.
- **Data validation** — Checks after a load (counts, orphans, duplicates) to confirm correctness.
- **Stored procedure** — Saved, named SQL logic run with `CALL`.
- **View** — A saved query that runs fresh each time.
- **Materialized view** — A saved query whose results are stored and refreshed.
- **Trigger** — Code a database runs automatically when data changes.
- **CDC (Change Data Capture)** — Streaming only the inserts, updates and deletes from a database's change log.
- **MERGE / upsert** — Insert new rows and update existing ones in one statement.

## Big Picture
- **Terraform** — Infrastructure-as-code tool that creates and destroys cloud resources from configuration files.
- **MLOps** — Practices and tools for training, deploying and monitoring ML models.
- **MLflow** — Open-source MLOps platform for experiment tracking, model registry and serving.
- **Regression** — Predicting a number.
- **Clustering** — Grouping similar items without labels.
- **BI tools** — Power BI, Tableau, QuickSight: dashboards and reports on warehouse data.
