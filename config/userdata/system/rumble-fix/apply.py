#!/usr/bin/env python3
"""Action Pi rumble calibration, confirmed on the user's device 2026-10-26."""
from pathlib import Path
import fcntl
import json
import sys
import time

BASE = Path('/sys/devices/platform/rgp_joypad')
HOME = Path('/userdata/system/rumble-fix')
TARGET = {'rumble_period': '40000', 'rumble_boost_strong': '32768',
          'rumble_boost_weak': '0', 'rumble_enable': '1'}
HOOK = '''#!/bin/sh
# ACTIONPI_RUMBLE_CALIBRATION: recreated from userdata at each boot.
case "$1" in
 suspend|hibernate) python3 /userdata/system/rumble-fix/apply.py suspend ;;
 resume|thaw) python3 /userdata/system/rumble-fix/apply.py resume ;;
esac
exit 0
'''

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'apply'
    with open('/run/actionpi-rumble-fix.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if mode == 'start':
            hook = Path('/etc/pm/sleep.d/98-actionpi-rumble')
            hook.write_text(HOOK)
            hook.chmod(0o755)
        for _ in range(100):
            if all((BASE / key).exists() for key in TARGET):
                break
            time.sleep(.1)
        else:
            raise RuntimeError('Joystick rumble sysfs is not ready')
        if mode == 'suspend':
            (BASE / 'rumble_enable').write_text('0')
            return
        before = {key: (BASE / key).read_text().strip() for key in TARGET}
        if before != TARGET:
            try:
                (BASE / 'rumble_enable').write_text('0')
                for key in ('rumble_period', 'rumble_boost_strong', 'rumble_boost_weak'):
                    (BASE / key).write_text(TARGET[key])
                (BASE / 'rumble_enable').write_text('1')
                after = {key: (BASE / key).read_text().strip() for key in TARGET}
                if after != TARGET:
                    raise RuntimeError('Rumble calibration readback mismatch')
            except BaseException:
                (BASE / 'rumble_enable').write_text('0')
                for key in ('rumble_period', 'rumble_boost_strong', 'rumble_boost_weak'):
                    (BASE / key).write_text(before[key])
                raise
        log = HOME / 'apply.log'
        if log.exists() and log.stat().st_size > 65536:
            log.replace(HOME / 'apply.previous.log')
        with log.open('a') as out:
            out.write(json.dumps({'time': time.time(), 'mode': mode,
                                  'boot': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                                  'values': TARGET}) + '\n')
        print('RUMBLE_CALIBRATION_OK', mode, json.dumps(TARGET))

if __name__ == '__main__':
    main()
