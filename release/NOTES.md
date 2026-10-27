# Action Pi KNULLI v1.0.6

## English

Unofficial KNULLI adaptation for the Helegaly Action Pi. Mali runs the menu and PPSSPP Vulkan in the same boot.

### What changed

- **Flycast Vulkan:** standard, VL and Xtreme now use Vulkan with correctly oriented gameplay and RetroArch menus, plus normal HOME exit and return to ES without rebooting.
- **Standard Flycast 2.7:** update the standard core to the official v2.7 source release. VL and Xtreme retain their existing source revisions.
- **Strong recommendation:** hands-on testing on the Action Pi showed a significant performance improvement when switching the standard Flycast core from OpenGL to Vulkan, with much smoother gameplay. **We strongly recommend using the standard Flycast core as your first choice.** This observed gain comes from the Vulkan switch; it is not a measured 2.7-versus-2.5 benchmark or a guarantee for every game. (Depending on the game, VL or Xtreme may perform better, so compare the cores and choose the one that works best for your game.)
- **Resolution-change rotation fix:** retain the scoped rotation loader when RetroArch reinitializes Vulkan after an internal-resolution change. The shared fix is installed for all three cores. OpenGL shaders are disabled for these Vulkan sessions; other emulators keep their existing settings.
- Existing Wi-Fi, PPSSPP, Mali menu, Ozone, PortMaster, rumble, brightness, ZRAM and BennuGD improvements are retained.

### Installation

Download this release's .img.xz and SHA256SUMS, verify the checksum and flash the whole SD card. Extract XZ first if required by your flashing tool. Flashing erases the selected card.

**On first installation, a black screen after the boot image is normal. Allow about 5 minutes: SHARE expansion and settings installation may restart the device once or twice before the menu appears. Keep power on until setup finishes.**

Brightness: **hold SELECT + Volume +/−**. Exit PPSSPP: **hold SELECT+START for about one second**. Emulator exit with the top HOME key works in RetroArch and remains disabled in PPSSPP. No game ROMs are included. ZRAM recovery: create an empty `ACTIONPI_ZRAM/DISABLED` file on BOOT to skip its startup.

### Verification and technical documentation

The maintainer directly played standard/VL/Xtreme Vulkan and reported improved clarity and performance, especially with the standard core. Standard 2.7 was checked remotely for game/demo and menu output, actual Vulkan reinitialization after a resolution increase, preserved orientation and clean return to ES on the same boot. Individual VL/Xtreme resolution changes, physical audio/input on 2.7, a 2.7 performance comparison, a fresh SD flash of these final images and all hardware batches were not retested.

- [History](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/HISTORY.md)
- [Architecture](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/ARCHITECTURE.md)
- [Build and packaging](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/BUILD.md)
- [Published files](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/PUBLIC_FILES.md)
- [Sources and licenses](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/SOURCES_AND_LICENSES.md)
- [Installation](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/RELEASE.md)
- [Verification scope](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/TESTING.md)

Board integration is based on [upstream KNULLI's Action Pi board configuration](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi). This is an adaptation of an inherited image, not a complete from-source firmware build.

Raw IMG: 6,069,178,368 bytes. SHA256: fcc87396aa584440d3c93e50ca3b8bec00e5ec2f29219391c2ceaacacd87fb5f.

---

## 한국어

Helegaly Action Pi용 비공식 KNULLI 수정 배포판입니다. 같은 부팅에서 Mali 메뉴와 PPSSPP Vulkan을 사용합니다.

### 수정 내역

- **Flycast Vulkan 적용:** 일반·VL·Xtreme을 Vulkan으로 실행하며 게임·RetroArch 메뉴 회전 보정, HOME 종료와 재부팅 없는 ES 메뉴 복귀를 연결했습니다.
- **일반 Flycast 2.7 업데이트:** 일반 코어만 공식 v2.7 소스로 업데이트했습니다. VL·Xtreme의 소스 버전은 유지했습니다.
- **일반 코어 강력 추천:** 액션파이 실기에서 일반 Flycast 코어를 OpenGL에서 Vulkan으로 전환한 뒤 큰 폭의 성능 향상과 훨씬 부드러운 게임 화면을 직접 확인했습니다. **일반 Flycast 코어를 우선 사용하실 것을 강력히 권장합니다.** 확인된 향상은 Vulkan 전환 결과이며 2.7과 2.5의 정량 비교나 모든 게임의 성능 보장은 아닙니다. (게임에 따라 VL이나 Xtreme이 더 유리할 수 있으니 직접 비교해 보고 알맞은 코어를 선택해 주세요.)
- **해상도 변경 시 회전 유지:** 내부 해상도를 바꾸며 RetroArch가 Vulkan을 재초기화할 때 회전 보정 로더가 빠지는 문제를 수정했습니다. 세 코어에 공통 적용했습니다. 해당 Vulkan 실행에서는 GL 셰이더를 끄며 다른 에뮬레이터의 설정은 유지합니다.
- 기존 Wi-Fi·PPSSPP·Mali 메뉴·Ozone·PortMaster·진동·밝기·ZRAM·BennuGD 보완을 유지합니다.

### 설치

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 굽습니다. 기록 프로그램이 XZ를 지원하지 않으면 먼저 압축을 풀어 주세요. 기록 대상 SD의 기존 내용은 지워집니다.

**첫 설치는 부팅 이미지 뒤 검정화면이 보여도 정상입니다. 약 5분 기다리면 SHARE 자동 확장·설정 설치 중 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 전원을 유지한 채 완료될 때까지 기다려 주세요.**

밝기는 **SELECT를 누른 채 볼륨 +/−**, PPSSPP 종료는 **SELECT+START 약 1초**입니다. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하며 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 안에 이름이 `DISABLED`인 빈 파일을 만들면 됩니다.

### 검증 범위와 기술 문서

제작자가 일반·VL·Xtreme Vulkan을 직접 플레이해 화질·성능 향상을 확인했으며 특히 일반 코어의 큰 개선을 보고했습니다. 일반 2.7은 원격으로 게임/데모·메뉴 표시, 해상도 증가에 따른 실제 Vulkan 재초기화 후 방향 유지와 같은 부팅의 정상 ES 복귀를 확인했습니다. VL·Xtreme의 개별 해상도 변경, 2.7의 실제 소리·물리 입력·성능 비교, 최종 이미지의 새 SD 플래싱과 모든 생산분은 추가 시험하지 않았습니다.

- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6/docs/TESTING.ko.md)

보드 구성은 상위 KNULLI의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)을 기반으로 했습니다. 기존 이미지를 수정한 배포판이며 모든 구성요소를 소스에서 완전히 재빌드한 펌웨어는 아닙니다.

압축 해제 IMG: 6,069,178,368바이트. SHA256: fcc87396aa584440d3c93e50ca3b8bec00e5ec2f29219391c2ceaacacd87fb5f.
