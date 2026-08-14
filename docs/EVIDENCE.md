# 구현 및 검증 증빙

## 화면

- 데스크톱: `docs/screenshots/desktop.png`
- 모바일: `docs/screenshots/mobile.png`
- AI 결과 UX: `docs/screenshots/ai-result.png`

스크린샷은 로컬 데모 모드에서 동일한 렌더링 경로를 사용해 생성한다. 실제 운영 환경에서는 `/api/blueprint`가 OpenAI API 응답을 반환한다.

## AI 코딩 도구 활용 과정

1. Codyssey 학습 화면을 CDP로 읽어 필수 제출물, 기능 조건, 보안 제약을 구조화했다.
2. 요구사항을 서비스 아이디어, 화면 구조, AI 입출력, 실패 UX로 나누었다.
3. 생성된 HTML/CSS/JavaScript와 Python API를 단위 테스트 및 브라우저 화면으로 재검증했다.
4. 저장소에는 비밀값을 제외하고 실행·배포 재현 방법을 문서화했다.

## 확인 목록

- [x] 메뉴가 연결된 3개 이상의 섹션
- [x] Vanilla HTML/CSS/JavaScript 반응형 UI
- [x] Python `api/`와 OpenAI 호출 코드
- [x] 빈 입력·API 오류·시간 초과 UX
- [x] 환경변수 기반 비밀키 관리
- [x] 서비스 기획서와 README
- [x] GitHub 공개 저장소에 `main` 브랜치 푸시
- [ ] 실제 OpenAI 키를 설정한 배포 URL에서 최종 호출 확인
