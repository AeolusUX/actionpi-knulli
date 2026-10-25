# Action Pi KNULLI v1.0.1

## English

Unofficial KNULLI adaptation for the Helegaly Action Pi, with a Mali-based menu
and PPSSPP Vulkan running on the same boot.

### What changed in v1.0.1

- **Wi-Fi after reboot:** retain the existing AIC support and add the stock RTL8723DS path. The active BOOT and the normal/recovery BOOT used by Mali now contain the same Wi-Fi loader and startup code. Their integrity hashes are updated together, preventing the old AIC-only loader from returning on the next boot.
- **Wi-Fi startup:** wait for persistent SHARE settings and a driver-bound radio, then use the current settings. Correct the readiness marker to `/var/run/knulli.share.mounted`. Automatically started workers preserve already active Wi-Fi and existing ConnMan services.
- **Emulator orientation:** extend direction/size correction to standalone RetroArch, N64/Mupen64Plus, Saturn/YabaSanshiro and OpenBOR. The maintainer confirmed all emulator screen directions on hardware. Align the hardware N64/Saturn RetroArch launch paths with their GLES backends rather than the incompatible forced SDL2 route.
- **Other screens:** correct SDLPoP and OD-Commander, and apply scoped rotation to supported SDL/GLES PortMaster games. Compatibility with every individual port is not claimed.
- **PortMaster menus:** fix crashes caused by runtime metadata being a list rather than a single string, including runtime-manager display, port information, requirements and download-size calculation paths. Handle both `pylibs.zip` and already extracted installed sources; apply the correction when PortMaster is launched after installation.
- Keep the existing Mali menu, PPSSPP Vulkan, settings persistence, input, brightness and suspend/resume improvements.

On 2026-10-25, device-test feedback confirmed Wi-Fi still works after reboot with the test8 firmware. This public release promotes the normal test8 image **without changing its IMG bytes**. Emulator orientation was confirmed on hardware by the maintainer. PortMaster runtime-manager and port-management screens were also confirmed; every game, full update, forced update, runtime download and future PortMaster version was not exhaustively retested. See [verification scope](../docs/TESTING.md).

### Features

- Launch PSP games and return to the menu without rebooting.
- ES **Emulators → PPSSPP** opens the same Vulkan application without a game file.
- Correct screen direction and size for the menu, PPSSPP, RetroArch, Flycast and
  PortMaster; PortMaster installer included.
- Persistent brightness direction and held adjustment, saved preferences,
  suspend/wake with Wi-Fi reconnection, and audio improvements.
- No game ROMs included. Legacy restore-menu and PPSSPP test Ports entries removed.
- Hold **SELECT+START for about one second** to exit PPSSPP and return to the menu.
  Emulator exit using the top HOME key works in RetroArch and is disabled in PPSSPP.

### Installation and first boot

Download the `.img.xz` asset and verify its matching `SHA256SUMS`. Extract it if
your flashing application does not accept XZ, then write the image to the whole
SD card.

**On first installation, a black screen after the boot image is normal. Allow
about 5 minutes: the device will automatically restart once or twice while
expanding SHARE and installing settings, then show the menu. There is no need to
worry; keep the power on and wait for setup to finish.** Normal game launches and
exits do not require a reboot.

### Technical implementation and published files

The adaptation rebuilds the Mali module against a reviewed public kernel
candidate, applies a guarded repair to the existing kernel's display-client
cleanup, and aligns the Mali userspace libraries, Vulkan ICD registration, SDL
and launch environment. A supervisor keeps Mali active while coordinating menu
and PPSSPP sessions. Scoped adapters correct output rotation, logical dimensions
and the alpha/blending mismatch; boot and resume hooks normalize hardware PWM
polarity for brightness.

Runtime scripts, adapter source, pinned Mali source, recovered kernel options,
display repair code and historical image-packaging tools are published here.
The packaging documentation explains how settings are prepared, the existing
root filesystem is retained, deleted FAT data is scrubbed, and image/component
checksums are recorded.

- [Development history and reasons for the fixes](../docs/HISTORY.md)
- [Runtime architecture and integration](../docs/ARCHITECTURE.md)
- [Build inputs and image-packaging process](../docs/BUILD.md)
- [Published file inventory](../docs/PUBLIC_FILES.md)
- [Sources, licenses and unresolved provenance](../docs/SOURCES_AND_LICENSES.md)

