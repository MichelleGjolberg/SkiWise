## file to pull from a weather API 
# will have a list of the resorts that are within the user-defined distance range and make API calls to get the recent snowfall at that location

import sys
import os
import base64
import jsonpickle, json
import requests

# Synoptic data API
# token: fda25733baec41ee90dd23653e94a1a8
# key: KuOMm49ZKk4W5zFM2YEVmGID1bIaXFgJKUmJI2tekJ

# snow_depth, snow_accum, precip_storm, precip_accum_six_hour, precip_accum_six_hour, snow_accum_since_7_local, snow_accum_24_hour


API_ROOT = "https://api.synopticdata.com/v2/"
API_TOKEN = "fda25733baec41ee90dd23653e94a1a8"