#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import common as beerlib

html = beerlib.download_html('https://untappd.com/v/fa-bar-oranzova/1728532')
if not html:
	exit(-1)

beerlib.process_untappd(html, 'F.A. Bar Oranžová', sys.argv)
