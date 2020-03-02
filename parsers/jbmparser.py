#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
import re, sys
import common as beerlib

html = beerlib.download_html('https://untappd.com/v/jbm-brew-lab-pub/4222393')
if not html:
	exit(-1)

beerlib.process_untappd(html, 'JBM Brew Lab Pub', sys.argv)
