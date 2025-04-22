# 🧊 Apache Iceberg — Day 3

> This lab demonstrates the full WAP (Write-Audit-Publish) pattern in Apache Iceberg.
> It walks through writing to the main branch, validating changes through an audit branch, and promoting the audit branch to production using fast-forwarding.
> It includes automated Glue jobs, schema setup, data quality checks, and safe publishing of data changes.

---

## ♻️ WAP Pattern: Write → Audit → Publish

### 1️⃣ Writing to the `main` Branch

#### 🧪 Ingestion Script (`iceberg_branching_example.py`)
This script ingests stock tickers from the [Polygon API](https://polygon.io), adds a partitioning date, and writes the data into an Iceberg table with WAP enabled:

```python
import sys
from datetime import datetime
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col
import requests

# Initialize Spark and Glue context
spark = SparkSession.builder.getOrCreate()
glueContext = GlueContext(spark.sparkContext)
spark = glueContext.spark_session

# Job arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME", "ds", 'output_table'])
run_date = args['ds']
output_table = args['output_table']

# Polygon API call
api_key = 'api_key'
starter_url = f'https://api.polygon.io/v3/reference/tickers?active=true&limit=1000&apiKey={api_key}'
response = requests.get(starter_url)
data = response.json()
tickers = data['results']

# Fetch additional pages
while data['status'] == 'OK' and 'next_url' in data:
    response = requests.get(data['next_url'] + '&apiKey=' + api_key)
    data = response.json()
    tickers.extend(data['results'])

# Create DataFrame and add partition column
load_date = datetime.strptime(run_date, "%Y-%m-%d").date()
df = spark.createDataFrame(tickers).withColumn('date', lit(load_date))

# Create Iceberg table if not exists
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {output_table} (
    active BOOLEAN,
    cik STRING,
    composite_figi STRING,
    currency_name STRING,
    last_updated_utc STRING,
    locale STRING,
    market STRING,
    name STRING,
    primary_exchange STRING,
    share_class_figi STRING,
    ticker STRING,
    `type` STRING,
    date DATE
)
USING iceberg
PARTITIONED BY (date)
TBLPROPERTIES ('write.wap.enabled' = 'true');
""")

# Write data with overwrite mode and WAP enabled
df.select(
    "active", "cik", "composite_figi", "currency_name", "last_updated_utc",
    "locale", "market", "name", "primary_exchange", "share_class_figi",
    "ticker", "type", "date"
).writeTo(output_table).using("iceberg").partitionedBy("date").overwritePartitions()

job = Job(glueContext)
job.init(args["JOB_NAME"], args)
```

#### 🚀 Run Glue Job (`glue_job_runner.py`)
```python
import os
from include.eczachly.aws_secret_manager import get_secret
from include.eczachly.glue_job_submission import create_glue_job
from dotenv import load_dotenv
load_dotenv()

schema = os.getenv("SCHEMA")
local_script_path = os.path.join("include", 'eczachly/scripts/iceberg_branching_example.py')
create_and_run_glue_job(f'iceberg_main_{schema}',
    script_path=local_script_path,
    arguments={'--ds': '2024-11-21', '--output_table': f'{schema}.branching_stock_tickers'})
```

#### 📄 Check Iceberg Branches
```sql
SELECT * FROM javierchiesa."branching_stock_tickers$refs";
```

| NAME | TYPE  | SNAPSHOT_ID         | MAX_REFERENCE_AGE_IN_MS | MIN_SNAPSHOTS_TO_KEEP | MAX_SNAPSHOT_AGE_IN_MS |
|------|-------|---------------------|--------------------------|------------------------|-------------------------|
| main | BRANCH| 4987149624528344000 | null                     | null                   | null                   |

---

### 2️⃣ Writing to the `audit_branch`

#### 🔧 Modify `glue_job_runner.py` to use audit branch
```python
create_and_run_glue_job(f'iceberg_audit_{schema}',
    script_path=local_script_path,
    arguments={'--ds': '2024-11-21',
               '--output_table': f'{schema}.branching_stock_tickers',
               '--branch': 'audit_branch'})
```

#### 🖋️ Validate Branch Creation
```sql
SELECT * FROM javierchiesa."branching_stock_tickers$refs";
```

| NAME         | TYPE   | SNAPSHOT_ID         | MAX_REFERENCE_AGE_IN_MS | MIN_SNAPSHOTS_TO_KEEP | MAX_SNAPSHOT_AGE_IN_MS |
|--------------|--------|---------------------|--------------------------|------------------------|-------------------------|
| audit_branch | BRANCH | 8251856541678302000 | null                     | null                   | null                   |
| main         | BRANCH | 4987149624528344000 | null                     | null                   | null                   |

---

### 3️⃣ Audit the Data

#### 🔎 Duplicate Detection
```sql
SELECT COUNT(DISTINCT ticker) = COUNT(ticker) AS there_are_no_duplicates
FROM javierchiesa.branching_stock_tickers FOR VERSION AS OF 'audit_branch';
```

**Result:**
| there_are_no_duplicates |
|-------------------------|
| false                   |

#### 🛠️ Clean the Data: Remove Duplicates
```python
df.select(
    col("active"),
    col("cik"),
    col("composite_figi"),
    upper(col("currency_name")).alias("currency_name"),
    col("last_updated_utc"),
    col("locale"),
    col("market"),
    col("name"),
    col("primary_exchange"),
    col("share_class_figi"),
    col("ticker"),
    col("type"),
    col("date")
).dropDuplicates(['ticker']).writeTo(output_table)
 .using("iceberg")
 .partitionedBy("date")
 .overwritePartitions()
```

#### 🔍 Run Data Quality Checks on `audit_branch`
```sql
WITH last_week_row_count AS (
  SELECT COUNT(1) AS count
  FROM javierchiesa.branching_stock_tickers
  WHERE date = DATE('2025-04-14')
),
checks AS (
SELECT 
  COUNT(DISTINCT ticker) = COUNT(ticker) AS there_are_no_duplicates,
  COUNT(CASE WHEN market = 'stocks' AND primary_exchange IS NULL THEN 1 END) = 0 AS all_stocks_have_primary_exchanges,
  COUNT(CASE WHEN locale = 'us' AND currency_name NOT IN ('usd', 'USD') THEN 1 END) = 0 AS all_us_stocks_trade_in_usd,
  COUNT(CASE WHEN market = 'otc' AND primary_exchange IS NOT NULL THEN 1 END) = 0 AS all_otc_stocks_not_on_exchanges,
  COUNT(CASE WHEN market IS NULL THEN 1 END) = 0 AS market_is_never_null,
  COUNT(CASE WHEN locale IS NULL THEN 1 END) = 0 AS locale_is_never_null,
  COUNT(1) >= (SELECT count FROM last_week_row_count) AS more_stocks_than_last_week
FROM javierchiesa.branching_stock_tickers FOR VERSION AS OF 'audit_branch'
)
SELECT 
  there_are_no_duplicates AND
  all_stocks_have_primary_exchanges AND
  all_us_stocks_trade_in_usd AND
  all_otc_stocks_not_on_exchanges AND
  market_is_never_null AND
  locale_is_never_null AND
  more_stocks_than_last_week AS all_checks_pass
FROM checks;
```

**Result:**
| all_checks_pass |
|-------------------------|
| true                 |

---

### 4️⃣ Publish with Fast-Forwarding

#### 🔄 Promote Branch to Main
```python
# Run glue job again without --branch to publish audit branch to main
```

#### 🔢 Confirm Audit on `main`
```sql
WITH last_week_row_count AS (
  SELECT COUNT(1) AS count
  FROM javierchiesa.branching_stock_tickers
  WHERE date = DATE('2025-04-14')
),
checks AS (
SELECT 
  COUNT(DISTINCT ticker) = COUNT(ticker) AS there_are_no_duplicates,
  COUNT(CASE WHEN market = 'stocks' AND primary_exchange IS NULL THEN 1 END) = 0 AS all_stocks_have_primary_exchanges,
  COUNT(CASE WHEN locale = 'us' AND currency_name NOT IN ('usd', 'USD') THEN 1 END) = 0 AS all_us_stocks_trade_in_usd,
  COUNT(CASE WHEN market = 'otc' AND primary_exchange IS NOT NULL THEN 1 END) = 0 AS all_otc_stocks_not_on_exchanges,
  COUNT(CASE WHEN market IS NULL THEN 1 END) = 0 AS market_is_never_null,
  COUNT(CASE WHEN locale IS NULL THEN 1 END) = 0 AS locale_is_never_null,
  COUNT(1) >= (SELECT count FROM last_week_row_count) AS more_stocks_than_last_week
FROM javierchiesa.branching_stock_tickers
)
SELECT 
  there_are_no_duplicates AND
  all_stocks_have_primary_exchanges AND
  all_us_stocks_trade_in_usd AND
  all_otc_stocks_not_on_exchanges AND
  market_is_never_null AND
  locale_is_never_null AND
  more_stocks_than_last_week AS all_checks_pass
FROM checks;
```

**Result:**
| all_checks_pass |
|-------------------------|
| true                 |

---

### 5️⃣ Drop the `audit_branch` once data is validated and promoted.
Once all data quality checks pass and the changes have been published to the main branch, the audit_branch can be safely dropped to clean up the environment.
