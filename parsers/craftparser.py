#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, re, json
from bs4 import BeautifulSoup
import common as beerlib

curl_ua = 'curl/7.54.1'
request_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}

# first we need the post ID
data = beerlib.download_html('https://www.facebook.com/Craftbeerbottleshopbar/photos', user_agent = curl_ua, headers = request_headers)
if not data:
	exit(-1)

# find photo ulrs
photos = re.findall('href="(https://www.facebook.com/photo.php\?fbid[^"]+type=3)', data)

# Look at all photo texts
for photo in photos:
	# Okay, let's get the photo
	post = beerlib.download_html(photo.replace('&amp;', '&'), user_agent = curl_ua, headers = request_headers)
	if not post:
		continue

	# print(post_html)

	texts = re.findall('"text":"([^"]+)"', post)
	if not texts:
		continue

	text = bytes(texts[0], 'utf-8')
	text = text.decode('unicode-escape')
	beers = text.splitlines()

	# Nothing? Give up
	if not beers:
		continue

	# Hope that the beer list format is the same
	headers = ['Pivo', 'EPM', 'Alk.', 'Pivovar', 'Typ']
	output = []
	for line in beers:
		beer = False
		# Beertime dialogue 14° (Raven) - IPA
		m = re.match(' *(.+?)(?: -)? +([0-9,\.]+°) +\(([^\)]+)\) - ?(.+)?', line)
		if m:
			beer = list(m.groups())
			# Empty Alk.
			beer.insert(2, "")

		if not m:
			# No niin 6,4% (Tanker) - DDH IPA
			m = re.match(' *(.+?)(?: -)? +([0-9,\.]+%) +\(([^\)]+)\) - ?(.+)?', line)
			if m:
				beer = list(m.groups())
				# Empty EPM
				beer.insert(1, "")

		if not m:
			# 1. Clock Hektor 10° Svetlé výčapné
			m = re.match('[0-9]+.? *(.+?)(?: -)? +([0-9,\.]+°) +(.+)?', line)
			if m:
				beer = list(m.groups())
				# Empty Alk
				beer.insert(2, "")
				# We cannot determine brewery
				beer.insert(3, "")

		# if not m:
		# 	# Black Label #4 8,1% (Raven, Wild Ale)
		# 	m = re.match(' *(.+?)(?: -)? +([0-9,\.]+%) +\(([^,]+), ?([^\)]+)\)?', line)
		# if not m:
		# 	# Zlaté Prasátko 6,5%
		# 	m = re.match(' *(.+?)(?: -)? +([0-9,\.]+%)()()', line)
		if beer:
			output = output + [beer]

	if output:
		beerlib.parser_output(output, headers, 'Craftbeer bottle shop & bar', sys.argv)
		exit(0)

# nothing was found
exit(1)
