# 🧊 Apache Iceberg — Lab Day 1

> This notebook demonstrates key functionalities of Apache Iceberg using Trino, including snapshotting, time travel, partition pruning, and file-level metadata exploration.  
> We learned how to create tables, track snapshots, restore historical data, optimize queries through partitioning, and analyze file storage behavior in both partitioned and unpartitioned formats.

---

## 📸 1. Snapshots

### ✅ Create a partitioned table

```sql
CREATE TABLE javierchiesa.showcase_iceberg (
    col VARCHAR,
    event_date DATE
)
WITH (
    partitioning = ARRAY['event_date']
);
```

### 🔍 Query snapshots

```sql
SELECT * FROM javierchiesa."showcase_iceberg$snapshots";
```

| committed_at        | snapshot_id         | parent_id | operation | manifest_list | summary |
|---------------------|---------------------|-----------|-----------|----------------|---------|
| 2025-04-17 11:29:16 | 6282228431002613123 | *(null)*  | append    | ...avro        | {...}   |

- **`manifest_list`**: File listing snapshots and their relationships (linked list structure: snapshot → parent).
- **`parent_id`**: Points to the previous snapshot. It's null when creating the table (first operation).

### ➕ Insert data and see new snapshot

```sql
INSERT INTO javierchiesa.showcase_iceberg 
VALUES ('Hello world', DATE('2025-04-15'));

SELECT * FROM javierchiesa."showcase_iceberg$snapshots";
```

Now there are two snapshots: table creation and the insert.

---

## ⏳ 2. Time Travel

### ❌ Delete all records

```sql
DELETE FROM javierchiesa.showcase_iceberg;

SELECT * FROM javierchiesa.showcase_iceberg; -- Returns empty
```

### 🕐 Travel back to a previous snapshot

```sql
SELECT *
FROM javierchiesa.showcase_iceberg 
FOR TIMESTAMP AS OF TIMESTAMP '2025-04-17 15:08:52';
```

| col         | event_date |
|-------------|------------|
| Hello world | 2025-04-15 |

---

## 🧹 3. Partitioning

### 🔍 Efficient query using exact partition

```sql
SELECT *
FROM javierchiesa.showcase_iceberg 
FOR TIMESTAMP AS OF TIMESTAMP '2025-04-17 15:08:52'
WHERE event_date = DATE('2025-04-15');
```

- ✅ Enables **partition pruning**.

### ⚠️ Inefficient (non-sargable) query

```sql
SELECT *
FROM javierchiesa.showcase_iceberg 
FOR TIMESTAMP AS OF TIMESTAMP '2025-04-17 15:08:52'
WHERE YEAR(event_date) = 2025;
```

- ❌ Not sargable → No partition pruning possible.
- **Sargable**: Query allows the engine to use indexes/partitions without function transformations.

### ✅ Insert multiple rows

```sql
INSERT INTO javierchiesa.showcase_iceberg
VALUES 
  ('Bye World', DATE('2025-04-17')),
  ('Hello Again', DATE('2025-04-18')),
  ('Test Row 1', DATE('2025-04-19')),
  ('Test Row 2', DATE('2025-04-20')),
  ('Final Row', DATE('2025-04-21'));
```

### 🗃️ Efficient range query

```sql
SELECT *
FROM javierchiesa.showcase_iceberg 
FOR TIMESTAMP AS OF TIMESTAMP '2025-04-17 15:08:52'
WHERE event_date BETWEEN DATE('2025-01-01') AND DATE('2025-12-31');
```

- ✅ Keeps `event_date` untransformed → partition pruning is possible.

---

## 📋 4. Physical Files (`$files`)

```sql
SELECT * FROM javierchiesa."showcase_iceberg$files";
```

- Iceberg uses `lower_bounds` and `upper_bounds` to filter partitions.

### 🔍 Sargable example

```sql
SELECT *
FROM javierchiesa.showcase_iceberg
WHERE col > 'G';
```

- ✅ Can use file-level metadata.

### ❌ Non-sargable example

```sql
SELECT *
FROM javierchiesa.showcase_iceberg
WHERE UPPER(col) > 'G';
```

- ❌ Transforms the column → full scan needed.

> ⚠️ **General rule:** Keep the left side of your `WHERE` clause clean (no transformations).

---

## 🏀 5. NBA Table Example

### 🧠 Explore partitioned files

```sql
SELECT *
FROM bootcamp."nba_player_seasons$files";

SELECT SUM(FILE_SIZE_IN_BYTES)
FROM bootcamp."nba_player_seasons$files"; -- 619,376 bytes
```

### 📃 Create unpartitioned table

```sql
CREATE TABLE javierchiesa.nba_player_seasons_unpartitioned AS
SELECT * 
FROM bootcamp.nba_player_seasons;

SELECT * FROM javierchiesa."nba_player_seasons_unpartitioned$files"; -- 1 file
```

### ⚖️ Compare partitioned vs unpartitioned

```sql
SELECT
  'unpartitioned' AS type,
  SUM(record_count) AS record_count,
  SUM(file_size_in_bytes) AS file_size_in_bytes
FROM javierchiesa."nba_player_seasons_unpartitioned$files"
UNION ALL
SELECT
  'partitioned' AS type,
  SUM(record_count) AS record_count,
  SUM(file_size_in_bytes) AS file_size_in_bytes
FROM bootcamp."nba_player_seasons$files";
```

| type          | record_count | file_size_in_bytes |
|---------------|--------------|--------------------|
| unpartitioned | 12,869       | 238,708            |
| partitioned   | 12,869       | 619,376            |

- Unpartitioned is 60% smaller → better compression.
- **Why?** → Run-Length Encoding (RLE) is more effective on non-partitioned columnar files. If we sort the data we can get even more compression (but is a expensive operation).

### 🤔 Conclusion

| Case           | Main Benefit          | When to Use                                      |
|----------------|------------------------|--------------------------------------------------|
| **Partitioned** | Query performance      | Large datasets, frequent filtering               |
| **Unpartitioned** | Storage efficiency    | Small/infrequent datasets, prioritize compression |
