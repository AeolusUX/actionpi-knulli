"""S12 postshare installer, after the original partition expansion and mount."""
from pathlib import Path, PurePosixPath
import hashlib,json,os,subprocess,tarfile,time
B=Path('/boot/STABLE_V119')

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while data:=f.read(4*1024*1024):h.update(data)
 return h.hexdigest()

def install():
 if (B/'install-complete.json').exists():return
 assert Path('/boot/boot/knulli.board').read_text().strip()=='helegany-action-pi'
 mounts=[line.split() for line in Path('/proc/mounts').read_text().splitlines()]
 assert any(x[1]=='/userdata' and x[2] not in ('tmpfs','ramfs') for x in mounts),'SHARE is not mounted on storage'
 manifest=json.loads((B/'payload.json').read_text())
 for name in ('settings.tar.gz',):
  assert digest(B/name)==manifest['payloads'][name],name+' checksum mismatch'
 for name in ('settings.tar.gz',):
  with tarfile.open(B/name,'r:gz') as archive:
   for entry in archive.getmembers():
    path=PurePosixPath(entry.name)
    assert not path.is_absolute() and '..' not in path.parts,'Unsafe archive path'
    assert entry.isfile() or entry.isdir() or entry.issym() or entry.islnk()
   archive.extractall('/userdata',filter='data')
 tmp=B/'install-complete.tmp'
 tmp.write_text(json.dumps({'version':'v119','time':time.strftime('%F %T'),'settings_restored':True,'bios_restored':False,'edition':'distribution'},indent=2))
 tmp.replace(B/'install-complete.json');os.sync()
 print('v119 settings installed after SHARE expansion; restarting once.',flush=True)
 subprocess.run(['/sbin/reboot','-f'],check=True)
 # Do not let init launch graphics while the reboot request is pending.
 while True:time.sleep(1)

if __name__=='__main__':install()
