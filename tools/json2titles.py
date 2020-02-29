#!/usr/bin/env python3

import sys
import json

beers = []
for line in sys.stdin:
    data = json.loads(line)
    index = data['headers'].index('Pivo')
    beers += [beer[index] for beer in data['beers']]

print(" | ".join(beers))
