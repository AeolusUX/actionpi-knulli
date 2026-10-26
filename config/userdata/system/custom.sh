#!/bin/sh

# ACTIONPI_QUIET_START
if [ "$1" = start ]; then
    python3 /userdata/system/background-quiet/quiet_start.py || true
fi

# ACTIONPI_RUMBLE_CALIBRATION
if [ "$1" = start ]; then
    python3 /userdata/system/rumble-fix/apply.py start || true
fi
