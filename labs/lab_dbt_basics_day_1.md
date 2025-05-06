# 📦 dbt Basics - Day 1

> This hands-on session walks through essential setup and execution of a dbt project, including profile and project configuration, staging models, seeds, commands, and documentation generation.

---

## Important files

### `dbt_project.yml`

```yaml
name: 'jaffle_shop'

config-version: 2
version: '0.1'

profile: 'jaffle_shop'

model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests", "data-tests"]
analysis-paths: ["analysis"]
macro-paths: ["macros"]

target-path: "target"
clean-targets:
    - "target"
    - "dbt_modules"
    - "logs"

require-dbt-version: [">=1.0.0", "<2.0.0"]

models:
  jaffle_shop:
      materialized: table
      staging:
        materialized: view
```

### `profiles.yml`

```yaml
jaffle_shop:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: # account

      # User/password auth
      user: # user
      password: # password

      role: ALL_USERS_ROLE
      database: DATAEXPERT_STUDENT
      warehouse: COMPUTE_WH
      schema: "{{ env_var('STUDENT_SCHEMA')}}"
      threads: 1
      client_session_keep_alive: False
      query_tag: "{{ env_var('STUDENT_SCHEMA')}}"

      # optional
      connect_retries: 0 # default 0
      connect_timeout: 10 # default: 10
      retry_on_database_errors: False # default: false
      retry_all: False  # default: false
      reuse_connections: True # default: True if client_session_keep_alive is False, otherwise None

    prod:
      type: snowflake
      account: # account

      # User/password auth
      user: # user
      password: # password

      role: ALL_USERS_ROLE
      database: DATAEXPERT_STUDENT
      warehouse: COMPUTE_WH
      schema: "{{ env_var('STUDENT_SCHEMA')}}_prod"
      threads: 1
      client_session_keep_alive: False
      query_tag: "{{ env_var('STUDENT_SCHEMA')}}_prod"

      # optional
      connect_retries: 0 # default 0
      connect_timeout: 10 # default: 10
      retry_on_database_errors: False # default: false
      retry_all: False  # default: false
      reuse_connections: True # default: True if client_session_keep_alive is False, otherwise None
```

---
## Important commands

* `dbt debug`: Checks if all the connections defined in your `profiles.yml` file work.
* `dbt deps`: Install packages/plugins from your `packages.yml` file.

---
## Working with `models/staging`

1. Create the `_sources.yml` file inside the `staging` folder:

```yaml
# _sources.yml
version: 2

sources:
  - name: jaffle_shop
    database: raw  
    schema: jaffle_shop  
    tables:
      - name: orders
      - name: customers

  - name: stripe
    tables:
      - name: payments
```

```yaml
version: 2

sources:
  - name: bootcamp
    database: dataexpert_student
    schema: bootcamp
    tables:
      - name: js_raw_orders
        freshness:
          warn_after:
            count: 1
            period: day
          error_after:
            count: 7
            period: day
        loaded_at_field: last_updated_dt

      - name: js_raw_payments
      - name: js_raw_customers

      - name: incremental_example_raw_orders
```

2. Run `dbt source freshness` to check freshness based on defined rules.
3. Create your first staging model: `stg_orders.sql`

```sql
with
    staging as (
        select
            id
            , user_id
            , order_date
            , status
        from {{ source('bootcamp', 'js_raw_orders') }}
    )

select *
from staging
```

4. Run: `dbt run -s stg_orders`
5. Check your data warehouse; the `stg_orders` model should now exist.

Materialization type can be defined in `dbt_project.yml`:

```yaml
models:
  jaffle_shop:
      materialized: table
      staging:
        materialized: view
```

Or within your model:

```sql
{{ config(
    materialized='table'
) }}

with
    staging as (
        select
            id
            , first_name
            , last_name
            , last_updated_dt
            , country_code
            , dbt_valid_to
            , dbt_valid_from
            , row_number() over (
                partition by id
                order by dbt_valid_to desc
            ) as row_num
        from {{ ref('snapshot_customers') }}
    )

select *
from staging
where row_num = 1
```

---
## Working with Seeds

1. Create a CSV file inside the `seeds` folder:

```
code,name
BR,Brazil
UK,United Kingdom
US,United States
JP,Japan
CN,China
CA,Canada
DE,Germany
FR,France
IT,Italy
IN,India
```

2. Run: `dbt seed`
3. The table will be created in your DW as defined in `profiles.yml`

---
## `dbt build`

* Runs the entire project and updates all models in your data warehouse.

---
## `target/run` folder
* Contains the compiled SQL that dbt runs in your DW.
* Useful for debugging and inspecting what will be executed.

---
## `dbt docs generate`
* Generates documentation files.
* Run `dbt docs serve` to open a local interactive web app with your project's lineage and model metadata.
