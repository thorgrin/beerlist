#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, re, json
from xml.etree import ElementTree as ET
import common as beerlib

curl_ua = 'curl/7.54.1'

# first we need the post ID
html = beerlib.download_html('https://m.facebook.com/page_content_list_view/more/?page_id=1871132519814729&start_cursor=10000&num_to_fetch=10&surface_type=timeline', curl_ua)
if not html:
	exit(-1)

reg = re.compile('(<p>.*?</p>)')

# find post ids
ids = re.findall('top_level_post_id&quot;:&quot;([0-9]+)', html)

# Look at all articles until some beers are found
for content_id in ids:
	post_url = "https://m.facebook.com/story.php?story_fbid=%s&id=%s" % (content_id, '1871132519814729')
	# print(post_url)

	# Okay, let's get the post
	post_html = beerlib.download_html(post_url, curl_ua)
	if not post_html:
		continue

	paragraphs = reg.findall(post_html)

	# Hope that some paragraph of post contains beers
	for p in paragraphs:
		beers = ET.XML(p)

		# Nothing? Give up
		if not beers:
			continue

		beers = list(beers.itertext())

		# Hope that the beer list format is the same
		headers = ['Pivo', 'Alk.', 'Pivovar', 'Typ']
		output = []
		for line in beers:
			# Black Label #4 8,1% (Raven, Wild Ale)
			m = re.match(' *(.+?)(?: -)? +([0-9,\.]+%) +\(([^,]+), ?([^\)]+)\)?', line)
			if not m:
				# Zlaté Prasátko 6,5%
				m = re.match(' *(.+?)(?: -)? +([0-9,\.]+%)()()', line)
			if m:
				output = output + [list(m.groups())]

		if output:
			beerlib.parser_output(output, headers, 'Craftbeer bottle shop & bar', sys.argv)
			exit(0)

# nothing was found
exit(1)
