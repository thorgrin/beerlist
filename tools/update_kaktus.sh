#!/bin/bash

CWD=`dirname "$(readlink -f "$0")"`

# Read config file if it exists
#config="$(readlink -f ~/.config/beerbot.conf)"
config="$(readlink -f /etc/beerbot.conf)"
if [ -f "$config" ]; then
	source $config
fi

if [ -z "$KAKTUS_NOTIFY" ]; then
	# No users to notify
	exit 1
fi

dobijecka=`${CWD}/kaktus_dobijecka.py`

if [ "$?" -eq 0 -a -n "$dobijecka" ]; then
	if [ ! -f "${IRC_DIR}/${IRC_SERVER}/${IRC_CHANNEL}/out" ]; then
		echo "/j ${IRC_CHANNEL}" > "${IRC_DIR}/${IRC_SERVER}/in"
		sleep 1
	fi
	# Push it to IRC
	echo "$KAKTUS_NOTIFY: $dobijecka" > "${IRC_DIR}/${IRC_SERVER}/${IRC_CHANNEL}/in"
fi

