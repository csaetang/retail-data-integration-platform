import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"


def extract_inventory(limit=1000, max_batches=None):
    records = []
    offset = 0
    batches = 0

    while True:
        response = requests.get(
            f"{BASE_URL}/inventory",
            params={
                "limit": limit,
                "offset": offset
            },
            timeout=30
        )

        response.raise_for_status()

        result = response.json()
        batch = result["data"]

        if not batch:
            break

        records.extend(batch)
        offset += limit
        batches += 1

        if max_batches is not None and batches >= max_batches:
            break

    return pd.DataFrame(records)