# v119 Distribution Edition r2

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

Write the whole SD image. **On first installation, a black screen after the boot
image is normal. Allow about 5 minutes: the device will automatically restart
once or twice while expanding SHARE and installing settings, then show the menu.
There is no need to worry; keep the power on and wait for setup to finish.**
Normal game round trips do not require reboot.

**첫 설치 시 부팅 이미지 이후 검정화면만 보여도 걱정하지 않으셔도 됩니다. 약 5분
기다리면 한두 차례 자동으로 재부팅한 뒤 메뉴가 표시됩니다. 전원을 끄지 말고
설치가 끝날 때까지 기다려 주세요.**

The base v119 and PortMaster correction were confirmed on hardware. This final
public variant was checked offline and not reflashed again. Exact vendor kernel
source and some inherited binary provenance remain unresolved; the source
inventory states those limits instead of claiming a complete firmware rebuild.

Raw IMG: 6,069,178,368 bytes.
Raw SHA256: `322efb6a52025372ef3c063fc840e6e296b4ff2a93860132a18ac578a4783842`.
Use the adjacent compressed-asset SHA256 before extracting/flashing.

[Installation](../docs/RELEASE.md) · [History](../docs/HISTORY.md) ·
[Sources and licenses](../docs/SOURCES_AND_LICENSES.md)

