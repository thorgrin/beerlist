#!/bin/bash

CWD=`dirname "$(readlink -f "$0")"`

# Read config file if it exists
config="$(readlink -f ~/.config/beerbot.conf)"
if [ -f "$config" ]; then
	source $config
fi

if [ -n "$1" ]; then
	bars="$1"
else
	bars="mw op craft"
fi

for bar in $bars; do
	file_new="${CWD}/../cache/${bar}.new.json"
	file_old="${CWD}/../cache/${bar}.json"

	# Get update from the bar
	${CWD}/../parsers/${bar}parser.py json > "$file_new"

	# Compute the diff
	diff=`${CWD}/beerdiff.py "$bar" "$file_new" "$file_old"`
	
	if [ -z "$diff" ]; then
		cat "$file_new" > "$file_old"
		rm "$file_new"
		continue
	fi

	# Log the new beers
	echo "$diff" >> "${CWD}/../log/beerlog.json"


	# Push the new beers to IRC
	if [ "$IRC_PUSH" == "yes" ]; then
		if [ ! -d "${IRC_DIR}/${IRC_SERVER}/${IRC_CHANNEL}" ]; then
			echo "/j ${IRC_CHANNEL}" > "${IRC_DIR}/${IRC_SERVER}/in"
			sleep 1
		fi
		# Make the diff nicer and push it to IRC
		echo "$diff" | ${CWD}/diff2notify.py > "${IRC_DIR}/${IRC_SERVER}/${IRC_CHANNEL}/in"
	fi

	cat "$file_new" > "$file_old"
	rm "$file_new"
done
