# Yaba Sanshiro 1.20.51 / Action Pi GLES

The `saturn-standalone-1.20.51-v1.0.8-r2-sources.tar.xz` release asset contains
the actual modified source tree used for the shipped ARM64 executable, pinned
libchdr, upstream notices, build references and a rebuild helper. The official
source is https://d1t36rsydvwkyk.cloudfront.net/yabasanshiro-src-1.20.51.tar.gz
(SHA256 ef9abad152af10f812c5876ae9337e8a92314766421e2fa92737b548639163c4).

GLES is enabled, Vulkan disabled, SH2 DevMiyax JIT enabled, SCSP2 and OpenAL
disabled. The SDL output backend and realtime SCSP generator are retained.
Changes cover the Linux frontend, L3 menu, GLES menu drawing, control mapping,
render-thread FPS initialization and absolute-deadline audio pacing.

Image revision r2 additionally honors the digital/3D pad selector and merges
the saved physical D-pad and analog-stick mappings into digital directions.
It keeps the ordinary Saturn pad protocol (including START compatibility).
The direction merge handles held-source releases, diagonals, opposite directions,
deadzone and axis inversion; true 3D mode keeps its existing analog handling.
The helper and host behavior check are included alongside the source.

`existing-source-changes.patch` records changes to existing UTF-8 C/C++/CMake
files only; it is not a substitute for the full source asset, which also contains
new adapter files, headers and generated code. Android benchmark disc images
and unrelated binaries/build outputs are omitted. Upstream notices are retained.

To build: extract the full source asset, supply the matching ARM64 SDL2/Mali
SDK and dependencies listed in DEPENDENCIES.json, install the Arm GNU 13.3.rel1
aarch64-none-linux-gnu toolchain and recent CMake, then run `rebuild.py` with
--sdk, --toolchain-prefix and --cmake arguments. The historical configure script
documents initial porting; do not rerun it over the already-fixed source.
Reference absolute paths in the archived CMake files are rewritten by rebuild.py.
This is corresponding application source; it does not establish the provenance
of every inherited firmware component or promise byte-for-byte reproducibility.

RetroAchievements support in this standalone frontend is unavailable in this
build. The existing RetroArch Saturn core is unchanged. No game or BIOS files,
personal device profiles or failed Vulkan experiments are included.
