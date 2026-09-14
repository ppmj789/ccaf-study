#!/usr/bin/env python3
"""cards/*.json + guide/s*.json → dist/index.html"""
import json, re, glob, hashlib, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAINS = [
    {"id": 1, "en": "Agentic Architecture & Orchestration", "ko": "에이전트 아키텍처·오케스트레이션", "weight": 27},
    {"id": 2, "en": "Tool Design & MCP Integration", "ko": "툴 설계·MCP 연동", "weight": 18},
    {"id": 3, "en": "Claude Code Configuration & Workflows", "ko": "Claude Code 설정·워크플로우", "weight": 20},
    {"id": 4, "en": "Prompt Engineering & Structured Output", "ko": "프롬프트·구조화 출력", "weight": 20},
    {"id": 5, "en": "Context Management & Reliability", "ko": "컨텍스트 관리·신뢰성", "weight": 15},
]
SCENARIOS = [
    {"no": 1, "en": "Customer Support Resolution Agent", "ko": "고객 지원 해결 에이전트"},
    {"no": 2, "en": "Code Generation with Claude Code", "ko": "Claude Code로 코드 작성"},
    {"no": 3, "en": "Multi-Agent Research System", "ko": "멀티 에이전트 리서치 시스템"},
    {"no": 4, "en": "Developer Productivity with Claude", "ko": "Claude로 개발 생산성 도구"},
    {"no": 5, "en": "Claude Code for Continuous Integration", "ko": "CI 파이프라인의 Claude Code"},
    {"no": 6, "en": "Structured Data Extraction", "ko": "구조화 데이터 추출"},
]
# 커뮤니티 문제에 섞여 있던 옛 시나리오 이름 → 공식 번호
SCENARIO_ALIAS = {
    "Customer Support Agent": 1, "Customer Support Resolution Agent": 1,
    "Code Generation with Claude Code": 2,
    "Multi-Agent Research System": 3,
    "Developer Productivity Tools": 4, "Developer Productivity with Claude": 4,
    "Claude Code for CI/CD": 5, "Claude Code for Continuous Integration": 5,
    "Structured Data Extraction": 6,
}
# 공식 가이드 샘플(G-xx)과 같은 커뮤니티 문제는 빼고 공식 버전을 쓴다
REPLACED = {"D1-01": "G-01", "D2-01": "G-02", "D3-01": "G-04", "D1-02": "G-07", "D2-04": "G-09", "D3-09": "G-10"}
REQ = ["id", "domain", "scenario", "q_en", "q_ko", "options", "answer", "point_ko", "explain_ko", "clues", "discuss_ko", "words"]

warn = []
cards = []
seen = set()
for f in sorted(glob.glob(os.path.join(ROOT, "cards", "*.json"))):
    for c in json.load(open(f, encoding="utf-8")):
        cid = c.get("id")
        if cid in seen:
            warn.append(f"{cid}: id 중복")
            continue
        seen.add(cid)
        miss = [k for k in REQ if k not in c]
        if miss:
            warn.append(f"{cid}: 빠진 필드 {miss}")
            continue
        n = len(c["options"])
        ans = c["answer"] if isinstance(c["answer"], list) else [c["answer"]]
        sel = c.get("select", 1)
        if n not in (4, 5) or len(ans) != sel or any(not 0 <= a < n for a in ans):
            warn.append(f"{cid}: 보기/정답 형식 오류")
            continue
        if c["scenario"] not in SCENARIO_ALIAS:
            warn.append(f"{cid}: 모르는 시나리오 {c['scenario']}")
            continue
        for cl in c["clues"]:
            if cl["en"] not in c["q_en"]:
                warn.append(f"{cid}: 단서가 지문에 없음 — {cl['en'][:40]}")
        if cid in REPLACED and REPLACED[cid]:
            continue
        c["sc"] = SCENARIO_ALIAS[c["scenario"]]
        c["scenario"] = SCENARIOS[c["sc"] - 1]["en"]
        c.setdefault("source", "community")
        # 원본 정답 위치가 B·C 에 몰려 있어 id 로 고정된 순서로 보기를 섞는다
        order = sorted(range(n), key=lambda i: hashlib.md5(f"{cid}:{i}".encode()).hexdigest())
        c["options"] = [c["options"][i] for i in order]
        # 해설 속 {A}~{E} 는 원래 순서의 보기 글자 → 섞인 뒤 글자로 바꾼다
        def relabel(t, _order=order, _n=n, _id=cid):
            def sub(m):
                k = "ABCDE".index(m.group(1))
                if k >= _n:
                    warn.append(f"{_id}: 없는 보기 토큰 {m.group(0)}")
                    return m.group(0)
                return "ABCDE"[_order.index(k)]
            return re.sub(r"\{([A-E])\}", sub, t)
        for k in ("point_ko", "discuss_ko", "checkNote"):
            if isinstance(c.get(k), str):
                c[k] = relabel(c[k])
        c["explain_ko"] = [relabel(x) for x in c["explain_ko"]]
        for o in c["options"]:
            o["why"] = relabel(o.get("why", ""))
        mapped = sorted(order.index(a) for a in ans)
        c["answer"] = mapped if sel > 1 else mapped[0]
        cards.append(c)

