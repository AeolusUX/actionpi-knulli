"""Guarded offline binary repair; writes a NEW image only after ARM64 tests."""
import hashlib,json,struct,sys,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/mali-rebuild-prep/display-binary-repair'
sys.path.insert(0,str(root/'work/firmware-audit-deps'))
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X19,UC_ARM64_REG_X20,UC_ARM64_REG_X21,UC_ARM64_REG_X29,UC_ARM64_REG_X30,UC_ARM64_REG_SP,UC_ARM64_REG_PC
source=root/'outputs/action-pi-knulli-sd-stable-wifi-v115.img'
dest=root/'outputs/action-pi-knulli-sd-display-cleanup-test-v116.img'
assert not dest.exists(),'Refuse existing destination'
boot=5423235072
with source.open('rb') as f:
 f.seek(boot);header=f.read(2048);ks=struct.unpack_from('<I',header,8)[0];rs=struct.unpack_from('<I',header,16)[0];page=struct.unpack_from('<I',header,36)[0]
 assert header[:8]==b'ANDROID!' and page==2048 and ks==23095304 and struct.unpack_from('<I',header,24)[0]==0
 f.seek(boot+page);original=f.read(ks)
 rpos=boot+page+((ks+page-1)//page)*page;f.seek(rpos);ramdisk=f.read(rs)
assert hashlib.sha256(original).hexdigest()=='32068a6db3f71748880acd356241884f0243eaad90a7f1fb4e96e52fa12f786b'
assert (out/'relocations.txt').read_text().strip()=='There are no relocations in this file.'
patched=bytearray(original);changes=[]
def patch(at,data,expected=None):
 if expected is not None:assert original[at:at+len(expected)]==expected
 assert not any(at<a+len(b) and a<at+len(data) for a,b in changes)
 changes.append((at,data));patched[at:at+len(data)]=data
def branch(pc,target,link=False):
 assert (target-pc)%4==0 and -(1<<27)<=target-pc<(1<<27)
 return struct.pack('<I',(0x94000000 if link else 0x14000000)|(((target-pc)//4)&0x3ffffff))
for name,at,maximum in [('logo',0x7777d0,0xd4),('exit',0x7778a4,0x4c),('cleanup',0x7778f0,0x60)]:
 blob=(out/(name+'.bin')).read_bytes();assert len(blob)<=maximum
 patch(at,blob)
# Repurpose only the old debug-print callback. Its sole source-level work
# initializer is redirected to the existing return-zero no-op helper.
assert struct.unpack_from('<I',original,0x777fa8)[0]==0x90000000
patch(0x777fac,struct.pack('<I',0x913b5000),struct.pack('<I',0x9123c000)) # add x0,x0,#0xed4
assert original[0x777ed4:0x777ee4]==bytes.fromhex('000080523f2303d5bf2303d5c0035fd6')
patch(0x777ff4,branch(0x777ff4,0x7778f0),struct.pack('<I',0x52800000))
patch(0x7776bc,struct.pack('<I',0xf941a661)+branch(0x7776c0,0x777ff4,True),bytes.fromhex('e06246b960040035'))

# Reject external branches into replaced function interiors. All executable
# replacement bytes stay inside previously present, post-boot code functions.
ranges=[(0x7777d0,0x7778a4),(0x7778a4,0x7778f0),(0x7778f0,0x777950)]
refs=[];bad=[];debug_addr_refs=[]
for pc in range(0,len(original)-3,4):
 w=struct.unpack_from('<I',original,pc)[0]
 target=None
 if w&0x7c000000==0x14000000:
  n=w&0x3ffffff;n=n-(1<<26) if n&(1<<25) else n;target=pc+4*n
 elif w&0xff000010==0x54000000 or w&0x7e000000==0x34000000:
  n=(w>>5)&0x7ffff;n=n-(1<<19) if n&(1<<18) else n;target=pc+4*n
 elif w&0x7e000000==0x36000000:
  n=(w>>5)&0x3fff;n=n-(1<<14) if n&(1<<13) else n;target=pc+4*n
 if target is not None:
  for a,b in ranges:
   if a<=target<b and not a<=pc<b:
    refs.append({'pc':hex(pc),'target':hex(target)})
    if target!=a:bad.append(refs[-1])
 if w&0x9f000000==0x90000000 and pc+8<=len(original):
  nxt=struct.unpack_from('<I',original,pc+4)[0];reg=w&31
  if nxt&0xffc00000==0x91000000 and nxt&31==reg and (nxt>>5)&31==reg:
   n=((w>>29)&3)|(((w>>5)&0x7ffff)<<2);n=n-(1<<21) if n&(1<<20) else n
   address=(pc&~4095)+(n<<12)+((nxt>>10)&0xfff)
   if address==0x7778f0:debug_addr_refs.append(hex(pc))
assert not bad,bad
assert debug_addr_refs==['0x777fa8'],debug_addr_refs

tests=[]
def simulate(kind,getter_rc=0,dimensions=(720,960,720,960),phy=0,bpp=32):
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(0,0x1800000);u.mem_write(0,bytes(patched));u.mem_map(0x3000000,0x10000);u.mem_map(0x4000000,0x10000)
 sp=0x3008000;end=0x1000;par=0x4000000;client=par+0x40;node=client+16;dev=0x4001000;head=dev+0x120;info=0x4003000;events=[]
 def put(at,*words):u.mem_write(at,struct.pack('<'+'Q'*len(words),*words))
 put(client,dev,0);put(node,head,head);put(head,node,node);put(info+840,par);put(0x1650668,info)
 u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_X30,end)
 sent={UC_ARM64_REG_X19:0x1919,UC_ARM64_REG_X20:0x2020,UC_ARM64_REG_X21:0x2121,UC_ARM64_REG_X29:0x2929}
 for r,v in sent.items():u.reg_write(r,v)
 def hook(uc,pc,size,data):
  if pc==end or kind=='failure' and pc==0x7776c4:uc.emu_stop();return
  if pc not in [0x772e50,0x7774d4,0x4264b0,0x4295e0,0xc26c90,0xc26460,0x4e6de4]:return
  x0=uc.reg_read(UC_ARM64_REG_X0);ret=0
  if pc==0x772e50:
   events.append('get_logo');ret=getter_rc
   if not getter_rc:
    w,h,sw,sh=dimensions
    uc.mem_write(uc.reg_read(UC_ARM64_REG_X1),struct.pack('<4I',phy,w,h,bpp))
    # X0..X28 are consecutive in Unicorn except X29/X30.
    from unicorn.arm64_const import UC_ARM64_REG_X2,UC_ARM64_REG_X3
    uc.mem_write(uc.reg_read(UC_ARM64_REG_X2),struct.pack('<I',sw));uc.mem_write(uc.reg_read(UC_ARM64_REG_X3),struct.pack('<I',sh))
  elif pc==0x7774d4:
   events.append('fb_core_init');assert x0==0x1650698
   data=bytes(uc.mem_read(x0,56));assert struct.unpack_from('<Q',data)[0]==dev
   w,h,sw,sh=dimensions;assert struct.unpack_from('<4I',data,12)==(w,h,sw,sh)
   assert struct.unpack_from('<I',data,8)[0]==(int(bpp!=32) if phy else 0)
   assert struct.unpack_from('<Q',data,32)[0]==phy
  elif pc==0xc26c90:events.append('lock');assert x0==dev+0x100
  elif pc==0xc26460:events.append('unlock');assert x0==dev+0x100
  elif pc==0x4e6de4:
   events.append('release_client');assert x0==client
   assert bytes(uc.mem_read(head,16))==struct.pack('<QQ',head,head)
  elif pc==0x4264b0:events.append('unregister_fb');assert x0==info
  elif pc==0x4295e0:
   events.append('free_fb');assert x0==info and 'release_client' in events
  uc.reg_write(UC_ARM64_REG_X0,ret&((1<<64)-1));uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_X30))
 u.hook_add(UC_HOOK_CODE,hook)
 if kind=='logo':u.reg_write(UC_ARM64_REG_X0,dev);u.reg_write(UC_ARM64_REG_X1,0x4005000);start=0x7777d0
 elif kind in ['exit','empty_exit']:
  if kind=='empty_exit':put(0x1650668,0)
  start=0x7778a4
 elif kind=='failure':u.reg_write(UC_ARM64_REG_X19,info);start=0x7776bc
 else:u.reg_write(UC_ARM64_REG_X1,par);start=0x777ff4
 u.emu_start(start,end,count=1000)
 assert u.reg_read(UC_ARM64_REG_SP)==sp
 if kind!='failure':
  for r,v in sent.items():assert u.reg_read(r)==v,(kind,r)
 if kind=='logo':
  expected=['get_logo']+(['fb_core_init'] if getter_rc==0 and all(dimensions) else [])
  assert events==expected,(events,expected)
  rc=u.reg_read(UC_ARM64_REG_X0)&0xffffffff
  assert rc==((getter_rc if getter_rc else (0 if all(dimensions) else -22))&0xffffffff)
 elif kind=='exit':assert events==['unregister_fb','lock','release_client','unlock','free_fb'];assert bytes(u.mem_read(0x1650668,8))==b'\0'*8
 elif kind=='empty_exit':assert events==[]
 else:assert events==['lock','release_client','unlock']
 tests.append({'kind':kind,'getter_rc':getter_rc,'dimensions':dimensions,'events':events,'passed':True})
simulate('logo',-1);simulate('logo',0,(0,0,0,0));simulate('logo');simulate('logo',0,phy=0x40000000,bpp=24)
simulate('cleanup');simulate('failure');simulate('exit');simulate('empty_exit')
manifest={'kernel_before_sha256':hashlib.sha256(original).hexdigest(),'kernel_after_sha256':hashlib.sha256(patched).hexdigest(),'external_branch_refs':refs,'debug_callback_address_refs':debug_addr_refs,'emulation':tests,'patches':[{'offset':hex(a),'size':len(b),'old':original[a:a+len(b)].hex(),'new':b.hex()} for a,b in changes]}
(out/'verification.json').write_text(json.dumps(manifest,indent=2))
print('All code placement, reference and ARM64 behavior checks passed; 8 scenarios.')
if '--build-image' not in sys.argv:sys.exit(0)
assert source.resolve()!=dest.resolve()
sha=hashlib.sha256()
try:
 with source.open('rb') as f,dest.open('xb') as g:
  while data:=f.read(8*1024*1024):sha.update(data);g.write(data)
 assert sha.hexdigest()=='b1398c425ea699eb8939859a27759532eaa78f81d5caef01f9675b17c0233330'
 newhead=bytearray(header);dig=hashlib.sha1()
 for component in (patched,ramdisk,b''):
  dig.update(component);dig.update(struct.pack('<I',len(component)))
 newhead[576:596]=dig.digest()
 with dest.open('r+b') as g:g.seek(boot);g.write(newhead);g.seek(boot+page);g.write(patched)
 allowed=[(boot+576,boot+596)]+[(boot+page+a,boot+page+a+len(b)) for a,b in changes]
 outputsha=hashlib.sha256();diffbytes=0;offset=0
 with source.open('rb') as f,dest.open('rb') as g:
  while a:=f.read(8*1024*1024):
   b=g.read(len(a));assert len(b)==len(a);outputsha.update(b)
   if a!=b:
    for i,(x,y) in enumerate(zip(a,b)):
     if x!=y:assert any(lo<=offset+i<hi for lo,hi in allowed);diffbytes+=1
   offset+=len(a)
  assert not g.read(1)
 manifest.update(image=str(dest),source_sha256=sha.hexdigest(),image_sha256=outputsha.hexdigest(),image_size=offset,differing_bytes=diffbytes,scope='Offline verified test image, not hardware tested. Normal Panfrost startup preserved.')
 (out/'verification.json').write_text(json.dumps(manifest,indent=2));Path(str(dest)+'.sha256').write_text(outputsha.hexdigest()+'  '+dest.name+'\n')
 print(json.dumps({k:manifest[k] for k in ['image','image_sha256','image_size','differing_bytes']}))
except Exception:
 # Keep a failed output for inspection; never present it as a validated image.
 (out/'BUILD_FAILED.txt').write_text('Image generation/verification failed. Do not flash the destination.\n')
 raise
