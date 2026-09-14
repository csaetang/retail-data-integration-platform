from pipeline.extract.postgres_extract import extract_table
from pipeline.extract.products_extract import extract_products
from pipeline.extract.inventory_extract import extract_inventory

from pipeline.load.bigquery_loader import (
    load_dataframe_to_bigquery,
    get_max_sale_id
)

from pipeline.transform.validate import (
    validate_users,
    validate_orders,
    validate_order_items
)

from pipeline.transform.transform import (
    build_dim_customer,
    build_dim_product,
    build_fact_sales,
    build_inventory_snapshot,
    build_dim_date
)


def run_pipeline():
    print("Extracting data...")

    users = extract_table("users")
    orders = extract_table("orders")
    order_items = extract_table("order_items")
    products = extract_products()
    inventory = extract_inventory()

    print("\nValidating data...")

    users = validate_users(users)
    orders = validate_orders(orders)
    order_items = validate_order_items(order_items)

    print("\nTransforming data...")

    dim_customer = build_dim_customer(users)
    dim_product = build_dim_product(products)
    fact_sales = build_fact_sales(order_items, orders)

    max_sale_id = get_max_sale_id()

    new_fact_sales = fact_sales[
        fact_sales["sale_id"] > max_sale_id
    ].copy()

    dim_date = build_dim_date(fact_sales)
    inventory_snapshot = build_inventory_snapshot(inventory)

    print("\nPipeline results:")
    print(f"dim_customer:       {len(dim_customer):,}")
    print(f"dim_product:        {len(dim_product):,}")
    print(f"fact_sales:         {len(fact_sales):,}")
    print(f"new_fact_sales:     {len(new_fact_sales):,}")
    print(f"dim_date:           {len(dim_date):,}")
    print(f"inventory_snapshot: {len(inventory_snapshot):,}")

    print("\nLoading to BigQuery...")

    load_dataframe_to_bigquery(dim_customer, "dim_customer")
    load_dataframe_to_bigquery(dim_product, "dim_product")
    load_dataframe_to_bigquery(dim_date, "dim_date")

    if not new_fact_sales.empty:
        load_dataframe_to_bigquery(
            new_fact_sales,
            "fact_sales",
            write_disposition="WRITE_APPEND"
        )
    else:
        print("fact_sales: no new rows to load")

    load_dataframe_to_bigquery(
        inventory_snapshot,
        "inventory_snapshot"
    )

    return {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "fact_sales": fact_sales,
        "dim_date": dim_date,
        "inventory_snapshot": inventory_snapshot
    }


if __name__ == "__main__":
    run_pipeline()