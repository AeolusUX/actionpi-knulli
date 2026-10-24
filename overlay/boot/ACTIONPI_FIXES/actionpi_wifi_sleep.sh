#!/bin/sh
# Action Pi AIC8800DC holds a wake lock while its interface is active.
[ "$(cat /boot/boot/knulli.board)" = helegany-action-pi ] || exit 0
state=/run/actionpi-wifi-before-sleep
case "$1" in
 suspend|hibernate)
  rm -f "$state" # Cancel any older recovery attempt before a new sleep.
  if connmanctl technologies 2>/dev/null | awk '/Type = wifi/{wifi=1} wifi && /Powered = True/{found=1} END{exit !found}'; then
   python3 /boot/ACTIONPI_FIXES/actionpi_wifi_resume.py prepare
   connmanctl disable wifi >/dev/null 2>&1
   for dev in /sys/class/net/*; do
    [ -d "$dev/wireless" ] && ip link set "${dev##*/}" down 2>/dev/null
   done
   sleep 1
  fi
  ;;
 resume|thaw)
  python3 /boot/ACTIONPI_FIXES/actionpi_pwm_normalize.py resume >>/boot/ACTIONPI_FIXES/pwm-polarity.log 2>&1 || true
  if [ -f "$state" ]; then
   python3 /boot/ACTIONPI_FIXES/actionpi_wifi_resume.py resume </dev/null >>/boot/ACTIONPI_FIXES/wifi-resume.log 2>&1 &
  fi
  ;;
esac
exit 0
