#!/usr/bin/env python3

import sys
import json
from tabulate import tabulate
from collections import OrderedDict

table = []

for line in sys.stdin:
    if not '{' in line:
        continue
    d = json.loads(line, object_pairs_hook=OrderedDict)
    if 'Action' in d:
        a = '🍺' if 'added' in d['Action'] else '🚫'
        del d['Action']
    else:
        a = '🍺'

    d['*'] = a
    d.move_to_end('*', last=False)
    table  = [d] + table

print(tabulate(table, headers='keys', tablefmt="simple"))
