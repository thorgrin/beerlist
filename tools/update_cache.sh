#!/bin/bash

CWD=`dirname "$(readlink -f "$0")"`

for bar in mw op craft; do
	file_new="${CWD}/../cache/${bar}.new.json"
	file_old="${CWD}/../cache/${bar}.json"

	${CWD}/../parsers/${bar}parser.py json > $file_new
	${CWD}/beerdiff.py $file_new $file_old >> ${CWD}/../log/beerlog.json
	
	mv $file_new $file_old
done
