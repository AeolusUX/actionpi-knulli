"""Package only after cold boot + suspend direction and hardware readback pass."""
from pathlib import Path
import hashlib,json,os,struct,subprocess
from pwm_toc_fix import patched_package,ORIGINAL,OFFSET,LENGTH
from backlight_pwm_fix import patch as patch_dtb
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs';PREP=OUT/'stable-v119-prep'
SOURCE=OUT/'action-pi-knulli-sd-stable-v118.img';FINAL=OUT/'action-pi-knulli-sd-stable-v119.img'
PARTIAL=FINAL.with_suffix('.img.partial');TREE=PREP/'changes'
SOURCE_SHA='6f95a6ffc117f696f153b221dedbdd99035655a4408109bfb13c3696814a849d'

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 evidence=json.loads((PREP/'confirmed-state.json').read_text())
 assert evidence['user_coldboot_and_resume_confirmed'] is True
 assert evidence['runtime_pwm_args']==[269,0,50000,0] and evidence['hardware_pcr']&0x100
 assert not FINAL.exists() and not PARTIAL.exists()
 TREE.mkdir();h=hashlib.sha256()
 with SOURCE.open('rb') as f,PARTIAL.open('xb') as g:
  while data:=f.read(8*1024*1024):h.update(data);g.write(data)
 assert h.hexdigest()==SOURCE_SHA
 print('Verified source copied; applying the live-tested boot/resume polarity fix.',flush=True)
 disk=str(PARTIAL)+'@@37748736'
 def get(name):return subprocess.check_output(['mtype','-i',disk,'::/'+name])
 changed={}
 def add(name,data):
  p=TREE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);changed[name]=sha(data)
 with PARTIAL.open('r+b') as f:
  f.seek(OFFSET);before=f.read(LENGTH);assert sha(before)==ORIGINAL
  package,package_report=patched_package(before)
  f.seek(OFFSET);f.write(package)
  at=5423235072+0x1883000;f.seek(at);dtb=f.read(173030)
  fixed,flag,old=patch_dtb(dtb);assert old==1
  f.seek(at+flag);f.write(struct.pack('>I',0));f.flush();os.fsync(f.fileno())
  f.seek(OFFSET);assert f.read(LENGTH)==package
  f.seek(at);assert f.read(173030)==fixed
 add('partitions/boot_package.fex',package)
 for name in ['actionpi_pwm_normalize.py','actionpi_wifi_sleep.sh']:
  add('ACTIONPI_FIXES/'+name,(ROOT/'work'/name).read_bytes())
 s=get('PPSSPP_VULKAN/mali_autostart.py').decode()
 anchor='    m=base();m.guard();token=token_present()\n';assert s.count(anchor)==1 and 'PWM_NORMALIZE' not in s
 extra="    sys.path.insert(0,'/boot/ACTIONPI_FIXES')\n    from actionpi_pwm_normalize import normalize\n    m.log('PWM_NORMALIZE',normalize('boot'))\n"
 add('PPSSPP_VULKAN/mali_autostart.py',s.replace(anchor,anchor+extra).encode())
 manifest=json.loads(get('ACTIONPI_FIXES/manifest.json'))
 for name,digest in changed.items():
  if name.startswith('ACTIONPI_FIXES/'):manifest[name.split('/',1)[1]]=digest
 add('ACTIONPI_FIXES/manifest.json',json.dumps(manifest,indent=2).encode())
 first=get('STABLE_V118/firstboot.py').decode().replace('STABLE_V118','STABLE_V119').replace("'v118'","'v119'").replace('v118 settings','v119 settings')
 add('STABLE_V119/firstboot.py',first.encode())
 payload=json.loads(get('STABLE_V118/payload.json'));payload['version']='v119'
 payload['brightness_model']='native values; effective raw TOC external DT normal; reconcile hardware polarity at boot and resume'
 add('STABLE_V119/payload.json',json.dumps(payload,indent=2).encode())
 add('postshare.sh',b'#!/bin/sh\n[ "$1" = start ] || exit 0\nmount -o remount,rw /boot || exit 1\nexec python3 /boot/STABLE_V119/firstboot.py >>/boot/STABLE_V119/firstboot.log 2>&1\n')
 for p in TREE.rglob('*.py'):compile(p.read_bytes(),str(p),'exec')
 for p in [TREE/'postshare.sh',TREE/'ACTIONPI_FIXES/actionpi_wifi_sleep.sh']:subprocess.run(['sh','-n',str(p)],check=True)
 subprocess.run(['mren','-i',disk,'::/STABLE_V118','::/STABLE_V119'],check=True)
 for name in changed:subprocess.run(['mcopy','-o','-i',disk,str(TREE/name),'::/'+name],check=True)
 for name,digest in changed.items():assert sha(get(name))==digest,name
 print('Changed boot files read back; producing image checksum.',flush=True)
 h=hashlib.sha256()
 with PARTIAL.open('rb') as f:
  while data:=f.read(8*1024*1024):h.update(data)
 digest=h.hexdigest();PARTIAL.rename(FINAL)
 report=json.loads(SOURCE.with_suffix('.manifest.json').read_text())
 report.update(version='v119',image=FINAL.name,sha256=digest,source_v118_sha256=SOURCE_SHA,
  status='live cold boot and suspend/wake brightness confirmed; image files verified, new reflash not repeated',
  brightness='effective raw TOC DT PWM polarity0; hardware PWM bit8 restored to1 at boot and resume; native UI and hold repeat',
  supersedes='v117/v118 withdrawn for incomplete brightness polarity handling',
  first_boot='original resize reboot + STABLE_V119 settings/BIOS restoration reboot + tested Mali menu',
  effective_package_patch=package_report,hardware_evidence=evidence,
  validation='source checksum during clone, bounded raw DTB/TOC edits and checksum, changed file readback, source syntax, final image checksum; no GPU/game tests')
 FINAL.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2))
 FINAL.with_suffix('.sha256').write_text(digest+'  '+FINAL.name+'\n')
 print(json.dumps({'image':str(FINAL),'bytes':FINAL.stat().st_size,'sha256':digest}),flush=True)

if __name__=='__main__':main()
