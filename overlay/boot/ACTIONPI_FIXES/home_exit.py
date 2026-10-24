"""HOME: request the active emulator's normal exit; never target ES."""
from pathlib import Path
import fcntl,json,os,signal,sys,time

ACTIVE=Path('/run/actionpi-active-emulator.json')
SESSION=Path('/boot/PPSSPP_VULKAN/transaction/session')

def stamp(pid):
    return Path('/proc/%d/stat'%pid).read_text().rsplit(')',1)[1].split()[19]

def register(pid,program):
    try:
        data={'pid':pid,'start':stamp(pid),'program':program}
        tmp=ACTIVE.with_suffix('.tmp');tmp.write_text(json.dumps(data));tmp.replace(ACTIVE)
    except OSError:pass

def alive(data):
    try:return stamp(data['pid'])==data['start']
    except (OSError,ProcessLookupError):return False

def exit_game():
    with open('/run/actionpi-home-exit.lock','w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return
        state=SESSION/'state.json'
        if state.exists():
            s=json.loads(state.read_text())
            if s.get('phase')=='game' and s.get('boot_id')==Path('/proc/sys/kernel/random/boot_id').read_text().strip():
                folder=Path(s['folder']).resolve()
                if folder.is_relative_to(SESSION.resolve()):
                    # Disabled after a live PPSSPP quit timeout triggered fallback.
                    # Keep SELECT+START as the known working exit until diagnosed.
                    return
        if not ACTIVE.exists():return
        data=json.loads(ACTIVE.read_text())
        if not alive(data):return
        program=Path(data['program']).name
        if program in ('emulationstation','python3','sh','bash'):return
        keys=None
        from evdev import UInput,ecodes
        if program=='retroarch':keys=[ecodes.KEY_LEFTSHIFT,ecodes.KEY_ESC]
        elif program=='flycast':keys=[ecodes.KEY_F7]
        if keys:
            with UInput({ecodes.EV_KEY:keys},name='ActionPi HOME exit') as keyboard:
                time.sleep(.2)
                for key in keys:keyboard.write(ecodes.EV_KEY,key,1)
                keyboard.syn();time.sleep(.15)
                for key in reversed(keys):keyboard.write(ecodes.EV_KEY,key,0)
                keyboard.syn();time.sleep(.1)
            for _ in range(20):
                if not alive(data):return
                time.sleep(.1)
        if alive(data):os.kill(data['pid'],signal.SIGTERM)

if __name__=='__main__':exit_game()
