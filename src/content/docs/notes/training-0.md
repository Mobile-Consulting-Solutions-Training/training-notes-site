---
title: Training 0 - Data Engineering Fundamentals
description: Hardware, Distributed Systems, Data Engineering Concepts, and The Data Engineer Role
---

Teacher: Evan Flint

# Prerequisites for Next Session

Note: the full Windows instructions (WSL 2 + Docker Desktop) don't apply since you're on a Mac - kept below for reference. Your actual homework is the Mac guide.

## My Homework (macOS Setup Guide: Hardware Virtualization + Docker)

For Mac users, setup is simpler than Windows - WSL is not required because macOS is Unix-based. You only need to verify your Mac supports virtualization and install Docker Desktop.

### 1. Hardware virtualization on Mac

Apple Silicon Macs (M1, M2, M3, M4, M5, etc.): virtualization support is built into the processor and macOS - there is normally no BIOS/UEFI setting to enable. Check your chip: Apple menu -> About This Mac -> look for "Chip" (e.g. "Chip: Apple M3 Pro"). If it's Apple M1-M5 or another Apple Silicon chip, proceed directly to installing Docker.

Intel Macs: open Terminal and run:
```
sysctl -a | grep machdep.cpu.features
```
Look for `VMX` in the output - this indicates the Intel processor supports Intel VT-x hardware virtualization. You can also run:
```
sysctl -n machdep.cpu.features | grep VMX
```
Unlike a typical Windows PC, Macs generally don't provide a BIOS setting to manually enable Intel VT-x - on supported Intel Macs, macOS manages virtualization capability itself.

### 2. Determine whether you need Apple Silicon or Intel Docker

Apple menu -> About This Mac -> look at Chip/Processor:
- Apple M1/M2/M3/M4/M5 -> download the Apple Silicon version of Docker Desktop
- Intel Core i5/i7/i9 -> download the Intel version

### 3. Install Docker Desktop

- [ ] Download Docker Desktop for Mac (correct version for your chip): https://docs.docker.com/desktop/setup/install/mac-install/
- [ ] Open the .dmg, drag Docker into the Applications folder
- [ ] Open Applications, launch Docker
- [ ] Accept the license agreement, allow any macOS permissions requested, enter your Mac password if prompted
- [ ] Wait for Docker to start (may take a minute)

### 4. Verify Docker

- [ ] In Terminal:
```
docker --version
docker compose version
docker run hello-world
```
Should print "Hello from Docker!" after downloading the test image.

### 5. Test with a Linux container

- [ ] Run:
```
docker run -it ubuntu bash
cat /etc/os-release
exit
docker ps -a
docker images
```

If `docker run hello-world` and the Ubuntu container both work, the Mac is ready for Docker-based development.

## Windows Setup Guide (reference only - not needed on Mac)

Recommended Windows configuration: Windows -> WSL 2 -> Ubuntu -> Docker Desktop. WSL 2 uses hardware virtualization, so virtualization should be checked before installing the rest of the environment.

