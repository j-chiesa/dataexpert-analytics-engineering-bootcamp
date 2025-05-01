"""
Glue Job Script for Fetching MAANG Stock Data and Writing to Iceberg Table

This script retrieves aggregated daily stock data for a set of MAANG stocks
from the Polygon.io API, processes the data into the required schema, and
writes the results into an Iceberg table using AWS Glue and PySpark.
"""

import sys
from datetime import datetime, timezone
from ast import literal_eval
import requests

from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# --- Spark/Glue context setup ---
spark = SparkSession.builder.getOrCreate()
args = getResolvedOptions(
    sys.argv, ["JOB_NAME", "ds", "output_table", "polygon_credentials"]
)

# --- Job parameters ---
api_date = args.get("ds")
output_table = args.get("output_table")
polygon_credentials = args.get("polygon_credentials")
polygon_api_key = literal_eval(polygon_credentials).get("AWS_SECRET_ACCESS_KEY")

# Optionally capture branch name if provided
branch_name = None
for idx, arg in enumerate(sys.argv):
    if arg == "--branch":
        branch_name = sys.argv[idx + 1]
        break

glue_context = GlueContext(spark.sparkContext)
spark = glue_context.spark_session

# --- Stock configuration and API URL ---
MAANG_STOCKS = ["AAPL", "AMZN", "NFLX", "GOOGL", "META"]
POLYGON_URL = (
    "https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date}/{date}"
    "?adjusted=true&sort=asc&apiKey={polygon_api_key}"
)


def fetch_stock_data():
    """
    Fetch aggregated daily bar data for all configured MAANG stocks from the Polygon.io API.

    Returns:
        list[dict]: A list of stock data rows (dicts) for the specified date.
    """
    agg_bars = []
    for ticker in MAANG_STOCKS:
        try:
            response = requests.get(
                POLYGON_URL.format(
                    ticker=ticker,
                    date=api_date,
                    polygon_api_key=polygon_api_key,
                ),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"[ERROR] {ticker} → {e}")
            continue

        results = data.get("results") or []
        if not results:
            print(f"[WARNING] No data for {ticker} on {api_date}")
            continue

        agg_bars.extend(
            [{
                "ticker": ticker,
                "v": float(row.get("v", 0)),
                "vw": float(row.get("vw", 0)),
                "o": float(row.get("o", 0)),
                "c": float(row.get("c", 0)),
                "h": float(row.get("h", 0)),
                "l": float(row.get("l", 0)), 
                "t": int(row.get("t", 0)),
                "n": int(row.get("n", 0)),
                "date": datetime.fromtimestamp(row.get("t") / 1000, tz=timezone.utc).date()
            } for row in results]
)
    return agg_bars


def main():
    """
    Main entrypoint for the Glue ETL job.
    Fetches, processes, and writes stock data to Iceberg table.
    """
    # Initialize Glue job for bookkeeping
    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    agg_bars = fetch_stock_data()

    if not agg_bars:
        print(f"[INFO] No data for any ticker on {api_date}. Ending job without writing.")
        job.commit()
        return

    # Create Spark DataFrame
    df = spark.createDataFrame(agg_bars)
    df.show()

    # Select required columns and print schema for debugging
    df = df.select(
        col("ticker"),
        col("v"),
        col("vw"),
        col("o"),
        col("c"),
        col("h"),
        col("l"),
        col("t"),
        col("n"),
        col("date")
    )

    df.printSchema()

    # Write data to Iceberg table, partitioned by date
    df.writeTo(output_table).using("iceberg").partitionedBy("date").overwritePartitions()

    # If not running in a branch, clean up the audit branch if it exists
    if not branch_name:
        spark.catalog.refreshTable("javierchiesa.maang_stock_prices")
        spark.sql("ALTER TABLE javierchiesa.maang_stock_prices DROP BRANCH audit_branch")

    job.commit()


if __name__ == "__main__":
    main()