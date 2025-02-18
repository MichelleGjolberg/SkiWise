import pandas as pd
import psycopg2



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
    return df


def insert_colorado_df_to_db(df, table_name='colorado_resorts'):
    """
    Inserts the provided DataFrame (filtered for Colorado resorts) into the specified PostgreSQL table.
    Converts numeric columns to native Python types to avoid type issues.
    """
    print("Inserting Colorado resorts into database table...")
    try:
        # Establish a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create the table if it doesn't exist. Adjust column types as needed.
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
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
        print(f"Table '{table_name}' created or already exists.")

        # Prepare the insert query
        insert_query = f"""
        INSERT INTO {table_name} (
            resort_name, state, summit, base, vertical, lifts, runs, acres, 
            green_percent, green_acres, blue_percent, blue_acres, 
            black_percent, black_acres, lat, lon
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """

        # Build a list of tuples with proper type conversion
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

        # Insert all rows using executemany for efficiency
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


# main
try_connection()

df = import_csv_to_db('ski_resort_stats.csv')
colorado_df = filter_co_resorts(df)

insert_colorado_df_to_db(colorado_df)
