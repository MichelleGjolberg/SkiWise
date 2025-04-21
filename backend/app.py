from flask import Flask, request, jsonify
import psycopg2
import requests
import json
from flask_cors import CORS
from get_traffic import calculate_route, get_incidents
from decimal import Decimal
from formulations import optimize_ski_resorts
from dotenv import load_dotenv
import os
import math
from datetime import datetime, timedelta
import subprocess

load_dotenv()  # Load variables from .env

SYNOPTIC_API_ROOT = "https://api.synopticdata.com/v2/"

SYNOPTIC_API_TOKEN = os.getenv("SYNOPTIC_API_TOKEN")
GMAPS_API_KEY = os.getenv("GMAPS_API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")


last_snowfall_update = None  # Global variable to track last update time
UPDATE_INTERVAL = timedelta(hours=1)  # How often to refresh snowfall data

# ==========================
# User Inputs & from API ----------------------> Get from backend
# ==========================

# Hardcoded Data for 10 Resorts -----------------> Get from backend
num_people = 4
max_budget = 100
max_time = 5
min_snowfall = 1
cost_importance, time_importance = -5, -5 
snowfall_importance = 5 # TODO add frontend slider to snowfall_importance and capture variable in backend

# get from results of traffic API call
miles =          []
accidents =      []
current_time =   [3600, 1800, 5400, 4320, 2880, 7200, 3960, 4680, 2520, 3480, 3600, 1800, 5400, 4320, 2880, 7200, 3960, 4680, 2520, 3480, 1111, 2222, 3333, 4444]  # In seconds


# snowfall_start = [1, 2, 2, 6, 4, 3, 2, 5, 1, 2, 1, 2, 2, 6, 4, 3, 2, 5, 1, 2, 1, 2, 3, 4] # TODO call weather API to get recent snowfall (1 hr?) at start location
snowfall_end =   [12, 7, 14, 8, 6, 18, 9, 11, 4, 10, 12, 7, 14, 8, 6, 18, 9, 11, 4, 10, 11, 12, 13, 14] # TODO call weather API to get recent snowfall (1 hr?) at end locations = resorts (already in db)

# Hardcoded Parameters
DRIVING_EXPERIENCE_FACTOR = 0.1  # Intermediate level
FUEL_COST = 3                 # Dollars per mile
MAINTENANCE_FACTOR = 0.10     # 10%
SNOWFALL_TIME_FACTOR = 0.5   # Random weight added per inch of snowfall
NORM_MIN = 1 # Normalization range
NORM_MAX = 5

# Attributes for each resort: miles (both-ways), accidents, snowfall_start, snowfall_end, current_time (seconds)
resorts_to_optimize = []

# list of all resorts and data
all_resorts = []

app = Flask(__name__)

# Enable CORS for all routes or specific origins
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})


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

