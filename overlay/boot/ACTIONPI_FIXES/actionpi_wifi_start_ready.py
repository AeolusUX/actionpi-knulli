"""Deferred ConnMan startup: fresh SHARE settings, no automatic radio reset."""
from pathlib import Path
import fcntl, hashlib, json, os, re, subprocess, sys, time, uuid

STATE = Path('/run/actionpi-wifi-start')
CONF = Path('/userdata/system/knulli.conf')
SCRIPT = '/etc/init.d/S08connman'
LOG = Path('/tmp/actionpi-wifi-start.log')


class Finish(Exception):
    def __init__(self, status, reason):
        self.status, self.reason = status, reason


class Host:
    def __init__(self, token):
        self.token = token

    def command(self, *args, quiet=False):
        self.check()
        try:
            p = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL if quiet else subprocess.PIPE,
                               stderr=subprocess.DEVNULL, timeout=6, text=True)
            self.check()
            return p.returncode, p.stdout or ''
        except (OSError, subprocess.TimeoutExpired):
            self.check()
            return 124, ''

    def check(self):
        if (STATE / 'token').read_text() != self.token:
            raise Finish('cancelled', 'SUPERSEDED_OR_STOPPED')
        if Path('/run/actionpi-wifi-power-unsafe').exists():
            raise Finish('blocked', 'POWER_RESTORATION_UNCONFIRMED')

    def storage(self):
        mounts = [line.split() for line in Path('/proc/mounts').read_text().splitlines()]
        real = any(len(x) >= 3 and x[1] == '/userdata' and x[2] not in ('tmpfs', 'ramfs', 'rootfs') for x in mounts)
        installed = Path('/boot/STABLE_V119')
        return (real and Path('/var/run/knulli.share.mounted').exists() and CONF.is_file()
                and Path('/userdata/system/data.version').is_file()
                and (not (installed / 'firstboot.py').exists() or (installed / 'install-complete.json').exists()))

    def snapshot(self):
        before = CONF.read_bytes()
        rc, enabled = self.command('/usr/bin/knulli-settings-get', '-f', str(CONF), 'wifi.enabled')
        rc2, country = self.command('/usr/bin/knulli-settings-get', '-f', str(CONF), 'wifi.country')
        if rc or rc2 not in (0, 1) or (rc2 and country.strip()) or enabled.strip() not in ('0', '1'):
            raise Finish('failure', 'SETTINGS_READ_FAILED')
        if CONF.read_bytes() != before:
            return None
        return {'digest': hashlib.sha256(before).hexdigest(), 'enabled': enabled.strip() == '1', 'country': country.strip()}

    def interfaces(self):
        return [p for p in Path('/sys/class/net').glob('*') if (p / 'wireless').is_dir()]

    def radio(self):
        return any((p / 'device/driver').is_symlink() and (p / 'device/driver').exists() for p in self.interfaces())

    def daemon(self):
        rc, text = self.command('connmanctl', 'state')
        if rc == 0 and re.search(r'^\s*State\s*=', text, re.M):
            return 'ready'
        try:
            pid = int(Path('/var/run/connmand.pid').read_text().strip())
            if Path('/proc/' + str(pid) + '/comm').read_text().strip() == 'connmand':
                return 'starting'
        except (OSError, ValueError):
            pass
        # Also protect a daemon which has not written its PID file yet.
        for p in Path('/proc').glob('[0-9]*/comm'):
            try:
                if p.read_text().strip() == 'connmand':
                    return 'starting'
            except OSError:
                pass
        return 'absent'

    def technology(self):
        rc, text = self.command('connmanctl', 'technologies')
        if rc:
            return 'unknown'
        # ConnMan prints each technology as an object block.
        for block in re.split(r'(?m)^\s*/net/connman/technology/', text):
            if re.search(r'Type\s*=\s*wifi\b', block):
                power = re.search(r'Powered\s*=\s*(True|False)\b', block)
                return 'on' if power and power[1] == 'True' else 'off' if power else 'unknown'
        return 'missing'

    def connected(self):
        for p in self.interfaces():
            try:
                if (p / 'operstate').read_text().strip() == 'up':
                    return True
                if (p / 'carrier').read_text().strip() == '1':
                    return True
            except OSError:
                pass
        rc, text = self.command('connmanctl', 'services')
        return rc == 0 and any(re.match(r'^\*A\S', line) and 'wifi_' in line for line in text.splitlines())

    def busy(self):
        for p in self.interfaces():
            try:
                if int((p / 'flags').read_text().strip(), 16) & 1:
                    return 'WIRELESS_INTERFACE_UP'
            except (OSError, ValueError):
                return 'WIRELESS_STATE_UNREADABLE'
        if self.connected():
            return 'WIFI_CONNECTING_OR_CONNECTED'
        tech = self.technology()
        if tech == 'on':
            return 'WIFI_ALREADY_POWERED'
        if tech == 'unknown' and self.daemon() != 'absent':
            return 'CONNMAN_STATE_UNAVAILABLE'
        return None

    def prepare(self):
        return self.command(SCRIPT, 'actionpi-ready-config', quiet=True)[0] == 0

    def start_daemon(self):
        return self.command('start-stop-daemon', '-S', '-q', '-m', '-b', '-p', '/var/run/connmand.pid',
                            '--exec', '/usr/sbin/connmand', '--', '-n', '-r', quiet=True)[0] == 0

    def country(self, value):
        return self.command('/usr/sbin/iw', 'reg', 'set', value, quiet=True)[0] == 0

    def enable(self):
        return self.command('connmanctl', 'enable', 'wifi', quiet=True)[0] == 0

    def scan(self):
        return self.command('connmanctl', 'scan', 'wifi', quiet=True)[0] == 0

    def pause(self):
        time.sleep(.5)

    def now(self):
        return time.monotonic()

    def mark(self, status, reason):
        payload = {'status': status, 'reason': reason, 'uptime_seconds': round(time.monotonic(), 3)}
        temp = STATE / ('status.' + str(os.getpid()) + '.tmp')
        temp.write_text(json.dumps(payload) + '\n')
        temp.replace(STATE / 'status.json')


