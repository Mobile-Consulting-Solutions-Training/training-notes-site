---
title: "Training 11 - Postgres to Hive with Scala Spark"
description: "The teacher's finished Postgres to Hive Scala Spark job, why native metastore integration failed against the hive-server container, and the generate_sales.py data generator."
sidebar:
  order: 11
---

Teacher: Evan Flint

Syllabus Day 12 (per file numbering) - actual coverage: continuing the Postgres -> Hive Scala Spark pipeline, now with the teacher's finished version - reads AND writes, using native Spark-Hive metastore integration (`enableHiveSupport()` + `hive.metastore.uris`) instead of the CSV/`LOAD DATA` bridge approach documented in `Training 8.md`/`hive-spark-etl-walkthrough.md`. Note: this continues the pacing drift already visible in `Training 6.md`-`Training 10.md`.

# The Teacher's Finished Postgres -> Hive Scala Job

```scala
import org.apache.spark.sql.{SparkSession, DataFrame}
import java.util.Properties

object HelloWorld {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession
      .builder
      .master("local[*]")
      .appName("Test Scala App")
      .config("hive.metastore.uris", "thrift://localhost:9083")
      .config("spark.sql.hive.metastore.version", "3.1.3")
      .config("spark.sql.hive.metastore.jars", "maven")
      .enableHiveSupport()
      .getOrCreate()

    val JDBC_URL = "jdbc:postgresql://localhost:5432/sample_database"

    val jdbcProperties = new Properties()
    jdbcProperties.setProperty("user", "evan")
    jdbcProperties.setProperty("password", sys.env("PG_PASSWORD"))
    jdbcProperties.setProperty("driver", "org.postgresql.Driver")

    def readPostgres(table: String): DataFrame = {
      spark.read.jdbc(JDBC_URL, table, jdbcProperties)
    }

    val bronze = readPostgres("bronze.sales")
    val silver = readPostgres("silver.sales")
    val customerTable = readPostgres("gold.dim_customer")
    val dateTable = readPostgres("gold.dim_date")
    val departmentTable = readPostgres("gold.dim_department")
    val employeeTable = readPostgres("gold.dim_employee")
    val officeTable = readPostgres("gold.dim_office")
    val productTable = readPostgres("gold.dim_product")
    val factPaymentTable = readPostgres("gold.fact_payment")
    val factSalesTable = readPostgres("gold.fact_sales")

    bronze.show()
    silver.show()
    customerTable.show()
    dateTable.show()
    departmentTable.show()
    employeeTable.show()
    officeTable.show()
    productTable.show()
    factPaymentTable.show()
    factSalesTable.show()

    // Native Spark-Hive write - no CSV bridge, no LOAD DATA
    bronze.write.mode("overwrite").saveAsTable("bronze.sales")
    silver.write.mode("overwrite").saveAsTable("silver.sales")
    customerTable.write.mode("overwrite").saveAsTable("gold.dim_customer")
    dateTable.write.mode("overwrite").saveAsTable("gold.dim_date")
    departmentTable.write.mode("overwrite").saveAsTable("gold.dim_department")
    employeeTable.write.mode("overwrite").saveAsTable("gold.dim_employee")
    officeTable.write.mode("overwrite").saveAsTable("gold.dim_office")
    productTable.write.mode("overwrite").saveAsTable("gold.dim_product")
    factPaymentTable.write.mode("overwrite").saveAsTable("gold.fact_payment")
    factSalesTable.write.mode("overwrite").saveAsTable("gold.fact_sales")

    spark.stop()
  }
}
```

Expanded: this is the direct resolution of the open question flagged back in `Training 9.md`/`Training 10.md` - does native Spark-Hive metastore integration (via `hive.metastore.uris` + `enableHiveSupport()`) actually work, as an alternative to the CSV/`LOAD DATA` bridge we built and proved working in `Training 8.md`? The teacher's script now includes real `.write...saveAsTable(...)` calls - no intermediate file, no `docker cp`, no beeline `LOAD DATA` - Spark writes directly into Hive's catalog via the shared metastore. See `hive-spark-etl-scala/` (a new, separate Scala project, adapted to connect to our own `warehouse_practice`/`ajackson` Postgres and our own `hive-server` container) for the adapted version and whether it actually works against our infrastructure.

