# Action Pi KNULLI v1.0.3

## English

Unofficial KNULLI adaptation for the Helegaly Action Pi. Mali runs the menu and PPSSPP Vulkan in the same boot.

### What changed

- **Rumble:** use a 25 kHz motor PWM carrier and compensate low-strength effects. Crazy Taxi 1/2 with Flycast VL/Xtreme now provides noticeable small rumble with reduced high-pitched motor-related noise on the tested device.
- **Brightness shortcut:** hold SELECT, then use Volume +/−. Normal volume and HOME behavior are retained; held adjustment works.
- **Brightness overlay:** show a sun icon, percentage and bar above the menu or game, then hide it about 2.2 seconds after adjustment. It uses an unused display plane and runs only while visible; no idle overlay service is added.
- **Background cleanup:** disable KNULLI usage-statistics reporting by default and stop the obsolete repeating boot-log copy on devices carrying it. Omit old diagnostic maps from the image.
- Existing Mali menu/PPSSPP Vulkan, Wi-Fi, screen rotation, Ozone and PortMaster functionality is retained.

### Installation

Download this release's .img.xz and SHA256SUMS, verify the checksum and flash the whole SD card. Extract XZ first if required by your flashing tool. Flashing erases the selected card.

**On first installation, a black screen after the boot image is normal. Allow about 5 minutes: SHARE expansion and settings installation may restart the device once or twice before the menu appears. Keep power on until setup finishes.**

Brightness: **hold SELECT + Volume +/−**. Exit PPSSPP: **hold SELECT+START for about one second**. Emulator exit with the top HOME key works in RetroArch and remains disabled in PPSSPP. No game ROMs are included.

### Verification and technical documentation

On-device tests confirmed rumble strength/noise and persistence after reboot, disabled statistics/repeating logging after reboot, and the brightness shortcut's direction, hold and normal-volume behavior. The owner confirmed the brightness overlay in ES and PPSSPP, automatic hiding, and game exit/menu return; remote inspection confirmed the overlay worker exits. The overlay uses a shared display path, but every emulator and hardware batch was not individually retested. The owner subsequently rebooted the device and confirmed all applied changes still work, including the brightness shortcut and overlay. These newly packaged installation images have not been independently reflashed.

- [History](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/HISTORY.md)
- [Architecture](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/ARCHITECTURE.md)
- [Build and packaging](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/BUILD.md)
- [Published files](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/PUBLIC_FILES.md)
- [Sources and licenses](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/SOURCES_AND_LICENSES.md)
- [Installation](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/RELEASE.md)
- [Verification scope](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/TESTING.md)

Board integration is based on [upstream KNULLI's Action Pi board configuration](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi). This is an adaptation of an inherited image, not a complete from-source firmware build.

Raw IMG: 6,069,178,368 bytes. SHA256: 17b65929b241ce27dbcd147a406f2d7dfa14f017c863219e1ede090656b27df4.

---

## 한국어

Helegaly Action Pi용 비공식 KNULLI 수정 배포판입니다. 같은 부팅에서 Mali 메뉴와 PPSSPP Vulkan을 사용합니다.

### 수정 내역

- **진동 보정:** 모터 PWM을 25kHz로 바꾸고 작은 진동 신호의 세기를 보정했습니다. 시험 기기의 Flycast VL·Xtreme 크레이지택시 1·2에서 작은 진동이 느껴지고 거슬리던 고주파음이 줄어드는 것을 확인했습니다.
- **밝기 단축키:** SELECT를 먼저 누른 채 볼륨 +/−로 조절합니다. 길게 누름을 지원하며 일반 볼륨과 HOME 동작은 유지합니다.
- **밝기 게이지:** 메뉴와 게임 위에 해 아이콘·밝기 %·막대를 표시하고 조작 후 약 2.2초 뒤 숨깁니다. 비어 있는 출력 레이어를 사용하며 표시할 때만 실행하므로 대기 중 상주 서비스가 추가되지 않습니다.
- **백그라운드 정리:** 기본 통계 전송을 끄고, 예전 부팅 로그 반복 복사 작업이 남은 기기에서는 이를 중지합니다. 옛 진단 maps 파일은 이미지에서 제외했습니다.
- 기존 Mali 메뉴·PPSSPP Vulkan·Wi-Fi·화면 회전·Ozone·PortMaster 기능은 유지했습니다.

### 설치

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 굽습니다. 기록 프로그램이 XZ를 지원하지 않으면 먼저 압축을 풀어 주세요. 기록 대상 SD의 기존 내용은 지워집니다.

**첫 설치는 부팅 이미지 뒤 검정화면이 보여도 정상입니다. 약 5분 기다리면 SHARE 자동 확장·설정 설치 중 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 전원을 유지한 채 완료될 때까지 기다려 주세요.**

밝기는 **SELECT를 누른 채 볼륨 +/−**, PPSSPP 종료는 **SELECT+START 약 1초**입니다. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하며 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다.

### 검증 범위와 기술 문서

실기에서 진동 세기·소음과 재부팅 후 유지, 재부팅 후 통계 전송·반복 로그 중지, 밝기 단축키의 방향·길게 누름·일반 볼륨 유지를 확인했습니다. 사용자가 ES와 PPSSPP의 밝기 게이지 표시·자동 숨김·게임 종료·메뉴 복귀를 확인했고, 표시 뒤 작업도 종료되는 것을 원격으로 확인했습니다. 공통 화면 경로를 사용하지만 모든 에뮬레이터·생산분을 각각 재시험한 것은 아닙니다. 이후 사용자가 기기를 재부팅하고 밝기 단축키·게이지를 포함한 수정 사항 전체가 정상 작동한다고 확인했습니다. 새로 패키징한 설치 IMG를 별도 SD에 다시 굽는 시험도 반복하지 않았습니다.

- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3/docs/TESTING.ko.md)

보드 구성은 상위 KNULLI의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)을 기반으로 했습니다. 기존 이미지를 수정한 배포판이며 모든 구성요소를 소스에서 완전히 재빌드한 펌웨어는 아닙니다.

압축 해제 IMG: 6,069,178,368바이트. SHA256: 17b65929b241ce27dbcd147a406f2d7dfa14f017c863219e1ede090656b27df4.
