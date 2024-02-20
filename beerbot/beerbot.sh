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
	#pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2} <([^ ]+)> !([a-z]+)$'
	pattern='^[0-9]+ <([^ ]+)> !([a-z]+)[[:space:]]*([a-žA-Ž0-9[:space:]]+)?$'
	[[ $line =~ $pattern ]]
	nick=${BASH_REMATCH[1]}
	bar=${BASH_REMATCH[2]}
	param=${BASH_REMATCH[3]}

	if [ -z $bar ]; then
		pattern='^[0-9]+ <([^ ]+)> (.*?[[:space:]]+|)(1[0-9]{3}!+).*?$'
		[[ $line =~ $pattern ]]
		if [ -z ${BASH_REMATCH[3]} ]; then
			continue
		fi
		nick=${BASH_REMATCH[1]}
		bar='_salina_'
		param=${BASH_REMATCH[3]}
	fi

	if [ -z $bar ]; then
		continue
	fi

	case $bar in
		op|mw|craft|fa|jbm|pa|bg|dno)
			# Update cache if necessary
			cache="${CWD}/../cache/$bar.json"
			if test `find "$cache" -mmin +${BEERBOT_CACHE_UPDATE}`; then
				${CWD}/../tools/update_cache.sh $bar
			fi

			cat "$cache" | ${CWD}/../tools/json2titles.py > "${CHANNEL_DIR}/in"
			;;
		korona)
			today=`date --date="today" +%Y-%m-%d`
			yesterday=`date --date="yesterday" +%Y-%m-%d`
			last_week=`date --date="8 days ago" +%Y-%m-%d`
			overview=`curl --compressed -s "https://onemocneni-aktualne.mzcr.cz/api/v3/zakladni-prehled/$today?apiToken=$KORONA_TOKEN" -H 'accept: application/json'`
			active=`echo $overview | jq '.aktivni_pripady'`
			tests_overall=`echo $overview| jq '.provedene_testy_celkem'`
			tests_overall_atg=`echo $overview| jq '.provedene_antigenni_testy_celkem'`
			tests_yesterday=`echo $overview| jq '.provedene_testy_vcerejsi_den'`
			tests_yesterday_atg=`echo $overview| jq '.provedene_antigenni_testy_vcerejsi_den'`
			hospitalised=`echo $overview | jq '.aktualne_hospitalizovani'`
			active=`echo $overview | jq '.aktivni_pripady'`
			infected_overall=`echo $overview | jq '.potvrzene_pripady_celkem'`
			infected_yesterday=`echo $overview | jq '.potvrzene_pripady_vcerejsi_den'`
			cured=`echo $overview | jq '.vyleceni'`
			deceased=`echo $overview | jq '.umrti'`

			reinfections=`curl --compressed -s "https://onemocneni-aktualne.mzcr.cz/api/v3/nakazeni-reinfekce?page=1&itemsPerPage=100&datum%5Bbefore%5D=$yesterday&datum%5Bafter%5D=$last_week&apiToken=$KORONA_TOKEN" -H 'accept: application/json'`
			reinfections_yesterday=`echo "$reinfections" | jq '.[] | select (.datum == "'$yesterday'") | .nove_reinfekce'`
			reinfections_7d_ago=`echo "$reinfections" | jq '.[] | select (.datum == "'$last_week'") | .nove_reinfekce'`
			infected_7d_ago=`echo "$reinfections" | jq '.[] | select (.datum == "'$last_week'") | .nove_pripady'`
			infected_week_diff=`echo "$infected_yesterday $infected_7d_ago" | awk '//{printf("%+d", $1 - $2)}'`
			reinfections_week_diff=`echo "$reinfections_yesterday $reinfections_7d_ago" | awk '//{printf("%+d", $1 - $2)}'`
			positive_tests=`echo "scale=2; 100 * ($infected_yesterday + $reinfections_yesterday) / $tests_yesterday" | bc`

			detailed_yesterday=`curl --compressed -s "https://onemocneni-aktualne.mzcr.cz/api/v3/nakazeni-vyleceni-umrti-testy/$yesterday?apiToken=$KORONA_TOKEN" -H 'accept: application/json'`
			cured_yesterday=`echo $detailed_yesterday | jq '.prirustkovy_pocet_vylecenych'`
			deceased_yesterday=`echo $detailed_yesterday | jq '.prirustkovy_pocet_umrti'`


			# There are lots of items, but no more than 10000, which seems to be a limit
			vaccinations=`curl --compressed -s "https://onemocneni-aktualne.mzcr.cz/api/v3/ockovani?page=1&datum%5Bbefore%5D=$yesterday&datum%5Bafter%5D=$yesterday&apiToken=$KORONA_TOKEN&itemsPerPage=10000" -H 'accept: application/json'`
			vaccinations_yesterday=`echo "$vaccinations" | jq '[.[] | select (.datum == "'$yesterday'") | .celkem_davek] | add'`
			vaccinations_first_yesterday=`echo "$vaccinations" | jq '[.[] | select (.datum == "'$yesterday'") | .prvnich_davek] | add'`
			vaccinations_second_yesterday=`echo "$vaccinations" | jq '[.[] | select (.datum == "'$yesterday'") | .druhych_davek] | add'`
			vaccinations_third_yesterday=$((${vaccinations_yesterday} - ${vaccinations_first_yesterday} - ${vaccinations_second_yesterday}))
