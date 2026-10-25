"""Fix legacy PortMaster runtime-list data handling without replacing the app."""
from pathlib import Path
import copy,io,os,zipfile
MARK='# ACTIONPI_RUNTIME_LIST_TYPES'
def patched_source(text):
    if MARK in text:return text
    start=text.find('class RuntimesScene(BaseScene):')
    if start<0:return text
    end=text.find('\nclass ',start+1)
    if end<0:end=len(text)
    section=text[start:end]
    old="""        for port_name, port_info in self.gui.hm.list_ports(filters=['installed']).items():
            if port_info['attr']['runtime'] in self.runtimes:
                self.runtimes[port_info['attr']['runtime']]['ports'].append(port_info['attr']['title'])"""
    if section.count(old)!=1:return text
    new="""        # ACTIONPI_RUNTIME_LIST_TYPES
        for port_name, port_info in self.gui.hm.list_ports(filters=['installed']).items():
            attr = port_info.get('attr') or {}
            used = attr.get('runtime') or []
            if isinstance(used, str):
                used = [used]
            if not isinstance(used, (list, tuple)):
                continue
            for runtime_name in used:
                if isinstance(runtime_name, str) and runtime_name in self.runtimes:
                    self.runtimes[runtime_name]['ports'].append(attr.get('title', port_name))"""
    section=section.replace(old,new,1)
    section=section.replace("        runtime_info = self.runtimes[self.last_select]","        if self.last_select not in self.runtimes:\n            self.last_select = 'all'\n        runtime_info = self.runtimes[self.last_select]",1)
    old="        selected = self.tags['runtime_list'].selected_option()"
    section=section.replace(old,old+"\n        if selected not in self.runtimes:\n            selected = 'all'",1)
    result=text[:start]+section+text[end:];compile(result,'pugscene.py','exec');return result


HARBOUR_MARK = '# ACTIONPI_RUNTIME_REQUIREMENTS_LIST'

def patched_harbour(text):
    if HARBOUR_MARK in text:
        return text
    old = """        runtime = port_info.get('attr', {}).get('runtime', None)

        if runtime is not None:
            if not runtime.endswith('.squashfs'):
                runtime += '.squashfs'

            requirements.append('|'.join(self.runtimes_info.get(runtime, {}).get('remote', {}).keys()))
            show = True

        else:"""
    new = """        # ACTIONPI_RUNTIME_REQUIREMENTS_LIST
        runtimes = port_info.get('attr', {}).get('runtime') or []
        if isinstance(runtimes, str):
            runtimes = [runtimes]
        if not isinstance(runtimes, (list, tuple)):
            runtimes = []
        runtimes = [runtime for runtime in runtimes if isinstance(runtime, str) and runtime]

        if runtimes:
            for runtime in runtimes:
                if not runtime.endswith('.squashfs'):
                    runtime += '.squashfs'
                requirements.append('|'.join(self.runtimes_info.get(runtime, {}).get('remote', {}).keys()))
            show = True

        else:"""
    if text.count(old) != 1:
        return text
    result = text.replace(old, new, 1)
    compile(result, 'harbour.py', 'exec')
    return result


def patched_util(text):
    marker = '# ACTIONPI_RUNTIME_DISPLAY_LIST'
    if marker in text: return text
    anchor = 'def runtime_nicename(runtime):\n'
    if text.count(anchor) != 1: return text
    extra = "    # ACTIONPI_RUNTIME_DISPLAY_LIST\n    if isinstance(runtime, (list, tuple)):\n        return ', '.join(runtime_nicename(item) for item in runtime if isinstance(item, str) and item)\n    if not isinstance(runtime, str) or not runtime:\n        return ''\n"
    result = text.replace(anchor, anchor + extra, 1)
    compile(result, 'util.py', 'exec')
    return result


