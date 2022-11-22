import requests

from .models import Location
from star_burger.settings import Y_API_KEY


def fetch_coordinates(address, apikey=Y_API_KEY):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_or_create_locations(*addresses):
    existed_locations = {
        location.address: (location.lon, location.lat)
        for location in Location.objects.filter(address__in=addresses)
    }
    for address in addresses:
        if address in existed_locations.keys():
            continue
        coordinates = fetch_coordinates(address)
        if not coordinates:
            continue
        lon, lat = coordinates
        location = Location.objects.create(
            address=address, lon=lon, lat=lat
        )
        existed_locations[location.address] = (location.lon, location.lat)
    return existed_locations
