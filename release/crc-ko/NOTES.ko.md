# 한국 사용자용 · CRC 무시 코어 적용판 v1.0.8

한글 패치 아케이드 게임용 FBNeo·MAME2003 Plus CRC 무시 코어가 필요한 분을 위한 별도 배포판입니다. 기본 배포판과 이미지·체크섬을 분리했습니다.

CRC 무시 코어는 **[dsno님 자료](https://dsno.tistory.com/m/)**를 사용했습니다. 이번 버전에서 두 코어 바이너리는 변경하지 않았습니다.

## v1.0.8 수정 내역

- **야바산시로 스탠드얼론 1.9.0 → 1.20.51 업데이트:** 공식 엔진과 프런트엔드를 Linux ARM64/GLES용으로 적용했습니다. ARM64 JIT와 액션파이 회전 보정을 유지하며 RetroArch 새턴 코어는 변경하지 않았습니다.
- **게임 중 설정 메뉴는 L3(왼쪽 아날로그 스틱 클릭)로 열고 닫습니다.**
- **소리 지직·틱틱 잡음 수정:** 소리 생성 시점을 누적 기준으로 계산하여 Linux 스케줄러의 대기 지연이 계속 쌓이는 문제를 고쳤습니다. 오디오 버퍼 확대나 출력 방식 변경 없이 실기에서 확인된 BIOS·게임 잡음을 해결했습니다.
- **조작과 FPS 메뉴 수정:** 게임 버튼·D패드·스틱 매핑을 적용하고 Show/Hide FPS의 표시·숨김과 충돌 문제를 수정했습니다. GLES 설정 메뉴 그리기와 렌더링 스레드의 초기화도 보완했습니다.
- **시험 파일 정리:** 최신 GLES판을 정식 실행 경로로 연결했습니다. 구형 시험 연결과 실패한 새턴 Vulkan 실험은 배포에 포함하지 않습니다.
- 기존 Mali·PPSSPP Vulkan·Flycast Vulkan/일반 코어 2.7·Wi-Fi·회전·Ozone·PortMaster·밝기·진동·ZRAM·BennuGD는 유지합니다. 새턴 스탠드얼론은 Vulkan이 아닌 **GLES**입니다.

코어는 재부팅할 때마다 자동 연결되며 save-overlay는 필요 없습니다. MAME2003 Plus의 mame078plus 이름도 처리합니다.

## 설치와 사용

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 기록합니다. 필요하면 XZ를 먼저 풀어 주세요. 대상 SD의 기존 내용은 지워집니다.

**첫 설치 시 부팅 이미지 이후 검정화면이 보여도 약 5분 기다려 주세요. 자동 확장·설정 적용으로 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 완료될 때까지 전원을 유지하세요.**

새턴 스탠드얼론 메뉴: **L3(왼쪽 스틱 클릭)**.

밝기: SELECT+볼륨 +/−. PPSSPP 종료: SELECT+START 약 1초. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하고 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 폴더에 `DISABLED`라는 빈 파일을 만들면 됩니다.

## 확인 범위와 출처

사용자가 최신 스탠드얼론의 게임 버튼·D패드·스틱, L3 설정 메뉴와 FPS 표시를 확인했고, 마지막 소리 타이밍 수정 후 BIOS·게임 잡음이 전혀 없어졌다고 확인했습니다. 짧은 측정에서 소리 생성·전달이 44.1kHz에 가까워졌고 버퍼 비움이 관찰되지 않았습니다. 최종 v1.0.8 이미지를 다시 SD에 굽거나 별도로 재부팅하여 확인하지는 않았습니다. 앞서 보고된 마법기사 레이어스의 음절 반복은 이번 수정 뒤 재확인하지 않았으므로 해결됐다고 표기하지 않습니다.

제공된 두 코어와 자동 연결은 기존 확인 결과를 유지하며 새 이미지에서 코어 해시 동일성을 확인했습니다. 정확히 일치하는 수정 코어 소스와 CRC 패치는 제공받지 못했으며 상위 소스 링크를 정확한 대응 소스로 주장하지 않습니다.

- [CRC판 상세 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8-crc-ko/docs/CRC_KOREAN.ko.md)
- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8-crc-ko/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8-crc-ko/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8-crc-ko/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8-crc-ko/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8-crc-ko/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8-crc-ko/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.8-crc-ko/docs/TESTING.ko.md)

압축 해제 IMG: 6,069,178,368바이트. SHA256: b4ab37a9d37627dabcb6aa9635a6f8256208b804ee8b447118dd5cddf0ddf63d. CRC판 전용 체크섬을 사용하세요.

BennuGD는 별도로 제공받은 코어이며 dsno님 출처 표기는 FBNeo·MAME CRC 무시 코어에만 해당합니다. BennuGD의 정확한 대응 소스·빌드 정보는 제공받지 못했습니다.

Flycast 대응 소스: [일반판의 flycast-v1.0.6-sources.tar](https://github.com/pikachu220v/actionpi-knulli/releases/download/v1.0.8/flycast-v1.0.6-sources.tar). 펌웨어 이미지가 아닌 소스 묶음입니다.


야바산시로 소스·빌드 자료: [src/saturn-standalone](https://github.com/pikachu220v/actionpi-knulli/tree/v1.0.8/src/saturn-standalone). 정확히 대응하는 전체 수정 소스 묶음을 릴리스에 첨부했습니다.
