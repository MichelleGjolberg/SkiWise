from flask import Flask, request, jsonify
import psycopg2
import requests
import json
from flask_cors import CORS
from decimal import Decimal
from formulations import (
    calculate_base_fee,
    round_up_to_nearest_10,
    normalize,
    calculate_cost_per_person,
    calculate_travel_time,
    optimize_ski_resorts)


# ==========================
# User Inputs & from API ----------------------> Get from backend
# ==========================
num_people = 4
max_budget = 100
max_time = 5
min_snowfall = 1
w1, w2, w3 = 5, -5, -5

# Hardcoded Parameters
DRIVING_EXPERIENCE_FACTOR = 0.1  # Intermediate level
FUEL_COST = 3                 # Dollars per mile
MAINTENANCE_FACTOR = 0.10     # 10%
SNOWFALL_TIME_FACTOR = 0.5   # Random weight added per inch of snowfall
NORM_MIN = 1 # Normalization range
NORM_MAX = 5

# ==========================
# Hardcoded Data for 10 Resorts -----------------> Get from backend
# ==========================

# Attributes for each resort: miles (both-ways), accidents, snowfall_start, snowfall_end, current_time (seconds)
# resorts_to_optimize = []
resorts_to_optimize = [
    "Arapahoe Basin, CO",
    "Aspen Highlands, CO",
    "Aspen Mt, CO",
    "Beaver Creek, CO",
    "Breckenridge, CO",
    "Buttermilk, CO",
    "Copper Mt, CO",
    "Crested Butte, CO",
    "Echo Mountain",          # TODO not in DB
    "Eldora, CO"
]



miles =          [30, 21, 40, 57, 46, 105, 72, 83, 85, 220]
accidents =      [3,  1,  2,  0,  5,   1,  0,  2,  0,  7]
snowfall_start = [1, 2, 2, 6, 4, 3, 2, 5, 1, 2]
snowfall_end =   [12, 7, 14, 8, 6, 18, 9, 11, 4, 10]
current_time =   [3600, 1800, 5400, 4320, 2880, 7200, 3960, 4680, 2520, 3480]  # In seconds


# list of all resorts and data
all_resorts = []

app = Flask(__name__)

# Enable CORS for all routes or specific origins
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

gmaps_API_KEY="AIzaSyAVmTm21eXwuF0FRIopdo-IIiajWOMZlfs"

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
    get_coordinates_url=f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={gmaps_API_KEY}"

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
    distance = data.get("distance")
    people = data.get("people")
    budget = data.get("budget")
    driving_experience = data.get("drivingExperience")
    fresh_powder_inches = data.get("freshPowder")
    pass_type = data.get("passType")
    cost_importance = data.get("costImportance")
    time_importance = data.get("timeImportance")

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


    ### TODO need to then pass filtered_resorts to cotrip api to get travel times (traffic backend)


    ### pass list of filtered resorts with travel times to optimization function
    # TODO works on dummy variables in formulations.py right now, need to update with data from frontend (Sierra working on)
    # update global variables with data from frontend user input
    # resorts_to_optimize = [resort["resort_name"] for resort in filtered_resorts]
    
    # Optimize
    top_3, cost, time, scores = optimize_ski_resorts(resorts_to_optimize, num_people, max_budget, max_time, min_snowfall, w1, w2, w3)

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


    print(top_3)

    # Filter the in-memory list to only include those resorts
    filtered_resorts = [
        resort for resort in all_resorts
        if resort["resort_name"] in top_3
    ]

    print(filtered_resorts)
    # store the filtered list in the database, should only have 3
    store_filtered_resorts(filtered_resorts)


    # call db to select only predicted resorts and wanted columns (for frontend cards) from filtered_resorts, add cols
    resort_cards_list = build_resort_cards()

    # TODO call polyline API with start_location and the lat/long of the 3 predicted resorts and add this to the list


    # return jsonify({"message": "Input received successfully"}), 200
    return jsonify({"resorts": resort_cards_list}), 200 



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
    fresh_powder_cm = float(fresh_powder_inches) * 2.54 if fresh_powder_inches is not None else 0.0  # Convert to cm

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


def build_resort_cards():
    """
    Fetch relevant resort data from filtered_resorts, reshape it to match
    the frontend card format, and inject distance values from the provided list.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT resort_name, lat, lon, logo_path, logo_alt, precip_accum_24_hour
        FROM filtered_resorts
        ORDER BY precip_accum_24_hour DESC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    resort_cards = []
    for idx, row in enumerate(rows):
        resort_name, lat, lon, logo_path, logo_alt, snowfall = row

        card = {
            "place": resort_name,
            "distance": 0, # TODO update when have global distance variable, make sure in same order (maybe make distances a dictionary?)
            "icon": logo_path,
            "iconAlt": logo_alt,
            "endPoint": {
                "lat": float(lat) if lat else None,
                "lng": float(lon) if lon else None
            },
            "encodedPolyline": None,
            "snow": float(snowfall) if snowfall else 0.0
        }
        resort_cards.append(card)

    cursor.close()
    conn.close()

    return resort_cards



if __name__ == "__main__":
    # start flask app
    #print(get_start_coordinates("232 Co Rd 29, Leadville, CO"))
    app.run(host="0.0.0.0", port=8000)
