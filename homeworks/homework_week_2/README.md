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
- Uses `JOIN ... ON BETWEEN` instead of CROSS JOIN
- Replaces `FULL OUTER JOIN` with `LEFT JOIN` to check for missing years
- Uses `ARRAY_AGG` to collect final gaps per actor

```sql
-- CTEs: year_range, year_sequence, actor_min_max_year, actor_year, actor_inactive_years
-- Final SELECT: actor_id, actor, ARRAY_AGG(CASE WHEN year IS NULL THEN year_seq ELSE NULL END)
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
- ✅ **Well-structured SQL and clear modular CTE logic**
- ✅ **Correct implementation of Python UDFs**
- ✅ **Proper use of external libraries in Snowflake**
- ✅ **Result format aligns with problem requirements**

### Suggestions
- 🔁 Consider using a **window function (e.g., LAG)** in future iterations for time gap detection.
- ⚠️ Be cautious with **large-scale JOINs** in bigger datasets—may affect performance.

---

## 🏁 Final Assessment

```json
{
  "letter_grade": "A",
  "passes": true
}
```

Excellent submission! The revised `LEFT JOIN` implementation improved clarity, and all tasks were addressed correctly.

---

📁 **Next Step:**
- Use parameterized inputs to make UDFs more reusable
- Explore using `LAG()`/`LEAD()` to spot gaps in sequential data
- Test your UDF performance on larger datasets
