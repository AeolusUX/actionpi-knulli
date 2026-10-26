"""Build two clean v1.0.3 images from the matching immutable v1.0.2 editions."""
from pathlib import Path
import copy,hashlib,importlib.util,io,json,os,re,subprocess,tarfile

ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ.get('ACTIONPI_IMAGE_DIR',ROOT/'images')).resolve();PREP=OUT/'public-v1.0.3-prep'
spec=importlib.util.spec_from_file_location('v103fat',ROOT/'tools/fat32_image.py')
u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
sha=lambda b:hashlib.sha256(b).hexdigest()
def linux(p):
    s=p.resolve().as_posix()
    return '/mnt/'+s[0].lower()+s[2:] if len(s)>1 and s[1]==':' else s
def mcopy(image,source,target):
    args=['mcopy','-o','-i',linux(image)+'@@'+str(u.BOOT_RESOURCE_OFFSET),linux(source),'::/'+target]
    subprocess.run((['wsl','-d','Ubuntu','--']+args) if os.name=='nt' else args,check=True)
def setting(text,key,value):
    pattern=r'^'+re.escape(key)+r'=.*$'
    if re.search(pattern,text,re.M):return re.sub(pattern,key+'='+value,text,flags=re.M)
    return text.rstrip()+'\n'+key+'='+value+'\n'
def ranges(fat,paths):
    result=[(fat.offset,fat.data_offset)]
    for name in ('/','/STABLE_V119','/ACTIONPI_FIXES'):
        cluster=fat.root if name=='/' else fat.locate(name)[2]
        result.extend((fat.cluster_offset(c),fat.cluster_offset(c)+fat.cluster_size) for c in fat.chain(cluster))
    for path in paths:
        try:entry=fat.locate('/'+path)
        except FileNotFoundError:continue
        result.extend((fat.cluster_offset(c),fat.cluster_offset(c)+fat.cluster_size) for c in fat.chain(entry[2]))
    return result
def protected():
    return {p.name:[p.stat().st_size,p.stat().st_mtime_ns] for p in OUT.glob('action-pi-knulli-v1.0.2*.img*')}

