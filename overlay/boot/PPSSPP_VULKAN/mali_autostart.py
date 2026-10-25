"""v116 only: disarm next boot before GPU startup, re-arm after a healthy menu."""
import importlib.util,json,os,shutil,subprocess,sys,time
from pathlib import Path

B=Path('/boot/PPSSPP_VULKAN');F=B/'autostart-backup'
FLAG=B/'autostart-enabled.json';ATTEMPT=B/'autostart-attempt.json'
BASE_SOURCE=B/'manager-before-session.py'
BASE_SHA='2e3b3705d6d2ebc2aff70f032320146a7732865230a126b9f5c687517bd8d0f2'
RECOVERY=(Path('/boot/DISABLE_MALI'),Path('/boot/DISABLE_MALI.txt'))
_base=None

def base():
    global _base
    if _base is None:
        import hashlib
        if hashlib.sha256(BASE_SOURCE.read_bytes()).hexdigest()!=BASE_SHA:raise RuntimeError('Original manager mismatch')
        spec=importlib.util.spec_from_file_location('mali_original',BASE_SOURCE)
        _base=importlib.util.module_from_spec(spec);spec.loader.exec_module(_base)
    return _base

def enabled():
    return FLAG.exists() and json.loads(FLAG.read_text()).get('enabled') is True
def recovery_requested():return any(p.exists() for p in RECOVERY)
def token_present():return base().TOKEN.decode() in Path('/proc/cmdline').read_text()
def set_enabled(value,reason):
    base().jsonwrite(FLAG,{'enabled':bool(value),'reason':reason,'time':time.strftime('%F %T')})

def verified_backup():
    m=base();meta=json.loads((F/'manifest.json').read_text())
    for name,digest in meta['hashes'].items():
        if m.sha((F/name).read_bytes())!=digest:raise RuntimeError('Recovery backup corrupted: '+name)
    return meta

def restore_boot():
    m=base();verified_backup()
    m.write(m.BOOT,(F/'BOOT.IMG').read_bytes());m.envwrite((F/'ENV.bin').read_bytes());os.sync()

def arm_boot():
    m=base();verified_backup()
    env,boot=m.modified((F/'ENV.bin').read_bytes(),(F/'BOOT.IMG').read_bytes())
    # Overlay guard must be durable before changing the actual boot arguments.
    m.write(m.BOOT,boot);os.sync();m.envwrite(env);os.sync()
    return {'boot_sha':m.sha(boot),'env_sha':m.sha(env)}

def archive_pending():
    m=base();m.H.mkdir(exist_ok=True)
    stem=time.strftime('%Y%m%d-%H%M%S');dest=m.H/stem;n=0
    while dest.exists():n+=1;dest=m.H/(stem+'-'+str(n))
    m.T.rename(dest);m.log('Archived',dest)

def recover_pending():
    m=base()
    if not m.T.exists():return
    meta=m.checked_backup()
    if not meta.get('auto_mali'):
        m.restore_all() # Legacy one-shot tests temporarily changed system.es.atstartup.
    else:
        # Automatic sessions never change knulli.conf. Restoring its historical
        # snapshot here discards language/timezone/Wi-Fi/other user changes.
        m.restore_boot()
        # PPSSPP settings belong to the user, including changes made before
        # interrupted shutdowns. Automatic mode never rolls back this directory.
    archive_pending()

def prepare_transaction():
    m=base();m.T.mkdir()
    data={'BOOT.IMG':(F/'BOOT.IMG').read_bytes(),'ENV.bin':(F/'ENV.bin').read_bytes(),'knulli.conf':m.CONF.read_bytes()}
    for name,value in data.items():m.write(m.T/name,value)
    m.jsonwrite(m.T/'manifest.json',{'hashes':{n:m.sha(v) for n,v in data.items()},'auto_mali':True,'game':'','test_seconds':None})

def schedule_reboot():
    os.sync();subprocess.Popen(['/sbin/reboot'],close_fds=True,start_new_session=True)

def boot():
    m=base()
    if not (enabled() or recovery_requested() or m.T.exists() or token_present()):return
    # S00 is before SHARE. Only install a RAM gate here; userdata is accessed at S31.
    path=Path('/etc/init.d/S31emulationstation');old=path.read_bytes()
    if b'ACTIONPI_MALI_AUTOSTART_GATE' in old:return
    prefix=b'''#!/bin/sh
# ACTIONPI_MALI_AUTOSTART_GATE (RAM only)
if [ "$1" = start ]; then
    python3 /boot/PPSSPP_VULKAN/mali_autostart.py gate >>/boot/PPSSPP_VULKAN/boot.log 2>&1
    [ "$?" = 42 ] && exit 0
fi
'''
    m.write(path,prefix+old);path.chmod(0o755)

