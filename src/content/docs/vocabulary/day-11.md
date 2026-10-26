---
title: Day 11 Vocabulary
description: Glossary of terms and definitions from the Training 11 notes.
sidebar:
  order: 11
---

Vocabulary — Study Guide Day 11

Source: notes/Training 11.md

## Spark-Hive Integration
- **Hive Metastore** — The catalog service storing Hive's database, table, schema and storage-location metadata.
- **enableHiveSupport()** — SparkSession builder option that connects Spark to a Hive metastore so it can read and write Hive tables.
- **hive.metastore.uris** — Config setting giving the Thrift address of a remote Hive metastore, e.g. `thrift://localhost:9083`.
- **spark.sql.hive.metastore.version** — Config setting telling Spark which Hive metastore version to talk to.
- **spark.sql.hive.metastore.jars** — Config setting telling Spark where to get Hive client jars, e.g. `maven` to download them.
- **spark.sql.warehouse.dir** — Config setting for the default storage location of managed tables and databases.
- **Port 9083** — Default port of the Hive metastore Thrift service.
- **Thrift** — Apache RPC framework that Spark and Hive clients use to communicate with the metastore.
- **RPC (Remote Procedure Call)** — Calling a function that runs on another process or server over the network.
- **saveAsTable** — Spark write method that saves a DataFrame as a table registered in the metastore catalog.
- **write.mode("overwrite")** — Write mode that replaces any existing data in the target table.
- **Managed table** — A Hive table whose data files are stored and controlled by Hive in the warehouse directory.
- **CSV / LOAD DATA bridge** — The earlier workaround of exporting CSVs and loading them into Hive, replaced here by native writes.
- **CREATE DATABASE IF NOT EXISTS** — SQL statement creating a database only if it is missing; needed because `saveAsTable` does not create parent databases.

## JDBC and Postgres Reading
- **JDBC (Java Database Connectivity)** — Java API for connecting to relational databases through a driver.
- **JDBC URL** — Connection string such as `jdbc:postgresql://localhost:5432/<db>` identifying the database.
- **java.util.Properties** — Java key-value object holding JDBC connection settings like user, password and driver.
- **org.postgresql.Driver** — The PostgreSQL JDBC driver class.
- **spark.read.jdbc** — Spark method that reads a database table into a DataFrame over JDBC.
- **sys.env** — Scala map of environment variables, used to read passwords instead of hard-coding them.
- **Port 5432** — PostgreSQL's default port.
- **Medallion layers (bronze / silver / gold)** — Raw, cleaned and business-ready data layers used as schema names.
- **Dimension table (dim_)** — A table holding descriptive attributes such as customer, product or date.
- **Fact table (fact_)** — A table holding measurable events such as sales or payments, linked to dimensions.

## Metastore Backend and Troubleshooting
- **Derby (embedded)** — Lightweight Java database used as Hive's default metastore backend; only one JVM can hold it at a time.
- **metastore_db** — Folder created by an embedded Derby metastore, a sign Spark silently fell back to a local metastore.
- **spark-warehouse** — Local folder Spark creates for managed tables when no warehouse directory is configured.
- **Silent fallback** — Spark appearing to succeed by using a local embedded metastore instead of the real one.
- **HiveServer2** — Hive's query service that clients like beeline connect to, on ports 10000 and 10002.
- **beeline** — Hive's JDBC command-line client for running queries against HiveServer2.
- **hive-site.xml** — Hive's main configuration file.
- **javax.jdo.option.ConnectionURL** — hive-site.xml setting for the JDBC URL of the metastore's backend database.
- **ConnectionDriverName / ConnectionUserName / ConnectionPassword** — hive-site.xml settings for the metastore backend's driver and credentials.
- **schematool** — Hive tool that creates the metastore tables in a backend DB, e.g. `schematool -dbType postgres -initSchema`.
- **hive --service metastore** — Command that starts a standalone Hive metastore Thrift service.
- **DBS table** — Metastore backend table storing each database's metadata and location.
- **TTransportException / Broken pipe** — Thrift error when a connection is accepted but nothing real answers the RPC.
- **Connection refused** — Error when no process is listening on the target port.
- **NoSuchDatabaseException** — Spark error when writing to a database that does not exist in the metastore.
- **MetaException** — Hive metastore server-side error, e.g. failing to create a table directory.
- **Shared filesystem** — Storage such as HDFS or S3 that the metastore and all Spark clients resolve paths against identically.
- **HDFS (Hadoop Distributed File System)** — Hadoop's distributed storage layer.
- **Tez** — Execution engine Hive uses to run queries.
- **/proc/net/tcp6** — Linux file listing a system's IPv6 TCP sockets, used to see which ports are listening.

## Docker Operations
- **docker exec** — Runs a command inside a running container; `-d` runs it detached.
- **docker commit** — Saves a container's current state as a new image, used as a snapshot.
- **docker inspect** — Shows a container's detailed configuration such as mounts and network.
- **docker stop / rm / run** — Stop, remove and create containers.
- **Bind mount (-v)** — Maps a host directory into a container so both see the same files.
- **host.docker.internal** — Docker Desktop hostname that routes from a container back to the host machine.
- **Default bridge network** — Docker's default network, which does not resolve container names via DNS.
- **PID 1** — The first process in a container, its init or entrypoint process.
- **Stale PID file** — A leftover process-ID file that falsely makes a service think it is already running.
- **--entrypoint** — docker run flag overriding the image's startup command; committing such a container bakes the override in.
- **Port mapping** — Docker exposing a container port on the host; the port can be mapped even if nothing inside listens on it.

## Synthetic Data Generation
- **generate_sales.py** — The teacher's Python script that inserts batches of synthetic sales rows into bronze to simulate ongoing new data.
- **psycopg2** — Python library for connecting to and querying PostgreSQL.
- **Cursor** — Database object used to execute SQL statements and fetch results.
- **conn.commit()** — Makes inserted rows permanent in the database.
- **fetchone() / fetchall()** — Cursor methods returning one result row or all result rows.
- **Parameterized query (%s)** — SQL with placeholders filled safely by the driver rather than string concatenation.
- **COALESCE** — SQL function returning the first non-null argument, used to default to 0.
- **SUBSTRING ... FROM** — SQL function extracting part of a string, e.g. dropping the `T` prefix.
- **CAST** — SQL conversion of a value to another type, such as INTEGER.
- **~ (regex match)** — PostgreSQL operator testing whether a string matches a regular expression.
- **ANY(array)** — SQL condition matching a value against any element of an array.
- **Batch size** — Number of records generated or inserted per run.
- **random.choice / randint / uniform** — Python functions picking a random list item, integer or float.
- **timedelta** — Python type representing a duration, used to compute past dates.
- **isoformat()** — Formats a date as `YYYY-MM-DD`.
- **if __name__ == "__main__"** — Python idiom that runs code only when the file is executed directly.
- **Environment variable** — Value set in the shell, such as `PG_PASSWORD`, read by code to avoid hard-coded secrets.
