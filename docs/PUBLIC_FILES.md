# Public file boundaries

[English](PUBLIC_FILES.md) · [한국어](PUBLIC_FILES.ko.md)

Published code is staged using an explicit allowlist from the **public distribution**.
The original private working directory and complete conversation are not uploaded.

## Included

- Curated development history with confirmed outcomes and failed approaches.
- Current startup/session/opacity/rotation/input/power helpers.
- Exact upstream Mali driver source at the pinned commit, with original notices.
- Recovered kernel config and candidate config/options, source cleanup patch,
  guarded assembly repair and verification summary.
- Historical image conversion and PWM tools, identified as historical where they
  require unpublished earlier input images.
- Sanitized public defaults, PortMaster installer entry, release manifest,
  component hashes, final image/checksum and a compressed release asset.
- Build, installation, recovery, test-coverage and source/provenance documentation.

## Excluded

- Personal images, the private BIOS archive and private captures.
- Saved personal Wi-Fi SSIDs/passwords and recovery copies containing them.
- GitHub credentials, browser session material, authentication screenshots,
  known-hosts files and SSH private/host keys.
- Raw user conversations, private network logs, machine IDs, cookies, histories,
  Bluetooth pairing records, game captures, diagnostic memory dumps and game ROMs.
- Compiler installations, Git databases and untracked build artifacts from the
  driver working tree.

The source image's base rootfs and its original BIOS were deliberately retained
unchanged. This is distinct from excluding the additional personal BIOS archive.
The public packaging zeroed 3,289,493,504 free FAT bytes and scrubbed 122 file
tails plus 26 deleted records, so removing a filename was not the only cleanup.

The downloadable IMG belongs in GitHub **Releases**, not the Git source history.
The source tree is small enough to inspect and clone without downloading firmware.

## Added or refreshed for v1.0.1

- overlay/etc/init.d/S06modprobe and S08connman: effective boot startup code.
- overlay/usr/bin/emulatorlauncher: renderer-aware application routing.
- overlay/boot/ACTIONPI_FIXES/: current common app, PortMaster runtime, OD-Commander and Wi-Fi helpers.
- overlay/boot/PPSSPP_VULKAN/: updated active manager/autostart integrity link.
- src/app_sdl_rotation.c, app_gl_rotation.c and od_commander_rotation.c: adapter source; no compiled userspace adapter is needed in Git.
- tools/ActionPi-WiFi-Diagnostic.sh and wifi-diagnostic.py: passive report collector, compatible with this release.
- release/distribution-v1.0.1.manifest.json and current component/source inventories and asset hashes.

Personal CRC-core images, game ROMs, screenshots containing network details and personal stable images are not release assets.

## Added or refreshed for v1.0.2

- src/retroarch_gles3_context.c and its ARM64 command in tools/build-runtime.sh.
- overlay/boot/ACTIONPI_FIXES/actionpi_app_launcher.py and MALI_MENU_TRIAL/mali_menu_trial.py.
- release/distribution-v1.0.2.manifest.json, FIELD_VALIDATION-v1.0.2.json and current image/asset/source hashes.
- User CRC cores and prior personal BIOS/settings are not public assets.
