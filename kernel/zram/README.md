# Action Pi ZRAM module build

The standard v1.0.5 release includes the full pinned Orange Pi source archive named in SOURCE.json. Extract it with one leading directory stripped and configure ACTIONPI_KERNEL_SOURCE, ACTIONPI_KERNEL_BUILD and optionally CROSS_COMPILE. Run `bash build.sh`. The tree-preparation patch enables building this older tree with GCC 13; candidate.config records the exact normalized configuration used. target.config is the recovered original configuration. `source/` contains the actual external module translation units and Kbuild used; zram_drv.c already contains zram-capacity-compat.patch, so do not apply it twice. Module checksums are in MODULES.json. The compressed source archive is shared by the standard and CRC editions.

The compiler was Arm GNU 13.3.Rel1 (GCC 13.3.1). Building without the original Module.symvers required KBUILD_MODPOST_WARN=1. That flag is not ABI proof: the original candidate was separately compared with the actual kernel exports, selected structure offsets/callbacks, and limited real-device compression/swap tests. A rebuild is not automatically runtime-certified. The pinned public tree is not claimed to be the exact original vendor kernel source.

Only the two zero-to-size/size-to-zero calls to set_capacity_and_notify were replaced by set_capacity. zram already rejects resizing an initialized device, and the original notification helper skips the RESIZE event across these zero transitions. This is not a general replacement for nonzero-to-nonzero resizing.

Kernel-derived files retain their own notices and Linux licensing. See ../../LICENSES/zram and ../../docs/SOURCES_AND_LICENSES.md. No device credentials, settings backups, runtime logs or extracted kernel binary are included.

한국어 과정은 ../../docs/BUILD.ko.md의 v1.0.5 항목을 참고하세요.

Packaging inputs: set ACTIONPI_IMAGE_DIR to the two v1.0.4 IMG files, ACTIONPI_ZRAM_BUNDLE to the directory containing the five built .ko files plus MODULES.json, and ACTIONPI_BENNU_CORE to the supplied binary. ACTIONPI_ZRAM_SERVICE and ACTIONPI_CORE_LOADER default to the published overlay/config scripts. Run `python3 tools/package-v1.0.5.py`; the source archive is a release asset, not a file to flash.
