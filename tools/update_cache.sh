#!/bin/bash

CWD=`dirname "$(readlink -f "$0")"`

# Read config file if it exists
#config="$(readlink -f ~/.config/beerbot.conf)"
config="$(readlink -f /etc/beerbot.conf)"
if [ -f "$config" ]; then
	source $config
fi

if [ -n "$1" ]; then
	bars="$1"
else
	bars="mw op fa pa bg dno craft kult" # u2pb u2pt | fuck fb
	#bars="mw op jbm fa craft"
fi

for bar in $bars; do
	file_new="${CWD}/../cache/${bar}.new.json"
	file_old="${CWD}/../cache/${bar}.json"

	# Get update from the bar
	${CWD}/../parsers/${bar}parser.py json > "$file_new"
	if [ "$?" -ne 0 ]; then
		# Skip further processing on error
		continue;
	fi

	# Compute the diff
	add_diff=`${CWD}/beerdiff.py "$file_new" "$file_old" "added"`
	del_diff=`${CWD}/beerdiff.py "$file_old" "$file_new" "removed"`

	# Log the new beers
	if [ -n "$del_diff" ]; then
		echo "$del_diff" >> "${CWD}/../log/beerlog.json"
	fi
	if [ -n "$add_diff" ]; then
		echo "$add_diff" >> "${CWD}/../log/beerlog.json"
	fi

	# Push the new beers to IRC
	if [ "x$IRC_PUSH" = "xyes"  -a -n "$add_diff" ]; then
		if [ ! -f "${IRC_DIR}/${IRC_SERVER}/${IRC_CHANNEL}/out" ]; then
			echo "/j ${IRC_CHANNEL}" > "${IRC_DIR}/${IRC_SERVER}/in"
			sleep 1
		fi
		# Make the diff nicer and push it to IRC
		echo "$add_diff" | ${CWD}/diff2notify.py > "${IRC_DIR}/${IRC_SERVER}/${IRC_CHANNEL}/in"
	fi

	cat "$file_new" > "$file_old"
	rm "$file_new"
done
