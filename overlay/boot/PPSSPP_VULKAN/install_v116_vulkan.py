import hashlib,json,shlex,shutil,sys
from pathlib import Path
from v116_vulkan_manager import guard,B,MODULE_SHA,sha,write,jsonwrite
guard();assert not (B/'install.json').exists(),'Already installed'
hook=Path('/boot/boot-custom.sh');port=Path('/userdata/roms/ports/PPSSPP Vulkan.sh')
assert not hook.exists() and not port.exists(),'Refuse to overwrite existing hook/launcher'
games=sorted(p for p in Path('/userdata/roms/psp').iterdir() if p.suffix.lower() in ('.iso','.cso','.chd') and p.is_file());assert len(games)==1,'Select game explicitly if multiple exist'
module=B/'mali_candidate.ko'
if not module.exists():shutil.copyfile('/boot/MALI_TEST_V116/mali_candidate.ko',module)
assert sha(module.read_bytes())==MODULE_SHA
rotation=B/'rotation';assert (rotation/'libvulkan.so.1').is_file() and (rotation/'sdl_output_rotation.so').is_file()
shutil.copyfile(rotation/'libvulkan.so.1',rotation/'libvulkan.so')
jsonwrite(B/'settings.json',{'rotation':1,'full_output_rotation':True})
hookdata=b'#!/bin/sh\n[ "$1" = start ] || exit 0\npython3 /boot/PPSSPP_VULKAN/v116_vulkan_manager.py boot >>/boot/PPSSPP_VULKAN/boot.log 2>&1\n'
portdata=('#!/bin/bash\nexec /usr/bin/python3 /boot/PPSSPP_VULKAN/v116_vulkan_manager.py request '+shlex.quote(str(games[0]))+'\n').encode()
write(hook,hookdata);write(port,portdata);port.chmod(0o755)
manifest={'scope':'v116 test SD only; v115 untouched','boot_hook_existed':False,'port_existed':False,'game':str(games[0]),'port':str(port),'hook_sha256':sha(hookdata),'port_sha256':sha(portdata),'rotation':1,'full_output_rotation':True,'exit_combo':'SELECT+START held1second','files':{n:sha((B/n).read_bytes()) for n in ['v116_vulkan_manager.py','v116_vulkan_opacity.py','mali_candidate.ko','rotation/libvulkan.so','rotation/libvulkan.so.1','rotation/sdl_output_rotation.so']}}
jsonwrite(B/'install.json',manifest);print(json.dumps(manifest,indent=2))


