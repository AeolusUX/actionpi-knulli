"""Fix the effective TOC1 external DTB, preserving all bootloader code."""
from pathlib import Path
import hashlib,json,os,struct,sys
from backlight_pwm_fix import patch,property_offsets
OFFSET=0x1004000
LENGTH=1753088
ORIGINAL='64c7e295dc1647150f1f1420d8514950df23c477838c0ddaa8d67352cb232d91'
BACKUP=Path('/boot/ACTIONPI_FIXES/pwm-toc-backup')

def sha(data):return hashlib.sha256(data).hexdigest()
def checksum(package):
 data=bytearray(package);struct.pack_into('<I',data,20,0x5f0a6c39)
 return sum(struct.unpack('<%dI'%(len(data)//4),data))&0xffffffff

def dtb_item(package):
 assert package[:16].rstrip(b'\0')==b'sunxi-package'
 assert struct.unpack_from('<I',package,16)[0]==0x89119800
 assert struct.unpack_from('<2I',package,32)==(4,LENGTH) and len(package)==LENGTH
 assert struct.unpack_from('<I',package,20)[0]==checksum(package),'TOC checksum mismatch'
 items={}
 for i in range(4):
  entry=64+i*368;name=package[entry:entry+64].split(b'\0')[0].decode('ascii')
  at,n,encrypted,kind=struct.unpack_from('<4I',package,entry+64)
  assert at>=2048 and at+n<=len(package) and encrypted==0
  items[name]=(at,n)
 assert tuple(items)==('u-boot','monitor','scp','dtb')
 return items['dtb']

def patched_package(before):
 at,n=dtb_item(before);size=struct.unpack_from('>I',before,at+4)[0];assert size<=n
 fixed,prop,old=patch(before[at:at+size]);assert old==1
 result=bytearray(before);result[at:at+size]=fixed
 struct.pack_into('<I',result,20,checksum(result))
 changed=[i for i,(a,b) in enumerate(zip(before,result)) if a!=b]
 assert set(changed)<=set(range(20,24))|set(range(at+prop,at+prop+4))
 assert dtb_item(result)==(at,n)
 return bytes(result),{'dtb_offset':at,'dtb_size':size,'property_offset':prop,'changed_byte_offsets':changed,'before_sha256':sha(before),'after_sha256':sha(result),'dtb_after_sha256':sha(fixed)}

def write_raw(data):
 with open('/dev/mmcblk0','r+b',buffering=0) as f:
  f.seek(OFFSET);assert f.write(data)==len(data);os.fsync(f.fileno())
  f.seek(OFFSET);assert f.read(len(data))==data

def main():
 assert Path('/boot/boot/knulli.board').read_text().strip()=='helegany-action-pi'
 fat=Path('/boot/partitions/boot_package.fex')
 with open('/dev/mmcblk0','rb') as f:f.seek(OFFSET);before=f.read(LENGTH)
 if sys.argv[1:] == ['--restore']:
  report=json.loads((BACKUP/'manifest.json').read_text());assert sha(before)==report['after_sha256']
  original=(BACKUP/'raw-before.fex').read_bytes();assert sha(original)==report['before_sha256'];dtb_item(original)
  write_raw(original);fat.write_bytes((BACKUP/'fat-before.fex').read_bytes());os.sync();print('Original raw TOC and FAT copy restored.');return
 assert sys.argv[1:] == ['--apply'] and sha(before)==ORIGINAL
 after,report=patched_package(before)
 BACKUP.mkdir(exist_ok=False)
 (BACKUP/'raw-before.fex').write_bytes(before);(BACKUP/'raw-after.fex').write_bytes(after)
 (BACKUP/'fat-before.fex').write_bytes(fat.read_bytes())
 report.update(raw_offset=OFFSET,scope='only effective external DTB PWM flag and TOC checksum; bootloader code unchanged')
 (BACKUP/'manifest.json').write_text(json.dumps(report,indent=2));os.sync()
 write_raw(after)
 temp=fat.with_suffix('.native');temp.write_bytes(after);temp.replace(fat);os.sync()
 print(json.dumps(report),flush=True)

if __name__=='__main__':main()
