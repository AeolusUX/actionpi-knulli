#!/bin/sh
# Only keep a worker alive while a brightness notification is visible.
: > /run/actionpi-brightness-osd.request
(
    flock -n 9 || exit 0
    exec /usr/bin/python3 /userdata/system/brightness-osd/overlay.py \
        >/run/actionpi-brightness-osd.log 2>&1
) 9>/run/actionpi-brightness-osd.launch.lock </dev/null &
exit 0