def get_resort_coordinates(resort_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT lon, lat FROM colorado_resorts WHERE resort_name = %s;"

    # Execute query with parameterized input to prevent SQL injection
    cursor.execute(query, (resort_name,))
    result = cursor.fetchone()

    if not result:
        print("Resort not found.")
    
    return result

def get_start_coordinates(address):
    address=address.replace(" ", "+")
    get_coordinates_url=f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GMAPS_API_KEY}"

    try:
        response = requests.request("GET", get_coordinates_url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        response=response.json()

        coordinates=response["results"][0]["geometry"]["location"]
        return f"{coordinates['lat']},{coordinates['lng']}"
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return
    

    
@app.route("/get_mountain", methods=["POST"])
def get_mountain():
    data = request.get_json()
    print("Input received:")

    #maybe_update_snowfall_data() # check if snowfall data has been updated within the past hour

    # clear the top_3 table
    conn = get_db_connection()
    cursor = conn.cursor()


    # Clear the given table
    clear_table_query = f"DELETE FROM top_3_resorts;"
    cursor.execute(clear_table_query)
    print(f"Cleared existing resorts in top_3_resorts.")


    # Clear the given table
    clear_table_query = f"DELETE FROM filtered_resorts;"
    cursor.execute(clear_table_query)
    print(f"Cleared existing resorts in filtered_resorts.")

    cursor.close()
    conn.close()


    ### Extract all fields from the JSON request
    user_name = data.get("userName")
    distance = float(data.get("distance")) # minutes
    people = int(data.get("people"))
    budget = float(data.get("budget"))
    driving_experience = data.get("drivingExperience")
    fresh_powder_inches = float(data.get("freshPowder"))
    pass_type = data.get("passType")
    cost_importance = int(data.get("costImportance"))
    time_importance = int(data.get("timeImportance"))
    location=data.get("location")
    latitude=location.get("latitude")
    longitude=location.get("longitude")
    
    ### Debug print to ensure all values are captured
    print(f"User: {user_name}, Distance: {distance}, People: {people}, Budget: {budget}, "
          f"Driving Experience: {driving_experience}, Fresh Powder: {fresh_powder_inches}, Pass Type: {pass_type}, "
          f"Cost Importance: {cost_importance}, Time Importance: {time_importance}")

    ### get all resorts
    all_resorts = get_all_resorts()

    ### filter by meeting min_snowfall requirement
    filtered_resorts = get_resorts_with_fresh_powder(fresh_powder_inches) # returns a filtered list of resorts that meet min snow requirement
    
    if filtered_resorts is None or len(filtered_resorts)==0:
        print("No resorts have the required powder so running optimization for all resorts")
        filtered_resorts=all_resorts
        print(filtered_resorts)

    ### filter by pass type
    filtered_resorts = get_resorts_with_pass(filtered_resorts, pass_type) # filter by pass type (ikon, epic, none)
    print(f"filtered_resorts after pass filtering: {filtered_resorts}")
    store_resorts(filtered_resorts, "filtered_resorts")

    ### get 1 hr snowfall at start and end locations (end = at each resort)
    snowfall_end = [resort.get("precip_accum_1_hour", 0.0) for resort in filtered_resorts]


    stations_1_hr = get_all_1_hr_stations()

    closest_1hr_stations_to_start = get_closest_stations_by_location(stations_1_hr, 40.01791680728027, -105.27065695880714)

    snowfall_start = get_snowfall_from_stations(closest_1hr_stations_to_start)
    print(f"snowfall_start: {snowfall_start}")


    ### update global variables with data from frontend user input
    resorts_to_optimize = [resort["resort_name"] for resort in filtered_resorts]
    resorts_to_optimize.sort()

    ### pass filtered_resorts to cotrip api to get travel times (traffic backend)
    current_time, miles= get_travel_times(latitude, longitude, resorts_to_optimize)

    min_snowfall = fresh_powder_inches
    num_people = people
    max_budget = budget
    max_time = distance
    accidents=[0 for i in range(len(resorts_to_optimize))]
    print(f"resorts_to_optimize: {resorts_to_optimize}")
    print(f"min_snowfall: {min_snowfall},  num_people: {num_people},  max_budget: {max_budget},  max_time: {max_time},  snowfall_importance: {snowfall_importance},  cost_importance: {cost_importance},  time_importance: {time_importance}, snowfall_end: {snowfall_end}, snowfall_start: {snowfall_start}, miles: {miles}, accidents: {accidents}")
    
    ### pass list of filtered resorts with travel times to optimization function
    top_3, cost, time, scores = optimize_ski_resorts(resorts_to_optimize, num_people, max_budget, max_time, min_snowfall, snowfall_importance, cost_importance, time_importance, miles, accidents, snowfall_start, snowfall_end, current_time) 
    #top_3, cost, time, scores = optimize_ski_resorts(resorts_to_optimize, num_people, max_budget, max_time, min_snowfall, snowfall_importance, cost_importance, time_importance) 

    # Print the top resorts in the terminal
    print("\n=== Top 3 Ski Resorts ===")
    for rank, resort_name in enumerate(top_3, start=1):
        idx = resorts_to_optimize.index(resort_name)
        print(f"\nRank #{rank}:")
        print(f"  {resort_name}")
        print(f"  Score: {scores[idx]:.2f}")
        print(f"  Cost per Person: ${cost[idx]}")
        print(f"  Travel Time: {time[idx]:.2f} hrs")
        print(f"  Snowfall: {snowfall_end[idx]} inches")


    print(f"Top 3 resorts: {top_3}")


    # Get fresh resort data from DB with updated distances
    updated_filtered_resorts = get_filtered_resorts_from_db()

    # Filter only the top 3
    top_3_resorts = [
        resort for resort in updated_filtered_resorts
        if resort["resort_name"] in top_3
    ]


    print(f"top_3_resorts: {top_3_resorts}")
    # store the filtered list in the database in "top_3_resorts" table, should only have 3
    store_resorts(top_3_resorts, "top_3_resorts")

    # call polyline API with start_location and the lat/long of the 3 predicted resorts and update polyline variable in resort_cards_list 
    get_polyline(latitude, longitude, "top_3_resorts")


    # call db to select only predicted resorts and wanted columns (for frontend cards) from top_3_resorts, add cols
    resort_cards_list = build_resort_cards("top_3_resorts")

    # if not resort_cards_list:
    #     resort_cards_list = all_resorts_cards = build_resort_cards("colorado_resorts") # get all cards for all resorts in colorado_resorts db

    return jsonify({"resorts": resort_cards_list}), 200 


@app.route("/get_all_resorts", methods=["GET"])
def api_get_all_resorts():
    all_resorts_cards = build_resort_cards("colorado_resorts") # get all cards for all resorts in colorado_resorts db
    return jsonify({"resorts": all_resorts_cards}), 200


def get_all_resorts():
    """
    Retrieves all resorts from the colorado_resorts table.
    Returns a list of dictionaries, each representing a resort.
    """
    print("Fetching all resorts from colorado_resorts...")

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM colorado_resorts;"
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    resorts = [
        {col: float(row[idx]) if isinstance(row[idx], Decimal) else row[idx] for idx, col in enumerate(column_names)}
        for row in rows
    ]

    cursor.close()
    conn.close()
    print(f"Retrieved {len(resorts)} resorts.")
    return resorts


def get_resorts_with_fresh_powder(fresh_powder_inches):
    """
    Queries the database for resorts with snowfall in the last 24 hours greater than or equal to fresh_powder_inches.
    Converts inches to cm before querying.
    """
    print("Filtering by fresh powder...")
    fresh_powder_cm = float(fresh_powder_inches) * 25.4 if fresh_powder_inches is not None else 0.0  # Convert to mm

    print(f"Getting resorts with ≥ {fresh_powder_cm}cm of fresh powder")

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT cr.*
    FROM colorado_resorts cr
    JOIN recent_snowfall rs ON cr.resort_name = rs.resort_name
    WHERE rs.precip_accum_24_hour >= %s;
    """
    
    cursor.execute(query, (fresh_powder_cm,))
    resorts = cursor.fetchall()
    
    column_names = [desc[0] for desc in cursor.description]


    # convert Decimals to float before returning JSON
    resort_list = [
        {col: float(row[idx]) if isinstance(row[idx], Decimal) else row[idx] for idx, col in enumerate(column_names)}
        for row in resorts
    ]

    cursor.close()
    conn.close()
    # print(resort_list)

    return resort_list  # Return the filtered list of resorts


def get_resorts_with_pass(resort_list, pass_type):
    """
    Filters the resort list based on the pass type.
    - If pass_type is "epic", returns resorts where pass_type is "Epic".
    - If pass_type is "ikon", returns resorts where pass_type is "Ikon".
    - If pass_type is "none", returns all resorts without filtering.
    """
    if pass_type.lower() == "none":
        print("No filtering applied for pass type.")
        return resort_list  # No filtering needed

    # Convert pass_type to title case to match database values ("Epic", "Ikon", "Neither")
    pass_type = pass_type.title()

    # Filter the resorts based on the pass_type column
    filtered_resorts = [resort for resort in resort_list if resort["pass_type"] == pass_type]

    print(f"Filtered {len(filtered_resorts)} resorts for pass type: {pass_type}")

    return filtered_resorts


def store_resorts(resort_list, table_to_store):
    """
    Clears the given table and inserts the filtered resorts.
    """
    if not resort_list:
        print(f"No resorts to store in {table_to_store}.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear the given table
    clear_table_query = f"DELETE FROM {table_to_store};"
    cursor.execute(clear_table_query)
    print(f"Cleared existing resorts in {table_to_store}.")

    # Sort by snowfall
    sorted_resort_list = sorted(resort_list, key=lambda r: r["precip_accum_24_hour"], reverse=True)

    # Build the INSERT query dynamically using the table name
    insert_query = f"""
    INSERT INTO {table_to_store} (
        resort_name, state, summit, base, vertical, lifts, runs, acres, 
        green_percent, green_acres, blue_percent, blue_acres, black_percent, 
        black_acres, lat, lon, closest_station, closest_station_id, 
        precip_accum_24_hour, precip_accum_1_hour, pass_type, logo_path, logo_alt, distance
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    );
    """

    resort_rows = [
        (
            resort["resort_name"], resort["state"], resort["summit"], resort["base"], resort["vertical"],
            resort["lifts"], resort["runs"], resort["acres"], resort["green_percent"], resort["green_acres"],
            resort["blue_percent"], resort["blue_acres"], resort["black_percent"], resort["black_acres"],
            resort["lat"], resort["lon"], resort["closest_station"], resort["closest_station_id"], 
            resort["precip_accum_24_hour"], resort["precip_accum_1_hour"], resort["pass_type"], resort["logo_path"], resort["logo_alt"], resort["distance"]
        )
        for resort in sorted_resort_list
    ]

    cursor.executemany(insert_query, resort_rows)
    conn.commit()
    
    print(f"Stored {len(sorted_resort_list)} resorts in {table_to_store}.")

    cursor.close()
    conn.close()


def build_resort_cards(table_name):
    """
    Fetch relevant resort data from filtered_resorts, reshape it to match
    the frontend card format, and inject distance values from the provided list.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT resort_name, lat, lon, logo_path, logo_alt, precip_accum_24_hour, polyline, distance
        FROM {table_name}
        ORDER BY precip_accum_24_hour DESC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    # rows = rows in top_3_resorts

    resort_cards = []
    for idx, row in enumerate(rows):
        resort_name, lat, lon, logo_path, logo_alt, precip_accum_24_hour, polyline, distance = row

        if resort_name == "Sunlight, CO":
            continue  # skip Sunlight

        card = {
            "place": resort_name,
            "distance": int(distance) if distance is not None else 0, # updated
            "icon": logo_path,
            "iconAlt": logo_alt,
            "endPoint": {
                "lat": float(lat) if lat else None,
                "lng": float(lon) if lon else None
            },
            "encodedPolyline": polyline,
            "snow": float(precip_accum_24_hour)/25.4 if precip_accum_24_hour else 0.0
        }
        resort_cards.append(card)

    cursor.close()
    conn.close()

    return resort_cards


# https://maps.googleapis.com/maps/api/directions/json?origin=39.6995,-105.1162&destination=40.01499,-105.27055&mode=driving&departure_time=now&key=YOUR_API_KEY

def get_polyline(start_lat, start_lng, table_name):
    """
    Given the user's start coordinates, generate and update the polyline for each resort in the given table.
    If the initial API call fails, retry using 'Boulder, CO' as origin and 'resort_name, CO' as destination.
    """
    print(f"Fetching polylines from Google Maps API for table: {table_name}...")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch resort names and their lat/lng from the specified table
    select_query = f"SELECT resort_name, lat, lon, state FROM {table_name};"
    cursor.execute(select_query)
    resorts = cursor.fetchall()

    for resort_name, resort_lat, resort_lng, state in resorts:
        origin = f"{start_lat},{start_lng}"
        destination = f"{resort_lat},{resort_lng}"
        api_url = (
            f"https://maps.googleapis.com/maps/api/directions/json"
            f"?origin={origin}&destination={destination}&mode=driving"
            f"&departure_time=now&key={GMAPS_API_KEY}"
        )
        print(api_url)

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            directions_data = response.json()

            if directions_data["status"] == "OK":
                polyline = directions_data["routes"][0]["overview_polyline"]["points"]

            else:
                # Fallback: use city names instead of lat/lng
                print(f"Primary route failed for {resort_name}. Trying fallback with city names...")
                fallback_origin = "Boulder, CO"
                fallback_destination = f"{resort_name}, {state}"

                fallback_url = (
                    f"https://maps.googleapis.com/maps/api/directions/json"
                    f"?origin={fallback_origin}&destination={fallback_destination}&mode=driving"
                    f"&departure_time=now&key={GMAPS_API_KEY}"
                )
                fallback_response = requests.get(fallback_url)
                fallback_response.raise_for_status()
                fallback_data = fallback_response.json()

                if fallback_data["status"] == "OK":
                    polyline = fallback_data["routes"][0]["overview_polyline"]["points"]
                else:
                    print(f"Fallback failed for {resort_name}: {fallback_data['status']}")
                    continue  # Skip updating this resort

            # Update the specified table with the polyline
            update_query = f"""
                UPDATE {table_name}
                SET polyline = %s
                WHERE resort_name = %s;
            """
            cursor.execute(update_query, (polyline, resort_name))
            conn.commit()
            print(f"Updated polyline for: {resort_name}")

        except Exception as e:
            print(f"Exception fetching polyline for {resort_name}: {e}")

    cursor.close()
    conn.close()
    print(f"Polyline updates complete for table: {table_name}.")


def get_closest_stations_to_coordinates(latitude, longitude):
    """
    For the given lat/long, call the Synoptic API with a 20-mile radius and limit of 50.
    Return a list of the closest 50 station STIDs.
    """
    print(f"Getting closest stations to (Lat: {latitude}, Lon: {longitude})")
    radius_miles = 20
    limit_count = 50
    url = (
        f"{SYNOPTIC_API_ROOT}stations/metadata?"
        f"token={SYNOPTIC_API_TOKEN}&radius={latitude},{longitude},{radius_miles}&limit={limit_count}"
    )
    headers = {'content-type': 'application/json'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"API call error for coordinates {latitude}, {longitude}: {e}")
        return []

    if "STATION" in data and len(data["STATION"]) > 0:
        stations = data["STATION"]
        print(f"Found {len(stations)} stations for coordinates {latitude}, {longitude}")
        return [station["STID"] for station in stations if "STID" in station]
    else:
        print(f"No station data available for coordinates {latitude}, {longitude}")
        return []



def get_snowfall_from_stations(start_closest_stations):
    """
    Go through the list of STIDs stored in start_closest_stations and make an API call for each
    to try to get the 1-hr snowfall (precip_accum_one_hour). Return the first valid result found.
    If none are found, return 0.0.
    """
    print("Checking 1-hour snowfall at starting location...")

    for station in start_closest_stations:
        station_id = station['stid']
        print(f"  Trying station {station_id}...")

        url = (
            f"{SYNOPTIC_API_ROOT}stations/timeseries?stid={station_id}&recent=1000"
            f"&vars=precip_accum_one_hour&token={SYNOPTIC_API_TOKEN}"
        )
        headers = {'content-type': 'application/json'}
        #print(f"  API URL: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"    Error fetching/parsing data for station {station_id}: {e}")
            continue

        station_data = data.get('STATION', [])
        if not station_data:
            print(f"    No station data returned for station {station_id}")
            continue

        observations = station_data[0].get('OBSERVATIONS', {})

        precip_values = observations.get('precip_accum_one_hour_set_1', [])

        if precip_values:
            valid_precip_values = [v for v in precip_values if v is not None]
            if valid_precip_values:
                precip = valid_precip_values[-1]
                print(f"    Found valid 1-hr snowfall: {precip} mm at station {station_id}")
                return precip
            else:
                print(f"    No valid 1-hr precipitation values at station {station_id}")
        else:
            print(f"    No precipitation data at all for station {station_id}")

    print("  No valid 1-hr snowfall found at any nearby station. Defaulting to 0.0.")
    return 0.0


def get_all_1_hr_stations():

    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM station_locations_snowfall_1_hr;'
    cursor.execute(query)
    rows = cursor.fetchall()

    # Get column names
    colnames = [desc[0] for desc in cursor.description]

    result = [dict(zip(colnames, row)) for row in rows]

    cursor.close()
    conn.close()

    return result


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two lat/lon points using the Haversine formula."""
    R = 6371  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in kilometers


def get_closest_stations_by_location(station_list, start_lat, start_long, max_results=None):
    """
    Returns the list of STIDs from the station_list sorted by distance to the starting location.
    
    Args:
        station_list: list of dicts, each with 'STID', 'STID_lat', 'STID_long'
        start_lat: float, starting latitude
        start_long: float, starting longitude
        max_results: optional int, limit number of closest stations returned

    Returns:
        List of station dicts sorted by distance (each dict will have 'STID', 'distance_km', etc.)
    """
    stations_with_distance = []
    
    for station in station_list:
        try:
            distance = haversine_distance(
                start_lat, start_long,
                float(station['stid_lat']),
                float(station['stid_long'])
            )
            station_with_distance = {
                **station,
                'distance_km': distance
            }
            stations_with_distance.append(station_with_distance)
        except Exception as e:
            print(f"Error calculating distance for station {station.get('STID')}: {e}")
            continue

    # Sort by distance
    sorted_stations = sorted(stations_with_distance, key=lambda x: x['distance_km'])

    if max_results:
        return sorted_stations[:max_results]
    return sorted_stations


# def get_travel_times(start_lat, start_long, resort_names):
#     """
#     Fetchs both time taken to reach the ski resort as well as distance to the ski resort
#     """
#     print("Fetching travel times to all colorado_resorts...")
#     current_times=[]
#     miles=[]
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     # Create a tuple of resort names for the SQL IN clause
#     placeholders = ', '.join(["%s"] * len(resort_names))
#     query = f"SELECT resort_name, lat, lon FROM colorado_resorts WHERE resort_name IN ({placeholders}) ORDER BY resort_name;"
    
#     cursor.execute(query, resort_names)
#     rows = cursor.fetchall()

#     for row in rows:
#         travel_details=calculate_route(f"{start_lat},{start_long}", f"{row[1]},{row[2]}")["routes"][0]
#         current_times.append(travel_details["summary"]["travelTimeInSeconds"])
#         miles.append(travel_details["summary"]["lengthInMeters"]*0.00062137)

#     cursor.close()
#     conn.close()
#     print(f"Retrieved travel information.")
#     return current_times, miles

def get_travel_times(start_lat, start_long, resort_names):
    """
    Fetch both time taken to reach the ski resort as well as distance to the ski resort,
    preserving the order of resort_names. Also update the filtered_resorts table with distances.
    """
    print("Fetching travel times to all colorado_resorts...")
    travel_info = {}  # temp dict to store results by resort name

    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ', '.join(["%s"] * len(resort_names))
    query = f"SELECT resort_name, lat, lon FROM colorado_resorts WHERE resort_name IN ({placeholders});"
    
    cursor.execute(query, resort_names)
    rows = cursor.fetchall()

    for row in rows:
        resort_name, lat, lon = row
        travel_details = calculate_route(f"{start_lat},{start_long}", f"{lat},{lon}")["routes"][0]
        travel_time = travel_details["summary"]["travelTimeInSeconds"]
        distance_miles = travel_details["summary"]["lengthInMeters"] * 0.00062137

        travel_info[resort_name] = {
            "time": travel_time,
            "miles": distance_miles
        }

        # Update the distance in the filtered_resorts table
        update_query = """
            UPDATE filtered_resorts
            SET distance = %s
            WHERE resort_name = %s;
        """
        cursor.execute(update_query, (distance_miles, resort_name))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Retrieved travel information and updated filtered_resorts.")

    # Reconstruct ordered lists
    current_times = [travel_info[name]["time"] for name in resort_names]
    miles = [travel_info[name]["miles"] for name in resort_names]

    return current_times, miles


def get_filtered_resorts_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM filtered_resorts;"
    cursor.execute(query)
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]

    result = [dict(zip(colnames, row)) for row in rows]

    cursor.close()
    conn.close()
    return result


def maybe_update_snowfall_data():
    global last_snowfall_update

    now = datetime.utcnow()
    if last_snowfall_update is None or (now - last_snowfall_update > UPDATE_INTERVAL):
        print("Updating snowfall data...")
        try:
            subprocess.run(["python3", "recent_snowfall_backend.py"], check=True)
            last_snowfall_update = now
            print("Snowfall data updated.")
        except subprocess.CalledProcessError as e:
            print(f"Error updating snowfall data: {e}")
    else:
        print("Snowfall data is up-to-date.")


if __name__ == "__main__":
    # start flask app
    app.run(host="0.0.0.0", port=8000)
    # api_get_all_resorts()
    # get_closest_stations_to_coordinates(40.01791680728027, -105.27065695880714)
    
