import json
import os
from dotenv import load_dotenv
import folium
import requests
from geopy import distance


def fetch_coordinates(apikey, address):
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


def distance_to_place(dist):
    return dist['distance']


def main():
    load_dotenv()
    apikey = os.getenv('APIKEY')

    location = input('Где вы находитесь? ')
    coords = fetch_coordinates (apikey, location)
    a, b = coords
    coords = b, a

    with open("coffee.json", "r") as my_file:
      file_contents = my_file.read()

    cafe = json.loads(file_contents)

    coffee_shop = []
    for shop in cafe:
        coordinates_coffee_shop = shop['Latitude_WGS84'], shop['Longitude_WGS84']
        distance_to_coffee_shop = distance.distance(coords, coordinates_coffee_shop).km
        coffee_shop_details = {
            'title': shop['Name'],
            'distance': distance_to_coffee_shop,
            'latitude': shop['Latitude_WGS84'],
            'longitude': shop['Longitude_WGS84']
        }
        coffee_shop.append(coffee_shop_details)
    organized_coffe_shop = sorted(coffee_shop, key=distance_to_place)
    slice_coffe_shop = organized_coffe_shop[:5]

    map = folium.Map(location=coords)

    group_1 = folium.FeatureGroup("first group").add_to(map)
    folium.Marker(coords, icon=folium.Icon("green")).add_to(group_1)

    for coordinates in slice_coffe_shop:
        group_2 = folium.FeatureGroup("second group").add_to(map)
        folium.Marker((coordinates['latitude'], coordinates['longitude']), icon=folium.Icon("red")).add_to(group_2)

    map.save("index.html")


if __name__ == '__main__':
    main()