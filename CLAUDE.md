# 미지의 CCAF 카드 — 작업 절차 (Claude 용)

박미지의 Claude Certified Architect – Foundations(CCAF) 시험 준비. 2026-09-14 에 예전 강의 노트 프로젝트를 전부 버리고 새로 시작했다(강의 대본 노트·표지·Supabase·GitHub Pages 는 사용자가 원치 않으니 되살리지 않는다). 사용자 응답은 항상 한국어.

목표: 합격(720/1000). 방식은 **문제 카드뉴스로 풀기 → Claude 와 토론 → 시험 영어 단어장 외우기**.

## 구조

- `cards/dN.json` — 영역(D1~D5)별 문제 카드. 필드 규격은 아래.
- `template.html` — 앱 화면(답안지 OMR 모티프, 카드 4장: 지문 · 보기 · 정답 · 이유와 토론, 단어장 목록·암기 카드). 디자인은 여기서만 고친다.
- `build.py` — 카드를 모아 검증(빠진 필드, 단서가 지문에 있는지), 보기 순서를 id 기준으로 섞고(원본 정답이 B·C 에 몰려 있음), 단어 빈도(전체 지문·보기에서 몇 번 나오는지)를 세어 `dist/index.html` 을 만든다.
- 아티팩트: https://claude.ai/code/artifact/543b273b-06c4-4823-88f0-0fee3b3fb520 — `dist/index.html` 을 이 `url` 로 재발행, capabilities `{"db": {}}`. 진도는 db 문서 `progress/miji` (`answers{id:{pick, ok, at, n}}`, `words{word:"known"|"learn"}`, `tries`), 없으면 localStorage.

## 문제 출처 원칙

- 인터넷의 "실제 시험 유출 덤프"(examheist, clearcatnet 류)는 가져오지 않는다. 응시 약관 위반이라 자격이 취소될 수 있고 정답도 믿기 어렵다.
- 쓰는 것: 라이선스가 분명한 커뮤니티 연습 문제(현재 hamzafarooq/claude-certified-architect, MIT), 공식 시험 가이드의 샘플 문항, 가이드 범위 안에서 Claude 가 새로 쓴 문제. 새로 쓴 문제는 `source` 필드로 구분한다.
- 정답은 Anthropic 공식 문서 기준으로 확인한다. 어긋나 보이면 `check: "doubt"` + `checkNote`.

## 카드 필드

`id`(D3-01), `domain`(1~5), `scenario`, `q_en`, `q_ko`, `options[4]{en, ko, why}`, `answer`(0-based, 원본 순서), `point_ko`(정답을 가르는 한 줄), `explain_ko[]`, `clues[{en(지문의 부분 문자열), ko}]`, `discuss_ko`(토론 거리), `words[{word, pos, ko, example}]`, `check`, `checkNote`.
- 코드·경로·명령어는 `백틱`. 이모지 금지. 한국어는 짧고 쉬운 말, 기술 용어는 영어 그대로.
- words 는 한국인 학습자가 막힐 시험 영어(misroute, idempotent, discrepancy …) 4~7개. 쉬운 단어·순수 식별자는 넣지 않는다.

## 토론

사용자가 카드의 `토론 요청 복사` 로 "CCAF D1-03 토론하자 — …" 를 붙여 오면: 해당 카드를 `cards/` 에서 읽고, 사용자의 답을 먼저 들어 준 뒤 정답 논리·그럴듯한 오답이 왜 안 되는지·실무에서는 어떤지를 대화로 푼다. 토론 중 정답이나 풀이가 틀렸다고 결론 나면 카드를 고치고 다시 빌드·발행한다.

## 빌드 · 발행 · 커밋

```bash
cd ~/ccaf-notes && python3 build.py   # 경고가 있으면 exit 1, 고친다
```
아티팩트는 같은 파일 경로로 재발행(주소 유지). 커밋은 `git add -A && git commit -m "<한국어 한 줄>"`. 원격 저장소는 없다.
