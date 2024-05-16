#!/usr/bin/env python3

import json
import requests
import urllib.parse
import sys, os.path
from geopy import distance
import argparse
import unicodedata
from bs4 import BeautifulSoup
import re

def ono_prices():
    res = requests.get('http://m.tank-ono.cz/cz/index.php?page=cenik')
    if (res.status_code != 200):
        exit(1)

    soup = BeautifulSoup(res.content, 'html.parser')
    text = soup.select('div.divprgw') + soup.select('div.divprbw')
    products = []
    for i in text:
        name = i.get_text().strip()
        if len(name) > 2:
            name = name.lower().capitalize()
        products.append(name + ': ' + '%.2f' % (int(i.findNextSibling('div').get_text())/100))
    print('[ONO] ' + ', '.join(products))

def makro_prices():
    res = requests.get('https://www.makro.cz/prodejny/brno',
    headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0', 'Accept': '*/*'})
    if (res.status_code != 200):
        exit(1)

    soup = BeautifulSoup(res.content, 'html.parser')
    text = soup.select('div.price')
    products = []
    for i in text:
        products.append(i.select_one('div.field-name').get_text() + ': ' + i.select_one('div.field-price').get_text())
    print('[Makro Brno] ' + ', '.join(products))

# stupid lat/lon parser
# expects format from eurooil api:
# 48°46'44.016"N or 16°41'37.987"E
def parse_gps_string(string):
    try:
        parts = re.findall(r'\d+(?:[.,]\d+)?', string.strip())
        if parts:
            parts = [float(part.replace(',', '.')) for part in parts]
            return parts[0] + parts[1] / 60 + parts[2] / 3600
        else:
            raise ValueError()
    except:
        return None

# Parse commandline arguments
parser = argparse.ArgumentParser(description='Eurooil prices checker.')
parser.add_argument('--location', help='Location to search for nearest station', nargs='+', default='')
parser.add_argument('--update', action='store_const', const=True, default=False,
                    help='Update data from Eurooil web')
parser.add_argument('--update-stations', action='store_const', const=True, default=False,
                    help='Update station data from Eurooil web')
args = parser.parse_args()

# convert input location to single string
input_location_raw = " ".join(args.location).strip()
# normalize input location
input_location = unicodedata.normalize('NFKD', input_location_raw).encode('ascii','ignore').decode('ascii').lower()

# Set default location if none is given
if len(input_location) == 0:
    input_location = 'opustena'

# Handle ONO special case
if input_location == 'ono':
    ono_prices()
    exit(0)
elif input_location == 'makro':
    makro_prices()
    exit(0)

# Use cache to read data if possible
s_cache = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../cache/stations.json')
stations = None
if not args.update_stations:
    try:
        with open(s_cache) as f:
            stations = json.load(f)
    except:
        pass

cache = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../cache/phm.json')
data = None
if not args.update:
    try:
        with open(cache) as f:
            data = json.load(f)
    except:
        pass

# When cache is not available or an update was requested, read from API
if not stations:
    res = requests.get('https://srdcovka.eurooil.cz/api/verejne/cerpaci-stanice',
        headers={'User-Agent': 'Ktor client'}
    )
    if (res.status_code != 200):
        exit(1)

    stations = json.loads(res.content)
    with open(s_cache, 'w+') as f:
        json.dump(stations, f)

if not data:
    res = requests.get('https://srdcovka.eurooil.cz/api/verejne/ceniky',
        headers={'User-Agent': 'Ktor client'}
    )
    if (res.status_code != 200):
        exit(1)

    data = json.loads(res.content)
    with open(cache, 'w+') as f:
        json.dump(data, f)

station = None
# Try to find exact station based on the name of location
for s in stations['data']:
    if input_location in unicodedata.normalize('NFKD', s['nazev']).encode('ascii', 'ignore').decode('ascii').lower():
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
        for s in stations['data']:
            s_lat = parse_gps_string(s['gprsDelka'])
            s_lon = parse_gps_string(s['gprsSirka'])
            if (s_lat and s_lon):
                s_distance = distance.distance(
                    (s_lat, s_lon),
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
for product in station['produkty']:
    products[product['ean']] = product['nazev']

# Get prices
prices = dict()
for price in data['data']:
    if station['cerpaciStaniceIID'] == price['cerpaciStaniceIID']:
        prices[price['ean']] = price['prodejniCena']

prices = dict(sorted(prices.items(), key=lambda i: int(i[0])))

# Print
print('[{station_name}] {prices}'.format(
    station_name=station['nazev'],
    prices=', '.join([products[k] + ": " + '%.2f' % prices[k] for k in prices if k in products]))
)
