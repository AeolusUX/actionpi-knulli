#!/usr/bin/python3
"""Action Pi 5.15.147: bounded service backed by runtime-tested external modules."""
from pathlib import Path
import fcntl,hashlib,json,os,subprocess,sys,time

ROOT=Path('/boot/ACTIONPI_ZRAM')
STATE=Path('/var/run/actionpi-zram.json')
PENDING=ROOT/'pending.json'
DISABLED=ROOT/'DISABLED'
ORDER=[('lzo_compress.ko','lzo_compress'),('lzo.ko','lzo'),('lzo-rle.ko','lzo_rle'),('zsmalloc.ko','zsmalloc'),('zram.ko','zram')]

def log(message):
    print('ACTIONPI_ZRAM '+message,flush=True)
    Path('/var/run/actionpi-zram-status').write_text(message+'\n')

def command(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=20)
    if r.returncode:raise RuntimeError(str(args)+': '+r.stderr.strip()+r.stdout.strip())

def save(path,value):
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('w') as f:
        json.dump(value,f);f.flush();os.fsync(f.fileno())
    tmp.replace(path)

def active():
    return any(s.split()[0]=='/dev/zram0' for s in Path('/proc/swaps').read_text().splitlines()[1:])

def modules():
    return {s.split()[0] for s in Path('/proc/modules').read_text().splitlines()}

def stop():
    if not STATE.exists():
        if active():raise RuntimeError('unowned active zram; refusing to alter it')
        log('OFF');return
    state=json.loads(STATE.read_text())
    # Never reset or unload while swapoff fails (e.g. insufficient free memory).
    if active():command(['swapoff','/dev/zram0'])
    p=Path('/sys/block/zram0/reset')
    if p.exists():p.write_text('1')
    for name in reversed(state['loaded']):
        if name in modules():command(['rmmod',name])
    STATE.unlink(missing_ok=True)
    log('OFF: swap disabled and owned modules unloaded')

def start():
    if DISABLED.exists():
        log('RECOVERY_DISABLED: '+DISABLED.read_text().strip());return
    boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if PENDING.exists():
        prior=json.loads(PENDING.read_text())
        if prior['boot_id']!=boot_id:
            DISABLED.write_text('Previous startup did not complete. Re-enable only after checking logs.\n')
            log('RECOVERY_DISABLED: incomplete previous boot startup');return
        raise RuntimeError('previous start in this boot did not complete')
    if active():
        if not STATE.exists():raise RuntimeError('unowned active zram')
        log('ON: already active');return
    # During boot, use the same settled menu state as the successful live trial.
    if float(Path('/proc/uptime').read_text().split()[0])<120:
        log('WAITING_FOR_MENU')
        deadline=time.monotonic()+100;seen=None;last_pid=None
        while time.monotonic()<deadline:
            pid=subprocess.run(['pidof','emulationstation'],capture_output=True,text=True,timeout=3).stdout.strip()
            if pid and pid==last_pid:
                if time.monotonic()-seen>=10:break
            else:seen=time.monotonic() if pid else None;last_pid=pid
            time.sleep(1)
        else:raise RuntimeError('menu did not stabilize; ZRAM was not loaded')
    assert Path('/proc/sys/kernel/osrelease').read_text().strip()=='5.15.147','kernel version changed'
    before=modules()
    assert not {'zram','zsmalloc'} & before,'other zram/zsmalloc module already loaded'
    manifest=json.loads((ROOT/'MODULES.json').read_text())
    for file,_ in ORDER:
        assert hashlib.sha256((ROOT/'modules'/file).read_bytes()).hexdigest()==manifest[file]['sha256'],file+' checksum mismatch'
    memory={s.split(':')[0]:int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith(('MemTotal:','MemAvailable:'))}
    assert memory['MemAvailable']>=128*1024*1024,'insufficient available RAM for starting'
    disk=(memory['MemTotal']//2)//4096*4096
    limit=min(memory['MemTotal']//4,512*1024*1024)//4096*4096
    state={'boot_id':boot_id,'loaded':[],'disksize':disk,'mem_limit':limit,'algorithm':'lzo-rle'}
    panic=Path('/proc/sys/kernel/panic');old_panic=panic.read_text()
    save(PENDING,{'boot_id':boot_id,'time':time.time()});save(STATE,state);os.sync()
    # Existing panic_on_oops is retained. Only bound the wait during module startup.
    panic.write_text('10')
    try:
        for file,name in ORDER:
            if name not in before:
                command(['insmod',str(ROOT/'modules'/file)]+(['num_devices=1'] if name=='zram' else []))
                state['loaded'].append(name);save(STATE,state)
        for _ in range(50):
            if Path('/dev/zram0').exists():break
            time.sleep(.1)
        p=Path('/sys/block/zram0')
        (p/'comp_algorithm').write_text('lzo-rle')
        (p/'disksize').write_text(str(disk));(p/'mem_limit').write_text(str(limit))
        command(['mkswap','/dev/zram0']);command(['swapon','-p','1000','/dev/zram0'])
        assert active(),'swap activation was not confirmed'
        PENDING.unlink();os.sync()
        log('ON: lzo-rle disksize='+str(disk)+' memory_limit='+str(limit))
    except BaseException:
        try:stop()
        except Exception as e:log('CLEANUP_FAILED: '+str(e))
        raise
    finally:
        panic.write_text(old_panic)

def main():
    action=sys.argv[1] if len(sys.argv)>1 else 'status'
    with open('/var/run/actionpi-zram.lock','w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if action=='start':start()
        elif action=='stop':stop()
        elif action=='restart':stop();start()
        elif action=='status':
            print('ON' if active() else 'OFF')
            if STATE.exists():print(STATE.read_text())
        elif action=='recover':
            DISABLED.write_text('Manually disabled for recovery.\n')
            command(['knulli-services','disable','zramswap']);stop()
        else:raise ValueError('start|stop|restart|status|recover')

if __name__=='__main__':
    try:main()
    except Exception as error:
        log('FAILED: '+str(error));sys.exit(1)
