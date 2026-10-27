"""Add guarded ZRAM service and supplied BennuGD to the two clean v1.0.4 images."""
from pathlib import Path
import copy,hashlib,importlib.util,io,json,os,re,subprocess,tarfile,shutil

ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ.get('ACTIONPI_IMAGE_DIR',ROOT/'images'))
PREP=OUT/'public-v1.0.5-prep';ZRAM=Path(os.environ.get('ACTIONPI_ZRAM_BUNDLE',ROOT/'zram-bundle'))
SERVICE=Path(os.environ.get('ACTIONPI_ZRAM_SERVICE',ROOT/'overlay/boot/ACTIONPI_ZRAM'))
BENNU=Path(os.environ['ACTIONPI_BENNU_CORE'])
LOADER=Path(os.environ.get('ACTIONPI_CORE_LOADER',ROOT/'config/crc-ko/load.py'))
FAT_HELPER=Path(os.environ.get('ACTIONPI_FAT_HELPER',ROOT/'tools/fat32_image.py'))
spec=importlib.util.spec_from_file_location('fat105',FAT_HELPER);fatmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(fatmod)
sha=lambda d:hashlib.sha256(d).hexdigest()
def linux(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:] if len(s)>1 and s[1]==':' else s
def wsl(*args):subprocess.run((['wsl','-d','Ubuntu','--',*args] if os.name=='nt' else list(args)),check=True)
def protected():
 return {p.name:[p.stat().st_size,p.stat().st_mtime_ns] for p in OUT.glob('action-pi-knulli-v1.0.4*.img*')}
def ranges(fat,paths):
 result=[(fat.offset,fat.data_offset)]
 names={'/'}
 for path in paths:
  parts=path.strip('/').split('/')
  for i in range(1,len(parts)+1):names.add('/'+'/'.join(parts[:i]))
 for name in sorted(names):
  try:cluster=fat.root if name=='/' else fat.locate(name)[2]
  except FileNotFoundError:continue
  if cluster:result.extend((fat.cluster_offset(c),fat.cluster_offset(c)+fat.cluster_size) for c in fat.chain(cluster))
 return result
