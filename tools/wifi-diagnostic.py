"""Read-only test7 Wi-Fi evidence; no raw network identifiers are exported."""
from pathlib import Path
import collections, datetime, hashlib, json, os, re, subprocess, sys, time, zipfile

CONFIGS = ('/userdata/system/knulli.conf', '/boot/knulli-boot.conf')
COMMANDS = {('connmanctl', 'state'), ('connmanctl', 'technologies'), ('connmanctl', 'services'),
            ('dmesg',), ('iw', 'reg', 'get')}
COMMANDS |= {('/usr/bin/knulli-settings-get', '-f', p, key)
             for p in CONFIGS for key in ('wifi.enabled', 'wifi.country')}


def command(args):
    args = tuple(args)
    if args not in COMMANDS:
        raise ValueError('Command is not a read-only diagnostic query')
    try:
        p = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, text=True, errors='replace', timeout=7)
        return {'rc': p.returncode, 'text': p.stdout[-2_000_000:]}
    except subprocess.TimeoutExpired:
        return {'rc': 124, 'text': ''}
    except OSError:
        return {'rc': 127, 'text': ''}


def safe_word(value):
    value = (value or '').strip()
    return value if re.fullmatch(r'[A-Za-z0-9_.+-]{1,80}', value) and not re.search(r'[0-9a-fA-F]{12,}', value) else '[omitted]'


def uptime_value(text):
    match = re.match(r'^\s*(\d+(?:\.\d+)?)\b', text or '')
    return match[1] if match else None


class Reader:
    def __init__(self, root):
        self.root = root
        self.errors = collections.Counter()

    def p(self, path):
        return self.root / path.lstrip('/')

    def read(self, path, limit=1_000_000):
        try:
            with self.p(path).open('rb') as stream:
                return stream.read(limit).decode('utf-8', errors='replace')
        except OSError as e:
            self.errors[type(e).__name__] += 1
            return None

    def number(self, path):
        value = self.read(path, 80)
        if value is not None and re.fullmatch(r'-?(?:0x[0-9a-fA-F]+|\d+)\s*', value):
            return value.strip()
        return None

    def exists(self, path):
        return self.p(path).exists()

    def link_name(self, path):
        p = self.p(path)
        try:
            return safe_word(p.resolve().name) if p.is_symlink() else None
        except OSError:
            return None


def public_status(text):
    try:
        data = json.loads(text or '')
    except (ValueError, TypeError):
        return {'readable_json': False}
    if not isinstance(data, dict):
        return {'readable_json': False}
    result = {}
    numbers = {'checks', 'initial_state', 'final_state', 'uptime_seconds', 'power_started',
               'restored', 'cycle_completed', 'wifi_start_blocked', 'restore_confirmed'}
    for key, value in data.items():
        if key in numbers and isinstance(value, (int, float, bool)):
            result[key] = value
        elif key in ('status', 'reason') and isinstance(value, str):
            result[key] = value if re.fullmatch(r'[A-Za-z0-9_:+ .-]{1,180}', value) else '[nonstandard text omitted]'
        elif key == 'boot_id' and isinstance(value, str) and re.fullmatch(r'[0-9a-f-]{36}', value):
            result[key] = value
    return result


def log_summary(text):
    """Only known status/return-code records, never raw traceback or network text."""
    result = {'records': [], 'exception_types': [], 'line_count': len((text or '').splitlines())}
    for line in (text or '').splitlines():
        line = line.strip()
        if re.fullmatch(r'(?:AIC_MODPROBE_RC|RTL8723DS_INSMOD_RC|RADIO_READY_AFTER_HALF_SECONDS)=-?\d+', line):
            result['records'].append(line)
        elif re.fullmatch(r'(?:waiting|attempt|preserved|cancelled|disabled|success|failure|blocked):[A-Z0-9_]+', line):
            result['records'].append(line)
        elif line in {'ACTIONPI-DUAL-WIFI-TEST-1', 'RTL8723DS_DISABLED_BY_USER', 'RTL8723DS_ALREADY_LOADED',
                      'DUAL_WIFI_WORKER_COMPLETE', 'WAITING_FOR_RADIO', 'CANCELLED_WIFI_OFF',
                      'RADIO_NOT_READY_WITHIN_45_SECONDS'}:
            result['records'].append(line)
        elif re.match(r'^(?:ALREADY_TERMINAL_THIS_BOOT|SUCCESS|FAILURE|BLOCKED|DISABLED):[A-Za-z0-9_:]+$', line):
            result['records'].append(line)
        match = re.match(r'^(\w+(?:Error|Exception)):', line)
        if match:
            result['exception_types'].append(safe_word(match[1]))
    result['records'] = result['records'][-150:]
    return result


