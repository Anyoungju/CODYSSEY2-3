# Codyssey Compass

막연한 웹 서비스 아이디어를 실행 가능한 MVP 청사진으로 바꾸는 AI 프로젝트 내비게이터입니다. Codyssey의 **AI 웹 개발: 내 아이디어를 현실로** 미션 결과물로 제작했습니다.

- GitHub: <https://github.com/Anyoungju/CODYSSEY2-3>
- 데모 페이지: <https://anyoungju.github.io/CODYSSEY2-3/>
- AI API: `https://codyssey-compass.vercel.app/api/blueprint`

> GitHub Pages는 정적 프론트엔드를 제공하며, AI 생성 요청은 Vercel의 Python API로 전달됩니다. Vercel 프로젝트에는 `OPENAI_API_KEY`가 등록되어 있다고 가정합니다.

## 주요 기능

- 아이디어, 대상 사용자, 우선 조건을 바탕으로 AI 프로젝트 청사진 생성
- 3개 이상의 화면 구성, AI 입출력, 4단계 개발 순서, 위험 요소 제안
- 빈 입력·API 실패·시간 초과에 대한 사용자 안내
- 모바일 반응형 화면과 라이트/다크 테마
- 브라우저에 API 키를 노출하지 않는 Python 서버리스 API

## 기술 스택

- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Python 3.12+, Vercel Functions
- AI: OpenAI Responses API (`gpt-5.4-mini`, 환경변수로 변경 가능)
- Test: Python `unittest`

## 프로젝트 구조

```text
├── index.html
├── css/styles.css
├── js/app.js
├── api/blueprint.py
├── tests/test_blueprint.py
├── docs/
├── requirements.txt
└── vercel.json
```

## 로컬 실행

정적 화면과 데모 결과를 확인합니다. 데모 모드는 OpenAI를 호출하지 않으며 화면 검증 전용입니다.

```powershell
python -m http.server 8000
```

브라우저에서 `http://localhost:8000/?demo=1`을 엽니다. 운영과 동일한 API 호출을 로컬에서 시험하려면 Vercel CLI가 필요합니다.

```powershell
vercel dev
```

## 환경변수

`.env.example`을 참고해 로컬 또는 Vercel 프로젝트에 설정합니다.

```dotenv
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.4-mini
ALLOWED_ORIGIN=https://anyoungju.github.io
```

API 키는 절대 Git에 커밋하지 않습니다. Vercel에서는 Project Settings → Environment Variables에 `OPENAI_API_KEY`를 등록한 뒤 다시 배포합니다.

## 테스트

```powershell
python -m unittest discover -s tests -v
```

## 배포

GitHub 저장소를 Vercel에 Import한 뒤 환경변수를 등록하면 별도 빌드 설정 없이 정적 사이트와 `api/blueprint.py`가 함께 배포됩니다.

- 프론트엔드 데모: <https://anyoungju.github.io/CODYSSEY2-3/>
- Vercel API: <https://codyssey-compass.vercel.app/api/blueprint>
- 상세 기획: [docs/SERVICE_PLAN.md](docs/SERVICE_PLAN.md)
- 구현 증빙: [docs/EVIDENCE.md](docs/EVIDENCE.md)

## 보안 및 비용

- OpenAI 키는 서버 환경변수에서만 읽습니다.
- 입력은 600자, 요청 본문은 8KB로 제한합니다.
- AI 요청 제한 시간은 18초, 재시도는 1회로 제한합니다.
- 실제 공개 운영 전에는 사용자별 호출 제한과 사용량 알림을 추가하세요.
