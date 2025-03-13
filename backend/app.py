from flask import Flask, request, jsonify
import psycopg2
import requests
import json
from flask_cors import CORS


app = Flask(__name__)

# Enable CORS for all routes or specific origins
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

gmaps_API_KEY="AIzaSyAVmTm21eXwuF0FRIopdo-IIiajWOMZlfs"

def get_db_connection():
    conn = psycopg2.connect(
        host="34.46.13.43",
        database="postgres",
        user="postgres",
        password="letsg0sk!!ng"
    )
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
        return f"{coordinates["lat"]},{coordinates["lng"]}"
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return
    
@app.route("/get_mountain", methods=["POST"])
def get_mountain():
    data=request.get_json()
    print("Input recieved")
    print(data)
    user_name=data.get("userName")
    distance=data.get("distance")
    pass_type=data.get("passType")
    difficulty=data.get("difficulty")
    avalanche_risk=data.get("avalancheRisk")


    return jsonify({"Input recieved": str(1)}), 200

if __name__ == "__main__":
    # start flask app
    #print(get_start_coordinates("232 Co Rd 29, Leadville, CO"))
    app.run(host="0.0.0.0", port=8000)
