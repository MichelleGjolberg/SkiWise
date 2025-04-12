import pandas as pd
import psycopg2
import jsonpickle, json
import requests
import os


SYNOPTIC_API_ROOT = "https://api.synopticdata.com/v2/"

SYNOPTIC_API_TOKEN = os.environ.get("SYNOPTIC_API_TOKEN")
GMAPS_API_KEY = os.environ.get("GMAPS_API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")




def returnResp(response):
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print("response status code = 200")
        print(jsonResponse)
        return
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
        return response.text

# doesn't work on UCB Guest wifi? 
def get_db_connection():
    print("Getting db connection...")
    conn = psycopg2.connect(
        host="34.46.13.43",
        database="postgres",
        user="postgres",
        password=DB_PASSWORD
    )
    print("Successfully connected to server")
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
        print("Executing create table query")
        cursor.execute(create_table_query)
        
        # Commit the transaction
        conn.commit()
        
        print("Table created successfully.")

        print("Deleting test table")

        cursor.execute("DROP TABLE IF EXISTS employees;")
        conn.commit()

        print("Test table has been deleted successfully.")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        return None
    

def import_csv_to_db(csv_path: str, table_name: str = "ski_resort_stats"):
    # read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)
    print(f"CSV file loaded with {len(df)} rows.")
    return df


def filter_co_resorts(df):
    # filter to only include CO resorts
    # Clean up the 'state' column in case of extra whitespace
    df['state'] = df['state'].str.strip()

    # Filter for resorts in Colorado
    colorado_df = df[df['state'] == "Colorado"]
    print(f"Filtered data: {len(colorado_df)} rows for Colorado resorts.")
    return colorado_df


def insert_colorado_df_to_db(df, table_name='colorado_resorts'):
    # checks if table exists, creates table if it doesn't, then adds rows of df to db
    print("Checking if table exists...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the table exists in the 'public' schema.
        check_table_query = """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = %s
            );
        """
        cursor.execute(check_table_query, (table_name,))
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print(f"Table '{table_name}' already exists. No data will be inserted.")
        else:
            print(f"Table '{table_name}' does not exist. Creating table and inserting data...")

            create_table_query = f"""
            CREATE TABLE {table_name} (
                resort_name VARCHAR(255),
                state VARCHAR(50),
                summit INT,
                base INT,
                vertical INT,
                lifts INT,
                runs INT,
                acres NUMERIC,
                green_percent NUMERIC,
                green_acres NUMERIC,
                blue_percent NUMERIC,
                blue_acres NUMERIC,
                black_percent NUMERIC,
                black_acres NUMERIC,
                lat NUMERIC,
                lon NUMERIC
            );
            """
            cursor.execute(create_table_query)
            conn.commit()
            print(f"Table '{table_name}' created.")

            insert_query = f"""
            INSERT INTO {table_name} (
                resort_name, state, summit, base, vertical, lifts, runs, acres, 
                green_percent, green_acres, blue_percent, blue_acres, 
                black_percent, black_acres, lat, lon
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
            """

            rows = []
            for _, row in df.iterrows():
                new_row = (
                    row['resort_name'],
                    row['state'],
                    int(row['summit']) if pd.notnull(row['summit']) else None,
                    int(row['base']) if pd.notnull(row['base']) else None,
                    int(row['vertical']) if pd.notnull(row['vertical']) else None,
                    int(row['lifts']) if pd.notnull(row['lifts']) else None,
                    int(row['runs']) if pd.notnull(row['runs']) else None,
                    float(row['acres']) if pd.notnull(row['acres']) else None,
                    float(row['green_percent']) if pd.notnull(row['green_percent']) else None,
                    float(row['green_acres']) if pd.notnull(row['green_acres']) else None,
                    float(row['blue_percent']) if pd.notnull(row['blue_percent']) else None,
                    float(row['blue_acres']) if pd.notnull(row['blue_acres']) else None,
                    float(row['black_percent']) if pd.notnull(row['black_percent']) else None,
                    float(row['black_acres']) if pd.notnull(row['black_acres']) else None,
                    float(row['lat']) if pd.notnull(row['lat']) else None,
                    float(row['lon']) if pd.notnull(row['lon']) else None
                )
                rows.append(new_row)

            cursor.executemany(insert_query, rows)
            conn.commit()
            print("Data inserted successfully.")

    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_all_co_resorts():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT * FROM "colorado_resorts"
    """
    # cursor.execute(query)
    # resorts = cursor.fetchall()
    # print(len(resorts)) # 24 colorado resorts
    # print(resorts[0])

    df = pd.read_sql(query, conn)
    #print(df)
    return df


# function to add a column to the specified table if it does not already exist
def add_column(table_name, column_name, column_definition):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Construct the ALTER TABLE query. Note: Column names cannot be parameterized,
        # so ensure the input is trusted or properly sanitized.
        query = f"""
        ALTER TABLE {table_name}
        ADD COLUMN IF NOT EXISTS {column_name} {column_definition};
        """
        cursor.execute(query)
        conn.commit()
        print(f"Column '{column_name}' added to table '{table_name}' (or already exists).")
    except Exception as e:
        print(f"Error adding column '{column_name}' to table '{table_name}': {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def returnResp(response):
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print("response status code = 200")
        print(jsonResponse)
    else:
        print(f"response code is {response.status_code}, raw response is {response.text}")
    return


if __name__ == "__main__":
    try_connection()

    df = import_csv_to_db('ski_resort_stats.csv')
    colorado_df = filter_co_resorts(df)
    # print(colorado_df)

    insert_colorado_df_to_db(colorado_df)

    colorado_resorts = get_all_co_resorts()
