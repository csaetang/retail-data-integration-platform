import pandas as pd


def build_dim_customer(users):
    return users[[
        "id",
        "first_name",
        "last_name",
        "email",
        "country",
        "created_at",
        "email_missing"
    ]].rename(columns={
        "id": "customer_id"
    })


def build_dim_product(products):
    products = products.drop_duplicates(subset=["id"])

    return products[[
        "id",
        "name",
        "category",
        "brand",
        "cost",
        "retail_price"
    ]].rename(columns={
        "id": "product_id",
        "name": "product_name"
    })


def build_fact_sales(order_items, orders):
    sales = order_items.merge(
        orders[["order_id", "status"]],
        on="order_id",
        how="left",
        suffixes=("_item", "_order")
    )

    return sales[[
        "id",
        "order_id",
        "user_id",
        "product_id",
        "sale_price",
        "status_order",
        "created_at"
    ]].rename(columns={
        "id": "sale_id",
        "user_id": "customer_id",
        "status_order": "order_status",
        "created_at": "sale_timestamp"
    })


def build_inventory_snapshot(inventory):
    inventory = inventory.copy()

    inventory["created_at"] = pd.to_datetime(
        inventory["created_at"],
        errors="coerce"
    )

    inventory["sold_at"] = pd.to_datetime(
        inventory["sold_at"],
        errors="coerce"
    )

    # Unsold inventory represents currently available stock
    available = inventory[inventory["sold_at"].isna()]

    return (
        available
        .groupby("product_id")
        .size()
        .reset_index(name="stock_quantity")
    )

def build_dim_date(fact_sales):
    dates = pd.to_datetime(
        fact_sales["sale_timestamp"],
        errors="coerce"
    ).dropna()

    start_date = dates.min().normalize()
    end_date = dates.max().normalize()

    date_range = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D"
    )

    dim_date = pd.DataFrame({
        "date": date_range
    })

    dim_date["date_key"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["month_name"] = dim_date["date"].dt.month_name()
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["day"] = dim_date["date"].dt.day
    dim_date["day_of_week"] = dim_date["date"].dt.day_name()

    return dim_date