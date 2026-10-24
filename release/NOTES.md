# v119 Distribution Edition r2

## English

Unofficial KNULLI adaptation for the Helegany Action Pi, with a Mali-based menu
and PPSSPP Vulkan running on the same boot.

### Features

- Launch PSP games and return to the menu without rebooting.
- ES **Emulators → PPSSPP** opens the same Vulkan application without a game file.
- Correct screen direction and size for the menu, PPSSPP, RetroArch, Flycast and
  PortMaster; PortMaster installer included.
- Persistent brightness direction and held adjustment, saved preferences,
  suspend/wake with Wi-Fi reconnection, and audio improvements.
- No game ROMs included. Legacy restore-menu and PPSSPP test Ports entries removed.
- Hold **SELECT+START for about one second** to exit PPSSPP and return to the menu.
  HOME exit works in RetroArch; it is disabled in PPSSPP.

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

This modifies and packages an existing KNULLI image. The exact original vendor
kernel source and some inherited binary provenance remain unresolved, so this
repository does not provide a complete from-source firmware rebuild. The v119
base, PortMaster correction and standalone PPSSPP routing were confirmed on
hardware; the final public image was checked offline and was not reflashed again.
See [test coverage](../docs/TESTING.md).

Raw IMG size: 6,069,178,368 bytes. Raw IMG SHA256:
`322efb6a52025372ef3c063fc840e6e296b4ff2a93860132a18ac578a4783842`.
Use `SHA256SUMS` to verify the compressed download before extracting/flashing.
[Detailed installation guide](../docs/RELEASE.md)

---

## 한국어

Helegany Action Pi용 비공식 KNULLI 수정 배포판입니다. Mali 기반 메뉴와 PPSSPP
Vulkan을 같은 부팅 상태에서 사용하도록 구성했습니다.

### 주요 기능

- 재부팅 없이 PSP 게임 실행 → 종료 → 메뉴 복귀가 가능합니다.
- ES의 **Emulators → PPSSPP**에서도 게임 파일 없이 같은 Vulkan용 PPSSPP가 실행됩니다.
- 메뉴, PPSSPP, RetroArch, Flycast, PortMaster의 화면 방향과 크기를 보정했습니다.
  PortMaster 설치 항목도 포함합니다.
- 밝기 방향과 길게 눌러 연속 조절, 사용자 설정 유지, 절전·복귀와 Wi-Fi 재연결,
  오디오 개선을 적용했습니다.
- 게임 ROM은 포함하지 않습니다. 이전 메뉴 복원 및 PPSSPP 시험용 Ports 항목은 제거했습니다.
- PPSSPP 종료는 **SELECT+START를 약 1초간 함께 누르면** 메뉴로 돌아옵니다.
  HOME 종료는 RetroArch에서 작동하며 PPSSPP에서는 비활성화되어 있습니다.

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
아래 기술 문서 본문은 영문입니다.

- [작업 히스토리와 각 수정의 이유](../docs/HISTORY.md)
- [작동 구조와 연결 방식](../docs/ARCHITECTURE.md)
- [빌드에 사용한 구성과 이미지 제작 과정](../docs/BUILD.md)
- [공개 파일 목록](../docs/PUBLIC_FILES.md)
- [소스·라이선스와 출처 확인이 남은 부분](../docs/SOURCES_AND_LICENSES.md)

기존 KNULLI 이미지를 수정·패키징한 배포판입니다. 원본 제조사 커널의 정확한 소스와
일부 기존 바이너리의 출처는 아직 확인되지 않아, 이 저장소만으로 펌웨어 전체를
처음부터 빌드할 수 있는 상태는 아닙니다. v119 기반 기능, PortMaster 보정과 PPSSPP
단독 실행 연결은 실기에서 확인했습니다. 최종 배포판 이미지는 오프라인 검증했으며
다시 구워서 확인하지는 않았습니다. [검증 범위](../docs/TESTING.md)

압축 해제한 IMG 크기: 6,069,178,368바이트. IMG SHA256:
`322efb6a52025372ef3c063fc840e6e296b4ff2a93860132a18ac578a4783842`.
압축 파일은 압축 해제·기록 전에 `SHA256SUMS`로 확인해 주세요.
[자세한 설치 안내](../docs/RELEASE.md)