def gate():
    m=base();m.guard();token=token_present()
    sys.path.insert(0,'/boot/ACTIONPI_FIXES')
    from actionpi_pwm_normalize import normalize
    m.log('PWM_NORMALIZE',normalize('boot'))
    if recovery_requested() or (enabled() and not token):
        set_enabled(False,'Recovery file or fallback boot');restore_boot();recover_pending()
        if token:schedule_reboot();return 42
        return 0
    if not enabled():
        if m.T.exists():
            meta=m.checked_backup()
            if meta.get('auto_mali'):
                restore_boot();recover_pending()
                if token:schedule_reboot();return 42
                return 0
            return m.gate() # Retain old, explicit one-game test behavior when disabled.
        if token:
            restore_boot();schedule_reboot();return 42
        return 0
    # The next boot is normal before any module loading or menu work is attempted.
    restore_boot();recover_pending();prepare_transaction()
    m.jsonwrite(ATTEMPT,{'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'phase':'starting'})
    with (m.T/'runner.log').open('ab') as log:
        subprocess.Popen([sys.executable,str(B/'mali_autostart.py'),'auto-run'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
    return 42

def run():
    m=base();m.guard();m.checked_backup();p=None;healthy=False
    try:
        if not m.CONFIG.is_dir():raise RuntimeError('Missing PSP config')
        if Path('/sys/bus/platform/devices/1800000.gpu/driver').exists():raise RuntimeError('GPU already owned')
        if m.sha((B/'mali_candidate.ko').read_bytes())!=m.MODULE_SHA:raise RuntimeError('Module mismatch')
        subprocess.run(['insmod',str(B/'mali_candidate.ko')],check=True,timeout=15)
        p=subprocess.Popen([sys.executable,'/boot/MALI_MENU_TRIAL/mali_session.py','run'])
        start=time.monotonic();seen=None;pid=None;s=m.T/'session'
        boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        while p.poll() is None and time.monotonic()-start<90:
            state_path=s/'state.json'
            if state_path.exists():
                state=json.loads(state_path.read_text())
                if state.get('phase')=='menu' and state.get('boot_id')==boot_id:
                    current=state['pid']
                    if current!=pid:pid=current;seen=time.monotonic()
                    log=Path(state['folder'])/'menu.log'
                    if time.monotonic()-seen>=8 and Path('/proc/%d'%pid).exists() and 'MALI_MENU_AUDIT GL_1f01=Mali-G57' in log.read_text(errors='replace'):
                        armed=arm_boot();healthy=True
                        m.jsonwrite(ATTEMPT,dict(phase='healthy',boot_id=boot_id,menu_pid=pid,**armed))
                        m.log('MALI_AUTOSTART_HEALTHY',boot_id,pid);break
                else:pid=None;seen=None
            time.sleep(.25)
        if not healthy:raise RuntimeError('Menu startup did not become healthy within90s')
        rc=p.wait()
        if rc==0 and enabled() and not (s/'stop-session').exists():
            # A normal ES exit can be part of an intentional poweroff/reboot.
            # Preserve the armed next boot; recovery of this transaction occurs at next S31.
            m.log('Menu exited normally; retaining automatic next boot');return
        raise RuntimeError('Session stopped or failed, rc='+str(rc))
    except BaseException as e:
        m.log('MALI_AUTOSTART_FALLBACK',repr(e));set_enabled(False,repr(e));restore_boot()
        if p and p.poll() is None:
            s=m.T/'session'
            if s.exists():(s/'stop-session').touch()
            try:p.wait(timeout=25)
            except subprocess.TimeoutExpired:
                p.terminate()
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
        recover_pending();schedule_reboot()

def disable():
    m=base();m.guard();verified_backup();set_enabled(False,'User requested original menu');restore_boot()
    s=m.T/'session'
    if s.exists() and (s/'state.json').exists():
        (s/'stop-session').touch() # Running controller does the ordered cleanup/reboot.
    else:recover_pending();schedule_reboot()

def enable():
    m=base();m.guard();verified_backup()
    if m.T.exists() or token_present():raise RuntimeError('Enable only from a clean normal boot')
    if recovery_requested():raise RuntimeError('Remove DISABLE_MALI recovery file before enabling')
    try:set_enabled(True,'User enabled automatic Mali menu');arm_boot()
    except BaseException:
        set_enabled(False,'Enable failed');restore_boot();raise
    schedule_reboot()

def dispatch():
    mode=sys.argv[1];m=base()
    if mode=='boot':boot()
    elif mode=='gate':sys.exit(gate())
    elif mode=='auto-run':run()
    elif mode=='enable':enable()
    elif mode=='disable':disable()
    elif mode=='request' and enabled():
        subprocess.run([sys.executable,'/boot/MALI_MENU_TRIAL/mali_session.py','request',sys.argv[2]],check=True)
    else:m.main()

if __name__=='__main__':dispatch()
