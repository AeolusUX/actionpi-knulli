"""Bounded direct-ES trial; requires Mali and restored next-boot files already.
No module operations, boot writes, opacity changes, rotation changes or reboot.
The separate one-shot controller handles entry/recovery, not this process.
"""
import ctypes as c
import hashlib,json,os,re,signal,struct,subprocess,sys,time
from pathlib import Path

BASE=Path(__file__).resolve().parent
KERNEL='52eb2334f61bad08c82cd0d5a27f11f93596b686b06019bc6948c7ef6a03847d'
BOOT='fca98e6206df6d3f9b4b6a7fae05c2bfc75043d933ef4213ad960d4d430fbe63'
ENV='c6ce5d571c2b42835458ef082dc867ba1c71f4941426462f02d9faba606266ce'
def require(ok,text):
    if not ok: raise RuntimeError(text)
def digest(data):return hashlib.sha256(data).hexdigest()
def guard():
    require(int(Path('/sys/class/block/mmcblk0/size').read_text())*512>=6069178368,'Wrong SD')
    with open('/dev/mmcblk0p3','rb') as f:
        h=f.read(4096);n=struct.unpack_from('<I',h,8)[0];page=struct.unpack_from('<I',h,36)[0]
        require(h[:8]==b'ANDROID!' and 0<n<128*1024*1024 and page in (2048,4096,8192,16384),'Invalid boot header')
        f.seek(page);require(digest(f.read(n))==KERNEL,'Wrong kernel')
    require(Path('/sys/bus/platform/devices/1800000.gpu/driver').resolve().name=='mali','Mali must already own GPU')
    require(digest(Path('/boot/partitions/BOOT.IMG').read_bytes())==BOOT,'Next-boot overlay not restored')
    require(digest(Path('/boot/partitions/env.img').read_bytes())==ENV,'Next-boot ENV file not restored')
    with open('/dev/mmcblk0p2','rb') as f:require(digest(f.read(131072))==ENV,'Next-boot raw ENV not restored')
    for p in Path('/proc').glob('[0-9]*/comm'):
        try:name=p.read_text().strip()
        except OSError:continue
        require(name not in ('emulationstatio','emulationstation','sway-actionpi','sway','PPSSPP'),'A graphical application is still running: '+name)

