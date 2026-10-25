# 소스·라이선스·출처

[English](SOURCES_AND_LICENSES.md) · [한국어](SOURCES_AND_LICENSES.ko.md)

## 소스·라이선스·출처

이 펌웨어는 서로 다른 라이선스를 적용받는 구성 요소들의 모음입니다. 새로 작성한
연결 코드의 저장소 라이선스가 Linux, Arm, SDL, 에뮬레이터, 펌웨어나 BIOS의 조건을
대신하지 않습니다. 포함한 외부 소스의 기존 고지문은 보존했습니다.

| 구성 요소 | 기록한 소스·출처 | 확인 상태 |
| --- | --- | --- |
| 직접 작성한 연결 코드 | `overlay/`, `src/`, `tools/` | 해당 범위를 명시한 MIT 고지 적용. 커널 파생 작업은 GPL 조건 유지 |
| Mali 커널 드라이버 | Radxa allwinner-bsp 커밋 `2045a3ca2a01f088c0314dc924bda59d154e363e`, `modules/gpu/mali-valhall/driver` | 추적되는 상위 소스를 저장소에 포함. license.txt와 파일별 고지 보존. 후보 빌드 입력 기록 |
| 제조사 Linux 5.15.147 | 복구 설정, 바이너리 식별 정보, 보호 조건을 둔 수정 소스 포함 | 정확한 원본 제조사 트리와 빌드 출처는 미확인 |
| 공개 커널 후보 | Orange Pi 커밋 `5b956b750422abd5e9e9c5523540d2aaf41a7939` | 헤더·구조체 배치·소스 비교용. 제조사 바이너리의 정확한 대응 소스라고 주장하지 않음 |
| KNULLI 통합 | `knulli-main`의 [Action Pi 보드 설정](https://github.com/knulli-cfw/knulli-linux/tree/knulli-main/board/allwinner/a527/helegany-action-pi), A527 이력 `5a7cb1e8e4dd` | 보드 구성 기반. 기존 이미지 전체의 정확한 소스 대응은 확립되지 않음 |
| SDL2 | [release-2.32.8](https://github.com/libsdl-org/SDL/tree/release-2.32.8) | 대상 SDL 2.32.8 확인. 새 보정 기능은 별도 소스 파일로 제공 |
| Flycast VL 참조 | [libretro/flycast 커밋 4a913e0](https://github.com/libretro/flycast/tree/4a913e063c95d1fae98afc64645831de0bcad57e) | 구형 시그널·JIT 조사에 사용한 소스 참조 |
| PPSSPP/Flycast/RetroArch/ES | 기존 KNULLI 프로그램. 이 저장소의 수정 소스가 실행·출력 동작을 감쌈 | 기존 바이너리 각각의 정확한 소스·버전 대응을 모두 확보했다고 주장하지 않음 |
| Mali 사용자 공간 라이브러리 | 기존 제조사 구성. GLES 렌더러에서 r32p0 관찰 | 제조사 독점 바이너리. 커널 드라이버 GPL이 libmali까지 허가하는 것은 아님 |
| AIC8800DC 모듈·펌웨어 | 정상 작동하는 순정 펌웨어의 파일 재사용 | 수정 작업에서 바이너리 출처를 기록했으나, 정확한 대응 모듈 소스·재배포 조건은 완전히 해결되지 않음 |
| 기본 BIOS | 기존 기본 루트 파일시스템의 BIOS를 그대로 유지 | 연결 코드 라이선스 적용 대상이 아님. BIOS가 전혀 없는 배포판은 아님 |
| 추가 개인 BIOS 압축 파일 | 제외 | 공개 배포 파일이 아님 |

## 소스 구분이 필요한 이유

[GNU GPLv2 FAQ](https://www.gnu.org/licenses/old-licenses/gpl-2.0-faq.html)는 GPL
바이너리를 배포할 때의 소스 제공 의무를 설명합니다. 일반적인 상위 프로젝트 주소나
버전 숫자가 비슷한 커널만으로 특정 제조사 바이너리에 사용된 소스라고 할 수는 없습니다.
따라서 공개 후보를 올렸다는 이유만으로 미해결 제조사 소스 문제가 해결되었다고
주장하지 않습니다.

기존 배포판 전체의 소스·출처 목록에는 추가 조사가 필요합니다. 특히 원본 커널 변경분,
순정 Wi-Fi 소스, 제조사 사용자 공간과 유지한 BIOS의 이용 조건을 확인해야 이미지
전체의 완전한 소스 제공이나 재배포 조건 준수를 주장할 수 있습니다. 이 문서는
확인한 근거와 남은 공백을 기록하며, 그 주장을 인증하는 문서가 아닙니다.

## 주요 상위 프로젝트와 원출처

- [KNULLI](https://github.com/knulli-cfw/knulli-linux)
- [고정한 Mali 소스](https://github.com/radxa/allwinner-bsp/tree/2045a3ca2a01f088c0314dc924bda59d154e363e/modules/gpu/mali-valhall/driver)
- [고정한 Orange Pi 후보](https://github.com/orangepi-xunlong/linux-orangepi/tree/5b956b750422abd5e9e9c5523540d2aaf41a7939)
- [Arm GNU 13.3.Rel1](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)
- [SDL evdev 시그널 처리 경로](https://github.com/libsdl-org/SDL/blob/release-2.32.8/src/core/linux/SDL_evdev_kbd.c)
- [Ultramarine 핸드헬드 제조사 그래픽 구성 작업](https://github.com/Ultramarine-Linux/ultramarine-handheld)

준비 과정에서 기록한 빌드 툴체인 압축 파일의 SHA256:
`322f0b4482fc0d9fa0bb468134841f08d8c554c54ff5aa29a13a7a24bf7e1eb5`.

## v1.0.1 Wi-Fi 출처

AIC 바이너리는 기존에 기록한 순정펌 이식본을 유지했습니다. 8723ds도 5.15.147 대상에서 검토했던 순정 바이너리이며 SDIO 024c:d723 지원 별칭을 포함합니다. 이번 배포는 기존 모듈을 재부팅 후에도 유지되는 부팅 사본에 연결한 것으로, 제조사 소스 전체를 작성하거나 재빌드했다고 주장하지 않습니다. 바이너리 해시는 release/BOOT_COMPONENTS.json에 기록했고 위에 명시한 원본 제조사 커널·소스 출처의 미확인 범위는 그대로입니다.

## v1.0.2 보조 파일

retroarch_gles3_context.c는 이번 적용을 위해 작성한 MIT 보조 소스입니다. SDL의 컨텍스트 주 버전 요청만 해당 프로세스에서 조정하며 SDL/RetroArch 자체를 교체하지 않습니다. 기존 소스·라이선스 미확정 사항은 동일합니다.

## 한국 사용자용 CRC 별도판

FBNeo·MAME2003 Plus는 사용자가 제공한 수정 바이너리이며 IMG를 별도 릴리스로 제공합니다. 정확히 대응하는 소스 버전·CRC 수정 패치는 제공받지 못했습니다. 상위 [FBNeo](https://github.com/finalburnneo/FBNeo)·[MAME2003 Plus](https://github.com/libretro/mame2003-plus-libretro) 링크는 참고 자료입니다. 자동 적용 소스와 해시는 config/crc-ko/ 및 release/crc-ko/에 공개합니다. [한국어 안내](CRC_KOREAN.ko.md). 각 코어의 조건은 일반 MIT 적용 범위와 별개입니다.

CRC 무시 코어 자료 출처: **[dsno님 블로그](https://dsno.tistory.com/m/)**. 사용자가 이 자료를 사용했다고 확인했습니다.
