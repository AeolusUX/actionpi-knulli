# Action Pi Knulli v1.0.8

## English

Unofficial Knulli adaptation for the Helegaly Action Pi. Mali runs the menu and PPSSPP Vulkan in the same boot.

### What changed

- **Yaba Sanshiro standalone updated from 1.9.0 to 1.20.51:** the official engine and frontend are adapted for Linux ARM64/GLES, with the ARM64 JIT enabled and Action Pi rotation retained. The RetroArch Saturn core is unchanged.
- **In-game settings: press L3 (click the left analog stick) to open or close the standalone menu.**
- **Audio crackles corrected:** the realtime sound generator now keeps cumulative deadlines instead of accumulating Linux scheduler delays. This fixes the verified BIOS/game crackles without increasing the audio buffer or changing the output backend.
- **Controls and FPS menu fixed:** game buttons, D-pad and sticks are mapped correctly; the Show/Hide FPS setting works without the previous crash. GLES menu drawing and render-thread initialization are corrected.
- **Trial cleanup:** the latest GLES executable has a permanent launch path. Old trial routes and the failed Saturn Vulkan experiment are excluded from this release.
- Existing Mali, PPSSPP Vulkan, Flycast Vulkan/standard core 2.7, Wi-Fi, rotation, Ozone, PortMaster, brightness, rumble, ZRAM and BennuGD are retained. Saturn standalone uses **GLES**, not Vulkan.

### Installation

Download this release's .img.xz and SHA256SUMS, verify the checksum and flash the whole SD card. Extract XZ first if required by your flashing tool. Flashing erases the selected card.

**On first installation, a black screen after the boot image is normal. Allow about 5 minutes: SHARE expansion and settings installation may restart the device once or twice before the menu appears. Keep power on until setup finishes.**

Saturn standalone settings: **L3 (click the left analog stick)**.

Brightness: **hold SELECT + Volume +/−**. Exit PPSSPP: **hold SELECT+START for about one second**. Emulator exit with the top HOME key works in RetroArch and remains disabled in PPSSPP. No game ROMs are included. ZRAM recovery: create an empty `ACTIONPI_ZRAM/DISABLED` file on BOOT to skip its startup.

### Verification and technical documentation

The user confirmed the latest standalone game buttons, D-pad, sticks, L3 menu and FPS toggle, and reported that BIOS/game crackles disappeared after the final sound timing fix. Measured audio generation/delivery returned close to 44.1 kHz without observed empty-ring samples in the short measurement. The final v1.0.8 images have not been freshly flashed or separately reboot-tested. The earlier Magic Knight Rayearth syllable-repetition issue has not been rechecked after this fix; it is not claimed resolved.

- [History](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/HISTORY.md)
- [Architecture](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/ARCHITECTURE.md)
- [Build and packaging](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/BUILD.md)
- [Published files](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/PUBLIC_FILES.md)
- [Sources and licenses](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/SOURCES_AND_LICENSES.md)
- [Installation](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/RELEASE.md)
- [Verification scope](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/TESTING.md)

Board integration is based on [upstream Knulli's Action Pi board configuration](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi). This is an adaptation of an inherited image, not a complete from-source firmware build.

Raw IMG: 6,069,178,368 bytes. SHA256: 5cbba01b7376845167749183975a72b4e9a1f7c32eb8981660928b0239975365.


Yaba Sanshiro application source and build notes: [src/saturn-standalone](https://github.com/pikachu220v/actionpi-knulli/tree/v1.0.8/src/saturn-standalone); the matching full source archive is attached to this release.

---

## 한국어

Helegaly Action Pi용 비공식 Knulli 수정 배포판입니다. 같은 부팅에서 Mali 메뉴와 PPSSPP Vulkan을 사용합니다.

### 수정 내역

- **야바산시로 스탠드얼론 1.9.0 → 1.20.51 업데이트:** 공식 엔진과 프런트엔드를 Linux ARM64/GLES용으로 적용했습니다. ARM64 JIT와 액션파이 회전 보정을 유지하며 RetroArch 새턴 코어는 변경하지 않았습니다.
- **게임 중 설정 메뉴는 L3(왼쪽 아날로그 스틱 클릭)로 열고 닫습니다.**
- **소리 지직·틱틱 잡음 수정:** 소리 생성 시점을 누적 기준으로 계산하여 Linux 스케줄러의 대기 지연이 계속 쌓이는 문제를 고쳤습니다. 오디오 버퍼 확대나 출력 방식 변경 없이 실기에서 확인된 BIOS·게임 잡음을 해결했습니다.
- **조작과 FPS 메뉴 수정:** 게임 버튼·D패드·스틱 매핑을 적용하고 Show/Hide FPS의 표시·숨김과 충돌 문제를 수정했습니다. GLES 설정 메뉴 그리기와 렌더링 스레드의 초기화도 보완했습니다.
- **시험 파일 정리:** 최신 GLES판을 정식 실행 경로로 연결했습니다. 구형 시험 연결과 실패한 새턴 Vulkan 실험은 배포에 포함하지 않습니다.
- 기존 Mali·PPSSPP Vulkan·Flycast Vulkan/일반 코어 2.7·Wi-Fi·회전·Ozone·PortMaster·밝기·진동·ZRAM·BennuGD는 유지합니다. 새턴 스탠드얼론은 Vulkan이 아닌 **GLES**입니다.

### 설치

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 굽습니다. 기록 프로그램이 XZ를 지원하지 않으면 먼저 압축을 풀어 주세요. 기록 대상 SD의 기존 내용은 지워집니다.

**첫 설치는 부팅 이미지 뒤 검정화면이 보여도 정상입니다. 약 5분 기다리면 SHARE 자동 확장·설정 설치 중 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 전원을 유지한 채 완료될 때까지 기다려 주세요.**

새턴 스탠드얼론 설정 메뉴: **L3(왼쪽 아날로그 스틱 클릭)**.

밝기는 **SELECT를 누른 채 볼륨 +/−**, PPSSPP 종료는 **SELECT+START 약 1초**입니다. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하며 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 안에 이름이 `DISABLED`인 빈 파일을 만들면 됩니다.

### 검증 범위와 기술 문서

사용자가 최신 스탠드얼론의 게임 버튼·D패드·스틱, L3 설정 메뉴와 FPS 표시를 확인했고, 마지막 소리 타이밍 수정 후 BIOS·게임 잡음이 전혀 없어졌다고 확인했습니다. 짧은 측정에서 소리 생성·전달이 44.1kHz에 가까워졌고 버퍼 비움이 관찰되지 않았습니다. 최종 v1.0.8 이미지를 다시 SD에 굽거나 별도로 재부팅하여 확인하지는 않았습니다. 앞서 보고된 마법기사 레이어스의 음절 반복은 이번 수정 뒤 재확인하지 않았으므로 해결됐다고 표기하지 않습니다.

- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8/docs/TESTING.ko.md)

보드 구성은 상위 Knulli의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi)을 기반으로 했습니다. 기존 이미지를 수정한 배포판이며 모든 구성요소를 소스에서 완전히 재빌드한 펌웨어는 아닙니다.

압축 해제 IMG: 6,069,178,368바이트. SHA256: 5cbba01b7376845167749183975a72b4e9a1f7c32eb8981660928b0239975365.


야바산시로 소스·빌드 자료: [src/saturn-standalone](https://github.com/pikachu220v/actionpi-knulli/tree/v1.0.8/src/saturn-standalone). 정확히 대응하는 전체 수정 소스 묶음을 릴리스에 첨부했습니다.
