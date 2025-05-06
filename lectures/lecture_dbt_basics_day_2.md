# 📦 dbt Basics - Day 2

> In this class we covered different types of tests (data and unit tests) in dbt, how to write them, when to use them, and how to implement Snapshots as Slowly Changing Dimensions Type 2 (SCD2).

---

## ✅ Tests

### Data Tests

- Validate the quality of data inside a table (run **after** the model is created).
- Confirm that the data meets certain expectations or business rules.
- Types:
  - **Generic**: reusable, written with Jinja.

    ![Generic Test](./data_test_generic.png)

  - **Singular**: specific to a single model.

    ![Singular Test](./data_test_singular.png)

- dbt comes with four built-in generic tests:
  - `not_null`
  - `unique`
  - `accepted_values`
  - `relationships`

- Many more are available through packages like `dbt_utils` and `dbt_expectations`.
- You can adjust test severity (`warn` or `error`) and log failed records to your database for debugging.

---

### Unit Tests

- Test your **SQL logic**, not real production data.
- Define inputs and expected outputs, similar to testing Python functions.
- Run **before** the model is created.
- Great for development and CI/CD pipelines.

![Unit Test Example](./unit_test_Example.png)

- Supports inputs as:
  - Dictionaries
  - CSVs
  - SQL (via `SELECT ... UNION ALL`)

---

## 🏆 dbt Test Best Practices

### Data Tests

| Type     | Typical Use Cases                                 |
|----------|---------------------------------------------------|
| Generic  | `unique`, `not_null`, `accepted_values`, ranges   |
| Singular | Business-specific logic                           |

### Unit Tests

| Recommended For                    |
|-----------------------------------|
| Complex joins or filters          |
| Regex functions                   |
| Incremental models                |
| Window functions                  |
| Business logic validation         |

---

## 🕒 Snapshots

> Snapshots in dbt are the built-in way to implement Slowly Changing Dimension Type 2 (SCD2), allowing you to track changes in records over time.

### Key Concepts:

- Used on top of **sources**.
- Require a `unique_key` to track records.
- Store historical versions when data changes.
- Run using `dbt snapshot`.

---

### Snapshot Strategies

#### 🕒 Timestamp

- Requires an `updated_at` column.
- Tracks changes by comparing timestamps.

![Snapshot Timestamp](./snapshots_timestamp.png)

#### ✅ Check

- Compares specified columns (`check_cols`) to detect changes.

![Snapshot Check](./snapshots_check.png)

---

## 💡 Snapshot Best Practices

- Use `source()` for better lineage tracking.
- Include as many columns as possible (you can’t add them later).
- Avoid joins (they make `updated_at` less reliable).
- Limit transformations in your query.

> **KEEP YOUR SNAPSHOTS AS SIMILAR AS POSSIBLE TO THE SOURCE!**

---

## 📦 dbt Packages

- Extensions that add models, macros, or tests to your project.

### Useful Packages:

| Package                | Functionality                              |
|------------------------|--------------------------------------------|
| `codegen`              | Auto-generates boilerplate code            |
| `dbt_utils`            | Adds macros and reusable tests             |
| `dbt_expectations`     | Great Expectations-inspired test suite     |
| `dbt_project_evaluator`| Enforces project best practices            |

> Find more at: [dbt Hub](https://hub.getdbt.com/)
