## file to pull from a weather API 
# will have a list of the resorts that are within the user-defined distance range and make API calls to get the recent snowfall at that location

import pandas as pd
import psycopg2
from backend_closest_stations import safe_table_name
import jsonpickle, json
import requests
from co_ski_resort_table_insertion import get_db_connection, add_column, returnResp, get_all_co_resorts



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



# make calls to synoptic API based on closest weather station to get recent 24 hr snowfall
# https://api.synopticdata.com/v2/stations/timeseries?stid=wbb&recent=10080&vars=air_temp,dew_point_temperature,heat_index&token=[YOUR_TOKEN]
# def get_recent_snowfall():
#     """
#     Query the colorado_resorts table, iterate over each row to extract closest weather station, then 
#     make an API call to get the recent 24 hr snowfall
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # call add_column for closest_station and closest_station_id
#     add_column("recent_snowfall", "precip_accum_24_hour", "NUMERIC") 
#     add_column("recent_snowfall", "precipitation_since_local_midnight", "NUMERIC") 


#     query = 'SELECT resort_name, lat, lon, closest_station, closest_station_id FROM "colorado_resorts";'
#     cursor.execute(query)
    
#     rows = cursor.fetchall()
#     for row in rows:
#         resort = row[0]
#         latitude = row[1]
#         longitude = row[2]
#         closest_station = row[3]
#         closest_station_id = row[4]
#         print(f"{resort}: Closest station = {closest_station}, Closest station id = {closest_station_id}")
        
#         # https://api.synopticdata.com/v2/stations/timeseries?stid=wbb&recent=10080&vars=air_temp,dew_point_temperature,heat_index&token=[YOUR_TOKEN]
#         # make a call to synoptic API to get closest weather station report of 24 hr snowfall
#         # TODO 
#         url = (
#             f"{API_ROOT}stations/timeseries?stid={closest_station_id}&recent=1&vars=snow_accum_24_hour&token={API_TOKEN}"
#         ) # TODO - what to put for recent=# ?
#         headers = {'content-type': 'application/json'}
#         response = requests.get(url, headers=headers)
#         returnResp(response) # TODO - make sure the station is reporting ?

#         data = response.json()
#         print(data)


#         # check if 'STATION' exists and has at least one entry TODO
#         if "STATION" in data and len(data["STATION"]) > 0:
#             station_name = data["STATION"][0].get("NAME")
#             print("Station name:", station_name)
#             station_id = data["STATION"][0].get("STID")
#             print("Station id:", station_id)
#             snowfall_24_hr = 0;
#             print("24 hour snowfall: ", "TODO")


#             # update the corresponding row in the database with the 24 hr snowfall
#             update_query = """
#                 UPDATE colorado_resorts
#                 SET snowfall_24_hr = %s
#                 WHERE resort_name = %s AND closest_station = %s;
#             """ # TODO also match on closest_station
#             cursor.execute(update_query, (snowfall_24_hr, resort, closest_station)) # TODO is %s just for string ?
#             conn.commit()
#             print("Added 24 hr snowfall to database for {resort} from {closest_station}.")
#         else:
#             print("No station weather data available.")
        

#     cursor.close()
#     conn.close()

def get_recent_snowfall():
    """
    For each resort in colorado_resorts, iterate through the stations stored
    in its dedicated station table (ordered by distance). For each station, make
    an API call (with variable 'precip_accum_24_hour') and check the response.
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
            # Here, recent=1 means the most recent data (you can adjust if needed).
            url = (
                f"{API_ROOT}stations/timeseries?stid={station_id}&recent=1"
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
                # Valid data returned; convert the whole JSON to a string.
                precip_json = json.dumps(data)
                
                # Upsert into the recent_snowfall table.
                upsert_query = """
                INSERT INTO recent_snowfall (resort_name, precip_accum_24_hour)
                VALUES (%s, %s)
                ON CONFLICT (resort_name)
                DO UPDATE SET precip_accum_24_hour = EXCLUDED.precip_accum_24_hour;
                """
                try:
                    cursor.execute(upsert_query, (resort, precip_json))
                    conn.commit()
                    print(f"    Recorded precipitation data for resort '{resort}' using station '{station_id}'.")
                except Exception as e:
                    print(f"    Error updating recent_snowfall for resort '{resort}': {e}")
                found_valid_station = True
                break  # Exit loop for current resort since we found valid data
        
        if not found_valid_station:
            print(f"    No valid station data found for resort '{resort}'.")
        
    
    cursor.close()
    conn.close()



# main
# add_column("recent_snowfall", "precipitation_since_local_midnight", "NUMERIC")

get_recent_snowfall()


