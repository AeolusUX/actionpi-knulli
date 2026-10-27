#!/bin/bash
set -euo pipefail
root="${ACTIONPI_PROJECT_ROOT:?Set the extracted source bundle root}"
dest=/root/actionpi-flycast-2.7
out="$root/outputs/flycast-2.7-prep"
if [ ! -f "$dest/source/.source-extracted" ];then
 python3 "$root/work/extract_flycast27_sources.py" "$root" > "$out/source.log" 2>&1
fi
cmake=/root/.cache/actionpi-nodosumi-buildtools/cmake/data/bin/cmake
sdk="$root/outputs/ppsspp-1.20.4-prep/target-sdk"
"$cmake" -S "$dest/source" -B "$dest/build" \
 -DCMAKE_TOOLCHAIN_FILE="$root/outputs/ppsspp-1.20.4-prep/aarch64-actionpi.cmake" \
 -DCMAKE_BUILD_TYPE=Release -DCMAKE_SKIP_RPATH=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
 -DCMAKE_C_FLAGS="-I$out/include -I$sdk/usr/include" -DCMAKE_CXX_FLAGS="-I$out/include -I$sdk/usr/include" \
 -DCMAKE_SHARED_LINKER_FLAGS="-L$sdk/usr/lib -Wl,-rpath-link,$sdk/usr/lib" \
 -DCMAKE_DISABLE_FIND_PACKAGE_PkgConfig=ON -DCMAKE_DISABLE_FIND_PACKAGE_X11=ON \
 -DLIBRETRO=ON -DUSE_VULKAN=ON -DUSE_OPENGL=ON -DUSE_GLES=ON -DUSE_GLES2=OFF \
 -DOPENGL_LIBRARIES="$sdk/usr/lib/libmali.so.0" \
 -DUSE_HOST_LIBZIP=OFF -DENABLE_UPNP=OFF -DENABLE_DC_PROFILER=OFF > "$out/configure.log" 2>&1
"$cmake" --build "$dest/build" -j4 > "$out/build.log" 2>&1
core=$(find "$dest/build" -name flycast_libretro.so -type f -print -quit)
test -n "$core"
cp "$core" "$out/flycast-standard-vulkan_libretro.so"
prefix=/opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-
"${prefix}strip" --strip-unneeded "$out/flycast-standard-vulkan_libretro.so"
"${prefix}readelf" -h -d -V "$out/flycast-standard-vulkan_libretro.so" > "$out/ELF.txt"
sha256sum "$out/flycast-standard-vulkan_libretro.so"
echo STANDARD_2_7_VULKAN_BUILD_OK
