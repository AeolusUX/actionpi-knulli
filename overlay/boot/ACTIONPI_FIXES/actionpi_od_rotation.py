"""OD-Commander only: correct its SDL2 software window surface in Mali mode."""
from pathlib import Path
import os, shutil, sys
BASE=Path('/boot/ACTIONPI_FIXES')
ORIGINAL=Path('/run/actionpi-od-commander-original')
MARK='# ACTIONPI_OD_SURFACE_WRAPPER'

def run(args):
    env=os.environ.copy()
    if env.get('ACTIONPI_MALI_SESSION')=='1':
        rotation={'app_output_rotation.so','retroarch_output_rotation.so',
                  'flycast_gl_rotation.so','od_commander_rotation.so'}
        existing=env.get('LD_PRELOAD','').replace(' ',':').split(':')
        retained=[item for item in existing if item and Path(item).name not in rotation]
        env['LD_PRELOAD']=':'.join([str(BASE/'od_commander_rotation.so'),*retained])
    os.execve(ORIGINAL,['/usr/bin/od-commander',*args],env)

def install():
    assert (BASE/'od_commander_rotation.so').is_file()
    path=Path('/usr/bin/od-commander')
    if not path.is_file():return False
    head=path.read_bytes()[:250]
    if MARK.encode() in head:return True
    if not head.startswith(b'\x7fELF'):return False
    if not ORIGINAL.exists():shutil.copy2(path,ORIGINAL)
    wrapper=('#!/usr/bin/python3\n'+MARK+'\nimport sys\n'
             'sys.path.insert(0,"/boot/ACTIONPI_FIXES")\n'
             'from actionpi_od_rotation import run\nrun(sys.argv[1:])\n')
    path.unlink();path.write_text(wrapper);path.chmod(0o755)
    return True

if __name__=='__main__':install()
