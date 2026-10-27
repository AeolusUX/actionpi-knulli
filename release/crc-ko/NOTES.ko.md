# 한국 사용자용 · CRC 무시 코어 적용판 v1.0.6

한글 패치 아케이드 게임용 FBNeo·MAME2003 Plus CRC 무시 코어가 필요한 분을 위한 별도 배포판입니다. 기본 배포판과 이미지·체크섬을 분리했습니다.

CRC 무시 코어는 **[dsno님 자료](https://dsno.tistory.com/m/)**를 사용했습니다. 이번 버전에서 두 코어 바이너리는 변경하지 않았습니다.

## v1.0.6 수정 내역

- **Flycast Vulkan 적용:** 일반·VL·Xtreme을 Vulkan으로 실행하며 게임·RetroArch 메뉴 회전 보정, HOME 종료와 재부팅 없는 ES 메뉴 복귀를 연결했습니다.
- **일반 Flycast 2.7 업데이트:** 일반 코어만 공식 v2.7 소스로 업데이트했습니다. VL·Xtreme의 소스 버전은 유지했습니다.
- **일반 코어 강력 추천:** 액션파이 실기에서 일반 Flycast 코어를 OpenGL에서 Vulkan으로 전환한 뒤 큰 폭의 성능 향상과 훨씬 부드러운 게임 화면을 직접 확인했습니다. **일반 Flycast 코어를 우선 사용하실 것을 강력히 권장합니다.** 확인된 향상은 Vulkan 전환 결과이며 2.7과 2.5의 정량 비교나 모든 게임의 성능 보장은 아닙니다.
- **해상도 변경 시 회전 유지:** 내부 해상도를 바꾸며 RetroArch가 Vulkan을 재초기화할 때 회전 보정 로더가 빠지는 문제를 수정했습니다. 세 코어에 공통 적용했습니다. 해당 Vulkan 실행에서는 GL 셰이더를 끄며 다른 에뮬레이터의 설정은 유지합니다.
- 기존 Wi-Fi·PPSSPP·Mali 메뉴·Ozone·PortMaster·진동·밝기·ZRAM·BennuGD 보완을 유지합니다.

코어는 재부팅할 때마다 자동 연결되며 save-overlay는 필요 없습니다. MAME2003 Plus의 mame078plus 이름도 처리합니다.

## 설치와 사용

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 기록합니다. 필요하면 XZ를 먼저 풀어 주세요. 대상 SD의 기존 내용은 지워집니다.

**첫 설치 시 부팅 이미지 이후 검정화면이 보여도 약 5분 기다려 주세요. 자동 확장·설정 적용으로 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 완료될 때까지 전원을 유지하세요.**

밝기: SELECT+볼륨 +/−. PPSSPP 종료: SELECT+START 약 1초. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하고 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다. ZRAM 복구는 BOOT의 `ACTIONPI_ZRAM` 폴더에 `DISABLED`라는 빈 파일을 만들면 됩니다.

## 확인 범위와 출처

제작자가 일반·VL·Xtreme Vulkan을 직접 플레이해 화질·성능 향상을 확인했으며 특히 일반 코어의 큰 개선을 보고했습니다. 일반 2.7은 원격으로 게임/데모·메뉴 표시, 해상도 증가에 따른 실제 Vulkan 재초기화 후 방향 유지와 같은 부팅의 정상 ES 복귀를 확인했습니다. VL·Xtreme의 개별 해상도 변경, 2.7의 실제 소리·물리 입력·성능 비교, 최종 이미지의 새 SD 플래싱과 모든 생산분은 추가 시험하지 않았습니다.

제공된 두 코어와 자동 연결은 기존 확인 결과를 유지하며 새 이미지에서 코어 해시 동일성을 확인했습니다. 정확히 일치하는 수정 코어 소스와 CRC 패치는 제공받지 못했으며 상위 소스 링크를 정확한 대응 소스로 주장하지 않습니다.

- [CRC판 상세 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6-crc-ko/docs/CRC_KOREAN.ko.md)
- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6-crc-ko/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6-crc-ko/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6-crc-ko/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6-crc-ko/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6-crc-ko/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6-crc-ko/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.6-crc-ko/docs/TESTING.ko.md)

압축 해제 IMG: 6,069,178,368바이트. SHA256: a0931b5048fb78fb196ab42f09e17022388eb579cc998a4baedc644d7c519f4d. CRC판 전용 체크섬을 사용하세요.

BennuGD는 별도로 제공받은 코어이며 dsno님 출처 표기는 FBNeo·MAME CRC 무시 코어에만 해당합니다. BennuGD의 정확한 대응 소스·빌드 정보는 제공받지 못했습니다.

Flycast 대응 소스: [일반판의 flycast-v1.0.6-sources.tar](https://github.com/pikachu220v/actionpi-knulli/releases/download/v1.0.6/flycast-v1.0.6-sources.tar). 펌웨어 이미지가 아닌 소스 묶음입니다.
