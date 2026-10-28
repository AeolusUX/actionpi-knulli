# Action Pi KNULLI v1.0.7

## English

Unofficial KNULLI adaptation for the Helegaly Action Pi. Mali runs the menu and PPSSPP Vulkan in the same boot.

### What changed

- **Return to the game list:** after closing PPSSPP or Flycast Vulkan, ES now reopens the saved system’s game list instead of the top-level system selector.
- **Normal startup preserved:** game-list startup is temporary for the return session. The original startup preference is restored when ES closes, or at the next supervisor start after an interrupted session. Other ES settings are retained.
- **Selection limit:** the game list opens at its first entry; the exited game’s cursor position and subfolder are not restored.
- Existing Mali, PPSSPP Vulkan, Flycast Vulkan/standard core 2.7, rotation, Wi-Fi, Ozone, PortMaster, rumble, brightness, ZRAM and BennuGD functionality is retained. Standard Flycast is a good first choice, but VL or Xtreme may perform better in some games; compare the cores for your game.

### Installation

Download this release's .img.xz and SHA256SUMS, verify the checksum and flash the whole SD card. Extract XZ first if required by your flashing tool. Flashing erases the selected card.

**On first installation, a black screen after the boot image is normal. Allow about 5 minutes: SHARE expansion and settings installation may restart the device once or twice before the menu appears. Keep power on until setup finishes.**

Brightness: **hold SELECT + Volume +/−**. Exit PPSSPP: **hold SELECT+START for about one second**. Emulator exit with the top HOME key works in RetroArch and remains disabled in PPSSPP. No game ROMs are included. ZRAM recovery: create an empty `ACTIONPI_ZRAM/DISABLED` file on BOOT to skip its startup.

### Verification and technical documentation

On the maintainer device, PSP OutRun 2006 and standard Flycast Crazy Taxi 2 were launched from their ES game lists, exited normally, and returned to the respective PSP/Dreamcast lists without another reboot; captures confirmed both lists. Initial startup remained unchanged after the installation reboot. Preference restoration was checked with both absent and explicit-false settings while preserving other settings. VL/Xtreme use the same supervisor path; their individual launches and a fresh SD flash of these final images were not repeated.

- [History](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/HISTORY.md)
- [Architecture](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/ARCHITECTURE.md)
- [Build and packaging](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/BUILD.md)
- [Published files](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/PUBLIC_FILES.md)
- [Sources and licenses](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/SOURCES_AND_LICENSES.md)
- [Installation](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/RELEASE.md)
- [Verification scope](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/TESTING.md)

Board integration is based on [upstream KNULLI's Action Pi board configuration](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi). This is an adaptation of an inherited image, not a complete from-source firmware build.

Raw IMG: 6,069,178,368 bytes. SHA256: 56ea1f86b6e7dea4ba512059d1018eaad98e5e50d8922576cd0468f2a8c9c80f.

---

## 한국어

Helegaly Action Pi용 비공식 KNULLI 수정 배포판입니다. 같은 부팅에서 Mali 메뉴와 PPSSPP Vulkan을 사용합니다.

### 수정 내역

- **게임 종료 후 목록 복귀:** PPSSPP·Flycast Vulkan을 종료하면 ES 상위 기종 선택 화면 대신 저장된 해당 기종의 게임 목록으로 돌아갑니다.
- **평소 부팅 설정 유지:** 게임 종료 후 복귀할 때만 임시로 게임 목록을 열며, ES 종료 후 원래 시작 설정을 복원합니다. 비정상 종료된 경우 다음 감독자 시작 때 복원하고 다른 ES 설정은 유지합니다.
- **선택 위치 제한:** 목록은 첫 항목부터 표시하며 종료한 게임의 커서·하위 폴더 위치까지 복원하는 기능은 아닙니다.
- 기존 Mali·PPSSPP Vulkan·Flycast Vulkan/일반 코어 2.7·회전·Wi-Fi·Ozone·PortMaster·진동·밝기·ZRAM·BennuGD 기능은 유지합니다. 일반 Flycast를 우선 권장하지만 게임에 따라 VL이나 Xtreme이 더 유리할 수 있으니 비교해서 선택해 주세요.

### 설치

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 굽습니다. 기록 프로그램이 XZ를 지원하지 않으면 먼저 압축을 풀어 주세요. 기록 대상 SD의 기존 내용은 지워집니다.

**첫 설치는 부팅 이미지 뒤 검정화면이 보여도 정상입니다. 약 5분 기다리면 SHARE 자동 확장·설정 설치 중 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 전원을 유지한 채 완료될 때까지 기다려 주세요.**

밝기는 **SELECT를 누른 채 볼륨 +/−**, PPSSPP 종료는 **SELECT+START 약 1초**입니다. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하며 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 안에 이름이 `DISABLED`인 빈 파일을 만들면 됩니다.

### 검증 범위와 기술 문서

실기 ES의 각 게임 목록에서 PSP OutRun 2006과 일반 Flycast Crazy Taxi 2를 실행·정상 종료하고, 재부팅 없이 각각 PSP·Dreamcast 목록으로 돌아오는 것을 캡처로 확인했습니다. 설치 후 재부팅에서는 기존 첫 화면 설정이 유지됐고, 원래 값이 없거나 false인 설정의 복원과 다른 설정 보존을 확인했습니다. VL·Xtreme은 같은 감독 경로를 사용하며 개별 실행과 최종 이미지의 새 SD 플래싱 시험은 반복하지 않았습니다.

- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7/docs/TESTING.ko.md)

보드 구성은 상위 KNULLI의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)을 기반으로 했습니다. 기존 이미지를 수정한 배포판이며 모든 구성요소를 소스에서 완전히 재빌드한 펌웨어는 아닙니다.

압축 해제 IMG: 6,069,178,368바이트. SHA256: 56ea1f86b6e7dea4ba512059d1018eaad98e5e50d8922576cd0468f2a8c9c80f.
