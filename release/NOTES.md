# v119 Distribution Edition

Unofficial Action Pi adaptation with the hardware-confirmed Mali menu/PPSSPP
path, persistent brightness direction and PortMaster rotation correction.

- English defaults; Wi-Fi initially off with no personal saved network.
- Additional personal BIOS collection excluded; **original base-system BIOS retained**.
- No game ROMs. Removed legacy restore-menu and hardcoded PSP test Ports entries.
- PortMaster installer retained; its GUI receives scoped direction/size correction.
- Revision2: ES Emulators/PPSSPP standalone menu uses the same Vulkan supervisor
  without a ROM, including output correction and SELECT+START exit/menu return.
- Existing brightness, preferences, emulator output, suspend/reconnect and audio
  improvements retained. Hold SELECT+START about one second to leave PPSSPP.

Write the whole SD image. First installation performs SHARE expansion/reboot,
then settings installation/reboot. Normal game round trips do not require reboot.

The base v119 and PortMaster correction were confirmed on hardware. This final
public variant was checked offline and not reflashed again. Exact vendor kernel
source and some inherited binary provenance remain unresolved; the source
inventory states those limits instead of claiming a complete firmware rebuild.

Raw IMG: 6,069,178,368 bytes.
Raw SHA256: `322efb6a52025372ef3c063fc840e6e296b4ff2a93860132a18ac578a4783842`.
Use the adjacent compressed-asset SHA256 before extracting/flashing.

[Installation](../docs/RELEASE.md) · [History](../docs/HISTORY.md) ·
[Sources and licenses](../docs/SOURCES_AND_LICENSES.md)

