#!/usr/bin/env python3

import sys
import json

data = json.load(sys.stdin)
index = data['headers'].index('Pivo')
print(" | ".join([beer[0] for beer in data['beers']]))
