---
title: Training 6 - Distributed Systems & HDFS
description: HPC, fault tolerance, cluster managers (RAFT/ZAB), Hadoop cluster components, HDFS blocks/replication, the CAP theorem, MapReduce, the small file problem, a Hive intro, and file compression/storage formats.
sidebar:
  order: 6
---

Teacher: Evan Flint

Syllabus Day 7 (per file numbering) - actual coverage: Distributed Systems fundamentals (HPC, fault tolerance, cluster managers). Note: this continues the pacing drift already visible in `Training 5.md`, which covered the Course Roadmap's Day 7 topic (dimensional schemas/medallion architecture) inside the Day 6 file - so this session's real content lines up more closely with the roadmap's Day 8 topic ("Distributed Systems + HDFS") than its own nominal Day 7 slot.

---

# High Performance Computing (HPC)

Q. What does HPC stand for?

A. (Teacher's definition) HPC - High Performance Computing.

Expanded: HPC refers to using clusters of many machines working together to achieve computing power far beyond what a single machine could provide - the general category of infrastructure (supercomputers, distributed clusters) that the rest of this training's concepts (fault tolerance, cluster managers) exist to make practical and reliable. In a data engineering context, this is the same underlying idea as a Spark/Hadoop cluster: many nodes pooling compute and storage to process data at a scale no single machine could handle alone.

---

# Fault Tolerance

Q. Why does fault tolerance become more important as a distributed system grows?

A. (Teacher's definition) For each additional node that you add to a distributed system, the chances of any one of the nodes failing at any given time increases.

Expanded: this is the core trade-off underlying every distributed system design choice in this course - scaling out (adding more machines/nodes) buys more compute/storage capacity, but each additional node is one more independent thing that can crash, lose network connectivity, or run out of disk, so the overall probability that *some* node is failing at any given moment climbs steadily with cluster size. A system with 1,000 nodes should expect failures to be a routine, constant background event, not a rare edge case - which is exactly why distributed systems (HDFS, Kafka, Spark, etc.) are built from the ground up around expecting and automatically recovering from node failure, rather than treating it as exceptional.

| Cluster size | Effect on failure probability |
|---|---|
| Small (few nodes) | Node failure is a rare, notable event |
| Large (hundreds/thousands of nodes) | Some node failing at any given moment becomes the expected, routine state |

This is also the underlying reason replication (e.g. HDFS block replication) and automatic leader re-election (via cluster managers, below) exist - both are direct responses to the fact that failure isn't an if, it's a when, once a cluster is large enough.

---

# Cluster Manager

Q. What is a cluster manager, and what algorithms do they typically rely on?

A. (Teacher's definition) Cluster managers are usually based on algorithms such as RAFT or ZAB.

Expanded: a cluster manager is the component responsible for keeping a distributed system's nodes coordinated - tracking which nodes are alive, electing a leader/coordinator node, and keeping shared cluster state consistent across all nodes even as individual nodes fail and restart. RAFT and ZAB are both **consensus algorithms** - protocols that let a group of independent nodes agree on a single shared value (most commonly, "who is the current leader") even when some nodes are slow, unreachable, or crash mid-process. Without a consensus algorithm, a network split or timing issue could cause two nodes to both believe they're the leader at once (a "split-brain" scenario) - RAFT/ZAB exist specifically to make that impossible.

**Examples of cluster managers (teacher's list):**
- **Hadoop YARN** - resource/cluster manager for the Hadoop ecosystem
- **KRaft** - Apache Kafka's own cluster manager (built on the RAFT algorithm)
- **Zookeeper** - coordination service used by many distributed systems, built on the **ZAB** (ZooKeeper Atomic Broadcast) algorithm
- **Kubernetes** (in some cases) - Kubernetes' own control plane performs cluster-manager-style coordination (tracking node health, scheduling, leader election among control-plane replicas) for a container cluster

| Cluster Manager | Underlying Algorithm | Used By |
|---|---|---|
| Hadoop YARN | - | Hadoop ecosystem (resource scheduling across a Hadoop cluster) |
| KRaft | RAFT | Apache Kafka (replaced Kafka's older Zookeeper-based coordination) |
| Zookeeper | ZAB | Historically Kafka, Hadoop, and many other distributed systems needing coordination |
| Kubernetes | etcd's Raft-based consensus | Container orchestration clusters (in some cases, per teacher's note) |

Expanded (correction): the teacher's list mixes two different kinds of system. Raft and ZAB are used by **coordination/consensus services**, not by resource managers like YARN.

| Category | Job | Examples | Consensus algorithm |
|---|---|---|---|
| Resource manager / scheduler | Allocates CPU and memory to jobs and containers | YARN, Kubernetes scheduler, Mesos, Spark Standalone Master | None of its own (YARN uses ZooKeeper for ResourceManager HA) |
| Coordination / consensus service | Stores small critical metadata, elects leaders, prevents split-brain | ZooKeeper (ZAB), etcd (Raft, used by Kubernetes), Kafka KRaft (Raft, Kafka's metadata quorum) | ZAB / Raft |

Consensus quorums use an **odd number of nodes** (3 or 5): a write needs a majority, so a cluster of n nodes survives (n-1)/2 failures (3 nodes survive 1, 5 survive 2). An even number adds cost without adding fault tolerance.

**Worth remembering for later Kafka material:** KRaft's name is a direct nod to RAFT - Kafka moved away from depending on a separate Zookeeper cluster for coordination toward managing consensus internally via KRaft, removing Zookeeper as an external dependency. This will likely come up again in `Training 13.md`'s Kafka coverage.

**Note on Kubernetes' "(in some cases)":** Kubernetes itself isn't always described as a "cluster manager" in the same breath as YARN/Zookeeper/KRaft, since it's more commonly framed as a container orchestrator - but its control plane relies on `etcd` (a Raft-based key-value store) to do exactly the same job those other tools do: track cluster/node state and keep it consistent across control-plane replicas. This connects forward to `Training 42.md`'s dedicated Kubernetes coverage later in the course.

---

## How a Cluster Manager Actually Works: Heartbeats

Q. For a cluster manager to work, what has to be installed, and how do nodes know about each other?

A. (Teacher's definition) For a cluster manager to work, an instance of it must be installed on all computers in the cluster. These instances know that each other exist, and they send messages to each other periodically known as "heartbeats."

---

Q. What is a heartbeat message?

A. (Teacher's definition) A heartbeat message is just a message from one node to another, and then a confirmation message that the node sends back to the originator.

Expanded: this is the actual mechanism underlying everything described in the Cluster Manager section above - "knowing which nodes are alive" isn't magic, it's each node's cluster-manager instance periodically pinging every other node it knows about and listening for a reply. If a node's heartbeat confirmation doesn't come back within an expected time window, the cluster manager treats that node as failed/unreachable and can trigger recovery behavior (leader re-election via RAFT/ZAB, rescheduling work elsewhere, replicating data to a healthy node, etc.) - this is the concrete, mechanical link back to the Fault Tolerance section's point that failure has to be *detected* automatically before a system can *respond* to it automatically.

| Step | What happens |
|---|---|
| 1. Send | Node A's cluster-manager instance sends a small "heartbeat" message to Node B |
| 2. Confirm | Node B immediately sends a confirmation message back to Node A |
| 3. Repeat | This exchange repeats on a fixed interval, between each worker and the master/leader (not between every pair of nodes) |
| 4. Detect failure | If a confirmation doesn't arrive within the expected window, Node B is presumed down/unreachable, triggering the cluster manager's failure-handling logic |

Expanded (correction): heartbeats are not sent between every pair of nodes; all-to-all heartbeats would grow as O(n^2) messages. In Hadoop, **workers heartbeat to the master**: each DataNode sends a heartbeat to the NameNode every 3 seconds (and the NameNode marks it dead after about 10 minutes of silence), and each NodeManager heartbeats to the YARN ResourceManager. In Raft, the **leader** sends heartbeats to its followers. (Some gossip-based systems like Cassandra exchange state with a few random peers each round, which also avoids all-to-all.)

**Prerequisite worth flagging:** the teacher's definition specifies the cluster manager software itself must be installed on *every* machine in the cluster, not just a central coordinator - each node runs its own instance, and those instances are what talk to each other via heartbeats. This is different from, say, a single external monitoring tool checking on machines from the outside.

---

## What Happens When a Heartbeat Fails

Q. What does the algorithm do if a heartbeat message is sent and no response is received?

A. (Teacher's definition) If a heartbeat message is sent and NO response is received, then the algorithm considers the node that did not respond to be down.

---

Q. Does the cluster automatically keep working when a node goes down?

A. (Teacher's definition) In some cluster managers there are automatic ways to adjust the cluster's functionality in order to continue operating when a node goes down, and in all cases, a notification is sent to the system administrator to give human attention to the problem.

Expanded: this is the direct continuation of the heartbeat send/confirm mechanism above - a missing confirmation isn't just logged and ignored, it's the actual trigger event the cluster manager acts on. Two things happen from there, and the teacher's wording draws a clear line between them:

| Response | Guaranteed? | What it looks like |
|---|---|---|
| Automatic self-healing (e.g. leader re-election via RAFT/ZAB, rescheduling work to a healthy node, replicating data elsewhere) | **Not always** - "in some cluster managers" | Depends on the specific tool/algorithm; this is what lets a cluster stay available *without* waiting on a human |
| Notification to the system administrator | Only if monitoring/alerting is configured (see correction below) | Alerting so a human is aware and can investigate/intervene, even if the cluster already recovered on its own |

The key distinction to hold onto for an interview: automatic recovery is a *capability*, not a *given* - it varies by which cluster manager/algorithm is in play. Human notification, by contrast, is treated as non-negotiable in every case, because even a cluster that self-heals still had a real failure that needs root-cause investigation (a disk failing, a network partition, bad hardware) - the automation buys uptime, it doesn't remove the need for a person to eventually look at why the node went down.

Expanded (correction): the cluster manager itself does not automatically notify anyone. It records the node as dead (in logs and its UI/metrics). A human is alerted only if monitoring and alerting are set up on top, e.g. Ambari/Cloudera Manager alerts, Prometheus + Alertmanager, CloudWatch alarms or PagerDuty. Setting that up is part of running a production cluster.

**Interview line (what happens when a DataNode dies):** "The DataNode stops sending heartbeats. After about 10 minutes the NameNode marks it dead, finds every block that now has fewer than 3 replicas, and copies them from surviving replicas to other DataNodes. Clients just read from another replica in the meantime, and monitoring alerts the on-call engineer."

---

# Hadoop Cluster Components

Q. What does YARN stand for?

A. (Teacher's definition) YARN - Yet Another Resource Negotiator.

---

Q. Where does YARN fit into the overall Hadoop cluster?

A. (Teacher's definition) YARN is one of the 3 things that makes up a Hadoop cluster.

Expanded: this places YARN (already introduced above as a cluster-manager example, built for resource/cluster management) inside the bigger picture of what "Hadoop" actually refers to - Hadoop isn't a single program, it's a stack of (classically) three core components that each handle a different responsibility, working together as one cluster:

| Component | Role |
|---|---|
| **HDFS** (Hadoop Distributed File System) | Distributed storage layer - splits files into blocks and replicates them across nodes |
| **YARN** (Yet Another Resource Negotiator) | Cluster/resource manager - tracks node health and schedules/allocates compute resources for jobs across the cluster |
| **MapReduce** | Distributed processing/compute engine - the original programming model for actually running jobs across the cluster's data |

This ties directly back into the Cluster Manager section above: YARN is Hadoop's *specific* answer to "who tracks which nodes are alive and coordinates work across them" - the same job Zookeeper/KRaft/Kubernetes perform for their respective systems, just scoped to Hadoop's own storage (HDFS) and processing (MapReduce) layers. Expanded (YARN components):

| YARN component | Role |
|---|---|
| ResourceManager | Cluster-wide master; tracks resources and schedules applications |
| NodeManager | Agent on each worker; launches and monitors containers, reports to the ResourceManager |
| ApplicationMaster | One per application (e.g. per Spark job); negotiates containers from the ResourceManager and tracks its tasks |
| Container | A bundle of CPU and memory on one node where a task (or Spark executor) runs |

**Interview line:** "In YARN the ResourceManager allocates resources cluster-wide, a NodeManager runs on each worker, each application gets its own ApplicationMaster that requests containers, and the work runs inside those containers."

Worth flagging forward to `Training 8.md`'s Hive + Spark Intro coverage: Spark largely emerged as a faster alternative to MapReduce, but still commonly runs *on top of* YARN and reads/writes HDFS - so YARN's role as cluster manager often persists even once MapReduce itself has been replaced.

---

# HDFS

Q. What does HDFS stand for, and what is it?

A. (Teacher's definition) HDFS - Hadoop Distributed File System. HDFS is a distributed data storage system and the primary location where you will store data in most regular Hadoop clusters.

---

Q. Is HDFS a database?

A. (Teacher's definition) HDFS is NOT a database, it's a file system.

---

Q. How do you actually interact with HDFS?

A. (Teacher's definition) The way you will interact with HDFS is that you'll have access to a normal Linux terminal and you'll send commands to HDFS related to data storage via the command line. If you want to put data from the local system into HDFS, for example, you use:
```bash
hdfs dfs -put my_file_name.csv
```

Expanded: this is the storage component from the Hadoop Cluster Components table above, expanded on its own. The "NOT a database" distinction matters because HDFS has no query engine, tables, schema, or SQL of its own built in - it's purely a place to durably store files (typically split into blocks and replicated across nodes, per the Fault Tolerance section above), the same conceptual role an object store like S3 plays in a lakehouse (`Training 5.md`). Anything database/table-like sitting "on top of" HDFS - Hive tables, Spark DataFrames reading Parquet files, etc. - is a separate layer built on top of plain file storage, not a feature of HDFS itself.

The command-line interaction model is also worth noting precisely: you're not given some separate HDFS-specific shell/GUI - you use the same familiar Linux terminal (`Training 1.md`), just prefixing storage-related commands so they get routed to HDFS instead of the local filesystem (the classic pattern being `hdfs dfs -<command>`, mirroring familiar Linux commands like `-put`, `-get`, `-ls`, `-mkdir`).

| HDFS is... | HDFS is NOT... |
|---|---|
| A distributed **file system** (blocks, replication, files/directories) | A database (no schema, tables, or SQL engine of its own) |
| Interacted with via Linux terminal commands | A separate GUI/dedicated client required to use it |

---

## HDFS Components (NameNode, DataNode, HA)

Q. What are the components of HDFS?

A.

| Component | Role |
|---|---|
| **NameNode** | Master. Holds the file system namespace and block map (which blocks make up each file and where every replica lives) in memory. Stores no file data |
| **DataNode** | Worker. Stores the actual blocks on local disk, serves reads/writes, sends heartbeats and block reports to the NameNode |
| **Secondary NameNode** | Checkpoint helper only: periodically merges the edit log into the fsimage. **Not** a failover node |
| **Standby NameNode (HA)** | Hot standby kept in sync through JournalNodes; ZooKeeper (ZKFC) fails over to it if the active NameNode dies |

Expanded: **write path:** the client asks the NameNode where to put each block, then streams the block through a **pipeline** of DataNodes (client -> DN1 -> DN2 -> DN3); acknowledgements flow back along the pipeline. **Read path:** the client gets block locations from the NameNode, then reads each block directly from the closest DataNode. **Rack awareness:** with the default policy, replica 1 goes on the writer's node (or a random node), replicas 2 and 3 on two different nodes in another rack, so losing a whole rack never loses a block.

**Interview line:** "The NameNode holds metadata, DataNodes hold the blocks. The Secondary NameNode only does checkpoints; high availability comes from a Standby NameNode with ZooKeeper failover."

---

## Replication

Q. What is replication?

A. (Teacher's definition) Replication - storing the same data multiple times in multiple locations.

---

Q. What is the standard replication factor in Hadoop?

A. (Teacher's definition) The standard replication factor in Hadoop is 3. So therefore, you can lose your data in 2 different places and still have one copy of it left.

Expanded: this is HDFS's concrete answer to the Fault Tolerance section's core problem above - since node failure is expected at scale, HDFS never stores a file's blocks on just one machine. Instead, each block is copied to multiple different nodes (the "replication factor" controlling exactly how many copies), so if one node holding a copy goes down, the data is still fully available from the others. A replication factor of 3 means every block exists on three separate nodes at once - typically spread across different physical machines (and often different racks) specifically so a single node or rack failure can never make data unavailable.

| Concept | Meaning |
|---|---|
| Replication | Storing identical copies of the same data across multiple nodes |
| Replication factor | The number of copies kept per block (Hadoop's default/standard: **3**) |
| Why 3 specifically | Balances fault tolerance (can lose 2 copies and still have the data) against the storage overhead cost of keeping extra copies |

This directly ties back to the earlier Fault Tolerance and Heartbeat sections: when a node holding a replica misses its heartbeats and is marked down, HDFS's NameNode (the metadata/coordinator component - see HDFS Components above) can direct the cluster to re-replicate that node's blocks onto a healthy node, restoring the replication factor back to 3 without any data loss.

---

# CAP Theorem

Q. What is the CAP Theorem?

A. (Teacher's definition) CAP stands for:
- **Consistency**
- **Availability**
- **Partition Tolerance**

Expanded: the CAP Theorem states that a distributed system can only fully guarantee **two of these three** properties at the same time, never all three at once - a direct consequence of the same reality driving every other topic in this training (nodes fail, networks partition, and a system has to make a trade-off about how to behave when that happens).

| Property | Meaning |
|---|---|
| **Consistency (C)** | Every node returns the same, most up-to-date data for a given read, no matter which node answers the request |
| **Availability (A)** | Every request receives a (non-error) response, even if it isn't guaranteed to be the most recent data |
| **Partition Tolerance (P)** | The system keeps operating even when network communication breaks down between nodes (a "partition" - some nodes can't talk to others) |

**Why you can't have all three:** partitions are a fact of distributed systems (the same node-failure/network-unreliability reality from the Fault Tolerance section above) - so Partition Tolerance isn't really optional to give up in practice. That leaves the real-world choice as **CP vs. AP** once a partition actually happens:

| Choice | Behavior during a partition | Example use case |
|---|---|---|
| **CP** (Consistency + Partition Tolerance) | Refuses/delays requests to affected nodes rather than risk returning stale data | Systems where correctness matters more than uptime (e.g. financial transactions) |
| **AP** (Availability + Partition Tolerance) | Keeps answering requests from every node, even if some return slightly stale data until the partition heals | Systems where staying up matters more than perfect freshness (e.g. social media feeds, shopping carts) |

This is the theoretical backbone behind why different distributed systems are built with fundamentally different trade-offs, and it'll likely resurface directly in `Training 7.md`'s Distributed Systems + HDFS material and again whenever NoSQL/MongoDB (`Training 14.md`) comes up.

**Where does HDFS land: CP or AP?** Teacher's definition (in response to a student question about whether HDFS keeps all its replicas in sync instantly): "HDFS is not what we call strongly consistent. Instead, HDFS is highly available... Hadoop, as a system, chose the availability side of that. So Hadoop systems can be highly available, but they do not guarantee strong consistency."

Expanded (correction): in CAP terms, HDFS is usually classified as **CP**, not AP. That's the answer most interviewers expect:

| HDFS behavior | Why it points to CP |
|---|---|
| A single active **NameNode** holds all file metadata | One source of truth; there's no second copy of the metadata that could disagree |
| A write goes through a **pipeline** to every replica before it is acknowledged | Once a file is written and closed, every reader sees the same data |
| If the NameNode is down or cut off, clients can't read or write | It gives up availability rather than serve inconsistent data (NameNode HA reduces downtime but keeps one active NameNode) |

What Evan was likely describing: HDFS is built to **tolerate failures**. If a DataNode dies, its blocks are **re-replicated in the background** to get back to 3 copies, and a file that is still being written may not be visible to readers until it is closed. That's fault tolerance and replication lag, not an AP design.

**CP vs AP examples:**

| CP (consistency first) | AP (availability first) |
|---|---|
| HDFS, HBase, ZooKeeper, etcd, traditional RDBMS with synchronous replication | Cassandra, DynamoDB (default eventually consistent reads), CouchDB, DNS |

Interview line: *"HDFS favors consistency. It's CP: one NameNode is the source of truth, and if it's unavailable the file system stops rather than return inconsistent data. Replication gives fault tolerance, not eventual consistency of reads."*

---

# MapReduce: Memory vs. Disk

Q. Does MapReduce perform all of its operations the same way?

A. (Teacher's definition) In MapReduce, some operations are performed in memory, and other operations are performed on disk.

---

Q. What is Disk I/O?

A. (Teacher's definition) Disk I/O - I/O stands for input and output.

Expanded: this distinction is the classic performance bottleneck story behind MapReduce (the processing component from the Hadoop Cluster Components table above) - and it's exactly the reason Spark later replaced it as the dominant engine. **I/O (Input/Output)** just means reading data in and writing data out; **Disk I/O** specifically means that read/write is happening against physical disk storage rather than RAM. Disk I/O is orders of magnitude slower than in-memory access, so which one an operation uses has a major effect on job speed.

| Location | Speed | MapReduce behavior |
|---|---|---|
| In-memory (RAM) | Fast | Some intermediate operations can be held/processed in memory |
| Disk | Slow (relative to memory) | MapReduce classically writes intermediate results (e.g. between the Map and Reduce phases) back to disk before the next stage reads them |

**Why this matters going forward:** MapReduce's heavy reliance on writing intermediate results to disk between stages is the single biggest reason it's considered slow compared to Spark - Spark's core innovation (`Training 8.md`/`Training 9.md`) is keeping intermediate data in memory across multiple processing steps instead of round-tripping through disk I/O every time, which is why Spark jobs can run substantially faster than equivalent MapReduce jobs on the same cluster.

---

## MapReduce Phases: Word Count

Q. How does MapReduce work? Walk through word count.

A.

| Phase | What happens | Word count example |
|---|---|---|
| Input split | Each mapper gets one block/split of the input | Mapper 1 gets "a b a", Mapper 2 gets "b c" |
| Map | Emit key/value pairs | (a,1) (b,1) (a,1) / (b,1) (c,1) |
| Shuffle & sort | Group all values by key and send each key to one reducer (written to disk) | a -> [1,1], b -> [1,1], c -> [1] |
| Reduce | Aggregate each key's values | (a,2) (b,2) (c,1) |
| Output | Written to HDFS | One file per reducer |

Expanded: MapReduce relies on **data locality**: YARN schedules each map task on a node that already holds that block ("move compute to the data"), so the input isn't shipped over the network. The shuffle is the expensive part, which is the same wide-dependency idea as a Spark shuffle.

**Interview line:** "Mappers read local blocks and emit key/value pairs, the shuffle groups pairs by key and sends each key to one reducer, and reducers aggregate. For word count, map emits (word, 1) and reduce sums the ones."

---

## Consistency Models

Q. What is the difference between strong and eventual consistency, and what is a quorum?

A. **Strong consistency:** every read returns the latest acknowledged write. **Eventual consistency:** replicas may briefly return stale data, but converge if writes stop. A **quorum** system with N replicas, writing to W and reading from R of them, is strongly consistent for reads when **R + W > N** (the read set always overlaps the latest write).

Expanded: e.g. Cassandra with N = 3, W = 2 (QUORUM), R = 2 (QUORUM): 2 + 2 > 3, so reads see the latest write. With R = 1, W = 1 it is faster and more available but only eventually consistent. This is the practical knob behind CP vs AP.

---

# HDFS Blocks

Q. What size are HDFS blocks?

A. (Teacher's definition) For a while, the default HDFS block size was 128 MB. Today, it's 256 MB.

Expanded (correction): the Apache Hadoop default block size (`dfs.blocksize`) is still **128 MB** (since Hadoop 2.x; it was 64 MB in Hadoop 1.x). 256 MB is a common **tuned** value on some clusters and distributions, not the default. Say 128 MB in an interview (this also matches `Training 0.md`).

Expanded: HDFS doesn't store a file as one single unit - it splits each file into fixed-size chunks called **blocks**, and each of those blocks is what actually gets replicated across nodes (tying directly back into the Replication section above - each block gets its own 3 copies spread across different nodes, not the file as a whole). The default grew from 64 MB (Hadoop 1.x) to 128 MB (Hadoop 2.x and 3.x), and many clusters tune it higher - bigger blocks mean fewer, larger chunks to track/coordinate per file.

| Era | Default HDFS block size |
|---|---|
| Hadoop 1.x | 64 MB |
| Hadoop 2.x / 3.x (current default) | 128 MB |
| Common tuned value | 256 MB (configured, not default) |

| Concept | Meaning |
|---|---|
| Block | A fixed-size chunk that a file gets split into for storage in HDFS |
| Why chunk into blocks at all | Lets a single large file be spread/replicated across many different nodes rather than needing to fit on one machine, and lets MapReduce/Spark process different blocks of the same file in parallel across the cluster |

---

Q. Is the HDFS block size fixed?

A. (Teacher's definition) The block size can be edited in the Hadoop config.

Expanded: 128 MB is just the default, not a hard limit - the block size is a configurable cluster setting, so a team can tune it up or down depending on their data/workload (e.g. larger blocks for huge files to reduce per-block coordination overhead, smaller blocks if a workload needs finer-grained parallelism). This sets up the very next topic directly: choosing too small a block size, or storing files smaller than the block size, is exactly what leads into the Small File Problem below.

---

# The Small File Problem

Q. What is the Small File Problem?

A. (Teacher's definition) If you put a lot of small files on a Hadoop system, it's not only going to be inefficient for storage, it will also slow down data processing speeds.

Expanded: this is the direct consequence of the two sections just above - HDFS blocks (128 MB by default) and the NameNode-style metadata coordinator implied by earlier sections are built around the assumption of relatively large files. A "small file" here means any file significantly smaller than the block size - every file, no matter how tiny, still consumes a full block-tracking metadata entry, so millions of small files bloat the amount of metadata the cluster's coordinator has to hold in memory, which is the storage-inefficiency half of the problem.

The processing-speed half comes from how MapReduce/Spark parallelize work: they typically launch one task per block/file. A single 128 MB file processes as one efficient task, but the same 128 MB spread across thousands of tiny files means thousands of tiny tasks - and the overhead of starting/scheduling/tearing down each task can end up costing more than the actual work being done, dragging overall job speed down even though the total data volume hasn't changed.

| Effect | Why it happens |
|---|---|
| Storage inefficiency | Every file (regardless of size) still needs its own block metadata entry, bloating the coordinator's in-memory bookkeeping |
| Slower processing | MapReduce/Spark launch roughly one task per file/block - many tiny files means many tiny tasks, and per-task overhead dominates over actual work |

**Common fix (context for later material):** compacting many small files into fewer, larger files before/during ingestion - this is part of why the Bronze -> Silver refinement step in the Medallion Architecture (`Training 5.md`) often exists, and it'll likely resurface when Spark/Delta compaction patterns come up later in the course.

---

# Scalability

Q. What is Scalability?

A. (Teacher's definition) How big can you make a process?

Expanded: framed this way, scalability is really asking "what's the ceiling on how much work/data a system can take on before it breaks down or stops being practical?" This connects directly back to the earlier HPC section - the whole reason distributed clusters exist is that a single machine has a hard ceiling on how big a process can get (limited CPU, RAM, disk on one box), while a distributed system raises that ceiling by spreading the process across many machines instead of one.

---

Q. What is Vertical Scalability?

A. (Teacher's definition) Vertical Scalability - taking one system and improving its components to be able to handle more things.

---

Q. What is Horizontal Scalability?

A. (Teacher's definition) Horizontal Scalability - taking a system and creating multiple identical systems which will work together.

| Type | Teacher's definition | Limit |
|---|---|---|
| **Vertical scaling** ("scale up") | Improving one system's own components (more CPU/RAM/disk) to handle more | Hits a hard ceiling - eventually no bigger machine is available/affordable |
| **Horizontal scaling** ("scale out") | Creating multiple identical systems that work together | In principle much higher ceiling, at the cost of the distributed-systems complexity covered throughout this training (fault tolerance, heartbeats, replication, CAP theorem trade-offs) |

This is likely the on-ramp to `Training 7.md`'s "Horizontal scaling" coverage per the Course Roadmap - everything in this file so far (fault tolerance, cluster managers, HDFS, replication, CAP theorem) is effectively the machinery that *makes* horizontal scaling actually work in practice, since "multiple identical systems working together" only helps if the system can coordinate them, tolerate their failures, and keep data consistent/available across them.

---

# Hive

Q. What is Hive?

A. (Teacher's definition) Hive is the OLAP Data Warehouse framework for Hadoop systems.

Expanded: this connects Hadoop back to the OLAP/data warehouse material from `Training 5.md` and the Analytical Databases section there, which already flagged Hive as "old school Hadoop stack data warehouse - a bit outdated." Hive sits *on top of* the Hadoop components already covered in this file - it doesn't replace HDFS or YARN, it gives them a SQL-like interface (HiveQL) so data sitting as plain files in HDFS can be queried and organized like warehouse tables, with YARN still handling resource scheduling and MapReduce (or later, Spark) still doing the actual execution underneath.

| Layer | Role |
|---|---|
| HDFS | Stores the raw files Hive tables point to |
| YARN | Schedules/allocates the compute resources Hive's queries run on |
| MapReduce (or Spark) | Actually executes the query as a distributed job |
| **Hive** | Sits on top of all three - the SQL/table/OLAP layer analysts actually interact with |

This is the same "engine + storage" layering idea introduced with Databricks Delta Lake / DuckDB + Iceberg in `Training 5.md` - Hive is Hadoop's own native version of putting a warehouse-style interface over raw distributed file storage, just older and generally considered slower than modern alternatives (Spark SQL, Presto/Trino, or a cloud warehouse) per that same Training 5 note.

---

## HiveQL

Q. What is Hive SQL / HiveQL, and how does it actually run?

A. (Teacher's definition) Hive SQL (sometimes called HiveQL) is an SQL query language system which operates basically as a wrapper for MapReduce.

Expanded: this is the mechanical detail underneath the Hive table above - when someone writes a `SELECT ... GROUP BY ...` in HiveQL, Hive doesn't execute that query directly itself; it translates the SQL into one or more MapReduce jobs (the same MapReduce processing engine from the Hadoop Cluster Components and Memory-vs-Disk sections above), which then actually run across the cluster via YARN. This is exactly why classic Hive queries inherit MapReduce's disk-I/O-heavy performance characteristics - a HiveQL query is, under the hood, paying the same intermediate disk-write cost between stages that plain MapReduce jobs do, which is a big part of why Hive is considered slow compared to Spark SQL (which skips MapReduce and executes directly via Spark's in-memory engine instead).

| Layer | What happens |
|---|---|
| You write | A SQL-like query in HiveQL |
| Hive translates | The query into one or more MapReduce jobs |
| YARN schedules | Resources for those MapReduce jobs across the cluster |
| MapReduce executes | The actual distributed processing (including its disk I/O between stages) |

---

## Metastore (General Definition)

Q. What is a Metastore, generally?

A. (Teacher's definition) A Metastore is a system which is designed to store metadata (schemas - so column names and data types, indexes, etc).

Expanded: this is the general concept the "Hive Metastore" is one specific implementation of - a metastore itself never holds the actual data (rows/files), only the *description* of that data: what columns exist, what type each column is, what indexes/partitions exist, and (per the sections above) where the underlying files actually live in storage. Separating "the data" from "the description of the data" is precisely what makes Schema on Read possible (below) - the metastore is the lookup table an engine consults to know how to interpret raw files as a structured table.

---

## Hive Metastore

Q. What is the Hive Metastore?

A. (Teacher's definition) The Hive Metastore is the only part of Hive that's still modern.

Expanded: the Metastore is Hive's metadata catalog - it stores the table definitions (schema, column names/types, partition info, and the location of the underlying files in HDFS/object storage) *separately* from the actual query execution engine (HiveQL -> MapReduce, covered above). The teacher's framing here is significant: while HiveQL-over-MapReduce is considered outdated/slow (per the HiveQL section above and `Training 5.md`'s "old school... a bit outdated" note), the Metastore itself survived as genuinely useful infrastructure - modern engines like Spark SQL, Presto/Trino, and even some cloud warehouses can point at a Hive Metastore to discover table schemas and file locations, without ever running an actual MapReduce job.

| Hive component | Status per teacher's note |
|---|---|
| HiveQL -> MapReduce execution | Outdated, slow (disk I/O-heavy, per the HiveQL section above) |
| **Hive Metastore** | Still modern - widely reused as a shared table-metadata catalog by newer engines |

**Why this matters going forward:** this is the reason "Hive Metastore" keeps showing up as a term even in fully modern lakehouse stacks that have nothing to do with running actual Hive/MapReduce queries - it's become a de facto standard *catalog format* that other tools adopted, independent of Hive's own (now-outdated) execution engine. Worth watching for this same idea to resurface around `Training 8.md`'s Hive + Spark Intro material.

---

Q. Are there other metastores besides Hive's?

A. (Teacher's definition) Other metastores include: The AWS Glue Data Catalog.

Expanded: this confirms the point just above - the "metastore" concept generalized beyond Hive itself. AWS Glue Data Catalog is Amazon's own managed metadata catalog, doing the same job (tracking table schemas, partitions, and file locations for data sitting in S3) that the Hive Metastore does for HDFS-based data - and it's actually **Hive-Metastore-API-compatible**, meaning tools built to talk to a Hive Metastore (Spark, Presto/Trino, Athena) can point at Glue's catalog instead without needing different code. This will come up again directly in `Training 21.md`'s AWS Glue coverage.

---

Q. Why do metastores matter so much in Big Data today?

A. (Teacher's definition) Metastores are used all over the Big Data world today in order to implement a data storage technique called Schema on Read, which is the foundation of the biggest Big Data today.

Expanded: this is the payoff that ties the whole Hive/Metastore/Lakehouse thread together. **Schema on Read** means raw data can be dumped into storage (HDFS, S3, etc.) in whatever native format it arrives in - no schema has to be defined or enforced at write time. The schema only gets applied *later*, at query time, by consulting a metastore that says "here's how to interpret these files as a table" (column names, types, partitioning). This is the exact opposite of a traditional relational database's **Schema on Write**, where the schema has to be fully defined before any data can be loaded in at all.

| | Schema on Write | Schema on Read |
|---|---|---|
| When schema is defined/enforced | Before data is loaded (traditional RDBMS, data warehouses) | At query time, via a metastore (Hive Metastore, AWS Glue Data Catalog) |
| Data must match schema up front? | Yes - load fails if it doesn't fit | No - raw files land as-is; interpretation happens later |
| Flexibility | Lower - schema changes require careful migration | Higher - different queries/tools can interpret the same raw files differently if needed |
| Where it's used | OLTP databases, classic data warehouses | Data lakes / lakehouses (HDFS, S3 + Hive Metastore/Glue Catalog) |

This directly connects back to `Training 5.md`'s Data Lakehouse vs. Data Warehouse comparison, which already described a warehouse as schema-on-write and a lakehouse as schema-on-read "with enforcement added by the table format" - the metastore (Hive Metastore or Glue Data Catalog) is precisely the piece of infrastructure that makes schema-on-read practical: without a shared, queryable catalog telling every engine how to interpret the raw files, "schema on read" would just be a pile of unstructured files with no way to reliably query them as tables at all.

---

## Internal (Managed) vs. External Tables

Q. What's the difference between an internal (managed) table in Hive vs. an external table? **(Common interview question)**

A. (Teacher's definition) The answer to the interview question is - if you drop an internal/managed table, then you lose both the data and the metadata. If you drop an external table, you ONLY lose the metadata - the original data stays where it is.

Expanded: this is a direct, concrete application of the Metastore's "data vs. description of data" separation covered above. An **internal/managed table** means Hive considers itself the owner of both the metadata entry (in the Metastore) *and* the actual data files - so `DROP TABLE` cleans up both. An **external table** means Hive only owns the metadata entry (schema, column types, and a pointer to wherever the data actually lives); the data itself was written and is owned by something else (another pipeline, another tool), so dropping the table only removes Hive's *knowledge* of it - the files are untouched.

| | Internal (Managed) Table | External Table |
|---|---|---|
| What Hive owns | Both the metadata **and** the data | Only the metadata (a pointer to the data's location) |
| Effect of `DROP TABLE` | Deletes **both** metadata and underlying data | Deletes **only** the metadata - original data stays where it is |
| Typical use case | Data created and fully managed within Hive | Data shared across multiple tools/pipelines that shouldn't be destroyable from inside Hive |

**Why this is a favorite interview question:** it directly tests whether you understand that the Metastore only stores metadata (per the General Metastore definition above) - the "internal vs. external" distinction is really just a policy setting on *whether Hive is allowed to delete the actual files* when the metadata entry goes away, not two fundamentally different storage mechanisms.

---

## Partitioning vs. Bucketing

Q. What is Partitioning?

A. (Teacher's definition) Partitioning is subdividing the rows of a table physically - the partitions are stored as separate sub-files on disk.

Expanded: partitioning splits one logical table into multiple physical sub-files/directories on disk, grouped by the value of one or more chosen columns (commonly something like `date` or `region`). The payoff is query performance: if a query filters on the partition column (e.g. `WHERE order_date = '2026-09-18'`), the engine can skip reading every other partition's files entirely - known as **partition pruning** - instead of scanning the whole table. This is a direct, practical extension of the HDFS Blocks/Small File Problem material above: partitioning is a *deliberate*, logical way of splitting a table's physical storage, as opposed to the accidental fragmentation the Small File Problem describes.

| Concept | Meaning |
|---|---|
| Partitioning | Physically splitting a table's rows into separate sub-files/directories, grouped by a column's value |
| Why it helps | Lets queries filtering on the partition column skip reading irrelevant partitions entirely (partition pruning) |
| Common partition columns | Date, region, category - anything frequently filtered on and with a manageable number of distinct values |

---

Q. What is Bucketing?

A. (Teacher's definition) Bucketing is another way of subdividing a table - it's not done at the file level but rather involves a hash being applied to particular rows of the table.

Expanded: where partitioning splits a table by the literal value of a column (creating one sub-file/directory per distinct value or value-group), bucketing instead runs a **hash function** over a chosen column's value for each row, and the hash result determines which bucket that row lands in. This solves a problem partitioning has: partitioning on a column with a huge number of distinct values (e.g. `customer_id`) would create an unmanageable number of tiny partitions, but hashing into a fixed number of buckets (e.g. 32 buckets) gives an even, predictable spread of rows regardless of how many distinct values the column actually has.

| | Partitioning | Bucketing |
|---|---|---|
| How rows are grouped | By the literal value of a column | By the output of a hash function applied to a column |
| Number of groups | Varies with the data (one per distinct value/value-group) | Fixed, chosen in advance (a set number of buckets) |
| Best for | Columns with a manageable number of distinct values, frequently filtered on (date, region) | Columns with very high cardinality (e.g. customer_id, user_id), or when even data distribution across files matters more than filter pruning |
| Main benefit | Partition pruning - skip irrelevant partitions entirely on a filtered query | Even distribution of data + efficient joins/sampling on the bucketed column |

**Terminology note worth double-checking:** the teacher's phrasing ("not done at the file level") is worth confirming in context - in most standard Hive/Spark documentation, bucketing *does* still result in a fixed number of physical files per partition (one file per bucket), it's just that which file a row lands in is determined by a hash rather than by the literal partition-column value the way partitioning works. Worth clarifying with Evan if this comes up again, since the distinction that matters most for an interview is *hash-based fixed-count buckets* vs. *value-based variable-count partitions*, not necessarily "file-level vs. not."

**What actually gets hashed?** A student's follow-up question in class assumed bucketing always hashes an entire row - teacher's clarification: "A hash can be of literally anything. So it can be from just the value of an individual cell. It can be an entire row. It can be an entire column. It just has to be a string before you pass it to the hashing algorithm." Expanded (correction): hash functions work on **bytes**, not specifically strings, and Spark (Murmur3) and Hive hash the typed column values directly; nothing has to be converted to a string first. Also worth knowing: Spark bucketing and Hive bucketing use **different hash functions**, so a table bucketed by one engine is not treated as bucketed by the other.

So bucketing by a single column (e.g. hashing just the `date` value) is completely normal - the hash input isn't required to be the whole row, just whatever column(s) you choose to bucket by, converted to a string first if it isn't one already.

---

# File Compression Formats

## Snappy

Q. What is Snappy?

A. (Teacher's definition) Snappy is a file compression format with an emphasis of speed of compression/decompression.

Expanded: Snappy (originally developed by Google) trades off maximum compression ratio in exchange for very fast compress/decompress speed - it won't shrink a file as small as heavier algorithms (like gzip) can, but it costs far less CPU time to compress and decompress. In a Big Data/Hadoop-Spark context, this trade-off usually wins: since jobs are constantly reading and writing huge volumes of data across a cluster, spending less CPU time per read/write (Snappy) is often more valuable overall than saving disk space (heavier compression), especially when disk/object storage is comparatively cheap and processing time is the actual bottleneck.

| | Snappy | Heavier compression (e.g. gzip) |
|---|---|---|
| Priority | Speed of compression/decompression | Smaller final file size |
| Compression ratio | Lower (files stay somewhat larger) | Higher (files shrink more) |
| CPU cost | Low | Higher |
| Common pairing | Parquet/ORC files in Spark/Hadoop pipelines | Archival storage, network transfer where size matters more than speed |

This connects back to the Disk I/O material from the MapReduce section above - compression format choice is itself a speed/size trade-off decision, and Snappy is the common default precisely because Big Data workloads are usually more sensitive to processing speed than to storage footprint.

---

# File Storage Formats

## ORC

Q. What is ORC?

A. (Teacher's definition) ORC - Optimized Row Columnar - the default data format for Hive. Like Parquet, ORC is also columnar, able to be partitioned, and able to be distributed, and compressed.

Expanded: ORC is a file storage format (distinct from Snappy, which is a *compression* codec that can be applied on top of a storage format like ORC or Parquet). Being **columnar** means data is physically stored column-by-column rather than row-by-row - the same structural idea already covered for Pandas DataFrames (`Training 2.md`), just applied to on-disk file storage instead of in-memory data: a query that only needs a few columns out of a wide table can read just those columns' data off disk, skipping the rest entirely, which is a major speed win for typical OLAP-style analytical queries (aggregations, `GROUP BY`, `SUM`, etc. over a handful of columns across millions of rows).

| Property | What it means for ORC |
|---|---|
| Columnar | Stores data column-by-column, letting queries read only the columns they need |
| Partitionable | Can be split into partitions (per the Partitioning section above) |
| Distributable | Files can be spread across a cluster's nodes (same distributed storage model as HDFS blocks/replication) |
| Compressible | Can have a compression codec (e.g. Snappy, above) applied to shrink file size |
| Default for | Hive |

**Worth comparing to Parquet directly** (per the teacher's own comparison) - both are modern columnar formats sharing the same core properties (columnar, partitionable, distributable, compressible), which is why they're so often mentioned together; ORC is more closely associated with the Hive/Hadoop ecosystem specifically, while Parquet is the more common default across the broader Spark/lakehouse world (Databricks Delta Lake, `Training 5.md`, is built on Parquet).

---

## Avro

Q. What is Avro?

A. (Teacher's definition) Avro - basically a compressed JSON file with a flexible schema.

Expanded (correction): Avro is **not** JSON. It is a compact **binary, row-based** format whose **schema is written in JSON** and stored in the file header. Compression is an optional codec (e.g. Snappy, Deflate) applied to blocks of records. The "JSON-like" part is the flexible, nested schema, not the data encoding.

---

Q. When should you use Parquet/ORC vs. JSON/Avro?

A. (Teacher's definition) Parquet and ORC are good for batch processing, JSON and Avro are good for streaming.

---

Q. What's a second advantage Avro has, beyond compression?

A. (Teacher's definition) Aside from being compressed, a second advantage that Avro has is the Avro schema - that facilitates implementing schema evolution.

Expanded: Avro is a **row-based** format (unlike ORC/Parquet's columnar layout) that stores each record as a compact, schema-tagged binary blob - conceptually close to JSON's flexible, nested structure, but compressed and with the schema itself embedded/versioned alongside the data. That "flexible schema" property is the key: Avro supports **schema evolution** (adding/removing/renaming fields over time) more gracefully than a rigid columnar format, which matters a lot for streaming, where individual events arrive one at a time and the producer's schema might change between deployments without every consumer being upgraded simultaneously.

The batch-vs-streaming split follows directly from row-based vs. columnar layout:

| | Parquet / ORC (columnar) | JSON / Avro (row-based) |
|---|---|---|
| Best for | Batch processing | Streaming |
| Layout | Column-by-column | Row-by-row (whole record at once) |
| Why it fits that workload | Batch jobs scan large volumes and often only need a few columns - columnar read-pruning wins big | Streaming processes one record/event at a time as it arrives - reading/writing a whole row at once is the natural unit, and columnar's per-column layout doesn't help when there's no large batch to scan yet |
| Schema flexibility | Less flexible - schema is more rigid once written | More flexible - Avro's embedded schema versioning handles evolving event shapes well |

This connects directly forward to `Training 13.md`'s Kafka coverage (where individual streamed messages are the unit of work, matching Avro/JSON's row-at-a-time model) and back to the ORC/Parquet section above (matching Hive/batch-style analytical queries scanning large historical tables).

---

## Schema Evolution: Beyond Avro

Q. Is Avro the only format that handles schema evolution?

A. (Teacher's definition) Schema evolution can be handled with file formats such as Avro, Protobuf, Iceberg, and Delta, among others.

Expanded: this broadens the schema-evolution concept beyond just Avro - it's a capability multiple modern formats/technologies provide, not something unique to one tool. Worth noting these fall into two different categories that solve schema evolution at different layers:

| Format | Category | Role |
|---|---|---|
| **Avro** | Row-based serialization format | Embeds/versions the schema alongside individual records - covered above |
| **Protobuf** | Row-based serialization format | Google's binary serialization format, similar role to Avro - schema defined separately (`.proto` files) with built-in support for adding/removing fields over time |
| **Iceberg** | Open Table Format | Tracks schema changes at the *table* level (on top of underlying Parquet/ORC/Avro files) - lets columns be added/renamed/dropped without rewriting existing data files |
| **Delta** (Delta Lake) | Open Table Format | Same table-level schema evolution/enforcement role as Iceberg. Created by Databricks but open source (Apache 2.0, Linux Foundation); Databricks adds proprietary features on top (`Training 5.md`) |

**Why this distinction matters:** Avro/Protobuf solve schema evolution at the *individual record/message* level (useful for streaming, per the section above), while Iceberg/Delta solve it at the *whole table* level (useful for a data lakehouse's Bronze/Silver/Gold tables, `Training 5.md`'s Medallion Architecture) - a real pipeline commonly uses both together, e.g. Avro-encoded Kafka messages landing into Delta/Iceberg tables downstream.

---

# Additional Notes (from class)

## The Small File Problem in Practice: JPMorgan Chase Story

Q. What is a real-world example of the small file problem?

A. (Teacher's definition, real-world account) "I actually have personal experience with the small file problem. This was actually something that I encountered while I was at JPMorgan Chase... I was in charge of their data archival system... our output was usually between 500 gigabytes and one and a half terabytes for one file. But the system that we had partitioned that data so that the partitions were only one megabyte in size... What would happen is that I would start the archival job and a few hundred of those partitions would get archived, but then one would fail. And if one failed, the entire job failed... Ultimately, the method that I arrived on was Spark's repartition method... I took these one megabyte partitions and turned them into 10 gigabyte partitions. And as soon as they were 10 gigabyte partitions, they would all archive, no problem. And we archived our entire backlog in a matter of like two weeks."

Expanded: a concrete, real production illustration of the Small File Problem section above - the archival job wasn't failing because of bad code, it was failing because of file architecture: thousands of 1MB partitions meant thousands of chances for a single archival step to fail, and any one failure killed the whole job (with no simple retry available, per additional constraints the teacher didn't detail). The fix wasn't smarter code, it was consolidating file count - using Spark's `repartition` method (an "odd choice" per the teacher, since `coalesce` is the more commonly expected tool for reducing partition count, but benchmarks in this specific case showed `repartition` performed better) to go from many tiny partitions to few large ones, which is exactly the "compact many small files into fewer, larger files" fix already noted in the Small File Problem section above, just with real numbers attached (500GB-1.5TB files, 1MB partitions -> 10GB partitions, a 2-week backlog cleared once fixed). Worth remembering `repartition` vs. `coalesce` as a concrete pair of Spark methods to investigate further once Spark coverage begins next week.

**Also worth noting (teacher's aside):** the small file problem is largely obsolete for teams using an object store (S3, ADLS, GCS) instead of raw HDFS - "the nice thing about cloud is that all that stuff is the company's problem," since the cloud provider handles fault tolerance/replication internally and doesn't expose the same fixed-block-size architecture that makes small files expensive on HDFS specifically.

Expanded (correction): only half of this is true. The cloud removes the **NameNode memory** part of the problem, but small files still hurt on S3/ADLS/GCS: every file costs a separate GET/LIST request (latency and per-request cost), Spark still schedules roughly one task per small file, and Delta/Iceberg metadata grows with file count. That is exactly why compaction exists (Delta `OPTIMIZE`, auto-compaction, Iceberg `rewrite_data_files`). Aim for files of roughly 128 MB to 1 GB.

---

## Optimization Principle: Less Work, Not Faster Work

Q. What is the key principle behind most optimizations?

A. (Teacher's definition) "Most optimizations are actually not faster methods to do something. They're methods that involve less work at all."

Expanded: this was stated directly as the takeaway from the "why is Spark faster than MapReduce" discussion (see the MapReduce Memory vs. Disk section above) - a live correction of a common misconception. A student asked whether Spark's speed advantage just comes down to memory being faster than disk; the teacher's answer was explicitly that this reasoning is wrong: "The reason that Spark is faster than MapReduce is because there are a bunch of data transfers that just simply don't happen in a Spark job, but which need to happen in a MapReduce job" - it's not that the same operations run faster, it's that Spark skips operations MapReduce is forced to do (the repeated disk<->memory round-trips). The same principle was illustrated with a second example: querying an unpartitioned billion-row sales table for one month's data means scanning all billion rows (a full table scan), while querying a *partitioned* table means the engine only has to look at that one partition - e.g. 100,000 rows instead of a billion - finishing much faster not because each row is processed any quicker, but because 99.99% of the rows were never touched at all. This is a generalizable interview-ready framing worth remembering: **first ask "can I avoid doing this work entirely?" before asking "can I do this work faster?"**

---

## Schema Evolution: Naming Gotcha

Q. Is it "schema evolution" or "schema evaluation"?

A. (Teacher's definition) "It is Schema Evolution and it is not Schema Evaluation. It's very common for people to say Schema Evaluation, but that is quickly dispelled when you think about what you're actually doing."

Expanded: worth flagging as a common mix-up - the correct term is **Schema Evolution** (the schema *evolves*/changes over time as source systems add, remove, or rename columns, per the Schema Evolution section above), not "Schema Evaluation." The teacher's reasoning for why "Evolution" is the right word: the system is adapting to a schema that is genuinely changing over time (evolving), not just checking/evaluating a fixed schema once. Small thing, but exactly the kind of terminology slip an interviewer might notice.

---

## Introduction to Spark

Q. What is Spark, and why did it replace MapReduce?

A. (Teacher's definition) "Spark is the big giant technology in data engineering. When Spark came out, it basically revolutionized the entire field. And while open source regular Spark is not necessarily the most important thing anymore, every single modern data processing system either is exactly Spark or it is absolutely based on Spark."

Expanded: this is the teacher's first formal introduction of Spark in this training (setting up the following week's material, per the teacher's own framing: "today we've basically taken everything we learned this week, and it's all been leading up to when we talk about Spark"). It naturally continues the MapReduce discussion above - Spark is presented as MapReduce's direct successor and replacement, not an unrelated new technology.

**Spark is everywhere, even when it isn't literally "Spark" (teacher's examples):**

| System | Relationship to Spark |
|---|---|
| AWS Glue | Not exactly Spark, but "an AWS special syntax special situation version of Spark" |
| Google Cloud Dataproc | Written in Apache Beam syntax - Beam is a syntax/API layer, not a processing engine itself, and Beam's backend is based on Spark |
| Databricks | Founded by some of the original Spark developers; the original product concept was literally "Spark plus a data warehouse in a single cloud service." Per the teacher: "Databricks is Spark. Spark is Databricks. Everything that you do in Databricks is based on Spark." |

Expanded (correction - Dataproc row): **Dataproc** is Google's managed Spark/Hadoop service: you run normal Spark jobs on it, no Beam involved. **Dataflow** is Google's managed **Apache Beam** service, and it runs on Google's own Dataflow runner. Beam is a portable API that *can* run on Spark or Flink runners, but it is not "based on Spark".

| GCP service | What it is | You write |
|---|---|---|
| Dataproc | Managed Spark/Hadoop clusters (and serverless Spark) | Normal PySpark/Scala Spark |
| Dataflow | Managed Apache Beam runner (batch + streaming) | Beam pipelines (Java/Python) |

**Why Spark took over - two reasons (teacher's definition):**

1. **Speed** - "Before Spark came out, we had MapReduce. MapReduce did some operations on disk and others in memory. In Spark, we did all of our processing in memory. Turns out if you do that, your average processing time is about 100 times faster, give or take." (See the MapReduce Memory vs. Disk section above, and the Optimization Principle note above for *why* this is true - it's the elimination of disk round-trips, not memory being inherently faster.)
2. **The DataFrame API** - Spark 1.0's original data structure was the **RDD** (Resilient Distributed Dataset) - "a large distributed list of values or a distributed array, basically," conceptually the same lineage as a plain Python list processed with `map`/`filter`/`reduce`, just distributed across a cluster at a much bigger scale (the same lineage MapReduce itself came from, per the MapReduce section above). With Spark 2.0, the Spark developers noticed Python's Pandas library becoming popular for data processing and built an equivalent into Spark itself - "Spark SQL," built around a **DataFrame**, that behaves like a Pandas DataFrame but at distributed scale. Per the teacher: "Spark SQL is the underlying thing of pretty much all data processing technologies right now. In an average data engineering job... it is probably either going to be working with a Spark DataFrame or some other framework's equivalent of a Spark DataFrame."

Expanded (correction): two dates and one claim need fixing. DataFrames arrived in **Spark 1.3** (2015, with Spark SQL); **Spark 2.0** (2016) unified the DataFrame and Dataset APIs and introduced `SparkSession`. And Spark does not do *all* processing in memory: it spills to disk when data doesn't fit and writes shuffle files to local disk. Its speed comes from avoiding HDFS writes **between** stages, optional in-memory caching, and DAG/query optimization (see the Optimization Principle note above). The "100 times faster" figure is a best-case benchmark for iterative in-memory workloads, not a typical number.

**Spark is a processing engine, not a storage system (important distinction):**

Teacher's definition: "Spark does not itself have a data storage system in it. So it does not ever make sense to say that you are storing data in Spark. Spark is the processor, it is not the storage, and so you always need to use Spark with a separate storage system."

Expanded: this directly parallels the earlier Hadoop Cluster Components table (HDFS = storage, YARN = cluster manager, MapReduce = processing) - Spark occupies the *processing* role in a modern stack, the same role MapReduce used to fill, but it always needs to be paired with something else for actual storage (HDFS, S3, a Hive/Glue-catalog-backed table, etc.). A worked example the teacher gave: on an on-prem Hadoop stack, new data lands in HDFS -> Spark reads it, processes it into a warehouse-shaped format -> Spark writes the result into Hive -> BI tools (Tableau, Power BI) query Hive. Spark is the middle step connecting storage to storage, never the storage itself. This is also why Databricks' original pitch mattered so much: it was explicitly "Spark **plus** a place to store your data" - solving the one thing plain Spark deliberately doesn't do on its own.

**ETL vs. ELT with Spark:** a student asked whether Spark always uses ETL. Teacher's answer: "Spark can be adapted to ELT purposes, and that's the way that it's normally used in Databricks today. But ELT methods in Spark did come in later Spark versions. So yeah, its original concept was to be an ETL tool. ETL was the way that things were done in data engineering until about two or three years ago. It's only been since then that ELT became the dominant way of doing things." This connects directly to the ETL/ELT material and the "Taylor Swift problem" push-vs-pull framing from `Training 5.md` - Spark's own history (ETL-first, ELT added later) mirrors the industry-wide shift described there.

---

# Homework Assignment: Weekend Project - Containerized Sales Report Pipeline

The full weekend project prompt (Bash -> Docker Compose -> Python/Pandas -> PostgreSQL -> SQL aggregation -> `output/sales_report.csv`) is in `homework/assignment/Homework - Training 6 (Assignment).md`.

---