def kernel_summary(text):
    """Export times, known subsystem symbols/tags and numeric errors, not lines."""
    result = {'events': [], 'sensitive_lines_omitted': 0, 'matching_lines': 0}
    private = re.compile(r'ssid|bssid|essid|password|passphrase|\bpsk\b|\bpmk\b|credential|\bkey\b', re.I)
    subsystem = re.compile(r'\b(?:aic\w*|rtw_\w*|rtl\w*|8723ds|mmc\w*|sdio\w*|sunxi\w*|cfg80211\w*|rfkill)\b', re.I)
    tags = re.compile(r'\b(?:fail(?:ed|ure)?|error|err|timeout|timed|firmware|download|power|reset|probe|attach|bind|card|voltage|crc|scan|ready|success|unsupported|missing|retry|regulatory)\b', re.I)
    for line in (text or '').splitlines():
        if not subsystem.search(line):
            continue
        result['matching_lines'] += 1
        if private.search(line):
            result['sensitive_lines_omitted'] += 1
            continue
        stamp = re.search(r'^\s*\[\s*(\d+(?:\.\d+)?)\]', line)
        symbols = sorted({safe_word(s) for s in subsystem.findall(line)})
        event = {'uptime': stamp[1] if stamp else None, 'symbols': symbols[:16],
                 'tags': sorted({s.lower() for s in tags.findall(line)}),
                 'numeric_errors': re.findall(r'\b(?:err(?:or|no|code)?|ret|rc|status)\s*[:=]?\s*(-?\d+)\b', line, re.I)[:12]}
        if event['symbols'] or event['tags']:
            result['events'].append(event)
    result['events_total'] = len(result['events'])
    result['events'] = result['events'][:150] + result['events'][150:][-650:]
    return result


