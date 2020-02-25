#!/usr/bin/env python3

import sys
import json
from tabulate import tabulate
from collections import OrderedDict

bars = {
    'op': 'Ochutnávková pivnice',
    'mw': 'Malt Worm',
    'craft': 'Craftbeer bottle shop & bar',
    'jbm': 'JBM Brew Lab Pub'
}

table = []

for line in sys.stdin:
    if not '{' in line:
        continue
    d = json.loads(line, object_pairs_hook=OrderedDict)
    d['Pivnice'] = bars[d['Pivnice']]
    if 'Action' in d:
        a = '🍺' if 'added' in d['Action'] else '🚫'
        del d['Action']
    else:
        a = '🍺'

    d['*'] = a
    d.move_to_end('*', last=False)
    table  = [d] + table

print(tabulate(table, headers='keys', tablefmt="simple"))