def build(crc=False):
 edition='crc-ko' if crc else 'standard';suffix='-crc-ko' if crc else ''
 source=OUT/('action-pi-knulli-v1.0.4'+suffix+'.img');final=OUT/('action-pi-knulli-v1.0.5'+suffix+'.img')
 partial=final.with_suffix('.img.partial');stage=PREP/edition;stage.mkdir(parents=True,exist_ok=True)
 assert not final.exists() and not partial.exists(),'Refuse overwrite'
 expected='2d9733617773319a85a3492ee0db2b6832802fea03c0ba21ee37a1c69f0da605' if crc else '3b7595a3d131cee45473e8c448279cc530acfe2412ab148a13653d50d256c916'
 before=protected();changed={};additions={};records={}
 manifest=json.loads((ZRAM/'MODULES.json').read_bytes())
 for n,m in manifest.items():
  d=(ZRAM/n).read_bytes();assert sha(d)==m['sha256'];changed['ACTIONPI_ZRAM/modules/'+n]=d
 changed['ACTIONPI_ZRAM/MODULES.json']=(ZRAM/'MODULES.json').read_bytes()
 for n in ['service.py','bind.sh','zramswap']:
  d=(SERVICE/n).read_bytes()
  if n.endswith('.py'):compile(d,n,'exec')
  changed['ACTIONPI_ZRAM/'+n]=d
 recovery='''ZRAM is off by default. Toggle zramswap in the normal Services menu. Reboot preserves the setting.
Recovery: create an empty file named DISABLED in ACTIONPI_ZRAM on BOOT to skip startup.
SSH recovery: python3 /boot/ACTIONPI_ZRAM/service.py recover
Keep the replacement service binding: removing only its boot hook exposes the incompatible original service.
ZRAM defaults: lzo-rle, logical swap=RAM/2, compressed RAM cap=min(RAM/4,512MiB), allocated on demand. Not an FPS guarantee.

ZRAM 기본값은 꺼짐입니다. 서비스 메뉴에서 zramswap을 켜고 끌 수 있습니다.
복구: BOOT의 ACTIONPI_ZRAM 폴더에 이름이 DISABLED인 빈 파일을 만들면 시작을 건너뜁니다.
호환 서비스 연결 훅만 삭제하지 마세요. 원래 호환되지 않는 서비스가 다시 노출됩니다.
'''
 changed['ACTIONPI_ZRAM/RECOVERY.txt']=recovery.encode()
 for n in ['COPYING','GPL-2.0.txt','Linux-syscall-note.txt']:
  changed['ACTIONPI_ZRAM/licenses/'+n]=(ROOT/'LICENSES/zram'/n).read_bytes()
 core=BENNU.read_bytes();assert sha(core)=='152aeaade426a9c8ccf11d0b34ee3a64278768f1f1fa91a635d7c20efa5cc34b'
 loader=LOADER.read_text(encoding='utf-8')
 if not crc:
  old="pairs=[('fbneo_libretro.so','fbneo_libretro.so'),('mame2003_plus_libretro.so','mame2003_plus_libretro.so'),('bennugd_libretro.so','bennugd_libretro.so')]"
  assert old in loader;loader=loader.replace(old,"pairs=[('bennugd_libretro.so','bennugd_libretro.so')]")
  loader=loader.replace("if (CORE/'mame078plus_libretro.so').is_file():pairs.append(('mame2003_plus_libretro.so','mame078plus_libretro.so'))","# Standard edition does not replace the arcade cores.")
 loader=loader.encode();compile(loader,'load.py','exec')
 additions['system/custom-cores/bennugd_libretro.so']=core
 additions['system/custom-cores/load.py']=loader
 with source.open('rb') as f:
  fat=fatmod.Fat32Editor(f,fatmod.BOOT_RESOURCE_OFFSET)
  original=fat.read_file('/STABLE_V119/settings.tar.gz')
  payload=json.loads(fat.read_file('/STABLE_V119/payload.json'));assert sha(original)==payload['payloads']['settings.tar.gz']
  old_clusters=list(fat.chain(fat.locate('/STABLE_V119/settings.tar.gz')[2]))
  with tarfile.open(fileobj=io.BytesIO(original),mode='r:gz') as src:
   members=src.getmembers();old={e.name:src.extractfile(e).read() for e in members if e.isfile()}
   conf=old['system/knulli.conf'].decode()
   assert 'system.language=en_US' in conf.splitlines() and 'wifi.enabled=0' in conf.splitlines()
   assert not any(re.match(r'^wifi(?:\.\d+)?\.(?:ssid|key)=.+',s) for s in conf.splitlines())
   assert not any('zramswap' in s.split('=',1)[1].split() for s in conf.splitlines() if s.startswith('system.services='))
   cm=json.loads(old.get('system/custom-cores/manifest.json',b'{}'))
   for n,d in [('bennugd_libretro.so',core),('load.py',loader)]:cm[n]={'bytes':len(d),'sha256':sha(d)}
   additions['system/custom-cores/manifest.json']=(json.dumps(cm,indent=2)+'\n').encode()
   hook=old['system/custom.sh'].decode()
   if crc:assert 'custom-cores/load.py' in hook
   else:
    assert 'custom-cores/load.py' not in hook
    hook+='\n# ACTIONPI_BENNUGD_CORE\nif [ "$1" = start ]; then\n    python3 /userdata/system/custom-cores/load.py || true\nfi\n'
    additions['system/custom.sh']=hook.encode()
   target=io.BytesIO()
   with tarfile.open(fileobj=target,mode='w:gz',compresslevel=9,format=tarfile.PAX_FORMAT) as dst:
    done=set()
    for e in members:
     if e.name in additions:
      d=additions[e.name];n=copy.copy(e);n.size=len(d);dst.addfile(n,io.BytesIO(d));done.add(e.name)
     else:
      d=old.get(e.name);dst.addfile(copy.copy(e),io.BytesIO(d) if d is not None else None)
      records[e.name]=(e.mode,e.type,e.linkname,sha(d) if d is not None else None)
    for n,d in additions.items():
     if n in done:continue
     e=tarfile.TarInfo(n);e.size=len(d);e.mode=0o755 if n.endswith(('.py','.so','.sh')) else 0o644;e.uname=e.gname='root';dst.addfile(e,io.BytesIO(d))
   settings=target.getvalue()
  with tarfile.open(fileobj=io.BytesIO(settings),mode='r:gz') as tar:
   actual={e.name:e for e in tar}
   for n,expected_record in records.items():
    e=actual[n];d=tar.extractfile(e).read() if e.isfile() else None
    assert expected_record==(e.mode,e.type,e.linkname,sha(d) if d is not None else None),n
   for n,d in additions.items():assert tar.extractfile(n).read()==d,n
   for n in actual:
    assert not any(x in n for x in ['zram-trial','zram-service/backup','bennugd-install-result','custom-cores/backups'])
   if crc:
    for n,m in payload['personal_arcade_cores']['cores'].items():assert sha(tar.extractfile('system/custom-cores/'+n).read())==m['sha256']
    payload['personal_arcade_cores']['variant']='v1.0.5-crc-ko'
  payload['public_version']='v1.0.5';payload['payloads']['settings.tar.gz']=sha(settings)
  payload['runtime_updates'].update(zram_compatible_service=True,zram_default_enabled=False,bennugd_supplied_core=True,bennugd_reboot_loader=True)
  changed['STABLE_V119/settings.tar.gz']=settings
  changed['STABLE_V119/payload.json']=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode()
  hook=fat.read_file('/boot-custom.sh').decode();assert 'ACTIONPI_ZRAM_BOOT' not in hook and hook.startswith('#!/bin/sh\n')
  zhook='# ACTIONPI_ZRAM_BOOT\nif [ "$1" = start ]; then\n    sh /boot/ACTIONPI_ZRAM/bind.sh >>/boot/ACTIONPI_ZRAM/bind.log 2>&1 || true\nfi\n'
  changed['boot-custom.sh']=('#!/bin/sh\n'+zhook+hook[len('#!/bin/sh\n'):]).encode()
  allowed=ranges(fat,list(changed))
  stable={p:sha(fat.read_file(p)) for p in ['/partitions/BOOT.IMG','/partitions/ENV.IMG','/STABLE_V119/firstboot.py','/MALI_MENU_TRIAL/mali_session.py','/PPSSPP_VULKAN/mali_autostart.py','/MALI_MENU_TRIAL/v116_ppsspp_session.py','/ACTIONPI_FIXES/v116_ppsspp_session.py']}
 for n,d in changed.items():p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d)
 print('COPY_SOURCE',edition,flush=True);h=hashlib.sha256()
 with source.open('rb') as src,partial.open('xb') as dst:
  while d:=src.read(16*1024*1024):h.update(d);dst.write(d)
  dst.flush();os.fsync(dst.fileno())
 assert h.hexdigest()==expected,'Source identity mismatch'
 imagearg=linux(partial)+'@@'+str(fatmod.BOOT_RESOURCE_OFFSET)
 wsl('mcopy','-s','-o','-i',imagearg,linux(stage/'ACTIONPI_ZRAM'),'::/')
 for n in ['boot-custom.sh','STABLE_V119/settings.tar.gz','STABLE_V119/payload.json']:
  wsl('mcopy','-o','-i',imagearg,linux(stage/n),'::/'+n)
 with partial.open('r+b') as stream:
  fat=fatmod.Fat32Editor(stream,fatmod.BOOT_RESOURCE_OFFSET)
  for c in old_clusters:
   if fat.next_cluster(c)==0:stream.seek(fat.cluster_offset(c));stream.write(bytes(fat.cluster_size))
  for n,d in changed.items():assert fat.read_file('/'+n)==d,n
  assert stable=={p:sha(fat.read_file(p)) for p in stable}
  allowed+=ranges(fat,list(changed))
 merged=[]
 for a,b in sorted(allowed):
  if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
  else:merged.append([a,b])
 print('VERIFY_IMAGE_AND_HASH',edition,flush=True);h=hashlib.sha256();cursor=compared=0
 with source.open('rb') as a,partial.open('rb') as b:
  for start,end in merged+[[source.stat().st_size,source.stat().st_size]]:
   while cursor<start:
    n=min(16*1024*1024,start-cursor);d=b.read(n);assert len(d)==n and a.read(n)==d,'Unexpected change '+str(cursor)
    h.update(d);cursor+=n;compared+=n
   a.seek(end)
   while cursor<end:
    n=min(16*1024*1024,end-cursor);d=b.read(n);assert len(d)==n;h.update(d);cursor+=n
 assert protected()==before,'Previous images changed'
 partial.rename(final)
 report={'version':'v1.0.5','edition':edition,'image':final.name,'bytes':final.stat().st_size,'sha256':h.hexdigest(),'source_image':source.name,'source_sha256':expected,'changed_files':{p:sha(d) for p,d in changed.items()},'added_or_updated_userdata':{p:sha(d) for p,d in additions.items()},'defaults':payload['defaults'],'zram':{'default_enabled':False,'algorithm':'lzo-rle','disksize':'MemTotal/2','mem_limit':'min(MemTotal/4,512MiB)','modules':manifest},'bennugd':{'bytes':len(core),'sha256':sha(core),'provenance':'User-supplied binary; exact corresponding source/build not supplied'},'checks':{'unchanged_tar_members_preserved':True,'crc_arcade_cores_preserved':crc,'kernel_mali_wifi_ppsspp_unchanged':True,'private_configuration_copied':False,'unchanged_bytes_compared':compared,'old_images_unchanged':True,'zram_default_off':True,'boot_and_userdata_payload_readback':True},'hardware_validation':'ZRAM compression/swap, service lifecycle and reboot integration verified on maintainer device. BennuGD mount verified; gameplay and new-image SD installation not retested.'}
 final.with_suffix('.manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 final.with_suffix('.sha256').write_text(report['sha256']+'  '+final.name+'\n')
 (stage/'IMAGE_BUILD_RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('BUILT',final.name,report['sha256'],flush=True)
if __name__=='__main__':
 import sys
 build('--crc' in sys.argv) if len(sys.argv)>1 else (build(False),build(True))
