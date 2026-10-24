# Action Pi KNULLI adaptation

Unofficial KNULLI adaptation for **Helegany Action Pi**, documenting the work needed
to run a Mali-based EmulationStation menu and PPSSPP Vulkan on the same boot.
This is a community adaptation, not an official KNULLI release or a universal
TrimUI Smart Pro S firmware.

[한국어 안내](README.ko.md) · [Development history](docs/HISTORY.md) ·
[Architecture](docs/ARCHITECTURE.md) · [Build/source status](docs/BUILD.md) ·
[Troubleshooting](docs/TROUBLESHOOTING.md)

## Download and install

Download **v119 Distribution Edition** from
[Releases](https://github.com/pikachu220v/actionpi-knulli/releases).
Use the `.img.xz` asset and matching SHA256 file. Extract the image if your flashing
application does not accept XZ, then write the image to the **whole SD card**.
Writing an image replaces the selected card's contents.

On first installation, SHARE expands and the device restarts. The settings
installer runs afterward and restarts once more. Wait for the menu; a black
screen during first-time installation is expected. Subsequent PSP launches do
not require a reboot. See [installation and release details](docs/RELEASE.md).

## Distribution defaults

| Item | Public distribution |
| --- | --- |
| Language | English, including PPSSPP |
| Wi-Fi | Off initially; no personal saved SSID/password |
| Additional BIOS collection | Excluded |
| Original base-system BIOS | Retained unchanged |
| Game ROMs | Not included |
| Ports restore-original-menu shortcut | Removed |
| Old hardcoded PPSSPP Vulkan test shortcut | Removed; launch games from PSP |
| PortMaster | Installer retained; direction/size fix applied when launched |

The distribution is **not BIOS-free**: it retains the base system's original
BIOS files at the maintainer's explicit choice. Add any additional BIOS you need
to SHARE's `bios` directory. This repository does not upload the separate
personal images or their Wi-Fi configuration.

## Working features

- Mali owns the GPU from startup; ES → PPSSPP Vulkan → ES works without a reboot
  between games.
- Correct menu, PSP, RetroArch, Flycast and PortMaster direction/size on the
  physically portrait 720×960 panel; application layout is landscape 960×720.
- PPSSPP game/menu output, audio, analog sticks, buttons and D-pad; preferences
  persist between launches.
- The ES **Emulators → PPSSPP** entry opens the same Vulkan application menu,
  without needing a game file, using the same display correction and exit path.
- Normal/standalone Flycast, plus VL/Xtreme gameplay after scoped signal handling.
- Brightness direction and held adjustment, including cold boot and suspend resume.
- Suspend/wake and Wi-Fi reconnect when Wi-Fi was enabled before sleep.
- Korean/Seoul preferences remain selectable and persistent, although this public
  edition starts in English. Speaker LINEOUT gain is adjusted from 23 to 25.

Hold **SELECT+START for about one second** to exit PPSSPP. HOME exit is enabled
for RetroArch but deliberately disabled for PPSSPP after a quit regression.
Flycast standalone HOME exit is not separately confirmed.

## Evidence and limits

The v119 base was installed and confirmed working by the device owner. PortMaster
direction/size was separately confirmed on hardware before packaging. Public
distribution defaults and file integrity were checked offline; the final public
variant was not flashed again. See [test coverage](docs/TESTING.md).

The exact vendor source of the original 5.15.147 kernel has **not** been identified.
The pinned public candidate is not described as that exact source. This repository
contains the adaptation code, guarded repair source, recovered config, and pinned
Mali source, but is **not a complete from-source rebuild of every firmware
component**. [Sources, licenses and unresolved provenance](docs/SOURCES_AND_LICENSES.md)
distinguish these cases explicitly.

## Repository contents

| Directory | Purpose |
| --- | --- |
| `overlay/boot/` | Actual runtime scripts/source extracted from the public IMG |
| `src/` | Rotation adapters and guarded display/PWM repair source |
| `kernel/` | Recovered kernel config, candidate options, repair patch/evidence |
| `third_party/mali-valhall/` | Pinned upstream driver source, with its license |
| `config/` | Public defaults and PortMaster installation entry |
| `tools/` | Portable helper build script and historical packaging scripts |
| `release/` | Public image manifest, hashes and component inventory; no IMG in Git |
| `docs/` | History, architecture, testing, troubleshooting and provenance |

Original project glue is provided under the scoped MIT terms in `LICENSE`;
kernel-derived and third-party files retain their own terms. No blanket MIT
license is applied to the firmware. Credits: KNULLI/Batocera, Linux/Allwinner/
Orange Pi/Radxa, Arm, SDL, PPSSPP, Libretro/Flycast, PortMaster and the
[Ultramarine handheld work](https://github.com/Ultramarine-Linux/ultramarine-handheld)
that helped establish the vendor-stack direction.
