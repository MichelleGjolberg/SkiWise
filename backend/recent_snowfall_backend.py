## file to pull from a weather API 
# will have a list of the resorts that are within the user-defined distance range and make API calls to get the recent snowfall at that location

import pandas as pd
import psycopg2
from backend_closest_stations import safe_table_name
import jsonpickle, json
import requests
from co_ski_resort_table_insertion import add_column, get_db_connection, returnResp
import os




# https://api.synopticdata.com/v2/stations/metadata?token={your token}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}
# snow_depth, snow_accum, precip_storm, precip_accum_six_hour, precip_accum_six_hour, snow_accum_since_7_local, snow_accum_24_hour


SYNOPTIC_API_ROOT = "https://api.synopticdata.com/v2/"

SYNOPTIC_API_TOKEN = os.environ.get("SYNOPTIC_API_TOKEN")
GMAPS_API_KEY = os.environ.get("GMAPS_API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")



# take latitude and longitude for each resort, make call to synoptic API to get closest weather station report of snowfall
# def get_recent_snowfall(df):
#     for index, row in df.iterrows():
#         # for each resort, get latitude and longitude
#         resort = row['resort_name']
#         latitude = row['lat']
#         longitude = row['lon']
#         print(f"{resort}: Latitude = {latitude}, Longitude = {longitude}")

#         # make a call to synoptic API to get closest weather station report of snowfall
#         # https://api.synopticdata.com/v2/stations/metadata?token={your token}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}
        
#     return 


