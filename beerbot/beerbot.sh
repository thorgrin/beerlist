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
		korona)
#			curl -s https://api.apify.com/v2/key-value-stores/K373S4uCFR9W1K8ei/records/LATEST?disableRedirect=true | jq '"active: " + (.active | tostring) + " | infected: " + (.infected | tostring) + " (+" + (.infectedDaily[-1].value | tostring) + "|+" + (.infected - reduce .infectedDaily[].value as $line (0; . + $line) | tostring) + ") | tested: " + (.totalTested | tostring) + " (+" + (.numberOfTestedGraph[-1].value | tostring) + ") | temporarily feeling better: " + (.recovered | tostring) + " | deceased: " + (.deceased | tostring)' | xargs echo > "${CHANNEL_DIR}/in"
#			curl -s https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakazeni-vyleceni-umrti-testy.min.json | jq '"active: " + (.data[-1].kumulativni_pocet_nakazenych - .data[-1].kumulativni_pocet_vylecenych - .data[-1].kumulativni_pocet_umrti | tostring) + " | infected: " + (.data[-1].kumulativni_pocet_nakazenych | tostring) + " (+" + ((.data[-1].kumulativni_pocet_nakazenych - .data[-2].kumulativni_pocet_nakazenych ) | tostring) + ") | tested: " + (.data[-1].kumulativni_pocet_testu | tostring) + " (+" + ((.data[-1].kumulativni_pocet_testu - .data[-2].kumulativni_pocet_testu) | tostring) + ") | temporarily feeling better: " + (.data[-1].kumulativni_pocet_vylecenych | tostring) + " (+" + ((.data[-1].kumulativni_pocet_vylecenych - .data[-2].kumulativni_pocet_vylecenych) | tostring) + ")" + " | deceased: " + (.data[-1].kumulativni_pocet_umrti | tostring) + " (+" + ((.data[-1].kumulativni_pocet_umrti - .data[-2].kumulativni_pocet_umrti) | tostring) + ")"' | xargs echo > "${CHANNEL_DIR}/in"
			overview=`curl -s https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/zakladni-prehled.min.json`
			detailed=`curl -s https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakazeni-vyleceni-umrti-testy.min.json`
			detailed_tests=`curl -s https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/testy.json`
			tests_yesterday_date=`echo $overview | jq '.data[0].provedene_testy_vcerejsi_den_datum'`
			infected_yesterday_date=`echo $overview | jq '.data[0].potvrzene_pripady_vcerejsi_den_datum'`
			tests_overall=`echo $overview| jq '.data[0].provedene_testy_celkem'`
			tests_yesterday=`echo $overview| jq '.data[0].provedene_testy_vcerejsi_den'` # works only after 18:00, data from day before otherwise
			tests_two_days_ago=`echo $detailed | jq '((.data[-2].kumulativni_pocet_testu - .data[-3].kumulativni_pocet_testu))'`
			hospitalised=`echo $overview | jq '.data[0].aktualne_hospitalizovani'`
			active=`echo $overview | jq '.data[0].aktivni_pripady'`
			infected_overall=`echo $overview | jq '.data[0].potvrzene_pripady_celkem'`
			infected_today=`echo $overview | jq '.data[0].potvrzene_pripady_dnesni_den'`
			infected_yesterday=`echo $overview | jq '.data[0].potvrzene_pripady_vcerejsi_den'`
			infected_two_days_ago=`echo $detailed | jq '((.data[-2].kumulativni_pocet_nakazenych - .data[-3].kumulativni_pocet_nakazenych))'`
			cured=`echo $overview | jq '.data[0].vyleceni'`
			cured_yesterday=`echo $detailed | jq '((.data[-1].kumulativni_pocet_vylecenych - .data[-2].kumulativni_pocet_vylecenych))'`
			deceased=`echo $overview | jq '.data[0].umrti'`
			deceased_yesterday=`echo $detailed | jq '((.data[-1].kumulativni_pocet_umrti - .data[-2].kumulativni_pocet_umrti))'`
			tests_first_newest=`echo $detailed_tests | jq '.data[-1].prirustkovy_pocet_prvnich_testu'` # yesterday or 2 days ago, depending on time
			if [[ $tests_yesterday_date == $infected_yesterday_date ]]; then
				# this means it's after 18:00 and we can use most recent data
				positive_tests=`echo "scale=2; 100 * $infected_yesterday / $tests_yesterday" | bc`
				positive_tests_first=`echo "scale=2; 100 * $infected_yesterday / $tests_first_newest" | bc`
				tests_prefix="yesterday:"
			else
				positive_tests=`echo "scale=2; 100 * $infected_two_days_ago / $tests_two_days_ago" | bc`
				positive_tests_first=`echo "scale=2; 100 * $infected_two_days_ago / $tests_first_newest" | bc`
				tests_prefix="2 days ago:"
			fi
			echo "active: $active | infected: $infected_overall (+$infected_yesterday, +$infected_today) | tested: $tests_overall ($tests_prefix +$tests_yesterday, $positive_tests% positive / +$tests_first_newest, $positive_tests_first%) | temporarily feeling better: $cured (+$cured_yesterday) | deceased: $deceased (+$deceased_yesterday) | hospitalised: $hospitalised" > "${CHANNEL_DIR}/in"
			;;
		nehody)
			curl -s https://d2g9cow0nr2qp.cloudfront.net/?q=$(echo -n "{ 'from': `date --date='00:00 yesterday' '+%s'`, 'to': `date --date='23:59:59 yesterday' '+%s'`, 'all': 'true' }" | base64) | jq '.["ČR"] | "accidents: " + (.PN | tostring) + " | dead: " + (.M | tostring) + " | serious injury: " + (.TR | tostring) + " | light injury: " + (.LR | tostring)' | xargs echo > "${CHANNEL_DIR}/in"
			;;
		*)
			echo "$nick: tvoje stara je $bar" > "${CHANNEL_DIR}/in"
			;;
	esac
done

