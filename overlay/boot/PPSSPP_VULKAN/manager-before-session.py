"""v116 test-SD-only reboot launcher, with boot recovery before menu startup."""
import hashlib,json,os,re,shutil,signal,struct,subprocess,sys,time,zlib
from pathlib import Path
B=Path('/boot/PPSSPP_VULKAN');T=B/'transaction';H=B/'history'
TOKEN=b'initcall_blacklist=panfrost_driver_init'
BOOT=Path('/boot/partitions/BOOT.IMG');ENV=Path('/dev/mmcblk0p2');ENVFILE=Path('/boot/partitions/env.img');CONF=Path('/userdata/system/knulli.conf')
CONFIG=Path('/userdata/system/configs/ppsspp');SIZE=131072
BOOT_SHA='eb313e883c54ab7e3fec85148df1c5c4770b008cd95cd554da4f337819dcb5c8'
KERNEL_SHA='52eb2334f61bad08c82cd0d5a27f11f93596b686b06019bc6948c7ef6a03847d'
MODULE_SHA='a771b7b870a9669f51f7b372ca3ccdcdee356f691e5e6202f1e86755bd1c6fe9'
sha=lambda b:hashlib.sha256(b).hexdigest()
def log(*a):print(time.strftime('%F %T'),*a,flush=True)
def write(p,data):
 with p.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def atomic(p,data):
 tmp=p.with_name(p.name+'.tmp');write(tmp,data);tmp.replace(p)
def jsonwrite(p,v):atomic(p,json.dumps(v,ensure_ascii=False,indent=2).encode())
def guard():
 assert int(Path('/sys/class/block/mmcblk0/size').read_text())*512>=6069178368,'Not v116 test SD'
 with open('/dev/mmcblk0p3','rb') as f:
  h=f.read(4096);n=struct.unpack_from('<I',h,8)[0];page=struct.unpack_from('<I',h,36)[0];f.seek(page);kernel=f.read(n)
 assert sha(kernel)==KERNEL_SHA,'Not v116 kernel'
def envwrite(data):
 assert len(data)==SIZE and struct.unpack_from('<I',data)[0]==zlib.crc32(data[4:])
 write(ENVFILE,data)
 with ENV.open('r+b',buffering=0) as f:assert f.write(data)==SIZE;os.fsync(f.fileno())
 with ENV.open('rb') as f:assert f.read(SIZE)==data
def modified(env,boot):
 assert TOKEN not in env and len(env)==SIZE
 assert struct.unpack_from('<I',env)[0]==zlib.crc32(env[4:])
 payload=env[4:];end=payload.index(b'\0\0');entries=payload[:end].split(b'\0')
 idx=[i for i,v in enumerate(entries) if v.startswith(b'setargs_mmc=')];assert len(idx)==1
 entries[idx[0]]+=b' '+TOKEN;used=b'\0'.join(entries)+b'\0\0'
 assert set(payload[end+2:])<={0,255} and len(used)<=len(payload)
 new=used+payload[end+2:][:len(payload)-len(used)]
 newenv=struct.pack('<I',zlib.crc32(new))+new
 head=boot[:16384];assert head.count(b'exit 0\n')==1
 block=b"# ACTIONPI_PPSSPP_VULKAN_AUTOLOAD_GUARD\nmkdir -p /etc/modprobe.d\nprintf 'blacklist mali_kbase\\ninstall mali_kbase /bin/true\\n' > /etc/modprobe.d/99-actionpi-mali-first.conf\n"
 prefix=head[:head.index(b'exit 0\n')]+block+b'exit 0\n';assert len(prefix)<=16384
 return newenv,prefix.ljust(16384,b'\n')+boot[16384:]
def checked_backup():
 manifest=json.loads((T/'manifest.json').read_text())
 for name,digest in manifest['hashes'].items():assert sha((T/name).read_bytes())==digest,name
 return manifest
def restore_boot():
 checked_backup();write(BOOT,(T/'BOOT.IMG').read_bytes());envwrite((T/'ENV.bin').read_bytes())
def tree(p):return {str(f.relative_to(p)):sha(f.read_bytes()) for f in p.rglob('*') if f.is_file()}
def restore_all():
 restore_boot();write(CONF,(T/'knulli.conf').read_bytes())
 if (T/'config-backed-up').exists() and not (T/'config-restored').exists():
  if CONFIG.exists():shutil.move(str(CONFIG),str(T/'generated-config'))
  if (T/'original-config').exists():shutil.copytree(T/'original-config',CONFIG)
  assert tree(CONFIG)==tree(T/'original-config')
  atomic(T/'config-restored',b'yes\n')