def collect(root=Path('/'), execute=command):
    r = Reader(root)
    report = {'format': 'ActionPi-WiFi-test7-diagnostic-v1',
              'collection': 'passive; no enable/disable/scan/reset/service changes',
              'privacy': 'No raw config, service names, MAC/IP, SSID/password, full dmesg or command line exported',
              'captured_local_time': datetime.datetime.now().isoformat(timespec='seconds')}
    before = r.read('/proc/uptime', 100)
    boot_id = r.read('/proc/sys/kernel/random/boot_id', 100)
    report['system'] = {'kernel': safe_word(r.read('/proc/sys/kernel/osrelease', 100)),
                        'board': safe_word(r.read('/boot/boot/knulli.board', 100)),
                        'boot_id': boot_id.strip() if boot_id and re.fullmatch(r'[0-9a-f-]{36}\s*', boot_id) else None,
                        'uptime_at_start': uptime_value(before)}
    mounts = []
    for line in (r.read('/proc/mounts') or '').splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[1] in ('/userdata', '/boot'):
            mounts.append({'target': fields[1], 'filesystem': safe_word(fields[2]),
                           'read_only': 'ro' in fields[3].split(','),
                           'persistent_userdata': fields[1] == '/userdata' and fields[2] not in ('tmpfs', 'ramfs', 'rootfs')})
    marker_paths = ['/run/knulli.share.mounted', '/var/run/knulli.share.mounted',
                    '/userdata/system/data.version', '/boot/STABLE_V119/firstboot.py',
                    '/boot/STABLE_V119/install-complete.json', '/run/actionpi-wifi-power-unsafe',
                    '/run/actionpi-wifi-power-once', '/boot/DISABLE_WIFI_POWER_INIT.txt', '/boot/DISABLE_RTL8723DS.txt',
                    '/etc/modprobe.d/98-actionpi-power-test5.conf']
    report['storage'] = {'mounts': mounts, 'markers': {p: r.exists(p) for p in marker_paths}}
    report['settings'] = {}
    for path in CONFIGS:
        text = r.read(path)
        fields = dict(re.findall(r'^\s*(wifi[\w.]+)\s*=(.*)$', text or '', re.M))
        summary = {'exists': r.exists(path), 'readable': text is not None,
                   'saved_ssid_present': any(k.endswith('.ssid') and v.strip() for k, v in fields.items()),
                   'saved_password_present': any(k.endswith('.key') and v.strip() for k, v in fields.items())}
        for key in ('wifi.enabled', 'wifi.country'):
            value = execute(('/usr/bin/knulli-settings-get', '-f', path, key))
            s = value['text'].strip()
            valid = s in ('0', '1') if key.endswith('enabled') else not s or bool(re.fullmatch('[A-Za-z0-9]{2}', s))
            summary[key] = {'rc': value['rc'], 'value': s if valid else '[unexpected value omitted]'}
        report['settings'][path] = summary
    state = execute(('connmanctl', 'state'))
    technologies = execute(('connmanctl', 'technologies'))
    services = execute(('connmanctl', 'services'))
    conn = {'state_rc': state['rc'], 'state': {}, 'technologies_rc': technologies['rc'], 'technologies': [],
            'services_rc': services['rc'], 'wifi_services': 0, 'wifi_service_states': dict()}
    for key, val in re.findall(r'^\s*(State|OfflineMode|SessionMode)\s*=\s*([A-Za-z]+)\s*$', state['text'], re.M):
        conn['state'][key] = safe_word(val)
    for block in re.split(r'(?m)^\s*/net/connman/technology/', technologies['text']):
        kind = re.search(r'\bType\s*=\s*(wifi|ethernet|bluetooth)\b', block)
        if kind:
            obj = {'type': kind[1]}
            for key, val in re.findall(r'\b(Powered|Connected|Tethering)\s*=\s*(True|False)\b', block):
                obj[key] = val == 'True'
            conn['technologies'].append(obj)
    counts = collections.Counter()
    for line in services['text'].splitlines():
        if re.search(r'\bwifi_[A-Za-z0-9_]+\s*$', line):
            conn['wifi_services'] += 1
            counts['online' if line[:3].endswith('O') else 'ready' if line[:3].endswith('R') else 'other'] += 1
    conn['wifi_service_states'] = dict(counts)
    conn['provisioning_files'] = {name: r.exists('/var/lib/connman/' + name) for name in
                                 ('knulli_wifi.config', 'knulli_wifi2.config', 'knulli_wifi3.config',
                                  'knulli_wifi.hidden.config', 'knulli_wifi.adhoc.config')}
    report['connman'] = conn
    report['sdio'] = []
    for n, p in enumerate(sorted(r.p('/sys/bus/sdio/devices').glob('*'))):
        base = '/sys/bus/sdio/devices/' + p.name
        item = {'slot': p.name if re.fullmatch(r'mmc\d+:[0-9a-fA-F]{4}:\d+', p.name) else 'sdio_' + str(n),
                'vendor': r.number(base + '/vendor'), 'device': r.number(base + '/device'),
                'class': r.number(base + '/class'), 'driver': r.link_name(base + '/driver')}
        for key in ('runtime_status', 'control'):
            raw = r.read(base + '/power/' + key, 80)
            item['power_' + key] = safe_word(raw) if raw is not None else None
        report['sdio'].append(item)
    report['wireless_interfaces'] = []
    for p in sorted(r.p('/sys/class/net').glob('*')):
        if not (p / 'wireless').is_dir():
            continue
        base = '/sys/class/net/' + p.name
        flags = r.number(base + '/flags')
        item = {'interface': 'wireless_' + str(len(report['wireless_interfaces'])),
                'driver': r.link_name(base + '/device/driver'), 'flags': flags,
                'up': bool(int(flags, 16) & 1) if flags else None,
                'operstate': safe_word(r.read(base + '/operstate', 80)), 'carrier': r.number(base + '/carrier')}
        report['wireless_interfaces'].append(item)
    power_paths = ['/sys/class/misc/sunxi-wlan/rf-ctrl/power_state',
                   '/sys/class/misc/sunxi-rfkill/wlan/state', '/sys/class/misc/sunxi-rfkill/bluetooth/state']
    report['power'] = {p: {'exists': r.exists(p), 'value': r.number(p)} for p in power_paths}
    report['rescan_interface_exists'] = {p: r.exists(p) for p in
        ('/sys/class/misc/sunxi-wlan/rf-ctrl/scan_device', '/sys/class/misc/sunxi-rfkill/wlan/scan')}
    report['rfkill'] = []
    for p in sorted(r.p('/sys/class/rfkill').glob('rfkill*')):
        base = '/sys/class/rfkill/' + p.name
        report['rfkill'].append({'type': safe_word(r.read(base + '/type', 80)),
                                 'soft': r.number(base + '/soft'), 'hard': r.number(base + '/hard')})
    modules = []
    for line in (r.read('/proc/modules') or '').splitlines():
        fields = line.split()
        if len(fields) >= 3 and re.match(r'^(aic|8723|rtl|rtw|mmc|sdio|sunxi|hci|btusb)', fields[0]):
            modules.append({'name': safe_word(fields[0]), 'bytes': fields[1] if fields[1].isdigit() else None,
                            'references': fields[2] if fields[2].isdigit() else None})
    report['modules'] = modules
    report['processes'] = []
    known = ('actionpi_wifi_start_ready.py', 'actionpi_wifi_power_init.py', 'S08connman')
    for p in r.p('/proc').glob('[0-9]*'):
        name = r.read('/proc/' + p.name + '/comm', 100)
        if not name:
            continue
        script = None
        if name.strip() in ('python3', 'sh', 'bash'):
            args = r.read('/proc/' + p.name + '/cmdline', 8192) or ''
            script = next((s for s in known if any(a.rsplit('/', 1)[-1] == s for a in args.split('\x00'))), None)
        if name.strip() in ('connmand', 'dbus-daemon') or script:
            report['processes'].append({'pid': int(p.name), 'comm': safe_word(name), 'known_script': script,
                                        'wchan': safe_word(r.read('/proc/' + p.name + '/wchan', 100))})
    report['helper_status'] = {}
    for group in ('actionpi-wifi-start', 'actionpi-wifi-power'):
        for name in ('status', 'waiting', 'attempt', 'success', 'failure', 'blocked', 'disabled'):
            path = '/run/' + group + '/' + name + '.json'
            if r.exists(path):
                report['helper_status'][path] = public_status(r.read(path, 10000))
    report['logs'] = {}
    for path in ('/tmp/actionpi-wifi-start.log', '/tmp/actionpi-dual-wifi.log', '/tmp/actionpi-wifi-ready.log',
                 '/boot/boot/wifi-power-init.log', '/boot/boot/dual-wifi.log', '/boot/boot/wifi-ready.log'):
        if r.exists(path):
            item = log_summary(r.read(path))
            item['current_boot_guaranteed'] = path.startswith('/tmp/')
            report['logs'][path] = item
    report['file_sha256'] = {}
    for path in ('/etc/init.d/S08connman', '/etc/init.d/S06modprobe',
                 '/boot/ACTIONPI_FIXES/actionpi_wifi_start_ready.py', '/boot/ACTIONPI_FIXES/actionpi_wifi_power_init.py'):
        try:
            data = r.p(path).read_bytes()
            report['file_sha256'][path] = hashlib.sha256(data).hexdigest() if len(data) < 500000 else '[too large]'
        except OSError:
            report['file_sha256'][path] = None
    regulatory = execute(('iw', 'reg', 'get'))
    report['regulatory'] = {'rc': regulatory['rc'], 'countries': sorted(set(re.findall(r'\bcountry ([A-Z0-9]{2}):', regulatory['text'])))}
    kernel = execute(('dmesg',))
    report['kernel'] = kernel_summary(kernel['text'])
    report['kernel']['read_rc'] = kernel['rc']
    report['read_errors_by_type'] = dict(r.errors)
    after = r.read('/proc/uptime', 100)
    report['uptime_at_end'] = uptime_value(after)
    return report


