## file to pull from a weather API 
# will have a list of the resorts that are within the user-defined distance range and make API calls to get the recent snowfall at that location

import pandas as pd
import psycopg2
from backend_closest_stations import safe_table_name
import jsonpickle, json
import requests
from co_ski_resort_table_insertion import add_column, get_db_connection, returnResp



# Synoptic data API
# token: fda25733baec41ee90dd23653e94a1a8
# key: KuOMm49ZKk4W5zFM2YEVmGID1bIaXFgJKUmJI2tekJ

# https://api.synopticdata.com/v2/stations/metadata?token={your token}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}
# snow_depth, snow_accum, precip_storm, precip_accum_six_hour, precip_accum_six_hour, snow_accum_since_7_local, snow_accum_24_hour


API_ROOT = "https://api.synopticdata.com/v2/"
API_TOKEN = "fda25733baec41ee90dd23653e94a1a8"


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
        
        # Query the station table for this resort, ordered by distance ascending.
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

        found_valid_station = False
        # Iterate through the stations (from closest to furthest)
        for st_row in station_rows:
            station_id = st_row[0]
            print(f"  Trying station {station_id} for resort {resort}...")
            
            # Build the API URL for precip_accum_24_hour.
            # Here, recent=10000 means the most recent # of mins of data (can adjust if needed)
            url = (
                f"{API_ROOT}stations/timeseries?stid={station_id}&recent=10000"
                f"&vars=precip_accum_24_hour&token={API_TOKEN}"
            )
            headers = {'content-type': 'application/json'}
            try:
                response = requests.get(url, headers=headers, timeout=10)
            except Exception as e:
                print(f"    API call error for station {station_id} of resort {resort}: {e}")
                continue

            # Log the API response (optional)
            returnResp(response)
            try:
                data = response.json()
            except Exception as e:
                print(f"    Error parsing JSON for station {station_id}: {e}")
                continue

            # Check the response summary.
            summary = data.get("SUMMARY", {})
            if summary.get("NUMBER_OF_OBJECTS", 0) == 0 and summary.get("RESPONSE_CODE") == 2:
                print(f"    No valid data for station {station_id} (response indicates no station data).")
                continue  # Try the next station
            else:
                # Valid data returned; calculate the average precipitation
                observations = data.get('STATION', [{}])[0].get('OBSERVATIONS', {})
                precip_values = observations.get('precip_accum_24_hour_set_1', [])

                if precip_values:
                    # Filter out None values before calculating the average
                    valid_precip_values = [v for v in precip_values if v is not None]

                    if valid_precip_values:
                        # if there is more than one day's worth of data (24 hrs * 15 min intervals), only take the most recent day
                        if len(valid_precip_values) >= 96: 
                            precip = max(valid_precip_values[-96:])
                        else: # otherwise take the max of all values (shorter than a day)
                            precip = max(valid_precip_values)

                        # Upsert into the recent_snowfall table
                        upsert_query = """
                        UPDATE recent_snowfall
                        SET precip_accum_24_hour = %s
                        WHERE resort_name = %s;
                        """
                        try:
                            cursor.execute(upsert_query, (precip, resort))
                            conn.commit()
                            print(f"    Recorded precipitation data for resort '{resort}' using station '{station_id}'.")
                        except Exception as e:
                            print(f"    Error updating recent_snowfall for resort '{resort}': {e}")
                        
                        found_valid_station = True
                        break  # Exit loop for current resort since we found valid data
                    else:
                        print(f"    No valid precipitation data available for resort '{resort}' using station '{station_id}'.")
                        conn.rollback()

        
        if not found_valid_station:
            print(f"    No valid station data found for resort '{resort}'.")
            # TODO do we want to add 0.0 or None when no data is available?
            upsert_query = """
                        UPDATE recent_snowfall
                        SET precip_accum_24_hour = %s
                        WHERE resort_name = %s;
            """
            try:
                cursor.execute(upsert_query, (0.0, resort))
                conn.commit()
                print(f"    Set precip_accum_24_hour to NULL for resort '{resort}' due to lack of valid data.")
            except Exception as e:
                print(f"    Error updating recent_snowfall for resort '{resort}' with NULL data: {e}")

        #break
        
    
    cursor.close()
    conn.close()



