# Development history and reasons for the final design

[English](HISTORY.md) · [한국어](HISTORY.ko.md)

## 1. Keep a bootable baseline

The original aim was PPSSPP Vulkan, rather than Vulkan in every emulator. An early
TSPS-style approach was too easily reduced to comparing Mali r32/r42 labels or
changing a PPSSPP option. In practice the kernel module, user-space Mali library,
Vulkan ICD registration, SDL and launch environment all had to agree.

Several experimental images failed before the menu, and adding/removing one
Wi-Fi file from an already changed image did not reconstruct a clean baseline.
The successful method was to restart from the known bootable v87 and preserve
working checkpoints. Stock firmware established that this unit's Wi-Fi hardware
worked. The final working stack used the AIC8800DC files appropriate to that
hardware, rather than treating every Wi-Fi module found in stock firmware as
interchangeable. v115 became the preserved working Wi-Fi/audio/RetroArch baseline.

## 2. Diagnose Mali ABI before installing it

The borrowed TSPS Mali module accessed three inode fields at offsets that did not
match the Action Pi kernel. The observed target offsets were `i_rdev=0x34`,
`i_mapping=0x20`, and `i_private=0x238`; the borrowed module used `0x44`, `0x30`,
and `0x248`. Page, mm_struct and dma_buf accesses were examined separately.

Rather than patching those three instructions and declaring compatibility,
the driver was rebuilt using a pinned public candidate kernel configuration.
The Orange Pi candidate is commit
`5b956b750422abd5e9e9c5523540d2aaf41a7939`; the Mali source is Radxa commit
`2045a3ca2a01f088c0314dc924bda59d154e363e`, r42p0-01eac0, JM/sunxi/devfreq.
Arm GNU 13.3.Rel1 supplied GCC 13.3.1 for AArch64 Linux.

Compilation produced the correct inode accesses. All 301 imported symbol names
were compared with actual target exports. That established name availability,
not complete semantic ABI compatibility. The candidate kernel still lost three
vendor config symbols (`AW_GPU_TYPE`, `ENC_SW2001`, `JOYSTICK_RGP`), so it was never
misrepresented as the exact original vendor tree. Initial compilation also lacked
Module.symvers; a produced `.ko` alone was not treated as dependency validation.

## 3. Avoid switching GPU drivers during each game launch

Removing Panfrost and loading Mali into the same running graphical session
encountered retained GPU power-management state. Starting with Mali as first
owner made initial Vulkan probing possible, but DRM close/restore could still
block. A Vulkan instance being created did not mean PPSSPP could render or exit.

The final route keeps Mali from boot and runs a compatible ES menu on the same
stack. It avoids requiring a Panfrost↔Mali transition for every game. Recovery
still exists for a failed menu startup; the normal path stays on Mali.

## 4. Repair display-client lifetime handling

Diagnostics followed the blocked DRM restore path to the output-poll worker and
its client list. Limited reads distinguished failed reads, wrong layouts and
invalid list entries. Offline code analysis then connected the dangling entry
to early framebuffer setup failure and incomplete cleanup.

The source repair propagates boot-logo connection errors before registration,
rejects zero dimensions, and unwinds registered clients before releasing their
containing allocation. The public candidate already had a meaningful platform
cleanup implementation, while the actual binary had an empty helper; applying
only a core-source diff to unknown vendor source would not restore that helper.

Since the exact vendor source was unavailable, v116 used a bounded ARM64 repair
within three existing function bodies, plus verified branch hooks. Original
bytes and kernel hash were guarded; the kernel was not expanded into guessed
padding. Link capacity, relocations and eight modeled ARM64 execution cases were
checked. Full-image comparison found 298 modified bytes in approved kernel/checksum
ranges. These modeled checks were not substitutes for hardware validation.

## 5. Separate rendering success from panel delivery

Vulkan initialized and PPSSPP ran while the physical display remained black.
Reading the final framebuffer showed recognizable game RGB content, proving
that a running process and a successful present call were insufficient evidence
of visible output. A later capture found alpha zero throughout the ARGB buffer.

The active plane was using premultiplied blending. Changing only its pixel blend
mode to **None**, through the application's existing DRM master, immediately made
the game visible. No DMA coherency or routing change was needed for that test.
The result identified the immediate alpha/blend mismatch, not every possible
source of alpha generation. The persistent opacity helper scopes this correction
to the PPSSPP session and closes its duplicate master descriptor before teardown.

## 6. Correct whole-application rotation and input

The panel's native mode is portrait 720×960. Rotating only the PSP game content
left the PPSSPP interface sideways; correcting orientation without agreeing on
logical dimensions then clipped menus and shrank games. The final wrappers use
landscape 960×720 application dimensions and rotate the complete output. The
owner confirmed game, menu, size, audio and controls, including the corrected D-pad.

The ES menu uses its established screen rotation option. RetroArch's SDL renderer
has a target-texture rotation adapter; GLES Flycast paths have a complete-drawable
adapter. These are separate scoped paths, not a global SDL replacement.

## 7. Keep ES and PPSSPP on one boot

