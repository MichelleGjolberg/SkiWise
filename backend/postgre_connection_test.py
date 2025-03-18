import psycopg2
from psycopg2.extras import RealDictCursor

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