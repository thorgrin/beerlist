# Beer List

This project aims to provide simple interface to get lists of beers from my favourite pubs.

## Supported pubs

* [Malt Worm](https://maltworm.cz/)
* [Ochutnávková pivnice](http://ochutnavkovapivnice.cz/)
* [Craftbeer bottle shop & bar](https://www.facebook.com/Craftbeerbottleshopbar/)
* [JBM Brew Lab Pub](http://jbmbrewlab.cz/)
* [F.A. Bar Oranžová](http://www.fabar.cz/)

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
* Check out the code to a web accessible directory with PHP support
* Change group of `cache` directory to that of the web server (e.g. www-data)
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
* Allow mod_rewrite (a2enmod rewrite)
* Allow .htaccess for the dir
```
        <Directory /var/www/html/beer>
                AllowOverride All
        </Directory>
```

### Push beer notifications to IRC
Notifications can be easily pushed to a selected IRC channel by setting up an instance of ii (IRC file based client)
```
apt-get install ii
sudo cp beerbot/beerbot-connection.service /etc/systemd/user/
# the config file must be accessible even for www-data, therefore this ugly place
sudo cp beerbot/beerbot.conf /etc/
systemctl --user daemon-reload
systemctl --user enable beerbot-connection
systemctl --user start beerbot-connection
```
To configure the IRC server, channel and bot name, edit the `beerbot.conf` file.

### Let beerbot react to commands
The beerbot can respond to IRC commands in form of `!pub` where `pub` is a shortcut of one of the supported pubs
For this to work, you need to start the `beerbot-connection` service. Pushing notifications to IRC can be disabled.

* Configure the path to the beerbot script in the `/etc/beerbot.conf`. It must be within the original directory structure.
* The beerbot systemd service needs to be enabled:
```
sudo cp beerbot/beerbot.service /etc/systemd/user/
systemctl --user daemon-reload
systemctl --user enable beerbot
systemctl --user start beerbot
```

### Push Untappd beer notifications to IRC
Untappd drinking notifications from your friends can be easily pushed to a selected IRC channel by setting up an instance of ii (IRC file based client).
Pushing ordinary beer notifications from pubs can be disabled in `beerbot.conf`.
```
apt-get install ii
sudo cp beerbot/beerbot-connection.service /etc/systemd/user/
# the config file must be accessible even for www-data, therefore this ugly place
sudo cp beerbot/beerbot.conf /etc/
systemctl --user daemon-reload
systemctl --user enable beerbot-connection
systemctl --user start beerbot-connection
```
To configure the IRC server, channel and bot name, edit the `beerbot.conf` file.

To enable Untappd notifications:
* It is necessary to write Untappd user names and corresponding IRC nicks into `beerbot.conf` file.
  ```
  UNTAPPD_USERS="beeruser1 beeruser2"
  UNTAPPD_IRC_NICKS="cervezaadicto1 cervezaadicto2"
  ```
* Add `update_untappd.sh` script to crontab
  ```
  */10 * * * * /path/to/tools/update_untappd.sh
  ```