# 			vaccinations_overall=`echo "$vaccinations" | jq -s '[.[].celkem_davek] | add'`
# 			vaccinations_first_overall=`echo "$vaccinations" | jq -s '[.[].prvnich_davek] | add'`
# 			vaccinations_second_overall=`echo "$vaccinations" | jq -s '[.[].druhych_davek] | add'`
# 			vaccinations_third_overall=$((${vaccinations_overall} - ${vaccinations_first_overall} - ${vaccinations_second_overall}))
			vaccinations_overall=`echo $overview | jq '.vykazana_ockovani_celkem'`

			echo "active: $active | infected: $infected_overall (+$infected_yesterday/$reinfections_yesterday [1d], $infected_week_diff/$reinfections_week_diff [1w diff]) | tested (PCR/ATG): $tests_overall/$tests_overall_atg (yesterday +$tests_yesterday/$tests_yesterday_atg, $positive_tests% positive) | temporarily feeling better: $cured (+$cured_yesterday) | deceased: $deceased (+$deceased_yesterday) | hospitalised: $hospitalised | vaccinated: $vaccinations_overall (+$vaccinations_first_yesterday/$vaccinations_second_yesterday/$vaccinations_third_yesterday)" > "${CHANNEL_DIR}/in"
			;;
		nehody)
			curl --compressed -s https://d2g9cow0nr2qp.cloudfront.net/?q=$(echo -n "{ 'from': `date --date='00:00 yesterday' '+%s'`, 'to': `date --date='23:59:59 yesterday' '+%s'`, 'all': 'true' }" | base64) | jq '.["ČR"] | "accidents: " + (.PN | tostring) + " | dead: " + (.M | tostring) + " | serious injury: " + (.TR | tostring) + " | light injury: " + (.LR | tostring)' | xargs echo > "${CHANNEL_DIR}/in"
			;;
		btc | eth)
			#curl -s 'https://www.bitstamp.net/api-internal/market/prices/?step=60&start='`date -u --date="day ago" +%Y-%m-%dT%H:%M:%S.000Z`'&end='`date -u +%Y-%m-%dT%H:%M:%S.999Z`'&pairs=btcusd'  | jq -r '.data[0]["price"] + " " +  .data[0]["history"][0]["open"] + " " + .data[0]["history"][-60]["open"]' | awk '//{printf("BTC: $%.2f | %+.2f%% (1h) | %+.2f%% (24h)\n", $1, 100*$1/$3-100, 100*$1/$2-100)}' > "${CHANNEL_DIR}/in"
			curl --compressed -s https://www.bitstamp.net/api-internal/price-history/${bar}usd/ | jq -r '.data["latest"]["price"] + " " + (.data["prices"]["hour"]["percent_change"]|tostring) + " " + (.data["prices"]["day"]["percent_change"]|tostring) + " " + (.data["prices"]["week"]["percent_change"]|tostring)' | awk '//{printf("%s: $%.2f | %+.2f%% (1h) | %+.2f%% (1d) | %+.2f%% (1w)\n", toupper("'$bar'"), $1, $2, $3, $4)}' > "${CHANNEL_DIR}/in"
			;;
		event | events)
			curl --compressed -s 'https://events.gcm.cz/api.php?action=events&from='`date --date='today' +%Y-%m-%d`'&to='`date --date='next month' +%Y-%m-%d`'&lat=49.1950602&lon=16.6068371&radius=15&requestId=1' | jq -r '.events | reduce .[] as $event (""; . + "(" + $event.gcid + ") " + $event.name + "|" + $event.date_from + "\n" )' | head -n-1 | head -n 4 | while IFS='|' read e d; do echo -n "$e ["`date --date="$d" "+%a %d %b %Y %R"`"] | "; done | sed 's/| $/\n/g' > "${CHANNEL_DIR}/in"
			;;
		phm)
			# Update cache if necessary
			cache="${CWD}/../cache/phm.json"
			scache="${CWD}/../cache/stations.json"
			update=""
			if test `find "$cache" -mmin +10 2> /dev/null`; then
				update="--update"
			fi
			if test `find "$scache" -mtime +1 2> /dev/null`; then
				update="${update} --update-stations"
			fi

			${CWD}/../tools/phm.py $update --location "$param" > "${CHANNEL_DIR}/in"
			[[ "$?" -ne 0 ]] && echo "$nick: sorry jako" > "${CHANNEL_DIR}/in"
			;;
		xkcd)
			curl -s https://xkcd.com/ | grep 'Permanent link to this comic' | sed 's#.*"\(https://xkcd.com/[^"]\+\)".*#\1#g' > "${CHANNEL_DIR}/in"
			;;
		_salina_)
			if [ $RANDOM -lt 28000 ]; then
				echo "$nick: jdi pryc" > "${CHANNEL_DIR}/in"
			else
				echo "$nick: /r/unexpectedfactorial" > "${CHANNEL_DIR}/in"
			fi
			;;
		*)
			echo "$nick: tvoje stara je $bar $param" > "${CHANNEL_DIR}/in"
			;;
	esac
done