def archive():
 H.mkdir(exist_ok=True);dest=H/time.strftime('%Y%m%d-%H%M%S');T.rename(dest);log('Archived',dest)
def request(game,test_seconds=None):
 guard();assert not T.exists(),'Previous transaction requires recovery'
 assert TOKEN.decode() not in Path('/proc/cmdline').read_text(),'GPU test already active'
 game=Path(game).resolve();assert game.is_file() and game.suffix.lower() in ('.iso','.cso','.chd')
 assert Path('/userdata/roms/psp').resolve() in game.parents
 assert sha((B/'mali_candidate.ko').read_bytes())==MODULE_SHA
 boot=BOOT.read_bytes();assert sha(boot)==BOOT_SHA
 with ENV.open('rb') as f:env=f.read(SIZE)
 assert ENVFILE.read_bytes()==env
 newenv,newboot=modified(env,boot);conf=CONF.read_bytes()
 T.mkdir();original={'BOOT.IMG':boot,'ENV.bin':env,'knulli.conf':conf}
 for n,data in original.items():write(T/n,data)
 jsonwrite(T/'manifest.json',{'hashes':{n:sha(d) for n,d in original.items()},'game':str(game),'test_seconds':test_seconds})
 try:
  write(BOOT,newboot)
  subprocess.run(['knulli-settings-set','system.es.atstartup','0'],check=True)
  jsonwrite(T/'request.json',{'game':str(game)})
  envwrite(newenv)
 except BaseException:restore_all();archive();raise
 log('Prepared one-shot Vulkan boot');os.sync();subprocess.run(['reboot'],check=True)
def boot():
 # S00bootcustom runs before the SHARE mount; defer all userdata access to S31.
 if not T.exists():return
 path=Path('/etc/init.d/S31emulationstation');old=path.read_bytes()
 marker=b'ACTIONPI_PPSSPP_VULKAN_GATE'
 if marker in old:return
 prefix=b'''#!/bin/sh
# ACTIONPI_PPSSPP_VULKAN_GATE (RAM only)
if [ "$1" = start ]; then
    python3 /boot/PPSSPP_VULKAN/v116_vulkan_manager.py gate >>/boot/PPSSPP_VULKAN/boot.log 2>&1
    [ "$?" = 42 ] && exit 0
fi
'''
 write(path,prefix+old);path.chmod(0o755)
