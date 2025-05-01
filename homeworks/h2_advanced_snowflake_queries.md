# ❄️ Homework Week 2 — Advanced Snowflake Queries

> This assignment involves querying the `bootcamp.actor_films` dataset to find **inactive years** for each actor, and detecting **similar actor names** using **Levenshtein distance**. The solution includes both a full-SQL workflow and Python UDFs with external packages in Snowflake.

---

## ✅ Requirements Recap

- Use **Snowflake SQL**, **Python UDFs**, and **CTEs**.
- Identify years each actor did **not** make a film (after their first film).
- Do it in two ways:
  1. Using **SQL only** (via generated sequences).
  2. Using a **Python UDF** to compute inactive years.
- Create a UDF with external package to calculate **Levenshtein distance**.
- Upload `.sql` files zipped to the submission platform.

---

## 🧾 Files

### 1. `actors_inactive_years_wf.sql`

This file:
- Finds the inactive years using full SQL
- Generates global year sequence and filters active spans
- Returns `ARRAY` of inactive years for each actor

**Highlights:**
- Uses `GENERATOR` + `SEQ4()` to build full year range
- `CROSS JOIN` with active span for expected year-actor pairs
- `FULL OUTER JOIN` to check if any year is missing
- `ARRAY_AGG` to collect final gaps per actor

```sql
-- CTEs: year_range, year_sequence, actor_min_max_year, actor_year, actor_inactive_years
-- Final SELECT: actor_id, actor, ARRAY_AGG(year_seq IF year IS NULL)
```

---

### 2. `actors_inactive_years_udf.sql`

This file:
- Implements a **Python UDF**: `get_inactive_years(active_years)`
- Aggregates years into arrays per actor
- Applies the UDF to get missing years

**Highlights:**
- UDF handles duplicates and edge cases
- Aggregates via `ARRAY_AGG(year)` per actor
- Resulting inactive years are sorted

```sql
-- Python logic: min/max, range, set difference
-- SQL steps: deduped actor-year, grouped by actor_id
```

---

### 3. `levenshtein_distance_udf.sql`

This file:
- Defines a Python UDF with external package: `python-Levenshtein`
- Computes distance between actor name pairs
- Filters similar names (distance ≤ 3)

**Highlights:**
- Uses `PACKAGES = ('python-Levenshtein')`
- Joins each actor with every other (excluding self)
- Filters for name similarity threshold

```sql
-- CTEs: actor (distinct list), distance (joined pairs + UDF)
-- Final SELECT: WHERE levenshtein_distance <= 3
```

---

## 🧪 Features Implemented

| Feature                                            | Status   | Notes                                             |
|---------------------------------------------------|----------|---------------------------------------------------|
| Inactive years with full SQL                      | ✅ Done  | Efficient use of `SEQ4()` + outer join logic     |
| Python UDF to compute inactive years              | ✅ Done  | Clean logic, handles gaps robustly               |
| UDF using external package (Levenshtein distance) | ✅ Done  | Uses `python-Levenshtein` for name matching      |
| Grouped queries with arrays per actor             | ✅ Done  | Structured result with inactive year lists       |
| Self-join actor names with distance threshold     | ✅ Done  | Finds near-duplicate names via edit distance     |

---

## 🧠 Feedback Summary

### Strengths
- ✅ **Efficient use of SQL CTEs and structure**
- ✅ **Python UDFs correctly implemented**
- ✅ **Clean logic and handling of edge cases**
- ✅ **Proper external package usage in UDFs**

### Suggestions
- 🔁 **Add explicit window function** (e.g., LAG) if required for clarity
- ⚠️ **Avoid overly wide FULL OUTER JOINs** → could get expensive on large datasets
- 🧩 **Break queries into modular scripts** if reused

---

## 🏁 Final Assessment

```json
{
  "letter_grade": "A",
  "passes": true
}
```

Excellent submission! The work meets all technical goals and shows a strong grasp of both SQL and Snowflake UDFs. Just be mindful of query performance on larger datasets.

---

📁 **Next Step:**
- Use parameterized inputs to make UDFs more reusable
- Try integrating these steps into a dbt pipeline or Airflow DAG
- Practice using `LAG()`/`LEAD()` to spot gaps in time series
