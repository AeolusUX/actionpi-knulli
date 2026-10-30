#!/usr/bin/env python3
"""Rebuild the archived, already patched GLES source; requires a matching SDK."""
from pathlib import Path
import argparse,os,subprocess,json
p=argparse.ArgumentParser();p.add_argument('--sdk',type=Path,required=True);p.add_argument('--toolchain-prefix',required=True);p.add_argument('--cmake',default='cmake');a=p.parse_args()
base=Path(__file__).resolve().parent;sdk=a.sdk.resolve();source=base/'source/yabause';build=base/'build';host=base/'host-tools';host.mkdir(exist_ok=True)
assert source.is_dir(),'Extract the full source asset, not only the Git checkout.'
subprocess.run(['cc','-O2',str(source/'src/retro_arena/nanogui-sdl/resources/bin2c.c'),'-o',str(host/'bin2c')],check=True)
old='/root/actionpi-saturn-1.20.51-trial'
for f in list(source.rglob('CMakeLists.txt'))+list(source.rglob('*.cmake')):
    t=f.read_text();u=t.replace(old+'/sdk',str(sdk)).replace(old,str(base))
    if u!=t:f.write_text(u)
ref=(base/'aarch64-actionpi.cmake').read_text().replace(old+'/sdk',str(sdk))
oldprefix='/opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-'
ref=ref.replace(oldprefix,a.toolchain_prefix)
sysroot=subprocess.check_output([a.toolchain_prefix+'gcc','-print-sysroot'],text=True).strip()
ref=ref.replace('/opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu/aarch64-none-linux-gnu/libc',sysroot)
tool=base/'toolchain.cmake';tool.write_text(ref)
subprocess.run([a.cmake,'-S',str(base/'libchdr'),'-B',str(base/'libchdr-build'),'-DCMAKE_TOOLCHAIN_FILE='+str(tool),'-DCMAKE_BUILD_TYPE=Release','-DBUILD_SHARED_LIBS=OFF','-DBUILD_CHDR_TESTS=OFF'],check=True)
subprocess.run([a.cmake,'--build',str(base/'libchdr-build'),'-j2'],check=True)
args=json.loads((base/'configure-command.json').read_text())[1:]
args=[x.replace(old+'/sdk',str(sdk)).replace(old,str(base)).replace('/mnt/c/Users/2nd/Documents/Codex/2026-09-16/actionpi-vulkan-continuation/outputs/saturn-1.20.51-prep/aarch64-actionpi.cmake',str(tool)) for x in args]
subprocess.run([a.cmake,*args],check=True)
subprocess.run([a.cmake,'--build',str(build),'--target','yabause-retro-arena','-j2'],check=True)
subprocess.run([a.toolchain_prefix+'strip','--strip-unneeded','-o',str(base/'yabasanshiro'),str(build/'src/retro_arena/yabasanshiro-1.20.51')],check=True)
