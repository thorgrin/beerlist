#!/usr/bin/env python3

import sys
import json
from tabulate import tabulate

data = json.load(sys.stdin)
print(tabulate(data['beers'], headers=data['headers']))
