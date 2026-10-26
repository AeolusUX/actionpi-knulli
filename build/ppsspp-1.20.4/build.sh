#!/bin/bash
set -euo pipefail
root=${ACTIONPI_WORKDIR:-$PWD}
prep="$root/outputs/ppsspp-1.20.4-prep"
trial=${ACTIONPI_BUILD_DIR:-$root/ppsspp-build}
tc=/opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu
cross="$tc/bin/aarch64-none-linux-gnu-"
cmake=${CMAKE_BIN:-cmake}
sdk="$prep/target-sdk"
mkdir -p "$trial" "$sdk/usr/include/SDL2" "$sdk/usr/lib/cmake/SDL2_ttf" "$sdk/usr/lib/cmake/Fontconfig"
if [ ! -f "$trial/source/CMakeLists.txt" ]; then
  mkdir -p "$trial/source"
  tar -xJf "$prep/ppsspp-1.20.4.tar.xz" -C "$trial/source" --strip-components=1
fi
if [ ! -f "$trial/SDL2-2.32.8/include/SDL.h" ]; then
  tar -xzf "$prep/downloads/SDL2-2.32.8.tar.gz" -C "$trial"
  tar -xzf "$prep/downloads/SDL2_ttf-2.24.0.tar.gz" -C "$trial"
fi
if [ ! -f "$trial/fontconfig-2.16.0/fontconfig/fontconfig.h" ]; then
  tar -xJf "$prep/downloads/fontconfig-2.16.0.tar.xz" -C "$trial"
fi
cp -u "$trial/SDL2-2.32.8/include/"*.h "$sdk/usr/include/SDL2/"
cp -u "$trial/SDL2_ttf-2.24.0/SDL_ttf.h" "$sdk/usr/include/SDL2/"
cp -ru "$trial/SDL2-2.32.8/src/video/khronos/"* "$sdk/usr/include/"
mkdir -p "$sdk/usr/include/fontconfig"
cp -u "$trial/fontconfig-2.16.0/fontconfig/fontconfig.h" "$sdk/usr/include/fontconfig/"
# Configure SDL's public headers using its official cross-configuration.
# This does not build or replace the on-device SDL runtime.
if [ ! -f "$trial/sdl-headers/include/SDL_config.h" ]; then
  mkdir -p "$trial/sdl-headers"
  (cd "$trial/sdl-headers" && CC="${cross}gcc" CXX="${cross}g++" \
    "$trial/SDL2-2.32.8/configure" --host=aarch64-none-linux-gnu \
    --disable-video-x11 --disable-video-wayland --disable-video-kmsdrm \
    --disable-audio --disable-render --disable-joystick --disable-haptic \
    --disable-libudev --disable-dbus --disable-ibus --disable-fcitx \
    > "$prep/sdl-headers-configure.log" 2>&1)
fi
cp -u "$trial/sdl-headers/include/SDL_config.h" "$sdk/usr/include/SDL2/SDL_config.h"
cat > "$sdk/usr/lib/cmake/SDL2_ttf/SDL2_ttfConfig.cmake" <<'EOF'
get_filename_component(_prefix "${CMAKE_CURRENT_LIST_DIR}/../../.." ABSOLUTE)
add_library(SDL2_ttf::SDL2_ttf SHARED IMPORTED)
set_target_properties(SDL2_ttf::SDL2_ttf PROPERTIES IMPORTED_LOCATION "${_prefix}/lib/libSDL2_ttf.so" INTERFACE_INCLUDE_DIRECTORIES "${_prefix}/include/SDL2")
set(SDL2_ttf_FOUND TRUE)
EOF
# Keep existing SDL_ttf+fontconfig font lookup; CMake's FindFontconfig finds this SDK.
if [ ! -s "$trial/source/ffmpeg/linux/aarch64/lib/libavcodec.a" ]; then
  python3 - "$trial" "$cross" "$sdk" <<'PY'
import pathlib, sys
trial, cross, sdk = sys.argv[1:]
path = pathlib.Path(trial)/'source/ffmpeg/linux_arm64.sh'
data = path.read_text().replace('aarch64-linux-gnu-', cross)
data = data.replace('--extra-cflags=" ', '--extra-cflags=" -I'+trial+'/source/ext/zlib ')
data = data.replace('--enable-zlib \\', '--enable-zlib \\\n    --extra-ldflags="-L'+sdk+'/usr/lib -Wl,-rpath-link,'+sdk+'/usr/lib" \\')
data = data.replace('make install', 'make -j2\nmake install')
(path.parent/'actionpi_arm64_trial.sh').write_text(data)
PY
  (cd "$trial/source/ffmpeg" && bash ./actionpi_arm64_trial.sh > "$prep/ffmpeg-build.log" 2>&1)
fi
echo FFMPEG_ARM64_BUILT
"$cmake" -S "$trial/source" -B "$trial/build" \
  -DCMAKE_TOOLCHAIN_FILE="$prep/aarch64-actionpi.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_SKIP_RPATH=ON \
  -DCMAKE_INSTALL_PREFIX=/opt/actionpi-ppsspp-1.20.4-test \
  -DCMAKE_C_FLAGS="-I$sdk/usr/include -DEGL_NO_X11=1" \
  -DCMAKE_CXX_FLAGS="-I$sdk/usr/include -DEGL_NO_X11=1" \
  -DCMAKE_EXE_LINKER_FLAGS="-L$sdk/usr/lib -Wl,-rpath-link,$sdk/usr/lib" \
  -DUSING_QT_UI=OFF -DLIBRETRO=OFF -DHEADLESS=OFF -DUNITTEST=OFF -DATLAS_TOOL=OFF \
  -DUSE_SYSTEM_LIBSDL2=ON -DSDL2_LIBRARY="$sdk/usr/lib/libSDL2.so" -DSDL2_INCLUDE_DIR="$sdk/usr/include/SDL2" \
  -DUSING_EGL=OFF -DUSING_GLES2=ON -DOPENGL_LIBRARIES="$sdk/usr/lib/libmali.so.0" \
  -DUSING_X11_VULKAN=OFF -DUSE_WAYLAND_WSI=OFF -DUSE_VULKAN_DISPLAY_KHR=ON \
  -DCMAKE_DISABLE_FIND_PACKAGE_X11=ON -DCMAKE_DISABLE_FIND_PACKAGE_Wayland=ON \
  -DCMAKE_DISABLE_FIND_PACKAGE_PkgConfig=ON \
  -DUSE_FFMPEG=ON -DUSE_SYSTEM_FFMPEG=OFF -DFFMPEG_DIR="$trial/source/ffmpeg/linux/aarch64" \
  -DUSE_SYSTEM_LIBPNG=OFF -DUSE_SYSTEM_ZSTD=OFF -DUSE_SYSTEM_FREETYPE=OFF \
  -DUSE_DISCORD=OFF -DUSE_CCACHE=OFF > "$prep/configure-trial.log" 2>&1
echo PPSSPP_CONFIGURED
"$cmake" --build "$trial/build" --target PPSSPPSDL -j2 > "$prep/ppsspp-build.log" 2>&1
mkdir -p "$prep/trial-bundle"
cp "$trial/build/PPSSPPSDL" "$prep/trial-bundle/PPSSPP-1.20.4"
"${cross}strip" --strip-unneeded "$prep/trial-bundle/PPSSPP-1.20.4"
cp -a "$trial/source/assets" "$prep/trial-bundle/assets"
"${cross}readelf" -h -d -V "$prep/trial-bundle/PPSSPP-1.20.4" > "$prep/trial-bundle/ELF.txt"
echo PPSSPP_1204_TRIAL_BUILT
