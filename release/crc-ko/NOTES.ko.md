# 한국 사용자용 · CRC 무시 코어 적용판 v1.0.7

한글 패치 아케이드 게임용 FBNeo·MAME2003 Plus CRC 무시 코어가 필요한 분을 위한 별도 배포판입니다. 기본 배포판과 이미지·체크섬을 분리했습니다.

CRC 무시 코어는 **[dsno님 자료](https://dsno.tistory.com/m/)**를 사용했습니다. 이번 버전에서 두 코어 바이너리는 변경하지 않았습니다.

## v1.0.7 수정 내역

- **게임 종료 후 목록 복귀:** PPSSPP·Flycast Vulkan을 종료하면 ES 상위 기종 선택 화면 대신 저장된 해당 기종의 게임 목록으로 돌아갑니다.
- **평소 부팅 설정 유지:** 게임 종료 후 복귀할 때만 임시로 게임 목록을 열며, ES 종료 후 원래 시작 설정을 복원합니다. 비정상 종료된 경우 다음 감독자 시작 때 복원하고 다른 ES 설정은 유지합니다.
- **선택 위치 제한:** 목록은 첫 항목부터 표시하며 종료한 게임의 커서·하위 폴더 위치까지 복원하는 기능은 아닙니다.
- 기존 Mali·PPSSPP Vulkan·Flycast Vulkan/일반 코어 2.7·회전·Wi-Fi·Ozone·PortMaster·진동·밝기·ZRAM·BennuGD 기능은 유지합니다. 일반 Flycast를 우선 권장하지만 게임에 따라 VL이나 Xtreme이 더 유리할 수 있으니 비교해서 선택해 주세요.

코어는 재부팅할 때마다 자동 연결되며 save-overlay는 필요 없습니다. MAME2003 Plus의 mame078plus 이름도 처리합니다.

## 설치와 사용

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 기록합니다. 필요하면 XZ를 먼저 풀어 주세요. 대상 SD의 기존 내용은 지워집니다.

**첫 설치 시 부팅 이미지 이후 검정화면이 보여도 약 5분 기다려 주세요. 자동 확장·설정 적용으로 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 완료될 때까지 전원을 유지하세요.**

밝기: SELECT+볼륨 +/−. PPSSPP 종료: SELECT+START 약 1초. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하고 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 폴더에 `DISABLED`라는 빈 파일을 만들면 됩니다.

## 확인 범위와 출처

실기 ES의 각 게임 목록에서 PSP OutRun 2006과 일반 Flycast Crazy Taxi 2를 실행·정상 종료하고, 재부팅 없이 각각 PSP·Dreamcast 목록으로 돌아오는 것을 캡처로 확인했습니다. 설치 후 재부팅에서는 기존 첫 화면 설정이 유지됐고, 원래 값이 없거나 false인 설정의 복원과 다른 설정 보존을 확인했습니다. VL·Xtreme은 같은 감독 경로를 사용하며 개별 실행과 최종 이미지의 새 SD 플래싱 시험은 반복하지 않았습니다.

제공된 두 코어와 자동 연결은 기존 확인 결과를 유지하며 새 이미지에서 코어 해시 동일성을 확인했습니다. 정확히 일치하는 수정 코어 소스와 CRC 패치는 제공받지 못했으며 상위 소스 링크를 정확한 대응 소스로 주장하지 않습니다.

- [CRC판 상세 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7-crc-ko/docs/CRC_KOREAN.ko.md)
- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7-crc-ko/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7-crc-ko/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7-crc-ko/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7-crc-ko/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7-crc-ko/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7-crc-ko/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.7-crc-ko/docs/TESTING.ko.md)

압축 해제 IMG: 6,069,178,368바이트. SHA256: 5b089f73c611c700a327a5516a120e7dc53f4a215cc977aa3125c33479836388. CRC판 전용 체크섬을 사용하세요.

BennuGD는 별도로 제공받은 코어이며 dsno님 출처 표기는 FBNeo·MAME CRC 무시 코어에만 해당합니다. BennuGD의 정확한 대응 소스·빌드 정보는 제공받지 못했습니다.

Flycast 대응 소스: [일반판의 flycast-v1.0.6-sources.tar](https://github.com/pikachu220v/actionpi-knulli/releases/download/v1.0.7/flycast-v1.0.6-sources.tar). 펌웨어 이미지가 아닌 소스 묶음입니다.
