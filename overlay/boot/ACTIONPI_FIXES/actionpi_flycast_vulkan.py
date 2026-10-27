"""Scoped Flycast Vulkan dispatch through the existing fixed-Mali supervisor."""
from pathlib import Path
import fcntl,json,os,re,signal,socket,subprocess,sys,time,uuid
BASE=Path('/userdata/system/flycast-vulkan')
SUP=Path('/boot/PPSSPP_VULKAN/transaction/session')
PENDING=Path('/run/actionpi-flycast-vulkan-request.json')
CORES={'flycast':'standard','flycastvl':'vl','flycast-xtreme':'xtreme'}
MARKER='flycast-vulkan-active.json'

def atomic(path,value):
 tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(value));tmp.replace(path)

def core_name(args):
 for i,a in enumerate(args[:-1]):
  if a in ('-L','--libretro'):return Path(args[i+1]).name.removesuffix('_libretro.so')
 return None

def request(args):
 core=core_name(args)
 if core not in CORES or Path('/boot/ACTIONPI_FIXES/DISABLE_FLYCAST_VULKAN').exists():return False
 assert (BASE/'cores'/('flycast-'+CORES[core]+'-vulkan_libretro.so')).is_file(),'Vulkan core missing'
 with open('/run/actionpi-flycast-vulkan.lock','w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  state=json.loads((SUP/'state.json').read_text());boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
  assert state['phase']=='menu' and state['boot_id']==boot,'Menu not ready'
  assert not (SUP/'request.json').exists(),'Another request pending'
  if PENDING.exists():
   old=json.loads(PENDING.read_text());assert old.get('boot_id')!=boot or old.get('expires',0)<time.monotonic(),'Flycast request pending'
   PENDING.unlink()
  folder=SUP/('game-%02d'%(state['completed_games']+1))
  governors={str(p):p.read_text().strip() for p in Path('/sys/devices/system/cpu/cpufreq').glob('policy*/scaling_governor')}
  env={k:os.environ[k] for k in ('SDL_GAMECONTROLLERCONFIG','SDL_AUDIODRIVER','LANG','LC_ALL') if k in os.environ}
  configs={}
  for i,a in enumerate(args):
   values=[]
   if a in ('-c','--config','--appendconfig') and i+1<len(args):values=args[i+1].split('|')
   elif a.startswith('--appendconfig='):values=a.split('=',1)[1].split('|')
   for name in values:
    p=Path(name)
    if p.is_file() and p.stat().st_size<8*1024*1024:configs[name]=p.read_text()
  job={'args':list(args),'configs':configs,'core':core,'boot_id':boot,'folder':str(folder),'expires':time.monotonic()+60,'id':uuid.uuid4().hex,'governors':governors,'nice':os.getpriority(os.PRIO_PROCESS,0),'env':env}
  atomic(PENDING,job)
  try:atomic(SUP/'request.json',{'ui_only':True,'game':None,'seconds':None})
  except BaseException:
   PENDING.unlink(missing_ok=True);raise
 return True

def append_config(args,path):
 args=list(args)
 for i,x in enumerate(args):
  if x=='--appendconfig' and i+1<len(args):args[i+1]+='|'+str(path);return args
  if x.startswith('--appendconfig='):args[i]=x+'|'+str(path);return args
 return args+['--appendconfig',str(path)]

def handle(argv):
 if len(argv)<2 or argv[0] or not PENDING.exists():return False
 job=json.loads(PENDING.read_text());boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
 if job.get('boot_id')!=boot or job.get('expires',0)<time.monotonic():PENDING.unlink(missing_ok=True);return False
 if job.get('folder')!=str(Path(argv[1])):return False
 state=json.loads((SUP/'state.json').read_text())
 assert state['phase']=='game' and state['folder']==job['folder'] and state['boot_id']==boot
 PENDING.unlink();run(job,Path(argv[1]));return True

def run(job,folder):
 result={'kind':'flycast-vulkan','core':job['core'],'boot_id':job['boot_id']};p=None;saved={};marker=folder/MARKER
 try:
  core=BASE/'cores'/('flycast-'+CORES[job['core']]+'-vulkan_libretro.so')
  cfg=folder/'flycast-vulkan.cfg'
  cfg.write_text('video_driver = "vulkan"\nvideo_context_driver = "khr_display"\nvideo_rotation = "0"\nvideo_fullscreen = "true"\nvideo_fullscreen_x = "960"\nvideo_fullscreen_y = "720"\nvideo_windowed_fullscreen = "false"\nvideo_threaded = "false"\nvideo_shader_enable = "false"\nnetwork_cmd_enable = "true"\nnetwork_cmd_port = "55356"\nlog_verbosity = "false"\nfrontend_log_level = "2"\nlibretro_log_level = "2"\n')
  args=list(job['args']);mapping={}
  for n,(name,text) in enumerate(job.get('configs',{}).items()):
   copy=folder/('configgen-%02d.cfg'%n);copy.write_text(text);mapping[name]=str(copy)
  for i,a in enumerate(args):
   if a in ('-c','--config','--appendconfig') and i+1<len(args):args[i+1]='|'.join(mapping.get(x,x) for x in args[i+1].split('|'))
   elif a.startswith('--appendconfig='):args[i]='--appendconfig='+'|'.join(mapping.get(x,x) for x in a.split('=',1)[1].split('|'))
  args=append_config(args,cfg)
  for i,a in enumerate(args[:-1]):
   if a in ('-L','--libretro'):args[i+1]=str(core)
  # Replace only output/logging; configgen's controls, saves, overrides and core options remain.
  args=[x for x in args if x!='--verbose']
  for i,a in enumerate(args[:-1]):
   if a=='--log-file':args[i+1]=str(folder/'flycast.log');break
  else:args+=['--log-file',str(folder/'flycast.log')]
  env=os.environ.copy()
  for k in list(env):
   if k.startswith(('SDL_','VK_','MESA_','WLR_')) or k in ('LD_PRELOAD','LD_LIBRARY_PATH','DISPLAY','WAYLAND_DISPLAY','EGL_PLATFORM'):env.pop(k,None)
  env.update(job['env']);env.update(LD_LIBRARY_PATH=str(BASE/'rotation'),VK_ICD_FILENAMES='/usr/share/vulkan/icd.d/mali_icd.json',SDL_NO_SIGNAL_HANDLERS='1',HOME='/userdata/system',XDG_CONFIG_HOME='/userdata/system/configs',XDG_RUNTIME_DIR='/var/run',PULSE_SERVER='unix:/var/run/pulse/native',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/dbus/system_bus_socket')
  for name,value in job['governors'].items():
   path=Path(name)
   if not re.fullmatch(r'/sys/devices/system/cpu/cpufreq/policy\d+/scaling_governor',name) or not re.fullmatch(r'[a-z_]+',value):continue
   old=path.read_text().strip()
   if old!=value:saved[name]=(old,value);path.write_text(value)
  cmd=['/run/actionpi-app-originals/retroarch',*args]
  with (folder/'flycast-console.log').open('wb') as log:
   def priority():os.setpriority(os.PRIO_PROCESS,0,int(job['nice']))
   p=subprocess.Popen(cmd,env=env,cwd='/userdata',stdout=log,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=priority)
   from home_exit import register,stamp
   register(p.pid,'/usr/bin/retroarch');atomic(marker,{'pid':p.pid,'start':stamp(p.pid),'program':'retroarch','boot_id':job['boot_id']})
   result['pid']=p.pid;atomic(folder/'flycast-running.json',result)
   while p.poll() is None:
    if (folder/'stop').exists():
     with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:s.sendto(b'QUIT\n',('127.0.0.1',55356))
    time.sleep(.3)
   result['exit_code']=p.returncode
 except BaseException as e:result['error']=repr(e)
 finally:
  marker.unlink(missing_ok=True)
  if p and p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=5)
  for name,(old,wanted) in saved.items():
   path=Path(name)
   if path.read_text().strip()==wanted:path.write_text(old)
  result['boot_id_after']=Path('/proc/sys/kernel/random/boot_id').read_text().strip();atomic(folder/'flycast-result.json',result)
  # Record launch failure and return to the menu, rather than triggering a recovery reboot.
  atomic(folder/'result.json',result)
