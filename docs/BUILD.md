# Build and reproduction status

[English](BUILD.md) · [한국어](BUILD.ko.md)

## What can be rebuilt here

The repository includes the current runtime scripts, rotation C source, pinned
Mali driver source, recovered kernel configuration, display repair assembly and
linker script, and the historical image transformation tools. This exposes the
adaptation rather than only publishing a binary image.

It does **not** provide a complete, proven corresponding source tree for the
original vendor kernel or all programs in the inherited root filesystem. A clean
full firmware build from this repository alone is not available. The historical
packagers reference local earlier image checkpoints that are not public assets;
they are included as an audit trail, not advertised as a one-command public build.

## Userspace helper build

Use Linux or WSL with an AArch64 Linux compiler. The recorded toolchain is Arm
GNU 13.3.Rel1 / GCC13.3.1, target `aarch64-none-linux-gnu`:

```sh
export CROSS_COMPILE=aarch64-none-linux-gnu-
SDL2_LIB=/path/to/target/libSDL2-2.0.so.0.3200.8 sh tools/build-runtime.sh
```

The SDL2 input must be the target ARM64 library, not the host x86_64 library. It
can be extracted from the public image's unchanged `boot/knulli` rootfs using
mtools and unsquashfs. The PortMaster wrapper links to its SONAME and forwards
unwrapped functions to it. The script builds helpers under `build/`; it does not
write a device or mutate an IMG. A compiler version change can change hashes.

The kernel helper can be assembled and linked separately:

```sh
${CROSS_COMPILE}as -march=armv8.1-a src/display_repair.S -o build/repair.o
${CROSS_COMPILE}ld -T src/display_repair.ld build/repair.o -o build/repair.elf
```

The linker script enforces the original function capacities. See
`tools/historical/make_display_test_image.py` for old-byte/hash guards, branch
checks, modeled Unicorn execution cases and Android checksum regeneration.
The public candidate source repair is under `kernel/display-cleanup/`; its
platform source must also provide the nonempty cleanup implementation. These
are two different ways of expressing the repair, not two interchangeable modules.

## Mali module build inputs

Pinned driver source is included under `third_party/mali-valhall/`:

```sh
make -C third_party/mali-valhall/drivers/gpu/arm/midgard \
  KDIR=/path/to/reviewed-kernel-build ARCH=arm64 \
  CROSS_COMPILE=aarch64-none-linux-gnu- \
  CONFIG_MALI_MIDGARD=m CONFIG_MALI_PLATFORM_NAME=sunxi \
  CONFIG_MALI_CSF_SUPPORT=n CONFIG_MALI_GATOR_SUPPORT=y CONFIG_MALI_DEVFREQ=y
```

The complete recorded candidate options and compiler commands are in `kernel/`.
They identify the experiment, not a guarantee that any newly prepared kernel
headers match the installed vendor kernel. Module.symvers, generated headers,
export names, struct layouts and actual behavior need to agree. Do not use force
loading or a fake symvers file as a replacement for that validation.

Public kernel candidate:
`orangepi-xunlong/linux-orangepi@5b956b750422abd5e9e9c5523540d2aaf41a7939`.
It is the header/source candidate used in the recorded module rebuild, not the
proven exact source of the original kernel. The recovered config and normalized
candidate config differ in vendor symbols; keep `candidate-config-delta.json`.

## Image packaging audit

`tools/historical/build_distribution_v119.py` records the actual public conversion:
sanitize settings and recovery copies, remove only the added BIOS archive,
include PortMaster hooks, retain the base rootfs, then scrub FAT free clusters,
tail slack and deleted directory records. It checks changed files, known private
credential residues and the final image checksum. Earlier kernel/PWM tools are
also included. Their hash guards are intentional; do not remove them to make an
unrelated firmware pass.

The public IMG is the reproducible starting artifact for investigating the final
installed overlay. `release/BOOT_COMPONENTS.json` ties shipped binary adapters
and the Mali module to their exact hashes. All these checks are narrower than a
complete from-source firmware reproducibility claim.

## Public v1.0.1 packaging

The public raw IMG is a byte-for-byte promotion of the normal internal test8 image, SHA256 `b5d2193e0b88808c7457d8d714d422f8b927630e06bac432bf8067ea31377c42`. No new kernel, GPU module, BIOS collection or personal CRC cores were introduced by promotion. The public-default audit rechecked English, Wi-Fi off, no saved credentials in settings/recovery configs, no personal cores or game ROMs, and the existing BIOS policy.