1. Check hardware virtualization: Task Manager (Ctrl+Shift+Esc) -> Performance -> CPU -> look for "Virtualization: Enabled"
2. If disabled, enable it in BIOS/UEFI (Windows 11: Settings -> System -> Recovery -> Advanced startup -> Restart now -> Troubleshoot -> Advanced options -> UEFI Firmware Settings). Look for "Intel VT-x"/"Intel Virtualization Technology" (Intel) or "SVM Mode"/"AMD-V" (AMD), set to Enabled, save and restart.
3. Install WSL: open PowerShell as Administrator, run `wsl --install` (installs WSL 2, the Linux kernel, and Ubuntu by default). Restart when prompted.
4. Complete Ubuntu setup: launch Ubuntu from Start menu, set a Linux username/password (separate from Windows credentials; password won't show characters as you type).
5. Verify WSL 2: `wsl --status` and `wsl --list --verbose` - should show Ubuntu with VERSION 2. If it shows version 1, run `wsl --set-version Ubuntu 2` and `wsl --set-default-version 2`. Keep it updated with `wsl --update` (Docker requires at least WSL 2.1.5).
6. Update Ubuntu: `sudo apt update` then `sudo apt upgrade -y`. Optionally `sudo apt install -y curl wget git unzip`. Verify with `uname -a`.
7. Install Docker Desktop for Windows (don't install Docker Engine separately inside Ubuntu - use Docker Desktop's WSL 2 integration instead): download from docs.docker.com/desktop/setup/install/windows-install, run the installer, select the WSL 2 backend when prompted.
8. Configure Docker: Docker Desktop -> Settings -> General -> ensure "Use the WSL 2 based engine" is enabled; Settings -> Resources -> WSL Integration -> enable integration with Ubuntu.
9. Verify Docker from the Ubuntu terminal: `docker --version`, `docker compose version`, `docker run hello-world` (should print "Hello from Docker!").
10. Test a real container: `docker run -it ubuntu bash`, then `cat /etc/os-release`, `exit`, `docker ps -a`, `docker images`.

Final verification (from PowerShell then Ubuntu): `wsl --status` / `wsl --list --verbose` (Ubuntu should show VERSION 2), then `git --version`, `docker --version`, `docker compose version`, `docker run hello-world` - all four should work.

---

# Hardware

## Video Resources (shared during interview)

| Video | Purpose | Link |
|---|---|---|
| How do CPUs Work? | Explains CPU architecture - how the processor executes instructions, core engineering behind computation | https://www.youtube.com/watch?v=16zrEPOsIcI |
| How do Graphics Cards Work? Exploring GPU Architecture | Covers GPU architecture - how graphics cards handle parallel processing (relevant to ML/data workloads) | https://www.youtube.com/watch?v=h9Z4oGN89MU |
| How does this SSD store 8TB of Data? | Deep dive on SSD engineering - how flash storage physically stores large amounts of data | https://www.youtube.com/watch?v=r-SivgEpA1Q |
| How does Computer Memory Work? | Explains RAM/memory fundamentals - how the CPU reads/writes active working data | https://www.youtube.com/watch?v=7J7X7aZvMXQ |
| How does Computer Hardware Work? [3D Animated Teardown] | General hardware overview - visual teardown of how all core components fit together | https://www.youtube.com/watch?v=d86ws7mQYIg |
| How do Hard Disk Drives Work? | Explains HDD mechanics - spinning disk storage, contrasts with SSD | https://www.youtube.com/watch?v=wtdnatmVdIg |
| How do SSDs Work? / How does your Smartphone store data? | Deeper look at SSD/flash storage at the nanoscopic/transistor level | https://www.youtube.com/watch?v=5Mh3o886qpg |
| How do Transistors Build into a CPU? | Explains the transistor as the fundamental building block of a CPU | https://www.youtube.com/watch?v=_Pqfjer8-O4 |
| How does Computer Cache, Memory, and Storage Work? | Ties together the full memory hierarchy - cache, RAM, and storage and how they interact | https://www.youtube.com/watch?v=TfhL5kBiQVI |

---

Q. What is the difference ROM memory vs RAM memory?

A. 
| | ROM (Read-Only Memory) | RAM (Random Access Memory) |
|---|---|---|
| Purpose | Stores firmware/boot instructions | Stores data/instructions actively in use |
| Volatility | Non-volatile (keeps data without power) | Volatile (data lost when power is off) |
| Read/Write | Read-only (or rarely rewritten) | Read and write freely |
| Speed | Slower | Much faster |
| Use case | BIOS, firmware, permanent instructions | Running programs, temporary working data |

---

Q. Two terms frequently used in Data Engineering: Memory and Disk - what do they mean?

A. (Teacher's definition)
- Memory - in common usage, we are talking about RAM memory
- Disk - the common usage for persistent memory, such as hard drives and SSDs

Expanded:
- Memory (RAM): fast, volatile storage the CPU uses to hold data and instructions it is actively working with. Cleared when power is lost; much faster but smaller/more expensive than disk.
- Disk: non-volatile - data survives power loss/restarts. Slower than RAM but much larger capacity and cheaper. Used for long-term storage: files, databases, OS, application data.

| | Memory (RAM) | Disk (SSD/HDD) |
|---|---|---|
| Speed | Very fast | Much slower |
| Capacity | Limited, expensive | Large, cheap |
| Persistence | Volatile - lost on power off | Persistent - survives restarts |
| Role | Active computation, working data | Long-term storage, files, DBs |

---

Q. What is Memory in data engineering?

A. Refers to in-memory computing - processing data in RAM instead of reading/writing disk on every step. Core reason engines like Apache Spark are fast (process in RAM across a cluster vs MapReduce writing intermediate results to disk).
- Memory (RAM): fast, limited/expensive, volatile - used for active computation, caching, shuffles
- Disk: slower, cheap/large, persistent - used for storage, checkpoints, final output
- Running out of memory during processing causes spilling to disk (slower) or OOM (out-of-memory) errors
- In-memory tools: Redis, Memcached (caching), Apache Arrow (in-memory columnar format)

| | Memory (RAM) | Disk |
|---|---|---|
| Used for | Active computation, caching, shuffles | Storage, checkpoints, final output |
| Cost/Capacity | Limited, expensive | Cheap, large |
| Failure mode | OOM (out-of-memory) errors | Spilling (slower but recoverable) |
| Example tools | Redis, Memcached, Apache Arrow | HDFS, S3, local disk |

---

# Distributed Systems & Infrastructure

Q. What is Distributed Systems in data engineering?

A. (Teacher's definition) Systems that involve multiple machines which are connected together in some way, and which all work together towards a common goal.

Expanded: A system where data storage and processing are spread across multiple machines (nodes) working together as one logical system, instead of one machine. Foundation of Big Data tooling.
- Why: scale (horizontal vs vertical scaling), fault tolerance (node failure doesn't stop the system), parallelism (split large jobs across nodes)
- Key concepts: partitioning/sharding (splitting data across nodes), replication (copies for fault tolerance), cluster (group of machines), master/worker or driver/executor (coordinator assigns work), shuffle (moving data across nodes - expensive)
- CAP theorem: a distributed system can only fully guarantee 2 of 3 - Consistency, Availability, Partition tolerance. Real-world tradeoff is usually Consistency vs Availability since partitions are unavoidable.
- Examples: HDFS/S3/Cassandra (storage), Spark/Hadoop/Flink (processing), Kafka (streaming), ZooKeeper/Kubernetes (coordination)

| Concept | Meaning |
|---|---|
| Partitioning/Sharding | Splitting data into chunks distributed across nodes |
| Replication | Keeping copies of data on multiple nodes for fault tolerance |
| Cluster | A group of machines (nodes) working together |
| Master/Worker (Driver/Executor) | Coordinator node assigns work to worker nodes |
| Consistency | Ensuring all copies of data agree |
| Fault tolerance | System keeps working even if nodes crash |
| Shuffle | Moving/redistributing data across nodes - expensive, common bottleneck |

CAP Theorem - a distributed system can only fully guarantee 2 of 3:

| Property | Meaning |
|---|---|
| Consistency (C) | All nodes see the same data at the same time |
| Availability (A) | Every request gets a response |
| Partition tolerance (P) | System keeps working despite network failures between nodes |

| Pros | Cons |
|---|---|
| Scales beyond what one machine can handle (horizontal scaling) | Much more complex to design, build, and debug than a single-machine system |
| Fault tolerant - system keeps running if individual nodes fail | Network latency/overhead between nodes (especially during shuffles) |
| Parallelism - large jobs finish faster by splitting across nodes | Consistency tradeoffs (CAP theorem) - can't have perfect consistency and availability during a network partition |
| Cost-effective - many cheap commodity machines instead of one expensive supercomputer | Higher operational/maintenance burden (monitoring, coordination, cluster management) |

---

Q. What is a compute cluster and how does it work?

A. (Teacher's definition) At least 3 computers, connected together via a local area network and a router, which are configured to work together on the same task.

Expanded: A compute cluster is a group of connected machines (nodes) that pool their CPU, memory, and disk to work together on tasks as if they were one system. It's the physical/virtual infrastructure that distributed systems (like Spark or Hadoop) run on top of.

How it works:
- One or more nodes act as the coordinator (master/driver) - it receives jobs, splits them into smaller tasks, and assigns those tasks to other nodes
- The remaining nodes are workers (executors) - each does its assigned slice of the work using its own local CPU/RAM/disk, in parallel with the others
- A cluster manager/resource manager (e.g. YARN, Kubernetes, Mesos, or Spark's own standalone manager) tracks which nodes are available and allocates resources to jobs
- Nodes communicate over a network to shuffle data, report progress, and return results back to the coordinator
- If a worker node fails, the coordinator detects it and reassigns its tasks to another healthy node (fault tolerance)

| Role | Job |
|---|---|
| Master/Driver | Accepts jobs, splits work into tasks, assigns to workers, collects/aggregates results |
| Worker/Executor | Executes assigned tasks using its own CPU/RAM/disk, reports status/results back to driver |
| Cluster Manager | Tracks node health/availability, allocates resources to jobs (e.g. YARN, Kubernetes, Mesos) |

Example: In Spark, you submit a job to the Driver -> the Driver breaks it into tasks -> the Cluster Manager allocates Executors on worker nodes -> Executors run tasks in parallel (in-memory where possible) -> results are sent back to the Driver.

| Pros | Cons |
|---|---|
| Pools CPU/RAM/disk across many machines - far more total capacity than one machine | Network communication between nodes adds latency/overhead |
| Fault tolerant - failed worker's tasks get reassigned automatically | Requires a cluster manager/orchestration layer (added complexity) |
| Scalable - add more nodes to handle more load | Harder to debug - failures can be distributed/intermittent across nodes |
| Cheaper than buying one massive single machine | Can be underutilized/costly if not sized correctly for the workload |

---

Q. What is HDFS?

A. HDFS (Hadoop Distributed File System) is a distributed storage system that splits large files into blocks and spreads them across many machines in a cluster, so data can be stored and processed at a scale no single machine could handle. It's the storage layer underneath Hadoop.

Key ideas:
- Blocks: files are split into large chunks (default 128MB) rather than stored as one whole file
- Replication: each block is copied (default 3x) across different nodes for fault tolerance - if one node dies, the data isn't lost
- NameNode/DataNode architecture: a NameNode (master) tracks metadata - which blocks live where; DataNodes (workers) store the actual block data
- Write-once, read-many: optimized for large sequential reads/writes rather than frequent small updates

| Component | Role |
|---|---|
| NameNode | Master node - stores metadata (file-to-block mapping, block locations), coordinates access |
| DataNode | Worker nodes - store actual data blocks, report health/status back to NameNode |
| Block | Fixed-size chunk (default 128MB) that a file is split into for distributed storage |
| Replication factor | Number of copies of each block kept across nodes (default 3) for fault tolerance |

| Pros | Cons |
|---|---|
| Fault tolerant via replication - no single node failure loses data | Poor for small files - each file/block adds NameNode metadata overhead |
| Scales to huge datasets across cheap commodity hardware | Not good for low-latency random access or frequent small updates |
| High throughput for large sequential reads/writes | NameNode can be a bottleneck/single point of failure (mitigated with HA setups, but adds complexity) |
| Integrates natively with the Hadoop/Spark ecosystem | Increasingly being replaced by cloud object storage (e.g. S3) in modern architectures |

---

Q. What are Processing Engines?

A. The software systems that actually execute computation over data - reading it, applying transform logic (filter, join, aggregate, ML, etc.), and producing output, usually distributed across a cluster. This is the "compute" layer, separate from the "storage" layer (HDFS, S3, a data lake) that just holds the data. Keeping storage and compute separate/independently scalable is a core principle of modern big data architecture.

| Type | Purpose | Examples |
|---|---|---|
| Batch | Process large, fixed datasets on a schedule (e.g. nightly job) | Hadoop MapReduce (original, disk-based), Apache Spark, Apache Tez |
| Stream | Process data continuously/in real-time as it arrives | Apache Flink, Kafka Streams, Spark Structured Streaming, Apache Storm |
| Query/SQL engines | Run SQL directly against data without owning the storage | Presto/Trino, Apache Hive, AWS Athena, Apache Drill |
| Unified engines | Handle both batch and streaming in one system | Apache Spark, Apache Flink, Apache Beam (an abstraction layer that can run on top of Spark/Flink/others) |

Note: Spark is a unified batch + streaming processing engine. Hive is really a query engine layer - it translates SQL into jobs that run on an underlying processing engine (originally MapReduce, now often Spark or Tez). HDFS/data lakes are storage, not processing.

---

Q. What is Apache Spark?

A. (Teacher's definition) Get the data from HDFS, and then process it according to logic that you program it to process by, then load the data into your Data Warehouse - in the past that would have been called Hive.

Expanded: Apache Spark is an open-source distributed processing engine for large-scale data. It was built to overcome the main weakness of the older Hadoop MapReduce model - MapReduce writes intermediate results to disk between every step, which is slow. Spark instead keeps data in-memory across the cluster whenever possible, which makes it roughly 10-100x faster for iterative/multi-step workloads.

Spark Architecture (the pieces, and how they connect):

```
Your Program (Driver)
      |
      v
Cluster Manager  --allocates nodes-->  Executors (on Worker Nodes)
      |                                     |
      v                                     v
  Builds DAG of                    Run tasks in parallel,
  transformations                  cache data in-memory,
                                    report results back to Driver
```

How a job actually executes - Job -> Stages -> Tasks:
1. Job: triggered by an action (e.g. `.save()`, `.count()`) - the whole unit of work
2. Stages: Spark splits the job into stages, breaking at points where a shuffle (data movement across the network) is required, like a `groupBy` or `join`
3. Tasks: each stage is split into tasks - one task per data partition - and these run in parallel across executors

How a typical Spark job works (matches the ETL pattern):
1. Extract - Spark reads data from a source, commonly HDFS, but also S3, Kafka, JDBC databases, or flat files
2. Transform - you write logic (filtering, joining, aggregating, cleaning) using Spark's DataFrame/SQL API; Spark builds this into a DAG (Directed Acyclic Graph) of steps and only actually runs it when an action (like save or count) is triggered - this is called lazy evaluation
3. Load - the processed result is written into a Data Warehouse or lake so it can be queried/analyzed downstream

| Spark Component | Role |
|---|---|
| Driver | Runs your program's main logic, builds the execution plan (DAG), schedules tasks across executors |
| Cluster Manager | Allocates resources/nodes for the job (YARN, Kubernetes, Mesos, or Spark's own standalone manager) |
| Executor | Runs on worker nodes, executes the assigned tasks, holds cached/in-memory data |
| RDD (Resilient Distributed Dataset) | Spark's original core data structure - an immutable, distributed, fault-tolerant collection of data partitioned across the cluster |
| DataFrame | Higher-level, structured, table-like data structure (built on RDDs) - optimized automatically by Spark's Catalyst query optimizer |

| Spark Module | Purpose |
|---|---|
| Spark Core | Base engine - task scheduling, memory management, fault recovery, RDDs |
| Spark SQL | Query structured data with SQL or the DataFrame API; can read/write Hive tables |
| Structured Streaming | Process real-time/streaming data (e.g. from Kafka) using the same DataFrame API |
| MLlib | Built-in distributed machine learning library |
| GraphX | Graph processing and analytics |

Note on Hive: Hive was the original SQL-on-Hadoop data warehouse - it let you write SQL (HiveQL) that got translated into MapReduce jobs, with a "Hive Metastore" tracking table schemas/locations. It was slow because it inherited MapReduce's disk-heavy execution. Spark can read and write Hive tables directly (via Spark SQL) and is now commonly used to do the processing work Hive's own engine used to do. In modern stacks, the "data warehouse" destination is often Snowflake, BigQuery, Redshift, or a lakehouse format like Delta Lake/Apache Iceberg - but the Hive Metastore concept (a central catalog of table metadata) is still widely used under the hood by these newer systems.

Pipeline: HDFS (storage) -> Spark (extract + transform, in-memory across the cluster) -> Data Warehouse / Hive / Delta Lake / Snowflake (load, for querying and analysis)

| Pros | Cons |
|---|---|
| In-memory processing - much faster than disk-based MapReduce, especially for iterative jobs | Memory-hungry - large jobs can hit OOM errors if the cluster doesn't have enough RAM |
| One engine for batch, streaming, SQL, ML, and graph processing | More complex to tune than a simple script (partitioning, memory settings, shuffles) |
| High-level APIs (DataFrame/SQL) make it accessible without deep distributed-systems knowledge | Higher infrastructure cost/overkill for small datasets that fit on one machine |
| Lazy evaluation lets Spark optimize the whole execution plan before running | Steep learning curve to properly optimize/debug performance issues (skew, spill, shuffle) |

---

Q. What is Hive?

A. (Teacher's definition) An old Data Warehouse program - a special kind of database called an analytical database (OLAP), which enforces a particular kind of table structure on the data, which is there to make it easier to use the data for analysis.

Expanded: Apache Hive is a data warehouse system built on top of Hadoop/HDFS. It lets you write SQL-like queries (HiveQL) against huge datasets stored in HDFS without writing MapReduce/Spark code directly - Hive translates the SQL into jobs that run on the cluster. It enforces a schema on the data (tables, columns, partitions) so that data which was originally just files in HDFS becomes structured and queryable like a normal database table.

| OLAP (Analytical Database) | |
|---|---|
| Purpose | Handle complex queries/reporting over large historical datasets |
| Query pattern | Fewer, large, complex read queries (aggregations, joins, scans) |
| Data structure | Often denormalized/star-schema (optimized for read speed) |
| Example systems | Hive, Snowflake, BigQuery, Redshift |
| Example use case | Reporting total sales by region for the quarter |

| Pros | Cons |
|---|---|
| SQL interface (HiveQL) makes big data accessible to anyone who already knows SQL | Historically slow - originally translated queries into MapReduce jobs |
| Good for large batch analytical queries over huge historical datasets | Not suited for real-time/low-latency queries |
| Schema enforcement helps organize and query data reliably | Not built for OLTP/transactional workloads (frequent small writes) |
| Hive Metastore (table metadata catalog) concept is still widely used today | Largely superseded in practice by faster engines (Spark SQL, Presto/Trino, cloud warehouses) |

---

Q. What is OLTP?

A. OLTP (Online Transaction Processing) is a type of database system built to handle the day-to-day operational transactions of an application - fast, small, frequent reads and writes, like placing an order, updating a user's profile, or processing a login. It's the counterpart to OLAP (analytical databases like Hive) - OLTP runs the live application, OLAP analyzes historical data from it afterward.

Expanded: OLTP systems are what sit behind almost every app you use day to day. Every time you add something to a cart, like a post, or update a setting, that's an OLTP transaction - a small, immediate read/write that has to complete reliably and fast, often with many users hitting the same database concurrently.

| | OLTP (Transactional Database) |
|---|---|
| Purpose | Run the live, operational side of an application |
| Query pattern | Many small, fast reads/writes - single-record lookups, inserts, updates, deletes |
| Data structure | Highly normalized - data split across many related tables to avoid redundancy |
| Transaction guarantees | ACID (Atomicity, Consistency, Isolation, Durability) - transactions must fully succeed or fully fail, no partial writes |
| Example systems | MySQL, PostgreSQL, Oracle DB, MongoDB (app databases) |
| Example use case | Placing an order, updating an account balance, logging a user in |

| Pros | Cons |
|---|---|
| Very fast for small, individual transactions | Poor performance for large analytical queries (scans, aggregations across millions of rows) |
| ACID guarantees keep data accurate and consistent even with many concurrent users | Normalized structure requires many joins, which get expensive at analytical scale |
| Optimized for high-concurrency read/write workloads | Not meant to hold years of historical data efficiently - usually only recent/active data |
| Data is always up to date (real-time) | Running heavy reporting queries directly on it can slow down or lock the live application |

Note: this is exactly why data gets extracted out of an OLTP database and loaded into an OLAP warehouse via ETL/ELT - each system is built for a different job, and trying to do both on one database causes problems.

---

Q. OLAP vs OLTP - expanded

A.

| | OLTP (Online Transaction Processing) | OLAP (Online Analytical Processing) |
|---|---|---|
| Purpose | Run the day-to-day operations of an application | Analyze historical data to support decisions/reporting |
| Query pattern | Many small, fast reads/writes (single-record lookups, inserts, updates) | Fewer, large, complex read queries (aggregations, joins, scans across millions of rows) |
| Data structure | Highly normalized - minimizes redundancy, optimized for fast writes | Often denormalized / star-schema - optimized for fast reads |
| Data freshness | Real-time, always current | Often a snapshot/batch-updated (hourly, daily) |
| Data volume per query | Small - a few rows | Large - potentially entire tables |
| Users | Applications, end users (e.g. checkout flow) | Analysts, data scientists, BI dashboards |
| Example systems | MySQL, PostgreSQL, MongoDB (app databases) | Hive, Snowflake, BigQuery, Redshift |
| Example operation | "Insert this new order" / "Update this user's address" | "What were total sales by region last quarter?" |

Why the distinction matters:
- OLTP systems are tuned for concurrency and speed on tiny transactions - locking, indexing, and normalization exist to keep writes fast and consistent.
- OLAP systems are tuned for scanning huge volumes of data - denormalization and columnar storage (Parquet, ORC) trade write-speed for much faster aggregation/read performance.
- You generally don't run analytics directly on an OLTP database - heavy analytical queries would slow down (or lock) the live application. This is exactly why data gets extracted out of OLTP systems and loaded into an OLAP warehouse - it's the real-world reason ETL/ELT pipelines exist in the first place.

---

Q. What is a Data Lake? What are the other storage destination options?

A. A data lake is a storage repository that holds raw data in its native format - structured, semi-structured, or unstructured - until it's needed, rather than transforming it into a fixed schema before storing it (as a warehouse does).

| | Data Warehouse | Data Lake | Data Lakehouse |
|---|---|---|---|
| Data type | Structured, already processed | Raw - structured/semi-structured/unstructured (JSON, logs, images, etc.) | Raw data + warehouse-like structure/management on top |
| Schema | Schema-on-write (defined before data is loaded) | Schema-on-read (defined only when you query it) | Enforced but flexible schema, via a table format layer |
| Cost | More expensive storage, but cheap/fast to query | Very cheap storage, more compute needed to query well | Cheap storage + fast queries - aims for the best of both |
| Examples | Hive, Snowflake, BigQuery, Redshift | Amazon S3, Azure Data Lake Storage, raw HDFS | Databricks (Delta Lake), Apache Iceberg, Apache Hudi |
| Best for | BI reporting, dashboards, structured analytics | ML/data science, storing everything cheaply "just in case" | Modern unified analytics + ML platform |

Other related concept - Data Mart: a smaller, focused subset of a data warehouse built for one team/department (e.g. a "Marketing" or "Finance" mart).

Note: plain operational/OLTP databases (MySQL, Postgres) aren't part of this comparison - they're built for fast transactions, not analytical storage/querying.

Q. What is the Medallion Architecture? (What are all the layers to a Data Lake?)

A. (Teacher's definition)
- Bronze - basically a data dumping ground, you can put anything you want into it with no real rules, and can think about organizing it later
- Silver - a layer where you do basic processing on your bronze data, and put the combined, cleaned data into a place where it can be easily used
- Gold - a layer that takes silver layer data that is applicable to answering specific questions, and puts it there for easy access
- T (Transformation) - there are transformation jobs between bronze and silver, and between silver and gold, and between any optional layers that are added

Expanded: The standard pattern (popularized by Databricks) for organizing data inside a data lake into three progressively cleaner layers - Bronze -> Silver -> Gold - so raw ingestion, cleaning, and business-ready output stay separate instead of mixed together.

Flow: Source Systems -> Bronze (raw) -> [Transform job] -> Silver (cleaned) -> [Transform job] -> Gold (business-ready) -> BI/Reports/ML

| Layer | Also called | Purpose | Data state | Example |
|---|---|---|---|---|
| Bronze | Raw / Landing zone | Dumping ground for raw data - no rules, organize later | Unprocessed - may have duplicates/nulls/errors | Raw JSON logs dumped straight from an API |
| Silver | Cleansed / Staging zone | Basic processing - combine and clean bronze data into an easily usable place | Structured, reliable, but not yet business-specific | User events joined with a users table, nulls filtered, types fixed |
| Gold | Curated / Business / Presentation zone | Takes silver data applicable to specific questions and makes it easy to access | Ready for BI dashboards, reporting, ML features | "Daily active users by region" summary table for a dashboard |

Why layer it this way:
- Bronze preserves the original raw data, so the pipeline can always be reprocessed from scratch if transform logic changes or a bug is found, instead of having to re-pull from the source
- A transformation job runs between every pair of layers (Bronze->Silver, Silver->Gold, and any optional layers in between) - this is where the actual "Transform" step of ETL/ELT lives
- Gold is optimized for consumption - fast queries, pre-aggregated, matches exactly what a report or ML model needs
- Each layer has a clear owner/purpose, so pipelines don't become one giant tangled transform

---

Q. What file formats are used to store data (e.g. in a data lake)?

A.

| Format | Type | Best for | Notes |
|---|---|---|---|
| CSV | Row-based, text | Simple, human-readable data | No schema/types built in, slow for large-scale analytics |
| JSON | Row-based, semi-structured | Nested/flexible data (logs, API responses) | Common in the Bronze layer - raw data as it arrives |
| Avro | Row-based, binary | Data with evolving schemas, streaming (Kafka) | Good schema evolution support, compact |
| Parquet | Columnar, binary | Analytical queries (read specific columns fast) | Most common format for Silver/Gold layers, highly compressed |
| ORC | Columnar, binary | Analytical queries, especially in the Hive ecosystem | Similar to Parquet, originally built for Hive |

Row-based vs Columnar - why it matters:
- Row-based (CSV, JSON, Avro): stores each full record together - good for writing/ingesting data quickly (Bronze layer)
- Columnar (Parquet, ORC): stores each column together - much faster for analytical queries that only need a few columns out of many (Silver/Gold layers, warehouses)

Q. What are Open Table Formats (OTF)? (a layer on top of file formats)

A. (Teacher's definition) Special file formats that are complex - they have an internal folder structure for storing both the data and the metadata together, and they contain optimizations that approximate what you get when you use a regular data warehouse (for mathematical and database operations).

Expanded: In data lakehouses, an Open Table Format sits on top of raw Parquet/ORC files to add transactional, warehouse-like capabilities - ACID transactions, schema enforcement/evolution, and time travel (querying past versions of a table). Examples: Delta Lake, Apache Iceberg, Apache Hudi. This is what makes a data lake behave more like a warehouse - ties into the Data Lakehouse row above.

| Piece | What it holds |
|---|---|
| Data files | The actual records, stored as Parquet (or ORC) files |
| Metadata/log files | Tracks schema, file listings, versions/snapshots, and transaction history - this internal structure is what enables ACID transactions and time travel |

The major OTF formats (Teacher's definitions):
- Iceberg - the most common one, it is the open source standard
- Delta - the most common proprietary format, associated with the Databricks data platform - only use Delta when working with Databricks
- Hudi - basically ignore Hudi, just know of its existence

| Format | Created by | Status | Notes |
|---|---|---|---|
| Apache Iceberg | Originally Netflix, now Apache | Open source standard - most common | Vendor-neutral, broad engine support (Spark, Trino, Flink, etc.) |
| Delta Lake | Databricks | Most common proprietary format | Deepest integration with Spark/Databricks - use it specifically when working in Databricks |
| Apache Hudi | Originally Uber, now Apache | Lower priority to learn | Strong focus on fast upserts/incremental data (streaming-heavy use cases) - just know it exists |

---

# Data Engineering Concepts

## Video Resources

| Video | Purpose | Link |
|---|---|---|
| What is Data Pipeline? \| Why Is It So Popular? | Explains what a data pipeline is and why it's become a core concept in data engineering - ties directly into the Data Lifecycle/ETL/ELT entries below | https://www.youtube.com/watch?v=kGT4PcTEPP8 |
| What Are Data Pipelines? | Another explainer on data pipelines - what moves data from source to destination and why pipelines are structured the way they are | https://www.youtube.com/watch?v=6kEGUCrBEU0 |
| ETL vs ELT \| Modern Data Architectures | Compares ETL and ELT directly - matches the ETL vs ELT comparison/pros-cons tables already in this section | https://www.youtube.com/watch?v=_Nk0v9qUWk4 |

---

Q. What is the Data Lifecycle?

A. (Teacher's definition) The full process of accessing, transforming, and placing the data in the location where it needs to be, in the order in which it's supposed to be organized.

Expanded: The data lifecycle is the end-to-end journey data takes from where it originates to where it's finally consumed/stored for use - every data pipeline follows some version of these stages, in order.

| Stage | What happens |
|---|---|
| Ingestion | Accessing/collecting raw data from its source (databases, APIs, files, streams) |
| Transformation | Cleaning, reshaping, validating, and enriching the data (ETL/ELT) |
| Storage | Placing the processed data into its destination (data warehouse, data lake, database) |
| Analysis/Consumption | Data is queried, analyzed, or used by downstream applications/reports/ML models |
| Archival/Deletion | Old or unneeded data is archived or deleted per retention policy |

Note: Order matters - each stage typically depends on the previous one being done correctly (e.g. you can't reliably transform data you haven't properly ingested).

---

Q. What is ETL?

A. (Teacher's definition) Extract-Transform-Load:
- Extract - find the data where it currently is, and we ingest it into our system
- Transform - we do operations on the data in order to improve it, such as combining previously unrelated data, filtering null values, dropping duplicate values, and organizing the data into output tables
- Load - putting the data into the desired destination, in the desired format

Expanded: ETL is the classic pattern for moving data from source systems into a destination (data warehouse/data lake) where it can be analyzed. Data is transformed *before* it's loaded into the destination - as opposed to ELT, where raw data is loaded first and transformed afterward inside the destination system.

| Stage | Description | Examples |
|---|---|---|
| Extract | Locate and pull data from its source system(s) into the pipeline | Databases, APIs, log files, flat files, streams |
| Transform | Clean, reshape, and improve the data | Joining/combining datasets, filtering nulls, deduplication, aggregations, type conversions, building output tables |
| Load | Write the finished data into its destination in the desired format | Data warehouse (Snowflake, BigQuery, Redshift), data lake, database table |

Note: ETL relates directly to the [[Data Lifecycle]] - Extract maps to Ingestion, Transform maps to Transformation, and Load maps to Storage.

Is ETL legacy? Not obsolete, but partially displaced by ELT in modern cloud-native stacks.

| | ETL | ELT |
|---|---|---|
| Order | Extract -> Transform -> Load | Extract -> Load -> Transform |
| Where transform happens | In a separate processing engine (Spark, on-prem ETL tools) before loading | Inside the destination warehouse itself, after raw data is loaded |
| Still used when | Data must be cleaned/filtered/masked before storage (compliance, PII, cost control), or destination can't transform at scale | Destination warehouse is powerful/cheap enough to transform (Snowflake, BigQuery, Redshift) - common with tools like dbt |
| Status | Still widely used - the foundational pattern everything else builds on | The more common modern default for cloud data warehouses |

| ETL Pros | ETL Cons |
|---|---|
| Only clean/relevant data gets stored - lower storage cost | Requires separate transform infrastructure (e.g. Spark) before loading |
| Sensitive data (PII) can be filtered/masked before it ever reaches the warehouse - good for compliance | Slower to get raw data available for use |
| Destination system doesn't need heavy compute power | Harder to reprocess - if transform logic changes, you often have to re-extract |

| ELT Pros | ELT Cons |
|---|---|
| Raw data is available immediately and can be re-transformed anytime without re-extracting | Raw (possibly messy/sensitive) data lands in the warehouse before being cleaned |
| Leverages the warehouse's own powerful, cheap compute (Snowflake/BigQuery/Redshift) | Requires a powerful (and potentially expensive) destination warehouse |
| Simpler pipeline - fewer moving parts, pairs well with tools like dbt | Storage costs for keeping raw data around; compliance risk if PII isn't filtered before landing |

---

Q. What is ELT?

A. (Teacher's definition) Extract-Load-Transform:
- E/L (Extract/Load) - basically means the data transfer - in ELT, data is NOT transformed during the process of moving it from one place to another
- Transform happens afterward, inside the destination

Expanded: ELT flips the last two steps of ETL. Raw data is extracted and loaded into the destination (data warehouse/lake) as-is, untransformed - then transformation happens afterward using the destination's own compute power (e.g. via SQL or a tool like dbt). This works well when the destination is powerful/cheap enough to handle the transform step itself, which is why it's become the common default for modern cloud data warehouses. See the ETL vs ELT comparison and pros/cons tables above.

---

Q. Batch Processing vs Streaming

A. (Teacher's definition)
- Batch Processing - data arrives periodically in "batches" - so for example, 3 times a day there will be a new file of about 10 GB arriving in S3
- Or once a day at 8am, expect a new 150GB batch

What processing pipeline would this be? Since the data arrives on a schedule (8am, or 3x/day) rather than continuously, this is a batch processing pipeline, not streaming:

| Piece | What's used |
|---|---|
| Trigger | Scheduled, not continuous - a fixed time (8am) or fixed interval (3x/day) |
| Orchestrator | Apache Airflow (or similar scheduler) - kicks off the job at the right time, or watches S3 for the new file to land |
| Processing engine | A batch engine - Apache Spark (most common today), historically Hadoop MapReduce |
| Storage pattern | Fits the Medallion Architecture - the raw file lands in S3/Bronze, gets cleaned into Silver, then aggregated into Gold |
| Pipeline pattern | ETL or ELT - Extract the file from S3, Transform it (Spark), Load it into the warehouse/lake |

Why this rules out streaming: Streaming engines (Flink, Kafka Streams, Spark Structured Streaming) react to data continuously, record by record, in real time. Here the data arrives predictably on a schedule, so a batch job that runs once the file lands is simpler, cheaper, and more appropriate than keeping a streaming job running 24/7.

Streaming (Teacher's definition): In streaming, the data is generated in real time, and must be processed and put into the proper place as efficiently as possible, and in some cases also in real time.

Examples (Teacher's list):
- You are monitoring data that's being produced by an industrial robot
- Stock market data
- Weather data
- Real time dashboard

Streaming requires two separate specialized programs (Teacher's definition):
- One for moving the streaming data (doing the streaming) - e.g. Apache Kafka
- One for processing the streaming data (streaming data processing) - e.g. Apache Flink, Spark Structured Streaming

| Job | What it does | Example tools |
|---|---|---|
| Moving the data (the "streaming" itself) | Transports records continuously from producers to consumers, in order, at scale | Apache Kafka, Amazon Kinesis |
| Processing the streaming data | Reads records off the stream and applies logic (filter, aggregate, window, join) as they arrive | Apache Flink, Spark Structured Streaming, Kafka Streams |

Note: Kafka itself doesn't do much processing - it's the pipe that reliably moves data from wherever it's generated to wherever it needs to be consumed. A separate processing engine (often Flink or Spark) then reads from Kafka and does the actual transform logic.

| | Batch Processing | Streaming |
|---|---|---|
| Data arrival | Periodic, scheduled chunks (e.g. 3x/day, or once daily at 8am) | Continuous, generated in real time, record by record |
| Processing timing | Runs on a schedule/trigger, processes everything at once | Processes each record (or small window) as it arrives |
| Latency | Minutes to hours is fine | Seconds or less, sometimes true real-time |
| Example use case | Daily sales file landing in S3 | Industrial robot sensor data, stock market data, weather data, real-time dashboards |
| Processing engine | Apache Spark (batch), Hadoop MapReduce | Apache Flink, Kafka Streams, Spark Structured Streaming, Apache Storm |
| Orchestration | Scheduler (Airflow, cron) | Long-running job that never stops, reading from a stream (e.g. Kafka topic) |

Note: this connects directly to the Processing Engines entry above - "Batch" and "Stream" are two of the categories listed there.

---

Q. What is Apache Kafka?

A. (Teacher's definition) For streaming more than 1,000 messages per second without losing messages.

Expanded: Apache Kafka is a distributed event streaming platform - it's the tool that does the "moving the streaming data" job described above. Producers write messages (events) to Kafka, organized into topics, and consumers read them - Kafka reliably transports huge volumes of messages between the two, in order, without losing them, even at very high throughput (1,000+ messages/second and beyond).

| Concept | Meaning |
|---|---|
| Topic | A named stream/category of messages (e.g. "orders", "sensor-readings") |
| Producer | An application/system that writes messages into a Kafka topic |
| Consumer | An application/system that reads messages from a Kafka topic |
| Partition | A topic is split into partitions for parallelism - messages within a partition stay in order |
| Broker | A Kafka server that stores and serves the data; multiple brokers form a Kafka cluster |
| Retention | Kafka keeps messages for a configurable period (not just "delivered and gone"), so consumers can replay/reprocess if needed |

Producer, Broker, Consumer - the core flow:

```
Producer  --writes messages-->  Broker (Kafka cluster)  --messages read by-->  Consumer
```

| Role | What it is | Example |
|---|---|---|
| Producer | The application/system that creates and sends messages into Kafka | A web app sending "user clicked checkout" events, or a sensor sending readings |
| Broker | The Kafka server that stores and serves the messages - the middleman. A group of brokers forms the Kafka cluster | The Kafka server(s) themselves |
| Consumer | The application/system that reads messages out of Kafka to do something with them | A Flink/Spark job reading events to process, or a dashboard reading live data to display |

Key things to know:
- Producers and consumers never talk to each other directly - they're fully decoupled. The producer just writes to a topic on the broker; it doesn't know or care who (or how many consumers) reads it later.
- Multiple consumers can read the same topic independently - e.g. one consumer stores raw data in a data lake while another feeds a real-time dashboard, both reading the same stream.
- The broker persists messages for a retention period, so a consumer that's temporarily down can catch up later instead of losing data.

| Pros | Cons |
|---|---|
| Extremely high throughput - built for thousands of messages/second without loss | Kafka itself does minimal processing - still need a separate engine (Flink, Spark) for transform logic |
| Durable - messages are persisted, not just passed through, so consumers can replay history | Operationally complex to run/maintain a Kafka cluster (partitions, brokers, replication) |
| Decouples producers from consumers - multiple consumers can read the same stream independently | Overkill for low-volume or simple use cases - adds infrastructure for a problem that might not need it |
| Fault tolerant via replication across brokers | Requires careful partitioning/key design to avoid bottlenecks or out-of-order data |

Alternatives to Kafka (Teacher's definition): RabbitMQ, MQTT, AWS SQS - simpler streaming/messaging programs, but which are NOT designed to handle high volumes of messages per second.

| Tool | Best for | Notes |
|---|---|---|
| RabbitMQ | Traditional message queuing between services | Flexible routing, but lower throughput than Kafka |
| MQTT | Lightweight messaging for IoT/low-power devices | Designed for small, resource-constrained devices, not high-volume streams |
| AWS SQS | Simple, fully-managed queue for decoupling AWS services | Easy to set up, but not built for Kafka-scale throughput |
| Apache Kafka | High-volume event streaming (1,000+ messages/sec) | The choice when Batch Processing vs Streaming volume/durability actually matters at scale |

---

Q. What is Streaming Processing? (Micro-batch processing)

A. (Teacher's definition) Micro-batch processing: getting one second's worth of data, then processing it during the next second or less, while at the same time getting the subsequent second's data, and so on and so on.

Spark Structured Streaming uses a micro-batch processing architecture.

Expanded: Micro-batch processing is a middle ground between true batch processing and true record-by-record streaming. Instead of waiting hours/a full day for a big batch (like the 8am 150GB example), or processing every single record the instant it arrives, the engine collects a very small window of data (e.g. 1 second's worth) and processes that tiny batch - continuously, on a tight loop - so it looks and feels like real-time streaming while actually being implemented as a rapid series of small batch jobs under the hood.

```
Second 1 data -> [processed during second 2]
Second 2 data -> [processed during second 3]      } happening continuously,
Second 3 data -> [processed during second 4]      } collecting the next window
...                                                } while processing the last
```

| | True Streaming (record-by-record) | Micro-batch |
|---|---|---|
| Unit of processing | One record at a time | A small time window of records (e.g. 1 second) |
| Latency | Lowest possible (milliseconds) | Slightly higher (near-real-time, ~1 second or so) |
| Example engine | Apache Flink (native streaming) | Spark Structured Streaming |
| Simplicity | More complex processing model | Reuses Spark's existing batch engine/APIs under the hood - simpler to build on |

Note: this is why Spark Structured Streaming appears in the Streaming column of the Batch vs Streaming table above, but architecturally it's really running a continuous loop of tiny batch jobs rather than true per-record streaming like Flink.

The other option (Teacher's definition): True real time streaming processing, using an application called Apache Flink.

Q. What is Apache Flink?

A. Apache Flink is a processing engine built for true real-time, record-by-record stream processing - as opposed to Spark Structured Streaming's micro-batch approach, Flink processes each event individually the moment it arrives, giving the lowest possible latency (milliseconds).

| | Spark Structured Streaming | Apache Flink |
|---|---|---|
| Processing model | Micro-batch - tiny batches every ~1 second | True streaming - one record at a time |
| Latency | Near-real-time (~1 second) | True real-time (milliseconds) |
| Built on top of | Spark's existing batch engine | A streaming-first engine, built from the ground up for streaming |
| When to choose | Good enough for most near-real-time use cases, and easier if you're already using Spark | When you genuinely need the lowest possible latency - e.g. fraud detection, industrial monitoring, high-frequency trading |

---

Q. What is Idempotency? (To make something idempotent)

A. (Teacher's definition) An idempotent process is one in which if you do it multiple times, you won't accumulate the same result over and over again unless you've specifically designed it to. Basically, we want processes to be idempotent so that we do not generate unnecessary duplicate data.

Expanded: This matters a lot in data pipelines - if a batch job or streaming consumer fails partway through and has to retry, you want re-processing the same data to be safe, not create duplicate rows or double-count something. A non-idempotent pipeline that gets re-run (due to a retry, a scheduler bug, or manual reprocessing) can silently corrupt downstream data by inserting the same records twice.

Common ways to make a process idempotent:
- Use UPSERT/MERGE instead of INSERT (insert-or-update based on a key, rather than blindly appending)
- Deduplicate on a unique event ID before writing
- Overwrite a partition entirely rather than appending to it (common in batch jobs)
- Track processed offsets/checkpoints (e.g. Kafka consumer offsets) so you don't reprocess what's already done

| Example | Idempotent? | Why |
|---|---|---|
| `INSERT INTO orders VALUES (...)` run twice | No | Creates two duplicate rows |
| `UPSERT INTO orders ON CONFLICT (order_id) DO UPDATE` run twice | Yes | Second run just re-updates the same row, no duplicate |
| Overwriting a partition with today's data, run twice | Yes | Second run replaces the same partition with the same result |
| Appending today's batch file to a table, run twice | No | Appends the same data a second time |

---

Q. Error handling in big data?

A. This ties directly into idempotency above - a lot of error handling exists so pipelines can fail safely and recover without corrupting data.

| Strategy | What it does | Example |
|---|---|---|
| Retries | Automatically re-attempt a failed operation, usually with backoff | A failed API call or write gets retried 3x with increasing delay |
| Idempotency | Makes retries safe - re-running doesn't create duplicates | UPSERT instead of INSERT |
| Dead-letter queue (DLQ) | Records that repeatedly fail processing get routed aside instead of blocking the whole pipeline | A malformed Kafka message goes to an `orders-dlq` topic for later review |
| Checkpointing | Periodically save pipeline progress so a failure resumes from the last checkpoint, not from scratch | Spark Structured Streaming/Flink track offsets so a restart doesn't reprocess everything |
| Data quality/schema validation | Catch bad data early, before it corrupts downstream tables | Tools like dbt tests or Great Expectations validate nulls, types, ranges |
| Quarantine bad records | Skip/set aside individual bad rows instead of failing the entire batch job | A batch job processes 99,000 good rows, routes 1,000 malformed ones to an error table |
| Alerting/monitoring | Detect failures quickly so a human can respond | Job failure triggers a Slack/PagerDuty alert (ties into admin/on-call work below) |
| Delivery guarantees | Define what happens to a message on failure - at-most-once, at-least-once, exactly-once | Kafka can be configured for exactly-once processing semantics |

Key principle: good error handling in big data isn't about preventing all failures (impossible at scale) - it's about designing for failure: failures should be retryable, isolated (one bad record shouldn't kill the whole job), observable (you get alerted), and recoverable (checkpointing/idempotency mean you don't lose or duplicate data when you retry).

---

Q. How is error handling implemented in Python? (try/except)

A. In Python, the code to do error handling is called a try/except block.

The basic pattern:

```python
try:
    # Code that might fail
    process_data()

except SomeSpecificError as e:
    # Handle an expected failure
    handle_error(e)

except Exception as e:
    # Handle unexpected failures
    log_error(e)

finally:
    # Cleanup that must always happen
    cleanup()
```

Realistic data-engineering example: processing a batch of CSV files where individual bad files or records should not crash the entire pipeline.

```python
import pandas as pd

files = [
    "customers_2026_09_01.csv",
    "customers_2026_09_02.csv",
    "customers_2026_09_03.csv"
]

for file in files:
    try:
        print(f"Processing {file}...")

        # Extract
        df = pd.read_csv(file)

        # Validate
        required_columns = ["customer_id", "name", "email"]
        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Transform
        df["email"] = df["email"].str.lower()

        # Load
        df.to_parquet(file.replace(".csv", ".parquet"))

        print(f"Successfully processed {file}")

    except FileNotFoundError:
        # Handle a specific error
        print(f"ERROR: {file} does not exist")

    except pd.errors.ParserError as e:
        # Handle malformed CSV data
        print(f"ERROR: Could not parse {file}: {e}")

    except ValueError as e:
        # Handle our validation error
        print(f"VALIDATION ERROR in {file}: {e}")

    except Exception as e:
        # Catch unexpected errors so the batch can continue
        print(f"UNEXPECTED ERROR in {file}: {e}")

    finally:
        # Runs whether processing succeeds or fails
        print(f"Finished attempt for {file}\n")
```

The important data-engineering concept is fault isolation. If one day's file is missing or malformed, we usually don't want an entire multi-file ingestion job to terminate.

| Exception caught | Handles |
|---|---|
| `FileNotFoundError` | The file doesn't exist |
| `pd.errors.ParserError` | The CSV is malformed and can't be parsed |
| `ValueError` | Our own validation logic raised it (e.g. missing required columns) |
| `Exception` (fallback) | Anything unexpected - catches it so the batch loop can continue to the next file |
| `finally` | Runs no matter what (success or failure) - used for cleanup that must always happen |

Best practices:
- Catch specific exceptions first, and use `except Exception` only as the final fallback - catching specific errors lets you handle each failure mode appropriately instead of treating everything the same way
- In a production pipeline, use Python's `logging` module instead of `print()`
- Send failed records/files to a dead-letter queue (DLQ) or quarantine location instead of just logging and dropping them, so they can be reviewed/reprocessed later - ties directly into the Error Handling and DLQ concepts above

---

# The Data Engineer Role

Q. What CI/CD tools might you encounter?

A. (Teacher's list) Jenkins, AWS CodeCommit and CodePipeline, Azure DevOps, GitLab CI, Travis CI, etc.

Expanded: CI/CD (Continuous Integration/Continuous Deployment) tools automate the build, test, and deployment of code - including data pipeline code (Spark jobs, dbt models, Airflow DAGs). A change gets pushed -> CI runs tests/validates the pipeline -> CD deploys the updated pipeline to production.

| Tool | Type | Notes |
|---|---|---|
| Jenkins | Open-source, self-hosted CI/CD server | The long-standing standard - highly customizable via plugins, but requires you to host/maintain it yourself |
| AWS CodeCommit & CodePipeline | AWS-native CI/CD | CodeCommit = managed Git repo hosting (AWS's alternative to GitHub); CodePipeline = orchestrates build/test/deploy stages, integrates tightly with other AWS services |
| Azure DevOps | Microsoft-native CI/CD + project management | Bundles repos, pipelines, boards, and artifacts into one platform, tightly integrated with the Azure ecosystem |
| GitLab CI | Built into GitLab | CI/CD config lives directly alongside the code in the same repo (`.gitlab-ci.yml`) |
| Travis CI | Cloud-based CI, historically popular with open source | Simpler config-driven setup, less commonly used in enterprise data engineering today |
| GitHub Actions | Built into GitHub | CI/CD config lives alongside the code (`.github/workflows/`) - very common today given how much code already lives on GitHub |

Note: this list is non-exhaustive ("etc.") - the common thread across all of them is automating test/build/deploy so pipeline changes get validated and shipped safely, tying into the admin/tooling work below.

---

Q. What admin work may a data engineer get asked to do?

A. A lot of the job is operational, not just building pipelines:

| Category | What it looks like |
|---|---|
| Access management | Granting/revoking access to warehouse tables, S3 buckets, cluster resources (IAM roles, permissions requests) |
| Cluster/infrastructure management | Spinning clusters up/down, monitoring resource usage, right-sizing for cost vs. performance |
| Pipeline monitoring & alerting | Setting up alerts for failed jobs, checking logs, being on-call when a pipeline breaks overnight |
| Cost monitoring/optimization | Tracking cloud compute/storage spend, finding wasteful queries, right-sizing warehouses |
| Data governance & compliance | Enforcing retention policies, masking/anonymizing PII, GDPR/HIPAA compliance, maintaining a data catalog |
| Documentation | Data dictionaries, pipeline runbooks, schema documentation |
| Schema/metadata management | Maintaining the metastore, managing schema changes/migrations without breaking downstream consumers |
| Backup & disaster recovery | Ensuring data is backed up, occasionally testing recovery procedures |
| Security | Credential rotation, patching, securing endpoints/connections |
| Vendor/tool management | Evaluating and maintaining SaaS tools (Snowflake, Fivetran, Airflow, dbt Cloud), license/seat management |
| Stakeholder communication | Explaining data discrepancies to business teams, gathering requirements for new pipelines/reports |

Note: this kind of work often gets left out of the "cool" parts of data engineering (Spark, pipelines, architecture) but ends up being a real chunk of the day-to-day - especially at smaller companies where one engineer wears many hats.

---

# Agent Generated Notes (from Class Recording)

Generated by comparing the full Training 0 class recording transcript against the notes above. These are things Evan covered live that weren't yet captured. Sourced from the recording (not directly typed by the student), so labeled "(From class recording)" rather than "(Teacher's definition)."

## CPU vs GPU

Q. What is the difference between a CPU and a GPU?

A. (From class recording) A CPU is the part of your computer that actually, literally is a computer - that's where the actual processing is done. It's a general purpose processing engine, designed to handle pretty much any kind of process a normal computer creates at any given time. GPUs are like CPUs in that they're also microprocessors made of silicon, but they're highly specialized in one domain of mathematics called matrix multiplication - they're very good at multiplying matrices (think of a data structure as a line, then another line, forming a square/rectangle). GPUs are good at multiplying those squares/rectangles by other squares/rectangles, which is exactly how pixels are represented on a screen (hence "graphics processing unit"). This same matrix-multiplication strength is also exactly what a machine learning model needs (inputs converted to numbers, multiplied through layer after layer), which is why GPUs are also very good for ML/AI.

| | CPU | GPU |
|---|---|---|
| Purpose | General-purpose processing - handles any kind of process | Highly specialized - matrix multiplication |
| Good for | Everyday computing, ordinary data engineering (Spark) workloads | Computer graphics (pixels = matrices of color values), machine learning/AI (layers of numeric matrix math) |
| Relevance to data engineering | For everyday Spark data processing, GPUs are pretty much irrelevant - CPUs are what you use | Critical for AI/ML workloads - running AI on CPU-only hardware is "very very painfully slow" |

## x86 vs ARM Processor Architecture

Q. What is the difference between an x86 processor and an ARM processor?

A. (From class recording) ARM uses a smaller/simpler set of instructions, which is power efficient (doesn't consume as much energy/heat). x86 is capable of handling a more varied set of instructions to run more complex operations in fewer steps, but requires more power and cooling to run.

| | x86 | ARM |
|---|---|---|
| Instruction set | Complex, handles varied/complex operations in fewer steps | Smaller, simpler set of instructions |
| Power/heat | Requires more power and cooling | Power efficient, generates less heat |
| Typical use | Laptops/desktops | Mobile devices (iOS/Android) - different architectures mean software needs a completely separate build for each; also increasingly popular in data centers for the same energy/heat efficiency reasons |

Note: ARM was originally brought in as mobile device architecture (low energy cost, less heat), but for those exact same reasons it's also become very popular in data centers - most average data center machines today run ARM, not x86.

## Data Centers: Energy and Heat

Q. What are a data center's two biggest operational considerations?

A. (From class recording) How much energy you're consuming (the electricity bill can get very high) and how much heat your computers are generating (data centers need air conditioning, since machines failing from excess heat is a real risk - the less heat generated for the same compute, the better for the data center's operation). A data center is basically a warehouse full of computers, used either for a company's own operations or rented out to third parties - which is what cloud computing fundamentally is (a provider with so many data centers that they can rent out capacity for money).

## Distributed Systems: Peer-to-Peer Networks (contrast to Compute Cluster)

Q. What's the difference between a peer-to-peer network and a compute cluster?

A. (From class recording) Both are types of distributed systems, but a peer-to-peer network functions entirely over the internet (you download a program, and data sharing happens between your computer and any other computer on the internet running that same application). A compute cluster instead requires the machines to be in the same room with a wired connection between them.

| | Peer-to-Peer Network | Compute Cluster |
|---|---|---|
| Connection | Over the internet | Local area network, wired connection |
| Examples | SETI (searching for extraterrestrial intelligence using volunteers' idle compute), Google AlphaFold (protein folding, historically used volunteer peer-to-peer compute), BitTorrent/Napster (illegal file sharing) | The kind of distributed system used in data engineering |
| Security | More exposed - data shared over the internet gives more opportunity for bad actors | More secure - if the cluster isn't even connected to the internet, it's very difficult for a bad actor to access the data |

Note: this is exactly why data engineering is still very much a "cluster forward" style of computing - security via a closed, wired, local network.

## Compute Cluster: How Machines Actually Connect (SSH, Local IPs, Switches)

A. (From class recording) When you plug multiple computers into a router, each computer gets a local IP address. Using that local IP address, you use a program called SSH to access one computer from another - this is the underlying technical basis for sharing data across the cluster's computers. A switch is an optional extra you can plug into your router to get more local IP addresses (i.e. connect more computers). The cluster's router does not need to provide internet access - it optionally can, but all that's actually required is the router being plugged in and an Ethernet cable connecting each computer to it.

## Is MongoDB a Data Lake?

Q. Can MongoDB be used as a data lake?

A. (From class recording) No. Any database could theoretically be used as a data lake if it can accept pretty much any kind of data - but MongoDB specifically has to accept JSON-formatted data, and because of that constraint, it can't really be used as a data lake. A true data lake requires either a regular file system (like the one you browse with your OS's folder manager) or an object store like AWS S3 or Azure Data Lake Storage - something with no format constraint on what you put into it.

## Streaming: Managed Cloud Alternatives to Kafka

Q. What are the cloud-managed alternatives to running your own Kafka cluster?

A. (From class recording) The big problem with Kafka is managing the broker - it runs on a distributed compute cluster with complex mechanisms for tracking/storing messages and handling node failures (electing a new primary node, etc.), which gets complicated fast. Cloud providers offer managed alternatives that remove this complexity:

| Service | Provider | What it replaces |
|---|---|---|
| AWS Kinesis | AWS | Replaces the Kafka broker with a simple cloud-based stream object - no cluster to manage, you just pay per message |
| AWS MSK (Managed Streaming for Kafka) | AWS | Actual Apache Kafka, deployed and managed for you on AWS |
| Azure Event Hubs | Azure | Same concept as Kinesis, on Azure |
| GCP Pub/Sub | Google Cloud | Same concept as Kinesis, on GCP |

The tradeoff: Kinesis (and equivalents) charge per message, which can add up to a hefty bill at high volume - but compare that cost against what it would cost to employ people to manage a Kafka cluster (electricity, hardware replacement, software/hardware updates, on-call for node failures). For many companies, paying per-message is cheaper than the operational overhead of self-managing Kafka.

Note: the producer/broker/consumer architecture is the same across Kafka, MQTT, and AWS SQS - the only real difference is which one is suited to your message volume (SQS/MQTT for smaller scale, Kafka for 1,000+ messages/sec).

## Idempotency: A Concrete Example

A. (From class recording) Suppose a process is instructed to "add `_1` to the end of a column's name." If the process is idempotent, calling it repeatedly still results in just one `_1` suffix - the second call notices the suffix is already there and does nothing further. If it's NOT idempotent, calling it repeatedly keeps appending `_1_1_1_1...` every time it's called, and the more the function gets called, the more the data degrades. This is why designing idempotent processes matters: you want a change made exactly once, regardless of how many times the triggering call happens to fire.

## Bronze Layer Clarification: It's Not the Producer/Broker/Consumer

A. (From class recording) In a streaming + Medallion Architecture pipeline, the Bronze layer is never the producer, broker, or consumer - those are the streaming pipeline's plumbing. The Bronze layer is a downstream storage destination: the consumer receives and processes streamed data, then either writes it into an OLTP database (for immediate/fast access) or into the Bronze layer of a data lakehouse (for eventual long-term analytics). Bronze is an endpoint the data lands at after the consumer is already done with it - not part of the streaming architecture itself.

## Git Flow / Branching Strategy

Q. What is Git Flow, and how does branching work in a team?

A. (From class recording) On an individual project: initiate a git repo, commit your work locally, and optionally push to a remote repo (e.g. GitHub) so it's accessible from other devices - each commit creates a snapshot with a history of everything you worked on. In a team environment, this extends into a branching strategy with (typically) four branch types:

| Branch | Purpose |
|---|---|
| `main` | Maintains the most accurate/stable version of the project |
| `develop` | The branch every developer clones from / branches off of for new work |
| `feature` branches | Created from `develop` for a specific feature; merged back into `develop` via a pull request (PR) once approved |
| `release` | Used for releasing the application/project |

## CI/CD: The Three Environments, and Why CI/CD Was Invented

A. (From class recording) Most data pipelines (and software generally) move through three environments: **Development** (where you do your work), **Testing/QA** (where code is validated before going further), and **Production** (where your actual users/systems consume it - once code is in production, developers shouldn't be touching it directly anymore). CI (continuous integration) covers things like linting, code-quality checks, and running tests when a PR is opened. CD (continuous deployment) is what actually gets validated code from GitHub into production with minimal disruption to users.

Why CI/CD was invented: before it existed, deploying an update meant finding the time of day with the fewest active users, taking the whole system down, manually installing the new code, testing it, then bringing it back online - inconveniencing at least some users every time. CI/CD (which grew out of "extreme programming," an alternative to agile aimed at very frequent production deployments) solved this: push to `main`, the CI/CD pipeline runs, and the production server reloads the code without taking the system down - users may not even notice the update happened. A canary deployment (rolling out to a small subset of pods/servers before fully replacing the old version) is an optional extra safety layer on top of this, not a requirement of CI/CD itself.

## What is "Big Data"? (The Actual Definition)

Q. When does data become "big data"?

A. (From class recording) Data becomes big when it is too large to be efficiently processed by a single computer. Different people will give different definitions, but this is the practical one to use.

Expanded, with the scale examples Evan walked through:

| Data size | Is it "big data"? | Why |
|---|---|---|
| A CSV file with ~1,000 lines | No (from a data engineering standpoint) | Might feel big to a human reading it, but a normal laptop processes it near-instantaneously - write a script, run it, done |
| Gigabytes | Borderline | A normal laptop can still do it, but it starts taking real time - 30 minutes, an hour, maybe three hours for a script to finish |
| Terabytes | Yes | Trying to process this on a laptop becomes a serious problem |
| Petabytes (one step above terabytes) | Definitely yes | Requires distributed systems, full stop |

The key insight: "big data" isn't about a fixed size threshold - it's about the point where a single machine can no longer process the data efficiently, which is exactly why distributed systems, clusters, and tools like Spark exist. Most of what modern data engineering is about is figuring out what kind of system can process a given amount of data, and how to make that processing as efficient as possible - which is why so much of the discipline is really about infrastructure (computer hardware or cloud-based substitutes for it), not just "working with data."

## The Three Major Ways Data Gets Used in an Organization

A. (From class recording) There are basically three major ways that data is used once a data engineer has made it available:

| # | Use | Description | Data Engineer's role |
|---|---|---|---|
| 1 | Visualization | Maps, charts, dashboards - the kind of output seen in news broadcasts or business reporting (upward/downward trends, geographic breakdowns, etc.) | Lower-level expectation - a component of big data engineering, but not the major focus of this course, since it's less about infrastructure |
| 2 | Machine learning models | Data is fed into a model as training input | The data engineer prepares/pipes the data and the training infrastructure - writing the model itself is generally the data scientist's job (though AI now makes writing simple models much easier for anyone) |
| 3 | Enhancing LLMs (RAG) | Using an organization's own data to make an LLM able to answer questions it otherwise couldn't (a public model like ChatGPT has no knowledge of your company's internal data) | Building the data pipeline that feeds an LLM's retrieval system |

Note on #3 - the "AI genie" example: suppose you run a website and want to ask an AI "what were our quarterly earnings for the past eight quarters?" A general-purpose LLM can't answer that because its training never saw that data. What you can do instead is feed your own data to the AI so it can answer questions grounded in that data - this is what a RAG (Retrieval-Augmented Generation) pipeline is for. LLMs can also be run locally/privately rather than communicating with a major provider, depending on an organization's needs.

## How AI Has Changed the Data Space (and Where Agentic AI Fits)

A. (From class recording, in response to a student question about agentic AI) Before AI became mainstream (~2019, when Evan started), data scientists were mostly statisticians - they took data and applied statistical methods to produce maps/charts/presentations so management could make decisions. That was the main way data added value to a business.

Since AI, most of that "make charts and summaries" work can be done directly by an LLM. So a data scientist's output has shifted from "make the charts" toward "how do we use this data to train a model" and "how do we use this in a RAG pipeline" (making an LLM's knowledge include your organization's own data).

Agentic AI specifically (an AI agent performing tasks on a regular, autonomous basis) has NOT penetrated the big data world as much as other AI advances, because:
- Data is one of the most economically important assets many companies have, and letting an autonomous agent make consequential decisions with it (e.g. cloud deployment choices, how to distribute data across a cluster) isn't considered safe/trustworthy enough yet.
- Data engineering involves a lot of interconnected moving parts and judgment calls that current agentic AI isn't reliable enough to be trusted with unsupervised.

Career implication Evan gave: data engineers are likely to be among the last technical disciplines AI fully replaces, precisely because of that complexity. The more effectively you learn to direct/prompt AI now (rather than being replaced by developers who can), the more valuable you remain - since AI in its current form is a prompt-and-response system that still needs a knowledgeable human to guide it well, even as it continues to automate more of what "average" development work looks like today.

