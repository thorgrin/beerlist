#!/usr/bin/env python3

import sys
import json
from collections import OrderedDict
from datetime import datetime

if len(sys.argv) != 4:
	print("diff requires four arguments: new.json old.json state (added/removed)")
	exit(-1)

try:
	with open(sys.argv[1]) as file_new:
		data_new = json.load(file_new)
except Exception:
	data_new = {'beers': [], 'headers': []}

try:
	with open(sys.argv[2]) as file_old:
		data_old = json.load(file_old)
except Exception:
	data_old = {'beers': [], 'headers': []}

# compute set difference of tuples (cannot do that with list of lists)
new_set = set(map(tuple, data_new['beers']))
old_set = set(map(tuple, data_old['beers']))
diff = new_set - old_set
# convert back to list of lists
diff = list(map(list, new_set - old_set))
if diff:
	for beer in diff:
		beer_dict = OrderedDict(zip(data_new['headers'], beer))
		beer_dict['Action'] = sys.argv[3]
		beer_dict['Time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
		print(json.dumps(beer_dict, ensure_ascii=False))
