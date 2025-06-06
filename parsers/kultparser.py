#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import common as beerlib

html = beerlib.download_html('https://untappd.com/v/pivni-kult/12772333')
if not html:
	exit(-1)

beerlib.process_untappd(html, 'Pivní Kult', sys.argv)
