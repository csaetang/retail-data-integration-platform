import pandas as pd


def extract_products():
    columns = [
        "id",
        "name",
        "category",
        "brand",
        "cost",
        "retail_price"
    ]

    return pd.read_csv(
        "data/products.csv",
        usecols=columns
    )