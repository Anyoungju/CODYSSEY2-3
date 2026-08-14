# 네이토 사전평가 기록

## 시도 1

- 평가 시각: 2026-08-14 17:28:44 KST
- 결과: **74% (14/19 통과)**
- 평가 저장소: `Anyoungju/CODYSSEY2-3`, 브랜치 `main`

핵심 기능인 반응형 UI, 프론트→서버리스→OpenAI 흐름, 입력·오류 처리, 환경변수 보안, 제출 문서 연결은 통과했다.

### 실패 항목과 반영

| 항목 | 평가 지적 | 반영 위치 |
| --- | --- | --- |
| #11 | Vercel 로그·콘솔 기반 배포 진단 부족 | `README.md`, `docs/OPERATIONS.md` |
| #12 | HTML/CSS/JS 개별 역할 설명 부족 | `README.md`, `docs/SERVICE_PLAN.md` |
| #17 | 프론트·백엔드 확장 아키텍처 부족 | `README.md`, `docs/SERVICE_PLAN.md` |
| #18 | API 키 유출 시 즉시·장기 대응 부족 | `README.md`, `docs/OPERATIONS.md` |
| #19 | 프레임워크 도입 장단점·변경 범위 부족 | `README.md`, `docs/OPERATIONS.md` |

### PASS 항목의 추가 권고 반영

- 프로젝트 구조를 파일별 책임 표로 구체화했다.
- 성공·실패 API JSON 예시와 테스트 매트릭스를 추가했다.
- UI 상태 변화와 오류 코드별 사용자 메시지를 문서화했다.
- Preview/Production 환경변수 전략을 분리했다.
- 프롬프트 버전, 성능·비용 선택지를 기록했다.
- `scripts/check_secrets.py`와 GitHub Actions 비밀 검사를 추가했다.

## 시도 2

- 평가 시각: 2026-08-14 17:41:33 KST
- 결과: **100% (19/19 통과)**
- 개선: 시도 1에서 실패한 #11, #12, #17, #18, #19가 모두 PASS로 전환됐다.

추가 권고는 실제 Vercel/OpenAI 운영 호출 캡처, 다양한 뷰포트와 오류 UI 스냅샷, CI 실행 결과 등 증빙 강화다. 실제 운영 키와 로그를 확인할 수 있을 때 `docs/EVIDENCE.md`에 사실 기반 자료만 추가한다.

## 재평가 방법

먼저 CDP Chrome과 자동로그인 세션을 연다.

```powershell
python scripts/open_chrome_cdp.py
python scripts/naito_precheck.py --output docs/naito/latest.json
```

결과 확인은 시도 횟수를 소비하지 않는다. 새 평가를 시작할 때만 명시적으로 `--start`를 사용한다.

```powershell
python scripts/naito_precheck.py --start --timeout 300 --output docs/naito/attempt-2.json
```

대기 프로세스가 중단되어도 새 시도를 시작하지 말고 진행 중인 평가에 다시 연결한다.

```powershell
python scripts/naito_precheck.py --wait --timeout 300 --output docs/naito/attempt-2.json
```
