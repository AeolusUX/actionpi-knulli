# 한국 사용자용 · CRC 무시 코어 적용판 v1.0.5

한글 패치 아케이드 게임용 FBNeo·MAME2003 Plus CRC 무시 코어가 필요한 분을 위한 별도 배포판입니다. 기본 배포판과 이미지·체크섬을 분리했습니다.

CRC 무시 코어는 **[dsno님 자료](https://dsno.tistory.com/m/)**를 사용했습니다. 이번 버전에서 두 코어 바이너리는 변경하지 않았습니다.

## v1.0.5 수정 내역

- **ZRAM 서비스 수정:** 서비스 메뉴에서 현재 커널에 맞춘 모듈을 켜고 끌 수 있으며 재부팅 후에도 선택이 유지됩니다. **기본값은 꺼짐**입니다. 메뉴 준비 후 lzo-rle로 시작하며 논리 스왑은 감지한 RAM의 절반, 실제 압축 RAM 사용 한도는 RAM의 1/4(최대 512MiB)입니다. 필요한 만큼만 RAM을 사용합니다. 메모리 부족 상황을 완화하는 기능이며 FPS 향상을 보장하지는 않습니다.
- **BennuGD 코어 적용:** 제공받은 ARM64 BennuGD libretro 코어를 넣고 재부팅 때 자동 연결되도록 했습니다. save-overlay는 필요 없습니다. 이 CRC판의 FBNeo·MAME2003 Plus 바이너리는 변경하지 않았습니다.
- 기존 PPSSPP 1.20.4·Vulkan, Mali 메뉴, Wi-Fi, 회전, Ozone, PortMaster, 진동·밝기 보완은 유지합니다.

코어는 재부팅할 때마다 자동 연결되며 save-overlay는 필요 없습니다. MAME2003 Plus의 mame078plus 이름도 처리합니다.

## 설치와 사용

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 기록합니다. 필요하면 XZ를 먼저 풀어 주세요. 대상 SD의 기존 내용은 지워집니다.

**첫 설치 시 부팅 이미지 이후 검정화면이 보여도 약 5분 기다려 주세요. 자동 확장·설정 적용으로 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 완료될 때까지 전원을 유지하세요.**

밝기: SELECT+볼륨 +/−. PPSSPP 종료: SELECT+START 약 1초. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하고 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 폴더에 `DISABLED`라는 빈 파일을 만들면 됩니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 폴더에 `DISABLED`라는 빈 파일을 만들면 됩니다.

## 확인 범위와 출처

관리자 실기에서 ZRAM 블록 압축·되읽기, 실제 32MiB 스왑 저장·복원, 서비스 켜기·끄기와 재부팅 자동 시작을 확인했습니다. BennuGD는 파일 해시·실제 코어 연결을 확인했으며 해당 제공 코어의 게임 실행·재부팅 시험은 반복하지 않았습니다. 장시간 메모리 압박·절전 복귀·모든 생산분 및 새 v1.0.5 IMG를 SD에 다시 굽는 시험은 하지 않았습니다.

제공된 두 코어와 자동 연결은 기존 확인 결과를 유지하며 새 이미지에서 코어 해시 동일성을 확인했습니다. 정확히 일치하는 수정 코어 소스와 CRC 패치는 제공받지 못했으며 상위 소스 링크를 정확한 대응 소스로 주장하지 않습니다.

- [CRC판 상세 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5-crc-ko/docs/CRC_KOREAN.ko.md)
- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5-crc-ko/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5-crc-ko/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5-crc-ko/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5-crc-ko/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5-crc-ko/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5-crc-ko/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.5-crc-ko/docs/TESTING.ko.md)

압축 해제 IMG: 6,069,178,368바이트. SHA256: 2335743b4178c753bd0998b7de1eb9ad6d3396c244b59a12b5ef6727a115fe4c. CRC판 전용 체크섬을 사용하세요.

BennuGD는 별도로 제공받은 코어이며 dsno님 출처 표기는 FBNeo·MAME CRC 무시 코어에만 해당합니다. BennuGD의 정확한 대응 소스·빌드 정보는 제공받지 못했습니다.