**Adaptations needed for our environment** (the teacher's version points at his own personal setup):

| Teacher's value | Our value | Why |
|---|---|---|
| `jdbc:postgresql://localhost:5432/sample_database` | `jdbc:postgresql://localhost:5432/warehouse_practice` | Our actual database (per `Training 5.md`/`Training 8.md`) |
| `user = "evan"` | `user = "ajackson"` | Our actual Postgres user |
| `hive.metastore.uris = thrift://localhost:9083` | Same, unchanged | We already exposed port `9083` on our `hive-server` container while investigating this exact question - genuine TCP connect confirmed, but not yet confirmed as a *working* metastore |
| Table names (`bronze.sales`, `gold.dim_customer`, etc.) | Unchanged | These already match our own warehouse's real table names exactly |

**Real risk worth flagging before running:** if `hive.metastore.uris` doesn't actually connect to a genuine, reachable metastore, Spark can fail *silently* rather than erroring - `enableHiveSupport()` without a working metastore connection can fall back to creating its own local embedded Derby metastore (a `metastore_db` folder in the current directory) and a local `spark-warehouse` folder, giving the *appearance* of success while never touching the real Hive tables at all. Worth explicitly checking the actual Hive tables (via `beeline`) after running this, not just trusting that the Scala program exited without an error.

---

## Confirmed: native metastore integration does NOT work against our `hive-server` container

Built `HiveSparkETL` (a new, separate Scala/sbt project - see `hive-spark-etl-scala/`) with the adapted version of the teacher's code above and actually ran it end-to-end. Result:

- All 10 `readPostgres(...)` calls and `.show()` calls succeeded - the Postgres JDBC side of this was never in question.
- The very first `.write.mode("overwrite").saveAsTable("bronze.sales")` failed with `org.apache.thrift.transport.TTransportException: java.net.SocketException: Broken pipe`, thrown from inside `HiveClientImpl.databaseExists` while trying to talk to `thrift://localhost:9083`.

**Diagnosed the actual cause by inspecting the `hive-server` container directly** (`docker exec hive-server ps -ef`, `/proc/net/tcp6`, and `hive-site.xml`):

| What we checked | What we found |
|---|---|
| Processes running in the container | Only `HiveServer2` (`hive-service-4.0.1.jar`) - no separate `metastore` process |
| Actual listening ports (`/proc/net/tcp6`) | Only `10000` and `10002` (HiveServer2's own ports) - **nothing listening on 9083 at all** |
| `hive-site.xml` | No `hive.metastore.uris` entry, no `javax.jdo.option.ConnectionURL` - metastore backend defaults to embedded Derby (`/opt/hive/metastore_db`) |

So `thrift://localhost:9083` was never a real metastore endpoint - Docker maps the port, but nothing inside the container is bound to it. The TCP connection gets accepted at the Docker-proxy layer (so Spark doesn't fail immediately at `getOrCreate()`), but breaks the moment Spark tries to send an actual Thrift RPC, producing the "Broken pipe" rather than a clean "Connection refused." And even if we started a standalone `hive --service metastore` process to genuinely listen on 9083, it would very likely conflict with HiveServer2's own embedded-Derby lock, since Derby's embedded mode only allows one JVM to hold the database file at a time - this isn't a one-line config fix, it's a container re-architecture (separate metastore service + a real shared backend DB, e.g. Postgres).

**Update: decided to pursue the container rework after all.** Rebuilt `hive-server`'s metastore backend for real:

1. `docker commit hive-server hive-server-backup-pre-metastore` - safety snapshot before touching anything.
2. Created a new `hive_metastore` database in the existing `ajackson` Postgres container (reusing the same superuser credentials as `warehouse_practice`).
3. Copied the `postgresql-42.7.4.jar` driver into `/opt/hive/lib` inside the container (Hive only shipped with a Derby driver by default).
4. Added `javax.jdo.option.ConnectionURL` (`jdbc:postgresql://host.docker.internal:5432/hive_metastore` - `host.docker.internal` is Docker Desktop's route from inside any container back to the Mac's host network, needed since the two containers only share the default `bridge` network, which does **not** do container-name DNS resolution), `ConnectionDriverName`, `ConnectionUserName`, `ConnectionPassword`, and `hive.metastore.uris=thrift://localhost:9083` to `hive-site.xml`.
5. Ran `schematool -dbType postgres -initSchema` inside the container - created all 83 real Hive metastore tables in Postgres.
6. Started `hive --service metastore` as a *second*, independent process inside the still-running container (`docker exec -d`) - confirmed via `/proc/net/tcp6` that port `9083` is now a genuine listener, backed by Postgres, with zero conflict with HiveServer2's own (still-embedded-Derby) process, since HiveServer2 itself was left untouched to avoid restarting the container's PID 1.

**Result so far:** the original `Broken pipe` is completely gone - Spark now genuinely reaches the metastore over Thrift. Progress through the remaining errors, each one a real, expected step rather than a connectivity failure:
- `NoSuchDatabaseException: SCHEMA_NOT_FOUND` for `bronze` - `saveAsTable` doesn't auto-create parent databases; fixed by adding `spark.sql("CREATE DATABASE IF NOT EXISTS ...")` for `bronze`/`silver`/`gold` at the top of `HiveSparkETL.scala`.
- `MetaException(...bronze.db/sales is not a directory or unable to create one)` - the real one. `CREATE DATABASE` used Spark's own default `spark.sql.warehouse.dir`, which resolved to a Mac-local path (`/Users/leaveittolou/IdeaProjects/HiveSparkETL/spark-warehouse`). That path got stored in the metastore as the database's location, and the metastore **server** (inside the container, confirmed via the exception coming back through `ThriftHiveMetastore$..._result.read()` - server-side, not client-side) then tried to `mkdir` that exact string on *its own* Linux filesystem, where it's meaningless. `docker inspect hive-server` confirmed zero volume mounts - the container's filesystem is fully isolated from the Mac's. This is exactly why real Hive deployments always sit on a shared filesystem (HDFS/S3) - the metastore server and every Spark client have to agree on what a storage path physically resolves to, and ours didn't. **Fix, and final result: it works.** Rebuilt the container with a real shared filesystem:

1. `docker commit hive-server hive-server-with-metastore-config` - snapshot capturing the Postgres metastore config from above.
2. Recreated the container (`docker stop` / `rm` / `run`) with a bind mount: `-v "<host>/hive-warehouse-shared:<same absolute path>"` - identical path string on both sides, so `file://<path>` means the same physical files whether Spark (on the Mac) or the metastore (in the container) touches it.
3. Hit the **exact same stale-PID-file bug from earlier this session** again, self-inflicted this time: `docker commit` captured `/opt/hive/conf/hiveserver2.pid` while HiveServer2 was genuinely running as PID 1 in the old container - and Docker always assigns PID 1 to a new container's own init process, so the false-positive "already running" check tripped again on the recreated container. Same fix as before: removed the stale pidfile in a temp container, committed that as `hive-server-with-metastore-fixed`, recreated `hive-server` from it with `--entrypoint /entrypoint.sh` explicitly restored (committing an entrypoint-overridden container bakes that override in as the new image's default - the same gotcha as last time).
4. Restarted the standalone `hive --service metastore` process (doesn't persist across container recreation - only HiveServer2 auto-starts via the entrypoint).
5. Deleted the `bronze`/`silver`/`gold` rows directly from the metastore's `DBS` table in Postgres (they were empty - no tables ever actually got created under the old, wrong locations - so no data was lost) so they'd get recreated fresh.
6. Added `.config("spark.sql.warehouse.dir", "file:///.../hive-warehouse-shared")` explicitly to `HiveSparkETL.scala`, instead of letting Spark silently default to a Mac-only path.

Re-ran `HiveSparkETL` end to end: **all 10 `saveAsTable` calls succeeded**, `[success] elapsed time: 14s`. Verified independently via `beeline` (a completely separate client from Spark) connecting to HiveServer2 directly: `SHOW DATABASES` returns `bronze`/`default`/`gold`/`silver`; `SHOW TABLES` in `gold` returns all 8 expected tables; `SELECT COUNT(*) FROM dim_customer` ran a real Tez job and returned `122` rows. This is real, independently-verified data, not just a clean program exit.

**Answer to the open question from `Training 9`-`11`:** native Spark-Hive metastore integration genuinely works - it just required rebuilding the container's metastore backend from embedded, single-process Derby to a real Postgres-backed metastore service, plus a shared filesystem (via a Docker bind mount) between the Spark client and the metastore server, since managed Hive tables require both sides to agree on what a storage path physically resolves to.

---

## New teacher script: `generate_sales.py`

Not covered in any earlier training session - the teacher shared this as a standalone Python script for generating synthetic Bronze-layer sales transactions directly into Postgres, rather than a one-time bulk load. It looks up the highest existing `T###` transaction ID already in `bronze.sales`, then inserts a new batch of 5 rows continuing that sequence - i.e., meant to be re-run repeatedly to simulate an ongoing stream of new transactions landing in the Bronze layer.

```python
import os
import random
import psycopg2
from datetime import date, timedelta

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "sample_database",
    "user": "evan",
    "password": os.environ["PG_PASSWORD"]
}

BATCH_SIZE = 5

# ---------------------------------------------------------
# Valid values for generated Bronze records
# ---------------------------------------------------------
FIRST_NAMES = [
    "Michael", "Sarah", "James", "Emily", "Daniel",
    "Jessica", "Robert", "Laura", "Kevin", "Amanda",
    "Brian", "Rachel", "Steven", "Nicole", "Andrew",
    "Michelle", "Jason", "Rebecca", "Thomas", "Jennifer"
]

LAST_NAMES = [
    "Johnson", "Williams", "Martinez", "Garcia", "Robinson",
    "Clark", "Lewis", "Walker", "Hall", "Allen",
    "Young", "King", "Wright", "Scott", "Green",
    "Baker", "Adams", "Nelson", "Carter", "Mitchell"
]

PRODUCTS = {
    "Laptop": ("Electronics", 1200.00),
    "Mouse": ("Electronics", 25.00),
    "Monitor": ("Electronics", 300.00),
    "Keyboard": ("Electronics", 75.00),
    "Desk": ("Furniture", 450.00),
    "Chair": ("Furniture", 125.00)
}

COUNTRIES = [
    "USA",
    "Canada"
]

def connect():
    return psycopg2.connect(**DB_CONFIG)

# ---------------------------------------------------------
# Find the largest existing T-number
# T001 -> 1
# T010 -> 10
# T125 -> 125
# Invalid IDs such as "12" are ignored.
# ---------------------------------------------------------
def get_next_transaction_id(cur):

    cur.execute("""
        SELECT COALESCE(
            MAX(
                CAST(
                    SUBSTRING(transaction_id FROM 2)
                    AS INTEGER
                )
            ),
            0
        )
        FROM bronze.sales
        WHERE transaction_id ~ '^T[0-9]+$';
    """)

    max_id = cur.fetchone()[0]

    return max_id + 1


# ---------------------------------------------------------
# Generate random customer
# ---------------------------------------------------------
def generate_customer():

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    return f"{first} {last}"


# ---------------------------------------------------------
# Generate random transaction date
# Generates a date within the last 30 days.
# ---------------------------------------------------------
def generate_date():

    days_ago = random.randint(0, 30)

    transaction_date = (
        date.today() - timedelta(days=days_ago)
    )

    return transaction_date.isoformat()


# ---------------------------------------------------------
# Generate one complete valid sales record
# ---------------------------------------------------------
def generate_sale(transaction_id):

    customer_name = generate_customer()

    product = random.choice(list(PRODUCTS.keys()))

    category, base_price = PRODUCTS[product]

    quantity = random.randint(1, 5)

    # Give prices a little realistic variation
    price_multiplier = random.uniform(0.90, 1.10)

    unit_price = round(
        base_price * price_multiplier,
        2
    )

    country = random.choice(COUNTRIES)

    return (
        transaction_id,
        generate_date(),
        customer_name,
        product,
        category,
        str(quantity),
        f"{unit_price:.2f}",
        country
    )


# ---------------------------------------------------------
# Generate and insert a batch
# ---------------------------------------------------------
def generate_batch():

    conn = connect()
    cur = conn.cursor()

    next_id = get_next_transaction_id(cur)

    print("\nGenerating batch...")
    print("-" * 80)

    sql = """
        INSERT INTO bronze.sales (
            transaction_id,
            transaction_date,
            customer_name,
            product,
            category,
            quantity,
            unit_price,
            country
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """

    generated_ids = []

    for i in range(BATCH_SIZE):

        numeric_id = next_id + i

        transaction_id = f"T{numeric_id:03d}"

        row = generate_sale(transaction_id)

        cur.execute(sql, row)

        generated_ids.append(transaction_id)

        print(
            f"{row[0]} | "
            f"{row[1]} | "
            f"{row[2]:20} | "
            f"{row[3]:10} | "
            f"{row[4]:12} | "
            f"qty={row[5]} | "
            f"${row[6]} | "
            f"{row[7]}"
        )

    conn.commit()

    print(
        f"\nSuccessfully inserted "
        f"{BATCH_SIZE} new transactions."
    )

    # -----------------------------------------------------
    # Verify exactly the rows we just inserted
    # -----------------------------------------------------

    cur.execute("""
        SELECT
            transaction_id,
            transaction_date,
            customer_name,
            product,
            category,
            quantity,
            unit_price,
            country
        FROM bronze.sales
        WHERE transaction_id = ANY(%s)
        ORDER BY
            CAST(
                SUBSTRING(transaction_id FROM 2)
                AS INTEGER
            );
    """, (generated_ids,))

    print("\nInserted records:")
    print("-" * 80)

    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


if __name__ == "__main__":
    generate_batch()
```

**Adaptations needed for our environment** (same pattern as the Scala job above): `dbname = "sample_database"` -> `warehouse_practice`, `user = "evan"` -> `ajackson`. Not yet adapted into a runnable file in `hive-spark-etl/` - noted here for now; will build the adapted version once the current Hive metastore write-path work is resolved.
