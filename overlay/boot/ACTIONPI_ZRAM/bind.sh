#!/bin/sh
# Called by S00bootcustom before S99userservices; never add a duplicate user service.
set -eu
target=/usr/share/knulli/services/zramswap
if ! grep -q ACTIONPI_ZRAM_COMPAT_SERVICE "$target"; then
    mount --bind /boot/ACTIONPI_ZRAM/zramswap "$target"
fi
grep -q ACTIONPI_ZRAM_COMPAT_SERVICE "$target"
printf 'ZRAM_SERVICE_BOUND boot='
cat /proc/sys/kernel/random/boot_id
