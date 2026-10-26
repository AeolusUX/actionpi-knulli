# Action Pi KNULLI v1.0.4

## English

Unofficial KNULLI adaptation for the Helegaly Action Pi. Mali runs the menu and PPSSPP Vulkan in the same boot.

### What changed

- **PPSSPP 1.20.4:** update from 1.19.3 using the official source release and an ARM64 build. PSP games and Emulators → PPSSPP both open the updated Vulkan application.
- **Vulkan/display compatibility:** preserve the existing Mali driver, rotation, output opacity correction and menu return. Add three real Vulkan forwarding exports required by the newer availability check; synchronize both persistent launcher copies.
- **Mixed Korean/English text:** improve fallback font selection for the installed Noto and Nanum families, resolving missing square glyphs in mixed strings.
- Previous Wi-Fi, emulator rotation, Ozone, PortMaster, rumble and brightness shortcut/overlay improvements are retained. No temporary test controllers, captures or personal settings are included.

### Installation

Download this release's .img.xz and SHA256SUMS, verify the checksum and flash the whole SD card. Extract XZ first if required by your flashing tool. Flashing erases the selected card.

**On first installation, a black screen after the boot image is normal. Allow about 5 minutes: SHARE expansion and settings installation may restart the device once or twice before the menu appears. Keep power on until setup finishes.**

Brightness: **hold SELECT + Volume +/−**. Exit PPSSPP: **hold SELECT+START for about one second**. Emulator exit with the top HOME key works in RetroArch and remains disabled in PPSSPP. No game ROMs are included.

### Verification and technical documentation

The owner confirmed PPSSPP 1.20.4 still launches correctly after reboot. On-device captures confirmed correct menu orientation and mixed Korean/English text; normal exit and return to ES without reboot were verified. Earlier title-screen rendering was checked remotely. Every game, performance characteristic and hardware batch was not retested. The newly packaged v1.0.4 SD installation images have not been independently reflashed.

- [History](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/HISTORY.md)
- [Architecture](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/ARCHITECTURE.md)
- [Build and packaging](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/BUILD.md)
- [Published files](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/PUBLIC_FILES.md)
- [Sources and licenses](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/SOURCES_AND_LICENSES.md)
- [Installation](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/RELEASE.md)
- [Verification scope](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/TESTING.md)

Board integration is based on [upstream KNULLI's Action Pi board configuration](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi). This is an adaptation of an inherited image, not a complete from-source firmware build.

Raw IMG: 6,069,178,368 bytes. SHA256: 3b7595a3d131cee45473e8c448279cc530acfe2412ab148a13653d50d256c916.

---

## 한국어

Helegaly Action Pi용 비공식 KNULLI 수정 배포판입니다. 같은 부팅에서 Mali 메뉴와 PPSSPP Vulkan을 사용합니다.

### 수정 내역

- **PPSSPP 1.20.4 업데이트:** 공식 소스로 ARM64 빌드해 1.19.3에서 올렸습니다. PSP 게임과 Emulators → PPSSPP 단독 실행 모두 새 Vulkan 버전으로 연결됩니다.
- **Vulkan·화면 호환 보완:** 기존 Mali 드라이버·회전·출력 투명도 보정·메뉴 복귀는 유지하고, 새 버전의 초기 검사에 필요한 Vulkan 함수 전달 3개를 추가했습니다. 부팅용 런처 두 사본도 동기화했습니다.
- **한영 혼합 글꼴 수정:** 설치된 Noto·나눔 글꼴을 올바르게 선택하도록 보완해 혼합 문장의 네모 글자를 해결했습니다.
- 기존 Wi-Fi·에뮬레이터 회전·Ozone·PortMaster·진동·밝기 단축키와 게이지 보정은 유지합니다. 임시 시험 제어 프로그램·캡처·개인 설정은 포함하지 않습니다.

### 설치

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 굽습니다. 기록 프로그램이 XZ를 지원하지 않으면 먼저 압축을 풀어 주세요. 기록 대상 SD의 기존 내용은 지워집니다.

**첫 설치는 부팅 이미지 뒤 검정화면이 보여도 정상입니다. 약 5분 기다리면 SHARE 자동 확장·설정 설치 중 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 전원을 유지한 채 완료될 때까지 기다려 주세요.**

밝기는 **SELECT를 누른 채 볼륨 +/−**, PPSSPP 종료는 **SELECT+START 약 1초**입니다. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하며 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다.

### 검증 범위와 기술 문서

사용자가 재부팅 후에도 PPSSPP 1.20.4가 정상 실행되는 것을 확인했습니다. 실기 캡처에서 메뉴 방향·한영 혼합 글꼴을 확인했고, 정상 종료와 재부팅 없는 ES 복귀를 확인했습니다. 앞선 시험에서 게임 타이틀 출력도 원격으로 확인했습니다. 모든 게임의 성능·동작과 모든 생산분을 다시 시험한 것은 아닙니다. 새로 패키징한 v1.0.4 설치 IMG를 별도 SD에 다시 굽는 시험은 반복하지 않았습니다.

- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4/docs/TESTING.ko.md)

보드 구성은 상위 KNULLI의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)을 기반으로 했습니다. 기존 이미지를 수정한 배포판이며 모든 구성요소를 소스에서 완전히 재빌드한 펌웨어는 아닙니다.

압축 해제 IMG: 6,069,178,368바이트. SHA256: 3b7595a3d131cee45473e8c448279cc530acfe2412ab148a13653d50d256c916.
