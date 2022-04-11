#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, re, json
from bs4 import BeautifulSoup
import common as beerlib

curl_ua = 'curl/7.54.1'

# first we need the post ID
data = beerlib.download_html('https://m.facebook.com/page_content_list_view/more/?page_id=1871132519814729&start_cursor=10000&num_to_fetch=10&surface_type=timeline', curl_ua)
if not data:
	exit(-1)

data = re.sub(r'for \(;;\);', '', data)

data_json = json.loads(data)
data_html = data_json['actions'][0]['html']

# print(data_html)

# find photo ulrs
photos = re.findall('href="(/Craftbeerbottleshopbar/photos/a.[0-9]+/[0-9]+/\?type=3)', data_html)

# Look at all photo texts
for photo in photos:
	# Okay, let's get the photo
	post_html = beerlib.download_html('https://m.facebook.com/' + photo, curl_ua)
	if not post_html:
		continue

	# print(post_html)
	soup = BeautifulSoup(post_html, 'html.parser')

	# Convert br to \n
	for br in soup.find_all('br'):
		br.replace_with('\n')

	# Find div with text
	text = soup.select('div#MPhotoContent div.msg div')

	# Get plaintext
	text = text[0].get_text()
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
		else:
			# No niin 6,4% (Tanker) - DDH IPA
			m = re.match(' *(.+?)(?: -)? +([0-9,\.]+%) +\(([^\)]+)\) - ?(.+)?', line)
			if m:
				beer = list(m.groups())
				# Empty EPM
				beer.insert(1, "")

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
