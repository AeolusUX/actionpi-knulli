"""Disable only these two installed launcher hooks, from a normal v116 boot."""
from pathlib import Path
import json
from v116_vulkan_manager import guard,B,T,TOKEN,restore_all,archive,sha
guard();assert TOKEN.decode() not in Path('/proc/cmdline').read_text(),'Exit the Vulkan game and reboot normally first'
if T.exists():restore_all();archive()
m=json.loads((B/'install.json').read_text())
for path,key,dest in [(Path('/boot/boot-custom.sh'),'hook_sha256',B/'disabled-boot-custom.sh'),(Path(m['port']),'port_sha256',B/'disabled-port.sh')]:
 assert path.exists() and sha(path.read_bytes())==m[key],'User-modified file; refuse to move'
 assert not dest.exists(),'Already disabled'
for path,key,dest in [(Path('/boot/boot-custom.sh'),'hook_sha256',B/'disabled-boot-custom.sh'),(Path(m['port']),'port_sha256',B/'disabled-port.sh')]:path.rename(dest)
print('Vulkan launcher disabled; normal v116 boot files preserved. Diagnostic backups retained.')


