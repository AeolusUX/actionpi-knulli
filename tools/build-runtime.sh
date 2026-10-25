#!/bin/sh
# Build original userspace adapters only; no flashing or live device operations.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
out="$root/build"
cc="${CROSS_COMPILE-aarch64-none-linux-gnu-}gcc"
mkdir -p "$out/portmaster-sdl"
flags='-shared -fPIC -O2 -Wall -Wextra -Werror'
"$cc" $flags "$root/overlay/boot/ACTIONPI_FIXES/mali_menu_audit.c" \
 "$root/overlay/boot/ACTIONPI_FIXES/actionpi_backlight_io.c" -ldl -o "$out/mali_menu_audit.so"
"$cc" $flags "$root/src/retroarch_output_rotation.c" -ldl -o "$out/retroarch_output_rotation.so"
"$cc" $flags "$root/overlay/boot/ACTIONPI_FIXES/flycast_gl_rotation.c" -ldl -o "$out/flycast_gl_rotation.so"
"$cc" $flags "$root/src/v116_sdl_output_rotation.c" -ldl -o "$out/sdl_output_rotation.so"
"$cc" $flags "$root/src/v116_vulkan_output_rotation.c" -ldl -o "$out/libvulkan.so.1"
"$cc" -shared -fPIC -O2 -Wall -Wextra "$root/src/app_sdl_rotation.c" \
 "$root/src/app_gl_rotation.c" -ldl -o "$out/app_output_rotation.so"
"$cc" -shared -fPIC -O2 -Wall -Wextra "$root/src/od_commander_rotation.c" \
 -ldl -o "$out/od_commander_rotation.so"
if [ -n "${SDL2_LIB:-}" ]; then
 "$cc" $flags "$root/src/portmaster_output_rotation.c" -Wl,--no-as-needed \
  "$SDL2_LIB" -Wl,--as-needed -ldl -o "$out/portmaster-sdl/libSDL2.so"
else
 printf '%s\n' 'PortMaster adapter skipped: set SDL2_LIB to the target ARM64 SDL2 file.'
fi
printf '%s\n' "Built helpers in $out; no IMG or device changed."
