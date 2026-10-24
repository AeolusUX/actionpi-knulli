"""Change only backlight0 PWM polarity in the appended kernel DTB, with backup."""
from pathlib import Path
import hashlib,json,os,struct,sys
KERNEL='52eb2334f61bad08c82cd0d5a27f11f93596b686b06019bc6948c7ef6a03847d'
BACKUP=Path('/boot/ACTIONPI_FIXES/pwm-polarity-backup')

def property_offsets(blob):
 magic,total,structure,strings=struct.unpack_from('>4I',blob)
 assert magic==0xd00dfeed and total<=len(blob)
 stack=[];p=structure;result={}
 while p<total:
  token=struct.unpack_from('>I',blob,p)[0];p+=4
  if token==1:
   end=blob.index(0,p);stack.append(blob[p:end].decode());p=(end+4)&~3
  elif token==2:stack.pop()
  elif token==3:
   size,nameoff=struct.unpack_from('>2I',blob,p);p+=8
   end=blob.index(0,strings+nameoff);name=blob[strings+nameoff:end].decode()
   result[('/'+'/'.join(x for x in stack if x),name)]=(p,size)
   p=(p+size+3)&~3
  elif token==4:pass
  elif token==9:break
  else:raise RuntimeError('Invalid FDT token')
 return result

def patch(blob):
 props=property_offsets(blob);at,size=props[('/backlight0','pwms')]
 assert size==16
 phandle,channel,period,polarity=struct.unpack_from('>4I',blob,at)
 assert phandle==0x10d and channel==0 and period==50000 and polarity in (0,1)
 data=bytearray(blob);struct.pack_into('>I',data,at+12,0)
 assert [i for i,(a,b) in enumerate(zip(blob,data)) if a!=b] in ([],[at+15])
 return bytes(data),at+12,polarity

def apply():
 assert Path('/boot/boot/knulli.board').read_text().strip()=='helegany-action-pi'
 with open('/dev/mmcblk0p3','rb') as f:
  header=f.read(2048);assert header[:8]==b'ANDROID!'
  kernel,ramdisk,second,page=[struct.unpack_from('<I',header,o)[0] for o in [8,16,24,36]]
  assert page==2048 and second==0 and kernel==23095304
  f.seek(page);assert hashlib.sha256(f.read(kernel)).hexdigest()==KERNEL
  offset=page+((kernel+page-1)//page)*page+((ramdisk+page-1)//page)*page
  assert offset==0x1883000
  f.seek(offset);head=f.read(40);length=struct.unpack_from('>I',head,4)[0]
  assert head[:4]==b'\xd0\x0d\xfe\xed' and length==173030
  f.seek(offset);before=f.read(length)
 after,at,old=patch(before)
 if old==0:print('Appended DTB already uses normal PWM polarity.');return
 assert sys.argv[1:] == ['--apply'],'Use --apply to write after inspecting the source'
 BACKUP.mkdir(exist_ok=False)
 (BACKUP/'kernel-before.dtb').write_bytes(before)
 (BACKUP/'kernel-after.dtb').write_bytes(after)
 report={'partition':'/dev/mmcblk0p3','dtb_offset':offset,'property_offset':at,'absolute_offset':offset+at,'before':1,'after':0,'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest(),'kernel_sha256_unchanged':KERNEL}
 (BACKUP/'manifest.json').write_text(json.dumps(report,indent=2));os.sync()
 with open('/dev/mmcblk0p3','r+b',buffering=0) as f:
  f.seek(offset+at);assert f.read(4)==struct.pack('>I',1)
  f.seek(offset+at);assert f.write(struct.pack('>I',0))==4;os.fsync(f.fileno())
  f.seek(offset);assert f.read(length)==after
 print(json.dumps(report),flush=True)

if __name__=='__main__':apply()