def get_recent_snowfall_24_hr():
    """
    For each resort in colorado_resorts, iterate through the stations stored
    in its dedicated station table (ordered by distance). For each station, make
    an API call (with variable 'precip_accum_24_hour' in MM) and check the response.
    If the response does not indicate "no data" (i.e. NUMBER_OF_OBJECTS is 0 and RESPONSE_CODE is 2),
    then record the JSON result in the recent_snowfall table and break out of the station loop.
    Otherwise, proceed to the next closest station.
    """
    
    # Connect to the database to query the resorts.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all resort names from the colorado_resorts table.
    query = 'SELECT resort_name FROM "colorado_resorts";'
    cursor.execute(query)
    resorts = cursor.fetchall()  # Each row is a tuple like (resort_name,)
    
    for res_row in resorts:
        
        resort = res_row[0]
        print(f"\nProcessing resort: {resort}")
        
        # Generate a safe table name for the stations of this resort.
        station_table = safe_table_name(resort)
        
        # Get station from valid_stations first
        get_valid_station_query = """
            SELECT station_id FROM valid_stations_24hr WHERE resort_name = %s;
        """
        cursor.execute(get_valid_station_query, (resort,))
        valid_station_row = cursor.fetchone()
        valid_station_id = valid_station_row[0] if valid_station_row else None

        stations_to_try = []

        # Add preferred valid station if it exists
        if valid_station_id:
            print(f"  Trying preferred valid station {valid_station_id} for resort {resort}...")
            stations_to_try.append(valid_station_id)


        # Query the remaining stations for this resort, ordered by distance ascending.
        try:
            conn_st = get_db_connection()
            cur_st = conn_st.cursor()
            station_query = f"SELECT station_id FROM {station_table} ORDER BY distance ASC;"
            cur_st.execute(station_query)
            station_rows = cur_st.fetchall()
            cur_st.close()
            conn_st.close()
        except Exception as e:
            print(f"Error querying station table '{station_table}' for resort '{resort}': {e}")
            continue

        # Add remaining stations (excluding the one already tried if it exists)
        all_station_ids = [row[0] for row in station_rows]
        if valid_station_id in all_station_ids:
            all_station_ids.remove(valid_station_id)
        stations_to_try.extend(all_station_ids)

        found_valid_station = False
        # Try each station in the prioritized list
        for station_id in stations_to_try:
            print(f"  Trying station {station_id} for resort {resort}...")

            url = (
                f"{SYNOPTIC_API_ROOT}stations/timeseries?stid={station_id}&recent=10000"
                f"&vars=precip_accum_24_hour&token={SYNOPTIC_API_TOKEN}"
            )
            print(f"url: {url}")
            headers = {'content-type': 'application/json'}

            try:
                response = requests.get(url, headers=headers, timeout=10)
            except Exception as e:
                print(f"    API call error for station {station_id} of resort {resort}: {e}")
                continue

            returnResp(response)

            try:
                data = response.json()
            except Exception as e:
                print(f"    Error parsing JSON for station {station_id}: {e}")
                continue

            summary = data.get("SUMMARY", {})
            if summary.get("NUMBER_OF_OBJECTS", 0) == 0 and summary.get("RESPONSE_CODE") == 2:
                print(f"    No valid data for station {station_id} (response indicates no station data).")
                continue  # Try next station

            observations = data.get('STATION', [{}])[0].get('OBSERVATIONS', {})
            precip_values = observations.get('precip_accum_24_hour_set_1', [])

            if precip_values:
                valid_precip_values = [v for v in precip_values if v is not None]

                if valid_precip_values:
                    precip = max(valid_precip_values[-96:]) if len(valid_precip_values) >= 96 else max(valid_precip_values)

                    try:
                        # Update recent_snowfall table
                        cursor.execute("""
                            UPDATE recent_snowfall
                            SET precip_accum_24_hour = %s
                            WHERE resort_name = %s;
                        """, (precip, resort))

                        # Update colorado_resorts table
                        cursor.execute("""
                            UPDATE colorado_resorts
                            SET precip_accum_24_hour = %s
                            WHERE resort_name = %s;
                        """, (precip, resort))

                        # Update valid_stations_24hr table
                        cursor.execute("""
                            UPDATE valid_stations_24hr
                            SET station_id = %s
                            WHERE resort_name = %s;
                        """, (station_id, resort))

                        conn.commit()
                        print(f"    Successfully recorded 24 hr snowfall of {precip} and updated station for resort '{resort}' using station '{station_id}'.")
                        found_valid_station = True
                        break

                    except Exception as e:
                        print(f"    Error during DB update for resort '{resort}': {e}")
                        conn.rollback()
                else:
                    print(f"    No valid precipitation values at station '{station_id}'")
            else:
                print(f"    No precipitation data at all for station '{station_id}'")

        if not found_valid_station:
            print(f"    No valid station data found for resort '{resort}'.")
            try:
                cursor.execute("""
                    UPDATE recent_snowfall
                    SET precip_accum_24_hour = %s
                    WHERE resort_name = %s;
                """, (0.0, resort))
                conn.commit()
                print(f"    Set precip_accum_24_hour to 0.0 for resort '{resort}' due to lack of valid data.")
            except Exception as e:
                print(f"    Error updating recent_snowfall for resort '{resort}' with 0.0 data: {e}")

    cursor.close()
    conn.close()


