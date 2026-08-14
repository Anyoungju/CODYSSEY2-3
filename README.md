# Codyssey Compass

막연한 웹 서비스 아이디어를 실행 가능한 MVP 청사진으로 바꾸는 AI 프로젝트 내비게이터입니다. Codyssey의 **AI 웹 개발: 내 아이디어를 현실로** 미션 결과물로 제작했습니다.

- GitHub: <https://github.com/Anyoungju/CODYSSEY2-3>
- 프론트엔드 데모: <https://anyoungju.github.io/CODYSSEY2-3/>
- AI API 예정 주소: `https://codyssey-compass.vercel.app/api/blueprint`

> GitHub Pages는 정적 프론트엔드를 제공합니다. 프론트는 Vercel Python API를 호출하도록 구현되어 있지만, 2026-08-14 확인 시 위 예정 주소는 `DEPLOYMENT_NOT_FOUND`(404)였습니다. Vercel 프로젝트 연결과 환경변수 등록 후 운영 호출 증빙을 완료해야 합니다.

## 주요 기능

- 아이디어, 대상 사용자, 우선 조건을 바탕으로 AI 프로젝트 청사진 생성
- 3개 이상의 화면 구성, AI 입출력, 4단계 개발 순서, 위험 요소 제안
- 빈 입력, API 오류, 시간 초과를 구분하는 사용자 안내
- 모바일 반응형 화면과 라이트/다크 테마
- 브라우저에 API 키를 노출하지 않는 Python 서버리스 API

## 기술별 책임

| 기술 | 책임 | 주요 파일 |
| --- | --- | --- |
| HTML | 콘텐츠 의미 구조, 메뉴와 폼, 접근성 속성 | `index.html` |
| CSS | 색상·레이아웃·애니메이션, 820px/520px 반응형 전환 | `css/styles.css` |
| JavaScript | 입력 검증, 상태 전환, `fetch`, 결과 렌더링 | `js/app.js` |
| Python | 요청 검증, OpenAI 호출, 결과 스키마 검사, HTTP 오류 변환 | `api/blueprint.py` |

데이터 흐름은 `사용자 입력 → JavaScript 검증 → POST /api/blueprint → Python 검증 → OpenAI Responses API → JSON 검사 → 결과 카드 렌더링` 순서입니다. API 키는 이 경계의 서버 쪽에만 존재합니다.

## 프로젝트 구조와 경계

| 경로 | 역할 |
| --- | --- |
| `index.html` | 화면의 의미 구조와 입력·결과 컨테이너 |
| `css/styles.css` | 디자인 토큰, 컴포넌트 스타일, 반응형 규칙 |
| `js/app.js` | 브라우저 상태와 API 통신 |
| `api/blueprint.py` | Vercel 함수 `/api/blueprint` |
| `tests/` | 입력·응답 파서와 자동화 도구 단위 테스트 |
| `docs/` | 서비스 기획, 운영, 증빙, 네이토 평가 기록 |
| `scripts/naito_precheck.py` | CDP 기반 네이토 사전평가 실행·수집 |

프론트엔드는 OpenAI를 직접 호출하지 않으며, Python API는 화면 DOM을 알지 못합니다. 두 계층의 계약은 아래 JSON 형식뿐입니다.

## 로컬 실행

정적 화면과 데모 결과를 확인합니다. `?demo=1`은 OpenAI를 호출하지 않는 화면 검증 전용 모드입니다.

```powershell
python -m http.server 8000
```

브라우저에서 `http://localhost:8000/?demo=1`을 엽니다. 운영과 동일한 API 흐름은 Vercel CLI로 실행합니다.

```powershell
vercel dev
```

## 환경변수

`.env.example`을 참고해 로컬 또는 Vercel에 설정합니다.

```dotenv
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.4-mini
ALLOWED_ORIGIN=https://anyoungju.github.io
```

- Preview와 Production에는 같은 변수 이름을 사용하되 값을 각각 등록합니다.
- Preview는 테스트용 OpenAI 프로젝트·낮은 사용 한도를, Production은 운영용 프로젝트·별도 사용량 알림을 사용합니다.
- 키는 Git, README, 스크린샷, 브라우저 저장소에 기록하지 않습니다.

## API 계약

요청:

```json
{
  "idea": "감정을 기록하면 회고 질문을 제안하는 서비스",
  "audience": "취업 준비생",
  "constraint": "빠르게 MVP 완성"
}
```

성공 `200`:

```json
{
  "blueprint": {
    "service_name": "마음 한 칸",
    "one_liner": "감정을 정리할 질문을 받는 회고 서비스",
    "pages": ["감정 기록", "AI 회고", "나의 흐름"],
    "ai_feature": {
      "title": "회고 질문",
      "input": "감정과 오늘 있었던 일",
      "output": "질문과 작은 행동",
      "user_value": "생각을 정리할 실마리",
      "failure_handling": "입력을 보존하고 재시도 안내"
    },
    "milestones": ["화면", "입력", "API", "배포"],
    "risks": ["민감정보", "호출 비용"]
  },
  "model": "gpt-5.4-mini"
}
```

오류 `400/413/502/503/504`:

```json
{"error": "아이디어를 입력해 주세요."}
```

브라우저는 상태 영역에 한국어 오류를 표시하고 입력을 보존합니다. 빈 입력은 API 호출 전에 차단하고, 네트워크·5xx 오류는 다시 시도할 수 있게 폼을 활성화하며, 20초가 지나면 시간 초과 메시지를 표시합니다. 개발자는 Network 탭의 상태 코드와 Vercel Request ID로 원인을 추적합니다.

## 테스트

```powershell
python -m unittest discover -s tests -v
python -m compileall -q api scripts
python scripts/check_secrets.py
```

| 시나리오 | 입력 | 기대 결과 |
| --- | --- | --- |
| 정상 | 1~600자의 아이디어 | 청사진 카드 표시 |
| 빈 입력 | 공백만 입력 | 폼 아래 즉시 안내, API 미호출 |
| 과도한 입력 | 601자 이상 | 서버 `400`, 입력 길이 안내 |
| API 미설정 | 서버 키 없음 | `503`, 설정 안내 |
| 지연 | 20초 이상 | 요청 중단, 재시도 안내 |

GitHub Actions도 단위 테스트, Python 컴파일, 비밀값 패턴 검사를 반복합니다.

## 배포와 진단

GitHub 저장소를 Vercel에 Import하고 환경변수를 등록하면 정적 사이트와 `api/blueprint.py`가 함께 배포됩니다.

```powershell
vercel inspect <deployment-url> --logs
vercel logs --level error --since "1 h"
vercel redeploy <deployment-url>
```

빌드 실패는 Vercel **Project → Deployments → 해당 배포 → Build Logs**, 실행 중 4xx/5xx는 **Project → Logs**에서 `/api/blueprint` 경로와 Request ID로 확인합니다. 수정 후 Preview에서 API를 검증한 다음 Production으로 승격하거나 재배포합니다. 상세 절차는 [운영 가이드](docs/OPERATIONS.md)에 있습니다.

## 확장 전략

| 단계 | 프론트엔드 변화 | 백엔드 변화 |
| --- | --- | --- |
| 현재 MVP | 단일 HTML과 작은 JS 상태 | 단일 Vercel 함수 |
| 기능 증가 | 기능별 JS 모듈, URL 라우팅 | 인증, 사용자별 호출 제한, 저장소 분리 |
| 트래픽 증가 | 정적 CDN 유지, 결과 캐시 | Redis 캐시, 작업 큐, 비동기 결과 조회, 관측성 |

Vanilla JS는 빌드 과정과 의존성이 작아 이 MVP에 적합합니다. 화면·공유 상태가 크게 늘면 React/Vue가 컴포넌트 재사용과 상태 추적에 유리하지만, `index.html`을 컴포넌트 트리로, `js/app.js`를 API 모듈과 상태 훅으로, CSS를 컴포넌트 단위로 옮기는 마이그레이션 비용이 생깁니다. 따라서 라우트 5개 이상 또는 공유 상태 3개 이상이 될 때 도입을 다시 검토합니다.

## 보안 사고 대응

키 유출이 의심되면 다음 순서로 대응합니다.

1. OpenAI 대시보드에서 노출 키를 즉시 폐기합니다.
2. 새 키를 발급하고 Vercel Preview·Production 환경변수를 교체합니다.
3. 배포를 재실행하고 정상 호출을 확인합니다.
4. Git 기록과 CI 로그에서 최초 노출 커밋·사용 범위를 조사합니다.
5. 공개 커밋에 포함됐다면 기록 정리 후 협업자에게 강제 갱신을 공지합니다.
6. 사용량·결제 로그를 확인하고 비밀 검사 CI와 키 회전 주기를 보강합니다.

## 문서

- [서비스 기획서](docs/SERVICE_PLAN.md)
- [운영·장애 대응 가이드](docs/OPERATIONS.md)
- [구현 및 테스트 증빙](docs/EVIDENCE.md)
- [네이토 사전평가 기록](docs/NAITO_PRECHECK.md)
- [2차 평가 후속 검토](docs/POST_EVALUATION_REVIEW.md)
