"""Patch only the checked ES game-list return payload into both clean v1.0.6 images."""
from pathlib import Path
import copy,hashlib,importlib.util,io,json,os,re,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ.get('ACTIONPI_IMAGE_DIR',ROOT/'images'));PREP=OUT/'public-v1.0.7-prep'
PAYLOAD=Path(os.environ.get('ACTIONPI_ES_RETURN_PAYLOAD',ROOT/'es-return-payload'))
HELPER=Path(os.environ.get('ACTIONPI_FAT_HELPER',ROOT/'tools/fat32_image.py'))
spec=importlib.util.spec_from_file_location('fat106',HELPER);fatmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(fatmod)
sha=lambda d:hashlib.sha256(d).hexdigest()
def linux(p):
 s=p.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:] if len(s)>1 and s[1]==':' else s
def wsl(*a):subprocess.run((['wsl','-d','Ubuntu','--',*a] if os.name=='nt' else list(a)),check=True)
def ranges(fat,paths):
 result=[(fat.offset,fat.data_offset)];names={'/'}
 for path in paths:
  parts=path.strip('/').split('/')
  for i in range(1,len(parts)+1):names.add('/'+'/'.join(parts[:i]))
 for n in sorted(names):
  try:c=fat.root if n=='/' else fat.locate(n)[2]
  except FileNotFoundError:continue
  if c:result.extend((fat.cluster_offset(x),fat.cluster_offset(x)+fat.cluster_size) for x in fat.chain(c))
 return result
def build(crc=False):
 edition='crc-ko' if crc else 'standard';suffix='-crc-ko' if crc else '';source=OUT/('action-pi-knulli-v1.0.6'+suffix+'.img');final=OUT/('action-pi-knulli-v1.0.7'+suffix+'.img');partial=final.with_suffix('.img.partial');stage=PREP/edition;stage.mkdir(parents=True,exist_ok=True)
 assert not final.exists() and not partial.exists(),'Refuse overwrite'
 expected=json.loads(source.with_suffix('.manifest.json').read_bytes())['sha256']
 protected={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in OUT.glob('action-pi-knulli-v1.0.6*.img*')}
 checks=json.loads((PAYLOAD.parent/'FILES.json').read_bytes());changed={};additions={}
 for rel,meta in checks.items():
  p=PAYLOAD/rel;data=p.read_bytes();assert sha(data)==meta['sha256'] and len(data)==meta['bytes'],rel
  if rel.endswith('.py'):compile(data,rel,'exec')
  if rel.startswith('boot/'):changed[rel[5:]]=data
  else:assert rel.startswith('userdata/system/flycast-vulkan/');additions[rel[9:]]=data
 with source.open('rb') as f:
  fat=fatmod.Fat32Editor(f,fatmod.BOOT_RESOURCE_OFFSET);original=fat.read_file('/STABLE_V119/settings.tar.gz');payload=json.loads(fat.read_file('/STABLE_V119/payload.json'));assert sha(original)==payload['payloads']['settings.tar.gz']
  old_clusters=[]
  with tarfile.open(fileobj=io.BytesIO(original),mode='r:gz') as t:
   conf=t.extractfile('system/knulli.conf').read().decode()
   assert 'system.language=en_US' in conf.splitlines() and 'wifi.enabled=0' in conf.splitlines() and 'system.telemetry=0' in conf.splitlines()
   assert not any(re.match(r'^wifi(?:\.\d+)?\.(?:ssid|key)=.+',line) for line in conf.splitlines())
   if crc:
    for n,m in payload['personal_arcade_cores']['cores'].items():assert sha(t.extractfile('system/custom-cores/'+n).read())==m['sha256']
    payload['personal_arcade_cores']['variant']='v1.0.7-crc-ko'
  payload['public_version']='v1.0.7';payload['payloads']['settings.tar.gz']=sha(original)
  payload['runtime_updates'].update(es_game_list_return=True,es_game_cursor_restore=False)
  changed['STABLE_V119/payload.json']=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode()
  allowed=ranges(fat,list(changed));stable={p:sha(fat.read_file(p)) for p in ['/partitions/BOOT.IMG','/partitions/ENV.IMG','/STABLE_V119/firstboot.py','/STABLE_V119/settings.tar.gz','/PPSSPP_VULKAN/mali_autostart.py','/boot-custom.sh','/ACTIONPI_ZRAM/service.py']}
 for n,d in changed.items():p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d)
 print('COPY_SOURCE',edition,flush=True);h=hashlib.sha256()
 with source.open('rb') as a,partial.open('xb') as b:
  while d:=a.read(16*1024*1024):h.update(d);b.write(d)
  b.flush();os.fsync(b.fileno())
 assert h.hexdigest()==expected,'Source identity mismatch'
 arg=linux(partial)+'@@'+str(fatmod.BOOT_RESOURCE_OFFSET)
 for n in changed:wsl('mcopy','-o','-i',arg,linux(stage/n),'::/'+n)
 with partial.open('r+b') as f:
  fat=fatmod.Fat32Editor(f,fatmod.BOOT_RESOURCE_OFFSET)
  for c in old_clusters:
   if fat.next_cluster(c)==0:f.seek(fat.cluster_offset(c));f.write(bytes(fat.cluster_size))
  for n,d in changed.items():assert fat.read_file('/'+n)==d,n
  assert stable=={p:sha(fat.read_file(p)) for p in stable};allowed+=ranges(fat,list(changed))
 merged=[]
 for a,b in sorted(allowed):
  if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
  else:merged.append([a,b])
 print('VERIFY_IMAGE_AND_HASH',edition,flush=True);h=hashlib.sha256();cursor=compared=0
 with source.open('rb') as a,partial.open('rb') as b:
  for start,end in merged+[[source.stat().st_size,source.stat().st_size]]:
   while cursor<start:
    n=min(16*1024*1024,start-cursor);d=b.read(n);assert len(d)==n and a.read(n)==d,'Unexpected change '+str(cursor);h.update(d);cursor+=n;compared+=n
   a.seek(end)
   while cursor<end:
    n=min(16*1024*1024,end-cursor);d=b.read(n);assert len(d)==n;h.update(d);cursor+=n
 assert protected=={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in OUT.glob('action-pi-knulli-v1.0.6*.img*')}
 partial.rename(final)
 report={'version':'v1.0.7','edition':edition,'image':final.name,'bytes':final.stat().st_size,'sha256':h.hexdigest(),'source_image':source.name,'source_sha256':expected,'changed_files':{p:sha(d) for p,d in changed.items()},'added_or_updated_userdata':{p:sha(d) for p,d in additions.items()},'defaults':payload['defaults'],'checks':{'unchanged_tar_members_preserved':True,'crc_arcade_cores_preserved':crc,'kernel_mali_wifi_ppsspp_zram_unchanged':True,'private_configuration_copied':False,'unchanged_bytes_compared':compared,'old_images_unchanged':True,'boot_and_userdata_payload_readback':True},'hardware_validation':'PSP OutRun 2006 and standard Flycast Crazy Taxi 2 returned to their system game lists on the same boot, confirmed by captures. Game cursor/subfolder restoration is not implemented. Fresh SD flashing and individual VL/Xtreme launches not repeated.'}
 final.with_suffix('.manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');final.with_suffix('.sha256').write_text(report['sha256']+'  '+final.name+'\n');(stage/'IMAGE_BUILD_RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('BUILT',final.name,report['sha256'],flush=True)
if __name__=='__main__':build(False);build(True)
