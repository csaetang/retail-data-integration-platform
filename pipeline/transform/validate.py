import pandas as pd


def validate_users(df):
    df = df.copy()

    # Remove duplicate users
    df = df.drop_duplicates(subset=["id"])

    # Flag missing emails rather than rejecting customer
    df["email_missing"] = (
        df["email"].isna() |
        (df["email"].astype(str).str.strip() == "")
    )

    # Validate timestamp
    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df = df[df["created_at"].notna()]

    return df


def validate_orders(df):
    df = df.copy()

    df = df.drop_duplicates(subset=["order_id"])

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df = df[df["created_at"].notna()]

    return df


def validate_order_items(df):
    df = df.copy()

    df = df.drop_duplicates(subset=["id"])

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    valid = (
        df["product_id"].notna()
        & df["created_at"].notna()
        & df["sale_price"].notna()
        & (df["sale_price"] >= 0)
    )

    return df[valid]