# Beer List

This project aims to provide simple interface to get lists of beers from my favourite pubs.

## Supported pubs

* [Malt Worm](https://maltworm.cz/)
* [Ochutnávková pivnice](http://ochutnavkovapivnice.cz/)
* [Craftbeer bottle shop & bar](https://www.facebook.com/Craftbeerbottleshopbar/)

## Howto use

### Separate use of parsers
* The parsers can be used separately, there are just a few simple dependencies as mentioned in `requirements.txt`.
* The parsers can be easily run in their own python virtual environment:
```
python3 -m venv ./venv
source /venv/bin/activate
pip3 install -r requirements.txt
python3 ./parsers/mwparser.py
```

### Run periodically and create beerlog
* Add `update_cache.sh ` script to crontab
```
*/20 0,1,9-23 * * * /path/to/tools/update_cache.sh
```

### Run as web service under Apache:
* check out the code to a web accessible directory with PHP support
* change group of `cache` directory to that of the web server (e.g. www-data)
```
chgrp www-data cache
chmod 6775 cache
```
* Check that all files are first created by calling `tools/update_cache.sh` to ensure that the usr has owner rights
* Setup log file with permissions:
```
touch log/beerlog.json
chgrp www-data log/beerlog.json
```
* allow mod_rewrite (a2enmod rewrite)
* allow .htaccess for the dir
```
        <Directory /var/www/html/beer>
                AllowOverride All
        </Directory>
```

### Push beer notifications to IRC
Notifications can be easily pushed to a selected IRC channel by setting up an instance of ii (IRC file based client)
```
apt-get install ii
sudo cp beerbot/beerbot.service /etc/systemd/user/
cp beerbot/beerbot.conf ~/.config/
systemctl --user daemon-reload
systemctl --user enable beerbot
systemctl --user start beerbot
```
To configure the IRC server, channel and bot name, edit the `beerbot.conf` file.
