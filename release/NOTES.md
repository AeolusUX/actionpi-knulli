# Action Pi KNULLI v1.0.5

## English

Unofficial KNULLI adaptation for the Helegaly Action Pi. Mali runs the menu and PPSSPP Vulkan in the same boot.

### What changed

- **ZRAM service repaired:** the Services menu now starts/stops runtime-tested modules for this kernel, with the setting retained after reboot. ZRAM is **off by default**. It starts after the menu settles, uses lzo-rle, exposes logical swap of half the detected RAM and caps compressed RAM usage at a quarter of RAM (up to 512 MiB). RAM is allocated on demand. This helps memory-pressure situations; it does not guarantee higher FPS.
- **BennuGD core:** install the supplied ARM64 BennuGD libretro core and reconnect it automatically on each boot without save-overlay. The standard edition keeps its existing FBNeo/MAME cores.
- Existing PPSSPP 1.20.4/Vulkan, Mali menu, Wi-Fi, rotation, Ozone, PortMaster, rumble and brightness improvements are retained.

### Installation

Download this release's .img.xz and SHA256SUMS, verify the checksum and flash the whole SD card. Extract XZ first if required by your flashing tool. Flashing erases the selected card.

**On first installation, a black screen after the boot image is normal. Allow about 5 minutes: SHARE expansion and settings installation may restart the device once or twice before the menu appears. Keep power on until setup finishes.**

Brightness: **hold SELECT + Volume +/−**. Exit PPSSPP: **hold SELECT+START for about one second**. Emulator exit with the top HOME key works in RetroArch and remains disabled in PPSSPP. No game ROMs are included. ZRAM recovery: create an empty `ACTIONPI_ZRAM/DISABLED` file on BOOT to skip its startup. ZRAM recovery: create an empty `ACTIONPI_ZRAM/DISABLED` file on BOOT to skip its startup.

### Verification and technical documentation

ZRAM block compression/readback, actual 32 MiB swap-out/in, service start/stop and reboot startup were verified on the maintainer device. BennuGD file identity and active core mapping were verified; gameplay and reboot testing of that supplied core were not repeated. Long memory-pressure stress, suspend/resume, all hardware batches and a fresh SD flash of these newly packaged v1.0.5 images have not been tested.

- [History](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/HISTORY.md)
- [Architecture](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/ARCHITECTURE.md)
- [Build and packaging](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/BUILD.md)
- [Published files](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/PUBLIC_FILES.md)
- [Sources and licenses](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/SOURCES_AND_LICENSES.md)
- [Installation](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/RELEASE.md)
- [Verification scope](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/TESTING.md)

Board integration is based on [upstream KNULLI's Action Pi board configuration](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi). This is an adaptation of an inherited image, not a complete from-source firmware build.

Raw IMG: 6,069,178,368 bytes. SHA256: 2b0120fe41d11e78ecca1b3c2e0fbb02b86f55e14240ec5ac15e109947751bfe.

---

## 한국어

Helegaly Action Pi용 비공식 KNULLI 수정 배포판입니다. 같은 부팅에서 Mali 메뉴와 PPSSPP Vulkan을 사용합니다.

### 수정 내역

- **ZRAM 서비스 수정:** 서비스 메뉴에서 현재 커널에 맞춘 모듈을 켜고 끌 수 있으며 재부팅 후에도 선택이 유지됩니다. **기본값은 꺼짐**입니다. 메뉴 준비 후 lzo-rle로 시작하며 논리 스왑은 감지한 RAM의 절반, 실제 압축 RAM 사용 한도는 RAM의 1/4(최대 512MiB)입니다. 필요한 만큼만 RAM을 사용합니다. 메모리 부족 상황을 완화하는 기능이며 FPS 향상을 보장하지는 않습니다.
- **BennuGD 코어 적용:** 제공받은 ARM64 BennuGD libretro 코어를 넣고 재부팅 때 자동 연결되도록 했습니다. save-overlay는 필요 없습니다. 일반판의 FBNeo·MAME 코어는 기존 상태를 유지합니다.
- 기존 PPSSPP 1.20.4·Vulkan, Mali 메뉴, Wi-Fi, 회전, Ozone, PortMaster, 진동·밝기 보완은 유지합니다.

### 설치

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 굽습니다. 기록 프로그램이 XZ를 지원하지 않으면 먼저 압축을 풀어 주세요. 기록 대상 SD의 기존 내용은 지워집니다.

**첫 설치는 부팅 이미지 뒤 검정화면이 보여도 정상입니다. 약 5분 기다리면 SHARE 자동 확장·설정 설치 중 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 전원을 유지한 채 완료될 때까지 기다려 주세요.**

밝기는 **SELECT를 누른 채 볼륨 +/−**, PPSSPP 종료는 **SELECT+START 약 1초**입니다. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하며 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 안에 이름이 `DISABLED`인 빈 파일을 만들면 됩니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 안에 이름이 `DISABLED`인 빈 파일을 만들면 됩니다.

### 검증 범위와 기술 문서

관리자 실기에서 ZRAM 블록 압축·되읽기, 실제 32MiB 스왑 저장·복원, 서비스 켜기·끄기와 재부팅 자동 시작을 확인했습니다. BennuGD는 파일 해시·실제 코어 연결을 확인했으며 해당 제공 코어의 게임 실행·재부팅 시험은 반복하지 않았습니다. 장시간 메모리 압박·절전 복귀·모든 생산분 및 새 v1.0.5 IMG를 SD에 다시 굽는 시험은 하지 않았습니다.

- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5/docs/TESTING.ko.md)

보드 구성은 상위 KNULLI의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)을 기반으로 했습니다. 기존 이미지를 수정한 배포판이며 모든 구성요소를 소스에서 완전히 재빌드한 펌웨어는 아닙니다.

압축 해제 IMG: 6,069,178,368바이트. SHA256: 2b0120fe41d11e78ecca1b3c2e0fbb02b86f55e14240ec5ac15e109947751bfe.
