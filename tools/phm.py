#!/usr/bin/env python3

import json
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import sys, os.path
from geopy import distance
import argparse
import unicodedata

# Parse commandline arguments
parser = argparse.ArgumentParser(description='Eurooil prices checker.')
parser.add_argument('--location', help='Location to search for nearest station', nargs='+', default='')
parser.add_argument('--update', action='store_const', const=True, default=False,
                    help='Update data from Eurooil web')
args = parser.parse_args()

# convert input location to single string
input_location_raw = " ".join(args.location).strip()
# normalize input location
input_location = unicodedata.normalize('NFKD', input_location_raw).encode('ascii','ignore').decode('ascii').lower()

# Set default location if none is given
if len(input_location) == 0:
    input_location = 'opustena'

# Use cache to read data if possible
cache = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../cache/phm.json')
data = None
if not args.update:
    try:
        with open(cache) as f:
            data = json.load(f)
    except:
        pass

# When cache is not available or an update was requested, read from API
if not data:
    res = requests.post('https://einfo.ceproas.cz/cepro_portal_ws/rest/common/prox/mobileData/',
        auth=HTTPBasicAuth('mobap', 'EWikA2'),
        data='{}',
        headers={'Content-Type': 'application/json; charset=UTF-8'}
    )
    if (res.status_code != 200):
        exit(1)

    data = json.loads(res.content)
    with open(cache, 'w+') as f:
        json.dump(data, f)

station = None
# Try to find exact station based on the name of location
for s in data['Data']['cs_fix_list']:
    if input_location in unicodedata.normalize('NFKD', s['nazev_kratky']).encode('ascii','ignore').decode('ascii').lower():
        station = s
        break

# If no station was found and we have location, try to find nearest one
location = None
if not station and len(input_location) > 0:
    res = requests.get('http://api.geonames.org/search?name=' + urllib.parse.quote_plus(input_location) + '&countryBias=CZ&username=thorgrin&maxRows=1&type=json')
    result = json.loads(res.content)
    if result['totalResultsCount'] > 0:
        location = result['geonames'][0]
        
        # Find nearest station to given location
        min_distance = float('inf')
        for s in data['Data']['cs_fix_list']:
            s_distance = distance.distance(
                (s['GPS']['lat_dec'], s['GPS']['long_dec']),
                (location['lat'], location['lng'])
            )
            if s_distance < min_distance:
                min_distance = s_distance
                station = s

# A location was given but not found
if not station:
    print(input_location_raw + ' is not a place')
    exit(0)

# Load products
products = dict()
for product in data['Data']['cis_prod_list']:
    products[product['kod_produkt']] = product['nazev_produkt']

# Get prices
for prices in data['Data']['cs_ceny']:
    if station['kod_cs'] == prices['kod_cs']:
        break;

# Print
print('[{station_name}] {prices}'.format(
    station_name=station['nazev_kratky'],
    prices=', '.join([products[p['kod_produkt']] + ": " + '%.2f' % p['cena'] for p in prices['ceny']]))
)
