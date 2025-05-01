# ❄️ Snowflake — Day 1

> This lab focuses on **cost optimization**, **integrating Iceberg tables**, and **leveraging Snowpark for data ingestion and processing** in Snowflake.

---

## 💸 Costs Optimization

> How to reduce unnecessary compute cost in Snowflake.

1. Go to **Admin → Warehouses → COMPUTE_WH → Edit**:
    - **Suspend After:** `1 minute`
    - **Size:** `X-Small`

✅ This ensures your warehouse shuts down quickly after inactivity and runs on minimal resources.

---

## 🧊 Creating External Iceberg Table

> Access external Iceberg tables from Snowflake via Tabular.

### Step 1: Create Iceberg Table with Trino
```sql
CREATE TABLE javierchiesa.showing_off_integration (
  col VARCHAR,
  date DATE
)
WITH (
  partitioning = ARRAY['date']
);
```

### Step 2: Insert Sample Data
```sql
INSERT INTO javierchiesa.showing_off_integration
VALUES ('javier', DATE('2025-04-24'));
```

### Step 3: Create External Volume in Snowflake
```sql
CREATE OR REPLACE EXTERNAL VOLUME tabular_vol
STORAGE_LOCATIONS =
(
    (
        NAME                 = 'tabular_root',
        STORAGE_PROVIDER     = 'S3',
        STORAGE_BASE_URL     = 's3://zachwilsonsorganization-522/ce557692-2f28-41e8-8250-8608042d2acb/',
        STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::785232649619:role/SnowflakeRole'
    )
)
ALLOW_WRITES = FALSE;
```

### Step 4: Create External Iceberg Table in Snowflake
```sql
CREATE ICEBERG TABLE javierchiesa.showing_off_integration
    EXTERNAL_VOLUME    = 'tabular_vol',
    CATALOG            = 'tabular_catalog_int',
    CATALOG_NAMESPACE  = 'javierchiesa',
    CATALOG_TABLE_NAME = 'showing_off_integration',
    AUTO_REFRESH       = TRUE;
```

---

## 📐 Clustering

> Optimize queries by clustering on frequently filtered/grouped columns.

```sql
ALTER TABLE bootcamp.nba_game_details CLUSTER BY (team_id, player_id);
```

Example queries that benefit from this clustering:
```sql
SELECT *
FROM bootcamp.nba_game_details
WHERE player_id = 2605;

SELECT player_id, MAX(pts)
FROM bootcamp.nba_game_details
GROUP BY player_id;

SELECT team_id, MAX(pts)
FROM bootcamp.nba_game_details
GROUP BY team_id;
```

---

## 🐍 Snowpark

> Use Python to interact with Snowflake just like PySpark.

### `snowflake_queries.py`
```python
import snowflake.connector
from snowflake.snowpark import Session

connection_params = {
    "account": 'aab46027',
    "user": 'dataexpert_student',
    "password": 'DataExpert123!',
    "role": "all_users_role",
    'warehouse': 'COMPUTE_WH',
    'database': 'dataexpert_student'
}

def get_snowpark_session(schema='bootcamp'):
    connection_params['schema'] = schema
    session = Session.builder.configs(connection_params).create()
    return session

def run_snowflake_query_dq_check(query):
    results = execute_snowflake_query(query)
    if len(results) == 0:
        raise ValueError('The query returned no results!')
    for result in results:
        for column in result:
            if type(column) is bool:
                assert column is True

def execute_snowflake_query(query):
    conn = snowflake.connector.connect(**connection_params)
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()
```

### `load_polygon_into_snowflake.py`
```python
import os
import requests
import ast
from include.eczachly.snowflake_queries import get_snowpark_session

def load_snowflake(polygon_key=None):
    session = get_snowpark_session()
    polygon_key = os.environ.get('POLYGON_API_KEY') or ast.literal_eval(polygon_key)['AWS_SECRET_ACCESS_KEY']
    url = 'https://api.polygon.io/v3/reference/tickers?active=true&limit=1000&apiKey=' + polygon_key
    response = requests.get(url).json()

    tickers = response['results']
    table = 'bootcamp.stock_tickers'

    while 'next_url' in response:
        url = response['next_url'] + '&apiKey=' + polygon_key
        response = requests.get(url).json()
        tickers.extend(response['results'])

    example_ticker = tickers[0]
    columns = []
    for key, value in example_ticker.items():
        if 'utc' in key:
            columns.append(key + ' TIMESTAMP')
        elif isinstance(value, str):
            columns.append(key + ' VARCHAR')
        elif isinstance(value, bool):
            columns.append(key + ' BOOLEAN')
        elif isinstance(value, int):
            columns.append(key + ' INTEGER')

    columns_str = ' , '.join(columns)
    create_ddl = f'CREATE TABLE IF NOT EXISTS {table} ({columns_str})'
    session.sql(create_ddl)

    dataframe = session.create_dataframe(tickers, schema=example_ticker.keys())
    dataframe.write.mode("overwrite").save_as_table(table)
```
