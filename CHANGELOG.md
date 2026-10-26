# Release and development milestones

These are curated milestones, not a fabricated historical Git commit log.
Development checkpoint numbers are internal, not upstream KNULLI versions.
Public release numbering starts at **v1.0.0**.

## v1.0.3 — 2026-10-26

- **Rumble:** use a 25 kHz motor PWM carrier and compensate low-strength effects. Crazy Taxi 1/2 with Flycast VL/Xtreme now provides noticeable small rumble with reduced high-pitched motor-related noise on the tested device.
- **Brightness shortcut:** hold SELECT, then use Volume +/−. Normal volume and HOME behavior are retained; held adjustment works.
- **Brightness overlay:** show a sun icon, percentage and bar above the menu or game, then hide it about 2.2 seconds after adjustment. It uses an unused display plane and runs only while visible; no idle overlay service is added.
- **Background cleanup:** disable KNULLI usage-statistics reporting by default and stop the obsolete repeating boot-log copy on devices carrying it. Omit old diagnostic maps from the image.
- Existing Mali menu/PPSSPP Vulkan, Wi-Fi, screen rotation, Ozone and PortMaster functionality is retained.

- **진동 보정:** 모터 PWM을 25kHz로 바꾸고 작은 진동 신호의 세기를 보정했습니다. 시험 기기의 Flycast VL·Xtreme 크레이지택시 1·2에서 작은 진동이 느껴지고 거슬리던 고주파음이 줄어드는 것을 확인했습니다.
- **밝기 단축키:** SELECT를 먼저 누른 채 볼륨 +/−로 조절합니다. 길게 누름을 지원하며 일반 볼륨과 HOME 동작은 유지합니다.
- **밝기 게이지:** 메뉴와 게임 위에 해 아이콘·밝기 %·막대를 표시하고 조작 후 약 2.2초 뒤 숨깁니다. 비어 있는 출력 레이어를 사용하며 표시할 때만 실행하므로 대기 중 상주 서비스가 추가되지 않습니다.
- **백그라운드 정리:** 기본 통계 전송을 끄고, 예전 부팅 로그 반복 복사 작업이 남은 기기에서는 이를 중지합니다. 옛 진단 maps 파일은 이미지에서 제외했습니다.
- 기존 Mali 메뉴·PPSSPP Vulkan·Wi-Fi·화면 회전·Ozone·PortMaster 기능은 유지했습니다.

On-device tests confirmed rumble strength/noise and persistence after reboot, disabled statistics/repeating logging after reboot, and the brightness shortcut's direction, hold and normal-volume behavior. The owner confirmed the brightness overlay in ES and PPSSPP, automatic hiding, and game exit/menu return; remote inspection confirmed the overlay worker exits. The overlay uses a shared display path, but every emulator and hardware batch was not individually retested. The owner subsequently rebooted the device and confirmed all applied changes still work, including the brightness shortcut and overlay. These newly packaged installation images have not been independently reflashed.

실기에서 진동 세기·소음과 재부팅 후 유지, 재부팅 후 통계 전송·반복 로그 중지, 밝기 단축키의 방향·길게 누름·일반 볼륨 유지를 확인했습니다. 사용자가 ES와 PPSSPP의 밝기 게이지 표시·자동 숨김·게임 종료·메뉴 복귀를 확인했고, 표시 뒤 작업도 종료되는 것을 원격으로 확인했습니다. 공통 화면 경로를 사용하지만 모든 에뮬레이터·생산분을 각각 재시험한 것은 아닙니다. 이후 사용자가 기기를 재부팅하고 밝기 단축키·게이지를 포함한 수정 사항 전체가 정상 작동한다고 확인했습니다. 새로 패키징한 설치 IMG를 별도 SD에 다시 굽는 시험도 반복하지 않았습니다.

## Optional Korean CRC edition: v1.0.2-crc-ko — 2026-10-25

Separate download for the user-supplied FBNeo/MAME2003 Plus CRC-override cores and the reboot-persistent late loader. The clean base and all v1.0.2 fixes are unchanged. Normal v1.0.2 remains the default/latest release. [Korean guide](docs/CRC_KOREAN.ko.md).

한글 패치 아케이드용 CRC 무시 코어와 재부팅 자동 적용을 넣은 별도 다운로드입니다. 클린 기본 설정과 v1.0.2 수정은 같으며, 기본 최신 릴리스는 일반판 v1.0.2로 유지합니다. [한국어 안내](docs/CRC_KOREAN.ko.md).

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

## v1.0.2 — 2026-10-25

- **RetroArch Ozone restored:** ordinary cores and standalone RetroArch now use GL/gl_sdl rather than forced SDL2 video, with Ozone selected for those sessions.
- **Rotation retained:** a small, scoped GLES3-context helper lets the existing full-frame adapter rotate both gameplay and Ozone. Existing hardware-core output settings and other applications are retained.
- **Menu startup fixed:** synchronize the menu guard's expected normal BOOT hash and its manifest with the Wi-Fi recovery BOOT. This fixes the stale check that could reject menu startup and trigger recovery. The safety check remains enabled.
- Retain the cumulative Wi-Fi reboot/startup fixes, emulator/SDLPoP/OD-Commander orientation, PortMaster runtime-list fixes, Mali menu and PPSSPP Vulkan.

The final runtime changes reached a healthy Mali menu after the home-device SSH update. Wi-Fi reconnected, and ordinary-core/standalone RetroArch checks completed. The owner then confirmed all final changes working on 2026-10-25. This newly packaged public IMG was not independently downloaded and reflashed; not every core, game, port or board variant was retested.

- **RetroArch Ozone 복원:** 일반 코어와 단독 RetroArch를 강제 SDL2 출력 대신 GL/gl_sdl로 실행하고 해당 실행에 Ozone을 지정했습니다.
- **회전 보정 유지:** 해당 RetroArch 실행에만 GLES3 컨텍스트 보조 파일을 연결해 게임과 Ozone 메뉴를 기존 전체 프레임 회전 경로로 표시합니다. 기존 하드웨어 코어 출력 설정과 다른 앱은 유지했습니다.
- **메뉴 시작 오류 수정:** 메뉴 guard의 normal BOOT 기대값과 해당 manifest를 Wi-Fi 복원 BOOT에 맞췄습니다. 옛 검사값 때문에 메뉴 시작을 거부하고 복구 부팅으로 넘어갈 수 있던 문제를 고쳤으며 안전 검사 자체는 유지했습니다.
- 재부팅 후 Wi-Fi·시작 순서, 에뮬레이터·SDLPoP·OD-Commander 방향, PortMaster 런타임 목록 처리, Mali 메뉴·PPSSPP Vulkan 등 누적 수정도 유지했습니다.

집 실기에 SSH로 최종 수정을 적용한 뒤 Mali 메뉴의 정상 시작과 재부팅 후 Wi-Fi 재연결을 확인했습니다. 일반 코어·단독 RetroArch 실행 검사 후, 2026년 10월 25일 사용자가 최종 수정 전체의 정상 작동을 확인했습니다. 새로 패키징한 공개 IMG를 게시 후 다시 내려받아 굽는 시험은 별도로 반복하지 않았으며, 모든 코어·게임·포트·보드 변형을 전부 재시험한 것은 아닙니다.
