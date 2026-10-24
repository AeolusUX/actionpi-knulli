"""Run the original configgen wrapper; scope output correction to SDL2 RetroArch only."""
import os,runpy,subprocess,sys,threading,time
from pathlib import Path

Popen=subprocess.Popen
def rotated_popen(args,*pos,**kwargs):
    command=[str(x) for x in args] if isinstance(args,(list,tuple)) else []
    if '/userdata/roms/ports/PortMaster.sh' in command:
        sys.path.insert(0,'/boot/ACTIONPI_FIXES')
        from actionpi_portmaster_fix import prepare
        prepare()
    is_ra=bool(command) and (command[0]=='/usr/bin/retroarch' or command[:4]==['nice','-n','-4','/usr/bin/retroarch'])
    cfg=Path('/tmp/actionpi-retroarch-sdl2-audio.cfg')
    shim=None
    if is_ra and cfg.exists() and 'video_driver = "sdl2"' in cfg.read_text():
        shim='/boot/MALI_MENU_TRIAL/retroarch_output_rotation.so'
    if (is_ra and cfg.exists() and 'video_driver = "gl"' in cfg.read_text()) or '/usr/bin/flycast' in command:
        shim='/boot/ACTIONPI_FIXES/flycast_gl_rotation.so'
    if shim:
        env=dict(kwargs.get('env') or os.environ)
        env['LD_PRELOAD']=shim+(':'+env['LD_PRELOAD'] if env.get('LD_PRELOAD') else '')
        if any(name+'_libretro.so' in x for name in ('flycastvl','flycast-xtreme') for x in command):
            # SDL evdev emergency cleanup otherwise re-raises JIT memory faults,
            # discarding the original siginfo/ucontext needed by old Flycast.
            env['SDL_NO_SIGNAL_HANDLERS']='1'
        kwargs['env']=env
    child=Popen(args,*pos,**kwargs)
    if command[:3]==['nice','-n','-4'] and len(command)>3:
        sys.path.insert(0,'/boot/ACTIONPI_FIXES')
        from home_exit import register
        register(child.pid,command[3])
    for name in ('flycastvl','flycast-xtreme'):
        if any(name+'_libretro.so' in x for x in command) and Path('/boot/ACTIONPI_FIXES/ENABLE_FAULT_TRACE').exists():
            tracer=Path('/boot/ACTIONPI_FIXES/flycast_fault_trace.py')
            if tracer.exists() and (tracer.parent/'ENABLE_FAULT_TRACE').exists():
                Popen([sys.executable,str(tracer),str(child.pid),str(tracer.parent/(name+'-fault'))],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            def record(p=child,label=name):
                dest=Path('/boot/ACTIONPI_FIXES')/(label+'-maps.txt')
                for _ in range(12):
                    try:
                        text=Path('/proc/%d/maps'%p.pid).read_text()
                        if label+'_libretro.so' in text:dest.write_text(text)
                    except OSError:break
                    time.sleep(.1)
            threading.Thread(target=record,daemon=True).start()
    return child

def launch():
    subprocess.Popen=rotated_popen
    try:runpy.run_path('/run/actionpi-emulatorlauncher-original',run_name='__main__')
    finally:subprocess.Popen=Popen

if __name__=='__main__':launch()
