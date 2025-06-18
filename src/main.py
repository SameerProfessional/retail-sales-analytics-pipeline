import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
snowflake_user = os.getenv("SNOWFLAKE_USER")
snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
snowflake_database = os.getenv("SNOWFLAKE_DATABASE")
snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA")
snowflake_warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

# Create Snowflake connection
conn = snowflake.connector.connect(
    user=snowflake_user,
    password=snowflake_password,
    account=snowflake_account,
    database=snowflake_database,
    schema=snowflake_schema,
    warehouse=snowflake_warehouse
)

# Create a cursor
cur = conn.cursor()

# Utility function to insert data from DataFrame to Snowflake
def insert_dataframe(df, table_name, cur):
    # Optional: remove ID column if auto-incremented
    id_col = f"{table_name[:-1].upper()}_ID"
    if id_col in df.columns.str.upper():
        df = df.loc[:, df.columns.str.upper() != id_col]

    # Use UPPERCASE column names without quotes
    columns = [col.strip().upper() for col in df.columns]
    column_list = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))

    sql = f'INSERT INTO {table_name.upper()} ({column_list}) VALUES ({placeholders})'
    print(f"Running SQL: {sql}")  # for debugging

    for _, row in df.iterrows():
        cur.execute(sql, tuple(row))





# Load and insert each CSV
data_path = "data/raw"

tables = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv"
}

for table, filename in tables.items():
    print(f"Inserting into {table}...")
    df = pd.read_csv(os.path.join(data_path, filename))
        # Drop the autoincrement ID column if it exists
    id_col = f"{table[:-1]}_id"  # e.g., 'customer_id' for 'customers'
    if id_col in df.columns:
        df = df.drop(columns=[id_col])
    insert_dataframe(df, table, cur)
    conn.commit()

cur.close()
conn.close()
print("All data inserted into Snowflake.")
