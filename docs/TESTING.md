# Verification scope

[English](TESTING.md) · [한국어](TESTING.ko.md)

| Check | Evidence |
| --- | --- |
| v1.0.2 final device runtime | Healthy menu/reboot Wi-Fi after SSH update and guard fix; owner subsequently confirmed all final changes, including Ozone, working |
| Newly packaged v1.0.2 IMG | File readback, complete BOOT references, unaffected bytes and XZ/image hashes checked; a fresh IMG reflash was not independently repeated |
| v1.0.1 source firmware | On 2026-10-25, user feedback confirmed test8 Wi-Fi still works after reboot; public IMG bytes match normal test8 |
| Emulator directions | Maintainer confirmed all emulator screen directions on hardware |
| PortMaster menus | Runtime manager and port-management display confirmed; full update/download/install matrix not exhaustively retested |
| Boot persistence | Actual Mali restore/arm functions preserved updated S06/S08 for three cycles in temporary files; transaction recovery and separate /var/run marker checked offline |
| Core functions | Owner confirmed normal operation after installation |
| Brightness | Owner confirmed complete shutdown/start and suspend/wake; runtime DT/PWM readback agreed |
| ES↔PPSSPP | Automatic and manual launch/exit/menu return confirmed on the same boot |
| PSP display/audio/input | Owner confirmed game and emulator UI, full-size orientation, sound and controls |
| Preferences | PPSSPP exit/relaunch persistence and system language/timezone persistence confirmed |
| RetroArch | Display direction/size and HOME exit confirmed |
| Flycast | Normal/standalone orientation confirmed; VL/Xtreme tested into gameplay, not only startup logo |
| Suspend | Screen remains off; wakes on next press; previously enabled Wi-Fi reconnects |
| PortMaster | Owner relaunched and confirmed direction and size before packaging |
| Emulators/PPSSPP standalone | Owner confirmed Vulkan selection, direction/size and SELECT+START return after the UI-only route fix; no ROM required |
| Public defaults | Offline archive assertions for English, Wi-Fi0, no saved personal network and removed Ports entries |
| Source/base integrity | Source IMG checksum, modified-file readback, unchanged rootfs checksum and final IMG checksum |
| Private data cleanup | Sanitized settings/recovery copies, cleared free clusters/slack, known-credential raw scan |
| Final public variant | On 2026-10-24, owner downloaded the published v1.0.0 image, wrote it to an SD card, installed it on the device and confirmed normal operation |

No claim is made that every game, every PortMaster port, every emulator backend,
all suspend scenarios, all driver ABI behavior or unrelated board variants were
tested. Standalone Flycast HOME exit remains unconfirmed. Shader cache presence,
module load, Vulkan enumeration, a presented framebuffer and a visible game are
different milestones; the history distinguishes them.

The kernel repair's modeled ARM64 tests check selected calls, error paths,
callee-saved state and cleanup ordering. They do not emulate the complete device,
allocator, concurrency, power management or electrical panel.

## v1.0.2

The final runtime changes reached a healthy Mali menu after the home-device SSH update. Wi-Fi reconnected, and ordinary-core/standalone RetroArch checks completed. The owner then confirmed all final changes working on 2026-10-25. This newly packaged public IMG was not independently downloaded and reflashed; not every core, game, port or board variant was retested.

## v1.0.3 — 2026-10-26

- **Rumble:** use a 25 kHz motor PWM carrier and compensate low-strength effects. Crazy Taxi 1/2 with Flycast VL/Xtreme now provides noticeable small rumble with reduced high-pitched motor-related noise on the tested device.
- **Brightness shortcut:** hold SELECT, then use Volume +/−. Normal volume and HOME behavior are retained; held adjustment works.
- **Brightness overlay:** show a sun icon, percentage and bar above the menu or game, then hide it about 2.2 seconds after adjustment. It uses an unused display plane and runs only while visible; no idle overlay service is added.
- **Background cleanup:** disable KNULLI usage-statistics reporting by default and stop the obsolete repeating boot-log copy on devices carrying it. Omit old diagnostic maps from the image.
- Existing Mali menu/PPSSPP Vulkan, Wi-Fi, screen rotation, Ozone and PortMaster functionality is retained.

On-device tests confirmed rumble strength/noise and persistence after reboot, disabled statistics/repeating logging after reboot, and the brightness shortcut's direction, hold and normal-volume behavior. The owner confirmed the brightness overlay in ES and PPSSPP, automatic hiding, and game exit/menu return; remote inspection confirmed the overlay worker exits. The overlay uses a shared display path, but every emulator and hardware batch was not individually retested. The owner subsequently rebooted the device and confirmed all applied changes still work, including the brightness shortcut and overlay. These newly packaged installation images have not been independently reflashed.
