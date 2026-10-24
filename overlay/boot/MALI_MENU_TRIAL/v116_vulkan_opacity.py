"""Apply opacity through this PPSSPP process's existing DRM master only."""
import ctypes as c,os,re
from pathlib import Path

class Props(c.Structure):
 _fields_=[('n',c.c_uint32),('ids',c.POINTER(c.c_uint32)),('values',c.POINTER(c.c_uint64))]
class Enum(c.Structure):
 _fields_=[('value',c.c_uint64),('name',c.c_char*32)]
class Prop(c.Structure):
 _fields_=[('id',c.c_uint32),('flags',c.c_uint32),('name',c.c_char*32),('nv',c.c_int),('values',c.POINTER(c.c_uint64)),('ne',c.c_int),('enums',c.POINTER(Enum)),('nb',c.c_int),('blobs',c.POINTER(c.c_uint32))]

class Opacity:
 def __init__(self,pid):
  self.pid=pid;self.fd=-1;self.plane=None;self.prop=None;self.original=None
  self.lib=c.CDLL('libdrm.so.2',use_errno=True);self.libc=c.CDLL(None,use_errno=True);self.libc.syscall.restype=c.c_long
  self.lib.drmIsMaster.argtypes=[c.c_int];self.lib.drmIsMaster.restype=c.c_int
  self.lib.drmModeObjectGetProperties.argtypes=[c.c_int,c.c_uint32,c.c_uint32];self.lib.drmModeObjectGetProperties.restype=c.POINTER(Props)
  self.lib.drmModeGetProperty.argtypes=[c.c_int,c.c_uint32];self.lib.drmModeGetProperty.restype=c.POINTER(Prop)
  self.lib.drmModeFreeProperty.argtypes=[c.POINTER(Prop)];self.lib.drmModeFreeObjectProperties.argtypes=[c.POINTER(Props)]
  self.lib.drmModeObjectSetProperty.argtypes=[c.c_int,c.c_uint32,c.c_uint32,c.c_uint32,c.c_uint64];self.lib.drmModeObjectSetProperty.restype=c.c_int
 def apply(self):
  state=Path('/sys/kernel/debug/dri/0/state').read_text()
  match=re.search(r'plane\[(\d+)\]:[^\n]*\n\s*crtc=DE-0\n\s*fb=([1-9]\d*)',state)
  if not match:return None
  plane=int(match[1])
  if self.fd<0:
   pfd=os.pidfd_open(self.pid,0)
   try:
    for f in Path('/proc/%d/fd'%self.pid).iterdir():
     try:target=os.readlink(f)
     except OSError:continue
     if target!='/dev/dri/card0':continue
     dup=self.libc.syscall(438,pfd,int(f.name),0)
     if dup<0:continue
     if self.lib.drmIsMaster(dup)==1:self.fd=dup;break
     os.close(dup)
   finally:os.close(pfd)
  if self.fd<0:return None
  props=self.lib.drmModeObjectGetProperties(self.fd,plane,0xeeeeeeee)
  if not props:return None
  found=None
  try:
   for i in range(props.contents.n):
    pp=self.lib.drmModeGetProperty(self.fd,props.contents.ids[i])
    if not pp:continue
    try:
     p=pp.contents
     if p.name.decode()=='pixel blend mode':
      enums={p.enums[j].name.decode():p.enums[j].value for j in range(p.ne)}
      found=(p.id,int(props.contents.values[i]),enums['None']);break
    finally:self.lib.drmModeFreeProperty(pp)
  finally:self.lib.drmModeFreeObjectProperties(props)
  if not found:return None
  prop,current,value=found
  if self.original is None:self.original=current;self.plane=plane;self.prop=prop
  if current!=value:
   rc=self.lib.drmModeObjectSetProperty(self.fd,plane,0xeeeeeeee,prop,value)
   if rc:raise OSError(c.get_errno(),'Set opaque plane')
  return dict(plane=plane,framebuffer=int(match[2]),property=prop,original=self.original,applied=value)
 def close(self):
  result={}
  if self.fd>=0:
   try:
    if self.original is not None:
     rc=self.lib.drmModeObjectSetProperty(self.fd,self.plane,0xeeeeeeee,self.prop,self.original)
     result={'restore_rc':rc,'errno':c.get_errno() if rc else 0}
   finally:os.close(self.fd);self.fd=-1
  return result
