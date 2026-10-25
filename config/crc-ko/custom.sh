#!/bin/sh
# ACTIONPI_PERSONAL_CORES_LATE
if [ "$1" = start ]; then
    {
        printf 'PERSONAL_CORES_BOOT_ID='
        cat /proc/sys/kernel/random/boot_id
        python3 /userdata/system/custom-cores/load.py
    } >>/userdata/system/custom-cores/boot.log 2>&1 || true
fi
