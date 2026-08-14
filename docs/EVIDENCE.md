# 구현 및 검증 증빙

## 화면

- 데스크톱: `docs/screenshots/desktop.png` (1440×1000)
- 모바일: `docs/screenshots/mobile.png` (390×844)
- 태블릿 가로: `docs/screenshots/tablet-landscape.png` (844×390)
- 빈 입력 오류: `docs/screenshots/validation-error.png` (390×844)
- AI 결과 UX: `docs/screenshots/ai-result.png`

스크린샷은 Chrome CDP로 실제 DOM을 렌더링해 생성했다. 모바일에서는 주요 버튼 터치, 입력 포커스, 결과 카드 단일 열 전환을 확인했다.

## 배포 상태 검증

2026-08-14 KST에 실제 URL을 다시 확인했다.

| 대상 | 확인 결과 | 판정 |
| --- | --- | --- |
| GitHub Pages `/CODYSSEY2-3/` | HTTP 200, HTML 8,524 bytes | 정상 |
| 예정 Vercel `/api/blueprint` GET | HTTP 404, `DEPLOYMENT_NOT_FOUND` | 미배포 또는 연결 해제 |
| 예정 Vercel `/api/blueprint` POST | HTTP 404, `DEPLOYMENT_NOT_FOUND` | 운영 AI 호출 미검증 |

따라서 정적 배포는 검증됐지만 운영 AI 연동은 완료로 주장하지 않는다. Vercel 프로젝트를 다시 연결한 뒤 정상 요청의 상태 코드, 비밀값을 제거한 응답 일부, 해당 시각의 Runtime Log를 추가해야 한다.

## 테스트 재현

| 케이스 | 절차 | 확인 결과 |
| --- | --- | --- |
| 정상 | `?demo=1`에서 예시 입력 제출 | 결과 화면·3개 페이지·로드맵 표시 |
| 빈 입력 | 아이디어를 비우고 제출 | 폼 아래 안내, 입력 포커스 이동, `validation-error.png` |
| 긴 입력 | Python 테스트에서 601자 전달 | `ValueError` 발생 |
| 모델 JSON | 코드펜스가 있는 응답 파싱 | 스키마 파싱 성공 |
| 잘못된 페이지 | 화면 1개인 모델 응답 | 파싱 거부 |

실행 명령과 최신 결과:

```text
python -m unittest discover -s tests -v
Ran 8 tests — OK
```

## AI 코딩 도구 활용 과정

1. Codyssey 학습 화면을 CDP로 읽어 필수 제출물, 기능 조건, 보안 제약을 구조화했다.
2. 요구사항을 서비스 아이디어, 화면 구조, AI 입출력, 실패 UX로 나누었다.
3. HTML/CSS/JavaScript와 Python API를 단위 테스트 및 실제 Chrome 화면으로 재검증했다.
4. 네이토 사전평가 결과를 CDP로 수집하고 실패 5개 항목을 운영·기술 문서에 반영했다.
5. 저장소에는 비밀값을 제외하고 실행·배포 재현 방법을 기록했다.

## 확인 목록

- [x] 메뉴가 연결된 3개 이상의 섹션
- [x] Vanilla HTML/CSS/JavaScript 반응형 UI
- [x] Python `api/`와 OpenAI 호출 코드
- [x] 빈 입력·API 오류·시간 초과 UX
- [x] 환경변수 기반 비밀키 관리
- [x] 서비스 기획서, 운영 가이드, README
- [x] GitHub 공개 저장소와 Pages 배포
- [x] 네이토 1차 사전평가 기록 및 피드백 반영
- [x] 네이토 2차 사전평가 100% (19/19) 확인
- [ ] Vercel 배포 복구 및 실제 OpenAI 운영 호출 캡처
