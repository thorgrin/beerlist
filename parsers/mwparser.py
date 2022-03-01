#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys
from bs4 import BeautifulSoup
import common as beerlib

html = beerlib.download_html('https://maltworm.cz/dnes-na-cepu/')
if not html:
	exit(-1)

soup = BeautifulSoup(html, 'html.parser')

# Fin all articles that are not under a hidden section
displayed = soup.select('section:not(.elementor-hidden-desktop) section article')

headers = ['Pivo', 'Typ', 'EPM', 'Alk.', 'IBU', 'Pivovar', 'Město']
output = []
for article in displayed:
	beer = article.find('p', attrs={'class': ['elementor-heading-title', 'elementor-size-default']})
	info = article.find_all('span', attrs={'class': 'elementor-icon-list-text'})
	# print(info)
	info = iter(info)
	if not info:
		continue
	values = [beer.text] + ["".join(i.text) for i in info]

	# get rid of 'IBU:' prefix
	ibu_pos = headers.index('IBU')
	if (len(values) > ibu_pos):
		values[ibu_pos] = values[ibu_pos].replace('IBU: ', '')

	output = output + [values]

beerlib.parser_output(output, headers, 'Malt Worm', sys.argv)