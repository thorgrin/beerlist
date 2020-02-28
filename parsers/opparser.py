#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
import re
from tabulate import tabulate
import json
import sys
from common import beer_download_html

html = beer_download_html('http://ochutnavkovapivnice.cz/prave_na_cepu/')
if not html:
	exit(-1)

reg = re.compile('(<table.*</table>)', re.MULTILINE | re.DOTALL)
html = reg.search(html).group(0)
table = ET.XML(html)

rows = iter(table)
headers = [col[0].text for col in next(rows)]
output = []
for row in rows:
	tds = iter(row)
	beer = next(tds)[0][0].text
	values = [beer] + [col.text for col in tds]
	output = output + [values]
	#print(dict(zip(headers, values)))

if len(sys.argv) > 1 and sys.argv[1] == 'json':
	print(json.dumps({'headers': headers, 'beers': output}, ensure_ascii=False))
else: 
	print(tabulate(output, headers=headers))
