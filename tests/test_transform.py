import pandas as pd

from pipeline.transform.validate import (
    validate_users,
    validate_order_items
)

from pipeline.transform.transform import (
    build_dim_customer,
    build_dim_product,
    build_fact_sales,
    build_inventory_snapshot
)


def test_validate_users_removes_duplicates():
    df = pd.DataFrame({
        "id": [1, 1, 2],
        "email": ["a@test.com", "a@test.com", "b@test.com"],
        "created_at": [
            "2026-01-01",
            "2026-01-01",
            "2026-01-02"
        ]
    })

    result = validate_users(df)

    assert len(result) == 2


def test_validate_users_flags_missing_email():
    df = pd.DataFrame({
        "id": [1, 2],
        "email": ["a@test.com", None],
        "created_at": ["2026-01-01", "2026-01-02"]
    })

    result = validate_users(df)

    assert result["email_missing"].sum() == 1


def test_validate_order_items_rejects_negative_price():
    df = pd.DataFrame({
        "id": [1, 2],
        "product_id": [100, 200],
        "sale_price": [50.00, -10.00],
        "created_at": ["2026-01-01", "2026-01-02"]
    })

    result = validate_order_items(df)

    assert len(result) == 1
    assert result.iloc[0]["sale_price"] == 50.00


def test_build_dim_product_removes_duplicate_products():
    df = pd.DataFrame({
        "id": [1, 1, 2],
        "name": ["Laptop", "Laptop", "Mouse"],
        "category": ["Electronics", "Electronics", "Electronics"],
        "brand": ["Brand A", "Brand A", "Brand B"],
        "cost": [500, 500, 10],
        "retail_price": [700, 700, 20]
    })

    result = build_dim_product(df)

    assert len(result) == 2
    assert "product_id" in result.columns
    assert "product_name" in result.columns


def test_inventory_snapshot_counts_available_stock():
    df = pd.DataFrame({
        "product_id": [1, 1, 1, 2],
        "created_at": [
            "2026-01-01",
            "2026-01-01",
            "2026-01-01",
            "2026-01-01"
        ],
        "sold_at": [
            None,
            None,
            "2026-01-03",
            None
        ]
    })

    result = build_inventory_snapshot(df)

    product_1_stock = result.loc[
        result["product_id"] == 1,
        "stock_quantity"
    ].iloc[0]

    assert product_1_stock == 2