def save(report, parent):
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    base = 'ActionPi-WiFi-test7-Report-' + stamp
    folder = parent / base
    number = 1
    while folder.exists() or folder.with_suffix('.zip').exists():
        folder = parent / (base + '-' + str(number))
        number += 1
    folder.mkdir()
    (folder / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    note = ('Passive test7 Wi-Fi snapshot. No scan/enable/disable/reset or service changes were requested.\n'
            'Kernel events are structured summaries; raw dmesg and network identifiers are not included.\n'
            'All snapshots are read sequentially; state can change during collection.\n'
            'Persistent BOOT logs may be from a previous boot; /run and /tmp describe this boot.\n'
            'A helper success status does not prove association or internet access.\n'
            'Missing/unreadable files or command timeouts are recorded rather than repaired.\n')
    (folder / 'README.txt').write_text(note, encoding='utf-8')
    compression = zipfile.ZIP_DEFLATED if zipfile.zlib is not None else zipfile.ZIP_STORED
    with zipfile.ZipFile(folder.with_suffix('.zip'), 'x', compression=compression) as z:
        for file in sorted(folder.iterdir()):
            z.write(file, folder.name + '/' + file.name)
    if hasattr(os, 'sync'):
        os.sync()
    return folder.with_suffix('.zip')


if __name__ == '__main__':
    target = Path(sys.argv[1]).resolve().parent
    print('Collecting a passive Wi-Fi report. This may take about one minute.', flush=True)
    archive = save(collect(), target)
    print('REPORT_COMPLETE: ' + archive.name, flush=True)
