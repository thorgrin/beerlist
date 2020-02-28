#!/usr/bin/env python3

import sys
import json
from tabulate import tabulate
from collections import OrderedDict

beers = []
for line in sys.stdin:
	data = json.loads(line)
	beers = beers + list(map(lambda x: OrderedDict(zip(data['headers'], x)), data['beers']))
	beers = beers + [{}]
    
print(tabulate(beers, headers='keys', tablefmt="simple"))
