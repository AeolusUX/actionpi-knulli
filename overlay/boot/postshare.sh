#!/bin/sh
[ "$1" = start ] || exit 0
mount -o remount,rw /boot || exit 1
exec python3 /boot/STABLE_V119/firstboot.py >>/boot/STABLE_V119/firstboot.log 2>&1
