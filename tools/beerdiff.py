#!/usr/bin/env python3

import sys
import json

if len(sys.argv) != 3:
	print("diff requires two arguments: new.json old.json")
	exit(-1)

with open(sys.argv[1]) as file_new:
	data_new = json.load(file_new)

with open(sys.argv[2]) as file_old:
	data_old = json.load(file_old)

new_set = set(map(tuple, data_new['beers']))
old_set = set(map(tuple, data_old['beers']))
diff = new_set - old_set
diff = list(map(list, diff))
if diff:
	for beer in diff:
		print(json.dumps(dict(zip(data_new['headers'], beer)), ensure_ascii=False))