def environment():
    env=os.environ.copy()
    for key in list(env):
        if key.startswith(('MESA_','WLR_','VK_','SDL_VIDEO','SDL_KMSDRM')) or key in (
          'LD_PRELOAD','LD_LIBRARY_PATH','LD_AUDIT','GALLIUM_DRIVER','LIBGL_ALWAYS_SOFTWARE',
          'LIBGL_DRIVERS_PATH','EGL_PLATFORM','__EGL_VENDOR_LIBRARY_FILENAMES',
          'WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','SDL_GAMECONTROLLERCONFIG',
          'SDL_OPENGL_LIBRARY','SDL_OPENGLES_LIBRARY','SDL_EGL_LIBRARY'):
            env.pop(key,None)
    vendor=str(BASE/'vendor')
    env.update(HOME='/userdata/system',XDG_RUNTIME_DIR='/var/run',PIPEWIRE_RUNTIME_DIR='/var/run',
       PULSE_SERVER='unix:/var/run/pulse/native',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/dbus/system_bus_socket',
       SDL_AUDIODRIVER='pipewire',SDL_NOMOUSE='1',SDL_VIDEODRIVER='KMSDRM',
       SDL_KMSDRM_DEVICE_INDEX='0',SDL_KMSDRM_REQUIRE_DRM_MASTER='1',
       LD_LIBRARY_PATH=vendor,SDL_VIDEO_EGL_DRIVER=vendor+'/libEGL.so.1',
       SDL_VIDEO_GL_DRIVER=vendor+'/libGLESv2.so.2',EGL_PLATFORM='gbm')
    setting=subprocess.run(['/usr/bin/knulli-settings-get','system.language'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
    lang=(setting.stdout.strip() if setting.returncode==0 else '') or 'en_US'
    require(re.fullmatch(r'[A-Za-z0-9_.@-]+',lang),'Unexpected locale')
    env.update(LANG=lang+'.UTF-8',LC_ALL=lang+'.UTF-8')
    return env

def snapshot(folder,label,pid=None):
    for name,path in [('state','/sys/kernel/debug/dri/0/state'),('clients','/sys/kernel/debug/dri/0/clients')]:
        try:(folder/(label+'-'+name+'.txt')).write_bytes(Path(path).read_bytes())
        except OSError as e:(folder/(label+'-'+name+'.txt')).write_text(str(e))
    if pid:
        try:(folder/(label+'-maps.txt')).write_text(Path('/proc/%d/maps'%pid).read_text())
        except OSError:pass

def master_available():
    # Briefly acquire/drop master without modesetting; never displace an existing owner.
    lib=c.CDLL('libdrm.so.2',use_errno=True)
    for name in ('drmSetMaster','drmDropMaster'):
        fn=getattr(lib,name);fn.argtypes=[c.c_int];fn.restype=c.c_int
    fd=os.open('/dev/dri/card0',os.O_RDWR|os.O_CLOEXEC)
    try:
        rc=lib.drmSetMaster(fd);err=c.get_errno() if rc else 0
        if rc==0:lib.drmDropMaster(fd)
        return {'available':rc==0,'errno':err}
    finally:os.close(fd)

def run(seconds=45):
    require(10<=seconds<=120,'Trial must be 10..120 seconds')
    guard()
    folder=Path('/boot/PPSSPP_VULKAN/transaction/menu-trial')
    require(folder.parent.is_dir(),'Needs existing guarded one-shot transaction')
    folder.mkdir(exist_ok=False)
    result={'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'scope':'menu display/exit only, no game launch'}
    proc=None
    try:
        result['master_before']=master_available()
        require(result['master_before']['available'],'DRM master is occupied')
        env=environment()
        with (folder/'egl.log').open('wb') as log:
            probe=subprocess.run([sys.executable,str(BASE/'probe_mali_menu_egl.py'),str(BASE/'vendor')],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=15)
        result['egl_returncode']=probe.returncode
        require(probe.returncode in (0,77),'EGL prerequisite failed; inspect egl.log')
        # Exit77 means only surfaceless is unavailable, not that a window cannot work.
        stop=folder/'stop';env['ACTIONPI_MENU_STOP']=str(stop)
        env['LD_PRELOAD']=str(BASE/'mali_menu_audit.so')
        (folder/'environment.json').write_text(json.dumps({k:v for k,v in env.items() if k.startswith(('SDL_','LD_','EGL_')) or k in ('HOME','LANG','LC_ALL','XDG_RUNTIME_DIR','PIPEWIRE_RUNTIME_DIR','PULSE_SERVER')},indent=2))
        snapshot(folder,'before')
        with (folder/'menu.log').open('wb') as log:
            proc=subprocess.Popen(['/usr/bin/emulationstation'],cwd='/userdata',env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            result['pid']=proc.pid;start=time.monotonic();captured=False
            while proc.poll() is None and time.monotonic()-start<seconds:
                if not captured and time.monotonic()-start>=5:
                    snapshot(folder,'running',proc.pid);captured=True
                time.sleep(.2)
            if proc.poll() is None:
                stop.write_text('quit\n');result['quit_method']='SDL_QUIT'
                try:proc.wait(timeout=12)
                except subprocess.TimeoutExpired:
                    result['quit_method']='SIGTERM fallback';os.killpg(proc.pid,signal.SIGTERM)
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        result['quit_method']='SIGKILL fallback';os.killpg(proc.pid,signal.SIGKILL)
                        proc.wait(timeout=5)
            result['returncode']=proc.returncode
        snapshot(folder,'after')
        result['master_after']=master_available()
        result['same_boot']=result['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        result['owner_after']=Path('/sys/bus/platform/devices/1800000.gpu/driver').resolve().name
        text=(folder/'menu.log').read_text(errors='replace')
        result['renderer_evidence']=[line for line in text.splitlines() if 'MALI_MENU_AUDIT GL_' in line]
        result['normal_quit']=result.get('quit_method')=='SDL_QUIT' and proc.returncode==0
        result['physical_display']='requires user confirmation; logs alone are insufficient'
        require(result['master_after']['available'],'DRM master was not released')
        require(result['same_boot'] and result['owner_after']=='mali','Boot or GPU owner changed')
        require(bool(result['renderer_evidence']),'No successful context evidence')
        require(result['normal_quit'],'Normal SDL quit not confirmed')
    except BaseException as e:
        result['error']=repr(e)
    finally:
        if proc and proc.poll() is None:
            os.killpg(proc.pid,signal.SIGKILL)
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:result['process_stuck']=True
        (folder/'result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2),flush=True)
    return 1 if 'error' in result else 0

if __name__=='__main__':sys.exit(run(int(sys.argv[1]) if len(sys.argv)>1 else 45))
