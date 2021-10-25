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
	pattern='^[0-9]+ <([^ ]+)> !([a-z]+)$'
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
			detailed_tests=`curl -s https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/testy.min.json`
			vaccinations=`curl -s https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani.min.json`
#			vacc_dist=`curl -s https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-distribuce.min.json`
			pes=`curl -s 'https://share.uzis.cz/s/BRfppYFpNTddAy4/download?path=%2F&files=pes_CR_verze2.csv'`
			tests_overall=`echo $overview| jq '.data[0].provedene_testy_celkem'`
			tests_overall_atg=`echo $overview| jq '.data[0].provedene_antigenni_testy_celkem'`
			tests_yesterday=`echo $overview| jq '.data[0].provedene_testy_vcerejsi_den'`
			tests_yesterday_atg=`echo $overview| jq '.data[0].provedene_antigenni_testy_vcerejsi_den'`
			hospitalised=`echo $overview | jq '.data[0].aktualne_hospitalizovani'`
			active=`echo $overview | jq '.data[0].aktivni_pripady'`
			infected_overall=`echo $overview | jq '.data[0].potvrzene_pripady_celkem'`
			infected_yesterday=`echo $overview | jq '.data[0].potvrzene_pripady_vcerejsi_den'`
			infected_7d=`echo $detailed | jq '((.data[-1].kumulativni_pocet_nakazenych - .data[-8].kumulativni_pocet_nakazenych))'`
			infected_7d_ago=`echo $detailed | jq '((.data[-8].kumulativni_pocet_nakazenych - .data[-9].kumulativni_pocet_nakazenych))'`
			infected_week_diff=`echo "$infected_yesterday $infected_7d_ago" | awk '//{printf("%+d", $1 - $2)}'`
			cured=`echo $overview | jq '.data[0].vyleceni'`
			cured_yesterday=`echo $detailed | jq '((.data[-1].kumulativni_pocet_vylecenych - .data[-2].kumulativni_pocet_vylecenych))'`
			deceased=`echo $overview | jq '.data[0].umrti'`
			deceased_yesterday=`echo $detailed | jq '((.data[-1].kumulativni_pocet_umrti - .data[-2].kumulativni_pocet_umrti))'`
			positive_tests=`echo "scale=2; 100 * $infected_yesterday / $tests_yesterday" | bc`
			vaccinations_overall=`echo "$vaccinations" | jq '.data[] | .celkem_davek' | awk '//{sum+=$1} END{print sum}'`
			vaccinations_yesterday=`echo "$vaccinations" | jq '.data[] | select (.datum | contains("'$(date --date="yesterday" +%Y-%m-%d)'")) | .celkem_davek' | awk '//{sum+=$1} END{print sum}'`
			vaccinations_first_overall=`echo "$vaccinations" | jq '.data[] | .prvnich_davek' | awk '//{sum+=$1} END{print sum}'`
			vaccinations_first_yesterday=`echo "$vaccinations" | jq '.data[] | select (.datum | contains("'$(date --date="yesterday" +%Y-%m-%d)'")) | .prvnich_davek' | awk '//{sum+=$1} END{print sum}'`
			vaccinations_second_overall=`echo "$vaccinations" | jq '.data[] | .druhych_davek' | awk '//{sum+=$1} END{print sum}'`
			vaccinations_second_yesterday=`echo "$vaccinations" | jq '.data[] | select (.datum | contains("'$(date --date="yesterday" +%Y-%m-%d)'")) | .druhych_davek' | awk '//{sum+=$1} END{print sum}'`
			vaccinations_third_overall=$((${vaccinations_overall} - ${vaccinations_first_overall} - ${vaccinations_second_overall}))
			vaccinations_third_yesterday=$((${vaccinations_yesterday} - ${vaccinations_first_yesterday} - ${vaccinations_second_yesterday}))
			pes_yesterday=`echo "$pes" | tail -n 1 | cut -d ';' -f 3`
			r_yesterday=`echo "$pes" | tail -n 1 | cut -d ';' -f 10 | xargs printf %.3f`
			echo "active: $active | infected: $infected_overall (+$infected_yesterday [1d], $infected_week_diff [1w diff]) | tested (PCR/ATG): $tests_overall/$tests_overall_atg (yesterday +$tests_yesterday/$tests_yesterday_atg, $positive_tests% positive) | temporarily feeling better: $cured (+$cured_yesterday) | deceased: $deceased (+$deceased_yesterday) | hospitalised: $hospitalised | vaccinated: $vaccinations_first_overall/$vaccinations_second_overall/$vaccinations_third_overall (+$vaccinations_yesterday/$vaccinations_second_yesterday/$vaccinations_third_yesterday) | PES: $pes_yesterday | R: $r_yesterday" > "${CHANNEL_DIR}/in"
			;;
		nehody)
			curl -s https://d2g9cow0nr2qp.cloudfront.net/?q=$(echo -n "{ 'from': `date --date='00:00 yesterday' '+%s'`, 'to': `date --date='23:59:59 yesterday' '+%s'`, 'all': 'true' }" | base64) | jq '.["ČR"] | "accidents: " + (.PN | tostring) + " | dead: " + (.M | tostring) + " | serious injury: " + (.TR | tostring) + " | light injury: " + (.LR | tostring)' | xargs echo > "${CHANNEL_DIR}/in"
			;;
		btc | eth)
			#curl -s 'https://www.bitstamp.net/api-internal/market/prices/?step=60&start='`date -u --date="day ago" +%Y-%m-%dT%H:%M:%S.000Z`'&end='`date -u +%Y-%m-%dT%H:%M:%S.999Z`'&pairs=btcusd'  | jq -r '.data[0]["price"] + " " +  .data[0]["history"][0]["open"] + " " + .data[0]["history"][-60]["open"]' | awk '//{printf("BTC: $%.2f | %+.2f%% (1h) | %+.2f%% (24h)\n", $1, 100*$1/$3-100, 100*$1/$2-100)}' > "${CHANNEL_DIR}/in"
			curl -s https://www.bitstamp.net/api-internal/price-history/${bar}usd/ | jq -r '.data["latest"]["price"] + " " + (.data["prices"]["hour"]["percent_change"]|tostring) + " " + (.data["prices"]["day"]["percent_change"]|tostring) + " " + (.data["prices"]["week"]["percent_change"]|tostring)' | awk '//{printf("%s: $%.2f | %+.2f%% (1h) | %+.2f%% (1d) | %+.2f%% (1w)\n", toupper("'$bar'"), $1, $2, $3, $4)}' > "${CHANNEL_DIR}/in"
			;;
		event | events)
			curl -s 'https://events.gcm.cz/api.php?action=events&from='`date --date='today' +%Y-%m-%d`'&to='`date --date='next month' +%Y-%m-%d`'&lat=49.1950602&lon=16.6068371&radius=10&requestId=1' | jq -r '.events | reduce .[] as $event (""; . + "(" + $event.gcid + ") " + $event.name + "|" + $event.date_from + "\n" )' | head -n-1 | head -n 4 | while IFS='|' read e d; do echo -n "$e ["`date --date="$d" "+%a %d %b %Y %R"`"] | "; done | sed 's/| $/\n/g' > "${CHANNEL_DIR}/in"
			;;
		*)
			echo "$nick: tvoje stara je $bar" > "${CHANNEL_DIR}/in"
			;;
	esac
done

