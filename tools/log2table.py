#!/usr/bin/env python3

import sys
import json
from tabulate import tabulate
from collections import OrderedDict

bars = {
    'op': 'Ochutnávková pivnice',
    'mw': 'Malt Worm',
    'craft': 'Craftbeer bottle shop & bar'
}

table = []

for line in sys.stdin:
    if not '{' in line:
        continue
    d = json.loads(line, object_pairs_hook=OrderedDict)
    d['Pivnice'] = bars[d['Pivnice']]
    table  = [d] + table

print(tabulate(table, headers='keys'))
