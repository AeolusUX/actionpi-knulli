# Release and development milestones

These are curated milestones, not a fabricated historical Git commit log.
Development checkpoint numbers are internal, not upstream KNULLI versions.
Public release numbering starts at **v1.0.0**.

| Checkpoint | Outcome |
| --- | --- |
| v87 baseline | Known bootable starting point; preserve it while testing Wi-Fi |
| v92–v114 experiments | Boot failures/freezes and incorrect Wi-Fi assumptions; not release recommendations |
| v115 | Personal stable checkpoint with working Wi-Fi, audio and RetroArch |
| v116, 2026-10-22 | Guarded display-client cleanup kernel repair; later Mali/Vulkan and presentation trials |
| 2026-10-23 integration | Correct scanout opacity/rotation, input, persistent settings; Mali menu and same-boot PSP round trips |
| v117 / v118 | Withdrawn because brightness inversion/polarity handling was incomplete |
| v119, 2026-10-24 | Cold boot and suspend/wake brightness correction confirmed; owner confirmed installed stable image |
| v119 Distribution Edition | Public defaults, personal BIOS archive removed, base BIOS retained, private data cleanup; PortMaster rotation added |
| v119 Distribution r2 / personal v120 r2 | ES Emulators/PPSSPP standalone entry routed through the existing Vulkan supervisor; no ROM required; owner confirmed output and menu return |
| Personal v120 | Private successor to personal v119, including BIOS/settings and PortMaster fix; not a public asset |

## First public release: v1.0.0 — 2026-10-24

Public v1.0.0 is the unchanged image previously labeled internally as
v119 Distribution Edition r2. The release title, tag, filenames and documentation
now use v1.0.0; the IMG and XZ bytes and their SHA256 values are unchanged.
The owner downloaded the published image, wrote it to an SD card and confirmed
installation and normal operation. Personal v120 remains unchanged and private.
Historical checkpoint names, runtime paths and packaging tools retain their
original identifiers so they still describe the actual work.
