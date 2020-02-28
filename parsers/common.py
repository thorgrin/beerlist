import requests
import sys
from tabulate import tabulate
from typing import List

def download_html(url: str) -> str:
	try: 
		res = requests.get(url, headers={'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
	except requests.exceptions.RequestException as e:
		print('Exception was caught while reading from \''+ url + '\': ' + str(e), file=sys.stderr);
		return ''
	res.encoding = 'utf-8'
	return res.text

def parser_output(beers: List[List[str]], headers: List[str], args: List[str]) -> None:
	if beers:
		if len(args) > 1 and args[1] == 'json':
			print(json.dumps({'headers': headers, 'beers': beers}, ensure_ascii=False))
		else: 
			print(tabulate(beers, headers=headers))
