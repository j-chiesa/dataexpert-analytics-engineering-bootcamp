# 🧊 Homework Week 1 — Apache Iceberg & PyIceberg

> This assignment involves setting up a daily-partitioned Iceberg table using **PyIceberg**, fetching MAANG stock prices from **Polygon API**, and writing/merging data via **AWS Glue jobs**. Bonus: fast-forward a branch to main.

---

## ✅ Requirements Recap

- Use **PyIceberg** (or **PySpark**), **Polygon API**, and **Tabular**.
- Create a **daily partitioned table** in your schema.
- Make an **audit branch** with `create_branch()`.
- Load daily stock data and write into the audit branch.
- Save logic in `stock_prices.py` and upload zipped file to DataExpert.
- **Bonus**: Write a job that fast-forwards the audit branch to main.

---

## 🧾 Files

### 1. `stock_prices.py`

This file:
- Initializes Iceberg schema and table
- Sets up branching and fast-forwarding logic
- Wraps Glue job orchestration

**Highlights:**
- Uses `pyiceberg` to define schema, partition, and sort
- Leverages AWS Glue via helper `create_and_run_glue_job`
- Supports conditional execution for writing or merging branches

```python
# Functions: create_table_if_not_exists, write_to_branch(date), fast_forwarding(date)
# Uses catalog.create_table_if_not_exists() and Glue job execution
```

### 2. `stock_prices_branching.py`

This Glue job:
- Fetches MAANG stock prices from **Polygon.io** using `requests`
- Converts result into a PySpark DataFrame
- Writes to Iceberg table partitioned by `date`

**Highlights:**
- Handles structured transformation and schema mapping
- Uses `ARRAY_AGG`, `OBJECT_CONSTRUCT`, and PySpark `.writeTo()`
- Supports writing to branches (optional `--branch` arg)
- Contains cleanup logic for audit branches if unused

```python
# Functions: fetch_stock_data(), main()
# Key tools: requests, pyspark.sql.functions, AWS GlueContext
```

---

## 🧪 Features Implemented

| Feature                                      | Status     | Notes                                                            |
|---------------------------------------------|------------|------------------------------------------------------------------|
| Daily-partitioned Iceberg table             | ✅ Done     | Uses `PartitionSpec` on `date`                                   |
| Branching (WAP audit)                       | ✅ Done     | Implemented via Glue job and CLI args                            |
| Stock data from Polygon API                 | ✅ Done     | Validated against real API responses                             |
| Upload script to DataExpert                 | ✅ Done     | `stock_prices.py` zipped and uploaded                           |
| Fast-forward logic                          | ✅ Done     | Job handles fast-forward from `audit_branch` to `main`           |

---

## 🧠 Feedback Summary

### Strengths
- **✅ Well-defined Iceberg schema and partitions**
- **✅ Correct API usage and data ingestion**
- **✅ Glue orchestration and branching logic implemented**

### Suggestions
- 🔒 **Secure API key management** → Use env variables or Vault
- 🔁 **Better modularization** → Use CLI flags vs manual uncommenting
- ⚙️ **Add more error handling** → Especially around Glue and API I/O
- 🧹 **Smarter branch cleanup** → Avoid accidental removal of prod branches
- ⚡ **Improve performance** → Consider parallelism when loading stock data

---

## 🏁 Final Assessment

```json
{
  "letter_grade": "A",
  "passes": true
}
```

You have delivered a complete and well-engineered solution. Just a few refinements around security, code structure and resilience would elevate this even further. Great job!

---

📁 **Next Step:**
- Incorporate feedback into future submissions
- Consider parameterizing the pipeline (e.g., CLI args or config files)
- Keep exploring advanced Iceberg features like snapshot expiration and schema evolution
