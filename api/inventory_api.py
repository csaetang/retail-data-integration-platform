from fastapi import FastAPI, Query
import pandas as pd

app = FastAPI(title="Retail Inventory API")

COLUMNS = [
    "id",
    "product_id",
    "created_at",
    "sold_at",
    "cost",
    "product_category",
    "product_name",
    "product_retail_price",
    "product_distribution_center_id"
]

inventory = pd.read_csv(
    "data/inventory_items.csv",
    usecols=COLUMNS
)

inventory = inventory.astype(object).where(pd.notnull(inventory), None)


@app.get("/inventory")
def get_inventory(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    result = inventory.iloc[offset:offset + limit].copy()
    result = result.astype(object).where(pd.notnull(result), None)

    return {
        "offset": offset,
        "limit": limit,
        "count": len(result),
        "data": result.to_dict(orient="records")
    }


@app.get("/inventory/product/{product_id}")
def get_product_inventory(product_id: int):
    result = inventory[inventory["product_id"] == product_id].copy()
    result = result.astype(object).where(pd.notnull(result), None)

    return {
        "product_id": product_id,
        "count": len(result),
        "data": result.to_dict(orient="records")
    }