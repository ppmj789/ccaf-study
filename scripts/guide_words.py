"""CCAR-F 가이드 대역본 HTML 의 단어 풀이(ul.notes)를 뽑아 words/guide.json 을 만든다.
가이드 원문 문장은 저장하지 않는다(단어·뜻·나오는 위치만).
사용: python3 scripts/guide_words.py "<대역본.html 경로>"
"""
import json, os, re, sys
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.sec, self.stack = [], "", []
        self.mode = None      # "head" | "b" | "span"
        self.buf, self.cur, self.head_en = "", None, False
    def handle_starttag(self, tag, a):
        a = dict(a); cls = a.get("class", "")
        if tag in ("h2", "h3", "h4") and cls in ("h1", "h2", "h3"):
            self.mode, self.buf, self.htag = "head", "", tag
        elif self.mode == "head" and tag == "span":
            self.head_en = a.get("class") == "h-ko"
        elif tag == "ul" and cls == "notes":
            self.in_notes = True
        elif getattr(self, "in_notes", False) and tag == "b":
            self.mode, self.buf = "b", ""
        elif getattr(self, "in_notes", False) and tag == "span" and self.cur is not None:
            self.mode, self.buf = "span", ""
    def handle_endtag(self, tag):
        if self.mode == "head" and tag == getattr(self, "htag", None):
            self.mode = None
        elif self.mode == "head" and tag == "span" and self.head_en:
            self.sec, self.head_en = self.buf.strip(), False
        elif self.mode == "b" and tag == "b":
            self.cur, self.mode = self.buf.strip(), None
        elif self.mode == "span" and tag == "span":
            self.out.append({"word": self.cur, "ko": self.buf.strip(), "sec": self.sec})
            self.cur, self.mode = None, None
        elif tag == "ul":
            self.in_notes = False
    def handle_data(self, d):
        if self.mode == "head" and not self.head_en:
            return
        if self.mode:
            self.buf += d

# 시험 문제 풀이와 상관없는 시험 운영·안내용 단어는 뺀다(2026-09-18 사용자 요청: "effective July 2026 이런 단어는 지워라")
# 머리말(날짜·개정 문구), 3장 시험 정보, 4장 비중표, 10~16장 채점·접수·정책·서약·갱신·지원 절 전체, 그리고 가이드 자체를 설명하는 표현
SKIP_SECS = re.compile(r"^(3|4|1[0-6])\. ")
SKIP_WORDS = {"sit the exam", "validates that ~", "ideal candidate", "frames a set of questions", "task statement",
              "measured against ~", "written against ~", "build ~", "in-scope", "out-of-scope"}

p = P(); p.feed(open(sys.argv[1], encoding="utf-8").read())
seen = {}
for i, x in enumerate(p.out):
    if not x["sec"] or SKIP_SECS.match(x["sec"]) or x["word"].lower() in SKIP_WORDS:
        continue
    key = x["word"].lower()
    if key in seen:
        seen[key]["n"] += 1
        continue
    seen[key] = {"word": x["word"], "ko": x["ko"], "sec": x["sec"], "order": len(seen), "n": 1}
out = list(seen.values())
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "words", "guide.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"풀이 {len(p.out)}개 · 단어 {len(out)}개")