This modifies and packages an existing KNULLI image. The KNULLI board-integration base is the upstream [Action Pi board configuration](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)
on `knulli-main` (`board/allwinner/a527/helegany-action-pi`).
The exact original vendor kernel source and some inherited binary provenance
remain unresolved, so this
repository does not provide a complete from-source firmware rebuild. The core
functions, PortMaster correction and standalone PPSSPP routing were confirmed on
hardware. For v1.0.1, the maintainer confirmed all emulator screen directions on hardware,
and test8 device feedback confirmed Wi-Fi after reboot on 2026-10-25. The public
normal-edition IMG is byte-identical to its test8 source; this is not a separate
post-publication download-and-reflash test.
See [test coverage](../docs/TESTING.md).

Raw IMG size: 6,069,178,368 bytes. Raw IMG SHA256:
`b5d2193e0b88808c7457d8d714d422f8b927630e06bac432bf8067ea31377c42`.
Use `SHA256SUMS` to verify the compressed download before extracting/flashing.
[Detailed installation guide](../docs/RELEASE.md)

---

## 한국어

Helegaly Action Pi용 비공식 KNULLI 수정 배포판입니다. Mali 기반 메뉴와 PPSSPP
Vulkan을 같은 부팅 상태에서 사용하도록 구성했습니다.

### v1.0.1 수정 내역

- **재부팅 후 Wi-Fi 검색·연결 문제 수정:** 기존 AIC 지원을 유지하면서 순정 RTL8723DS 드라이버 시작 경로를 추가했습니다. 실제 부팅 파일과 Mali가 재부팅·복원에 사용하는 기준 사본을 함께 갱신하고 검증 해시도 맞춰, 다음 부팅에서 옛 AIC 전용 로더로 돌아가던 문제를 고쳤습니다.
- **Wi-Fi 시작 순서 보완:** SHARE 저장 공간과 무선 장치가 준비된 뒤 최신 설정으로 시작하며, 준비 마커 경로를 실제 생성 위치인 `/var/run/knulli.share.mounted`로 바로잡았습니다. 자동 시작 과정은 이미 사용 중인 Wi-Fi와 기존 ConnMan을 강제로 끄거나 재시작하지 않습니다.
- **에뮬레이터 화면 방향·크기 수정:** 스탠드얼론 RetroArch, N64/Mupen64Plus, Saturn/YabaSanshiro, OpenBOR까지 보정 범위를 확장했습니다. 에뮬레이터 화면 방향은 제작자가 실기로 모두 확인했습니다. N64·Saturn의 하드웨어 RetroArch 코어 실행도 강제 SDL2 대신 실제 GLES 백엔드와 맞추도록 보완했습니다.
- **도구·포트 게임 화면 보정:** SDLPoP와 OD-Commander 방향을 수정하고, 지원되는 SDL/GLES 경로의 PortMaster 게임에도 회전 보정을 연결했습니다. 모든 개별 포트 게임의 호환을 보장한다는 뜻은 아닙니다.
- **PortMaster 메뉴 종료 오류 수정:** 런타임 정보가 문자열 대신 목록으로 들어올 때 발생하던 오류를 수정했습니다. 런타임 매니저 표시, 포트 정보·요구 조건, 다운로드 용량 계산 경로를 보완하고, 압축된 `pylibs.zip`과 이미 풀린 설치 소스를 모두 처리합니다. Install PortMaster로 설치한 뒤 실행할 때 보완이 적용됩니다.
- 기존 Mali 메뉴·PPSSPP Vulkan·설정 저장·조작·밝기·절전 복귀 수정은 유지했습니다.

2026년 10월 25일 test8 펌웨어에서 **재부팅 후에도 Wi-Fi가 정상 연결됨을 실기 후기와 사진으로 확인**했습니다. 공개판은 test8 일반판의 **IMG 내용을 바꾸지 않고** 정식 버전으로 승격했습니다. 에뮬레이터 방향은 제작자가 실기로 모두 확인했고, PortMaster 런타임 매니저와 포트 관리 화면도 실기로 확인했습니다. 모든 게임, 전체·강제 업데이트, 런타임 다운로드 및 향후 모든 PortMaster 버전을 전부 재시험한 것은 아닙니다. [검증 범위](../docs/TESTING.ko.md)

### 주요 기능

- 재부팅 없이 PSP 게임 실행 → 종료 → 메뉴 복귀가 가능합니다.
- ES의 **Emulators → PPSSPP**에서도 게임 파일 없이 같은 Vulkan용 PPSSPP가 실행됩니다.
- 메뉴, PPSSPP, RetroArch, Flycast, PortMaster의 화면 방향과 크기를 보정했습니다.
  PortMaster 설치 항목도 포함합니다.
