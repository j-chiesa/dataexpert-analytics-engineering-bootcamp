# 🧊 Apache Iceberg - Lecture Day 2

> This lecture focuses on Iceberg’s role in modern analytical architectures, storage agnosticism, streaming vs batch trade-offs, small file management, compaction strategies, and row-level operations. It explains how companies like Netflix and Facebook deal with challenges in large-scale data systems.
> 

## 🗄️ Agnostic Storage

![Agnostic Storage](img/apache_iceberg_day_2_1.png)

- Apache Iceberg is **file format agnostic** — it works with **Parquet**, **ORC**, and **Avro**.
    - **Parquet** is the industry standard.
- Iceberg is **engine agnostic** — it supports read/write operations from **Trino**, **Spark**, **Flink**, **Python**, etc.
- It is a **fully open-source** project.

![Apache Iceberg Features](img/apache_iceberg_day_2_2.png)

---

## 🧱 Current vs Future Analytical Architectures

### 📅 Current Analytical Architecture

![Current Analytical Architecture](img/apache_iceberg_day_2_3.png)

- **Production Database Layer**: Daily snapshots go through ETL and land in the data lake partitioned by date.
- **Application Layer**: Applications send events to a queue (e.g., Kafka, Scribe). Data is dumped daily into the data lake. For large volumes, hourly partitions are created and later combined into daily ones.

### 🔮 Future Analytical Architecture

![Future Analytical Architecture](img/apache_iceberg_day_2_4.png)

- **Production Database Layer**: No more daily snapshots. **Change Data Capture (CDC)** sends real-time changes to an event queue, then ingested directly into Iceberg.
- **Application Layer**: Remains unchanged.

---

## ⚡ How to Speed Up a Data Pipeline

- Use **streaming** (common but not always optimal).
- Prefer **hourly batch processing** for simplicity and coherence.
- Don’t always process 100% of the data.
    - Netflix example: Processed just **10%** of petabytes of logs and reached the same business conclusions.

### ⚠️ Streaming Drawbacks

- **Small file problem**: Every event creates a tiny file.
- **Limited Data Quality Checks**:
    - Only row-level checks possible.
    - Full comparisons (e.g., day-over-day) are expensive.

### ✅ Solutions by Big Tech

- Use **Lambda Architecture** or **Kappa Architecture** to balance streaming and batch pipelines.

---

## 🏗️ Lambda vs Kappa Architectures

### 🌀 Lambda Architecture

![Lambda Architecture](img/apache_iceberg_day_2_5.png)

- Two codebases: one for streaming, one for batch.
- **Streaming pipeline** creates small files and is fast but less accurate (we can have late arriving data).
- **Batch pipeline** does a daily/hourly **“true up”** for accuracy and quality.
- Batch is used for strong **data quality** checks.

### 🔁 Kappa Architecture

![Kappa Architecture](img/apache_iceberg_day_2_6.png)

- One unified codebase for both streaming and batch.
- Handles small files with **compaction** (e.g., Iceberg).
- Data quality is layered:
    - **Simple checks** in streaming.
    - **Volumetric checks** with observability tools.
    - **Complex checks** later in batch layers.

---

## 🧼 Iceberg Compaction

- Supports `INSERT INTO` operations → leads to **many small files**.
- Small files are inefficient: too many I/O operations and too much parallelism.

### 🧩 Small File Problem

![Small Files Problem](img/apache_iceberg_day_2_7.png)

- Avoid both extremes:
    - ⚠️ One file per row → too much overhead.
    - ⚠️ One file for all data → not enough parallelism.
- **Goal**: Balance I/O overhead vs parallelism.

### 🔧 Compaction Methods

1. **Automatic Compaction** (via data lake provider):
    - Combines small files.
    - Applies compression and table ordering.
    - Target file size default: **512MB**.
2. **Manual Compaction** (e.g., in Spark):

```python
CALL system.rewrite_data_files(table => 'bootcamp.nba_player_seasons')
```

### 🔍 Compaction Settings

- `target-file-size-bytes`: Usually 512MB. Can be tuned.
- **Strategies**:
    - `Binpack` (default): Simple file merging.
    - `Sort`: Merge + sort (e.g., by Z-Order). Costly — use only when necessary.

---

## ✂️ Row-Level Deletes/Updates

> Supported since Iceberg 2.0
> 
> 
> [Row-Level Changes on the Lakehouse – Dremio](https://www.dremio.com/blog/row-level-changes-on-the-lakehouse-copy-on-write-vs-merge-on-read-in-apache-iceberg/)
> 
- Allows **row-level mutations** without partitioning.

### 🧠 Two Snapshot Strategies

1. **Copy-on-Write (CoW)**:
    - When a row is updated or deleted, Iceberg **rewrites the entire data file** where that row is located, omitting or updating the necessary records.
    - Think of it like creating a new clean version of the file without the modified rows.

    **Pros:**
    - ✅ **Fast reads**: data is already clean and compact.
  
    **Cons:**
    - ❌ **Slow writes**: rewriting entire files is costly.

    **Best for:**
    - **Batch updates** — large, infrequent changes (e.g., cleaning up daily data).
2. **Merge-on-Read (MoR)**:
    - Iceberg **tracks deletes and updates in separate “change” files**.
    - On read, it **merges** the base data files with these change files to show the up-to-date view.

    **Pros:**
    - ✅ **Fast writes**: minimal overhead when data is written.

    **Cons:**
    - ❌ **Slow reads**: must merge base + change files during every query.

    **Best for:**
    - **Streaming updates** — small, frequent changes (e.g., events arriving every few seconds).

### 🧮 Quick Comparison

| Strategy         | Write Performance | Read Performance | Best Use Case         |
|------------------|-------------------|------------------|------------------------|
| Copy-on-Write    | ❌ Slow           | ✅ Fast          | Batch updates (large)  |
| Merge-on-Read    | ✅ Fast           | ❌ Slow          | Streaming (frequent)   |

---

## 🔥 Hot, Warm & Cold Data

![Latency vs Cost](img/apache_iceberg_day_2_8.png)

- **Latency ↔ Cost** trade-off.
- **Iceberg is not efficient for dashboards**.

### 📊 Dashboard Best Practices

- Dashboards should load instantly.
- Use **pre-aggregated data** stored in **low-latency engines**.
- Dashboards = `SELECT`, `WHERE`, light `GROUP BY`.
- 🚫 Avoid `JOIN` — a sign of poor data modeling.
