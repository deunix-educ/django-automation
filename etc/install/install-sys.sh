:x#!/bin/bash
if [ $EUID -ne 0 ]; then
  echo "Lancer en root: # $0" 1>&2
  exit 1
fi

apt update
#apt upgrade

apt -y install build-essential openssl git pkg-config redis supervisor
apt -y install python3-dev python3-pip python3-venv libmariadb-dev libpq-dev


# influxdb V2
curl https://repos.influxdata.com/influxdata-archive.key | gpg --dearmor | sudo tee /usr/share/keyrings/influxdb
echo "deb [signed-by=/usr/share/keyrings/influxdb-archive-keyring.gpg] https://repos.influxdata.com/debian stable main" | sudo tee /etc/apt/sources.list.d/influxdb.list
apt update
apt -y install influxdb2

## zigbee2mqtt
curl -sL https://deb.nodesource.com/setup_10.x | sudo bash -
apt -y install nodejs

## mosquitto
apt -y install mosquitto

# rpi2, orangepi, eeepc:i386, bananapi
# apt install python3-numpy python3-pandas python3-opencv python3-paho-mqtt python3-psycopg2
# pip3 --break-system-packages install imutils


# supervisor http access
#
if  [ "$INSTALL_SUPERVISOR" == "yes" ]; then
if [ ! -e "/etc/supervisor/supervisord.conf.old" ]; then
cp /etc/supervisor/supervisord.conf /etc/supervisor/supervisord.conf.old

cat >> /etc/supervisor/supervisord.conf << EOF
[inet_http_server]
port=*:9001
username=root
password=toor
EOF
fi
fi



