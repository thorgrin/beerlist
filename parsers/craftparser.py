#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, sys, re
from xml.etree import ElementTree as ET
from tabulate import tabulate
from common import beer_download_html

# first we need the post ID
html = beer_download_html('https://m.facebook.com/Craftbeerbottleshopbar/')
if not html:
	exit(-1)
# first we need the post ID

reg = re.compile('(<body.*</body>)', re.MULTILINE | re.DOTALL)
body = reg.search(html).group(0)

page = ET.XML(body)
articles = page.findall(".//div[@role='article']")


# Look at all articles until some beers are found
for article in articles:
	data = json.loads(article.attrib['data-ft'])
	post_url = "https://m.facebook.com/story.php?story_fbid=%s&id=%s" % (data['top_level_post_id'], data['content_owner_id_new'])

	# Okay, let's get the post
	post_html = beer_download_html(post_url)
	if not post_html:
		continue
	body = reg.search(post_html).group(0)

	# Hope that last paragraph of post contains beers
	page = ET.XML(body)

	# The relevant div has class either 'msg', 'cf' or 'bz'
	beers = page.find(".//div[@class='msg']")
	if not beers:
		beers = page.find(".//div[@class='cf']")
	if not beers:
		beers = page.find(".//div[@class='bz']")

	# Nothing? Give up
	if not beers:
		continue

	beers = list(beers.itertext())

	# Hope that the beer list format is the same
	headers = ['Pivo', 'Alk.', 'Pivovar', 'Typ']
	output = []
	for line in beers:
		# Black Label #4 8,1% (Raven, Wild Ale)
		m = re.match(' *(.+) ([0-9,\.]+%) \(([^,]+), ?(.+)\)', line)
		if not m:
			# Zlaté Prasátko 6,5%
			m = re.match(' *(.+) ([0-9,\.]+%)', line)
		if m:
			output = output + [m.groups()]

	if output:
		if len(sys.argv) > 1 and sys.argv[1] == 'json':
			print(json.dumps({'headers': headers, 'beers': output}, ensure_ascii=False))
		else:
			print(tabulate(output, headers=headers))
		break
