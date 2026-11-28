#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import common as beerlib

URL = 'https://ochutnavkovapivnice.cz/llms.txt'
SECTION_RE = re.compile(r'^## Právě na čepu[ \t]*\r?$(.*?)(?=^## |\Z)', re.MULTILINE | re.DOTALL)
BEER_RE = re.compile(r'^- \[([^\]]+)\]\([^)]+\):\s*(.+)$', re.MULTILINE)
EPM_RE = re.compile(r'^(\d+(?:[,.]\d+)?)\s*°$')
ALK_RE = re.compile(r'^(\d+(?:[,.]\d+)?)\s*%$')
IBU_RE = re.compile(r'^IBU\s*(\d+)$', re.IGNORECASE)
TAP_RE = re.compile(r'^pípa\s*\d+$', re.IGNORECASE)
LOCATION_RE = re.compile(r'^([^,]+),\s*([^,]+)')


def parse_beer(match):
    name = match.group(1).strip()
    epm = alk = ibu = ''
    text_parts = []

    for part in match.group(2).split(' · '):
        part = part.strip()
        if not part or TAP_RE.match(part) or part.lower() == 'právě naraženo':
            continue
        epm_match = EPM_RE.match(part)
        if epm_match:
            epm = epm_match.group(1)
            continue
        alk_match = ALK_RE.match(part)
        if alk_match:
            alk = alk_match.group(1)
            continue
        ibu_match = IBU_RE.match(part)
        if ibu_match:
            ibu = ibu_match.group(1)
            continue
        text_parts.append(part)

    # Remaining fields are the style followed by "brewery, city, country".
    if len(text_parts) > 1:
        style = ' · '.join(text_parts[:-1])
        location = text_parts[-1]
    else:
        style = text_parts[0] if text_parts else ''
        location = ''

    brewery = city = ''
    location_match = LOCATION_RE.match(location)
    if location_match:
        brewery = location_match.group(1).strip()
        city = location_match.group(2).strip()

    return [name, style, epm, alk, ibu, brewery, city]


text = beerlib.download_html(URL)
if not text:
    exit(-1)

section = SECTION_RE.search(text)
if not section:
    exit(-2)

output = [parse_beer(match) for match in BEER_RE.finditer(section.group(1))]
if not output:
    # No beers on tap is a fatal error (do not overwrite the cache).
    exit(-2)

headers = ['Pivo', 'Typ', 'EPM', 'Alk.', 'IBU', 'Pivovar', 'Město']
beerlib.parser_output(output, headers, 'Ochutnávková pivnice', sys.argv)