def run(host):
    def polls(count):
        deadline = host.now() + .5 * count
        for i in range(count):
            if i and host.now() >= deadline:
                break
            yield i

    def guard():
        host.check()
        reason = host.busy()
        if reason:
            raise Finish('preserved', reason)

    def current(expected=None):
        host.check()
        if not host.storage():
            raise Finish('cancelled', 'STORAGE_NO_LONGER_READY')
        snap = host.snapshot()
        if snap is None or expected is not None and snap != expected:
            raise Finish('cancelled', 'SETTINGS_CHANGED')
        return snap

    try:
        host.mark('waiting', 'STORAGE_AND_SETTINGS')
        for _ in polls(90):
            host.check()
            guard()
            if host.storage():
                snap = host.snapshot()
                if snap is not None:
                    break
            host.pause()
        else:
            raise Finish('failure', 'STORAGE_NOT_READY')

        host.mark('waiting', 'DRIVER_BOUND_INTERFACE')
        for _ in polls(90):
            guard()
            snap = current()
            if not snap['enabled'] or host.radio():
                break
            host.pause()
        else:
            raise Finish('failure', 'RADIO_NOT_READY')

        # Never restart, reconfigure or take over a pre-existing network manager.
        guard()
        if host.daemon() != 'absent':
            raise Finish('preserved', 'EXISTING_CONNMAN_NOT_RESTARTED')
        for _ in range(3):
            guard()
            snap = current()
            if snap['enabled'] and not host.radio():
                raise Finish('failure', 'RADIO_DISAPPEARED')
            host.mark('attempt', 'PREPARING_LATEST_USERDATA_SETTINGS')
            if not host.prepare():
                raise Finish('failure', 'CONFIG_PREPARATION_FAILED')
            # Original configuration may populate default ad-hoc values itself.
            latest = current()
            if latest == snap:
                break
        else:
            raise Finish('failure', 'SETTINGS_NOT_STABLE')
        guard()
        current(snap)
        if host.daemon() != 'absent':
            raise Finish('preserved', 'CONNMAN_APPEARED_DURING_PREPARATION')
        if not host.start_daemon():
            raise Finish('failure', 'CONNMAN_START_FAILED')
        host.mark('waiting', 'CONNMAN_RESPONSE')
        for _ in polls(16):
            current(snap)
            if host.daemon() == 'ready':
                break
            host.pause()
        else:
            raise Finish('failure', 'CONNMAN_NOT_READY')
        if not snap['enabled']:
            raise Finish('disabled', 'WIFI_OFF_NO_ENABLE_REQUESTED')

        host.mark('waiting', 'CONNMAN_WIFI_TECHNOLOGY')
        for _ in polls(30):
            guard()
            current(snap)
            if not host.radio():
                raise Finish('failure', 'RADIO_DISAPPEARED')
            if host.technology() == 'off':
                break
            host.pause()
        else:
            raise Finish('failure', 'WIFI_TECHNOLOGY_NOT_READY')
        guard()
        current(snap)
        if snap['country'] and not host.country(snap['country']):
            raise Finish('failure', 'COUNTRY_REQUEST_FAILED')
        guard()
        current(snap)
        host.mark('attempt', 'ENABLING_WIFI_ONCE')
        if not host.enable():
            raise Finish('failure', 'WIFI_ENABLE_FAILED')
        for _ in polls(10):
            current(snap)
            if host.technology() == 'on':
                break
            host.pause()
        else:
            raise Finish('failure', 'WIFI_POWERED_NOT_CONFIRMED')
        current(snap)
        if host.connected():
            raise Finish('success', 'ENABLED_CONNECTION_IN_PROGRESS_NO_SCAN_FORCED')
        if not host.scan():
            raise Finish('failure', 'SCAN_REQUEST_FAILED')
        raise Finish('success', 'ENABLED_AND_SCAN_REQUEST_ACCEPTED')
    except Finish as result:
        host.mark(result.status, result.reason)
        return result.status, result.reason
    except (OSError, ValueError):
        host.mark('failure', 'STATE_READ_OR_WRITE_FAILED')
        return 'failure', 'STATE_READ_OR_WRITE_FAILED'


