"""Reconnect the previous ConnMan Wi-Fi service after SDIO firmware resumes."""
from pathlib import Path
import json,os,re,subprocess,sys,time
STATE=Path('/run/actionpi-wifi-before-sleep')

def command(*args,timeout=8):
    try:return subprocess.run(['connmanctl',*args],capture_output=True,text=True,timeout=timeout).stdout
    except (subprocess.TimeoutExpired,OSError):return ''

def prepare():
    service=None
    for line in command('services').splitlines():
        words=line.split()
        if len(words)>=2 and re.fullmatch(r'\*A[OR]',words[0]) and re.fullmatch(r'wifi_[A-Za-z0-9_]+',words[-1]):
            service=words[-1];break
    STATE.write_text(json.dumps({'token':time.time_ns(),'service':service}))
    os.sync()

def resume():
    saved=STATE.read_text();meta=json.loads(saved);service=meta.get('service')
    def current():return STATE.exists() and STATE.read_text()==saved
    def completed():
        if service:
            return bool(re.search(r'State\s*=\s*(ready|online)',command('services',service)))
        return any(line.lstrip().startswith(('*AO','*AR')) for line in command('services').splitlines())
    def log(message):print(time.strftime('%F %T'),message,flush=True)
    # The resume callback returns before the radio is ready for a new connection.
    time.sleep(2)
    if not current():return
    command('enable','wifi')
    for attempt in range(12):
        if not current():return
        if completed():
            STATE.unlink();log('Previous Wi-Fi connection restored');return
        if attempt==3:
            # Reproduce the user's successful manual off/on once, after firmware settles.
            command('disable','wifi');time.sleep(.5)
            if not current():return
            command('enable','wifi')
        if attempt in (1,4):command('scan','wifi')
        if service and attempt in (2,5,8):command('connect',service)
        time.sleep(1)
    log('Wi-Fi automatic recovery timed out; current settings retained')

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='resume':resume()
    else:raise ValueError('Unknown mode')
