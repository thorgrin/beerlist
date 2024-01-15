#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys
import common as beerlib
from bs4 import BeautifulSoup


html = beerlib.download_html('https://www.jedemevpivu.cz/tap-menu/')
if not html:
        exit(-1)

soup = BeautifulSoup(html, 'html.parser')

tables = soup.find_all('table')

output = []

headers = ['Pivo', 'Pivovar', 'Typ', 'EPM']

# TÁBOR
rows = tables[1].find_all('tr')
del(rows[0])
for row in rows:
    values = []
    columns = row.find_all('td')
    pivovar = columns[1].text.strip().title()
    pivo = columns[2].text.strip().title()
    epm = columns[3].text.strip()
    typ = columns[4].text.strip()
    values.append(pivo)
    values.append(pivovar)
    values.append(typ)
    values.append(epm)
    output.append(values)

beerlib.parser_output(output, headers, 'U Dvou přátel Tábor', sys.argv)

