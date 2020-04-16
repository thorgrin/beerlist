#!/bin/bash

CWD=`dirname "$(readlink -f "$0")"`

# Read config file if it exists
#config="$(readlink -f ~/.config/beerbot.conf)"
config="$(readlink -f /etc/beerbot.conf)"
if [ -f "$config" ]; then
	source $config
fi

if [ -z "$UNTAPPD_USERS" -o -z "$UNTAPPD_IRC_NICKS" ]; then
	# No users to update
	exit 1
fi

users=($UNTAPPD_USERS)
irc_nicks=($UNTAPPD_IRC_NICKS)
if [ ${#users[*]} -ne ${#irc_nicks[*]} ]; then
	# Different array lengths
	exit 2
fi

for index in ${!users[*]}; do
	# Get update from Untappd
	diff=`${CWD}/../parsers/uuparser.py "${users[$index]}" "${irc_nicks[$index]}"`
	if [ "$?" -ne 0 ]; then
		# Skip further processing on error
		continue;
	fi

	# Log the new beer
	if [ -n "$diff" ]; then
		# No log for now
		# echo "$diff" >> "${CWD}/../log/untappdlog.json"

		if [ ! -f "${IRC_DIR}/${IRC_SERVER}/${IRC_CHANNEL}/out" ]; then
			echo "/j ${IRC_CHANNEL}" > "${IRC_DIR}/${IRC_SERVER}/in"
			sleep 1
		fi
		# Push it to IRC
		echo "$diff" > "${IRC_DIR}/${IRC_SERVER}/${IRC_CHANNEL}/in"
	fi
done
