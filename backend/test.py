import psycopg2
from psycopg2.extras import RealDictCursor
import os


SYNOPTIC_API_ROOT = "https://api.synopticdata.com/v2/"

SYNOPTIC_API_TOKEN = os.environ.get("SYNOPTIC_API_TOKEN")
GMAPS_API_KEY = os.environ.get("GMAPS_API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


def get_db_connection():
    conn = psycopg2.connect(
        host="34.46.13.43",
        database="postgres",
        user="postgres",
        password=DB_PASSWORD
    )
    return conn

def try_connection():
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
        cursor.execute(create_table_query)
        
        # Commit the transaction
        conn.commit()
        
        print("Table created successfully.")
        # Close the cursor and connection
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        return None
    
try_connection()