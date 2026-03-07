import requests

API_KEY = "COLE_SUA_CHAVE_AQUI"


def geocode(cidade):

    url = "https://api.openrouteservice.org/geocode/search"

    params = {
        "api_key": API_KEY,
        "text": cidade
    }

    r = requests.get(url, params=params)

    data = r.json()

    coords = data["features"][0]["geometry"]["coordinates"]

    return coords


def calcular_km(origem, destino):

    origem_coord = geocode(origem)
    destino_coord = geocode(destino)

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            origem_coord,
            destino_coord
        ]
    }

    r = requests.post(url, json=body, headers=headers)

    dados = r.json()

    distancia = dados["routes"][0]["summary"]["distance"]

    km = distancia / 1000

    return round(km)