def get_recent_snowfall_1_hr():
    """
    For each resort in colorado_resorts, try the station stored in valid_stations_1hr first.
    If it fails, iterate through the stations stored in its dedicated station table (ordered by distance).
    For each station, make an API call for 'precip_accum_one_hour' in MM.
    If valid, update the recent_snowfall and colorado_resorts tables and break.
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'SELECT resort_name FROM "colorado_resorts";'
    cursor.execute(query)
    resorts = cursor.fetchall()

    for res_row in resorts:
        resort = res_row[0]
        print(f"\nProcessing resort: {resort}")
        station_table = safe_table_name(resort)

        # Get station from valid_stations_1hr first
        get_valid_station_query = """
            SELECT station_id FROM valid_stations_1hr WHERE resort_name = %s;
        """
        cursor.execute(get_valid_station_query, (resort,))
        valid_station_row = cursor.fetchone()
        valid_station_id = valid_station_row[0] if valid_station_row else None

        stations_to_try = []

        if valid_station_id:
            print(f"  Trying preferred valid station {valid_station_id} for resort {resort}...")
            stations_to_try.append(valid_station_id)

        try:
            conn_st = get_db_connection()
            cur_st = conn_st.cursor()
            station_query = f"SELECT station_id FROM {station_table} ORDER BY distance ASC;"
            cur_st.execute(station_query)
            station_rows = cur_st.fetchall()
            cur_st.close()
            conn_st.close()
        except Exception as e:
            print(f"Error querying station table '{station_table}' for resort '{resort}': {e}")
            continue

        all_station_ids = [row[0] for row in station_rows]
        if valid_station_id in all_station_ids:
            all_station_ids.remove(valid_station_id)
        stations_to_try.extend(all_station_ids)

        found_valid_station = False
        for station_id in stations_to_try:
            print(f"  Trying station {station_id} for resort {resort}...")

            url = (
                f"{SYNOPTIC_API_ROOT}stations/timeseries?stid={station_id}&recent=1000"
                f"&vars=precip_accum_one_hour&token={SYNOPTIC_API_TOKEN}"
            )
            headers = {'content-type': 'application/json'}
            print(f"url: {url}")

            try:
                response = requests.get(url, headers=headers, timeout=10)
            except Exception as e:
                print(f"    API call error for station {station_id} of resort {resort}: {e}")
                continue

            returnResp(response)

            try:
                data = response.json()
            except Exception as e:
                print(f"    Error parsing JSON for station {station_id}: {e}")
                continue

            summary = data.get("SUMMARY", {})
            if summary.get("NUMBER_OF_OBJECTS", 0) == 0 and summary.get("RESPONSE_CODE") == 2:
                print(f"    No valid data for station {station_id} (response indicates no station data).")
                continue

            observations = data.get('STATION', [{}])[0].get('OBSERVATIONS', {})
            precip_values = observations.get('precip_accum_one_hour_set_1', [])

            if precip_values:
                valid_precip_values = [v for v in precip_values if v is not None]

                if valid_precip_values:
                    precip = valid_precip_values[-1]

                    try:
                        # Update recent_snowfall table
                        cursor.execute("""
                            UPDATE recent_snowfall
                            SET precip_accum_1_hour = %s
                            WHERE resort_name = %s;
                        """, (precip, resort))

                        # Update colorado_resorts table
                        cursor.execute("""
                            UPDATE colorado_resorts
                            SET precip_accum_1_hour = %s
                            WHERE resort_name = %s;
                        """, (precip, resort))

                        # Update valid_stations_1hr table
                        cursor.execute("""
                            UPDATE valid_stations_1hr
                            SET station_id = %s
                            WHERE resort_name = %s;
                        """, (station_id, resort))

                        conn.commit()
                        print(f"    Successfully recorded 1 hr snowfall and updated station for resort '{resort}' using station '{station_id}'.")
                        found_valid_station = True
                        break

                    except Exception as e:
                        print(f"    Error during DB update for resort '{resort}': {e}")
                        conn.rollback()
                else:
                    print(f"    No valid precipitation values at station '{station_id}'")
            else:
                print(f"    No precipitation data at all for station '{station_id}'")

        if not found_valid_station:
            print(f"    No valid station data found for resort '{resort}'.")
            try:
                cursor.execute("""
                    UPDATE recent_snowfall
                    SET precip_accum_1_hour = %s
                    WHERE resort_name = %s;
                """, (0.0, resort))
                conn.commit()
                print(f"    Set precip_accum_1_hour to 0.0 for resort '{resort}' due to lack of valid data.")
            except Exception as e:
                print(f"    Error updating recent_snowfall for resort '{resort}' with 0.0 data: {e}")

    cursor.close()
    conn.close()


# https://api.synopticdata.com/v2/stations/timeseries?stid=wbb&recent=10080&vars=air_temp,dew_point_temperature,heat_index&token=[YOUR_TOKEN]
# recent=(number of minutes to look for recent)


# add_column("recent_snowfall", "precipitation_since_local_midnight", "NUMERIC")

if __name__ == "__main__":
    get_recent_snowfall_24_hr()
    get_recent_snowfall_1_hr()