ES can initialize using the vendor EGL/GLES/GBM stack when its loader environment
is kept clean. A supervisor outside ES's process group coordinates normal menu
quit, DRM-master release, PPSSPP startup/quit and a fresh menu. Observing an
unchanged boot ID across round trips distinguished this from hidden reboots.
The owner also selected a game normally and confirmed exit/menu return.

Automatic startup includes a next-boot recovery mechanism. Later the dispatcher
was fixed to avoid restoring historical knulli.conf snapshots over current user
preferences. That resolved language/timezone reverting and preserves PPSSPP choices.

## 8. Other emulator and power fixes

Dreamcast rotation was corrected for normal and standalone Flycast. VL/Xtreme
initially passed the Dreamcast logo but failed entering gameplay; that earlier
logo-only report was not final validation. The original JIT fault context was
being lost through SDL's evdev emergency signal handler. The final fix sets
`SDL_NO_SIGNAL_HANDLERS=1` only for those two old cores. An experimental signal
bridge was abandoned. Both then reached gameplay and were confirmed by the owner.

Suspend immediately woke because active AIC8800 SDIO held a wake lock. The Action
Pi hook remembers enabled Wi-Fi state, disables it before suspend, then restores
the previous ConnMan service after the radio is ready. Token checks cancel stale
reconnect attempts. The owner confirmed wake and automatic reconnection.

RetroArch HOME exit works. PPSSPP HOME exit caused a freeze/recovery reboot and
was disabled; SELECT+START held for about one second remains its exit method.
An early brightness I/O observation hook caused background-music stutter. The
read-path interception was removed; the final held-button supplement is scoped
to real brightness writes and does not inspect every music-file read.

## 9. Resolve brightness recurrence at the actual hardware layer

v117/v118 attempted fixes were withdrawn. Native ascending brightness values are
correct when the physical PWM signal is correct; numerical inversion only hid
the underlying problem temporarily.

First, a DTB edited inside the appended kernel data was not the effective boot
source. The live tree came from the external DTB in the raw TOC1 package at SD
offset `0x1004000`. The FAT copy was also older than that active package. The fix
changes the actual `/backlight0/pwms` polarity flag, refreshes the TOC checksum,
and synchronizes the FAT package without changing bootloader executable code.

Second, even with runtime DT polarity normal, the BSP driver left hardware PCR
bit 8 clear while its cached state said normal. Both cold boot and resume showed
this mismatch. The guarded normalizer validates the board, PWM controller and
runtime arguments, then sets only that physical polarity bit at the late boot
gate and resume hook. Native brightness values and held adjustment stay intact.
The owner confirmed complete shutdown/start and suspend/wake, and register
readback confirmed both transitions from 0 to 256. This became stable v119.

## 10. Public packaging and PortMaster

The public variant sets English and Wi-Fi off, removes personal network settings
from both live defaults and recovery snapshots, omits the additional BIOS archive,
and retains the base system's BIOS. Deleted FAT clusters and file slack were
zeroed, rather than only removing directory entries. Machine IDs, cookies,
histories, pairings and diagnostic captures were excluded from the settings payload.

After installing PortMaster, its Python/PySDL2 interface was rotated left. PySDL2
resolves functions from a named DLL, bypassing the earlier LD_PRELOAD approach.
A private SDL adapter reuses the working renderer correction and forwards other
symbols to the original SDL library. Only PortMaster selects it. The launcher
prepares that setting again if installation/update replaces its shell entry.
The owner confirmed direction and size; this fix is included in the public IMG.

## 11. Unify the standalone PPSSPP entry

ES's Emulators/PPSSPP script contained only a direct `PPSSPP` invocation. It used
the same standalone binary as the working PSP route, but skipped the Vulkan ICD,
output wrappers and opacity/session handling. A separate libretro core exists;
the symptom did not establish two different standalone builds.

The dispatcher now recognizes that specific Emulators entry and requests the
PPSSPP UI through the existing supervisor, without selecting or requiring a ROM.
The session runner omits only the game argument in UI mode. Normal PSP path and
extension validation, Vulkan environment, rotation, opacity, preferences and
SELECT+START handling remain shared. One installation restart reloaded the
resident supervisor. The owner confirmed Vulkan, direction/size and menu return.
The correction is packaged in public v1.0.0 (internal build v119 r2) and personal v120 r2.
Public version numbering starts at v1.0.0; this rename does not change image bytes.

## v1.0.1: Wi-Fi recovery-copy diagnosis and wider rotation

The early test images could connect once and lose Wi-Fi after reboot. A passive failed-boot report identified SDIO 024c:d723 with no bound driver. Its live S06 matched the old AIC-only recovery BOOT and its S08 matched the original rootfs, while the new helper file was present but unused. Mali restore/arm rewrote the active BOOT from that older copy. The preparation marker also existed under /var/run rather than /run. Internal test8 synchronized both BOOT copies and their hashes and corrected the marker; the user then confirmed Wi-Fi after reboot on 2026-10-25. Public v1.0.1 uses the unchanged normal-test8 bytes.

This release also carries the N64/Saturn/OpenBOR/standalone RetroArch launch corrections, SDLPoP and OD-Commander adapters, scoped PortMaster game rotation, and runtime-list metadata fixes. Emulator directions were all verified on hardware by the maintainer. These internal test names remain development history, not public release numbers.
