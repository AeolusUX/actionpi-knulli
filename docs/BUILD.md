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
