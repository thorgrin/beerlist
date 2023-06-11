#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
import re, sys
import common as beerlib

html = beerlib.download_html('https://untappd.com/v/dno-pytle/2950721')
if not html:
	exit(-1)

beerlib.process_untappd(html, 'Dno pytle', sys.argv)