def get_recent_snowfall_1_hr():
    """
    For each resort in colorado_resorts, iterate through the stations stored
    in its dedicated station table (ordered by distance). For each station, make
    an API call (with variable 'precip_accum_one_hour_set_1' in MM) and check the response.
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
        
        # Query the station table for this resort, ordered by distance ascending.
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

        found_valid_station = False
        # Iterate through the stations (from closest to furthest)
        for st_row in station_rows:
            station_id = st_row[0]
            print(f"  Trying station {station_id} for resort {resort}...")
            
            # Build the API URL for precip_accum_one_hour
            # Here, recent=10000 means the most recent # of mins data (can adjust if needed)
            url = (
                f"{API_ROOT}stations/timeseries?stid={station_id}&recent=1000"
                f"&vars=precip_accum_one_hour&token={API_TOKEN}"
            )
            headers = {'content-type': 'application/json'}
            try:
                response = requests.get(url, headers=headers, timeout=10)
            except Exception as e:
                print(f"    API call error for station {station_id} of resort {resort}: {e}")
                continue

            # Log the API response (optional)
            returnResp(response)
            try:
                data = response.json()
            except Exception as e:
                print(f"    Error parsing JSON for station {station_id}: {e}")
                continue

            # Check the response summary.
            summary = data.get("SUMMARY", {})
            if summary.get("NUMBER_OF_OBJECTS", 0) == 0 and summary.get("RESPONSE_CODE") == 2:
                print(f"    No valid data for station {station_id} (response indicates no station data).")
                continue  # Try the next station
            else:
                # Valid data returned; calculate the average precipitation
                observations = data.get('STATION', [{}])[0].get('OBSERVATIONS', {})
                precip_values = observations.get('precip_accum_one_hour_set_1', [])

                if precip_values:
                    # Filter out None values before calculating the average
                    valid_precip_values = [v for v in precip_values if v is not None]

                    if valid_precip_values:
                        # if there is more than one day's worth of data (24 hrs * 15 min intervals), only take the most recent day
                        precip = valid_precip_values[-1]

                        # Upsert into the recent_snowfall table
                        upsert_query = """
                        UPDATE recent_snowfall
                        SET precip_accum_1_hour = %s
                        WHERE resort_name = %s;
                        """
                        try:
                            cursor.execute(upsert_query, (precip, resort))
                            conn.commit()
                            print(f"    Recorded precipitation data for resort '{resort}' using station '{station_id}'.")
                        except Exception as e:
                            print(f"    Error updating recent_snowfall for resort '{resort}': {e}")
                        
                        found_valid_station = True
                        break  # Exit loop for current resort since we found valid data
                    else:
                        print(f"    No valid precipitation data available for resort '{resort}' using station '{station_id}'.")
                        conn.rollback()

        
        if not found_valid_station:
            print(f"    No valid station data found for resort '{resort}'.")
            upsert_query = """
                        UPDATE recent_snowfall
                        SET precip_accum_1_hour = %s
                        WHERE resort_name = %s;
            """
            try:
                cursor.execute(upsert_query, (0.0, resort))
                conn.commit()
                print(f"    Set precip_accum_1_hour to NULL for resort '{resort}' due to lack of valid data.")
            except Exception as e:
                print(f"    Error updating recent_snowfall for resort '{resort}' with NULL data: {e}")

        #break
        
    
    cursor.close()
    conn.close()


# https://api.synopticdata.com/v2/stations/timeseries?stid=wbb&recent=10080&vars=air_temp,dew_point_temperature,heat_index&token=[YOUR_TOKEN]
# recent=(number of minutes to look for recent)


# add_column("recent_snowfall", "precipitation_since_local_midnight", "NUMERIC")

if __name__ == "__main__":
    #get_recent_snowfall_24_hr()
    get_recent_snowfall_1_hr()
    # add_column("recent_snowfall", "precip_accum_1_hour", "NUMERIC")



