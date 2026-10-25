# 공개 파일 범위

[English](PUBLIC_FILES.md) · [한국어](PUBLIC_FILES.ko.md)

## 공개 범위

공개 코드는 **배포판**에서 명시적인 허용 목록을 사용해 선별했습니다.
원래 개인 작업 디렉터리나 대화 전체를 업로드하지 않았습니다.

## 포함한 항목

- 확인된 결과와 실패한 접근을 정리한 개발 이력.
- 현재 사용하는 시작·세션·불투명도·회전·입력·전원 보조 기능.
- 고정한 커밋의 정확한 상위 Mali 드라이버 소스와 원래 고지문.
- 복구한 커널 설정, 후보 커널 설정과 옵션, 소스 정리 패치,
  원본 확인 조건이 있는 어셈블리 수정 및 검증 요약.
- 과거 이미지 변환·PWM 도구. 공개되지 않은 이전 입력 이미지를 필요로 하는 경우
  과거 작업용 도구임을 명시했습니다.
- 개인정보를 정리한 배포판 기본 설정, PortMaster 설치 항목, 릴리스 구성 명세,
  구성 파일 해시, 최종 이미지·체크섬 및 압축 배포 파일.
- 빌드·설치·복구·검증 범위·소스와 출처에 관한 문서.

## 제외한 항목

- 개인용 이미지, 개인 BIOS 압축 파일 및 개인 캡처.
- 저장된 개인 Wi-Fi SSID·비밀번호와 이를 포함하는 복구 사본.
- GitHub 인증 정보, 브라우저 세션 자료, 인증 화면 캡처,
  known-hosts 파일 및 SSH 개인 키·호스트 키.
- 원본 사용자 대화, 비공개 네트워크 로그, 기기 식별자, 쿠키, 사용 기록,
  Bluetooth 페어링 기록, 게임 화면 캡처, 진단 메모리 덤프 및 게임 ROM.
- 컴파일러 설치 파일, Git 데이터베이스와 드라이버 작업 폴더의 추적되지 않는 빌드 산출물.

원본 이미지의 기본 루트 파일시스템과 그 안의 원래 BIOS는 의도적으로 그대로 유지했습니다.
별도로 추가한 개인 BIOS 압축 파일을 제외한 것과는 구분됩니다. 공개 이미지 제작 시
FAT 여유 공간 3,289,493,504바이트를 0으로 채우고, 파일 끝 여유 영역 122개와 삭제된
항목 26개를 정리했습니다. 파일 이름만 지우는 방식으로 끝내지 않았습니다.

다운로드할 IMG는 Git 소스 이력 대신 GitHub **Releases**에 둡니다.
소스 저장소는 펌웨어 전체를 내려받지 않고도 살펴보고 복제할 수 있는 크기로 유지합니다.

## v1.0.1 추가·갱신 파일

- overlay/etc/init.d/S06modprobe·S08connman: 실제 부팅 시작 코드.
- overlay/usr/bin/emulatorlauncher: 렌더러에 맞춘 실행 경로.
- overlay/boot/ACTIONPI_FIXES/: 공통 앱·PortMaster 런타임·OD-Commander·Wi-Fi helper 최신본.
- overlay/boot/PPSSPP_VULKAN/: 활성 manager/autostart의 갱신된 해시 연결.
- src/app_sdl_rotation.c·app_gl_rotation.c·od_commander_rotation.c: 보정 소스. 컴파일된 사용자 공간 라이브러리를 Git에 넣지는 않습니다.
- tools/ActionPi-WiFi-Diagnostic.sh·wifi-diagnostic.py: 이번 공개판에서도 쓸 수 있는 읽기 전용 진단.
- release/distribution-v1.0.1.manifest.json과 현재 구성/소스 목록·자산 체크섬.

v1.0.1 공개 당시 CRC 코어판은 제외했습니다. 게임 ROM·네트워크 정보가 보이는 사진·이전 개인용 안정판은 공개하지 않습니다.

## v1.0.2 추가·갱신

- src/retroarch_gles3_context.c 및 tools/build-runtime.sh의 ARM64 빌드 명령.
- overlay/boot/ACTIONPI_FIXES/actionpi_app_launcher.py와 MALI_MENU_TRIAL/mali_menu_trial.py.
- release/distribution-v1.0.2.manifest.json, FIELD_VALIDATION-v1.0.2.json 및 최신 이미지/자산/소스 해시.
- 일반판에는 CRC 코어를 넣지 않습니다. 이전 개인 BIOS·설정은 공개하지 않습니다.

## 한국 사용자용 CRC 별도판

일반판과 분리된 릴리스에 CRC 적용 IMG를 제공합니다. config/crc-ko/는 실제 자동 적용 소스, release/crc-ko/는 전용 구성/체크섬입니다. [상세 안내](CRC_KOREAN.ko.md).