Test8 kept the BOOT payload body and S06/S08 code from test7, built a normal baseline without the generated Mali guard, and used the actual manager modified() function to generate the active Mali bundle. It updated the recovery manifest, manager BOOT_SHA and autostart BASE_SHA, plus only the SHARE marker in the startup helper. The actual restore/arm functions were exercised for three cycles against temporary files, and transaction recovery and separate /run versus /var/run were checked. No block device or live GPU was used in those checks.

The new adapter sources are src/app_sdl_rotation.c, src/app_gl_rotation.c and src/od_commander_rotation.c. Runtime sources and effective S06/S08 are exported under overlay/. Binary hashes, including both BOOT copies and the embedded 8723ds module, are in release/BOOT_COMPONENTS.json. XZ integrity and both raw/compressed hashes are checked before upload; this is not a new full from-source firmware build.

## v1.0.2 packaging

Starting from v1.0.1, add the Ozone launcher, GLES3 helper and ACTIONPI_FIXES manifest entries, then synchronize the menu guard BOOT constant and MALI_MENU_TRIAL manifest with normal BOOT. Work on a separate IMG copy. Execute the actual guard with redirected file I/O: accept normal BOOT, reject armed BOOT and reproduce the old mismatch. Read back inserted files and compare all bytes outside the allowed FAT/file regions while calculating SHA256. Existing clean-default data is unchanged. tools/build-runtime.sh includes the new helper. Verify XZ integrity and compressed/unpacked hashes in one streaming pass.

## v1.0.3 packaging

Runtime sources live under config/userdata/system/. Merge the shared multimedia_keys.conf and edition-specific custom.sh into the initial settings archive; set telemetry=0 in both SHARE defaults and boot configuration. Keep STABLE_V119 as the internal installer path and refresh the settings-archive payload hash. Retain the existing Wi-Fi/Mali/BOOT/rotation files.

Requires Python 3, mtools (mcopy), and Linux or Ubuntu WSL with mtools. Extract both public v1.0.2 IMG editions, retaining their public filenames, set ACTIONPI_IMAGE_DIR to that directory, then run python3 tools/package-v1.0.3.py. The tool checks fixed input SHA256 values, creates new files only, preserves original tar members/core identities and compares every byte outside allowed FAT/file ranges. Gzip timestamp metadata means bit-for-bit reproducible output hashes are not claimed. After XZ compression use tools/verify-release.py to check integrity and unpacked IMG identity in one streaming read.

## v1.0.4

For the CRC edition, clear only the previous settings archive's clusters that FAT now marks free after replacement. This removes stale unallocated bytes, reduces XZ size below the release asset limit and changes no active filesystem files. The packaging tool performs this step before computing the final IMG checksum.

build/ppsspp-1.20.4 contains the actual build procedure, toolchain file, FFmpeg script and font patch. The release asset ppsspp-1.20.4.tar.xz is the official full source used. Use ARM GNU 13.3.1, CMake 3.31 and the matching target-sdk runtime extracted from the inherited image plus its development headers. Configure ACTIONPI_WORKDIR, ACTIONPI_BUILD_DIR and CMAKE_BIN; run build.sh followed by font-fix.sh. Compile src/v116_vulkan_output_rotation.c with aarch64-none-linux-gnu-gcc -shared -fPIC -O2 -Wall -Wextra -Werror -ldl and install identical copies as rotation/libvulkan.so and libvulkan.so.1 alongside the existing SDL rotation helper. See build/ppsspp-1.20.4/README.md for layout.

Set ACTIONPI_IMAGE_DIR to both v1.0.3 IMG files and ACTIONPI_PPSSPP_BUNDLE to the built application bundle, then run tools/package-v1.0.4.py. It adds the application/assets/licenses to the settings archive and updates both /boot runners and the payload checksum. It checks preserved tar members, unchanged CRC core hashes and every byte outside the permitted image regions. tools/verify-release.py verifies XZ integrity and unpacked IMG identity in a single pass.

## v1.0.5

kernel/zram contains the actual external module sources, normalized/recovered configurations, source identity, build script and capacity compatibility patch. The standard release includes the full pinned Orange Pi source archive identified by SOURCE.json; CRC uses the same source asset linked from the standard release. This is not claimed to be the original vendor kernel tree. tools/package-v1.0.5.py consumes both v1.0.4 IMG files, the verified ZRAM .ko bundle and supplied BennuGD binary. It adds only whitelisted BOOT files and core/loader archive entries, keeps ZRAM off initially and verifies all unchanged tar members and image bytes outside the permitted regions. No live device settings, backups, logs or credentials are inputs.
