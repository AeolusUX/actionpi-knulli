#!/usr/bin/env python3
"""Short-lived brightness OSD on a free DRM plane, independent of GL/Vulkan.

The buffer belongs to our non-master client. A borrowed application master fd is
used only for a plane ioctl and immediately closed, never held across a wait.
"""
from pathlib import Path
import array,ctypes as C,fcntl,json,mmap,os,re,signal,sys,time

U=C.c_uint32;Q=C.c_uint64;I=C.c_int;P=C.c_void_p
class Plane(C.Structure):
    _fields_=[('count',U),('formats',C.POINTER(U)),('id',U),('crtc',U),('fb',U),('cx',U),('cy',U),('x',U),('y',U),('possible',U),('gamma',U)]
class Props(C.Structure):
    _fields_=[('n',U),('ids',C.POINTER(U)),('values',C.POINTER(Q))]
class Enum(C.Structure):
    _fields_=[('value',Q),('name',C.c_char*32)]
class Prop(C.Structure):
    _fields_=[('id',U),('flags',U),('name',C.c_char*32),('nv',I),('values',C.POINTER(Q)),('ne',I),('enums',C.POINTER(Enum)),('nb',I),('blobs',C.POINTER(U))]
class Dumb(C.Structure):
    _fields_=[('h',U),('w',U),('bpp',U),('flags',U),('handle',U),('pitch',U),('size',Q)]
class Map(C.Structure):
    _fields_=[('handle',U),('pad',U),('offset',Q)]

lib=C.CDLL('libdrm.so.2',use_errno=True);libc=C.CDLL(None,use_errno=True);libc.syscall.restype=C.c_long
def fn(name,args,result=I):
    f=getattr(lib,name);f.argtypes=args;f.restype=result;return f
is_master=fn('drmIsMaster',[I])
get_plane=fn('drmModeGetPlane',[I,U],C.POINTER(Plane));free_plane=fn('drmModeFreePlane',[C.POINTER(Plane)],None)
get_props=fn('drmModeObjectGetProperties',[I,U,U],C.POINTER(Props));free_props=fn('drmModeFreeObjectProperties',[C.POINTER(Props)],None)
get_prop=fn('drmModeGetProperty',[I,U],C.POINTER(Prop));free_prop=fn('drmModeFreeProperty',[C.POINTER(Prop)],None)
set_prop=fn('drmModeObjectSetProperty',[I,U,U,U,Q])
set_plane=fn('drmModeSetPlane',[I,U,U,U,U,I,I,U,U,U,U,U,U])
add_fb=fn('drmModeAddFB2',[I,U,U,U,C.POINTER(U),C.POINTER(U),C.POINTER(U),C.POINTER(U),U])
rm_fb=fn('drmModeRmFB',[I,U])
client_cap=fn('drmSetClientCap',[I,Q,Q])

def check(rc,what):
    if rc:raise OSError(C.get_errno(),what)

def master():
    for proc in Path('/proc').glob('[0-9]*'):
        if int(proc.name)==os.getpid():continue
        try:
            fds=[int(p.name) for p in (proc/'fd').iterdir() if os.readlink(p)=='/dev/dri/card0']
            if not fds:continue
            pfd=os.pidfd_open(int(proc.name))
            try:
                for fd in fds:
                    dup=libc.syscall(438,pfd,fd,0)
                    if dup<0:continue
                    if is_master(dup)==1:return dup
                    os.close(dup)
            finally:os.close(pfd)
        except (OSError,ValueError):pass
    raise RuntimeError('No current DRM master; do not take master')

def props(fd,plane):
    result={};p=get_props(fd,plane,0xeeeeeeee)
    if not p:raise RuntimeError('Plane properties unavailable')
    try:
        for i in range(p.contents.n):
            q=get_prop(fd,p.contents.ids[i])
            if not q:continue
            try:
                t=q.contents
                result[t.name.decode()]=(t.id,int(p.contents.values[i]))
            finally:free_prop(q)
    finally:free_props(p)
    return result

FONT={
 '0':['111','101','101','101','111'],'1':['010','110','010','010','111'],
 '2':['111','001','111','100','111'],'3':['111','001','111','001','111'],
 '4':['101','101','111','001','001'],'5':['111','100','111','001','111'],
 '6':['111','100','111','101','111'],'7':['111','001','010','010','010'],
 '8':['111','101','111','101','111'],'9':['111','101','111','001','111'],
 '%':['101','001','010','100','101']}

def bitmap(percent):
    w,h=300,72;bg=0xff202830;white=0xfff0f4f8;blue=0xff38c8dc
    a=array.array('I',[bg])*(w*h)
    def rect(x,y,rw,rh,color):
        row=array.array('I',[color])*rw
        for yy in range(y,y+rh):a[yy*w+x:yy*w+x+rw]=row
    # Sun, percentage, horizontal brightness bar.
    rect(24,23,18,18,white)
    for x,y,rw,rh in ((30,12,6,6),(30,46,6,6),(13,29,6,6),(47,29,6,6),(19,18,5,5),(42,18,5,5),(19,42,5,5),(42,42,5,5)):rect(x,y,rw,rh,white)
    x=68
    for char in str(percent)+'%':
        for yy,row in enumerate(FONT[char]):
            for xx,bit in enumerate(row):
                if bit=='1':rect(x+xx*4,13+yy*4,4,4,white)
        x+=16
    rect(68,45,211,12,0xff53606c)
    fill=211*percent//100
    if fill:rect(68,45,fill,12,blue)
    # Logical landscape -> native portrait clockwise, matching panel mounting.
    b=array.array('I',[0])*(w*h)
    for y in range(h):
        for x in range(w):b[x*h+(h-1-y)]=a[y*w+x]
    return h,w,b

