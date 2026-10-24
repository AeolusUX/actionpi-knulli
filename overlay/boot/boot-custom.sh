#!/bin/sh
[ "$1" = start ] || exit 0
python3 /boot/ACTIONPI_FIXES/actionpi_ui_fixes.py
python3 /boot/PPSSPP_VULKAN/v116_vulkan_manager.py boot >>/boot/PPSSPP_VULKAN/boot.log 2>&1
