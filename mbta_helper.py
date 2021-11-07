import urllib.request
import urllib.parse
import json
from pprint import pprint


# Useful URLs (you need to add the appropriate parameters for your requests)
MAPQUEST_BASE_URL = "http://www.mapquestapi.com/geocoding/v1/address"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"

# Your API KEYS (you need to use your own keys - very long random characters)
MAPQUEST_API_KEY = "HcIYW7mvcsgmK8EmyT1yAFMhAFJbUAXG"
MBTA_API_KEY = "b11548df087a42b9bad23d21a61347ad"


# A little bit of scaffolding if you want to use it


def get_json(url):
    """
    Given a properly formatted URL for a JSON web API request, return
    a Python JSON object containing the response to that request.
    """
    f = urllib.request.urlopen(url)
    response_text = f.read().decode('utf-8')
    response_data = json.loads(response_text)
    return response_data


def get_lat_long(place_name):
    """
    Given a place name or address, return a (latitude, longitude) tuple
    with the coordinates of the given place.
    See https://developer.mapquest.com/documentation/geocoding-api/address/get/
    for Mapquest Geocoding  API URL formatting requirements.
    """
    data = urllib.parse.urlencode({
        'key': MAPQUEST_API_KEY,
        'location': place_name,
        'maxResults': 1,
    })
    url = f"{MAPQUEST_BASE_URL}?{data}"
    response_data = get_json(url)
    return response_data["results"][0]["locations"][0]["latLng"][
        "lat"], response_data["results"][0]["locations"][0]["latLng"]["lng"]


def get_nearest_station(latitude, longitude, vehicle_types):
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible)
    tuple for the nearest MBTA station to the given coordinates.
    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL
    formatting requirements for the 'GET /stops' API.
    """
    data = urllib.parse.urlencode({
        'api_key': MBTA_API_KEY,
        'page[limit]': 1,
        'sort': 'distance',
        'filter[latitude]': latitude,
        'filter[longitude]': longitude,
        'filter[radius]': 1,
        'filter[route_type]': vehicle_types,
    })
    url = f"{MBTA_BASE_URL}?{data}"
    response_data = get_json(url)
    return response_data['data'][0]['attributes']['name'], response_data[
        'data'][0]['attributes']['wheelchair_boarding'] == 1


def find_stop_near(place_name, vehicle_types=None):
    """
    Given a place name or address, return the nearest MBTA stop and whether it is wheelchair accessible.
    """
    latitude, longitude = get_lat_long(place_name)
    return get_nearest_station(latitude, longitude, vehicle_types)


def main():
    """
    You can test all the functions here
    """
    print(find_stop_near("Babson College", '4'))


if __name__ == '__main__':
    main()