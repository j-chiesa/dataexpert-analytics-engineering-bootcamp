# 📦 dbt Basics - Day 2

> This session dives deeper into dbt's core features, including the dbt Power User extension, dynamic source definitions, snapshots, generic/custom/unit tests, and best practices for testing data models.

---

## 🔌 dbt Power User Extension (VS Code)

When selecting a dbt model in VS Code, the **dbt Power User** extension provides rich metadata:

* ✅ Model Tests
* 📌 Parent & Child Models
* 🧾 Documentation (editable in the extension)
* ⚙️ Project Actions (health check)
* 🔗 Lineage Graph

> 🌟 An official dbt VS Code extension will be released later this month!

---

## 🧍️‍⚖️ Defining Dynamic Sources

You can dynamically define source schemas based on the target environment:

```yaml
# models/staging/_sources.yml
version: 2

sources:
  - name: bootcamp
    database: dataexpert_student
    schema: |
      {%- if target.name == "prod" -%} bootcamp_prod
      {%- else -%} bootcamp
      {%- endif -%}
    tables:
      - name: js_raw_orders
        freshness:
          warn_after: { count: 1, period: day }
          error_after: { count: 7, period: day }
        loaded_at_field: last_updated_dt
      - name: js_raw_payments
      - name: js_raw_customers
      - name: incremental_example_raw_orders
```

Now you can run models in different environments:

```bash
dbt run -s stg_orders --target prod
```

---

## 🧱 Snapshots

Snapshots let you track slowly changing dimensions (SCD Type 2). Place your snapshot definition inside the `snapshots/` folder:

```yaml
# snapshots/snapshot_customers.yml
snapshots:
  - name: snapshot_customers
    relation: source('bootcamp', 'js_raw_customers')
    config:
      database: dataexpert_student
      schema: snapshots
      strategy: timestamp
      unique_key: id
      updated_at: last_updated_dt
```

Run snapshots with:

```bash
dbt snapshot           # Run all
dbt snapshot -s snapshot_customers  # Run specific
```

---

## ✅ Generic Data Tests

You can test your model fields directly from YAML:

```yaml
# models/staging/stg_orders.yml
version: 2

models:
  - name: stg_orders
    description: staging table for orders
    columns:
      - name: id
        data_tests:
          - unique
            config:
              severity: warn
          - not_null
```

To run the tests:

```bash
dbt build -s stg_orders
```

You can also use **dbt\_expectations** package:

```yaml
- dbt_expectations.expect_column_values_to_be_between:
    min_value: 0
    max_value: 10000
    row_condition: "id is not null"
    strictly: false
```

---

## 🧪 Custom Generic Tests

Create custom tests under `data-tests/generic/`:

```sql
-- data-tests/generic/is_even.sql
{% test is_even(model, column_name) %}

with validation as (
    select {{ column_name }} as value
    from {{ model }}
),
validation_errors as (
    select value from validation
    where (value % 2) = 1
)

select * from validation_errors

{% endtest %}
```

Usage:

```yaml
- name: id
  data_tests:
    - is_even
```

---

## 📊 Unit Tests

Unit tests simulate data input/output for deterministic model validation.

Example for `agg_orders` model:

```sql
-- models/agg_orders.sql
with fact_orders as (
    select order_date, status, amount
    from {{ ref('fact_orders') }}
),
aggregated as (
    select order_date, status, sum(amount) as total_amount
    from fact_orders
    group by order_date, status
)

select * from aggregated
```

```yaml
# models/agg_orders.yml
unit_tests:
  - name: test_amount_sum
    model: agg_orders
    given:
      - input: ref('fact_orders')
        format: csv
        rows: |
          order_date,status,amount
          '2024-01-01',completed,100
          '2024-01-01',completed,100
          '2024-01-02',cancelled,100
          '2024-01-02',shipped,100
    expect:
      format: csv
      rows: |
        order_date,status,total_amount
        '2024-01-01',completed,200
        '2024-01-02',cancelled,100
        '2024-01-02',shipped,100
```

Run the unit test:

```bash
dbt test -s agg_orders
```

---
