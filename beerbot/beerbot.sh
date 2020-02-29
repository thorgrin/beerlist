#!/bin/bash

CWD=`dirname "$(readlink -f "$0")"`

# Read config file if it exists
config="$(readlink -f /etc/beerbot.conf)"
if [ -f "$config" ]; then
        source $config
else
	echo "beerbot config not found" 1>&2
	exit 1
fi

CHANNEL_DIR="${IRC_DIR}/${IRC_SERVER}/${IRC_CHANNEL}"

# Check that the channel exists
if [ ! -f "${CHANNEL_DIR}/out" ]; then
	echo "/j ${IRC_CHANNEL}" > "${IRC_DIR}/${IRC_SERVER}/in"
fi

# Do the main work
tail -n 0 -F "${CHANNEL_DIR}/out"| while read line
do
	pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2} <([^ ]+)> !([a-z]+)$'
	[[ $line =~ $pattern ]]
	nick=${BASH_REMATCH[1]}
	bar=${BASH_REMATCH[2]}
	
	if [ -z $bar ]; then
		continue
	fi

	case $bar in
		op|mw|craft|fa|jbm)
			# Update cache if necessary
			cache="${CWD}/../cache/$bar.json"
			if test `find "$cache" -mmin +${BEERBOT_CACHE_UPDATE}`; then
				${CWD}/../tools/update_cache.sh $bar
			fi
			
			cat "$cache" | ${CWD}/../tools/json2titles.py > "${CHANNEL_DIR}/in"
			;;
		*)
			echo "$nick: wtf?" > "${CHANNEL_DIR}/in"
			;;
	esac
done

