"""Create a separate public v119 installer, keeping the stable image read-only."""
from pathlib import Path, PurePosixPath
import copy, hashlib, io, json, os, re, struct, subprocess, tarfile

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs'
SOURCE=OUT/'action-pi-knulli-sd-stable-v119.img'
FINAL=OUT/'action-pi-knulli-sd-distribution-v119.img'
PARTIAL=FINAL.with_suffix('.img.partial');PREP=OUT/'distribution-v119-prep'
TREE=PREP/'changes';OFFSET=37748736
EXPECTED='fd4734ef2769dbcd6520f14aab2aa0c8086db5e90aa557283a8c2ddbddcd0812'
SECRETS=set()

def digest(data):return hashlib.sha256(data).hexdigest()
def filehash(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()

def config(data):
 text=data.decode('utf-8-sig');lines=[]
 for line in text.splitlines():
  if '=' not in line or line.lstrip().startswith(('#',';')):
   lines.append(line);continue
  key,value=line.split('=',1);k=key.strip();v=value.strip()
  if re.match(r'^wifi.*\.(ssid|key)$',k):
   if '.adhoc.' not in k and v and len(v)>=6:
    SECRETS.add(v.encode());SECRETS.add(v.encode().hex().encode())
   continue
  if k.startswith('wifi.') or k in ('system.language','system.hostname','global.netplay.nickname'):
   continue
  if any(s in k.lower() for s in ('retroachievements','netplay.password','netplay.spectatepassword')):
   continue
  lines.append(line)
 lines+=['system.language=en_US','system.hostname=KNULLI','global.netplay.nickname=KNULLI',
         'wifi.enabled=0','wifi.ssid=','wifi.key=','wifi.adhoc.ssid=','wifi.adhoc.key=']
 return ('\n'.join(lines)+'\n').encode()

def clean_settings(blob):
 target=io.BytesIO();removed=[]
 drop=('system/.bash_history','system/.config/pulse','system/bluetooth',
       'system/cache','system/machine-id','system/knulli-machine-id',
       'system/configs/emulationstation/es_log','system/configs/emulationstation/imagecache.db',
       'system/configs/emulationstation/tmp','system/configs/emulationstation/recovery',
       'system/configs/ppsspp/PSP/SYSTEM/DUMP','system/configs/retroarch/playlists',
       'system/upgrade/update_response.json')
 ports={'roms/ports/Restore original menu.sh','roms/ports/PPSSPP Vulkan.sh'}
 with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as src,tarfile.open(fileobj=target,mode='w:gz',compresslevel=1) as dst:
  for info in src:
   path=PurePosixPath(info.name);assert not path.is_absolute() and '..' not in path.parts
   if info.name in ports or any(info.name==p or info.name.startswith(p+'/') or (p.endswith('es_log') and info.name.startswith(p)) for p in drop) or 'retroachievements.dat' in info.name:
    removed.append(info.name);continue
   member=copy.copy(info);member.uname=member.gname='root';member.uid=member.gid=0
   data=src.extractfile(info).read() if info.isfile() else None
   if info.name=='system/knulli.conf':data=config(data)
   elif info.name.endswith('ppsspp.ini'):
    text=data.decode('utf-8-sig');section='';result=[]
    for line in text.splitlines():
     if line.startswith('['):section=line.strip().lower();result.append(line);continue
     if section in ('[recent]','[playtime]','[achievements]'):continue
     if re.match(r'^Language\s*=',line):line='Language = en_US'
     if re.match(r'^MacAddress\s*=',line):continue
     if re.match(r'^NickName\s*=',line):line='NickName = PSP'
     if re.match(r'^(CurrentDirectory|MemStickDirectory|PinnedPaths)\s*=',line):continue
     result.append(line)
    data=('\n'.join(result)+'\n').encode()
   elif info.name.endswith('retroarchcustom.cfg'):
    text=data.decode('utf-8-sig')
    text=re.sub(r'^user_language\s*=.*$','user_language = "0"',text,flags=re.M)
    text=re.sub(r'^((?:cheevos_(?:username|password|token)|netplay_(?:password|spectate_password|nickname))\s*=).*$','\\1 ""',text,flags=re.M)
    data=text.encode()
   if data is not None:member.size=len(data)
   dst.addfile(member,io.BytesIO(data) if data is not None else None)
 return target.getvalue(),removed

def scrub_fat(path):
 """Zero free clusters, file tail slack and deleted directory records."""
 with path.open('r+b') as f:
  f.seek(OFFSET);bs=f.read(512);bps=struct.unpack_from('<H',bs,11)[0];spc=bs[13]
  reserved=struct.unpack_from('<H',bs,14)[0];nfats=bs[16]
  total=struct.unpack_from('<I',bs,32)[0];spf=struct.unpack_from('<I',bs,36)[0]
  root=struct.unpack_from('<I',bs,44)[0];assert bps==512 and nfats==2 and spf>0
  cluster=bps*spc;start=OFFSET+(reserved+nfats*spf)*bps
  count=(total-reserved-nfats*spf)//spc
  f.seek(OFFSET+reserved*bps);fat=f.read(spf*bps)
  def entry(c):return struct.unpack_from('<I',fat,c*4)[0]&0xfffffff
  def location(c):return start+(c-2)*cluster
  def chain(c):
   result=[];seen=set()
   while c<0xffffff8:
    assert 2<=c<count+2 and c not in seen;seen.add(c);result.append(c);c=entry(c)
   return result
  seen_dirs=set();files=0;deleted=0
  def directory(c):
   nonlocal files,deleted
   assert c not in seen_dirs;seen_dirs.add(c)
   clusters=chain(c);parts=[]
   for cl in clusters:f.seek(location(cl));parts.append(f.read(cluster))
   data=bytearray(b''.join(parts));children=[]
   for at in range(0,len(data),32):
    e=data[at:at+32]
    if e[0]==0:data[at:]=bytes(len(data)-at);break
    if e[0]==0xe5:data[at:at+32]=b'\xe5'+bytes(31);deleted+=1;continue
    if e[11]==15 or e[11]&8:continue
    child=(struct.unpack_from('<H',e,20)[0]<<16)|struct.unpack_from('<H',e,26)[0]
    if e[11]&16:
     if e[:11] not in (b'.          ',b'..         '):children.append(child)
    elif child:
     size=struct.unpack_from('<I',e,28)[0];cs=chain(child);files+=1
     assert len(cs)*cluster>=size
     # Erase unused bytes in the allocated tail, including overallocated clusters.
     for index,cl in enumerate(cs):
      used=max(0,min(cluster,size-index*cluster))
      if used<cluster:f.seek(location(cl)+used);f.write(bytes(cluster-used))
   for index,cl in enumerate(clusters):f.seek(location(cl));f.write(data[index*cluster:(index+1)*cluster])
   for child in children:directory(child)
  directory(root)
  cleared=0;run=None
  def clear(a,b):
   nonlocal cleared
   size=(b-a)*cluster;f.seek(location(a));zero=bytes(8*1024*1024)
   while size:n=min(size,len(zero));f.write(zero[:n]);size-=n;cleared+=n
  for c in range(2,count+2):
   if entry(c)==0:
    if run is None:run=c
   elif run is not None:clear(run,c);run=None
  if run is not None:clear(run,count+2)
  f.flush();os.fsync(f.fileno())
  return {'zeroed_free_bytes':cleared,'files_tail_scrubbed':files,'deleted_records_scrubbed':deleted}

def main():
 assert not FINAL.exists(),'Refuse overwrite of completed image'
 if PARTIAL.exists():assert PARTIAL.stat().st_size<SOURCE.stat().st_size,'Only an interrupted source copy can be resumed'
 TREE.mkdir(parents=True,exist_ok=True)
 srcdisk=str(SOURCE)+'@@'+str(OFFSET)
 def read(d,n):return subprocess.check_output(['mtype','-i',d,'::/'+n])
 settings,removed=clean_settings(read(srcdisk,'STABLE_V119/settings.tar.gz'))
 changed={}
 def put(n,b):
  p=TREE/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);changed[n]=digest(b)
 put('STABLE_V119/settings.tar.gz',settings)
 first=read(srcdisk,'STABLE_V119/firstboot.py').decode()
 assert first.count("('settings.tar.gz','bios.tar.gz')")==2
 first=first.replace("('settings.tar.gz','bios.tar.gz')","('settings.tar.gz',)")
 first=first.replace("'bios_restored':True","'bios_restored':False,'edition':'distribution'")
 put('STABLE_V119/firstboot.py',first.encode());compile(first,'firstboot.py','exec')
 payload={'version':'v119','edition':'distribution','payloads':{'settings.tar.gz':digest(settings)},
  'defaults':{'language':'en_US','wifi_enabled':False,'saved_wifi_credentials':False},
  'bios':'additional personal BIOS bundle excluded; original base-system BIOS unchanged',
  'ports_removed':['Restore original menu','PPSSPP Vulkan test shortcut']}
 put('STABLE_V119/payload.json',(json.dumps(payload,indent=2)+'\n').encode())
 boot=read(srcdisk,'knulli-boot.conf')
 put('knulli-boot.conf',config(boot))
 # The hardware-confirmed PortMaster follow-up is independent of user settings.
 pm=OUT/'portmaster-fix-20261024'
 for name in ('actionpi_portmaster_fix.py','portmaster-sdl/libSDL2.so'):
  put('ACTIONPI_FIXES/'+name,(pm/name).read_bytes())
 for folder in ('ACTIONPI_FIXES','MALI_MENU_TRIAL'):
  name=folder+'/retroarch_rotation_launcher.py';text=read(srcdisk,name).decode()
  anchor='    command=[str(x) for x in args] if isinstance(args,(list,tuple)) else []\n'
  assert text.count(anchor)==1 and 'from actionpi_portmaster_fix import prepare' not in text
  hook="    if '/userdata/roms/ports/PortMaster.sh' in command:\n        sys.path.insert(0,'/boot/ACTIONPI_FIXES')\n        from actionpi_portmaster_fix import prepare\n        prepare()\n"
  put(name,text.replace(anchor,anchor+hook).encode())
 names=subprocess.check_output(['mdir','-b','-s','-i',srcdisk,'::/'],text=True).splitlines()
 names=[x[3:] for x in names if x.startswith('::/') and not x.endswith('/')]
 # Recovery snapshots must also be anonymous; update the manifest which guards them.
 for n in names:
  if n.endswith('knulli.conf') and n!='knulli-boot.conf':put(n,config(read(srcdisk,n)))
 backup='PPSSPP_VULKAN/autostart-backup/'
 put(backup+'PSP-port.sh',b'#!/bin/sh\nprintf "Launch PSP games from the PSP system menu.\\n"\n')
 bm=json.loads(read(srcdisk,backup+'manifest.json'))
 for n,h in changed.items():
  if n.startswith(backup) and n[len(backup):] in bm['hashes']:bm['hashes'][n[len(backup):]]=h
 put(backup+'manifest.json',(json.dumps(bm,indent=2)+'\n').encode())
 removed_boot=[n for n in names if n=='STABLE_V119/bios.tar.gz' or any(n.startswith(p) for p in (
  'ACTIONPI_FIXES/flycastvl-fault/','ACTIONPI_FIXES/observer-selfcheck/','PPSSPP_VULKAN/rotation-check/'))]
 am=json.loads(read(srcdisk,'ACTIONPI_FIXES/manifest.json'))
 for n,h in changed.items():
  if n.startswith('ACTIONPI_FIXES/'):am[n[len('ACTIONPI_FIXES/'):]]=h
 for n in removed_boot:
  if n.startswith('ACTIONPI_FIXES/'):am.pop(n[len('ACTIONPI_FIXES/'):],None)
 put('ACTIONPI_FIXES/manifest.json',(json.dumps(am,indent=2)+'\n').encode())
 # Refresh any historical hash manifests referring to the sanitized snapshots.
 for n in names:
  if n.endswith('.json') and n not in changed:
   try:meta=json.loads(read(srcdisk,n))
   except (ValueError,UnicodeError):continue
   prefix=n.rsplit('/',1)[0]+'/'
   def refresh(obj):
    if isinstance(obj,dict):
     return {k:(changed[prefix+k] if prefix+k in changed and isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) else refresh(v)) for k,v in obj.items() if prefix+k not in removed_boot}
    if isinstance(obj,list):return [refresh(v) for v in obj]
    return obj
   new=refresh(meta)
   if new!=meta:put(n,(json.dumps(new,indent=2)+'\n').encode())
 # Validate public userdata before writing an image. No private values are printed.
 with tarfile.open(fileobj=io.BytesIO(settings),mode='r:gz') as t:
  members={x.name:x for x in t}
  assert not any(n.startswith('bios/') for n in members)
  assert not any(n in members for n in ('roms/ports/Restore original menu.sh','roms/ports/PPSSPP Vulkan.sh'))
  conf=t.extractfile('system/knulli.conf').read()
  assert b'system.language=en_US\n' in conf and b'wifi.enabled=0\n' in conf
  assert b'Language = en_US' in t.extractfile('system/configs/ppsspp/PSP/SYSTEM/ppsspp.ini').read()
  for m in members.values():
   tarfile.data_filter(m,'/userdata')
   if m.isfile():
    data=t.extractfile(m).read();assert not any(s in data for s in SECRETS),'Credential residue in settings: '+m.name
 for n in changed:
  if n!='STABLE_V119/settings.tar.gz':assert not any(s in (TREE/n).read_bytes() for s in SECRETS),'Credential residue: '+n
 for p in TREE.rglob('*.py'):compile(p.read_bytes(),str(p),'exec')
 print('Public settings prepared: English, Wi-Fi off, no saved network, no additional BIOS; test Ports removed.',flush=True)
 h=hashlib.sha256()
 with SOURCE.open('rb') as src,PARTIAL.open('r+b' if PARTIAL.exists() else 'xb') as dst:
  while data:=src.read(8*1024*1024):
   h.update(data);previous=dst.read(len(data)) if dst.readable() else b''
   assert previous==data[:len(previous)],'Interrupted copy differs from stable source'
   if len(previous)<len(data):dst.write(data[len(previous):])
 assert h.hexdigest()==EXPECTED
 disk=str(PARTIAL)+'@@'+str(OFFSET)
 subprocess.run(['mmd','-i',disk,'::/ACTIONPI_FIXES/portmaster-sdl'],check=True)
 for n in removed_boot:subprocess.run(['mdel','-i',disk,'::/'+n],check=True)
 for n in changed:subprocess.run(['mcopy','-o','-i',disk,str(TREE/n),'::/'+n],check=True)
 print('Separate v119 copy updated; erasing deleted BIOS and private configuration remnants.',flush=True)
 scrub=scrub_fat(PARTIAL)
 for n,h in changed.items():assert digest(read(disk,n))==h,n
 assert subprocess.run(['mtype','-i',disk,'::/STABLE_V119/bios.tar.gz'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0
 # Compare the untouched root filesystem as a stream; baseline BIOS remains identical.
 def image_file_hash(d,n):
  p=subprocess.Popen(['mtype','-i',d,'::/'+n],stdout=subprocess.PIPE);h=hashlib.sha256()
  while b:=p.stdout.read(8*1024*1024):h.update(b)
  assert p.wait()==0;return h.hexdigest()
 root_hash=image_file_hash(disk,'boot/knulli')
 assert root_hash==filehash(PREP/'rootfs.squashfs')
 h=hashlib.sha256();previous=b''
 with PARTIAL.open('rb') as f:
  while data:=f.read(8*1024*1024):
   assert not any(s in previous+data for s in SECRETS),'Credential residue in raw image'
   h.update(data);previous=data[-max([len(s) for s in SECRETS]+[1]):]
 sha=h.hexdigest();PARTIAL.rename(FINAL)
 report={'version':'v119','edition':'distribution','image':FINAL.name,'bytes':FINAL.stat().st_size,
  'sha256':sha,'source_stable_sha256':EXPECTED,'source_preserved':True,
  'defaults':payload['defaults'],'bios':payload['bios'],'base_rootfs_sha256_unchanged':root_hash,
  'removed_ports':payload['ports_removed'],'removed_userdata_items':removed,'removed_boot_files':removed_boot,
  'portmaster':'direction and size confirmed on device; scoped private PySDL2 rotation DLL plus persistent launch preparation included',
  'payloads':payload['payloads'],'privacy_cleanup':scrub,
  'validation':'stable source checksum, settings/archive/config assertions, changed-file readback, recovery snapshot hashes, unchanged rootfs checksum, free/slack space scrub, known credential raw scan, final checksum; no live reflash repeated'}
 FINAL.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 FINAL.with_suffix('.sha256').write_text(sha+'  '+FINAL.name+'\n')
 print(json.dumps({'image':str(FINAL),'bytes':FINAL.stat().st_size,'sha256':sha,'cleanup':scrub}),flush=True)

if __name__=='__main__':main()
