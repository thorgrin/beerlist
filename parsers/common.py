import requests
import sys

def beer_download_html(url: str) -> str:
	try: 
		res = requests.get(url, headers={'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
	except requests.exceptions.RequestException as e:
		print('Exception was caught while reading from \''+ url + '\': ' + str(e), file=sys.stderr);
		return ''
	res.encoding = 'utf-8'
	return res.text
