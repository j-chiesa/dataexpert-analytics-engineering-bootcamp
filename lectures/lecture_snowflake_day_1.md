# ❄️ Snowflake - Day 1

> This lecture explains **when and why to use Snowpark**, compares **Snowflake vs Iceberg** for data storage, and provides best practices on **clustering** and **cost management** in Snowflake.

---

## 🧵 Snowpark

> Snowpark is a developer framework to process external data with Python in Snowflake using a lazy execution model similar to Spark.

### When to Use Snowpark

Ideal for working with data *outside* of Snowflake:

- ✅ REST APIs  
- ✅ External files (excluding Iceberg tables — use an external catalog instead)  
- ✅ External databases

📌 Snowpark is essentially a **Python API** that connects these external sources into Snowflake pipelines.

### Snowpark Architecture

Snowpark is **similar** to Apache Spark:

- Lazy evaluation model
- Uses DataFrames

But also **different**:

- Runs **only on Snowflake** (not open source)
- No need for memory/performance tuning
- Translates DataFrame logic into optimized SQL behind the scenes

### Lazy Execution

> Like Spark, **no computation happens until an action is triggered**.

- **Transformations** (e.g. `.filter()`, `.select()`, `.join()`) build a logical plan.
- **Actions** (e.g. `.collect()`, `.count()`, `.toPandas()`, `.write()`) trigger query execution.

✅ Benefits:

- **Performance**: Query optimization before execution  
- **Flexibility**: Multiple chained transformations, fewer queries  
- **Debugging**: Safely test logic without triggering heavy workloads

---

## 🧊 Snowflake vs Iceberg

> Let’s compare Snowflake and Iceberg purely as **storage layers**, since Snowflake also includes compute.

| Aspect                | Snowflake                                     | Iceberg                                           |
|-----------------------|-----------------------------------------------|---------------------------------------------------|
| **Latency**           | ✅ Low — great for dashboards                  | ❌ High — not ideal for dashboards                |
| **Performance Tuning**| ✅ Fully managed                               | ❌ Manual tuning (skew, partitions, etc.)         |
| **Governance**        | ✅ Strong                                      | ❌ Harder — not built-in                          |
| **Access**            | ❌ Only via Snowflake APIs/SQL                | ✅ Open format — many engines                     |
| **Storage Cost**      | ❌ Expensive (~3x Iceberg)                    | ✅ Cheapest cloud-native format                   |
| **Use Case Fit**      | Dashboards, sensitive data                    | ML training data, shared datasets                |
| **Vendor Lock-in**    | ❌ Yes                                         | ✅ No — open standard                             |

### Examples of Usage

**Snowflake is ideal for:**

- Dashboarding  
- OLAP cubes  
- Sensitive PII data  

**Iceberg is better for:**

- Shared datasets across tools  
- Machine Learning datasets  
- Historical time travel + schema evolution use cases  

---

### Interoperability: Query Iceberg from Snowflake

You can access Iceberg tables from within Snowflake by setting up:

1. **Catalog Integration** – links to a REST catalog (like Tabular)  
2. **Catalog Volume** – points to actual data  
3. **Iceberg Table Reference** – acts as a managed table in Snowflake

> Once set up, Iceberg tables can be queried just like native Snowflake tables.

---

## 📐 Clustering in Snowflake

> Clustering is Snowflake’s way to optimize micro-partitions (its version of partitions).

- Snowflake doesn’t expose partitions directly.
- Instead, uses **micro-partitions** + optional **clustering keys** for optimization.

### Query Pruning

> Pruning = Skipping irrelevant micro-partitions during query.

- Each micro-partition stores metadata (min/max values)  
- Clustering organizes data so **queries read less data**

📌 Choose clustering keys wisely:
- **Good**: Time (`date`), low-cardinality (`country`, `OS`), `user_id` (in Snowflake only)  
- **Bad**: Booleans, high-cardinality (e.g. nanosecond timestamps)

### Partitioning in Iceberg

> Iceberg gives **more manual control** than Snowflake:

- **Partitions** → act like high-level folders
- **Buckets** → files within those folders, defined via `bucket_by` and `bucket_count`

✅ Iceberg offers:
- Static but configurable structure
- 80–90% of optimizations without reclustering
❗ But requires manual design (no automatic reclustering)

### When to Cluster?

Think of clustering like **indexing** in SQL:

- ✅ Use when you want faster queries and cost is not an issue  
- ❌ Don’t cluster everything — it’s expensive

---

## 💰 Cost Management in Snowflake

> Snowflake costs can grow quickly if left unchecked. Use built-in tools and good practices.

### Infrastructure

- **Warehouse settings**:
  - Set auto-suspend to 1–5 mins (default is 1 hour)
  - Downsize warehouse if over-provisioned

### Monitoring

- `INFORMATION_SCHEMA.TABLE_STORAGE_METRICS`  
  → Shows table size, time travel footprint  
- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`  
  → Tracks query cost, clustering usage, long-running queries

### Optimization Tips

- ✅ **Offload cold data to Iceberg**
- ✅ **Sample** datasets during development
- ✅ **Cluster selectively**
- ✅ **Retain only needed snapshots**
- ✅ **Negotiate policies with analysts on tradeoffs (e.g., suspend time)**

📌 Don’t pay for features you don’t need. Think long-term.
