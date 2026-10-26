#!/bin/bash
set -euo pipefail
root=${ACTIONPI_WORKDIR:-$PWD}
prep="$root/outputs/ppsspp-1.20.4-prep"
trial=${ACTIONPI_BUILD_DIR:-$root/ppsspp-build}
cmake=${CMAKE_BIN:-cmake}
python3 - "$trial/source/Common/Render/Text/draw_text_sdl.cpp" "$prep" <<'PY'
from pathlib import Path
import difflib,sys
p=Path(sys.argv[1]);prep=Path(sys.argv[2]);original=p.read_text()
data=original
if 'Action Pi: modern Noto family names' not in data:
    data=data.replace('const char *hardcodedNames[] = {','const char *hardcodedNames[] = {\n\t\t// Action Pi: modern Noto family names cover mixed Hangul/Latin.\n\t\t"Noto Sans KR",\n\t\t"NanumGothic",',1)
    for suffix in ('SC','TC','HK','JP','KR'):
        text='names.push_back("Noto Sans CJK '+suffix+'");'
        data=data.replace(text,text+'\n\t\tnames.push_back("Noto Sans '+suffix+'");')
    assert data!=original
    (prep/'font-fallback.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),data.splitlines(True),fromfile='a/Common/Render/Text/draw_text_sdl.cpp',tofile='b/Common/Render/Text/draw_text_sdl.cpp')))
    p.write_text(data)
(prep/'draw_text_sdl.font-fixed.cpp').write_text(data)
PY
"$cmake" --build "$trial/build" --target PPSSPPSDL -j2 > "$prep/font-fix-build.log" 2>&1
cp "$trial/build/PPSSPPSDL" "$prep/trial-bundle/PPSSPP-1.20.4"
/opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-strip --strip-unneeded "$prep/trial-bundle/PPSSPP-1.20.4"
sha256sum "$prep/trial-bundle/PPSSPP-1.20.4"
