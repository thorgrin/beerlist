#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from xml.etree import ElementTree as ET
import re
import sys
import json
import common as beerlib

if len(sys.argv) != 3:
    print("uuparser requires two arguments: untappd_username irc_nick")
    exit(-1)

cwd = os.path.dirname(os.path.realpath(__file__))
CACHE_FILE = os.path.join(cwd, '../cache/untappd.json')
USER = sys.argv[1]
IRC_NICK = sys.argv[2]

html = beerlib.download_html('https://untappd.com/user/' + USER)
if not html:
    exit(-2)

reg = re.compile('(<div id="main-stream.*?)<script', re.MULTILINE | re.DOTALL)
body = reg.search(html)
if not body:
    exit(-3)

body = body.group(1)
content = re.sub('<script.*?</script>', '', body, flags=re.MULTILINE | re.DOTALL)
content = re.sub('<img.*?>', '', content, flags=re.MULTILINE | re.DOTALL)
content = content.replace('&', '&#038;')
if not content:
    exit(-4)

try:
    with open(CACHE_FILE) as f:
        data = json.load(f)
except Exception:
    data = {}

try:
    page = ET.XML(content + '</div>')
    checkin = page.find('./div[@data-checkin-id]')
    checkin_id = checkin.get('data-checkin-id')
    saved_id = data.get(USER)
    if saved_id is not None and saved_id != checkin_id:
        # user had a good time!
        p = checkin.find('.//p[@class="text"]')
        text = list(p.itertext())
        text = [x.strip() for x in text if x.strip()]
        if len(text) < 5 or text[1].find('drinking') == -1:
            # something fishy
            exit(-5)
        print('Notify: {0} leje {1} (by {2})'.format(IRC_NICK, text[2], text[4]))
    # save data
    if saved_id != checkin_id:
        with open(CACHE_FILE, 'w') as f:
            data[USER] = checkin_id
            json.dump(data, f)

except Exception as e:
    exit(-6)
