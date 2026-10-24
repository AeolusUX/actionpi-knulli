"""Copy a known IMG and apply only the hardware-confirmed standalone PSP route."""
from pathlib import Path
import argparse,hashlib,json,subprocess,tarfile,io,re

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--source',required=True,type=Path);a.add_argument('--output',required=True,type=Path)
 a.add_argument('--source-sha256',required=True);a.add_argument('--fix-dir',required=True,type=Path)
 a.add_argument('--edition',required=True,choices=('distribution','personal'));args=a.parse_args()
 source=args.source;target=args.output;partial=target.with_suffix('.img.partial')
 assert source.is_file() and source.stat().st_size==6069178368
 assert not target.exists() and not partial.exists(),'Refuse overwrite'
 fixed=json.loads((args.fix_dir/'manifest.json').read_text());changed={}
 srcdisk=str(source)+'@@37748736';disk=str(partial)+'@@37748736'
 def get(d,n):return subprocess.check_output(['mtype','-i',d,'::/'+n])
 for n,v in fixed.items():
  assert sha(get(srcdisk,n))==v['before'],n+' source mismatch'
  data=(args.fix_dir/'files'/n).read_bytes();assert sha(data)==v['after'];compile(data,n,'exec');changed[n]=data
 substitutions={v['before']:v['after'] for v in fixed.values()}
 def refresh(x):
  if isinstance(x,dict):return {k:refresh(v) for k,v in x.items()}
  if isinstance(x,list):return [refresh(v) for v in x]
  return substitutions.get(x,x) if isinstance(x,str) else x
 for n in ('ACTIONPI_FIXES/manifest.json','MALI_MENU_TRIAL/manifest.json','MALI_MENU_TRIAL/retroarch-rotation-manifest.json'):
  changed[n]=(json.dumps(refresh(json.loads(get(srcdisk,n))),indent=2)+'\n').encode()
 folder='STABLE_V119' if args.edition=='distribution' else 'STABLE_V120'
 payload=json.loads(get(srcdisk,folder+'/payload.json'))
 if args.edition=='distribution':
  assert set(payload['payloads'])=={'settings.tar.gz'}
  with tarfile.open(fileobj=io.BytesIO(get(srcdisk,folder+'/settings.tar.gz')),mode='r:gz') as t:
   conf=t.extractfile('system/knulli.conf').read().decode()
   assert re.search(r'^system.language=en_US$',conf,re.M) and re.search(r'^wifi.enabled=0$',conf,re.M)
 else:assert set(payload['payloads'])=={'settings.tar.gz','bios.tar.gz'}
 print(args.edition+': validated original defaults; cloning without changing BIOS/settings payloads.',flush=True)
 h=hashlib.sha256()
 with source.open('rb') as f,partial.open('xb') as out:
  while data:=f.read(8*1024*1024):h.update(data);out.write(data)
 assert h.hexdigest()==args.source_sha256
 # Temporary staged files are next to the output, never inside a mounted device.
 stage=target.parent/(target.stem+'-changes');stage.mkdir()
 for n,data in changed.items():
  p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  subprocess.run(['mcopy','-o','-i',disk,str(p),'::/'+n],check=True)
 for n,data in changed.items():assert get(disk,n)==data,n
 assert json.loads(get(disk,folder+'/payload.json'))==payload
 print(args.edition+': seven changed files read back; generating final checksum.',flush=True)
 h=hashlib.sha256()
 with partial.open('rb') as f:
  while data:=f.read(8*1024*1024):h.update(data)
 checksum=h.hexdigest();partial.rename(target)
 report=json.loads(source.with_suffix('.manifest.json').read_text(encoding='utf-8-sig'))
 report.update(image=target.name,sha256=checksum,bytes=target.stat().st_size,packaging_revision=2,
  previous_image_sha256=args.source_sha256,
  standalone_ppsspp='ES Emulators entry uses the same Vulkan supervisor with no ROM argument; owner confirmed Vulkan, direction/size and exit/menu return',
  payload_preservation='settings and BIOS payloads unchanged from source edition',
  validation='source SHA256 during clone, changed script syntax, exact old-file guards, changed-file readback, unchanged payload metadata, final image SHA256; existing live tests not repeated')
 target.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 target.with_suffix('.sha256').write_text(checksum+'  '+target.name+'\n')
 print(json.dumps({'edition':args.edition,'image':str(target),'bytes':target.stat().st_size,'sha256':checksum}),flush=True)

if __name__=='__main__':main()
