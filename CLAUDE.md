# 미지의 CCAF 카드 — 작업 절차 (Claude 용)

박미지의 Claude Certified Architect – Foundations(CCAF) 시험 준비. 2026-09-14 에 예전 강의 노트 프로젝트를 전부 버리고 새로 시작했다(강의 대본 노트·표지·Supabase·GitHub Pages 는 사용자가 원치 않으니 되살리지 않는다). 사용자 응답은 항상 한국어.

목표: 합격(720/1000). 방식은 **시험 화면처럼 문제 풀기 → Claude 와 토론 → 시험 영어 단어장 외우기**.

## 구조

- `cards/*.json` — 문제 카드. `d1~d5.json` 커뮤니티(MIT) 문제, `official.json` 공식 가이드 9장 샘플 G-01~12, `new-sN.json` Claude 가 가이드 Task Statement 근거로 쓴 문제(C{시나리오}-nn). 공식 샘플과 겹치는 커뮤니티 문제 6개는 build.py 의 `REPLACED` 로 뺀다.
- `cards/ai-dN.json` — AI 문제(A{도메인}-nn, Task Statement마다 2개). `source: "claude"` 인 문제(C·A 접두)는 모두 `AI 문제 검수` 칸에만 나오고, 사용자가 `괜찮아요` 한 것만 일반 연습·모의고사에 들어간다. 검수 결과는 진도의 `reviews{id:{v:"ok"|"bad", reason, at}}`. 사용자가 "이상해요 고쳐줘"라고 하면 Supabase 행(동기화 암호 해시)을 읽어 bad 사유를 보고 카드를 고친다. 새 AI 문제는 작성 에이전트와 별도의 검증 에이전트(정답을 가린 blind 풀이 → 비교 → 보정)를 거친다. 오답노트는 `wrongs{id:{n,at,first,fixedAt}}`, 메모는 `notes{id:{text,at}}`.
- `words/extra.json` — 추가 단어장(시험 질문 표현 phrase, 가이드 핵심어 guide). `freq` 는 가이드 원문 기준으로 미리 계산해 둔 값(가이드 전문은 저장소에 두지 않는다).
- `words/guide.json` — 단어장 `가이드 단어` 탭(기본 탭). 바탕화면 `CCAR-F 가이드 대역본.html` 의 단어 풀이(`ul.notes`)를 `python3 scripts/guide_words.py "/mnt/c/Users/JeKim/Desktop/CCAR-F 가이드 대역본.html"` 로 뽑은 것(단어·뜻·나오는 절·순서만, 원문 문장은 저장하지 않음). 시험 운영·안내용 단어(머리말 날짜 문구, 3·4장 시험 정보·비중표, 10~16장 채점·접수·정책·서약·갱신·지원, "sit the exam"·"task statement" 같은 가이드 자체 설명)는 `SKIP_SECS`·`SKIP_WORDS` 로 뺀다(사용자 요청). 가이드 순서로 외우고 부분(도메인 1~5 등)으로 거른다. 기존 카드·phrase·guide 단어는 `문제 단어` 탭. 외움 표시는 두 탭이 `words{}` 를 같이 쓴다.
- 가이드 대역본 원본 HTML 은 평문으로 공개 저장소·GitHub Pages 에 올리지 않는다. 사용자 요청(2026-09-18)으로 **비밀번호 암호화본**만 `locked/guide.html` 에 두고 https://ppmj789.github.io/ccaf-study/guide.html 로 배포한다(로그인 없이 비밀번호로 열림, noindex). 만들기: `GUIDE_PW="$(cat ~/.config/ccaf-study/guide-password)" node scripts/lock_guide.mjs "/mnt/c/Users/JeKim/Desktop/CCAR-F 가이드 대역본.html"` → build.py 가 `locked/*` 를 dist 로 복사. 비밀번호는 `~/.config/ccaf-study/guide-password` (커밋 금지). 지울 때는 `locked/guide.html` 을 삭제하고 push(암호문은 git 기록에는 남음). 같은 내용의 비공개 claude.ai 아티팩트도 있다: https://claude.ai/artifact/SGChedYGunF7VYyZR8GEF4
- `guide/sN.json` — 시나리오 1~6 공부 자료(공식 설명 영어 원문·한국어, 쉽게 풀기, 흐름, 용어, 판단 포인트와 가이드 원문 근거, 비교표, 체크리스트). 앱의 `시나리오 공부` 화면이 그린다. 근거 원문은 공식 시험 가이드 PDF(CCAR-F, 2026-07).
- `template.html` — 앱 화면. **실제 컴퓨터 시험(CBT) 화면처럼**: 지문과 보기를 한 화면에, 상단 바(문항 번호·남은 시간), 하단 바(이전·검토 표시·검토 화면·다음). 처음 화면에서 연습 모드(바로 채점, 풀이·보기별 해설·토론 거리가 아래에) / 모의고사(문항당 2분, 끝나고 성적표·환산 점수) / 단어장(표·암기 카드). 사용자가 카드뉴스·OMR 같은 꾸밈 디자인은 불편하다고 해서 뺐으니 다시 넣지 않는다. **2026-09-18 부터 처음 화면에는 `가이드 대역본`·`단어장`·(연결 안 된 기기만) `기록 저장 (DB)` 칸만 둔다.** 시나리오 공부·연습 모드·AI 문제 검수·오답노트·모의고사 칸은 사용자 요청으로 뺐다(화면 코드는 남아 있어 단어장 예문의 문항 링크로는 열림). 사용자가 다시 요청하기 전에는 되살리지 않는다. 앱을 열면 단어장이 아니면 처음 화면에서 시작한다. 디자인은 여기서만 고친다.
- `build.py` — 카드를 모아 검증(빠진 필드, 단서가 지문에 있는지), 보기 순서를 id 기준으로 섞고(원본 정답이 B·C 에 몰려 있음), 단어 빈도(전체 지문·보기에서 몇 번 나오는지)를 세어 `dist/index.html` 을 만든다.
- 사용자는 **공개 주소만** 쓴다(2026-09-18). claude.ai 앱 아티팩트(https://claude.ai/code/artifact/543b273b-06c4-4823-88f0-0fee3b3fb520)는 더 갱신하지 않고, 앱에서 claude.ai 계정 db 저장과 `코드로 옮기기` 기능은 지웠다. 되살리지 않는다.
- **공개 주소(로그인 불필요, 휴대폰용)**: https://ppmj789.github.io/ccaf-study/ — GitHub 저장소 https://github.com/ppmj789/ccaf-study (공개, 브랜치 `main`). push 하면 `.github/workflows/pages.yml` 이 build 해서 배포한다. 기록은 Supabase 프로젝트 `ccaf-study`(ref `whmmrsgblocqhdjalojm`, 서울, 무료)에 **동기화 암호** 방식으로 저장한다: 기기마다 같은 암호를 입력하면 앱이 `sha256("ccaf-study:"+암호)` 를 열쇠로 `load_progress`/`save_progress` RPC 를 부른다. 테이블 `study_progress` 는 직접 접근이 막혀 있다(`supabase/schema.sql`). `site.json` 에는 공개용 publishable key 만 둔다(secret/service_role 키·액세스 토큰은 절대 커밋하지 않는다). DB 비밀번호는 `~/.config/ccaf-study/db-password`. 계정의 다른 프로젝트 UntoldChapters 는 이 앱과 무관하니 건드리지 않는다. 처음 화면의 `기록 저장 (DB)` 칸은 이 기기가 DB 에 연결 안 됐거나 연결이 실패했을 때만 보인다. 연결된 기기는 상단 표시(`동기화 HH:MM`, 누르면 바로 동기화)만 남는다.

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
커밋 뒤 `git push` 로 공개 주소를 갱신한다(Actions 가 build·배포). claude.ai 아티팩트는 재발행하지 않는다. 커밋은 `git add -A && git commit -m "<한국어 한 줄>"`. `gh` 는 `~/bin/gh`.
