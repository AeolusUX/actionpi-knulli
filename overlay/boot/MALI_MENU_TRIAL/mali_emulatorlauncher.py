#!/usr/bin/python3
"""RAM-only PSP dispatch; non-PSP calls retain the original launcher."""
import os,sys
args=sys.argv[1:]
def value(flag):
    return args[args.index(flag)+1] if flag in args and args.index(flag)+1<len(args) else None
if os.environ.get('ACTIONPI_MALI_SESSION')=='1' and value('-system')=='psp':
    sys.path.insert(0,'/boot/MALI_MENU_TRIAL')
    from mali_session import request_game
    request_game(value('-rom'))
elif os.environ.get('ACTIONPI_MALI_SESSION')=='1' and value('-system')=='emulators' and os.path.normpath(value('-rom') or '')=='/userdata/roms/emulators/PPSSPP.sh':
    sys.path.insert(0,'/boot/MALI_MENU_TRIAL')
    from mali_session import request_game
    request_game(ui_only=True)
else:
    # Observation preload is menu-only. Preserve original launcher's own settings/logic.
    os.environ.pop('LD_PRELOAD',None)
    if os.environ.get('ACTIONPI_MALI_SESSION')=='1':
        sys.path.insert(0,'/boot/MALI_MENU_TRIAL')
        from retroarch_rotation_launcher import launch
        launch()
        sys.exit(0)
    os.execv('/run/actionpi-emulatorlauncher-original',['emulatorlauncher']+args)