def build(crc=False):
    edition='crc-ko' if crc else 'standard'
    source=OUT/('action-pi-knulli-v1.0.2-crc-ko.img' if crc else 'action-pi-knulli-v1.0.2.img')
    final=OUT/('action-pi-knulli-v1.0.3'+('-crc-ko' if crc else '')+'.img')
    partial=final.with_suffix('.img.partial');stage=PREP/edition;stage.mkdir(parents=True,exist_ok=True)
    assert not final.exists() and not partial.exists(),'Refuse overwrite'
    expected='f67382eec2ac39ac4f5a2d59fcb93d008535d8e1f77e88a20cf87abedc186c7f' if crc else '18cfbf89a81dd4245caee0d557e8b12bf00c8627e01d81b7b2ac28b210143cc9'
    previous=protected();additions={}
    for target,local in {
        'system/rumble-fix/apply.py':'rumble-fix/apply.py',
        'system/background-quiet/quiet_start.py':'background-quiet/quiet_start.py',
        **{'system/brightness-osd/'+n:'brightness-osd/'+n for n in ('overlay.py','notify.sh','brightness-button','bin/knulli-brightness')}
    }.items():additions[target]=(ROOT/'config/userdata/system'/local).read_bytes()
    additions['system/configs/multimedia_keys.conf']=(ROOT/'config/defaults/multimedia_keys.conf').read_bytes()
    for name,data in additions.items():
        if name.endswith('.py'):compile(data,name,'exec')
    changed={};removed=[];records={}
    with source.open('rb') as stream:
        fat=u.Fat32Editor(stream,u.BOOT_RESOURCE_OFFSET)
        original=fat.read_file('/STABLE_V119/settings.tar.gz')
        payload=json.loads(fat.read_file('/STABLE_V119/payload.json'))
        assert sha(original)==payload['payloads']['settings.tar.gz']
        target=io.BytesIO()
        with tarfile.open(fileobj=io.BytesIO(original),mode='r:gz') as src:
            members=src.getmembers()
            old={e.name:src.extractfile(e).read() for e in members if e.isfile()}
            conf=old['system/knulli.conf'].decode()
            assert 'system.language=en_US' in conf.splitlines() and 'wifi.enabled=0' in conf.splitlines()
            assert not any(re.match(r'^wifi(?:\.\d+)?\.(?:ssid|key)=.+',s) for s in conf.splitlines())
            additions['system/knulli.conf']=setting(conf,'system.telemetry','0').encode()
            custom=old.get('system/custom.sh',b'#!/bin/sh\n').decode()
            assert 'ACTIONPI_RUMBLE_CALIBRATION' not in custom and 'ACTIONPI_QUIET_START' not in custom
            custom+='\n# ACTIONPI_QUIET_START\nif [ "$1" = start ]; then\n    python3 /userdata/system/background-quiet/quiet_start.py || true\nfi\n'
            custom+='\n# ACTIONPI_RUMBLE_CALIBRATION\nif [ "$1" = start ]; then\n    python3 /userdata/system/rumble-fix/apply.py start || true\nfi\n'
            additions['system/custom.sh']=custom.encode()
            with tarfile.open(fileobj=target,mode='w:gz',compresslevel=1,format=tarfile.PAX_FORMAT) as dst:
                done=set()
                for e in members:
                    if e.name in additions:
                        data=additions[e.name];n=copy.copy(e);n.size=len(data);dst.addfile(n,io.BytesIO(data));done.add(e.name)
                    else:
                        data=old.get(e.name);dst.addfile(copy.copy(e),io.BytesIO(data) if data is not None else None)
                        records[e.name]=(e.mode,e.type,e.linkname,sha(data) if data is not None else None)
                for name,data in additions.items():
                    if name in done:continue
                    e=tarfile.TarInfo(name);e.size=len(data);e.mode=0o755 if name.endswith(('.sh','.py')) or name.endswith(('brightness-button','bin/knulli-brightness')) else 0o644
                    e.uname=e.gname='root';dst.addfile(e,io.BytesIO(data))
        settings=target.getvalue()
        with tarfile.open(fileobj=io.BytesIO(settings),mode='r:gz') as check:
            actual={e.name:e for e in check}
            for name,wanted in records.items():
                e=actual[name];data=check.extractfile(e).read() if e.isfile() else None
                assert wanted==(e.mode,e.type,e.linkname,sha(data) if data is not None else None),name
            for name,data in additions.items():assert check.extractfile(name).read()==data,name
            if crc:
                for name,meta in payload['personal_arcade_cores']['cores'].items():
                    data=check.extractfile('system/custom-cores/'+name).read();assert sha(data)==meta['sha256']
                payload['personal_arcade_cores']['variant']='v1.0.3-crc-ko'
        payload['payloads']['settings.tar.gz']=sha(settings)
        payload['public_version']='v1.0.3'
        payload['defaults']['telemetry_enabled']=False
        payload['runtime_updates']={'rumble_carrier_hz':25000,'strong_boost':32768,'brightness_hotkey':'SELECT + volume +/-','brightness_osd':'short-lived free DRM plane'}
        changed['STABLE_V119/settings.tar.gz']=settings
        changed['STABLE_V119/payload.json']=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode()
        changed['knulli-boot.conf']=setting(fat.read_file('/knulli-boot.conf').decode(),'system.telemetry','0').encode()
        for path in ('ACTIONPI_FIXES/flycastvl-maps.txt','ACTIONPI_FIXES/flycast-xtreme-maps.txt'):
            try:fat.locate('/'+path);removed.append(path)
            except FileNotFoundError:pass
        allowed=ranges(fat,list(changed)+removed)
        stable_hashes={p:sha(fat.read_file(p)) for p in (
            '/partitions/BOOT.IMG','/partitions/ENV.IMG','/STABLE_V119/firstboot.py',
            '/MALI_MENU_TRIAL/mali_session.py','/PPSSPP_VULKAN/mali_autostart.py',
            '/ACTIONPI_FIXES/actionpi_app_launcher.py','/ACTIONPI_FIXES/retroarch_gles3_context.so')}
    for path,data in changed.items():
        p=stage/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    print('COPY_AND_SOURCE_HASH',edition,flush=True)
    h=hashlib.sha256()
    with source.open('rb') as src,partial.open('xb') as dst:
        while data:=src.read(16*1024*1024):h.update(data);dst.write(data)
        dst.flush();os.fsync(dst.fileno())
    assert h.hexdigest()==expected,'Source image mismatch'
    for path in changed:mcopy(partial,stage/path,path)
    with partial.open('r+b') as stream:
        fat=u.Fat32Editor(stream,u.BOOT_RESOURCE_OFFSET)
        for path in removed:
            entry=fat.locate('/'+path)
            for c in fat.chain(entry[2]):stream.seek(fat.cluster_offset(c));stream.write(bytes(fat.cluster_size))
            fat.remove_file('/'+path)
        for path,data in changed.items():assert fat.read_file('/'+path)==data,path
        assert stable_hashes=={p:sha(fat.read_file(p)) for p in stable_hashes}
        allowed+=ranges(fat,list(changed)+removed)
    merged=[]
    for start,end in sorted(allowed):
        if merged and start<=merged[-1][1]:merged[-1][1]=max(end,merged[-1][1])
        else:merged.append([start,end])
    h=hashlib.sha256();cursor=compared=0
    print('VERIFY_UNCHANGED_REGIONS_AND_HASH',edition,flush=True)
    with source.open('rb') as a,partial.open('rb') as b:
        for start,end in merged+[[source.stat().st_size,source.stat().st_size]]:
            while cursor<start:
                n=min(16*1024*1024,start-cursor);old=a.read(n);data=b.read(n)
                assert len(data)==n and old==data,'Unexpected byte change at '+str(cursor)
                h.update(data);cursor+=n;compared+=n
            a.seek(end)
            while cursor<end:
                n=min(16*1024*1024,end-cursor);data=b.read(n);assert len(data)==n
                h.update(data);cursor+=n
    assert protected()==previous,'Original images changed'
    partial.rename(final)
    report={'version':'v1.0.3','edition':edition,'image':final.name,'bytes':final.stat().st_size,'sha256':h.hexdigest(),
            'source_image':source.name,'source_sha256':expected,'changed_files':{p:sha(d) for p,d in changed.items()},
            'added_or_updated_userdata':{p:sha(d) for p,d in additions.items()},'removed_old_diagnostics':removed,
            'checks':{'unmodified_tar_members_preserved':True,'crc_cores_unchanged':crc,'runtime_files_readback':True,
                      'boot_mali_wifi_rotation_chain_unchanged':True,'unchanged_bytes_compared':compared,'original_images_unchanged':True},
            'defaults':payload['defaults'],'hardware_validation':'Live runtime fixes tested; this newly packaged installation image has not been freshly flashed.',
            'cpu_affinity_changed':False}
    final.with_suffix('.manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    final.with_suffix('.sha256').write_text(report['sha256']+'  '+final.name+'\n',encoding='utf8')
    (stage/'IMAGE_BUILD_RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'built':final.name,'sha256':report['sha256']}),flush=True)

if __name__=='__main__':
    build(False);build(True)
