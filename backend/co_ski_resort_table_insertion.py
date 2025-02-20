import pandas as pd
import psycopg2
import jsonpickle, json
import requests

# Synoptic data API
# key: KuOMm49ZKk4W5zFM2YEVmGID1bIaXFgJKUmJI2tekJ
# token: fda25733baec41ee90dd23653e94a1a8

API_ROOT = "https://api.synopticdata.com/v2/"
API_TOKEN = "fda25733baec41ee90dd23653e94a1a8"

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
        password="letsg0sk!!ng"
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


# make calls to synoptic API to determine closest weather station to each resort (via lat/long) and append to table
# https://api.synopticdata.com/v2/stations/metadata?token={your token}&radius=33.704,-112.014,10&limit=10
def get_closest_station():
    """
    Query the colorado_resorts table, iterate over each row to extract latitude and longitude,
    and make an API call to get the closest weather station data
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # call add_column for closest_station and closest_station_id
    add_column("colorado_resorts", "closest_station", "VARCHAR(255)")
    add_column("colorado_resorts", "closest_station_id", "VARCHAR(50)")

    query = 'SELECT resort_name, lat, lon FROM "colorado_resorts";'
    cursor.execute(query)
    
    rows = cursor.fetchall()
    for row in rows:
        resort = row[0]
        latitude = row[1]
        longitude = row[2]
        print(f"{resort}: Latitude = {latitude}, Longitude = {longitude}")
        
        # make a call to synoptic API to get closest weather station report of snowfall
        radius_miles = 10
        limit_count = 1  #  # TODO - can update to get more closest stations to get more data and take average
        url = (
            f"{API_ROOT}stations/metadata?"
            f"token={API_TOKEN}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}"
        )
        headers = {'content-type': 'application/json'}
        response = requests.get(url, headers=headers)
        returnResp(response) # TODO - make sure the station is active

        data = response.json()

        # check if 'STATION' exists and has at least one entry
        if "STATION" in data and len(data["STATION"]) > 0:
            station_name = data["STATION"][0].get("NAME")
            print("Station name:", station_name)
            station_id = data["STATION"][0].get("STID")
            print("Station id:", station_id)

            # Update the corresponding row in the database with the station info.
            update_query = """
                UPDATE colorado_resorts
                SET closest_station = %s,
                    closest_station_id = %s
                WHERE resort_name = %s;
            """
            cursor.execute(update_query, (station_name, station_id, resort))
            conn.commit()
            print("Added station name and id to database.")
        else:
            print("No station data available.")
        

    cursor.close()
    conn.close()

# make calls to synoptic API with the station for each resort to get recent snowfall TODO - expand to be able to get more data/fields
# https://api.synopticdata.com/v2/stations/metadata?token={your token}&radius=33.704,-112.014,10&limit=10
def get_station_data():
    # TODO - call API here to get data or do when getting the closest stations?
    pass




# main
try_connection()

df = import_csv_to_db('ski_resort_stats.csv')
colorado_df = filter_co_resorts(df)
# print(colorado_df)

insert_colorado_df_to_db(colorado_df)

colorado_resorts = get_all_co_resorts()
get_closest_station()
