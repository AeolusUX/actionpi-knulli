# Action Pi용 KNULLI 비공식 개선판

이 저장소는 Action Pi에서 KNULLI 메뉴와 PPSSPP Vulkan을 함께 사용하기 위해
진행한 작업의 소스와 기록입니다. KNULLI 공식 배포판은 아닙니다.

## 다운로드

[Releases](https://github.com/pikachu220v/actionpi-knulli/releases)의
**Action Pi KNULLI v1.0.2**을 사용하세요. `.img.xz`와 체크섬을 제공합니다.
압축 이미지를 지원하지 않는 프로그램에서는 먼저 압축을 풀고 SD 전체에 굽습니다.
선택한 SD의 내용은 지워집니다.

### 한글 패치 아케이드용 별도 다운로드

| 종류 | 선택 |
| --- | --- |
| 기본 배포판 | [일반판 v1.0.2](https://github.com/pikachu220v/actionpi-knulli/releases/tag/v1.0.2) |
| CRC 무시 코어 적용판 | [한국 사용자용 별도 릴리스](https://github.com/pikachu220v/actionpi-knulli/releases/tag/v1.0.2-crc-ko) · [상세 안내](docs/CRC_KOREAN.ko.md) |

CRC 적용판은 FBNeo·MAME2003 Plus와 재부팅 자동 적용을 추가한 변형입니다. 두 판의 체크섬이 다릅니다.

**첫 설치 시 부팅 이미지 이후 검정화면만 보여도 정상적인 설치 과정이니 걱정하지
않으셔도 됩니다. 약 5분 기다리면 SHARE 자동 확장과 설정 설치 중 한두 차례 자동으로
재부팅한 뒤 메뉴가 표시됩니다. 전원을 끄지 말고 설치가 끝날 때까지 기다려 주세요.**
일반적인 게임 실행·종료마다 재부팅할 필요는 없습니다.

## 공개 배포판의 초기 상태

- 영어 기본, Wi-Fi 초기 꺼짐. 개인 SSID와 비밀번호를 저장하지 않았습니다.
- 개인적으로 추가한 BIOS 묶음은 제외하고 **기본 시스템 BIOS는 유지**했습니다.
- 게임 ROM은 없습니다. 필요한 추가 BIOS는 SHARE의 `bios`에 직접 넣습니다.
- Ports의 원본 메뉴 복원 항목과 특정 게임을 실행하던 PPSSPP 테스트 항목은 제거했습니다.
- Install.PortMaster는 유지하며, 설치 후 PortMaster 실행 시 방향 보정이 적용됩니다.
- 개인용 이미지와 Wi-Fi 정보는 이 저장소에 올리지 않습니다.

## 주요 수정

Mali가 부팅부터 GPU를 맡도록 구성하고, 메뉴와 PPSSPP 사이의 화면 사용권을
정상적으로 넘겨 같은 부팅에서 실행·종료·메뉴 복귀가 되도록 했습니다.
PPSSPP의 검정화면은 실제 RGB 영상이 있는데 알파가 0인 버퍼와 출력 레이어의
혼합 방식이 맞지 않던 문제를 확인한 뒤 수정했습니다.

메뉴·PPSSPP·RetroArch·Flycast·PortMaster의 화면 방향과 크기, PPSSPP 설정 저장,
D패드, 절전과 Wi-Fi 재연결, 밝기 방향과 길게 누름을 수정했습니다.
밝기는 실제 부팅에 쓰이는 DTB와 하드웨어 신호를 함께 바로잡았으며,
완전 종료 후 시작과 절전 복귀 모두 실기로 확인했습니다.

PPSSPP 종료는 **SELECT+START 약 1초**입니다. 상단의 HOME키를 이용한 에뮬레이터 종료는
RetroArch에서 작동하며 PPSSPP에서는 종료 오류 때문에 비활성화되어 있습니다.
Emulators의 PPSSPP 단독 실행도 게임 파일 없이 같은 Vulkan 메뉴를 엽니다.

## 작업 기록과 공개 범위

[작업 이력](docs/HISTORY.ko.md), [구조](docs/ARCHITECTURE.ko.md),
[공개 파일 목록](docs/PUBLIC_FILES.ko.md), [빌드 방법](docs/BUILD.ko.md),
[시험 범위](docs/TESTING.ko.md), [문제 해결](docs/TROUBLESHOOTING.ko.md)을 함께 제공합니다.

기본 기능과 PortMaster 보정은 실기로 확인했으며 파일·설정·체크섬 검사도 수행했습니다.
2026년 10월 24일 사용자가 공개된 v1.0.0 이미지를 직접 내려받아 SD 카드에 기록하고
실기에 설치한 뒤 정상 작동을 확인했습니다.
KNULLI 보드 구성은 상위 프로젝트의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)을
기반으로 했습니다. 경로는 `knulli-main`의 `board/allwinner/a527/helegany-action-pi`입니다.

정확한 원본 커널 소스가 확인되지 않은 부분과 소스 출처가 불완전한 바이너리는
[출처·라이선스 문서](docs/SOURCES_AND_LICENSES.ko.md)에 구분했습니다.
모든 구성요소를 이 저장소만으로 완전히 재빌드할 수 있다고 주장하지 않습니다.

## v1.0.1 변경 사항

AIC·RTL8723DS Wi-Fi 지원과 재부팅 후 연결, 에뮬레이터·도구·지원되는 포트 게임의 회전 보정, PortMaster 런타임 메뉴 오류를 수정했습니다. 에뮬레이터 방향은 제작자가 실기로 모두 확인했고, test8의 재부팅 후 Wi-Fi 연결도 실기 후기로 확인했습니다. 공개판 IMG는 test8 일반판과 동일합니다. [전체 수정 내역](CHANGELOG.md).

## v1.0.2 변경 사항

- **RetroArch Ozone 복원:** 일반 코어와 단독 RetroArch를 강제 SDL2 출력 대신 GL/gl_sdl로 실행하고 해당 실행에 Ozone을 지정했습니다.
- **회전 보정 유지:** 해당 RetroArch 실행에만 GLES3 컨텍스트 보조 파일을 연결해 게임과 Ozone 메뉴를 기존 전체 프레임 회전 경로로 표시합니다. 기존 하드웨어 코어 출력 설정과 다른 앱은 유지했습니다.
- **메뉴 시작 오류 수정:** 메뉴 guard의 normal BOOT 기대값과 해당 manifest를 Wi-Fi 복원 BOOT에 맞췄습니다. 옛 검사값 때문에 메뉴 시작을 거부하고 복구 부팅으로 넘어갈 수 있던 문제를 고쳤으며 안전 검사 자체는 유지했습니다.
- 재부팅 후 Wi-Fi·시작 순서, 에뮬레이터·SDLPoP·OD-Commander 방향, PortMaster 런타임 목록 처리, Mali 메뉴·PPSSPP Vulkan 등 누적 수정도 유지했습니다.

집 실기에 SSH로 최종 수정을 적용한 뒤 Mali 메뉴의 정상 시작과 재부팅 후 Wi-Fi 재연결을 확인했습니다. 일반 코어·단독 RetroArch 실행 검사 후, 2026년 10월 25일 사용자가 최종 수정 전체의 정상 작동을 확인했습니다. 새로 패키징한 공개 IMG를 게시 후 다시 내려받아 굽는 시험은 별도로 반복하지 않았으며, 모든 코어·게임·포트·보드 변형을 전부 재시험한 것은 아닙니다. [전체 수정 내역](release/NOTES.md).
