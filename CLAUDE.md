# 미지의 CCAF 카드 — 작업 절차 (Claude 용)

박미지의 Claude Certified Architect – Foundations(CCAF) 시험 준비. 2026-09-14 에 예전 강의 노트 프로젝트를 전부 버리고 새로 시작했다(강의 대본 노트·표지·Supabase·GitHub Pages 는 사용자가 원치 않으니 되살리지 않는다). 사용자 응답은 항상 한국어.

목표: 합격(720/1000). 방식은 **시험 화면처럼 문제 풀기 → Claude 와 토론 → 시험 영어 단어장 외우기**.

## 구조

- `cards/*.json` — 문제 카드. `d1~d5.json` 커뮤니티(MIT) 문제, `official.json` 공식 가이드 9장 샘플 G-01~12, `new-sN.json` Claude 가 가이드 Task Statement 근거로 쓴 문제(C{시나리오}-nn). 공식 샘플과 겹치는 커뮤니티 문제 6개는 build.py 의 `REPLACED` 로 뺀다.
- `guide/sN.json` — 시나리오 1~6 공부 자료(공식 설명 영어 원문·한국어, 쉽게 풀기, 흐름, 용어, 판단 포인트와 가이드 원문 근거, 비교표, 체크리스트). 앱의 `시나리오 공부` 화면이 그린다. 근거 원문은 공식 시험 가이드 PDF(CCAR-F, 2026-07).
- `template.html` — 앱 화면. **실제 컴퓨터 시험(CBT) 화면처럼**: 지문과 보기를 한 화면에, 상단 바(문항 번호·남은 시간), 하단 바(이전·검토 표시·검토 화면·다음). 처음 화면에서 연습 모드(바로 채점, 풀이·보기별 해설·토론 거리가 아래에) / 모의고사(문항당 2분, 끝나고 성적표·환산 점수) / 단어장(표·암기 카드). 사용자가 카드뉴스·OMR 같은 꾸밈 디자인은 불편하다고 해서 뺐으니 다시 넣지 않는다. 디자인은 여기서만 고친다.
- `build.py` — 카드를 모아 검증(빠진 필드, 단서가 지문에 있는지), 보기 순서를 id 기준으로 섞고(원본 정답이 B·C 에 몰려 있음), 단어 빈도(전체 지문·보기에서 몇 번 나오는지)를 세어 `dist/index.html` 을 만든다.
- 아티팩트: https://claude.ai/code/artifact/543b273b-06c4-4823-88f0-0fee3b3fb520 — `dist/index.html` 을 이 `url` 로 재발행, capabilities `{"db": {}}`. 진도는 db 문서 `progress/miji` (`answers{id:{pick, ok, at, n}}`, `words{word:"known"|"learn"}`, `tries`), 없으면 localStorage.
- **공개 주소(로그인 불필요, 휴대폰용)**: https://ppmj789.github.io/ccaf-study/ — GitHub 저장소 https://github.com/ppmj789/ccaf-study (공개, 브랜치 `main`). push 하면 `.github/workflows/pages.yml` 이 build 해서 배포한다. 기록은 Supabase 프로젝트 `ccaf-study`(ref `whmmrsgblocqhdjalojm`, 서울, 무료)에 **동기화 암호** 방식으로 저장한다: 기기마다 같은 암호를 입력하면 앱이 `sha256("ccaf-study:"+암호)` 를 열쇠로 `load_progress`/`save_progress` RPC 를 부른다. 테이블 `study_progress` 는 직접 접근이 막혀 있다(`supabase/schema.sql`). `site.json` 에는 공개용 publishable key 만 둔다(secret/service_role 키·액세스 토큰은 절대 커밋하지 않는다). DB 비밀번호는 `~/.config/ccaf-study/db-password`. 계정의 다른 프로젝트 UntoldChapters 는 이 앱과 무관하니 건드리지 않는다. claude.ai 아티팩트는 CSP 때문에 Supabase 에 못 붙어 계정 db 를 쓰고, 둘 사이는 처음 화면 `기기 간 저장 → 코드로 옮기기` 로 옮긴다.

## 문제 출처 원칙

- 인터넷의 "실제 시험 유출 덤프"(examheist, clearcatnet 류)는 가져오지 않는다. 응시 약관 위반이라 자격이 취소될 수 있고 정답도 믿기 어렵다.
- 쓰는 것: 라이선스가 분명한 커뮤니티 연습 문제(현재 hamzafarooq/claude-certified-architect, MIT), 공식 시험 가이드의 샘플 문항, 가이드 범위 안에서 Claude 가 새로 쓴 문제. 새로 쓴 문제는 `source` 필드로 구분한다.
- 정답은 Anthropic 공식 문서 기준으로 확인한다. 어긋나 보이면 `check: "doubt"` + `checkNote`.

## 카드 필드

`id`, `domain`(1~5), `scenario`(공식 6개 이름, 옛 이름은 build 가 맞춤), `source`(official/community/claude), `ts`·`guide_en`(가이드 근거), `select`(여러 개 고르는 문항이면 2, `answer` 는 배열), `q_en`, `q_ko`, `options[4]{en, ko, why}`, `answer`(0-based, 원본 순서), `point_ko`(정답을 가르는 한 줄), `explain_ko[]`, `clues[{en(지문의 부분 문자열), ko}]`, `discuss_ko`(토론 거리), `words[{word, pos, ko, example}]`, `check`, `checkNote`.
- 한국어 해설에서 보기를 가리키는 글자는 반드시 `{A}`~`{E}` 토큰으로 쓴다(원래 options 순서 기준). build 가 보기를 섞은 뒤 글자로 바꾼다. 맨 글자 A/B 를 쓰면 섞인 뒤 어긋난다.
- 코드·경로·명령어는 `백틱`. 이모지 금지. 한국어는 짧고 쉬운 말, 기술 용어는 영어 그대로.
- words 는 한국인 학습자가 막힐 시험 영어(misroute, idempotent, discrepancy …) 4~7개. 쉬운 단어·순수 식별자는 넣지 않는다.

## 토론

사용자가 카드의 `토론 요청 복사` 로 "CCAF D1-03 토론하자 — …" 를 붙여 오면: 해당 카드를 `cards/` 에서 읽고, 사용자의 답을 먼저 들어 준 뒤 정답 논리·그럴듯한 오답이 왜 안 되는지·실무에서는 어떤지를 대화로 푼다. 토론 중 정답이나 풀이가 틀렸다고 결론 나면 카드를 고치고 다시 빌드·발행한다.

## 빌드 · 발행 · 커밋

```bash
cd ~/ccaf-notes && python3 build.py   # 경고가 있으면 exit 1, 고친다
```
아티팩트는 같은 파일 경로(또는 위 url)로 재발행하고, 커밋 뒤 `git push` 로 공개 주소도 갱신한다(둘 다 매번). 커밋은 `git add -A && git commit -m "<한국어 한 줄>"`. `gh` 는 `~/bin/gh`.
