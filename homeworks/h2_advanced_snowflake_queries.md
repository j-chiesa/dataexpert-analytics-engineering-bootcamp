# 🧪 Snowflake UDFs & Inactive Years — Assignment

> This lab explores advanced querying and UDF functionality in Snowflake to solve real-world data problems.
> It focuses on identifying inactive years for actors, both through SQL and Python UDF approaches, and detecting similar actor names via Levenshtein distance using external packages in Python.
> The solutions are modular, efficient, and follow best practices in CTE structuring and UDF handling.

---

## 🎬 Task 1 — Inactive Years via SQL (No UDF)

### 📁 File: `actors_inactive_years_wf.sql`

#### 1️⃣ Generate Full Range of Years

```sql
WITH year_range AS (
    SELECT
        MIN(year) AS min_year,
        MAX(year) AS max_year
    FROM bootcamp.actor_films
),
year_sequence AS (
    SELECT min_year + SEQ4() AS year
    FROM year_range,
        TABLE(GENERATOR(ROWCOUNT => max_year - min_year + 1))
)
```

- Extracts min and max year in dataset.
- Uses `GENERATOR` with `SEQ4()` to produce a year sequence efficiently.

---

#### 2️⃣ Determine Each Actor's Active Range

```sql
actor_min_max_year AS (
    SELECT
        actor_id,
        actor,
        MIN(year) AS min_year,
        MAX(year) AS max_year
    FROM bootcamp.actor_films
    GROUP BY actor_id, actor
)
```

- Aggregates each actor's first and last appearance in a film.

---

#### 3️⃣ Build All Expected Actor-Year Pairs

```sql
actor_year AS (
    SELECT
        ay.actor_id,
        ay.actor,
        ys.year
    FROM actor_min_max_year ay
    CROSS JOIN year_sequence ys
    WHERE ay.min_year <= ys.year AND ys.year <= ay.max_year
)
```

- Combines all actors with all years between their active span.

---

#### 4️⃣ Compare with Actual Film Years

```sql
actor_inactive_years AS (
    SELECT
        ay.actor_id,
        ay.actor,
        ay.year AS year_seq,
        af.year
    FROM actor_year ay
    FULL OUTER JOIN bootcamp.actor_films af
        ON ay.actor_id = af.actor_id AND ay.year = af.year
    GROUP BY ALL
    ORDER BY actor_id, ay.year
)
```

- Performs a full outer join to detect actor-year pairs that lack film records.

---

#### 5️⃣ Final Result: Get Inactive Years

```sql
SELECT
    actor_id,
    actor,
    ARRAY_AGG(
        CASE
            WHEN year IS NOT NULL THEN NULL
            ELSE year_seq
        END
    ) AS inactive_years
FROM actor_inactive_years
GROUP BY actor_id, actor;
```

- Returns an `ARRAY` of years where actors had no films during their career span.

---

## 🧑‍💻 Task 2 — Inactive Years via Python UDF

### 📁 File: `actors_inactive_years_udf.sql`

#### 🧠 Define Python UDF: `get_inactive_years`

```sql
CREATE OR REPLACE FUNCTION javierchiesa.get_inactive_years(active_years ARRAY)
RETURNS ARRAY
LANGUAGE PYTHON
HANDLER = 'get_inactive_years'
RUNTIME_VERSION = '3.11'
AS
$$
def get_inactive_years(active_years):
    if not active_years:
        return []

    active_years = list(set(int(y) for y in active_years))
    min_year = min(active_years)
    max_year = max(active_years)
    full_range = set(range(min_year, max_year + 1))
    inactive_years = sorted(full_range - set(active_years))
    return inactive_years
$$;
```

- Handles deduplication, min/max, and computes missing years in the range.

---

#### 🧹 Clean & Aggregate Actor Data

```sql
WITH deduped AS (
    SELECT
        actor_id,
        actor,
        year
    FROM bootcamp.actor_films
    GROUP BY ALL
    ORDER BY actor_id, year
),
combined AS (
    SELECT
        actor_id,
        actor,
        ARRAY_AGG(year) AS active_years
    FROM deduped
    GROUP BY actor_id, actor
)
```

- De-duplicates film-year records and groups active years into arrays.

---

#### 🗾️ Final Query: Compute Inactive Years with UDF

```sql
SELECT
    actor_id,
    actor,
    get_inactive_years(active_years) AS inactive_years
FROM combined;
```

- Returns inactive years per actor using the defined Python UDF.

---

## 🔠 Task 3 — Similar Actor Names (Levenshtein Distance)

### 📁 File: `actors_inactive_years_udf.sql`

#### 📦 Define Python UDF: `get_levenshtein_distance`

```sql
CREATE OR REPLACE FUNCTION javierchiesa.get_levenshtein_distance(name_one VARCHAR, name_two VARCHAR)
RETURNS INT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('python-Levenshtein')
HANDLER = 'get_levenshtein_distance'
AS
$$
from Levenshtein import distance

def get_levenshtein_distance(name_one, name_two):
    return distance(name_one, name_two)
$$;
```

- Uses external package `python-Levenshtein` to compare names.

---

#### 🔍 Similar Name Matching

```sql
WITH actor AS (
    SELECT actor_id, actor
    FROM bootcamp.actor_films
    GROUP BY actor_id, actor
),
distance AS (
    SELECT
        a1.actor AS actor_one,
        a2.actor AS actor_two,
        get_levenshtein_distance(a1.actor, a2.actor) AS levenshtein_distance
    FROM actor a1
    JOIN actor a2 ON a1.actor_id != a2.actor_id
)
SELECT *
FROM distance
WHERE levenshtein_distance <= 3;
```

- Joins each actor with all others.
- Returns pairs with distance ≤ 3 → considered similar.

---

## ✅ Feedback Summary

| File                         | Remarks |
|------------------------------|---------|
| `actors_inactive_years_wf.sql` | Excellent logic using CTEs. No explicit window function used, but functionality achieved. |
| `actors_inactive_years_udf.sql` | UDF is well-structured. Handles edge cases. Efficient use of aggregation. |
| `get_levenshtein_distance()` | Correct UDF implementation. Proper use of external package. Accurate filtering. |

---

## 🏁 Final Notes

> This assignment showcases strong understanding of Snowflake SQL, CTEs, UDFs in Python, and external package integration. The only optional suggestion would be explicitly showcasing a window function for completeness, though results are functionally correct.

**Final Grade:** ✅ **A**

