# 네이토 사전평가 결과

- 저장소: https://github.com/Anyoungju/CODYSSEY2-3
- 브랜치: `main`
- 점수: **74% (14/19)**

## 항목별 결과

### #1 — PASS

- 근거: README.md > '데모 페이지: <https://anyoungju.github.io/CODYSSEY2-3/>' | index.html > '<a href="#why">서비스 소개</a>'
- 잘한 점: 배포 URL과 내비게이션 링크로 섹션 기반 이동을 명시했음
- 부족한 점: 메뉴 이동 외 배포 상태(실제 호출 성공 여부) 스크린샷 보완 권장
- 보완: 데모 호출 성공 화면 또는 운영 배포 스크린샷을 README에 추가

### #2 — PASS

- 근거: css/styles.css > '@media(max-width:820px){.site-header nav{display:none}'
- 잘한 점: 명확한 미디어쿼리로 모바일 레이아웃을 제공함
- 부족한 점: 모바일 특정 상호작용(터치/포커스) 검증 결과 서술 부족
- 보완: 모바일 스크린샷과 주요 요소의 터치 동작 검증을 문서에 덧붙이기

### #3 — PASS

- 근거: api/blueprint.py > 'client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=18.0, max_retries=1)' | js/app.js > 'const response = await fetch(getBlueprintEndpoint(), '
- 잘한 점: 프론트→서버리스→OpenAI 흐름이 코드상으로 명확히 연결되어 있음
- 부족한 점: 실제 운영 호출 로그나 예시 응답 캡처가 없어 동작 검증 증빙 부족
- 보완: 운영 환경에서의 성공 응답 예시(스크린샷 또는 로그)를 추가

### #4 — PASS

- 근거: api/blueprint.py > 'if len(idea) > MAX_IDEA_LENGTH: raise ValueError(f"아이디어는 {MAX_IDEA_LENGTH}자 이내로 입력해 주세요.")' | js/app.js > 'if (new URLSearchParams(location.search).get("demo") === "1") {'
- 잘한 점: 빈·과도한 입력 검증과 데모(정상) 모드가 구현되어 있음
- 부족한 점: 테스트 케이스 목록(2~3개)과 결과 캡처가 문서에 더 필요함
- 보완: README 또는 docs에 정상/빈/긴 입력별 재현 스텝과 결과 스크린샷 추가

### #5 — PASS

- 근거: js/app.js > '아이디어를 한 문장 이상 입력해 주세요.' | api/blueprint.py > 'AI 응답 시간이 초과되었습니다. 다시 시도해 주세요.'
- 잘한 점: 클라이언트·서버 양쪽에서 빈입력·지연·오류 메시지를 처리함
- 부족한 점: 사용자에게 보이는 메시지의 언어 일관성·표현 우선순위 예시 부족
- 보완: 각 실패 시나리오별 UI 흐름(알림 위치·재시도 버튼 등)을 예시로 문서화

### #6 — PASS

- 근거: .env.example > 'OPENAI_API_KEY=your_openai_api_key'
- 잘한 점: 환경변수 사용 예시와 .env.example로 키 비노출 원칙을 지킴
- 부족한 점: 코드·커밋 기록에 실제 키가 없는지 자동 검사 언급 없음
- 보완: README에 .gitignore/CI 검사 등 키 유출 방지 체크리스트를 추가

### #7 — PASS

- 근거: README.md > '- 상세 기획: [docs/SERVICE_PLAN.md](docs/SERVICE_PLAN.md)'
- 잘한 점: README·기획서·배포 URL을 문서로 연결해 제출 패키지를 제공함
- 부족한 점: 제출물 내 스크린샷·운영 호출 증빙이 일부 로컬 데모로 표기되어 실제 운영 증빙 미완료
- 보완: 운영 환경에서의 호출 스크린샷과 테스트 결과를 docs/EVIDENCE.md에 추가

### #8 — PASS

- 근거: docs/SERVICE_PLAN.md > '비밀키는 서버의 `OPENAI_API_KEY` 환경변수에서만 읽으며 코드, 브라우저, 문서에 기록하지 않는다.'
- 잘한 점: 프론트/백엔드 분리 및 보안 이유를 문서에서 설명함
- 부족한 점: 구조 분리의 기술적 경계(파일·엔드포인트 목록)도 함께 제시하면 더 명확함
- 보완: 프로젝트 구조(파일별 책임)를 README에 간단 표로 추가

### #9 — PASS

- 근거: js/app.js > 'button.disabled = true; button.classList.add("loading"); status.textContent = "아이디어의 방향을 읽고 있어요…"; '
- 잘한 점: 로딩·성공·실패 상태와 버튼 비활성화로 상태 처리를 구현함
- 부족한 점: 상태관리(여러 컴포넌트 간 상태 공유) 전략 설명은 간략함
- 보완: 상태 변화 시나리오 다이어그램이나 간단한 설명을 문서에 덧붙이기

