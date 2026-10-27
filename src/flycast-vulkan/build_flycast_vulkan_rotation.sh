#!/bin/bash
set -euo pipefail
root="${ACTIONPI_PROJECT_ROOT:?Set the extracted source bundle root}"
out="${1:-$root/outputs/flycast-vulkan-trial/rotation}"
mkdir -p "$out"
compiler=/root/actionpi-flycast-vulkan-trial/host-tools/usr/bin/glslangValidator
for stage in vert frag;do
 "$compiler" -V --target-env vulkan1.0 -S "$stage" "$root/work/flycast_vulkan_rotate.$stage" -o "$out/rotation.$stage.spv"
done
python3 - "$out" <<'PY'
import pathlib,struct,sys
p=pathlib.Path(sys.argv[1]);text='#include <stdint.h>\n'
for s in ['vert','frag']:
 data=(p/('rotation.'+s+'.spv')).read_bytes();words=struct.unpack('<%dI'%(len(data)//4),data)
 text+='static const uint32_t rotation_'+s+'[]={'+','.join(hex(w) for w in words)+'};\n'
(p/'flycast_rotation_spv.h').write_text(text)
PY
prefix=/opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-
sdk="$root/outputs/ppsspp-1.20.4-prep/target-sdk"
# The real loader shares this SONAME. Keep our earlier lookup registered across
# RetroArch's dlclose/reopen on AV-info changes; otherwise the real loader wins.
"${prefix}gcc" -shared -fPIC -O2 -Wall -Wextra -Wno-misleading-indentation -Wl,-Bsymbolic-functions,-soname,libvulkan.so.1,-z,nodelete \
 -I"$sdk/usr/include" -I"$out" "$root/work/flycast_vulkan_rotation.c" -ldl -o "$out/libvulkan.so.1"
ln -sf libvulkan.so.1 "$out/libvulkan.so"
"${prefix}readelf" -h -d "$out/libvulkan.so.1" > "$out/ELF.txt"
sha256sum "$out/libvulkan.so.1"
