import os

from include.eczachly.aws_secret_manager import get_secret
from include.eczachly.glue_job_runner import create_and_run_glue_job

from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import DayTransform, IdentityTransform
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.types import (
    DoubleType,
    StringType,
    NestedField,
    LongType,
    DateType,
)


def create_table_if_not_exists(catalog):
    """
    Create an Iceberg table with the specified schema, partitioning, and sort order if it does not exist.

    Args:
        catalog: PyIceberg catalog instance to operate on.
    """
    schema = Schema(
        NestedField(field_id=1, name="ticker", field_type=StringType(), required=False),
        NestedField(field_id=2, name="v", field_type=DoubleType(), required=False),
        NestedField(field_id=3, name="vw", field_type=DoubleType(), required=False),
        NestedField(field_id=4, name="o", field_type=DoubleType(), required=False),
        NestedField(field_id=5, name="c", field_type=DoubleType(), required=False),
        NestedField(field_id=6, name="h", field_type=DoubleType(), required=False),
        NestedField(field_id=7, name="l", field_type=DoubleType(), required=False),
        NestedField(field_id=8, name="t", field_type=LongType(), required=False),
        NestedField(field_id=9, name="n", field_type=LongType(), required=False),
        NestedField(field_id=10, name="date", field_type=DateType(), required=False)
    )

    partition_spec = PartitionSpec(
        PartitionField(
            source_id=10,
            field_id=1000,
            transform=DayTransform(),
            name="date"
        )
    )

    sort_order = SortOrder(
        SortField(
            source_id=10,
            transform=IdentityTransform()
        )
    )

    catalog.create_table_if_not_exists(
        identifier="javierchiesa.maang_stock_prices",
        schema=schema,
        partition_spec=partition_spec,
        sort_order=sort_order,
        properties={"write.wap.enabled": "true"}
    )


def write_to_branch(date):
    """
    Run the Glue job to write stock prices to the 'audit_branch'.

    Args:
        date (str): Date to process in format YYYY-MM-DD.
    """
    local_script_path = os.path.join("homeworks", "week_1", "stock_prices_branching.py")
    create_and_run_glue_job(
        'stock_prices_branching_javierchiesa',
        script_path=local_script_path,
        arguments={
            '--ds': date,
            '--output_table': "javierchiesa.maang_stock_prices",
            '--branch': 'audit_branch'
        }
    )


def fast_forwarding(date):
    """
    Run the Glue job to fast-forward the branch changes to the main table.

    Args:
        date (str): Date to process in format YYYY-MM-DD.
    """
    local_script_path = os.path.join("homeworks", "week_1", "stock_prices_branching.py")
    create_and_run_glue_job(
        'stock_prices_branching_javierchiesa',
        script_path=local_script_path,
        arguments={
            '--ds': date,
            '--output_table': "javierchiesa.maang_stock_prices"
        }
    )


if __name__ == "__main__":
    # Load Iceberg catalog
    catalog = load_catalog(
        'academy',
        type="rest",
        uri="https://api.tabular.io/ws",
        warehouse=get_secret("CATALOG_NAME"),
        credential=get_secret("TABULAR_CREDENTIAL")
    )

    # Set date for fetching the data
    date = '2025-01-06'

    # Create table if it doesn't exist
    create_table_if_not_exists(catalog)

    # Uncomment the line below to write to a branch (WAP/Audit)
    write_to_branch(date)

    # Uncomment the line below for fast-forwarding branch to main
    fast_forwarding(date)
