import os

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

def get_max_sale_id():
    client = get_bigquery_client()

    project_id = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BQ_DATASET")

    table_id = f"{project_id}.{dataset}.fact_sales"

    query = f"""
        SELECT MAX(sale_id) AS max_sale_id
        FROM `{table_id}`
    """

    try:
        result = client.query(query).result()
        row = next(result)

        return row.max_sale_id if row.max_sale_id is not None else 0

    except Exception:
        return 0

def get_bigquery_client():
    project_id = os.getenv("GCP_PROJECT_ID")

    if not project_id:
        raise ValueError("GCP_PROJECT_ID is missing from .env")

    return bigquery.Client(project=project_id)


def load_dataframe_to_bigquery(df, table_name, write_disposition="WRITE_TRUNCATE"):
    client = get_bigquery_client()

    project_id = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BQ_DATASET")

    if not dataset:
        raise ValueError("BQ_DATASET is missing from .env")

    table_id = f"{project_id}.{dataset}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition
    )

    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=job_config
    )

    job.result()

    table = client.get_table(table_id)

    print(
        f"{table_name}: {table.num_rows:,} rows loaded to BigQuery"
    )

    