import hashlib,json,os,re,shutil,signal,struct,subprocess,sys,time
from pathlib import Path
B=Path('/boot/PPSSPP_VULKAN');T=Path(sys.argv[2]);CONFIG=Path('/userdata/system/configs/ppsspp')
KERNEL_SHA='52eb2334f61bad08c82cd0d5a27f11f93596b686b06019bc6948c7ef6a03847d'
sha=lambda b:hashlib.sha256(b).hexdigest()
def log(*a):print(time.strftime('%F %T'),*a,flush=True)
def write(p,data):
 with p.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def atomic(p,data):
 tmp=p.with_name(p.name+'.tmp');write(tmp,data);tmp.replace(p)
def jsonwrite(p,v):atomic(p,json.dumps(v,ensure_ascii=False,indent=2).encode())
def guard():
 assert int(Path('/sys/class/block/mmcblk0/size').read_text())*512==123773911040,'Not v116 test SD'
 with open('/dev/mmcblk0p3','rb') as f:
  h=f.read(4096);n=struct.unpack_from('<I',h,8)[0];page=struct.unpack_from('<I',h,36)[0];f.seek(page);kernel=f.read(n)
 assert sha(kernel)==KERNEL_SHA,'Not v116 kernel'
def tree(p):return {str(f.relative_to(p)):sha(f.read_bytes()) for f in p.rglob('*') if f.is_file()}

def restore_config():
 # Keep PPSSPP's own saved settings; original-config is an emergency backup only.
 atomic(T/'config-preserved',b'yes\n')
def run_game(game,seconds):
 from v116_vulkan_opacity import Opacity
 import select
 from evdev import InputDevice,ecodes
 guard();manifest={'game':game,'test_seconds':seconds};result={};p=None;opacity=None;pad=None
 try:
  if CONFIG.exists():shutil.copytree(CONFIG,T/'original-config')
  atomic(T/'config-backed-up',b'yes\n')
  # The verified D-pad mapping is already saved. Preserve user remapping too.
  settings=json.loads((B/'settings.json').read_text());rotation=int(settings['rotation']);assert rotation in (1,2,4)
  ini='[Graphics]\nGraphicsBackend = 3 (VULKAN)\nVulkanDevice = Mali-G57\nFullScreen = True\n[General]\nInternalScreenRotation = %d\nRemoteDebuggerOnStartup = False\nRemoteShareOnStartup = False\nEnableLogging = True\n'%rotation
  write(T/'vulkan.ini',ini.encode());result['rotation']=rotation
  for _ in range(120):
   if Path('/dev/dri/card0').exists():break
   time.sleep(.25)
  assert Path('/sys/bus/platform/devices/1800000.gpu/driver').resolve().name=='mali','Mali not active'
  env=os.environ.copy()
  for k in ['LD_PRELOAD','LD_LIBRARY_PATH','MESA_LOADER_DRIVER_OVERRIDE','WAYLAND_DISPLAY','DISPLAY']:env.pop(k,None)
  env.update(SDL_VIDEODRIVER='KMSDRM',SDL_KMSDRM_DEVICE_INDEX='0',SDL_KMSDRM_REQUIRE_DRM_MASTER='1',VK_ICD_FILENAMES='/usr/share/vulkan/icd.d/mali_icd.json',XDG_RUNTIME_DIR='/var/run',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/dbus/system_bus_socket',PULSE_SERVER='unix:/var/run/pulse/native')
  # Preserve the prior working SDL fallback bindings; correct only the D-pad.
  env['SDL_GAMECONTROLLERCONFIG']='19000000330100008811000000000000,adc_gamepad,x:b3,a:b0,b:b1,y:b2,back:b8,guide:b10,start:b9,dpleft:h0.8,dpdown:h0.4,dpright:h0.2,dpup:h0.1,leftshoulder:b4,lefttrigger:a2,rightshoulder:b6,rightshoulder:b5,righttrigger:a5,leftstick:b7,leftstick:b11,rightstick:b12,leftx:a0,lefty:a1,rightx:a3,righty:a4,platform:Linux,'
  if settings.get('full_output_rotation'):
   env['LD_LIBRARY_PATH']=str(B/'rotation');env['LD_PRELOAD']=str(B/'rotation'/'sdl_output_rotation.so');result['full_output_rotation']=True
  cmd=['/usr/bin/PPSSPP']+([manifest['game']] if manifest['game'] else [])+['--fullscreen','--appendconfig='+str(T/'vulkan.ini'),'--log='+str(T/'ppsspp.log'),'--loglevel=3']
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
  restore_config();os.sync();log('User config preserved; returning to same-boot menu')
 return 1 if result.get('error') or result.get('quit_timeout') or result.get('exit_code')!=0 else 0

if __name__=='__main__':sys.exit(run_game(sys.argv[1],int(sys.argv[3]) or None))
