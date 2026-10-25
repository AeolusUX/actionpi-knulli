"""Bounded pre-driver readiness retries; never retry a started power cycle."""
from pathlib import Path
import errno,fcntl,json,os,time
ROOT=Path('/')
CHECKS=5
INTERVAL=.25
MODULES={'8723ds','aic8800_bsp','aic8800_fdrv','aic8800_btlpm','hci_uart','hci_h5','btusb','aic_btusb','aic_uart'}
PAIRS=[('/sys/class/misc/sunxi-wlan/rf-ctrl/power_state','/sys/class/misc/sunxi-wlan/rf-ctrl/scan_device'),
       ('/sys/class/misc/sunxi-rfkill/wlan/state','/sys/class/misc/sunxi-rfkill/wlan/scan')]
GUARD_TEXT=''.join('blacklist '+n+'\ninstall '+n+' /bin/false\n' for n in ['8723ds','aic8800_bsp','aic8800_fdrv','aic8800_btlpm'])
class Busy(Exception):pass
class NotReady(Exception):pass
def p(name):return ROOT/name.lstrip('/')
def state(path):
    value=path.read_text().strip()
    if value not in ('0','1'):raise ValueError('invalid state')
    return int(value)
def write_state(path,value):
    path.write_text(str(value)+'\n')
    if state(path)!=value:raise RuntimeError('state did not change')
def unused():
    loaded={line.split()[0] for line in p('/proc/modules').read_text().splitlines() if line.split()}
    if loaded & MODULES:raise Busy('RADIO_MODULE_PRESENT')
    if any((x/'wireless').exists() for x in p('/sys/class/net').glob('*')):raise Busy('WIRELESS_INTERFACE_PRESENT')
    if any((x/'driver').exists() for x in p('/sys/bus/sdio/devices').glob('*')):raise Busy('BOUND_SDIO_DEVICE')
    bt=p('/sys/class/misc/sunxi-rfkill/bluetooth/state')
    if not bt.exists():raise NotReady('BT_STATE_MISSING')
    if state(bt)!=0:raise Busy('BT_POWERED')
    for x in p('/sys/class/rfkill').glob('rfkill*'):
        if (x/'type').read_text().strip()=='bluetooth' and state(x/'soft')!=1:raise Busy('BT_UNBLOCKED')
def ready():
    unused()
    pair=next(((p(a),p(b)) for a,b in PAIRS if p(a).exists() and p(b).exists()),None)
    if pair is None:raise NotReady('POWER_INTERFACE_MISSING')
    return pair,state(pair[0])
def transient(exc):
    return isinstance(exc,NotReady) or isinstance(exc,OSError) and exc.errno in (errno.ENOENT,errno.ENODEV,errno.EAGAIN)
def mark(name,**data):
    directory=p('/run/actionpi-wifi-power');directory.mkdir(parents=True,exist_ok=True)
    try:boot=p('/proc/sys/kernel/random/boot_id').read_text().strip()
    except OSError:boot='unknown'
    data.update(status=name,boot_id=boot,uptime_seconds=round(time.monotonic(),3))
    target=directory/(name+'.json');temp=target.with_name(target.name+'.'+str(os.getpid())+'.tmp')
    encoded=json.dumps(data,sort_keys=True)+'\n'
    temp.write_text(encoded);temp.replace(target)
    current=directory/'status.json';temp=current.with_name('status.'+str(os.getpid())+'.tmp')
    temp.write_text(encoded);temp.replace(current)
def terminal(name,reason,**data):
    mark(name,reason=reason,**data)
    p('/run/actionpi-wifi-power-once').write_text(name+'\n')
    return name.upper()+':'+reason
def run_locked():
    directory=p('/run/actionpi-wifi-power');unsafe=p('/run/actionpi-wifi-power-unsafe')
    for name in ('success','failure','blocked','disabled'):
        if (directory/(name+'.json')).exists():return 'ALREADY_TERMINAL_THIS_BOOT:'+name
    if p('/boot/DISABLE_WIFI_POWER_INIT.txt').exists():return terminal('disabled','DISABLED_BY_FLAG')
    if unsafe.exists():return terminal('blocked','EXISTING_UNSAFE_STATE')
    if p('/run/actionpi-wifi-power-once').exists():return terminal('blocked','LEGACY_ATTEMPT_PRESENT')
    guard=p('/etc/modprobe.d/98-actionpi-power-test5.conf')
    pair=None;initial=None;owned=False
    for check in range(1,CHECKS+1):
        try:
            if p('/boot/DISABLE_WIFI_POWER_INIT.txt').exists():return terminal('disabled','DISABLED_BY_FLAG')
            pair,initial=ready()
            with guard.open('x') as stream:
                owned=True;stream.write(GUARD_TEXT)
            unused()
            state(pair[0])
            break
        except (OSError,ValueError,Busy,NotReady) as exc:
            if owned:guard.unlink();owned=False
            if isinstance(exc,Busy):return terminal('blocked',str(exc),checks=check)
            if isinstance(exc,FileExistsError):return terminal('blocked','EXISTING_GUARD',checks=check)
            if not transient(exc):return terminal('failure','PRECHECK_'+type(exc).__name__,checks=check,power_started=False)
            mark('waiting',checks=check,reason=str(exc) if isinstance(exc,NotReady) else type(exc).__name__)
            if check==CHECKS:return terminal('failure','READINESS_TIMEOUT',checks=check,power_started=False)
            time.sleep(INTERVAL)
    touched=False;cycle_completed=False
    try:
        mark('attempt',initial_state=initial,checks=check)
        unsafe.write_text('power transition in progress\n')
        for value in (1,0,1):
            unused()
            touched=True;write_state(pair[0],value)
            if value==0:time.sleep(.2)
        time.sleep(.1)
        unused();pair[1].write_text('1\n');cycle_completed=True
        p('/run/actionpi-wifi-power-once').write_text('success\n')
        mark('success',reason='POWER_STATE_CYCLE_AND_RESCAN_REQUESTED',final_state=1)
        unsafe.unlink()
        return 'SUCCESS:POWER_STATE_CYCLE_AND_RESCAN_REQUESTED'
    except (OSError,ValueError,RuntimeError,Busy,NotReady) as exc:
        if cycle_completed:
            (directory/'success.json').unlink(missing_ok=True)
            return terminal('failure','RESULT_RECORDING_'+type(exc).__name__,power_started=True,cycle_completed=True,wifi_start_blocked=unsafe.exists())
        restored=not touched
        if touched:
            try:
                if state(pair[0])!=initial:
                    unused()
                    write_state(pair[0],initial)
                    if initial:
                        unused();pair[1].write_text('1\n')
                restored=True
            except (OSError,ValueError,RuntimeError,Busy,NotReady):restored=False
        if restored:unsafe.unlink(missing_ok=True)
        else:unsafe.write_text('initial power state could not be safely restored\n')
        (directory/'success.json').unlink(missing_ok=True)
        return terminal('failure','POWER_PHASE_'+type(exc).__name__,power_started=touched,initial_state_restored=restored,wifi_start_blocked=not restored)
    finally:
        if owned:guard.unlink(missing_ok=True)
def run():
    directory=p('/run/actionpi-wifi-power');directory.mkdir(parents=True,exist_ok=True)
    with (directory/'lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return 'BUSY:ANOTHER_HELPER_RUNNING'
        return run_locked()
if __name__=='__main__':
    try:print(run(),flush=True)
    except (OSError,ValueError) as exc:print('SETUP_FAILED:'+type(exc).__name__,flush=True)
