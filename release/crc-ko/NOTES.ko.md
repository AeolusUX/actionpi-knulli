# 한국 사용자용 · CRC 무시 코어 적용판 v1.0.3

한글 패치 아케이드 게임용 FBNeo·MAME2003 Plus CRC 무시 코어가 필요한 분을 위한 별도 배포판입니다. 기본 배포판과 이미지·체크섬을 분리했습니다.

CRC 무시 코어는 **[dsno님 자료](https://dsno.tistory.com/m/)**를 사용했습니다. 이번 버전에서 두 코어 바이너리는 변경하지 않았습니다.

## v1.0.3 수정 내역

- **진동 보정:** 모터 PWM을 25kHz로 바꾸고 작은 진동 신호의 세기를 보정했습니다. 시험 기기의 Flycast VL·Xtreme 크레이지택시 1·2에서 작은 진동이 느껴지고 거슬리던 고주파음이 줄어드는 것을 확인했습니다.
- **밝기 단축키:** SELECT를 먼저 누른 채 볼륨 +/−로 조절합니다. 길게 누름을 지원하며 일반 볼륨과 HOME 동작은 유지합니다.
- **밝기 게이지:** 메뉴와 게임 위에 해 아이콘·밝기 %·막대를 표시하고 조작 후 약 2.2초 뒤 숨깁니다. 비어 있는 출력 레이어를 사용하며 표시할 때만 실행하므로 대기 중 상주 서비스가 추가되지 않습니다.
- **백그라운드 정리:** 기본 통계 전송을 끄고, 예전 부팅 로그 반복 복사 작업이 남은 기기에서는 이를 중지합니다. 옛 진단 maps 파일은 이미지에서 제외했습니다.
- Mali 메뉴·PPSSPP Vulkan·Wi-Fi·회전·Ozone·PortMaster와 CRC판 코어 자동 적용을 유지했습니다. CPU 배치는 바꾸지 않았습니다.

코어는 재부팅할 때마다 자동 연결되며 save-overlay는 필요 없습니다. MAME2003 Plus의 mame078plus 이름도 처리합니다.

## 설치와 사용

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 기록합니다. 필요하면 XZ를 먼저 풀어 주세요. 대상 SD의 기존 내용은 지워집니다.

**첫 설치 시 부팅 이미지 이후 검정화면이 보여도 약 5분 기다려 주세요. 자동 확장·설정 적용으로 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 완료될 때까지 전원을 유지하세요.**

밝기: SELECT+볼륨 +/−. PPSSPP 종료: SELECT+START 약 1초. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하고 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다.

## 확인 범위와 출처

실기에서 진동 세기·소음과 재부팅 후 유지, 재부팅 후 통계 전송·반복 로그 중지, 밝기 단축키의 방향·길게 누름·일반 볼륨 유지를 확인했습니다. 사용자가 ES와 PPSSPP의 밝기 게이지 표시·자동 숨김·게임 종료·메뉴 복귀를 확인했고, 표시 뒤 작업도 종료되는 것을 원격으로 확인했습니다. 공통 화면 경로를 사용하지만 모든 에뮬레이터·생산분을 각각 재시험한 것은 아닙니다. 이후 사용자가 기기를 재부팅하고 밝기 단축키·게이지를 포함한 수정 사항 전체가 정상 작동한다고 확인했습니다. 새로 패키징한 설치 IMG를 별도 SD에 다시 굽는 시험도 반복하지 않았습니다.

제공된 두 코어와 자동 연결은 기존 확인 결과를 유지하며 새 이미지에서 코어 해시 동일성을 확인했습니다. 정확히 일치하는 수정 코어 소스와 CRC 패치는 제공받지 못했으며 상위 소스 링크를 정확한 대응 소스로 주장하지 않습니다.

- [CRC판 상세 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3-crc-ko/docs/CRC_KOREAN.ko.md)
- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3-crc-ko/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3-crc-ko/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3-crc-ko/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3-crc-ko/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3-crc-ko/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3-crc-ko/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.3-crc-ko/docs/TESTING.ko.md)

압축 해제 IMG: 6,069,178,368바이트. SHA256: 9b02a097dce0ee517112138bcae169bf44bbd50d84cba39fb10520f0f8b16a2f. CRC판 전용 체크섬을 사용하세요.
