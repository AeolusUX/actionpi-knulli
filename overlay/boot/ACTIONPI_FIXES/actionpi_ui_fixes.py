"""Install reversible Action Pi userspace patches into RAM on each boot."""
from pathlib import Path
import os

BASE=Path('/boot/ACTIONPI_FIXES')

def install():
    assert Path('/boot/boot/knulli.board').read_text().strip()=='helegany-action-pi'
    # ACTIONPI_OD_SURFACE_BOOT
    from actionpi_od_rotation import install as install_od
    install_od()
    from actionpi_app_launcher import install as install_apps
    install_apps()
    p=Path('/usr/bin/knulli-brightness');text=p.read_text()
    if '# ACTIONPI_INVERTED_BACKLIGHT' in text:
        start=text.index('  # ACTIONPI_INVERTED_BACKLIGHT')
        end=text.index('\nelse\n  XMAX=255',start)
        native='  # ACTIONPI_NATIVE_BACKLIGHT: raw30->raw130 was visibly brighter.\n  bl_get() { read -r v < "$BACKLIGHT_DIR/brightness"; printf \'%s\\n\' "$v"; }\n  bl_set() { printf \'%s\' "$1" > "$BACKLIGHT_DIR/brightness"; }'
        p.write_text(text[:start]+native+text[end:]);p.chmod(0o755)
    p=Path('/usr/bin/knulli-audio');text=p.read_text()
    old="amixer -c 0 sset 'LINEOUT Gain' 23"
    new="amixer -c 0 sset 'LINEOUT Gain' 25 # ACTIONPI_SPEAKER_GAIN +3dB"
    if '# ACTIONPI_SPEAKER_GAIN' not in text:
        assert text.count(old)==1,'Unexpected audio source'
        p.write_text(text.replace(old,new));p.chmod(0o755)
    p=Path('/etc/pm/sleep.d/09-actionpi-wifi')
    p.write_bytes((BASE/'actionpi_wifi_sleep.sh').read_bytes());p.chmod(0o755)
    # Remove the one-boot shell tracing wrapper used to diagnose suspend.
    original=Path('/run/actionpi-original-knulli-suspend')
    if original.exists():
        p=Path('/usr/bin/knulli-suspend');p.write_bytes(original.read_bytes());p.chmod(0o755)
    p=Path('/etc/triggerhappy/triggers.d/multimedia_keys.conf')
    text=p.read_text();line='KEY_HOME 1 /usr/bin/python3 /boot/ACTIONPI_FIXES/home_exit.py\n'
    if line not in text:
        p.write_text(text.rstrip()+'\n'+line)
    os.sync()

if __name__=='__main__':install()
