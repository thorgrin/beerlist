#!/bin/bash

CWD=`dirname "$(readlink -f "$0")"`

if [ -n "$1" ]; then
	bars="$1"
else
	bars="mw op craft"
fi

for bar in $bars; do
	file_new="${CWD}/../cache/${bar}.new.json"
	file_old="${CWD}/../cache/${bar}.json"

	${CWD}/../parsers/${bar}parser.py json > "$file_new"
	${CWD}/beerdiff.py "$bar" "$file_new" "$file_old" >> "${CWD}/../log/beerlog.json"
	
	mv $file_new $file_old
done
