import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

API_KEY=os.getenv("TRAFFIC_API_KEY")

def calculate_route(start, dest):
    calc_route_url=f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{dest}/json?key={API_KEY}"

    try:
        response = requests.request("GET", calc_route_url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request for route calculation: {e}")
        return None
    

def get_incidents(bleft, tright):
    get_incidents_url=f"https://api.tomtom.com/traffic/services/5/incidentDetails?key={API_KEY}&bbox={bleft},{tright}&language=en-GB&timeValidityFilter=present"

    try:
        response = requests.request("GET", get_incidents_url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request for traffic incidents: {e}")
        return


# start="39.7392,-104.9903"
# dest="38.8353,-104.8216"

# start="4.8854592519716675,52.36934334773164"
# dest="4.897883244144765,52.37496348620152"
#print(get_incidents(start, dest))
