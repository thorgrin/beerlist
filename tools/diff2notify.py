#!/usr/bin/env python3

import sys
import json
from tabulate import tabulate

bars = {
    'op': 'Ochutnávková pivnice',
    'mw': 'Malt Worm',
    'craft': 'Craftbeer bottle shop & bar'
}

headers = ['EPM', 'Alk.', 'IBU']

for line in sys.stdin:
    d = json.loads(line)
    pivovar = 'unknown' if not 'Pivovar' in d else d['Pivovar']
    typ = 'unspecified' if not 'Typ' in d else d['Typ']
    mesto = 'somewhere' if not 'Město' in d else d['Město']
    for h in headers:
        if not h in d or not d[h]:
            d[h] = '--'
    print("Notify: %s (by %s) :: %s :: EPM %s Alk. %s IBU %s :: %s :: %s" % (d['Pivo'], pivovar, typ, d['EPM'], d['Alk.'], d['IBU'], mesto, bars[d['Pivnice']]))