### #10 — PASS

- 근거: api/blueprint.py > 'if not isinstance(payload, dict):'
- 잘한 점: 서버리스 함수에서 입력 검증과 예외 대응을 명확히 구현함
- 부족한 점: 응답 포맷(성공·실패 스키마 예시)을 문서화한 별도 표가 없음
- 보완: API 응답 예시(JSON 성공·오류)를 README 또는 docs에 추가

### #11 — FAIL

- 근거: README.md > 'Vercel에서는 Project Settings → Environment Variables에 `OPENAI_API_KEY`를 등록한 뒤 다시 배포합니다.'
- 잘한 점: -
- 부족한 점: 배포 문제 진단(로그·콘솔 확인 방법)이 문서에 명시되어 있지 않음
- 보완: 배포 실패 시 확인할 Vercel 로그 위치·콘솔 명령과 재배포 절차를 문서화하세요

### #12 — FAIL

- 근거: docs/SERVICE_PLAN.md > '프론트엔드: Vanilla HTML/CSS/JavaScript'
- 잘한 점: -
- 부족한 점: HTML/CSS/JS 각각의 역할(무엇을 담당하는지)을 분명히 설명한 항목이 부족함
- 보완: 각 기술의 책임(구조·스타일·동작)을 한두 문장으로 정리해 추가하세요

### #13 — PASS

- 근거: js/app.js > 'const response = await fetch(getBlueprintEndpoint(), {method: "POST"' | js/app.js > 'renderBlueprint(blueprint);'
- 잘한 점: fetch로 서버리스 호출 후 응답을 렌더링하는 흐름이 구현되어 있음
- 부족한 점: fetch 에러→UI 반영의 구체적 로깅(서버 응답 코드별 처리) 예시 부족
- 보완: 서버 오류 코드별 사용자 메시지와 개발용 콘솔 로그 예시를 문서에 추가

### #14 — PASS

- 근거: docs/SERVICE_PLAN.md > '비밀키는 서버의 `OPENAI_API_KEY` 환경변수에서만 읽으며 코드, 브라우저, 문서에 기록하지 않는다.'
- 잘한 점: 환경변수 사용 이유(보안·운영)를 명확히 기술함
- 부족한 점: 운영별(스테이징/프로덕션) 환경변수 관리 전략 예시가 없음
- 보완: 환경별 변수 네이밍·배포 방식(스테이징/프로덕션) 가이드를 간단히 추가하세요

### #15 — PASS

- 근거: api/blueprint.py > '당신은 초보 개발자의 아이디어를 작고 검증 가능한 웹 서비스로 바꾸는 제품 코치입니다.'
- 잘한 점: 프롬프트 목적과 출력 스키마를 SYSTEM_PROMPT로 코드에 직접 명시함
- 부족한 점: 프롬프트 개선 포인트(예: 온도·응답 길이)와 샘플 변형 설명은 부족함
- 보완: 프롬프트 버전 예시와 변경 시 기대 효과(품질/비용)를 문서로 남기기

### #16 — PASS

- 근거: README.md > 'AI 요청 제한 시간은 18초, 재시도는 1회로 제한합니다.'
- 잘한 점: 타임아웃·재시도·모델 교체로 지연·비용을 관리하는 방안을 제시함
- 부족한 점: 구체적 속도 개선 옵션(비동기 캐시, 모델 축소 등) 예시는 더 필요함
- 보완: 지연 저감과 비용 절충(서버 캐시·라이트 모델 등) 선택지를 문서에 정리하세요

### #17 — FAIL

- 근거: README.md > '실제 공개 운영 전에는 사용자별 호출 제한과 사용량 알림을 추가하세요.'
- 잘한 점: -
- 부족한 점: 프론트·백엔드 확장(구체적 아키텍처 변경 범위)이 문서화되어 있지 않음
- 보완: 프론트 기능 확장 포인트와 백엔드 확장(큐·캐시·인증) 추천 항목을 정리하세요

### #18 — FAIL

- 근거: README.md > 'API 키는 절대 Git에 커밋하지 않습니다.'
- 잘한 점: -
- 부족한 점: API 키 유출 시 즉각 대책(키 회수/롤백·통지)과 장기 재발 방지 계획이 제시되지 않음
- 보완: 유출 발견 시 단계별 조치(키 폐기·재발급·로그 조사)를 문서로 명시하세요

### #19 — FAIL

- 근거: README.md > 'Frontend: HTML5, CSS3, Vanilla JavaScript'
- 잘한 점: -
- 부족한 점: 프레임워크 사용 시 장단점 및 변경 범위(파일·구현 영향)가 설명되어 있지 않음
- 보완: 프레임워크 도입 시 기대 이점과 마이그레이션 영향 범위를 비교 표로 정리하세요
