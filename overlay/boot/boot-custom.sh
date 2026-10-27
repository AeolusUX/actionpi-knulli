#!/bin/sh
# ACTIONPI_ZRAM_BOOT
if [ "$1" = start ]; then
    sh /boot/ACTIONPI_ZRAM/bind.sh >>/boot/ACTIONPI_ZRAM/bind.log 2>&1 || true
fi
[ "$1" = start ] || exit 0
python3 /boot/ACTIONPI_FIXES/actionpi_ui_fixes.py
python3 /boot/PPSSPP_VULKAN/v116_vulkan_manager.py boot >>/boot/PPSSPP_VULKAN/boot.log 2>&1
