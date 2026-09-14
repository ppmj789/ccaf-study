#!/usr/bin/env python3
"""cards/*.json + words 빈도 → dist/index.html"""
import json, re, glob, hashlib, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAINS = [
    {"id": 1, "en": "Agentic Architecture & Orchestration", "ko": "에이전트 아키텍처·오케스트레이션", "weight": 27},
    {"id": 2, "en": "Tool Design & MCP Integration", "ko": "툴 설계·MCP 연동", "weight": 18},
    {"id": 3, "en": "Claude Code Configuration & Workflows", "ko": "Claude Code 설정·워크플로우", "weight": 20},
    {"id": 4, "en": "Prompt Engineering & Structured Output", "ko": "프롬프트·구조화 출력", "weight": 20},
    {"id": 5, "en": "Context Management & Reliability", "ko": "컨텍스트 관리·신뢰성", "weight": 15},
]
REQ = ["id", "domain", "scenario", "q_en", "q_ko", "options", "answer", "point_ko", "explain_ko", "clues", "discuss_ko", "words"]

warn = []
cards = []
for f in sorted(glob.glob(os.path.join(ROOT, "cards", "d*.json"))):
    for c in json.load(open(f, encoding="utf-8")):
        miss = [k for k in REQ if k not in c]
        if miss:
            warn.append(f"{c.get('id')}: 빠진 필드 {miss}")
            continue
        if len(c["options"]) != 4 or not 0 <= c["answer"] < 4:
            warn.append(f"{c['id']}: 보기/정답 형식 오류")
        for cl in c["clues"]:
            if cl["en"] not in c["q_en"]:
                warn.append(f"{c['id']}: 단서가 지문에 없음 — {cl['en'][:40]}")
        # 원본 정답 위치가 B·C 에 몰려 있어 id 로 고정된 순서로 보기를 섞는다
        order = sorted(range(4), key=lambda i: hashlib.md5(f"{c['id']}:{i}".encode()).hexdigest())
        c["options"] = [c["options"][i] for i in order]
        c["answer"] = order.index(c["answer"])
        cards.append(c)

cards.sort(key=lambda c: (c["domain"], c["id"]))

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
    # 사전형 뒤에 붙는 흔한 어미까지 센다 (misroute → misrouted, misrouting)
    if " " not in word and len(word) > 4:
        stem = re.escape(word[:-1] if word.endswith("e") else word) + r"\w{0,4}"
    return len(re.findall(r"\b" + stem + r"\b", corpus))

for e in words.values():
    e["freq"] = max(count(e["word"]), len(e["ids"]))
wordlist = sorted(words.values(), key=lambda e: (-e["freq"], e["word"]))

data = {"domains": DOMAINS, "cards": cards, "words": wordlist,
        "source": {"name": "hamzafarooq/claude-certified-architect", "url": "https://github.com/hamzafarooq/claude-certified-architect", "license": "MIT"}}

tpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
out = tpl.replace("/*__DATA__*/null", payload)
os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
open(os.path.join(ROOT, "dist", "index.html"), "w", encoding="utf-8").write(out)

doubts = [c["id"] for c in cards if c.get("check") == "doubt"]
print(f"카드 {len(cards)}장 · 단어 {len(wordlist)}개 · 정답 확인 필요 {doubts or '없음'}")
for w in warn:
    print("경고:", w)
sys.exit(1 if warn else 0)