def brightness():
    b=next(Path('/sys/class/backlight').glob('*'))
    return max(0,min(100,round(int((b/'brightness').read_text())*100/int((b/'max_brightness').read_text()))))

def show(seconds=2.2,trial=False):
    own=-1;fb=U();bo=Dumb();memory=None;plane=None;saved={};running=True
    def stop(*_):
        nonlocal running
        running=False
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    try:
        # Confirm an existing master before opening our resource-only client.
        fd=master();os.close(fd)
        own=os.open('/dev/dri/card0',os.O_RDWR|os.O_CLOEXEC)
        if is_master(own)==1:raise RuntimeError('Refuse to hold DRM master')
        client_cap(own,2,1)
        state=Path('/sys/kernel/debug/dri/0/state').read_text()
        crtc=re.search(r'crtc\[(\d+)\]: DE-0\n\s*enable=1',state)
        mode=re.search(r'mode: "(\d+)x(\d+)"',state)
        if not crtc or not mode:raise RuntimeError('No active panel')
        screenw,screenh=map(int,mode.groups())
        for match in re.finditer(r'plane\[(\d+)\]:[^\n]*\n\s*crtc=\(null\)\n\s*fb=0',state):
            candidate=int(match[1]);p=get_plane(own,candidate)
            if not p:continue
            try:
                info=p.contents;pr=props(own,candidate)
                formats=[info.formats[i] for i in range(info.count)]
                if info.possible&1 and pr.get('type',(0,-1))[1]==0 and 0x34325258 in formats:
                    plane=candidate;saved=pr;break
            finally:free_plane(p)
        if plane is None:raise RuntimeError('No unused panel overlay plane')
        width,height,_=bitmap(0)
        bo.h=height;bo.w=width;bo.bpp=32
        fcntl.ioctl(own,0xc02064b2,bo)
        handles=(U*4)(bo.handle,0,0,0);pitches=(U*4)(bo.pitch,0,0,0);offsets=(U*4)()
        check(add_fb(own,width,height,0x34325258,handles,pitches,offsets,C.byref(fb),0),'Add OSD framebuffer')
        mapping=Map(bo.handle,0,0);fcntl.ioctl(own,0xc01064b3,mapping)
        memory=mmap.mmap(own,bo.size,mmap.MAP_SHARED,mmap.PROT_WRITE|mmap.PROT_READ,offset=mapping.offset)
        def paint():
            _,_,pixels=bitmap(brightness())
            for y in range(height):memory[y*bo.pitch:y*bo.pitch+width*4]=pixels[y*width:(y+1)*width].tobytes()
        paint()
        fd=master()
        try:
            current=get_plane(fd,plane)
            if not current:raise RuntimeError('Cannot recheck plane')
            try:
                if current.contents.fb:raise RuntimeError('Overlay plane was acquired by another client')
            finally:free_plane(current)
            for key,value in (('zpos',3),('alpha',65535),('pixel blend mode',2)):
                if key in saved:check(set_prop(fd,plane,0xeeeeeeee,saved[key][0],value),'Set OSD '+key)
            check(set_plane(fd,plane,int(crtc.group(1)),fb.value,0,screenw-width-22,(screenh-height)//2,width,height,0,0,width<<16,height<<16),'Show OSD')
        finally:os.close(fd)
        print(json.dumps({'shown':True,'plane':plane,'fb':fb.value,'seconds':seconds,'holds_master':False}),flush=True)
        started=time.monotonic();deadline=started+seconds;last=None
        request=Path('/run/actionpi-brightness-osd.request')
        while running and time.monotonic()<deadline and time.monotonic()-started<15:
            if not trial and request.exists():
                change=request.stat().st_mtime_ns
                if change!=last:last=change;paint();deadline=time.monotonic()+seconds
            time.sleep(.08)
    finally:
        if fb.value and own>=0:
            # RmFB detaches only our framebuffer; do not blank the application's plane.
            rm_fb(own,fb.value)
        if plane is not None:
            try:
                fd=master()
                try:
                    p=get_plane(fd,plane)
                    if p:
                        try:
                            if not p.contents.fb:
                                for key in ('zpos','alpha','pixel blend mode'):
                                    if key in saved:set_prop(fd,plane,0xeeeeeeee,saved[key][0],saved[key][1])
                        finally:free_plane(p)
                finally:os.close(fd)
            except (OSError,RuntimeError):pass
        if memory is not None:memory.close()
        if bo.handle and own>=0:
            handle=U(bo.handle);fcntl.ioctl(own,0xc00464b4,handle)
        if own>=0:os.close(own)
        print('OSD_CLEANED_UP',flush=True)

if __name__=='__main__':
    with open('/run/actionpi-brightness-osd.lock','w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:sys.exit(0)
        show(float(sys.argv[2]) if len(sys.argv)>2 else 2.2,trial='--trial' in sys.argv)