def patched_pugwash(text):
    marker = '# ACTIONPI_PORT_INFO_RUNTIME_LIST'
    if marker in text: return text
    old = '''        runtime = port_info['attr']['runtime']
        if runtime is not None and runtime != "None":
            self.set_data("port_info.runtime", harbourmaster.runtime_nicename(runtime))
            if (self.hm.libs_dir / runtime).is_file():'''
    new = '''        # ACTIONPI_PORT_INFO_RUNTIME_LIST
        runtime = port_info['attr']['runtime']
        runtimes = runtime if isinstance(runtime, (list, tuple)) else [runtime]
        runtimes = [name for name in runtimes if isinstance(name, str) and name and name != "None"]
        if runtimes:
            self.set_data("port_info.runtime", harbourmaster.runtime_nicename(runtimes))
            if all((self.hm.libs_dir / name).is_file() for name in runtimes):'''
    if text.count(old) != 1: return text
    result=text.replace(old,new,1);compile(result,'pugwash','exec');return result

def patched_source_download(text):
    marker = '# ACTIONPI_DOWNLOAD_RUNTIME_LIST'
    if marker in text: return text
    old = '''            if port_info['attr'].get('runtime', None) is not None:
                runtime = port_info['attr']['runtime']

                runtime_file = (self.hm.libs_dir / runtime)
                if not runtime_file.exists():
                    size += self.hm.port_download_size(runtime)'''
    new = '''            # ACTIONPI_DOWNLOAD_RUNTIME_LIST
            runtimes = port_info['attr'].get('runtime') or []
            if isinstance(runtimes, str):
                runtimes = [runtimes]
            if not isinstance(runtimes, (list, tuple)):
                runtimes = []
            for runtime in dict.fromkeys(name for name in runtimes if isinstance(name, str) and name):
                runtime_file = (self.hm.libs_dir / runtime)
                if not runtime_file.exists():
                    size += self.hm.port_download_size(runtime)'''
    if text.count(old) != 2: return text
    result=text.replace(old,new);compile(result,'source.py','exec');return result

def prepare():
    import datetime, hashlib, json
    backup = None
    def save_before(path):
        nonlocal backup
        if backup is None:
            backup = Path('/userdata/system/actionpi-backups') / ('portmaster-runtime-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        target = backup / str(path).lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        return target
    candidates = [Path('/userdata/system/.local/share/PortMaster'), Path('/userdata/roms/ports/PortMaster'), Path('/opt/tools/PortMaster'), Path('/opt/system/Tools/PortMaster')]
    patches = {'pylibs/pugscene.py': patched_source, 'pylibs/harbourmaster/harbour.py': patched_harbour, 'pylibs/harbourmaster/util.py': patched_util, 'pugwash': patched_pugwash, 'pylibs/harbourmaster/source.py': patched_source_download}
    for directory in candidates:
        archive = directory / 'pylibs.zip'
        if archive.is_file():
            with zipfile.ZipFile(archive) as source:
                updates = {}
                for name, patch in patches.items():
                    if name in source.namelist():
                        before = source.read(name)
                        after = patch(before.decode()).encode()
                        if after != before: updates[name] = after
                if updates:
                    save_before(archive)
                    result = io.BytesIO()
                    with zipfile.ZipFile(result, 'w') as target:
                        for info in source.infolist():
                            # Remove only cached modules whose source is being replaced.
                            if any(info.filename == name + 'c' or ('/__pycache__/' in info.filename and Path(info.filename).name.startswith(Path(name).stem + '.')) for name in updates):
                                continue
                            target.writestr(copy.copy(info), updates.get(info.filename, source.read(info.filename)))
                    temp = archive.with_name('pylibs.zip.actionpi-tmp')
                    temp.write_bytes(result.getvalue()); temp.replace(archive)
                    print('ACTIONPI PortMaster archive runtime fixes applied', flush=True)
        for name, patch in patches.items():
            path = directory / name
            if not path.is_file(): continue
            before = path.read_bytes(); after = patch(before.decode()).encode()
            if after == before: continue
            save_before(path)
            temp = path.with_name(path.name + '.actionpi-tmp')
            temp.write_bytes(after); temp.chmod(path.stat().st_mode & 0o777); temp.replace(path)
            print('ACTIONPI PortMaster extracted runtime fix applied: ' + str(path), flush=True)
    os.sync()
    return True
