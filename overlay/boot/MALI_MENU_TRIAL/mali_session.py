"""v116 fixed-Mali menu/game supervisor. No driver switching or per-game reboot."""
import json,os,signal,subprocess,sys,time
from pathlib import Path
from actionpi_es_menu_return import prepare as prepare_menu_return, restore as restore_menu_return
from mali_menu_trial import environment,guard,master_available,snapshot,require,BASE

B=Path('/boot/PPSSPP_VULKAN');SESSION=B/'transaction/session'
BOOTID=Path('/proc/sys/kernel/random/boot_id').read_text().strip()

def atomic(path,data):
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('w') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
    tmp.replace(path)

def same_owner():
    require(Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOTID,'Boot changed')
    require(Path('/sys/bus/platform/devices/1800000.gpu/driver').resolve().name=='mali','Mali owner changed')

def game_path(value=None):
    if value is None:
        games=[p for p in Path('/userdata/roms/psp').iterdir() if p.suffix.lower() in ('.iso','.cso','.chd')]
        require(len(games)==1,'Specify PSP game');value=str(games[0])
    game=Path(value).resolve()
    require(Path('/userdata/roms/psp').resolve() in game.parents and game.is_file(),'Invalid PSP game')
    require(game.suffix.lower() in ('.iso','.cso','.chd'),'Invalid extension')
    return str(game)

def request_game(value=None,seconds=None,ui_only=False):
    state=json.loads((SESSION/'state.json').read_text())
    require(state['boot_id']==BOOTID and state['phase']=='menu','Session is not at menu')
    require(not (SESSION/'request.json').exists(),'Request pending')
    if seconds is not None:require(10<=seconds<=180,'Invalid test duration')
    atomic(SESSION/'request.json',{'game':None if ui_only else game_path(value),'seconds':seconds,'ui_only':bool(ui_only)})

def stop_menu(proc,folder):
    (folder/'stop').write_text('normal SDL quit\n')
    try:proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid,signal.SIGTERM)
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
        raise RuntimeError('Menu did not quit normally; game was not launched')
    require(proc.returncode==0,'Menu exit failed: '+str(proc.returncode))
    require(master_available()['available'],'Menu retained DRM master')
    same_owner();snapshot(folder,'after')
    restore_menu_return()

def supervise():
    restore_menu_return()
    guard();require(not SESSION.exists(),'Session already exists');SESSION.mkdir()
    proc=None;rotation=1;counter=0;cycles=[];result={'boot_id':BOOTID,'status':'running'}
    launcher=Path('/usr/bin/emulatorlauncher');saved=Path('/run/actionpi-emulatorlauncher-original')
    require(not saved.exists(),'Launcher backup already exists')
    saved.write_bytes(launcher.read_bytes());saved.chmod(0o755)
    try:
        launcher.write_bytes((BASE/'mali_emulatorlauncher.py').read_bytes());launcher.chmod(0o755)
        while True:
            same_owner();require(master_available()['available'],'DRM master unavailable before menu')
            counter+=1;folder=SESSION/('menu-%02d'%counter);folder.mkdir()
            env=environment();env['LD_PRELOAD']=str(BASE/'mali_menu_audit.so');env['ACTIONPI_MENU_STOP']=str(folder/'stop')
            env['ACTIONPI_MALI_SESSION']='1'
            if cycles:prepare_menu_return()
            cmd=['/usr/bin/emulationstation','--screenrotate',str(rotation)]
            with (folder/'menu.log').open('wb') as log:
                proc=subprocess.Popen(cmd,cwd='/userdata',env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                atomic(SESSION/'state.json',{'phase':'menu','boot_id':BOOTID,'pid':proc.pid,'rotation':rotation,'completed_games':len(cycles),'folder':str(folder)})
                started=time.monotonic();captured=False;request=None;change=None;ending=False
                while proc.poll() is None:
                    if not captured and time.monotonic()-started>=6:
                        snapshot(folder,'running',proc.pid);captured=True
                    if (SESSION/'stop-session').exists():ending=True;break
                    if (SESSION/'rotation.json').exists():
                        change=json.loads((SESSION/'rotation.json').read_text())['rotation']
                        require(change in (0,1,2,3),'Invalid menu rotation');(SESSION/'rotation.json').unlink();break
                    if (SESSION/'request.json').exists():
                        request=json.loads((SESSION/'request.json').read_text());(SESSION/'request.json').unlink();break
                    time.sleep(.15)
                if proc.poll() is not None and not (request or change is not None or ending):
                    if proc.returncode==0:
                        result['status']='menu exited normally';return
                    raise RuntimeError('Menu exited outside supervisor request')
                atomic(SESSION/'state.json',{'phase':'menu-closing','boot_id':BOOTID,'pid':proc.pid,'completed_games':len(cycles)})
                stop_menu(proc,folder);proc=None
            if ending:break
            if change is not None:rotation=change;continue
            game='' if request.get('ui_only') else game_path(request['game']);seconds=request.get('seconds')
            folder=SESSION/('game-%02d'%(len(cycles)+1));folder.mkdir()
            atomic(SESSION/'state.json',{'phase':'game','boot_id':BOOTID,'folder':str(folder),'completed_games':len(cycles)})
            # Fresh process, no menu EGL/preload inheritance. PSP builds its own known-good environment.
            env=os.environ.copy()
            for key in list(env):
                if key.startswith(('SDL_','MESA_','WLR_','VK_')) or key in ('LD_PRELOAD','LD_LIBRARY_PATH','EGL_PLATFORM','WAYLAND_DISPLAY','DISPLAY'):env.pop(key,None)
            cmd=[sys.executable,str(BASE/'v116_ppsspp_session.py'),game,str(folder),str(seconds or 0)]
            with (folder/'runner.log').open('wb') as log:
                p=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                # No ordinary game timeout. SELECT+START retains its proven one-second hold.
                while p.poll() is None:
                    if (SESSION/'stop-session').exists():(folder/'stop').touch()
                    time.sleep(.2)
                require(p.returncode==0,'PPSSPP session failed; inspect '+str(folder))
            require(master_available()['available'],'Game retained DRM master');same_owner()
            snapshot(folder,'after');cycles.append({'folder':str(folder),'boot_id':BOOTID,'owner':'mali'})
            atomic(SESSION/'cycles.json',cycles)
        result['status']='stopped normally'
    except BaseException as e:
        result.update(status='failed',error=repr(e));raise
    finally:
        launcher.write_bytes(saved.read_bytes());launcher.chmod(0o755)
        if proc and proc.poll() is None:
            try:stop_menu(proc,folder)
            except BaseException as e:result['cleanup_error']=repr(e)
        restore_menu_return()
        result['cycles']=cycles;atomic(SESSION/'result.json',result)

def main():
    mode=sys.argv[1]
    if mode=='run':supervise()
    elif mode=='request':request_game(sys.argv[2] if len(sys.argv)>2 else None)
    elif mode=='request-ui':request_game(ui_only=True)
    elif mode=='test-request':request_game(None,int(sys.argv[2]))
    elif mode=='rotate':atomic(SESSION/'rotation.json',{'rotation':int(sys.argv[2])})
    elif mode=='stop':(SESSION/'stop-session').touch()
    else:raise ValueError(mode)
if __name__=='__main__':main()
