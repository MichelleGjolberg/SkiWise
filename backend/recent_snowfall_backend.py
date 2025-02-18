## file to pull from a weather API 
# will have a list of the resorts that are within the user-defined distance range and make API calls to get the recent snowfall at that location

import sys
import os
import base64
import jsonpickle, json
import requests

# from google.cloud.sql.connector import Connector
# from google.cloud import storage
# import sqlalchemy
# from sqlalchemy import text
# from flask import Flask, request, Response
# import datetime
import pandas as pd
import psycopg2


# Synoptic data API
# token: fda25733baec41ee90dd23653e94a1a8
# key: KuOMm49ZKk4W5zFM2YEVmGID1bIaXFgJKUmJI2tekJ

# snow_depth, snow_accum, precip_storm, precip_accum_six_hour, precip_accum_six_hour, snow_accum_since_7_local, snow_accum_24_hour


API_ROOT = "https://api.synopticdata.com/v2/"
API_TOKEN = "fda25733baec41ee90dd23653e94a1a8"

# https://api.synopticdata.com/v2/stations/metadata?token={your token}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}



def import_csv_to_db(csv_path: str, table_name: str = "ski_resort_stats"):
    # read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)
    print(f"CSV file loaded with {len(df)} rows.")

    # # Import the DataFrame to PostgreSQL using the SQLAlchemy engine (pool)
    # # If the table exists, it will be replaced; use 'append' to add to an existing table.
    # df.to_sql(table_name, pool, if_exists='replace', index=False)
    # print(f"Data successfully imported into the '{table_name}' table.")

    return df

df = import_csv_to_db('ski_resort_stats.csv')

# filter to only include CO resorts
# Clean up the 'state' column in case of extra whitespace
df['state'] = df['state'].str.strip()

# Filter for resorts in Colorado
colorado_df = df[df['state'] == "Colorado"]
print(f"Filtered data: {len(colorado_df)} rows for Colorado resorts.")

# # Import the filtered DataFrame to PostgreSQL
# # if_exists='replace' drops the table if it exists. Use 'append' if you want to add to an existing table.
# colorado_df.to_sql(table_name, pool, if_exists='replace', index=False)
# print(f"Data successfully imported into the '{table_name}' table.")

print(colorado_df)



def get_db_connection():
    print("getting db connection")
    conn = psycopg2.connect(
        host="34.46.13.43",
        database="postgres",
        user="postgres",
        password="letsg0sk!!ng"
    )
    return conn

def try_connection():
    print("trying connection")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT,
            department VARCHAR(50)
        )
        """
        
        # Execute the query
        print("executing create table query")
        cursor.execute(create_table_query)
        
        # Commit the transaction
        conn.commit()
        
        print("Table created successfully.")

        print("deleting test table")

        cursor.execute("DROP TABLE IF EXISTS employees;")
        conn.commit()

        print("Table 'employees' has been deleted successfully.")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        return None
    
try_connection()