# Release and development milestones

These are curated milestones, not a fabricated historical Git commit log.
Development checkpoint numbers are internal, not upstream KNULLI versions.
Public release numbering starts at **v1.0.0**.

| Checkpoint | Outcome |
| --- | --- |
| v87 baseline | Known bootable starting point; preserve it while testing Wi-Fi |
| v92–v114 experiments | Boot failures/freezes and incorrect Wi-Fi assumptions; not release recommendations |
| v115 | Personal stable checkpoint with working Wi-Fi, audio and RetroArch |
| v116, 2026-10-22 | Guarded display-client cleanup kernel repair; later Mali/Vulkan and presentation trials |
| 2026-10-23 integration | Correct scanout opacity/rotation, input, persistent settings; Mali menu and same-boot PSP round trips |
| v117 / v118 | Withdrawn because brightness inversion/polarity handling was incomplete |
| v119, 2026-10-24 | Cold boot and suspend/wake brightness correction confirmed; owner confirmed installed stable image |
| v119 Distribution Edition | Public defaults, personal BIOS archive removed, base BIOS retained, private data cleanup; PortMaster rotation added |
| v119 Distribution r2 / personal v120 r2 | ES Emulators/PPSSPP standalone entry routed through the existing Vulkan supervisor; no ROM required; owner confirmed output and menu return |
| Personal v120 | Private successor to personal v119, including BIOS/settings and PortMaster fix; not a public asset |

## First public release: v1.0.0 — 2026-10-24

Public v1.0.0 is the unchanged image previously labeled internally as
v119 Distribution Edition r2. The release title, tag, filenames and documentation
now use v1.0.0; the IMG and XZ bytes and their SHA256 values are unchanged.
The owner downloaded the published image, wrote it to an SD card and confirmed
installation and normal operation. Personal v120 remains unchanged and private.
Historical checkpoint names, runtime paths and packaging tools retain their
original identifiers so they still describe the actual work.

## v1.0.1 — 2026-10-25

- **Wi-Fi after reboot:** retain the existing AIC support and add the stock RTL8723DS path. The active BOOT and the normal/recovery BOOT used by Mali now contain the same Wi-Fi loader and startup code. Their integrity hashes are updated together, preventing the old AIC-only loader from returning on the next boot.
- **Wi-Fi startup:** wait for persistent SHARE settings and a driver-bound radio, then use the current settings. Correct the readiness marker to `/var/run/knulli.share.mounted`. Automatically started workers preserve already active Wi-Fi and existing ConnMan services.
- **Emulator orientation:** extend direction/size correction to standalone RetroArch, N64/Mupen64Plus, Saturn/YabaSanshiro and OpenBOR. The maintainer confirmed all emulator screen directions on hardware. Align the hardware N64/Saturn RetroArch launch paths with their GLES backends rather than the incompatible forced SDL2 route.
- **Other screens:** correct SDLPoP and OD-Commander, and apply scoped rotation to supported SDL/GLES PortMaster games. Compatibility with every individual port is not claimed.
- **PortMaster menus:** fix crashes caused by runtime metadata being a list rather than a single string, including runtime-manager display, port information, requirements and download-size calculation paths. Handle both `pylibs.zip` and already extracted installed sources; apply the correction when PortMaster is launched after installation.
- Keep the existing Mali menu, PPSSPP Vulkan, settings persistence, input, brightness and suspend/resume improvements.

On 2026-10-25, device-test feedback confirmed Wi-Fi still works after reboot with the test8 firmware. This public release promotes the normal test8 image **without changing its IMG bytes**. Emulator orientation was confirmed on hardware by the maintainer. PortMaster runtime-manager and port-management screens were also confirmed; every game, full update, forced update, runtime download and future PortMaster version was not exhaustively retested. See [verification scope](docs/TESTING.md).

- **재부팅 후 Wi-Fi 검색·연결 문제 수정:** 기존 AIC 지원을 유지하면서 순정 RTL8723DS 드라이버 시작 경로를 추가했습니다. 실제 부팅 파일과 Mali가 재부팅·복원에 사용하는 기준 사본을 함께 갱신하고 검증 해시도 맞춰, 다음 부팅에서 옛 AIC 전용 로더로 돌아가던 문제를 고쳤습니다.
- **Wi-Fi 시작 순서 보완:** SHARE 저장 공간과 무선 장치가 준비된 뒤 최신 설정으로 시작하며, 준비 마커 경로를 실제 생성 위치인 `/var/run/knulli.share.mounted`로 바로잡았습니다. 자동 시작 과정은 이미 사용 중인 Wi-Fi와 기존 ConnMan을 강제로 끄거나 재시작하지 않습니다.
- **에뮬레이터 화면 방향·크기 수정:** 스탠드얼론 RetroArch, N64/Mupen64Plus, Saturn/YabaSanshiro, OpenBOR까지 보정 범위를 확장했습니다. 에뮬레이터 화면 방향은 제작자가 실기로 모두 확인했습니다. N64·Saturn의 하드웨어 RetroArch 코어 실행도 강제 SDL2 대신 실제 GLES 백엔드와 맞추도록 보완했습니다.
- **도구·포트 게임 화면 보정:** SDLPoP와 OD-Commander 방향을 수정하고, 지원되는 SDL/GLES 경로의 PortMaster 게임에도 회전 보정을 연결했습니다. 모든 개별 포트 게임의 호환을 보장한다는 뜻은 아닙니다.
- **PortMaster 메뉴 종료 오류 수정:** 런타임 정보가 문자열 대신 목록으로 들어올 때 발생하던 오류를 수정했습니다. 런타임 매니저 표시, 포트 정보·요구 조건, 다운로드 용량 계산 경로를 보완하고, 압축된 `pylibs.zip`과 이미 풀린 설치 소스를 모두 처리합니다. Install PortMaster로 설치한 뒤 실행할 때 보완이 적용됩니다.
- 기존 Mali 메뉴·PPSSPP Vulkan·설정 저장·조작·밝기·절전 복귀 수정은 유지했습니다.

2026년 10월 25일 test8 펌웨어에서 **재부팅 후에도 Wi-Fi가 정상 연결됨을 실기 후기와 사진으로 확인**했습니다. 공개판은 test8 일반판의 **IMG 내용을 바꾸지 않고** 정식 버전으로 승격했습니다. 에뮬레이터 방향은 제작자가 실기로 모두 확인했고, PortMaster 런타임 매니저와 포트 관리 화면도 실기로 확인했습니다. 모든 게임, 전체·강제 업데이트, 런타임 다운로드 및 향후 모든 PortMaster 버전을 전부 재시험한 것은 아닙니다. [검증 범위](docs/TESTING.ko.md)
