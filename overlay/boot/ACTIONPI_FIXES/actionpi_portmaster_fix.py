"""Select the rotation DLL only in PortMaster's Python SDL process."""
from pathlib import Path
import os

BASE=Path('/boot/ACTIONPI_FIXES')
LAUNCHER=Path('/userdata/roms/ports/PortMaster.sh')
MARK='# ACTIONPI_PORTMASTER_ROTATION'

def prepare():
    if not LAUNCHER.is_file():return False
    assert Path('/boot/boot/knulli.board').read_text().strip()=='helegany-action-pi'
    assert (BASE/'portmaster-sdl/libSDL2.so').is_file()
    text=LAUNCHER.read_text()
    if MARK in text:return False
    anchor='export PYSDL2_DLL_PATH="/usr/lib"'
    if text.count(anchor)!=1:raise RuntimeError('Unknown PortMaster SDL loader setting')
    backup=BASE/'portmaster-before-rotation.sh'
    if not backup.exists():backup.write_bytes(LAUNCHER.read_bytes())
    correction='''
# ACTIONPI_PORTMASTER_ROTATION
if [ "${ACTIONPI_MALI_SESSION:-}" = 1 ] && [ -f /boot/ACTIONPI_FIXES/portmaster-sdl/libSDL2.so ]; then
  export PYSDL2_DLL_PATH="/boot/ACTIONPI_FIXES/portmaster-sdl"
fi
'''
    LAUNCHER.write_text(text.replace(anchor,anchor+correction));LAUNCHER.chmod(0o755)
    os.sync();return True

if __name__=='__main__':print('PortMaster rotation launcher updated:',prepare())
