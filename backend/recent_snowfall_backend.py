## file to pull from a weather API 
# will have a list of the resorts that are within the user-defined distance range and make API calls to get the recent snowfall at that location

import pandas as pd
import psycopg2


# Synoptic data API
# token: fda25733baec41ee90dd23653e94a1a8
# key: KuOMm49ZKk4W5zFM2YEVmGID1bIaXFgJKUmJI2tekJ

# snow_depth, snow_accum, precip_storm, precip_accum_six_hour, precip_accum_six_hour, snow_accum_since_7_local, snow_accum_24_hour


API_ROOT = "https://api.synopticdata.com/v2/"
API_TOKEN = "fda25733baec41ee90dd23653e94a1a8"

# https://api.synopticdata.com/v2/stations/metadata?token={your token}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}


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

# conn = get_db_connection()
# cursor = conn.cursor()


def get_all_co_resorts():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT * FROM "colorado_resorts"
    """
    cursor.execute(query)
    # resorts = cursor.fetchall()
    # print(len(resorts)) # 24 colorado resorts
    # print(resorts[0])

    df = pd.read_sql(query, conn)
    print(df)
    return df

# take latitude and longitude for each resort, make call to synoptic API to get closest weather station report of snowfall

def get_recent_snowfall(df):
    for index, row in df.iterrows():
        # for each resort, get latitude and longitude
        resort = row['resort_name']
        latitude = row['lat']
        longitude = row['lon']
        print(f"{resort}: Latitude = {latitude}, Longitude = {longitude}")

        # make a call to synoptic API to get closest weather station report of snowfall
        # https://api.synopticdata.com/v2/stations/metadata?token={your token}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}
        


    return 




colorado_resorts = get_all_co_resorts()
get_recent_snowfall(colorado_resorts)