#!/bin/bash
IP=192.168.4.1
PASS=bikewheel
DIR=~/Bike_LED/Front_ESP

for f in main.py apa102.py hall_sync.py frames.py espnow_tx.py index.html; do
    python3 ~/Downloads/webrepl_cli.py -p $PASS $DIR/$f $IP:/$f
    echo "Uploaded $f"
done