#!/bin/bash
IP=192.168.4.1
PASS=bikewheel
DIR=~/Bike_LED/Back_ESP

for f in main.py apa102.py espnow_rx.py; do
    python3 ~/Downloads/webrepl_cli.py -p $PASS $DIR/$f $IP:/$f
    echo "Uploaded $f"
done