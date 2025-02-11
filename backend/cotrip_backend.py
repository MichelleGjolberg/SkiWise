import sys
import os
import base64
import jsonpickle, json
import requests


# https://data.cotrip.org/api/v1/incidents?apiKey=<Your_API_KEY>
API_KEY = "S09B8RN-C9XMN13-K31MMV9-5DPCFW1"

addr = f"https://data.cotrip.org/api/v1/"


def returnResp(response):
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print(jsonResponse)
        return
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
        return response.text
    


def getIncidents():
    # visit cotrip incidents page via api to get a list of current incidents
    incidents_url = addr + f"incidents?apiKey={API_KEY}"
    print(incidents_url)
    headers = {'content-type': 'application/json'}

    response = requests.get(incidents_url, headers=headers)  
    return returnResp(response)  # TODO what data do we want 


def getRoadConditions():
    # visit cotrip road conditions page via api to get a list of current road conditions
    incidents_url = addr + f"roadConditions?apiKey={API_KEY}"
    print(incidents_url)
    headers = {'content-type': 'application/json'}

    response = requests.get(incidents_url, headers=headers)  
    return returnResp(response)  # TODO what data do we want 


def getPlannedEvents():
    # visit cotrip planned events page via api
    incidents_url = addr + f"plannedEvents?apiKey={API_KEY}"
    print(incidents_url)
    headers = {'content-type': 'application/json'}

    response = requests.get(incidents_url, headers=headers)  
    return returnResp(response)  # TODO what data do we want 


def getWeatherStations():
    # visit cotrip weather stations page via api to get data on current weather conditions/readings
    incidents_url = addr + f"weatherStations?apiKey={API_KEY}"
    print(incidents_url)
    headers = {'content-type': 'application/json'}

    response = requests.get(incidents_url, headers=headers)  
    return returnResp(response)  # TODO what data do we want 

def getSnowPlows():
    # visit cotrip snow plows page via api to get data on snow plow activity
    incidents_url = addr + f"snowPlows?apiKey={API_KEY}"
    print(incidents_url)
    headers = {'content-type': 'application/json'}

    response = requests.get(incidents_url, headers=headers)  
    return returnResp(response)  # TODO what data do we want 

def getDestinations():
    # visit cotrip destinations page via api to get travel time (seconds) of set road segments
    incidents_url = addr + f"destinations?apiKey={API_KEY}"
    print(incidents_url)
    headers = {'content-type': 'application/json'}

    response = requests.get(incidents_url, headers=headers)  
    return returnResp(response)  # TODO what data do we want 

def getSigns():
    # visit cotrip signs page via api to get sign status and messages
    incidents_url = addr + f"signs?apiKey={API_KEY}"
    print(incidents_url)
    headers = {'content-type': 'application/json'}

    response = requests.get(incidents_url, headers=headers)  
    return returnResp(response)  # TODO what data do we want 



# call each method to get response from COtrip
# getIncidents()
# getRoadConditions()
# getPlannedEvents()
# getWeatherStations()
# getSnowPlows()
# getDestinations()
#getSigns()

