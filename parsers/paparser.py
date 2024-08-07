#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys
import common as beerlib
from bs4 import BeautifulSoup


html = beerlib.download_html('https://www.pivniambasada.cz/')
if not html:
    exit(-1)

soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table', attrs={'class':'listek_tab'})

items = []
for item in table.find_all('td', attrs={'class':['listek_tab_nazev', 'listek_tab_popis', 'listek_tab_nadpis']}):
    if item.text == 'Akce':
        break
    items.append(item.text)

beer_list = []
others_list = []

for i in range(0, len(items)):
    if i % 2:
        others_list.append(items[i])
    else :
        beer_list.append(items[i])

brewery_list = []
city_list = []
type_list = []
alc_list = []

pattern = re.compile(r"(?P<alc>[\d,]+%)\s+(?:alc\.)?(?:\s+piv\.\s+)?(?P<brewery>.*?)(?:,\s+(?P<location>.*?))?,\s+(?P<type>.+)")

for i in range(0, len(others_list)):
    match = pattern.match(others_list[i])
    if match:
        alc = match.group('alc')
        brewery = match.group('brewery')
        location = match.group('location')
        beer_type = match.group('type')
    
        brewery_list.append(brewery)
        city_list.append(location)
        type_list.append(beer_type)
        alc_list.append(alc)

output = []
headers = ['Pivo', 'Typ', 'Alk.', 'Pivovar', 'Město']
for i in range(0, len(beer_list)):
    p = []
    p.append(beer_list[i])
    p.append(type_list[i])
    p.append(alc_list[i])
    p.append(brewery_list[i])
    p.append(city_list[i])
    output.append(p)

beerlib.parser_output(output, headers, 'Pivní Ambasáda', sys.argv)
