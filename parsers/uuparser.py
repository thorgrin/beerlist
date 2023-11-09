#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from xml.etree import ElementTree as ET
import re
import sys
import json
import common as beerlib


def extract_text(checkin):
    p = checkin.find('.//p[@class="text"]')
    text = list(p.itertext())
    text = [x.strip() for x in text if x.strip()]
    return None if len(text) < 5 or text[1].find('drinking') == -1 else text


def extract_rating(checkin):
    div = checkin.find('.//div[@data-rating]')
    if div is not None:
        return div.get('data-rating')
    return None


def extract_serving(checkin):
    p = checkin.find('.//p[@class="serving"]')
    span = None
    if p is not None:
        span = p.find('.//span')
    if span is not None:
        return span.text.strip().lower()
    return None


def extract_serving_from_checkin(user, id):
    html = beerlib.download_html('https://untappd.com/user/{0}/checkin/{1}'.format(user, id))
    if not html:
        exit(-20)

    reg = re.compile('(<p class="serving">.*?</p>)', re.MULTILINE | re.DOTALL)
    p = reg.search(html)
    if not p:
        exit(-21)

    p = re.sub('<img.*?>', '', p.group(1), flags=re.MULTILINE | re.DOTALL)
    checkin = ET.XML('<div>' + p + '</div>')
    return extract_serving(checkin)


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
    saved_id = data.get(USER)
    page = ET.XML(content + '</div>')
    checkins = page.findall('./div[@data-checkin-id]')
    if len(checkins) == 0:
        exit(-5)

    latest_check = checkins[0]
    latest_id = latest_check.get('data-checkin-id')
    if saved_id is not None and saved_id != latest_id:
        prev_idx = -1
        for idx, checkin in enumerate(checkins):
            if saved_id == checkin.get('data-checkin-id'):
                prev_idx = idx
                break
        if prev_idx == -1:
            # 5+ beers in an update interval? what a day! notify last beer only
            prev_idx = 1

        additional = []
        for i in range(1, prev_idx):
            text = extract_text(checkins[i])
            if text is None:
                exit(-6)
            output = '{0} (by {1})'.format(text[2], text[4])
            rating = extract_rating(checkins[i])
            if rating is not None:
                output += ' :: Hodnoceni: ' + rating
            additional.append(output)

        output = ''
        text = extract_text(latest_check)
        if text is None:
            exit(-7)

        serving = extract_serving(latest_check)
        if serving is None:
            serving = extract_serving_from_checkin(USER, latest_id)

        action = 'leje'
        if serving == 'draft':
            action = 'cepuje do sebe'
        elif serving == 'bottle':
            action = 'cumi do prazdne flasky od'
        elif serving == 'can':
            action = 'je na plech z'
        elif serving == 'taster':
            action = 'ucucava neci'

        if len(text) >= 7 and text[5] == 'at':
            venue = 'doma' if text[6] == 'Untappd at Home' else 'v ' + text[6]
            output = 'Notify: {0} sedi {1} a {4} {2} (by {3})'.format(IRC_NICK, venue, text[2], text[4], action)
        else:
            output = 'Notify: {0} {3} {1} (by {2})'.format(IRC_NICK, text[2], text[4], action)
        rating = extract_rating(latest_check)
        if rating is not None:
            output += ' :: Hodnoceni: ' + rating
        if len(additional) > 0:
            output += ', v sobe ma uz ' + ', '.join(additional)
        print(output)
    # save data
    if saved_id != latest_id:
        with open(CACHE_FILE, 'w') as f:
            data[USER] = latest_id
            json.dump(data, f)

except Exception as e:
    exit(-8)
