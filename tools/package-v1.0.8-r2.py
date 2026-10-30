"""Merge the hardware-confirmed Saturn input fixes into v1.0.8, revision r2."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil
R=Path(__file__).resolve().parents[1];O=Path(os.environ.get('ACTIONPI_IMAGE_DIR',R/'images'));P=O/'public-v1.0.8-r2-prep';G=O/'github-public/actionpi-knulli'
spec=importlib.util.spec_from_file_location('base108',R/'tools/package-v1.0.8.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
sha=lambda b:hashlib.sha256(b).hexdigest()
binary=Path(os.environ.get('ACTIONPI_SATURN_BINARY',R/'saturn-payload/boot/ACTIONPI_FIXES/saturn/yabasanshiro')).read_bytes();assert sha(binary)=='f6119fd510066b14781c32849b858056c62f31f87827170b6a0113560e55c6eb'
P.mkdir(exist_ok=True)
for edition,suffix in [('standard',''),('crc-ko','-crc-ko')]:
    source=O/('action-pi-knulli-v1.0.8'+suffix+'.img');target=O/('action-pi-knulli-v1.0.8'+suffix+'-r2.img');partial=target.with_suffix('.img.partial');stage=P/edition;stage.mkdir(exist_ok=True)
    assert not target.exists() and not partial.exists()
    old=json.loads(source.with_suffix('.manifest.json').read_bytes());before={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in O.glob('action-pi-knulli-v1.0.8*.img*')}
    with source.open('rb') as f:
        fat=base.fatmod.Fat32Editor(f,base.fatmod.BOOT_RESOURCE_OFFSET)
        payload=json.loads(fat.read_file('/STABLE_V119/payload.json'))
        assert sha(fat.read_file('/ACTIONPI_FIXES/saturn/yabasanshiro'))=='a6d3f63be8892f3aaaec21d497079d3c3d2534d6cd5a0cf41166ba3ebc36bf1f'
        payload.update(image_revision='r2');payload['runtime_updates'].update(saturn_pad_mode_respected=True,saturn_digital_stick_merge=True)
        changed={'ACTIONPI_FIXES/saturn/yabasanshiro':binary,'STABLE_V119/payload.json':(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode()}
        allowed=base.ranges(fat,list(changed))
        protected={n:sha(fat.read_file(n)) for n in ('/STABLE_V119/settings.tar.gz','/STABLE_V119/firstboot.py','/partitions/BOOT.IMG','/partitions/ENV.IMG','/ACTIONPI_FIXES/actionpi_app_launcher.py','/ACTIONPI_FIXES/saturn/run.py')}
    print('COPY_AND_PATCH',edition,flush=True);h=hashlib.sha256()
    with source.open('rb') as a,partial.open('xb') as b:
        while data:=a.read(16*1024*1024):h.update(data);b.write(data)
        b.flush();os.fsync(b.fileno())
    assert h.hexdigest()==old['sha256']
    with partial.open('r+b') as f:
        fat=base.fatmod.Fat32Editor(f,base.fatmod.BOOT_RESOURCE_OFFSET)
        for n,data in changed.items():fat.replace_file('/'+n,data)
        for n,data in changed.items():assert fat.read_file('/'+n)==data
        assert protected=={n:sha(fat.read_file(n)) for n in protected}
    merged=[]
    for a,b in sorted(allowed):
        if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
        else:merged.append([a,b])
    h=hashlib.sha256();cursor=compared=0
    with source.open('rb') as a,partial.open('rb') as b:
        for start,end in merged+[[source.stat().st_size,source.stat().st_size]]:
            while cursor<start:
                n=min(16*1024*1024,start-cursor);data=b.read(n);assert len(data)==n and a.read(n)==data,'Unexpected edit '+str(cursor);h.update(data);cursor+=n;compared+=n
            a.seek(end)
            while cursor<end:
                n=min(16*1024*1024,end-cursor);data=b.read(n);assert len(data)==n;h.update(data);cursor+=n
    assert all((O/n).stat().st_size==meta[0] and (O/n).stat().st_mtime_ns==meta[1] for n,meta in before.items())
    partial.rename(target)
    report=dict(old,version='v1.0.8',image_revision='r2',image=target.name,sha256=h.hexdigest(),source_image=source.name,source_sha256=old['sha256'],changed_files={n:sha(data) for n,data in changed.items()})
    report['checks']=dict(old['checks'],unchanged_bytes_compared=compared,old_images_unchanged=True,digital_pad_protocol_preserved=True,stick_dpad_merge_host_test_passed=True)
    report['hardware_validation']='User confirmed START in Dynamite Deka 1 and Slayers after the digital-pad selector fix, then confirmed normal operation with merged analog-stick/D-pad input. Existing GLES/L3/FPS/audio fixes retained. Final r2 images have not been freshly flashed.'
    target.with_suffix('.manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');target.with_suffix('.sha256').write_text(report['sha256']+'  '+target.name+'\n')
    (stage/'IMAGE_BUILD_RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('BUILT',target.name,report['sha256'],flush=True)
