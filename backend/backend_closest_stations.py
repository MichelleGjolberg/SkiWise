import re
import pandas as pd
import psycopg2
from co_ski_resort_table_insertion import try_connection, get_db_connection, add_column, returnResp
import jsonpickle, json
import requests
import os


SYNOPTIC_API_ROOT = "https://api.synopticdata.com/v2/"

SYNOPTIC_API_TOKEN = os.environ.get("SYNOPTIC_API_TOKEN")
GMAPS_API_KEY = os.environ.get("GMAPS_API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


def safe_table_name(resort_name):
    """
    Create a safe table name by replacing non-alphanumeric characters with underscores.
    Prefix the name with 'stations_'.
    """
    safe_name = re.sub(r'\W+', '_', resort_name)
    return f"stations_{safe_name.lower()}"


def create_resort_station_table(table_name):
    """
    Create a table for storing station data for a resort.
    Columns include station_id, station_name, distance, elevation, latitude, and longitude.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            station_id VARCHAR(50),
            station_name VARCHAR(255),
            distance NUMERIC,
            elevation NUMERIC,
            latitude NUMERIC,
            longitude NUMERIC
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print(f"Table '{table_name}' created (or already exists).")
    except Exception as e:
        print(f"Error creating table '{table_name}': {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_station_data(table_name, stations):
    """
    Inserts a list of station dictionaries into the specified table.
    Expected keys: 'ID' or 'STID' for station identifier, 'NAME', 'DISTANCE', 'ELEVATION', 'LATITUDE', 'LONGITUDE'
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = f"""
        INSERT INTO {table_name} (
            station_id, station_name, distance, elevation, latitude, longitude
        ) VALUES (
            %s, %s, %s, %s, %s, %s
        );
        """
        rows = []
        for station in stations:
            # Prefer STID as station_id; if not available, fallback to ID.
            station_id = station.get("STID") or station.get("ID")
            station_name = station.get("NAME")
            distance = station.get("DISTANCE")
            elevation = station.get("ELEVATION")
            latitude = station.get("LATITUDE")
            longitude = station.get("LONGITUDE")
            rows.append((station_id, station_name, distance, elevation, latitude, longitude))
        cursor.executemany(insert_query, rows)
        conn.commit()
        print(f"Inserted {len(rows)} station records into table '{table_name}'.")
    except Exception as e:
        print(f"Error inserting station data into '{table_name}': {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_closest_stations_for_all_resorts():
    """
    For each Colorado resort in the database, call the Synoptic API with a 20-mile radius and limit of 50.
    Then create a dedicated table for the resort to store its closest 50 stations.
    """
    # Get all resorts from the colorado_resorts table.
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT resort_name, lat, lon FROM "colorado_resorts";'
    cursor.execute(query)
    resorts = cursor.fetchall()
    cursor.close()
    conn.close()

    for resort, latitude, longitude in resorts:
        print(f"Processing resort: {resort} (Lat: {latitude}, Lon: {longitude})")
        radius_miles = 20
        limit_count = 50
        url = (
            f"{SYNOPTIC_API_ROOT}stations/metadata?"
            f"token={SYNOPTIC_API_TOKEN}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}"
        )
        headers = {'content-type': 'application/json'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except Exception as e:
            print(f"API call error for resort {resort}: {e}")
            continue

        returnResp(response) 
        data = response.json()
        if "STATION" in data and len(data["STATION"]) > 0:
            stations = data["STATION"]
            print(f"Found {len(stations)} stations for {resort}")
            table_name = safe_table_name(resort)
            create_resort_station_table(table_name)
            insert_station_data(table_name, stations)
            print(f"Inserted station data for {resort} into table '{table_name}'.\n")
        else:
            print(f"No station data available for resort {resort}")



# make calls to synoptic API to determine closest weather station to each resort (via lat/long) and append to table
# https://api.synopticdata.com/v2/stations/metadata?token={your token}&radius=33.704,-112.014,10&limit=10
# def get_closest_station():
#     """
#     Query the colorado_resorts table, iterate over each row to extract latitude and longitude,
#     and make an API call to get the closest weather station data
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # call add_column for closest_station and closest_station_id
#     add_column("colorado_resorts", "closest_station", "VARCHAR(255)")
#     add_column("colorado_resorts", "closest_station_id", "VARCHAR(50)")

#     query = 'SELECT resort_name, lat, lon FROM "colorado_resorts";'
#     cursor.execute(query)
    
#     rows = cursor.fetchall()
#     for row in rows:
#         resort = row[0]
#         latitude = row[1]
#         longitude = row[2]
#         print(f"{resort}: Latitude = {latitude}, Longitude = {longitude}")
        
#         # make a call to synoptic API to get closest weather station
#         radius_miles = 10
#         limit_count = 1  #  # TODO - can update to get more closest stations to get more data and take average
#         url = (
#             f"{API_ROOT}stations/metadata?"
#             f"token={API_TOKEN}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}"
#         )
#         headers = {'content-type': 'application/json'}
#         response = requests.get(url, headers=headers)
#         returnResp(response) # TODO - make sure the station is active

#         data = response.json()

#         # check if 'STATION' exists and has at least one entry
#         if "STATION" in data and len(data["STATION"]) > 0:
#             station_name = data["STATION"][0].get("NAME")
#             print("Station name:", station_name)
#             station_id = data["STATION"][0].get("STID")
#             print("Station id:", station_id)

#             # Update the corresponding row in the database with the station info.
#             update_query = """
#                 UPDATE colorado_resorts
#                 SET closest_station = %s,
#                     closest_station_id = %s
#                 WHERE resort_name = %s;
#             """
#             cursor.execute(update_query, (station_name, station_id, resort))
#             conn.commit()
#             print("Added station name and id to database.")
#         else:
#             print("No station data available.")
        

#     cursor.close()
#     conn.close()


if __name__ == "__main__":
    try_connection()  
    get_closest_stations_for_all_resorts()

