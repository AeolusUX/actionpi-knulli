#!/bin/bash
set -euo pipefail
root="${ACTIONPI_PROJECT_ROOT:?Set the extracted source bundle root}"
out="$root/outputs/flycast-vulkan-trial"
dest=/root/actionpi-flycast-vulkan-trial
prefix=/opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-
sdk="$root/outputs/ppsspp-1.20.4-prep/target-sdk"
variant="${1:?variant}"
shift
case "$variant" in vl|xtreme) ;; *) exit 2;; esac
source="$dest/$variant"
mkdir -p "$out/$variant"
python3 "$root/work/patch_flycast_vulkan_only.py" "$source" "$out/$variant"
if [ ! -f "$source/.vulkan-gl-jit-cleaned" ];then
 make -C "$source" clean platform=unix ARCH=arm64 HAVE_GENERIC_JIT=0 HAVE_VULKAN=1 HAVE_GL=1 >/dev/null 2>&1
 touch "$source/.vulkan-gl-jit-cleaned"
fi
flags="-march=armv8-a -mtune=cortex-a55 -DHAVE_OPENGLES2 -I$source/core/deps/zlib -I$sdk/usr/include -L$sdk/usr/lib -Wl,-rpath-link,$sdk/usr/lib -Wno-error=incompatible-pointer-types"
make -C "$source" -j4 platform=unix ARCH=arm64 WITH_DYNAREC=arm64 \
 CC="${prefix}gcc" CXX="${prefix}g++" LD="${prefix}g++" CC_AS="${prefix}gcc" \
 HAVE_VULKAN=1 HAVE_GL=1 HAVE_GENERIC_JIT=0 FORCE_GLES=1 GL_LIB="$sdk/usr/lib/libmali.so.0" HAVE_OPENMP=1 GIT_VERSION=actionpi-vulkan-trial \
 MFLAGS="$flags" "$@" > "$out/$variant/build.log" 2>&1
cp "$source/flycast_libretro.so" "$out/$variant/flycast-$variant-vulkan_libretro.so"
"${prefix}strip" --strip-unneeded "$out/$variant/flycast-$variant-vulkan_libretro.so"
"${prefix}readelf" -h -d -V "$out/$variant/flycast-$variant-vulkan_libretro.so" > "$out/$variant/ELF.txt"
sha256sum "$out/$variant/flycast-$variant-vulkan_libretro.so"
echo "${variant}_BUILD_OK"
