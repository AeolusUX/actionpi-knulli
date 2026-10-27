"""Mount personal libretro overrides without modifying the base rootfs."""
from pathlib import Path
import os,subprocess,json,sys
ROOT=Path('/userdata/system/custom-cores')
CORE=Path('/usr/lib/libretro')
def same(a,b):
 try:
  x=a.stat();y=b.stat();return (x.st_dev,x.st_ino)==(y.st_dev,y.st_ino)
 except OSError:return False
pairs=[('bennugd_libretro.so','bennugd_libretro.so')]
# KNULLI/Batocera commonly names MAME 2003 Plus mame078plus.
# Standard edition does not replace the arcade cores.
if (ROOT/'DISABLE').exists():
 print('Personal core overrides disabled');raise SystemExit(0)
results=[]
for source,target in pairs:
 src=ROOT/source;dst=CORE/target
 try:
  if not src.is_file() or not src.stat().st_size:raise RuntimeError('Missing personal core: '+source)
  if not same(src,dst):
   if not dst.exists():dst.touch()
   subprocess.run(['mount','--bind',str(src),str(dst)],check=True)
  if not same(src,dst):raise RuntimeError('Bind mount not active: '+target)
  results.append({'source':source,'target':target,'active':True})
 except Exception as exc:results.append({'source':source,'target':target,'active':False,'error':str(exc)})
print(json.dumps(results),flush=True)
raise SystemExit(0 if all(x['active'] for x in results) else 1)
