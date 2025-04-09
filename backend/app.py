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

load_dotenv()  # Load variables from .env

SYNOPTIC_API_ROOT = "https://api.synopticdata.com/v2/"

SYNOPTIC_API_TOKEN = os.getenv("SYNOPTIC_API_TOKEN")
GMAPS_API_KEY = os.getenv("GMAPS_API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ==========================
# User Inputs & from API ----------------------> Get from backend
# ==========================

# Hardcoded Data for 10 Resorts -----------------> Get from backend
# default values: TODO update to 0/null ?
num_people = 4
max_budget = 100
max_time = 5
min_snowfall = 1
cost_importance, time_importance = -5, -5 
snowfall_importance = 5 # TODO add frontend slider to snowfall_importance and capture variable in backend

# TODO get from results of traffic API call
miles =          [30, 21, 40, 57, 46, 105, 72, 83, 85, 220, 30, 21, 40, 57, 46, 105, 72, 83, 85, 220, 33, 44, 55, 66]
accidents =      [3,  1,  2,  0,  5,   1,  0,  2,  0,  7, 3,  1,  2,  0,  5,   1,  0,  2,  0,  7, 3, 2, 3, 4]
current_time =   [3600, 1800, 5400, 4320, 2880, 7200, 3960, 4680, 2520, 3480, 3600, 1800, 5400, 4320, 2880, 7200, 3960, 4680, 2520, 3480, 1111, 2222, 3333, 4444]  # In seconds


snowfall_start = [1, 2, 2, 6, 4, 3, 2, 5, 1, 2, 1, 2, 2, 6, 4, 3, 2, 5, 1, 2, 1, 2, 3, 4] # TODO call weather API to get recent snowfall (1 hr?) at start location
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

    ### filter by pass type
    filtered_resorts = get_resorts_with_pass(filtered_resorts, pass_type) # filter by pass type (ikon, epic, none)

    ### update global variables with data from frontend user input
    resorts_to_optimize = [resort["resort_name"] for resort in filtered_resorts]
    resorts_to_optimize.sort()

    ### TODO need to then pass filtered_resorts to cotrip api to get travel times (traffic backend)
    current_time, miles= get_travel_times(latitude, longitude, resorts_to_optimize)

    min_snowfall = fresh_powder_inches
    num_people = people
    max_budget = budget
    max_time = distance
    accidents=[0 for i in range(len(resorts_to_optimize))]
    print(f"resorts_to_optimize: {resorts_to_optimize}")
    print(f"min_snowfall: {min_snowfall},  num_people: {num_people},  max_budget: {max_budget},  max_time: {max_time},  snowfall_importance: {snowfall_importance},  cost_importance: {cost_importance},  time_importance: {time_importance}")
    
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

    # Filter the in-memory list to only include those resorts
    filtered_resorts = [
        resort for resort in all_resorts
        if resort["resort_name"] in top_3
    ]

    print(filtered_resorts)
    # store the filtered list in the database, should only have 3
    store_filtered_resorts(filtered_resorts)

    # TODO API calls for resorts in filtered_resorts to get polyline
    # TODO call polyline API with start_location and the lat/long of the 3 predicted resorts and update polyline variable in resort_cards_list (currently null)
    get_polyline(latitude, longitude)


    # call db to select only predicted resorts and wanted columns (for frontend cards) from filtered_resorts, add cols
    resort_cards_list = build_resort_cards("filtered_resorts")


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



def store_filtered_resorts(resort_list):
    """
    Clears the 'filtered_resorts' table and inserts the filtered resorts.
    If a resort already exists, update its snowfall data.
    """

    if not resort_list:
        print("No resorts to store.")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # clear the table before inserting new data
    clear_table_query = "DELETE FROM filtered_resorts;"
    cursor.execute(clear_table_query)
    print("Cleared existing filtered resorts.")

    # sort the resorts by snowfall in descending order
    sorted_resort_list = sorted(resort_list, key=lambda r: r["precip_accum_24_hour"], reverse=True)

    # insert new resort data
    insert_query = """
    INSERT INTO filtered_resorts (
        resort_name, state, summit, base, vertical, lifts, runs, acres, 
        green_percent, green_acres, blue_percent, blue_acres, black_percent, 
        black_acres, lat, lon, closest_station, closest_station_id, precip_accum_24_hour, pass_type, logo_path, logo_alt
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    );
    """

    resort_rows = [
        (
            resort["resort_name"], resort["state"], resort["summit"], resort["base"], resort["vertical"],
            resort["lifts"], resort["runs"], resort["acres"], resort["green_percent"], resort["green_acres"],
            resort["blue_percent"], resort["blue_acres"], resort["black_percent"], resort["black_acres"],
            resort["lat"], resort["lon"], resort["closest_station"], resort["closest_station_id"], 
            resort["precip_accum_24_hour"], resort["pass_type"], resort["logo_path"], resort["logo_alt"]
        )
        for resort in sorted_resort_list
    ]

    cursor.executemany(insert_query, resort_rows)
    conn.commit()
    
    print(f"Stored {len(sorted_resort_list)} resorts in filtered_resorts table.")

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
        SELECT resort_name, lat, lon, logo_path, logo_alt, precip_accum_24_hour, polyline
        FROM {table_name}
        ORDER BY precip_accum_24_hour DESC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    resort_cards = []
    for idx, row in enumerate(rows):
        resort_name, lat, lon, logo_path, logo_alt, precip_accum_24_hour, polyline = row

        card = {
            "place": resort_name,
            "distance": 0, # TODO update when have global distance variable, make sure in same order (maybe make distances a dictionary?)
            "icon": logo_path,
            "iconAlt": logo_alt,
            "endPoint": {
                "lat": float(lat) if lat else None,
                "lng": float(lon) if lon else None
            },
            "encodedPolyline": polyline,
            "snow": float(precip_accum_24_hour) if precip_accum_24_hour else 0.0
        }
        resort_cards.append(card)

    cursor.close()
    conn.close()

    return resort_cards


# https://maps.googleapis.com/maps/api/directions/json?origin=39.6995,-105.1162&destination=40.01499,-105.27055&mode=driving&departure_time=now&key=YOUR_API_KEY

def get_polyline(start_lat, start_lng):
    """
    Given the user's start coordinates, generate and update the polyline for each resort in the filtered_resorts table.
    """
    print("Fetching polylines from Google Maps API...")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch resort names and their lat/lng from filtered_resorts
    cursor.execute("SELECT resort_name, lat, lon FROM filtered_resorts;")
    resorts = cursor.fetchall()

    for resort_name, resort_lat, resort_lng in resorts:
        origin = f"{start_lat},{start_lng}"
        destination = f"{resort_lat},{resort_lng}"
        api_url = (
            f"https://maps.googleapis.com/maps/api/directions/json"
            f"?origin={origin}&destination={destination}&mode=driving"
            f"&departure_time=now&key={GMAPS_API_KEY}"
        )

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            directions_data = response.json()

            if directions_data["status"] == "OK":
                polyline = directions_data["routes"][0]["overview_polyline"]["points"]

                # Update resort with the polyline
                update_query = """
                    UPDATE filtered_resorts
                    SET polyline = %s
                    WHERE resort_name = %s;
                """
                cursor.execute(update_query, (polyline, resort_name))
                conn.commit()
                print(f"Updated polyline for: {resort_name}")
            else:
                print(f"Error fetching directions for {resort_name}: {directions_data['status']}")
        except Exception as e:
            print(f"Exception fetching polyline for {resort_name}: {e}")

    cursor.close()
    conn.close()
    print("Polyline updates complete.")

def get_travel_times(start_lat, start_long, resort_names):
    print("Fetching travel times to all colorado_resorts...")
    current_times=[]
    miles=[]
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create a tuple of resort names for the SQL IN clause
    placeholders = ', '.join(["%s"] * len(resort_names))
    query = f"SELECT resort_name, lat, lon FROM colorado_resorts WHERE resort_name IN ({placeholders}) ORDER BY resort_name;"
    
    cursor.execute(query, resort_names)
    rows = cursor.fetchall()

    for row in rows:
        travel_details=calculate_route(f"{start_lat},{start_long}", f"{row[1]},{row[2]}")["routes"][0]
        current_times.append(travel_details["summary"]["travelTimeInSeconds"])
        miles.append(travel_details["summary"]["lengthInMeters"]*0.00062137)

    cursor.close()
    conn.close()
    print(f"Retrieved travel information.")
    return current_times, miles

if __name__ == "__main__":
    # start flask app
    app.run(host="0.0.0.0", port=8000)
    # api_get_all_resorts()
    
