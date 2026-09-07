import os
import csv
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


load_dotenv()


# --------------------------------------------------
# Database connection
# --------------------------------------------------

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT", "5432")
)

cursor = conn.cursor()


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def clean_text(value):
    """Convert empty/NaN-like strings to None."""
    if value is None:
        return None

    value = value.strip()

    if value == "" or value.lower() in {"nan", "none", "null"}:
        return None

    return value


def parse_int(value):
    value = clean_text(value)

    if value is None:
        return None

    return int(float(value))


def parse_float(value):
    value = clean_text(value)

    if value is None:
        return None

    return float(value)


def parse_timestamp(value):
    value = clean_text(value)

    if value is None:
        return None

    try:
        # Handles values such as:
        # 2022-10-20 10:03:00+00:00
        dt = datetime.fromisoformat(value)

        # PostgreSQL columns are TIMESTAMP WITHOUT TIME ZONE
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)

        return dt

    except ValueError:
        return None


# --------------------------------------------------
# Load users
# --------------------------------------------------

def load_users():
    records = []

    with open(
        "data/users.csv",
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            records.append(
                (
                    parse_int(row["id"]),
                    clean_text(row["first_name"]),
                    clean_text(row["last_name"]),
                    clean_text(row["email"]),
                    clean_text(row["country"]),
                    parse_timestamp(row["created_at"])
                )
            )

    query = """
        INSERT INTO users (
            id,
            first_name,
            last_name,
            email,
            country,
            created_at
        )
        VALUES %s
        ON CONFLICT (id) DO NOTHING
    """

    execute_values(cursor, query, records, page_size=5000)
    conn.commit()

    print(f"users: {len(records):,} rows processed")


# --------------------------------------------------
# Load orders
# --------------------------------------------------

def load_orders():
    records = []

    with open(
        "data/orders.csv",
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            records.append(
                (
                    parse_int(row["order_id"]),
                    parse_int(row["user_id"]),
                    clean_text(row["status"]),
                    parse_timestamp(row["created_at"]),
                    parse_timestamp(row["shipped_at"]),
                    parse_timestamp(row["delivered_at"])
                )
            )

    query = """
        INSERT INTO orders (
            order_id,
            user_id,
            status,
            created_at,
            shipped_at,
            delivered_at
        )
        VALUES %s
        ON CONFLICT (order_id) DO NOTHING
    """

    execute_values(cursor, query, records, page_size=5000)
    conn.commit()

    print(f"orders: {len(records):,} rows processed")


# --------------------------------------------------
# Load order items
# --------------------------------------------------

def load_order_items():
    records = []

    with open(
        "data/order_items.csv",
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            records.append(
                (
                    parse_int(row["id"]),
                    parse_int(row["order_id"]),
                    parse_int(row["user_id"]),
                    parse_int(row["product_id"]),
                    clean_text(row["status"]),
                    parse_float(row["sale_price"]),
                    parse_timestamp(row["created_at"])
                )
            )

    query = """
        INSERT INTO order_items (
            id,
            order_id,
            user_id,
            product_id,
            status,
            sale_price,
            created_at
        )
        VALUES %s
        ON CONFLICT (id) DO NOTHING
    """

    execute_values(cursor, query, records, page_size=5000)
    conn.commit()

    print(f"order_items: {len(records):,} rows processed")


# --------------------------------------------------
# Run loaders
# --------------------------------------------------

try:
    load_users()
    load_orders()
    load_order_items()

    print("\nSource data loaded successfully.")

except Exception as error:
    conn.rollback()
    print("\nERROR:")
    print(error)
    raise

finally:
    cursor.close()
    conn.close()