from pathlib import Path
import json,subprocess,sys,hashlib,difflib
root=Path(sys.argv[1]);base=root/'outputs/flycast-2.7-prep';dest=Path('/root/actionpi-flycast-2.7/source')
for r in json.loads((base/'SOURCES.json').read_text()):
 archive=base/'archives'/r['archive'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==r['sha256']
 p=dest/r['path'];p.mkdir(parents=True,exist_ok=True)
 subprocess.run(['tar','-xzf',str(archive),'-C',str(p),'--strip-components=1'],check=True)
version=json.loads((base/'VERSION.json').read_text());p=dest/'CMakeLists.txt';before=p.read_text()
assert before.count('set(GIT_VERSION "v0.0.0-0-g000000000")')==1
after=before.replace('set(GIT_VERSION "v0.0.0-0-g000000000")','set(GIT_VERSION "v2.7")').replace('set(GIT_HASH "000000000")','set(GIT_HASH "'+version['commit'][:9]+'")')
p.write_text(after)
(base/'archive-version.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/CMakeLists.txt',tofile='b/CMakeLists.txt')))
(dest/'.source-extracted').write_text(version['commit'])
print('PINNED_2_7_SOURCE_READY')