- 밝기 방향과 길게 눌러 연속 조절, 사용자 설정 유지, 절전·복귀와 Wi-Fi 재연결,
  오디오 개선을 적용했습니다.
- 게임 ROM은 포함하지 않습니다. 이전 메뉴 복원 및 PPSSPP 시험용 Ports 항목은 제거했습니다.
- PPSSPP 종료는 **SELECT+START를 약 1초간 함께 누르면** 메뉴로 돌아옵니다.
  상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하며 PPSSPP에서는 비활성화되어 있습니다.

### 설치와 첫 부팅

`.img.xz` 파일을 내려받고 함께 제공되는 `SHA256SUMS`로 체크섬을 확인해 주세요.
굽기 프로그램이 XZ를 지원하지 않으면 먼저 압축을 해제한 뒤 SD 카드 전체에 이미지를
기록하면 됩니다.

**첫 설치 시 부팅 이미지 이후 검정화면만 보여도 정상적인 설치 과정이니 걱정하지
않으셔도 됩니다. 약 5분 기다리면 SHARE 자동 확장과 설정 설치 중 한두 차례 자동으로
재부팅한 뒤 메뉴가 표시됩니다. 전원을 끄지 말고 설치가 끝날 때까지 기다려 주세요.**
이후 일반적인 게임 실행·종료마다 재부팅할 필요는 없습니다.

### 기술적 적용 내용과 공개 파일

검토한 공개 커널 후보를 바탕으로 Mali 모듈을 재빌드하고, 기존 커널의 화면 클라이언트
정리 코드에는 원본을 확인하는 보호 조건을 둔 수정을 적용했습니다. Mali 사용자 공간
라이브러리, Vulkan ICD 등록, SDL과 실행 환경을 맞추고, Mali를 유지한 채 메뉴와
PPSSPP를 전환하는 관리 프로그램을 연결했습니다. 각 실행 경로에 화면 회전·논리 해상도·
투명도와 블렌딩 불일치 보정을 적용했으며, 부팅과 절전 복귀 시 실제 PWM 신호 방향을
맞춰 밝기 방향이 유지되도록 했습니다.

실행 스크립트, 화면 보정 소스, 사용한 Mali 소스, 복구한 커널 설정, 화면 정리 수정 코드와
당시의 이미지 제작 도구를 공개했습니다. 설정 준비, 기존 루트 파일시스템 유지,
삭제된 FAT 데이터 정리, 이미지와 구성 파일의 체크섬 기록 과정도 문서화했습니다.
아래 링크는 한국어 기술 문서로 연결됩니다. 각 문서 상단에서 영문판으로도 이동할 수 있습니다.

- [작업 히스토리와 각 수정의 이유](../docs/HISTORY.ko.md)
- [작동 구조와 연결 방식](../docs/ARCHITECTURE.ko.md)
- [빌드에 사용한 구성과 이미지 제작 과정](../docs/BUILD.ko.md)
- [공개 파일 목록](../docs/PUBLIC_FILES.ko.md)
- [소스·라이선스와 출처 확인이 남은 부분](../docs/SOURCES_AND_LICENSES.ko.md)

기존 KNULLI 이미지를 수정·패키징한 배포판입니다. KNULLI 보드 구성은 상위 프로젝트의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)을
기반으로 했습니다. 경로는 `knulli-main`의 `board/allwinner/a527/helegany-action-pi`입니다.
다만 원본 제조사 커널의 정확한 소스와 일부 기존 바이너리의 출처는 아직 확인되지 않아,
이 저장소만으로 펌웨어 전체를
처음부터 빌드할 수 있는 상태는 아닙니다. 기본 기능, PortMaster 보정과 PPSSPP
단독 실행 연결은 실기에서 확인했습니다. v1.0.1에서는 에뮬레이터 방향을 제작자가 실기로 모두 확인했고,
2026년 10월 25일 test8 재부팅 후 Wi-Fi 정상 연결도 확인했습니다. 공개 일반판 IMG는
test8 원본과 동일하며, 게시 후 다운로드·재설치를 별도로 반복했다는 뜻은 아닙니다. [검증 범위](../docs/TESTING.ko.md)

압축 해제한 IMG 크기: 6,069,178,368바이트. IMG SHA256:
`b5d2193e0b88808c7457d8d714d422f8b927630e06bac432bf8067ea31377c42`.
압축 파일은 압축 해제·기록 전에 `SHA256SUMS`로 확인해 주세요.
[자세한 설치 안내](../docs/RELEASE.ko.md)
