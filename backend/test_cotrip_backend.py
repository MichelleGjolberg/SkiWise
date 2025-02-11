import sys
import os
import jsonpickle, json
import requests

REST = os.getenv("REST") or "127.0.0.1:2000"
addr = f"http://{REST}"

def returnResp(response):
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print(jsonResponse)
        return
    else:
        print(f"response code is {response.status_code}, raw response is {response.text}")
        return response.text

def testGetCurrentIncidents():
    get_incidents_url = addr + "/apiv1/incidents/current"
    headers = {'content-type': 'application/json'}
    response = requests.get(get_incidents_url, headers=headers)
    returnResp(response)

def testGetIncidentDetails(incidentId):
    get_incident_details_url = addr + f"/apiv1/incidents/{incidentId}"
    headers = {'content-type': 'application/json'}
    response = requests.get(get_incident_details_url, headers=headers)
    returnResp(response)

def testReportIncident(description, location):
    report_incident_url = addr + "/apiv1/incidents/report"
    headers = {'content-type': 'application/json'}
    data = jsonpickle.encode({"description": description, "location": location})
    response = requests.post(report_incident_url, data=data, headers=headers)
    returnResp(response)

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <cmd>")
    print(f"    where <cmd> is one of: getCurrentIncidents, getIncidentDetails, reportIncident")
else:
    cmd = sys.argv[1]
    
    if cmd == 'getCurrentIncidents':
        print("Retrieving current incidents...")
        testGetCurrentIncidents()
    elif cmd == 'getIncidentDetails':
        if len(sys.argv) < 3:
            print(f"Usage: {sys.argv[0]} getIncidentDetails <incident-id>")
        else:
            print(f"Retrieving details for incident ID {sys.argv[2]}...")
            testGetIncidentDetails(sys.argv[2])
    elif cmd == 'reportIncident':
        if len(sys.argv) < 4:
            print(f"Usage: {sys.argv[0]} reportIncident <description> <location>")
        else:
            print(f"Reporting new incident: {sys.argv[2]} at {sys.argv[3]}...")
            testReportIncident(sys.argv[2], sys.argv[3])
    else:
        print("Unknown option", cmd)
