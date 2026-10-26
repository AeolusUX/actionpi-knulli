# 한국 사용자용 · CRC 무시 코어 적용판 v1.0.4

한글 패치 아케이드 게임용 FBNeo·MAME2003 Plus CRC 무시 코어가 필요한 분을 위한 별도 배포판입니다. 기본 배포판과 이미지·체크섬을 분리했습니다.

CRC 무시 코어는 **[dsno님 자료](https://dsno.tistory.com/m/)**를 사용했습니다. 이번 버전에서 두 코어 바이너리는 변경하지 않았습니다.

## v1.0.4 수정 내역

- **PPSSPP 1.20.4 업데이트:** 공식 소스로 ARM64 빌드해 1.19.3에서 올렸습니다. PSP 게임과 Emulators → PPSSPP 단독 실행 모두 새 Vulkan 버전으로 연결됩니다.
- **Vulkan·화면 호환 보완:** 기존 Mali 드라이버·회전·출력 투명도 보정·메뉴 복귀는 유지하고, 새 버전의 초기 검사에 필요한 Vulkan 함수 전달 3개를 추가했습니다. 부팅용 런처 두 사본도 동기화했습니다.
- **한영 혼합 글꼴 수정:** 설치된 Noto·나눔 글꼴을 올바르게 선택하도록 보완해 혼합 문장의 네모 글자를 해결했습니다.
- 기존 Wi-Fi·에뮬레이터 회전·Ozone·PortMaster·진동·밝기 단축키와 게이지 보정은 유지합니다. 임시 시험 제어 프로그램·캡처·개인 설정은 포함하지 않습니다.

코어는 재부팅할 때마다 자동 연결되며 save-overlay는 필요 없습니다. MAME2003 Plus의 mame078plus 이름도 처리합니다.

## 설치와 사용

이 릴리스의 .img.xz와 SHA256SUMS를 내려받아 체크섬을 확인하고 SD 전체에 기록합니다. 필요하면 XZ를 먼저 풀어 주세요. 대상 SD의 기존 내용은 지워집니다.

**첫 설치 시 부팅 이미지 이후 검정화면이 보여도 약 5분 기다려 주세요. 자동 확장·설정 적용으로 한두 번 재부팅한 뒤 메뉴가 표시됩니다. 완료될 때까지 전원을 유지하세요.**

밝기: SELECT+볼륨 +/−. PPSSPP 종료: SELECT+START 약 1초. 상단의 HOME키를 이용한 에뮬레이터 종료는 RetroArch에서 작동하고 PPSSPP에서는 비활성화되어 있습니다. 게임 ROM은 포함하지 않습니다.

## 확인 범위와 출처

사용자가 재부팅 후에도 PPSSPP 1.20.4가 정상 실행되는 것을 확인했습니다. 실기 캡처에서 메뉴 방향·한영 혼합 글꼴을 확인했고, 정상 종료와 재부팅 없는 ES 복귀를 확인했습니다. 앞선 시험에서 게임 타이틀 출력도 원격으로 확인했습니다. 모든 게임의 성능·동작과 모든 생산분을 다시 시험한 것은 아닙니다. 새로 패키징한 v1.0.4 설치 IMG를 별도 SD에 다시 굽는 시험은 반복하지 않았습니다.

제공된 두 코어와 자동 연결은 기존 확인 결과를 유지하며 새 이미지에서 코어 해시 동일성을 확인했습니다. 정확히 일치하는 수정 코어 소스와 CRC 패치는 제공받지 못했으며 상위 소스 링크를 정확한 대응 소스로 주장하지 않습니다.

- [CRC판 상세 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4-crc-ko/docs/CRC_KOREAN.ko.md)
- [작업 이력](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4-crc-ko/docs/HISTORY.ko.md)
- [작동 구조](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4-crc-ko/docs/ARCHITECTURE.ko.md)
- [빌드·이미지 제작](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4-crc-ko/docs/BUILD.ko.md)
- [공개 파일](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4-crc-ko/docs/PUBLIC_FILES.ko.md)
- [출처·라이선스](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4-crc-ko/docs/SOURCES_AND_LICENSES.ko.md)
- [설치 안내](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4-crc-ko/docs/RELEASE.ko.md)
- [검증 범위](https://github.com/pikachu220v/actionpi-knulli/blob/v1.0.4-crc-ko/docs/TESTING.ko.md)

압축 해제 IMG: 6,069,178,368바이트. SHA256: 2d9733617773319a85a3492ee0db2b6832802fea03c0ba21ee37a1c69f0da605. CRC판 전용 체크섬을 사용하세요.
