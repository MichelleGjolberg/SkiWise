from flask import Flask, request, jsonify
import psycopg2
import requests
import json
from flask_cors import CORS
from decimal import Decimal




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

    # Extract all fields from the JSON request
    user_name = data.get("userName")
    distance = data.get("distance")
    people = data.get("people")
    budget = data.get("budget")
    driving_experience = data.get("drivingExperience")
    fresh_powder_inches = data.get("freshPowder")
    pass_type = data.get("passType")
    cost_importance = data.get("costImportance")
    time_importance = data.get("timeImportance")

    # Debug print to ensure all values are captured
    print(f"User: {user_name}, Distance: {distance}, People: {people}, Budget: {budget}, "
          f"Driving Experience: {driving_experience}, Fresh Powder: {fresh_powder_inches}, Pass Type: {pass_type}, "
          f"Cost Importance: {cost_importance}, Time Importance: {time_importance}")
    
    resorts_with_snow = get_resorts_with_fresh_powder(fresh_powder_inches) # returns a filtered list of resorts

    # store the filtered list in the database
    store_filtered_resorts(resorts_with_snow)

    # TODO need to then pass them to cotrip api to get travel times (traffic backend)

    # TODO need to pass list of resorts with travel times to optimization function

    # return jsonify({"message": "Input received successfully"}), 200
    return jsonify({"resorts": resorts_with_snow}), 200 
    # TOOD do we want to return the list of resorts that meet the min powder requirement?  


def get_resorts_with_fresh_powder(fresh_powder_inches):
    """
    Queries the database for resorts with snowfall in the last 24 hours greater than or equal to fresh_powder_inches.
    Converts inches to cm before querying.
    """
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
    print(resort_list)

    return resort_list  # Return the filtered list of resorts


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
        black_acres, lat, lon, closest_station, closest_station_id, precip_accum_24_hour
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    );
    """

    resort_rows = [
        (
            resort["resort_name"], resort["state"], resort["summit"], resort["base"], resort["vertical"],
            resort["lifts"], resort["runs"], resort["acres"], resort["green_percent"], resort["green_acres"],
            resort["blue_percent"], resort["blue_acres"], resort["black_percent"], resort["black_acres"],
            resort["lat"], resort["lon"], resort["closest_station"], resort["closest_station_id"], 
            resort["precip_accum_24_hour"]
        )
        for resort in sorted_resort_list
    ]

    cursor.executemany(insert_query, resort_rows)
    conn.commit()
    
    print(f"Stored {len(sorted_resort_list)} resorts in filtered_resorts table.")

    cursor.close()
    conn.close()




if __name__ == "__main__":
    # start flask app
    #print(get_start_coordinates("232 Co Rd 29, Leadville, CO"))
    app.run(host="0.0.0.0", port=8000)
