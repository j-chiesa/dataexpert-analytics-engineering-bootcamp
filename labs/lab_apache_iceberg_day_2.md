# 🧊 Apache Iceberg — Lab Day 2

> This lab explores the compaction process in Apache Iceberg and how it affects performance and storage efficiency.
> It also covers the movement of data between Iceberg and Snowflake, using dynamic tables and Snowpark for integration.
> Finally, a latency comparison highlights when to use Trino, Snowflake, or Spark depending on data volume and performance needs.

## ⚙️ Iceberg Compaction

---

```sql
CREATE TABLE javierchiesa.test_compaction (col BIGINT, name VARCHAR);
```

### ➕ Insert multiple rows (in 3 separate batches)

```sql
INSERT INTO javierchiesa.test_compaction VALUES (345, 'Javier'), (3747467, 'Javier'), (75673, 'Javier');
INSERT INTO javierchiesa.test_compaction VALUES (2423, 'Javier'), (378394748, 'Javier'), (4738, 'Javier');
INSERT INTO javierchiesa.test_compaction VALUES (987654, 'Javier'), (127654, 'Javier'), (87, 'Javier');
```

### 🔍 Inspect file-level metadata

```sql
SELECT * FROM javierchiesa."test_compaction$files";
```

- We observe 3 small Parquet files, each with 3 records.
- All rows have the same value in the `name` column → opportunity for **Run-Length Encoding** (RLE).
- Goal: compact the files and **reduce size** by improving compression and file organization.

```sql
SELECT COUNT(1) AS count_files, SUM(file_size_in_bytes) AS sum_size_files
FROM javierchiesa."test_compaction$files";
```

| count_files | sum_size_files |
|-------------|----------------|
| 3           | 1305           |

---

### ✨ Compaction with AWS Glue + Spark

#### 💪 Spark Glue Job: `iceberg_compaction_example.py`

```python
import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import SparkSession

spark = (SparkSession.builder.getOrCreate())
args = getResolvedOptions(sys.argv, ["JOB_NAME", "ds", 'output_table'])
run_date = args['ds']
output_table = args['output_table']
glueContext = GlueContext(spark.sparkContext)
spark = glueContext.spark_session

spark.sql(f""" CALL system.rewrite_data_files( 
  table => '{output_table}',
  strategy => 'sort',
  sort_order => 'zorder(name)',
  options => map('rewrite-all', 'true') )
""")

job = Job(glueContext)
job.init(args["JOB_NAME"], args)
```

#### ⚙️ Glue Job Submission: `glue_job_runner.py`

```python
from include.eczachly.aws_secret_manager import get_secret
from include.eczachly.glue_job_submission import create_glue_job
import os
from dotenv import load_dotenv
load_dotenv()

schema = os.getenv("SCHEMA")  # javierchiesa

local_script_path = os.path.join("include", 'eczachly/scripts/iceberg_compaction_example.py')
create_and_run_glue_job(f'iceberg_compaction_example_{schema}',
                        script_path=local_script_path,
                        arguments={'--ds': '2024-11-21', '--output_table': f'{schema}.test_compaction'})
```

> ℹ️ **Note:** Trino does not support file compaction natively. This is why we use AWS Glue and Spark.

---

### 📊 Post-compaction check

```sql
SELECT COUNT(1) AS count_files, SUM(file_size_in_bytes) AS sum_size_files
FROM javierchiesa."test_compaction$files";
```

| count_files | sum_size_files |
|-------------|----------------|
| 1           | 778            |

- ✅ Files reduced from 3 → 1
- ✅ Total size reduced from 1305 → 778 bytes

---

## 🛫 Data Movement: Iceberg → Snowflake

### 🚀 Dynamic Apache Iceberg Tables

```sql
CREATE DYNAMIC ICEBERG TABLE product (
  product_id NUMBER(10,0), 
  product_name STRING, 
  order_time TIMESTAMP_NTZ
)
  TARGET_LAG = '20 minutes'
  WAREHOUSE = my_warehouse
  EXTERNAL_VOLUME = 'my_external_volume'
  CATALOG = 'SNOWFLAKE'
  BASE_LOCATION = 'my_iceberg_table'
AS
  SELECT product_id, product_name, order_time FROM staging_table;
```

- No need for external ETL jobs.
- **Managed** → data is copied from Iceberg into Snowflake.
- Requires schema to be defined up front.

### 🤖 Snowpark Approach

```python
from include.eczachly.trino_queries import execute_trino_query
from include.eczachly.snowflake_queries import get_snowpark_session

def get_data_and_schema_from_trino(table):
    snowflake_session = get_snowpark_session('bootcamp')
    data = execute_trino_query(f'SELECT * FROM {table}')
    schema = execute_trino_query(f'DESCRIBE {table}')
    column_names = [col[0] for col in schema]
    columns = [' '.join(col) for col in schema]

    current_config = snowflake_session.sql("SELECT CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA()").collect()
    print(f"Using warehouse: {current_config[0][0]}, database: {current_config[0][1]}, schema: {current_config[0][2]}")

    create_ddl = f'CREATE TABLE IF NOT EXISTS {table} ({','.join(columns)})'
    snowflake_session.sql(create_ddl)

    write_df = snowflake_session.create_dataframe(data, schema=column_names)
    write_df.write.mode("overwrite").save_as_table(table)
    snowflake_session.close()

get_data_and_schema_from_trino('bootcamp.web_events')
```

- Works without predefining schema
- Uses Python to pipe data from Trino → Snowflake
- Not optimal for large datasets due to performance limitations
- Snowpark mimics Spark but executes Snowflake-native SQL under the hood

---

## ⏱️ Latency: Trino vs Snowflake

- ❄️ **Snowflake** has significantly lower latency than Trino → better for dashboards
- 🧮 Pre-aggregate in Trino if using it for BI tools
- 🐢 Spark = most resilient, but slowest
- ⚖️ Trino is a middle ground
- 🚀 Snowflake/BigQuery = great for ≈ a few TBs or less
- 🏋️ Use Spark for 4+ TB of data
