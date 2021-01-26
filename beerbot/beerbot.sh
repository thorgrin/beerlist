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
			detailed_tests=`curl -s https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/testy.json`
			vaccinations=`curl -s https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani.json`
			pes=`curl -s 'https://share.uzis.cz/s/BRfppYFpNTddAy4/download?path=%2F&files=pes_CR_verze2.csv'`
			tests_overall=`echo $overview| jq '.data[0].provedene_testy_celkem'`
			tests_overall_atg=`echo $overview| jq '.data[0].provedene_antigenni_testy_celkem'`
			tests_yesterday=`echo $overview| jq '.data[0].provedene_testy_vcerejsi_den'`
			tests_yesterday_atg=`echo $overview| jq '.data[0].provedene_antigenni_testy_vcerejsi_den'`
			hospitalised=`echo $overview | jq '.data[0].aktualne_hospitalizovani'`
			active=`echo $overview | jq '.data[0].aktivni_pripady'`
			infected_overall=`echo $overview | jq '.data[0].potvrzene_pripady_celkem'`
			infected_today=`echo $overview | jq '.data[0].potvrzene_pripady_dnesni_den'`
			infected_yesterday=`echo $overview | jq '.data[0].potvrzene_pripady_vcerejsi_den'`
			cured=`echo $overview | jq '.data[0].vyleceni'`
			cured_yesterday=`echo $detailed | jq '((.data[-1].kumulativni_pocet_vylecenych - .data[-2].kumulativni_pocet_vylecenych))'`
			deceased=`echo $overview | jq '.data[0].umrti'`
			deceased_yesterday=`echo $detailed | jq '((.data[-1].kumulativni_pocet_umrti - .data[-2].kumulativni_pocet_umrti))'`
			positive_tests=`echo "scale=2; 100 * $infected_yesterday / $tests_yesterday" | bc`
			vaccinations_overall=`echo "$vaccinations" | jq '.data[] | .celkem_davek' | awk '//{sum+=$1} END{print sum}'`
			vaccinations_yesterday=`echo "$vaccinations" | jq '.data[] | select (.datum | contains("'$(date --date="yesterday" +%Y-%m-%d)'")) | .celkem_davek' | awk '//{sum+=$1} END{print sum}'`
			vaccinations_second_overall=`echo "$vaccinations" | jq '.data[] | .druhych_davek' | awk '//{sum+=$1} END{print sum}'`
			vaccinations_second_yesterday=`echo "$vaccinations" | jq '.data[] | select (.datum | contains("'$(date --date="yesterday" +%Y-%m-%d)'")) | .druhych_davek' | awk '//{sum+=$1} END{print sum}'`
pes_yesterday=`echo "$pes" | tail -n 1 | cut -d ';' -f 3`
			r_yesterday=`echo "$pes" | tail -n 1 | cut -d ';' -f 10 | xargs printf %.3f`
			echo "active: $active | infected: $infected_overall (+$infected_yesterday, +$infected_today) | tested (PCR/ATG): $tests_overall/$tests_overall_atg (yesterday +$tests_yesterday/$tests_yesterday_atg, $positive_tests% positive) | temporarily feeling better: $cured (+$cured_yesterday) | deceased: $deceased (+$deceased_yesterday) | hospitalised: $hospitalised | vaccinated: $vaccinations_overall/$vaccinations_second_overall (+$vaccinations_yesterday/$vaccinations_second_yesterday) | PES: $pes_yesterday | R: $r_yesterday" > "${CHANNEL_DIR}/in"
			;;
		nehody)
			curl -s https://d2g9cow0nr2qp.cloudfront.net/?q=$(echo -n "{ 'from': `date --date='00:00 yesterday' '+%s'`, 'to': `date --date='23:59:59 yesterday' '+%s'`, 'all': 'true' }" | base64) | jq '.["ČR"] | "accidents: " + (.PN | tostring) + " | dead: " + (.M | tostring) + " | serious injury: " + (.TR | tostring) + " | light injury: " + (.LR | tostring)' | xargs echo > "${CHANNEL_DIR}/in"
			;;
		*)
			echo "$nick: tvoje stara je $bar" > "${CHANNEL_DIR}/in"
			;;
	esac
done

