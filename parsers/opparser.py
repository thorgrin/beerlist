#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
import re, sys
import common as beerlib

html = beerlib.download_html('http://ochutnavkovapivnice.cz/prave_na_cepu/')
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

beerlib.parser_output(output, headers, sys.argv)