def gate():
 guard();manifest=checked_backup()
 if TOKEN.decode() in Path('/proc/cmdline').read_text() and (T/'request.json').exists():
  (T/'request.json').rename(T/'active.json')
  # Restore next boot first. Keep ES disabled in this boot until the game exits.
  restore_boot();log('Next boot already restored; launching Vulkan game')
  with (T/'runner.log').open('ab') as out:
   subprocess.Popen([sys.executable,str(B/'v116_vulkan_manager.py'),'run'],stdout=out,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
  return 42
 log('Recovering interrupted test before normal menu startup');restore_all();archive();return 0
def run():
 from v116_vulkan_opacity import Opacity
 import select
 from evdev import InputDevice,ecodes
 guard();manifest=checked_backup();result={};p=None;opacity=None;pad=None
 try:
  if CONFIG.exists():shutil.copytree(CONFIG,T/'original-config')
  atomic(T/'config-backed-up',b'yes\n')
  controls=CONFIG/'PSP/SYSTEM/controls.ini'
  if controls.exists():
   text=controls.read_text(encoding='utf-8-sig');text,n=re.subn(r'^Up\s*=.*$','Up = 10-19',text,flags=re.M);assert n==1
   write(controls,text.encode('utf-8-sig'))
  settings=json.loads((B/'settings.json').read_text());rotation=int(settings['rotation']);assert rotation in (1,2,4)
  ini='[Graphics]\nGraphicsBackend = 3 (VULKAN)\nVulkanDevice = Mali-G57\nFullScreen = True\n[General]\nInternalScreenRotation = %d\nRemoteDebuggerOnStartup = False\nRemoteShareOnStartup = False\nEnableLogging = True\n'%rotation
  write(T/'vulkan.ini',ini.encode());result['rotation']=rotation
  for _ in range(120):
   if Path('/dev/dri/card0').exists():break
   time.sleep(.25)
  device=Path('/sys/bus/platform/devices/1800000.gpu/driver')
  assert not device.exists(),'GPU unexpectedly owned'
  assert sha((B/'mali_candidate.ko').read_bytes())==MODULE_SHA
  subprocess.run(['insmod',str(B/'mali_candidate.ko')],check=True,timeout=15)
  env=os.environ.copy()
  for k in ['LD_PRELOAD','LD_LIBRARY_PATH','MESA_LOADER_DRIVER_OVERRIDE','WAYLAND_DISPLAY','DISPLAY']:env.pop(k,None)
  env.update(SDL_VIDEODRIVER='KMSDRM',SDL_KMSDRM_DEVICE_INDEX='0',SDL_KMSDRM_REQUIRE_DRM_MASTER='1',VK_ICD_FILENAMES='/usr/share/vulkan/icd.d/mali_icd.json',XDG_RUNTIME_DIR='/var/run',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/dbus/system_bus_socket',PULSE_SERVER='unix:/var/run/pulse/native')
  env['SDL_GAMECONTROLLERCONFIG']='19000000330100008811000000000000,adc_gamepad,x:b3,a:b0,b:b1,y:b2,back:b8,guide:b10,start:b9,dpleft:h0.8,dpdown:h0.4,dpright:h0.2,dpup:h0.1,leftshoulder:b4,lefttrigger:a2,rightshoulder:b6,rightshoulder:b5,righttrigger:a5,leftstick:b7,leftstick:b11,rightstick:b12,leftx:a0,lefty:a1,rightx:a3,righty:a4,platform:Linux,'
  if settings.get('full_output_rotation'):
   env['LD_LIBRARY_PATH']=str(B/'rotation');env['LD_PRELOAD']=str(B/'rotation'/'sdl_output_rotation.so');result['full_output_rotation']=True
  cmd=['/usr/bin/PPSSPP',manifest['game'],'--fullscreen','--appendconfig='+str(T/'vulkan.ini'),'--log='+str(T/'ppsspp.log'),'--loglevel=3']
  try:pad=InputDevice('/dev/input/by-path/platform-rgp_joypad-event-joystick')
  except OSError as e:log('Exit combo reader unavailable',e)
  with (T/'console.log').open('wb') as out:
   p=subprocess.Popen(cmd,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True);result['pid']=p.pid;opacity=Opacity(p.pid)
   started=time.monotonic();applied=False;held=set();combo_since=None
   while p.poll() is None:
    elapsed=time.monotonic()-started
    if not applied:
     info=opacity.apply()
     if info:
      result['opacity']=info;applied=True;log('OPACITY_AUTO_APPLIED',info)
      write(T/'state-opaque.txt',Path('/sys/kernel/debug/dri/0/state').read_bytes());jsonwrite(T/'running.json',result)
     elif elapsed>30:raise TimeoutError('Opacity not applied within30s')
    if pad and select.select([pad.fd],[],[],0)[0]:
     for event in pad.read():
      if event.type==ecodes.EV_KEY:
       if event.value:held.add(event.code)
       else:held.discard(event.code)
    if {ecodes.BTN_SELECT,ecodes.BTN_START}<=held:
     if combo_since is None:combo_since=time.monotonic()
     if time.monotonic()-combo_since>=1:result['exit_reason']='SELECT+START';break
    else:combo_since=None
    if (T/'stop').exists():result['exit_reason']='test stop';break
    if manifest['test_seconds'] and elapsed>=manifest['test_seconds']:result['exit_reason']='test timeout';break
    time.sleep(.1)
 except BaseException as e:result['error']=repr(e);log('RUN_ERROR',repr(e))
 finally:
  if opacity:result['opacity_restore']=opacity.close()
  if pad:pad.close()
  if p:
   if p.poll() is None:
    p.send_signal(signal.SIGTERM)
    try:p.wait(timeout=15)
    except subprocess.TimeoutExpired:
     result['quit_timeout']=True;p.kill();p.wait(timeout=5)
   result['exit_code']=p.returncode
  jsonwrite(T/'result.json',result)
  restore_all();archive();os.sync();log('Restored; returning to menu');subprocess.run(['reboot'],check=True)
def main():
 mode=sys.argv[1]
 if mode=='request':request(sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else None)
 elif mode=='boot':boot()
 elif mode=='gate':sys.exit(gate())
 elif mode=='run':run()
 elif mode=='recover':guard();restore_all();archive()
 else:raise ValueError(mode)
if __name__=='__main__':main()


