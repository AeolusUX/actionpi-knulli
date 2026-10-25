# Action Pi KNULLI v1.0.2

> **[한국 사용자용 CRC 무시 코어 적용판 다운로드](https://github.com/pikachu220v/actionpi-knulli/releases/tag/v1.0.2-crc-ko)** · [일반판 다운로드](https://github.com/pikachu220v/actionpi-knulli/releases/tag/v1.0.2)

## English

Unofficial KNULLI adaptation for the Helegaly Action Pi. Mali runs the menu and PPSSPP Vulkan in the same boot.

### What changed in v1.0.2

- **RetroArch Ozone restored:** ordinary cores and standalone RetroArch now use GL/gl_sdl rather than forced SDL2 video, with Ozone selected for those sessions.
- **Rotation retained:** a small, scoped GLES3-context helper lets the existing full-frame adapter rotate both gameplay and Ozone. Existing hardware-core output settings and other applications are retained.
- **Menu startup fixed:** synchronize the menu guard's expected normal BOOT hash and its manifest with the Wi-Fi recovery BOOT. This fixes the stale check that could reject menu startup and trigger recovery. The safety check remains enabled.
- Retain the cumulative Wi-Fi reboot/startup fixes, emulator/SDLPoP/OD-Commander orientation, PortMaster runtime-list fixes, Mali menu and PPSSPP Vulkan.

Use v1.0.2 instead of v1.0.1: the earlier image retained a stale menu BOOT check. All cumulative Wi-Fi, orientation and PortMaster fixes are included here.

### Installation

Download the `.img.xz` asset and matching `SHA256SUMS`, verify the checksum, and write the image to the whole SD card. Extract XZ first if the flashing application requires it. Writing the card erases its existing contents.

**On first installation, a black screen after the boot image is normal. Allow about 5 minutes: SHARE expansion and settings installation may automatically restart the device once or twice before the menu appears. Keep power on and wait for setup to finish.** Later game launches and exits do not require rebooting.

PPSSPP exits with **SELECT+START held for about one second**. Emulator exit using the top HOME key works in RetroArch and is disabled in PPSSPP. Emulators → PPSSPP opens the same Vulkan application without a ROM. No game ROMs are included.

### Verification and technical details

The final runtime changes reached a healthy Mali menu after the home-device SSH update. Wi-Fi reconnected, and ordinary-core/standalone RetroArch checks completed. The owner then confirmed all final changes working on 2026-10-25. This newly packaged public IMG was not independently downloaded and reflashed; not every core, game, port or board variant was retested. [Verification scope](../docs/TESTING.md).

The adaptation aligns the rebuilt Mali module, vendor userspace/Vulkan registration and SDL launch environment; applies guarded display cleanup and scoped output/brightness fixes; and supervises menu/PPSSPP transitions. This update adds a scoped GLES3 request for Ozone and completes the BOOT reference chain. Existing provenance limitations remain documented.

- [Development history](../docs/HISTORY.md)
- [Runtime architecture](../docs/ARCHITECTURE.md)
- [Build and packaging](../docs/BUILD.md)
- [Published files](../docs/PUBLIC_FILES.md)
- [Sources and licenses](../docs/SOURCES_AND_LICENSES.md)
- [Installation guide](../docs/RELEASE.md)

Board integration is based on upstream KNULLI's [Action Pi board configuration](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi). This is a modification of an inherited image, not a complete from-source firmware rebuild.

Raw IMG: 6,069,178,368 bytes. SHA256: `18cfbf89a81dd4245caee0d557e8b12bf00c8627e01d81b7b2ac28b210143cc9`. Verify the compressed download using `SHA256SUMS`.

---

## 한국어

Helegaly Action Pi용 비공식 KNULLI 수정 배포판입니다. 같은 부팅에서 Mali 메뉴와 PPSSPP Vulkan을 실행합니다.

### v1.0.2 수정 내역

- **RetroArch Ozone 복원:** 일반 코어와 단독 RetroArch를 강제 SDL2 출력 대신 GL/gl_sdl로 실행하고 해당 실행에 Ozone을 지정했습니다.
- **회전 보정 유지:** 해당 RetroArch 실행에만 GLES3 컨텍스트 보조 파일을 연결해 게임과 Ozone 메뉴를 기존 전체 프레임 회전 경로로 표시합니다. 기존 하드웨어 코어 출력 설정과 다른 앱은 유지했습니다.
- **메뉴 시작 오류 수정:** 메뉴 guard의 normal BOOT 기대값과 해당 manifest를 Wi-Fi 복원 BOOT에 맞췄습니다. 옛 검사값 때문에 메뉴 시작을 거부하고 복구 부팅으로 넘어갈 수 있던 문제를 고쳤으며 안전 검사 자체는 유지했습니다.
- 재부팅 후 Wi-Fi·시작 순서, 에뮬레이터·SDLPoP·OD-Commander 방향, PortMaster 런타임 목록 처리, Mali 메뉴·PPSSPP Vulkan 등 누적 수정도 유지했습니다.

v1.0.1에는 옛 메뉴 BOOT 검사값이 남아 있었으므로 v1.0.2를 사용해 주세요. 기존 Wi-Fi·화면 방향·PortMaster 수정도 모두 포함합니다.

### 설치 안내

`.img.xz`와 같은 릴리스의 `SHA256SUMS`를 내려받아 체크섬을 확인하고 SD 카드 전체에 기록합니다. 굽기 프로그램이 XZ를 지원하지 않으면 먼저 압축을 풀어 주세요. 기록 대상 SD의 기존 내용은 지워집니다.

**첫 설치 시 부팅 이미지 이후 검정화면만 보여도 정상적인 설치 과정이니 걱정하지 않으셔도 됩니다. 약 5분 기다리면 SHARE 자동 확장과 설정 설치 중 한두 차례 자동 재부팅한 뒤 메뉴가 표시됩니다. 전원을 끄지 말고 완료될 때까지 기다려 주세요.** 이후 일반적인 게임 실행·종료마다 재부팅할 필요는 없습니다.

PPSSPP 종료는 **SELECT+START를 약 1초간 함께 누르면** 됩니다. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하며 PPSSPP에서는 비활성화되어 있습니다. Emulators → PPSSPP에서도 게임 파일 없이 같은 Vulkan 앱을 엽니다. 게임 ROM은 포함하지 않습니다.

### 검증과 기술 문서

집 실기에 SSH로 최종 수정을 적용한 뒤 Mali 메뉴의 정상 시작과 재부팅 후 Wi-Fi 재연결을 확인했습니다. 일반 코어·단독 RetroArch 실행 검사 후, 2026년 10월 25일 사용자가 최종 수정 전체의 정상 작동을 확인했습니다. 새로 패키징한 공개 IMG를 게시 후 다시 내려받아 굽는 시험은 별도로 반복하지 않았으며, 모든 코어·게임·포트·보드 변형을 전부 재시험한 것은 아닙니다. [검증 범위](../docs/TESTING.ko.md).

Mali 모듈 재빌드, 사용자 공간 라이브러리·Vulkan 등록·SDL 실행 환경 연결, 보호 조건이 있는 화면 정리 수정, 회전·밝기 보정, 메뉴와 PPSSPP의 화면 사용권 전환을 적용한 구성입니다. 이번에는 Ozone용 GLES3 요청과 메뉴 검사값까지 BOOT 참조 연결을 보완했습니다. 소스·출처 확인이 남은 부분은 문서에 구분했습니다.

- [작업 이력](../docs/HISTORY.ko.md)
- [작동 구조](../docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](../docs/BUILD.ko.md)
- [공개 파일 목록](../docs/PUBLIC_FILES.ko.md)
- [소스·라이선스](../docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](../docs/RELEASE.ko.md)

보드 구성은 상위 KNULLI의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)을 기반으로 했습니다. 기존 이미지를 수정한 배포판이며 전체 펌웨어를 처음부터 재빌드할 수 있다고 주장하지 않습니다.

압축 해제 IMG: 6,069,178,368바이트. SHA256: `18cfbf89a81dd4245caee0d557e8b12bf00c8627e01d81b7b2ac28b210143cc9`. 압축 파일은 `SHA256SUMS`로 확인해 주세요.
