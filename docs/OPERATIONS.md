# 운영 및 장애 대응 가이드

## 배포 전 확인

```powershell
python -m unittest discover -s tests -v
python -m compileall -q api scripts
python scripts/check_secrets.py
```

Preview에 먼저 배포해 `/api/blueprint`의 정상·빈 입력·오류 응답을 확인한 뒤 Production으로 승격한다. Preview와 Production은 변수 이름은 같게, 키와 사용 한도는 분리한다.

## Vercel 진단

```powershell
vercel inspect <deployment-url> --logs
vercel logs --level error --since "1 h"
vercel logs --follow
vercel redeploy <deployment-url>
```

- 빌드 실패: Project → Deployments → 배포 선택 → Build Logs에서 Python 버전, 의존성 설치, 함수 번들 오류를 확인한다.
- 실행 실패: Project → Logs에서 route `/api/blueprint`, status `4xx/5xx`, environment, branch로 필터링한다.
- 개별 요청: Request ID를 열어 함수 실행 시간, 메모리, 외부 OpenAI 요청과 오류 메시지를 확인한다.
- 수정 후: Preview 재배포 → 테스트 입력 호출 → 오류 로그 없음 확인 → Production 승격 순서로 복구한다.

## 상태 코드별 대응

| 상태 | 사용자 메시지 | 개발자 확인 |
| --- | --- | --- |
| 400 | 입력 내용을 확인해 주세요 | JSON과 `idea` 길이 |
| 413 | 입력이 너무 깁니다 | 요청 본문 8KB 제한 |
| 502 | AI 응답을 만들지 못했습니다 | OpenAI 오류와 JSON 파싱 로그 |
| 503 | AI 설정이 완료되지 않았습니다 | `OPENAI_API_KEY` 환경변수 |
| 504/브라우저 timeout | 응답이 지연됐습니다 | 함수 실행 시간과 외부 요청 지연 |

사용자 메시지는 키·스택·원문 예외를 노출하지 않는다. 개발용 세부 정보는 Vercel 로그에서 Request ID로만 확인한다.

## 키 유출 사고 대응

1. 노출 키를 즉시 폐기하고 새 키를 발급한다.
2. Preview와 Production 환경변수를 각각 교체한다.
3. 관련 배포를 재실행한다.
4. `git log -p`와 Actions 로그에서 최초 노출 시점과 복제 범위를 조사한다.
5. 공개 기록을 정리했다면 협업자에게 브랜치 재동기화를 공지한다.
6. OpenAI 사용량·결제 로그를 확인하고 비정상 사용을 기록한다.
7. `scripts/check_secrets.py`, GitHub Actions, 정기 키 회전으로 재발을 막는다.

## 성능·비용 선택지

| 선택지 | 효과 | 트레이드오프 |
| --- | --- | --- |
| 더 작은 모델 | 지연·비용 감소 | 기획 구체성 감소 가능 |
| 입력 정규화·짧은 출력 | 토큰 감소 | 상세 설명 감소 |
| 동일 입력 결과 캐시 | 반복 호출 제거 | 오래된 결과 무효화 필요 |
| 비동기 큐 | 긴 요청 안정화 | 상태 조회 UI·저장소 필요 |
| 사용자 rate limit | 비용 폭증 방지 | 인증 또는 식별자 필요 |

## 프레임워크 도입 판단

| 선택 | 장점 | 단점·변경 범위 |
| --- | --- | --- |
| Vanilla 유지 | 빌드 없음, 작은 번들, 학습 구조 명확 | 화면·공유 상태가 늘면 수동 DOM 관리 증가 |
| React/Vue 도입 | 컴포넌트 재사용, 라우팅·상태 생태계 | 빌드 도구 추가, HTML을 컴포넌트로 이전, JS 상태 로직 재작성, CSS 범위 재구성 |

라우트 5개 이상, 공유 상태 3개 이상, 같은 UI 패턴 반복이 발생할 때 프레임워크 전환 비용을 다시 산정한다.
