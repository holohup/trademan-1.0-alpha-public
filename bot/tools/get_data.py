import requests
from settings import SHORTS_ENDPOINT, ENDPOINT_HOST, STOPS_ENDPOINT

def get_shorts():
    URL = ENDPOINT_HOST+SHORTS_ENDPOINT
    response = requests.get(URL)
    return response.json()

def get_stops():
    URL = ENDPOINT_HOST+STOPS_ENDPOINT
    response = requests.get(URL)
    return response.json()

