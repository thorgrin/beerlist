#!/usr/bin/env python3

import json
import requests
from requests.auth import HTTPBasicAuth

res = requests.post('https://einfo.ceproas.cz/cepro_portal_ws/rest/common/prox/mobileData/',
    auth=HTTPBasicAuth('mobap', 'EWikA2'),
    data='{}',
    headers={'Content-Type': 'application/json; charset=UTF-8'}
)
data = json.loads(res.content)

# Load products
products = dict()
for product in data['Data']['cis_prod_list']:
    products[product['kod_produkt']] = product['nazev_produkt']


# Find Brno Opuštěná station
for station in data['Data']['cs_fix_list']:
    if 'Opuštěná' in station['nazev_kratky']:
        kod_cs = station['kod_cs']
        break

# Get prices
for prices in data['Data']['cs_ceny']:
    if kod_cs == prices['kod_cs']:
        break;

# Print
print('[{station_name}] {prices}'.format(
    station_name=station['nazev_kratky'],
    prices=', '.join([products[p['kod_produkt']] + ": " + '%.2f' % p['cena'] for p in prices['ceny']]))
)