def write_token(token):
    temp = STATE / ('token.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(token)
    temp.replace(STATE / 'token')


def main(action, token=None):
    STATE.mkdir(exist_ok=True)
    if action == 'start' and token is None:
        action = 'request'
    if action in ('request', 'cancel'):
        # Assign identity before spawning, so even a not-yet-running worker can
        # be cancelled. A worker must never resurrect itself with a new token.
        with (STATE / 'request.lock').open('a') as request_lock:
            fcntl.flock(request_lock, fcntl.LOCK_EX)
            if action == 'request':
                with (STATE / 'lock').open('a') as owner:
                    try:
                        fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        return 0  # Preserve the existing worker and its identity.
                    token = uuid.uuid4().hex
                    write_token(token)
                    with LOG.open('a') as log:
                        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'start', token],
                                         stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                         close_fds=True, start_new_session=True)
                    return 0
            write_token(uuid.uuid4().hex)
    with (STATE / 'lock').open('a') as lock:
        for _ in range(120):
            if action == 'start' and (STATE / 'token').read_text() != token:
                return 0
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                time.sleep(.1)
        else:
            return 1  # Caller must not stop a daemon while startup is in flight.
        if action == 'cancel':
            return 0
        if (STATE / 'token').read_text() != token:
            return 0
        status, reason = run(Host(token))
        print(status + ':' + reason, flush=True)
        return 1 if status == 'failure' else 0


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3) or sys.argv[1] not in ('request', 'start', 'cancel'):
        raise SystemExit(2)
    if len(sys.argv) == 3 and sys.argv[1] != 'start':
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None))
