# Runtime architecture

[English](ARCHITECTURE.md) · [한국어](ARCHITECTURE.ko.md)

Target guard: `/boot/boot/knulli.board` must be `helegany-action-pi`; kernel is
the specifically guarded, repaired 5.15.147 binary. Equal version strings alone
are not a compatibility test. These files are not instructions to install the
module on arbitrary A527/TSPS devices.

## Startup

1. Original partition initialization expands SHARE on a new card and reboots.
2. S12 invokes `/boot/postshare.sh` after SHARE is mounted. `STABLE_V119/firstboot.py`
   verifies payload hashes, extracts only sanitized settings, writes a completion
   marker, syncs and reboots. It does not restore the personal BIOS archive.
3. `boot-custom.sh` prepares the Action Pi userspace fixes. The Mali startup gate
   and boot arguments prevent Panfrost from taking the GPU first, then use the
   candidate Mali module and vendor libraries.
4. The late gate reconciles the hardware PWM polarity. It validates the board,
   controller register description and live DT PWM arguments before changing bit8.
5. A supervisor starts ES with the vendor EGL/GLES/GBM loader environment, correct
   screen rotation, input and audio settings. Its recovery/attempt markers allow
   the next boot to fall back if startup fails.

## PSP handoff

The dispatcher routes PSP launch requests to `mali_session.py`. The supervisor
also handles an explicit UI-only request from ES Emulators/PPSSPP. It omits the
ROM argument for that mode; normal game requests retain their path validation.
The supervisor
asks ES to quit normally and waits for its display resources to close. It starts
PPSSPP with the scoped Vulkan/SDL output wrappers and opacity correction. On exit
it releases helper descriptors before bringing the menu back. GPU ownership
remains Mali; the ordinary route does not unload/rebind GPU drivers.

Automatic sessions do not restore a historical knulli.conf over current choices.
PPSSPP's configuration tree is handled without discarding saved preferences.
The old one-shot diagnostic managers remain separate from this normal session
route; manually running their original experiment commands is not required.

## Output adapters

| Process/path | Correction |
| --- | --- |
| ES | Native screenrotate option and menu-only audit/input supplement |
| PPSSPP Vulkan | Vulkan output transform, matching SDL logical dimensions, scoped opacity helper |
| RetroArch SDL2 | 960×720 target texture, clockwise90 presentation to 720×960 |
| RetroArch GL / standalone Flycast | Whole GLES drawable FBO rotation |
| PortMaster/PySDL2 | Private named SDL DLL with forwarding dependency on original SDL |

No rotation library replaces `/usr/lib/libSDL2` globally. The PortMaster helper
patches only its `PYSDL2_DLL_PATH` selection under `ACTIONPI_MALI_SESSION=1`;
launch preparation repeats if its shell entry has been replaced.

## Power, brightness and audio

The suspend hook records whether Wi-Fi is powered, disables it to release the
SDIO wake lock, then schedules reconnect to the remembered service after wake.
If Wi-Fi was off, the hook does not enable it merely because the unit woke.
The same resume entry normalizes PWM polarity. Brightness numbers are native
ascending values, not a software `max-value` inversion. Speaker LINEOUT gain is
25 instead of23; this does not change the headphone gain.

## Recovery

An empty `/boot/DISABLE_MALI.txt` requests the fallback menu. That fallback does
not provide the normal PPSSPP Vulkan path. Keep the card's own recovery snapshots:
they are checksum guarded and are not interchangeable with a different image's
backups. Do not restore just the old PWM DT flag while retaining the new strict
normalizer. Whole-image recovery is preferable to mixing historical experiments.
