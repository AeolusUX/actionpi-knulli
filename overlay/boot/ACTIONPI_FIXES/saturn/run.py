#!/usr/bin/python3
"""Yaba Sanshiro 1.20.51 GLES in the existing Mali game session."""
from pathlib import Path
import json,os,shutil,sys
import xml.etree.ElementTree as ET
from copy import deepcopy
BASE=Path(__file__).resolve().parent
if os.environ.get('ACTIONPI_MALI_SESSION')!='1':
    raise SystemExit('Run this application through the existing Mali game-session supervisor.')
rotation=Path('/boot/ACTIONPI_FIXES/app_output_rotation.so')
if not rotation.is_file():raise SystemExit('Existing Action Pi rotation helper is missing.')
oldhome=Path(os.environ.get('HOME','/userdata/system'))
home=Path('/userdata/system/configs/yabasanshiro-1.20.51')
cfg=home/'.yabasanshiro';cfg.mkdir(parents=True,exist_ok=True)
es=cfg/'.emulationstation';es.mkdir(exist_ok=True)
source=oldhome/'.yabasanshiro/es_temporaryinput.cfg'
if source.is_file():shutil.copy2(source,es/'es_temporaryinput.cfg')
elif not (es/'es_temporaryinput.cfg').exists():
    source=Path('/userdata/system/configs/emulationstation/es_input.cfg')
    if source.is_file():shutil.copy2(source,es/'es_temporaryinput.cfg')
# ACTIONPI_L3_MENU: copy only the real L3 binding, keeping game controls intact.
es_source=Path('/userdata/system/configs/emulationstation/es_input.cfg')
menu_xml=es/'es_temporaryinput.cfg'
if es_source.is_file() and menu_xml.is_file():
    source_tree=ET.parse(es_source)
    target_tree=ET.parse(menu_xml)
    changed=False
    for device in target_tree.getroot().iter('inputConfig'):
        match=next((d for d in source_tree.getroot().iter('inputConfig') if d.get('deviceGUID')==device.get('deviceGUID')),None)
        if match is None:continue
        binding=next((b for b in match.findall('input') if b.get('name')=='l3'),None)
        if binding is None:continue
        for prior in list(device.findall('input')):
            if prior.get('name')=='l3':device.remove(prior)
        device.append(deepcopy(binding));changed=True
    if changed:target_tree.write(menu_xml,encoding='utf-8',xml_declaration=True)
defaults=cfg/'default.config'
if not defaults.exists():
    defaults.write_text(json.dumps({'Resolution':0,'Aspect rate':1,'Rotate screen':False,'Rotate screen resolution':0,'Use compute shader':False,'Full screen':True,'Show Fps':False,'frame skip':False},indent=2)+'\n')
# ACTIONPI_SATURN_INPUT_SCHEMA: legacy flat keymap does not bind v1.20.51 pads.
keymap=cfg/'keymapv3.json'
mapping=json.loads(keymap.read_text()) if keymap.exists() else {}
existing_pad=mapping.get('player1',{}).get('pad')
required=('up','down','left','right','start','a','b','c','x','y','z','l','r','analogx','analogy')
if not isinstance(existing_pad,dict) or not all(k in existing_pad for k in required):
    es_input=Path('/userdata/system/configs/emulationstation/es_input.cfg')
    devices=list(ET.parse(es_input).getroot().iter('inputConfig'))
    device=next(d for d in devices if d.get('deviceName')=='adc_gamepad')
    guid=device.get('deviceGUID')
    inputs={b.get('name'):b for b in device.findall('input')}
    bind_names={'up':'up','down':'down','left':'left','right':'right','start':'start',
                'a':'a','b':'b','c':'pagedown','x':'x','y':'y','z':'pageup',
                'l':'l2','r':'r2','analogx':'joystick1left','analogy':'joystick1up'}
    pad={}
    for target,source_name in bind_names.items():
        b=inputs[source_name]
        pad[target]={'deviceGUID':guid,'type':b.get('type'),'id':int(b.get('id')),'value':int(b.get('value'))}
    player=mapping.setdefault('player1',{})
    player.update({'DeviceID':0,'deviceGUID':guid,'deviceName':device.get('deviceName'),'pad':pad})
    player.setdefault('padmode',0)
    mapping['_actionpi_input_schema']=1
    keymap.write_text(json.dumps(mapping,indent=2)+'\n')

env=os.environ.copy();env['HOME']=str(home);env['SDL_NO_SIGNAL_HANDLERS']='1'
for key in list(env):
    if key.startswith('ACTIONPI_SATURN_'):env.pop(key)
old=env.get('LD_PRELOAD','').replace(' ',':').split(':')
excluded={'saturn_jit.so','saturn_wait.so','app_output_rotation.so'}
env['LD_PRELOAD']=':'.join([str(rotation),*[p for p in old if p and Path(p).name not in excluded]])
# Official source selects SH2 dynarec id 3 directly; the old binary shim is excluded.
os.chdir(home)
binary=BASE/'yabasanshiro'
os.execve(binary,['/usr/bin/yabasanshiro',*sys.argv[1:]],env)
