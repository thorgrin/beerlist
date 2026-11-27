#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
import common as beerlib

URL = 'https://mozek.pivovarstern.cz/menu'
PIVNICE = 'U dvou přátel'

# The menu is server-rendered as a Next.js streamed RSC payload, not as
# ordinary HTML. The beer rows are delivered in self.__next_f.push(...) calls.
FLIGHT_RE = re.compile(r'self\.__next_f\.push\(\[1,\s*("(?:[^"\\]|\\.)*")\]')
BEER_RE = re.compile(r'(?="aria-label":"Kohout\s*\d+")')
JSON_STRING = r'((?:[^"\\]|\\.)*)'
NAME_RE = re.compile(r'"className":"[^"]*\bnazev-piva\b[^"]*","children":"' + JSON_STRING + '"')
STYLE_RE = re.compile(r'"className":"[^"]*\btext-sm font-medium text-green-700\b[^"]*","children":"' + JSON_STRING + '"')
EPM_RE = re.compile(r'(\d{1,2})\s*%\s*$')


def decode(value):
    return json.loads('"' + value + '"')


def extract_string(pattern, text):
    match = pattern.search(text)
    return decode(match.group(1)) if match else ''


html = beerlib.download_html(URL)
if not html:
    exit(-1)

payload = ''.join(json.loads(match.group(1)) for match in FLIGHT_RE.finditer(html))
beers = BEER_RE.split(payload)

output = []
for beer in beers[1:]:
    name = extract_string(NAME_RE, beer)
    if not name:
        continue

    style = extract_string(STYLE_RE, beer)

    epm_match = EPM_RE.search(name)
    epm = epm_match.group(1) if epm_match else ''

    # Names normally start with the brewery (e.g. "Stern Ponávka 10%").
    brewery_match = re.match(r'^(\S+)\s+\S', name)
    brewery = ''
    if brewery_match and brewery_match.group(1)[0].isupper():
        brewery = brewery_match.group(1)

    output.append([name, style, epm, brewery])

if not output:
    # No beers on the page is a fatal error (do not overwrite the cache).
    exit(-2)

headers = ['Pivo', 'Typ', 'EPM', 'Pivovar']
beerlib.parser_output(output, headers, PIVNICE, sys.argv)
