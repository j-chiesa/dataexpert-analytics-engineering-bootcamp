# 📦 dbt Basics - Day 1

> In this class we covered what dbt is, what problems it solves, its architecture, features, and best practices for modeling and structuring data transformation projects.

---

## 🔎 What is dbt?

* Open source tool used to model data in a data warehouse.
* A development framework that combines modular SQL with software engineering best practices to create a better, faster, and more reliable data transformation experience.
* SQL-friendly, allowing engineers, analysts, and scientists to work together using the same language.

> dbt is a tool that enables anyone comfortable with SQL to work on transformation pipelines using the best practices in software engineering.

---

## 🚫 What problem does dbt solve?

* Lack of testing, documentation, and modularity in stored procedures.
* Version control and data lineage are lost in traditional pipelines.
* Easier to re-write stored procedures code than fix existing logic.
* Hard to understand transformation code. Analysts don’t know what to trust.
* Leads to "data chaos."

---

## 🌟 dbt Viewpoint

* **Code reigns**: SQL-first, democratizes data
* **Best practices from software engineering**:

  * Testing
  * Version control
  * DRY code
  * Documentation
* **Data lineage and dependency management**

Builds more understandable pipelines, improves development, testing, and maintenance.

---

## 🧰 What is dbt?

* Transformation-only tool: needs to be paired with ingestion/storage tools.
* Runs inside orchestration frameworks (Airflow, Fivetran, Meltano).
* dbt **executes SQL** in your DW.
* Handles creation of views/tables/schemas.
* Handles DML: UPDATE, INSERT, MERGE, DELETE.

---

## 🚫 What dbt is NOT

* dbt **does not** store data (relies on your DW).
* dbt **does not** ingest data.
* dbt **does not** provide compute (relies on DW compute).

---

## 🔖 dbt Editions

### dbt Core

* Free & open source
* Full control, full flexibility
* Requires manual infra setup
* Supports many data warehouses

### dbt Cloud

* Managed (paid) platform
* Easy setup with CI/CD, RBAC, IDE, alerts
* Hosted compute & browser-based IDE
* Git integration
* Documentation hosting
* Supports only dbt Labs-supported warehouses

---

## 🧬 What is an Analytics Engineer?

* Coined by dbt Labs
* Hybrid between Data Engineer and Data Analyst
* Not a new role, but a new definition
* Engineers and analysts both can adopt dbt's toolset

---

## 🔧 Skills Needed

* SQL
* Jinja
* YAML
* Python (optional)
* Data modeling
* Source control (Git)

---

## ❓ Why dbt?

* **Made for data transformation**: dependency mgmt, testing, incrementals
* **SQL-native**
* **Open-source & strong community**
* **Supports collaborative workflows**
* **Highly integrable**

---

## 🚄 Connecting dbt to Your DW

### Cloud Supported Adapters

* Snowflake, BigQuery, Redshift, PostgreSQL, Databricks, Synapse, Fabric, Spark, Athena, Starburst

### Trusted Adapters

* Includes Glue, Oracle, Materialize, Dremio, Netezza

### Community Adapters

* Clickhouse, MySQL, SQL Server, DuckDB, SQLite, DB2, etc.

---

## 📁 dbt Project Structure

* `analyses/`
* `macros/`
* `models/`
* `seeds/`
* `snapshots/`
* `sources/`
* `tests/`

---

## 📊 Models

* SQL or Python scripts
* Materialized into views or tables
* Powered by Jinja templates

```sql
-- models/customers.sql
with customer_orders as (
  select customer_id, min(order_date) as first_order_date,
         max(order_date) as most_recent_order_date,
         count(order_id) as number_of_orders
  from jaffle_shop.orders
  group by 1
)

select c.customer_id, c.first_name, c.last_name,
       co.first_order_date, co.most_recent_order_date,
       coalesce(co.number_of_orders, 0) as number_of_orders
from jaffle_shop.customers c
left join customer_orders co using (customer_id)
```

```sql
-- What dbt compiles and runs:
create view dbt_schema.customers as (
  ... same as above ...
)
```

* Use `{{ ref() }}` and `{{ source() }}` for dependency mgmt and env support

### Materializations

* View
* Table
* Incremental
* Ephemeral

### Configurations

---

## 🔄 Model Best Practices

### Naming Conventions

* **staging**: 1:1 source mapping, light transforms
* **intermediate**: modular logic
* **marts**: business logic, facts/dims

### SQL Organization

* Import CTEs
* Functional CTEs
* Final SELECT

---

## 📰 Sources

* External data defined in YAML
* Not created by dbt
* Often raw data
* Defined with names for reusability


### Benefits

* Centralized definition
* Lineage-aware
* Supports freshness checks

---

## 📄 Seeds

* CSVs turned into tables
* Good for static mappings like country codes
* Version-controlled in repo

---

## ⚠️ Challenges

* Streaming workflows
* Complex DDL
* Over-reliance risks
* Best practices harder in Core

---

## 📃 Useful Commands

* `dbt debug`
* `dbt compile`
* `dbt source freshness`
* `dbt run`
* `dbt test`
* `dbt seed`
* `dbt snapshot`
* `dbt build`
* `dbt docs generate`
* `dbt docs serve`
* `dbt show`

More: [https://docs.getdbt.com/reference/node-selection/syntax](https://docs.getdbt.com/reference/node-selection/syntax)

---

## 🔍 Node Selection

### Graph Operators

* `+model`: upstream
* `model+`: downstream
* `+model+`: both directions
* `1+model+1`: one level up/down
* `model1 model2`: union
* `model1+,model2+`: intersection

More:

* [https://docs.getdbt.com/reference/node-selection/graph-operators](https://docs.getdbt.com/reference/node-selection/graph-operators)
* [https://docs.getdbt.com/reference/node-selection/set-operators](https://docs.getdbt.com/reference/node-selection/set-operators)

### Selection Methods

* `resource_type:model`
* `tag:my_tag`
* `test_type:unit`
* `state:modified`
* `result:error`
* `source:raw+`

More: [https://docs.getdbt.com/reference/node-selection/methods](https://docs.getdbt.com/reference/node-selection/methods)
