#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys
from xml.etree import ElementTree as ET
import common as beerlib

html = beerlib.download_html('https://maltworm.cz/dnes-na-cepu/')
if not html:
	exit(-1)

reg = re.compile('(<body.*</body>)', re.MULTILINE | re.DOTALL)
body = reg.search(html).group(0)
content = re.sub('<script.*</script>', '', body, flags=re.MULTILINE | re.DOTALL)

table = ET.XML(content)
articles = table.findall(".//article")

headers = ['Pivo', 'Typ', 'EPM', 'Alk.', 'IBU', 'Pivovar', 'Město']
output = []
for article in articles:
	beer = article.find(".//p[@class='elementor-heading-title elementor-size-default']")
	info = article.findall(".//span[@class='elementor-icon-list-text']")
	info = iter(info)
	values = [beer.text] + ["".join(i.itertext()) for i in info]

	# get rid of 'IBU:' prefix
	ibu_pos = headers.index('IBU')
	values[ibu_pos] = values[ibu_pos].replace('IBU: ', '')

	output = output + [values]

beerlib.parser_output(output, headers, 'Malt Worm', sys.argv)
