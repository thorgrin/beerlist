# import requests
import httpx
import sys
import re
import json
from xml.etree import ElementTree as ET
from tabulate import tabulate
from typing import List, Dict

def download_html_http1(url: str, user_agent: str = "", headers: Dict = {}) -> str:
	try:
		if not user_agent:
			user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
		headers['Connection'] = 'keep-alive'
		headers['User-Agent'] = user_agent
		res = requests.get(url, headers=headers)
	except requests.exceptions.RequestException as e:
		print('Exception was caught while reading from \''+ url + '\': ' + str(e), file=sys.stderr);
		return ''
	if res.status_code != 200:
		print('Loading "%s" failed' % url)
		return ''
	res.encoding = 'utf-8'
	return res.text

def download_html(url: str, user_agent: str = "", headers: Dict = {}) -> str:
	client = httpx.Client(http2=True)

	try:
		if not user_agent:
			user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
		headers['Connection'] = 'keep-alive'
		headers['User-Agent'] = user_agent
		res = client.get(url, headers=headers)
	finally:
		client.close()
	if res.status_code != 200:
		print('Loading "%s" failed' % url)
		return ''
	res.encoding = 'utf-8'
	return res.text

def parser_output(beers: List[List[str]], headers: List[str], pivnice: str, args: List[str]) -> None:
	if not beers:
		return

	if len(args) > 1 and args[1] == 'json':
		# Add 'Pivnice' field to json output:
		beers = list(map(lambda x: x + [pivnice], beers))
		headers.append('Pivnice')

		# Print the result as json
		print(json.dumps({'headers': headers, 'beers': beers}, ensure_ascii=False))
	else:
		print(tabulate(beers, headers=headers))

def process_untappd(html: str, pivnice: str, args: List[str]) -> None:
	reg = re.compile('(<body.*</body>)', re.MULTILINE | re.DOTALL)
	body = reg.search(html).group(0)

	# Get rid of scripts and select only the divs with beer
	content = re.sub('<script.*?</script>', '', body, flags=re.MULTILINE | re.DOTALL)
	content = re.sub('<h4>Pivotéka / Bottleshop.*', '', content, flags=re.MULTILINE | re.DOTALL)
	content = re.sub('<h4>Rozlévané | From bottle.*', '', content, flags=re.MULTILINE | re.DOTALL)
	content = re.sub('<h4>\n?Fridge.*', '', content, flags=re.MULTILINE | re.DOTALL)
	beers = re.findall('(<div class="beer-details">.*?</span>)', content, re.MULTILINE | re.DOTALL)

	headers = ['Pivo', 'Typ', 'Alk.', 'IBU', 'Pivovar']
	output = []
	for row in beers:
		row = row.replace('&', '&#038;')
		# Add tags to get valid XML
		beer = ET.XML(row + '</h6></div>')
		title = beer.findtext('h5/a')
		title = re.sub(r'\r?\n|\r', ' ', title).strip()
		title = re.sub(r'^[0-9]+\. ?', '', title).strip()
		style = beer.findtext('h5/em').strip('\n ')
		brewery = beer.findtext('h6/span/a').strip('\n ')
		properties = beer.findtext('h6/span').strip('\n ')
		# 6.2% ABV • N/A IBU •
		m = re.match('(.+) ABV • (.+) IBU', properties)
		if m:
			alk = m.groups()[0] if not 'N/A' in m.groups()[0] else ''
			ibu = m.groups()[1] if not 'N/A' in m.groups()[1] else ''
		else:
			alk = ''
			ibu = ''
		output = output + [[title, style, alk, ibu, brewery]]

	if output:
		parser_output(output, headers, pivnice, args)
	else:
		# Page does not contain any beers, this is a fatal error
		exit(-2)
