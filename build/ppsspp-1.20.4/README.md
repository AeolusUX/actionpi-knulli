# PPSSPP 1.20.4 build inputs

The full official source archive is the release asset `ppsspp-1.20.4.tar.xz`; its exact hash is in SOURCE.json. It includes FFmpeg and bundled dependencies. The executable is built from it, with `font-fallback.patch` applied by font-fix.sh. The former proprietary Mali/runtime dependency limitations remain documented in docs/SOURCES_AND_LICENSES.md.

The scripts preserve the build directory layout used in development: `$ACTIONPI_WORKDIR/outputs/ppsspp-1.20.4-prep/` contains the archive, `downloads/` dependency archives listed in DEPENDENCY_SOURCES.json, toolchain file and `target-sdk/usr/{include,lib}`. Stage the matching runtime libraries from the inherited root filesystem. This is an integration recipe, not a claim of a clean full-firmware rebuild. Set ACTIONPI_BUILD_DIR to a writable Linux build directory and CMAKE_BIN to CMake 3.31; the GNU ARM 13.3.1 toolchain is expected under /opt/actionpi-toolchain. Run build.sh then font-fix.sh. New SDL headers are used for compilation; the existing runtime SDL/Mali libraries are not rebuilt or replaced.

The output bundle must contain `PPSSPP-1.20.4`, `assets/`, the two LICENSE texts and `rotation/`. Compile `src/v116_vulkan_output_rotation.c` as a shared ARM64 library with `-shared -fPIC -O2 -Wall -Wextra -Werror -ldl`; copy it to both `rotation/libvulkan.so` and `rotation/libvulkan.so.1`. Retain the existing `sdl_output_rotation.so` and its published source. Kernel, ICD and libmali are unchanged. Package with tools/package-v1.0.4.py using ACTIONPI_IMAGE_DIR and ACTIONPI_PPSSPP_BUNDLE. Build and patch scripts remain separate so the original build order is explicit.

한국어 과정은 docs/BUILD.ko.md의 v1.0.4 부분을 참고하세요. 개인 설정·시험 캡처·원격 접속 도구는 공개하지 않습니다.
