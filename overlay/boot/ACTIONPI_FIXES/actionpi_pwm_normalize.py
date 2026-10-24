"""Reconcile the PWM hardware polarity with this board's normal runtime DT."""
from pathlib import Path
import json,mmap,os,struct,sys,time

def normalize(reason='boot'):
 assert Path('/boot/boot/knulli.board').read_text().strip()=='helegany-action-pi'
 node=Path('/sys/bus/platform/devices/2000c00.pwm0/of_node')
 assert node.joinpath('compatible').read_bytes().startswith(b'allwinner,sunxi-pwm-v201\0')
 assert struct.unpack('>4I',node.joinpath('reg').read_bytes())==(0,0x02000c00,0,0x400)
 desired=struct.unpack('>4I',Path('/sys/firmware/devicetree/base/backlight0/pwms').read_bytes())
 assert desired==(0x10d,0,50000,0),'Expected native-polarity DTB first'
 fd=os.open('/dev/mem',os.O_RDWR|os.O_SYNC)
 try:
  with mmap.mmap(fd,4096,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ|mmap.PROT_WRITE,offset=0x02000000) as mm:
   before=struct.unpack_from('<I',mm,0xd00)[0]
   after=before|0x100  # sunxi PWM_ACT_STA bit8:1=NORMAL; preserve all other fields.
   if after!=before:struct.pack_into('<I',mm,0xd00,after)
   assert struct.unpack_from('<I',mm,0xd00)[0]==after
 finally:os.close(fd)
 return {'reason':reason,'dt_polarity':0,'register_before':before,'register_after':after,'time':time.strftime('%F %T')}

if __name__=='__main__':print(json.dumps(normalize(sys.argv[1] if len(sys.argv)>1 else 'boot')),flush=True)
