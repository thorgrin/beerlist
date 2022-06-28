#!/usr/bin/env python3

import json
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import sys
from geopy import distance

res = requests.post('https://einfo.ceproas.cz/cepro_portal_ws/rest/common/prox/mobileData/',
    auth=HTTPBasicAuth('mobap', 'EWikA2'),
    data='{}',
    headers={'Content-Type': 'application/json; charset=UTF-8'}
)
data = json.loads(res.content)

# with open('data.json') as f:
#     data = json.load(f);

location = None
if len(sys.argv) > 1 and len(sys.argv[1]) > 0:
    input_location = sys.argv[1]
    res = requests.get('http://api.geonames.org/search?name=' + urllib.parse.quote_plus(input_location) + '&countryBias=CZ&username=thorgrin&maxRows=1&type=json')
    result = json.loads(res.content)
    if result['totalResultsCount'] > 0:
        location = result['geonames'][0]

# Find Brno Opuštěná station (default)
for station in data['Data']['cs_fix_list']:
    if 'Opuštěná' in station['nazev_kratky']:
        kod_cs = station['kod_cs']
        break

# Find nearest station to given location
if location:
    min_distance = float('inf')
    for s in data['Data']['cs_fix_list']:
        s_distance = distance.distance(
            (s['GPS']['lat_dec'], s['GPS']['long_dec']),
            (location['lat'], location['lng'])
        )
        if s_distance < min_distance:
            min_distance = s_distance
            station = s
            kod_cs = s['kod_cs']

# Load products
products = dict()
for product in data['Data']['cis_prod_list']:
    products[product['kod_produkt']] = product['nazev_produkt']

# Get prices
for prices in data['Data']['cs_ceny']:
    if kod_cs == prices['kod_cs']:
        break;

# Print
print('[{station_name}] {prices}'.format(
    station_name=station['nazev_kratky'],
    prices=', '.join([products[p['kod_produkt']] + ": " + '%.2f' % p['cena'] for p in prices['ceny']]))
)
