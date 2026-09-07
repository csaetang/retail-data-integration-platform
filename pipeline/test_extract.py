from pipeline.extract.postgres_extract import extract_table
from pipeline.extract.products_extract import extract_products
from pipeline.extract.inventory_extract import extract_inventory


print("Testing PostgreSQL...")
users = extract_table("users")
print("users:", len(users))

orders = extract_table("orders")
print("orders:", len(orders))

order_items = extract_table("order_items")
print("order_items:", len(order_items))


print("\nTesting products CSV...")
products = extract_products()
print("products:", len(products))


print("\nTesting inventory API...")
inventory = extract_inventory(limit=5, max_batches=1)
print(inventory.head())