SRC_ORDER = {"official": 0, "community": 1, "claude": 2}
cards.sort(key=lambda c: (c["sc"], SRC_ORDER.get(c["source"], 9), c["id"]))

# 시나리오 공부 자료
guide = []
GREQ = ["no", "name_en", "name_ko", "domains", "oneline_ko", "description", "story_ko", "flow", "cast", "patterns", "checklist_ko"]
for f in sorted(glob.glob(os.path.join(ROOT, "guide", "s*.json"))):
    g = json.load(open(f, encoding="utf-8"))
    miss = [k for k in GREQ if k not in g]
    if miss:
        warn.append(f"guide {os.path.basename(f)}: 빠진 필드 {miss}")
        continue
    guide.append(g)
    SCENARIOS[g["no"] - 1]["ko"] = g["name_ko"]
guide.sort(key=lambda g: g["no"])

# 단어장: 카드들의 words 를 합치고, 전체 지문·보기에서 몇 번 나오는지 센다
corpus = " ".join((c["q_en"] + " " + " ".join(o["en"] for o in c["options"])).lower() for c in cards)
words = {}
for c in cards:
    for w in c["words"]:
        key = w["word"].strip().lower()
        e = words.setdefault(key, {"word": key, "pos": w.get("pos", ""), "ko": w["ko"], "examples": [], "ids": []})
        if c["id"] not in e["ids"]:
            e["ids"].append(c["id"])
            e["examples"].append({"id": c["id"], "text": w.get("example", "")})

def count(word):
    stem = re.escape(word)
    if " " not in word and len(word) > 4:
        stem = re.escape(word[:-1] if word.endswith("e") else word) + r"\w{0,4}"
    return len(re.findall(r"\b" + stem + r"\b", corpus))

for e in words.values():
    e["freq"] = max(count(e["word"]), len(e["ids"]))
wordlist = sorted(words.values(), key=lambda e: (-e["freq"], e["word"]))

site = {}
if os.path.exists(os.path.join(ROOT, "site.json")):
    site = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))

data = {"site": site, "domains": DOMAINS, "scenarios": SCENARIOS, "cards": cards, "words": wordlist, "guide": guide,
        "source": {"name": "hamzafarooq/claude-certified-architect", "url": "https://github.com/hamzafarooq/claude-certified-architect", "license": "MIT"}}

tpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
out = tpl.replace("/*__DATA__*/null", payload)
os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
open(os.path.join(ROOT, "dist", "index.html"), "w", encoding="utf-8").write(out)

by_sc = {s["no"]: sum(1 for c in cards if c["sc"] == s["no"]) for s in SCENARIOS}
by_src = {k: sum(1 for c in cards if c["source"] == k) for k in SRC_ORDER}
multi = sum(1 for c in cards if c.get("select", 1) > 1)
doubts = [c["id"] for c in cards if c.get("check") == "doubt"]
print(f"카드 {len(cards)}장 (시나리오별 {by_sc}, 출처 {by_src}, 복수 선택 {multi}) · 단어 {len(wordlist)}개 · 공부 자료 {len(guide)}편 · 정답 확인 필요 {doubts or '없음'}")
for w in warn:
    print("경고:", w)
sys.exit(1 if warn else 0)
