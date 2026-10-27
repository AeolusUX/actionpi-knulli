"""Scoped display correction for native apps; installed into RAM each boot."""
from pathlib import Path
import os,re,shutil,sys
BASE=Path('/boot/ACTIONPI_FIXES');ORIGINAL=Path('/run/actionpi-app-originals')
APPS=('SDLPoP','retroarch','mupen64plus','yabasanshiro','OpenBOR4432','OpenBOR6412','OpenBOR7142','OpenBOR7530')
HW=('flycast','flycastvl','flycast-xtreme','mupen64plus-next','parallel_n64','yabasanshiro','kronos','beetle-psx-hw')
MARK='# ACTIONPI_APP_OUTPUT_WRAPPER'
def preload(env):
    old=env.get('LD_PRELOAD','').replace(' ',':').split(':')
    filtered=[x for x in old if x and Path(x).name not in ('app_output_rotation.so','retroarch_output_rotation.so','flycast_gl_rotation.so')]
    env['LD_PRELOAD']=':'.join([str(BASE/'app_output_rotation.so'),*filtered])
    return env

def ra_args(args):
    args=list(args);core=''
    for i,x in enumerate(args[:-1]):
        if x in ('-L','--libretro'):core=Path(args[i+1]).name.removesuffix('_libretro.so')
    # Use the existing complete-frame GLES rotation for game AND Ozone.
    # SDL2 video cannot draw Ozone in the bundled RetroArch build.
    driver='gl'
    cfg=Path('/run/actionpi-ra-output-%s.cfg'%os.getpid())
    text='video_driver = "gl"\nvideo_context_driver = "gl_sdl"\n'
    # Recover ordinary/standalone sessions even if an earlier fallback saved RGUI.
    # Hardware-core menu preferences and persistent config files stay unchanged.
    if core not in HW:text+='menu_driver = "ozone"\n'
    cfg.write_text(text)
    # Keep pre-existing append configs and their order, rather than discarding them.
    for i,x in enumerate(args):
        if x=='--appendconfig' and i+1<len(args):args[i+1]+='|'+str(cfg);break
        if x.startswith('--appendconfig='):args[i]=x+'|'+str(cfg);break
    else:args+=['--appendconfig',str(cfg)]
    return args,core,driver

def run(name,args):
    real=ORIGINAL/name;env=os.environ.copy();args=list(args)
    if env.get('ACTIONPI_MALI_SESSION')=='1':
        # ACTIONPI_FLYCAST_VULKAN_DEFAULT
        if name=='retroarch':
            from actionpi_flycast_vulkan import request
            if request(args):return
        preload(env)
        if name=='retroarch':
            args,core,driver=ra_args(args)
            env['SDL_NO_SIGNAL_HANDLERS']='1'
            if core not in HW:
                # Software cores normally request GLES2; the shared rotation FBO needs GLES3.
                env['ACTIONPI_RA_GLES3_CONTEXT']='1'
                helper=str(BASE/'retroarch_gles3_context.so')
                libs=[p for p in env['LD_PRELOAD'].split(':') if Path(p).name!='retroarch_gles3_context.so']
                env['LD_PRELOAD']=':'.join([helper,*libs])
            print('ACTIONPI_APP_OUTPUT retroarch driver='+driver+' core='+core,file=sys.stderr,flush=True)
        elif name in ('mupen64plus','yabasanshiro'):env['SDL_NO_SIGNAL_HANDLERS']='1'
    os.execve(real,[str(Path('/usr/bin')/name),*args],env)

def install():
    assert Path('/boot/boot/knulli.board').read_text().strip()=='helegany-action-pi'
    ORIGINAL.mkdir(exist_ok=True)
    # Avoid desktop glcore/slang selection for the GLES-built hardware cores.
    generator=Path('/usr/lib/python3.12/site-packages/configgen/generators/libretro/libretroGenerator.py')
    if generator.is_file():
        text=generator.read_text()
        marker='# ACTIONPI_GLES_CORE_BACKEND'
        head='def getGFXBackend(system: Emulator) -> str:\n'
        if marker not in text and text.count(head)==1:
            extra="        # ACTIONPI_GLES_CORE_BACKEND\n        if os.environ.get('ACTIONPI_MALI_SESSION') == '1' and not system.isOptSet('gfxbackend') and system.config['core'] in ('mupen64plus-next', 'parallel_n64', 'yabasanshiro', 'flycast', 'flycastvl', 'flycast-xtreme'):\n            return 'gl'\n"
            updated=text.replace(head,head+extra,1);compile(updated,str(generator),'exec');generator.write_text(updated)
    for name in APPS:
        path=Path('/usr/bin')/name
        if not path.is_file():continue
        head=path.read_bytes()[:250]
        if MARK.encode() in head:continue
        if not head.startswith(b'\x7fELF'):continue
        target=ORIGINAL/name
        if not target.exists():shutil.copy2(path,target)
        wrapper='#!/usr/bin/python3\n'+MARK+'\nimport sys\nsys.path.insert(0,"/boot/ACTIONPI_FIXES")\nfrom actionpi_app_launcher import run\nrun('+repr(name)+',sys.argv[1:])\n'
        path.unlink();path.write_text(wrapper);path.chmod(0o755)
