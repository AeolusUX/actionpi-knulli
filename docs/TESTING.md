# Verification scope

[English](TESTING.md) · [한국어](TESTING.ko.md)

| Check | Evidence |
| --- | --- |
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
