#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from xml.etree import ElementTree as ET
import re
from tabulate import tabulate
import json
import sys

res = requests.get('https://untappd.com/v/fa-bar-oranzova/1728532', headers={'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
res.encoding = 'utf-8'
html = res.text

reg = re.compile('(<body.*</body>)', re.MULTILINE | re.DOTALL)
body = reg.search(html).group(0)

# Get rid of scripts and select only the divs with beer
content = re.sub('<script.*?</script>', '', body, flags=re.MULTILINE | re.DOTALL)
content = re.sub('<h4>Pivotéka / Bottleshop.*', '', content, flags=re.MULTILINE | re.DOTALL)
beers = re.findall('(<div class="beer-details">.*?</span>)', content, re.MULTILINE | re.DOTALL)

headers = ['Pivo', 'Typ', 'Alk.', 'IBU', 'Pivovar']
output = []
for row in beers:
	row = row.replace('&', '&#038;')
	# Add tags to get valid XML
	beer = ET.XML(row + '</h6></div>')
	title = beer.findtext('h5/a')
	title = re.sub('^[0-9]+\. ', '', title)
	style = beer.findtext('h5/em')
	brewery = beer.findtext('h6/span/a')
	properties = beer.findtext('h6/span')
	# 6.2% ABV • N/A IBU •
	m = re.match('(.+) ABV • (.+) IBU', properties)
	if m:
		alk = m.groups()[0] if not 'N/A' in m.groups()[0] else ''
		ibu = m.groups()[1] if not 'N/A' in m.groups()[1] else ''
	else:
		alk = ''
		ibu = ''
	output = output + [[title, style, alk, ibu, brewery]]

if len(sys.argv) > 1 and sys.argv[1] == 'json':
	print(json.dumps({'headers': headers, 'beers': output}, ensure_ascii=False))
else:
	print(tabulate(output, headers=headers))
