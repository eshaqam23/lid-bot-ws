#!/bin/bash
# Re-binds cp210x drivers so the ESP (CP2102N) becomes /dev/ttyUSB0 and the lidar (CP2102)
# /dev/ttyUSB1. Needed because repo motor_commands hardcodes /dev/ttyUSB0. Run with sudo.
D=/sys/bus/usb/drivers/cp210x
esp=""; lidar=""
for i in $(ls $D | grep -E "^[0-9]+-[0-9.]+:1\.0$"); do
  m=$(cat $D/$i/../product 2>/dev/null)
  case "$m" in *CP2102N*) esp=$i;; *CP2102*) lidar=$i;; esac
done
[ -z "$esp" ] && { echo "ESP (CP2102N) not found"; exit 1; }
for i in $esp $lidar; do echo $i > $D/unbind; done; sleep 1
echo $esp > $D/bind; sleep 1.5
[ -n "$lidar" ] && { echo $lidar > $D/bind; sleep 1.5; }
for t in /dev/ttyUSB*; do echo "$t -> $(udevadm info -q property -n $t | grep ^ID_MODEL=)"; done
