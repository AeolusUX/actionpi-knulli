#!/bin/bash
set -euo pipefail
here=$(cd -- "$(dirname -- "$0")" && pwd)
src=${ACTIONPI_KERNEL_SOURCE:?Set the extracted pinned kernel source directory}
out=${ACTIONPI_KERNEL_BUILD:?Set a writable kernel build directory}
module=${ACTIONPI_MODULE_BUILD:-$out/actionpi-zram-module}
cross=${CROSS_COMPILE:-/opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-}
mkdir -p "$out" "$module"
if ! grep -q -- '-Wno-enum-int-mismatch' "$src/Makefile"; then
    patch -d "$src" -p1 < "$here/001-fix-build.patch"
fi
cp "$here/candidate.config" "$out/.config"
make -C "$src" O="$out" ARCH=arm64 CROSS_COMPILE="$cross" olddefconfig modules_prepare
cp "$here/source/"* "$module/"
make -C "$src" O="$out" M="$module" ARCH=arm64 CROSS_COMPILE="$cross" KBUILD_MODPOST_WARN=1 -j2 modules
