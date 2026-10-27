# Flycast Vulkan source bundle v1.0.6

Retains the full upstream archives and their original license notices. Standard: flyinghead/flycast v2.7; VL: libretro/flycast at 4a913e063c95d1fae98afc64645831de0bcad57e; Xtreme: metallic77/flycast at 603814c9f73b773c455d9a497f389d2f93a257fd. Project glue licensing does not replace the licenses of these sources or their dependencies.

Extract this bundle, export ACTIONPI_PROJECT_ROOT to its root, and install Arm GNU 13.3.Rel1 at the paths in the build scripts. Standard extraction uses SOURCES.json and the included archive-version.patch records the version-label-only change. Run work/build_flycast27_vulkan.sh. The VL/Xtreme source archives must first be extracted with one directory stripped into /root/actionpi-flycast-vulkan-trial/vl and xtreme; build_flycast_vulkan.sh applies the included libretro/comment-boundary patches automatically. Run it once per variant. Do not rebuild or install into a running game session.

Provide the matching ARM64 target SDK at outputs/ppsspp-1.20.4-prep/target-sdk (headers, libmali.so.0 and dependencies from the inherited firmware/build environment); those inherited binaries are not relicensed or included here. CMake is expected at /root/.cache/actionpi-nodosumi-buildtools/cmake/data/bin/cmake; adjust the path for an equivalent host installation. The rotation build additionally expects glslangValidator at /root/actionpi-flycast-vulkan-trial/host-tools/usr/bin/glslangValidator. Build scripts record all selected options. GL remains compiled in; normal dispatch selects Vulkan. HAVE_GENERIC_JIT=0 avoids the duplicate ARM64 JIT. No CPU affinity changes.

The scoped rotation loader uses SONAME libvulkan.so.1 and NODELETE; it loads the real /usr/lib/libvulkan.so.1 by absolute path. Install equal loader bytes under both .so and .so.1 on filesystems without symlinks. Its effective source is work/flycast_vulkan_rotation.c and the two shaders.

No emulator binaries, games, BIOS, personal settings, credentials or runtime captures are in this source bundle. The existing proprietary driver/original vendor-kernel source limitations remain documented in the repository.
