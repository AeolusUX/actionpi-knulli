# Sources, licenses and provenance

[English](SOURCES_AND_LICENSES.md) · [한국어](SOURCES_AND_LICENSES.ko.md)

This firmware is a collection of separately licensed components. A repository
license for original glue does not replace Linux, Arm, SDL, emulator, firmware
or BIOS terms. Existing notices in vendored files are preserved.

| Component | Recorded source/provenance | Status |
| --- | --- | --- |
| Original adaptation glue | `overlay/`, `src/`, `tools/` | Original glue uses the scoped MIT notice; kernel-derived work retains GPL terms |
| Mali kernel driver | Radxa allwinner-bsp commit `2045a3ca2a01f088c0314dc924bda59d154e363e`, `modules/gpu/mali-valhall/driver` | Tracked upstream source vendored here; license.txt and file notices retained; candidate build inputs recorded |
| Vendor Linux5.15.147 | Recovered config, binary identity and guarded repair source included | Exact original vendor tree/build provenance remains unidentified |
| Public kernel candidate | Orange Pi commit `5b956b750422abd5e9e9c5523540d2aaf41a7939` | Used for header/layout/source comparison; not a substitute claim for exact vendor corresponding source |
| KNULLI integration | [Action Pi board configuration](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi) on `knulli-main`; A527 history at `5a7cb1e8e4dd` | Board-integration base; complete exact source closure of inherited image not established |
| SDL2 | [release-2.32.8](https://github.com/libsdl-org/SDL/tree/release-2.32.8) | Target SDL2.32.8 identified; new adapters are separate source files |
| Flycast VL reference | [libretro/flycast commit4a913e0](https://github.com/libretro/flycast/tree/4a913e063c95d1fae98afc64645831de0bcad57e) | Recorded source reference for old signal/JIT investigation |
| PPSSPP/Flycast/RetroArch/ES | Inherited KNULLI programs; adaptation source here wraps their launch/output behavior | Exact source/version closure for every inherited binary is not claimed |
| Mali userspace libraries | Inherited vendor stack; observed r32p0 GLES renderer | Proprietary/vendor binaries; the kernel-driver GPL license does not license libmali |
| AIC8800DC module/firmware | Files reused from working stock firmware | Binary provenance recorded by adaptation; exact corresponding module source/redistribution terms not fully resolved |
| Base BIOS | Inherited base-rootfs BIOS retained unchanged | Not covered by this project's glue license; this is not a BIOS-free distribution |
| Added personal BIOS archive | Excluded | Not a public release asset |

## Why the source distinction matters

The [GNU GPLv2 FAQ](https://www.gnu.org/licenses/old-licenses/gpl-2.0-faq.html)
explains source obligations when distributing GPL binaries. A generic upstream
URL or similarly numbered kernel is not, by itself, the source used for a given
vendor binary. This repository therefore does not claim that the unresolved
vendor source questions have been solved merely by publishing a public candidate.

The full source/provenance inventory of the inherited distribution still needs
work. In particular, exact original kernel changes, stock Wi-Fi source and
vendor userspace/retained BIOS terms should be resolved before claiming complete
source or redistribution compliance for the entire image. This document records
the actual evidence and gaps; it is not a certification of that claim.

## Primary upstream references

- [KNULLI](https://github.com/knulli-cfw/knulli-linux)
- [Pinned Mali source](https://github.com/radxa/allwinner-bsp/tree/2045a3ca2a01f088c0314dc924bda59d154e363e/modules/gpu/mali-valhall/driver)
- [Pinned Orange Pi candidate](https://github.com/orangepi-xunlong/linux-orangepi/tree/5b956b750422abd5e9e9c5523540d2aaf41a7939)
- [Arm GNU13.3.Rel1](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)
- [SDL evdev signal path](https://github.com/libsdl-org/SDL/blob/release-2.32.8/src/core/linux/SDL_evdev_kbd.c)
- [Ultramarine handheld vendor-stack work](https://github.com/Ultramarine-Linux/ultramarine-handheld)

Build toolchain archive SHA256 recorded during preparation:
`322f0b4482fc0d9fa0bb468134841f08d8c554c54ff5aa29a13a7a24bf7e1eb5`.
