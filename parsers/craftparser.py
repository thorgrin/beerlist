#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, sys, re, requests
from xml.etree import ElementTree as ET
from tabulate import tabulate

# first we need the post ID
res = requests.get('https://m.facebook.com/Craftbeerbottleshopbar/', headers={'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
res.encoding = 'utf-8'

reg = re.compile('(<body.*</body>)', re.MULTILINE | re.DOTALL)
body = reg.search(res.text).group(0)

page = ET.XML(body)
articles = page.findall(".//div[@role='article']")

# Look at all articles until some beers are found
for article in articles:
	data = json.loads(article.attrib['data-ft'])
	post_url = "https://m.facebook.com/story.php?story_fbid=%s&id=%s" % (data['top_level_post_id'], data['content_owner_id_new'])


	# Okay, let's get the post
	res = requests.get(post_url, headers={'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
	res.encoding = 'utf-8'
	body = reg.search(res.text).group(0)

	# Hope that last paragraph of post contains beers
	page = ET.XML(body)

	# The relevant div has class either 'msg' or 'bz'
	beers = page.find(".//div[@class='msg']")
	if not beers:
		beers = page.find(".//div[@class='bz']")

	# Nothing? Give up
	if not beers:
		continue

	beers = list(beers.itertext())

	# Hope that the beer list format is the same
	headers = ['Pivo', 'EPM', 'Pivovar', 'Typ']
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
