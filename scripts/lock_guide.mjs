// 가이드 대역본 HTML 을 비밀번호로 암호화해 locked/guide.html 을 만든다.
// 저장소에는 암호문만 들어간다(PBKDF2-SHA256 60만 회 + AES-GCM). 비밀번호는 커밋하지 않는다.
// 사용: GUIDE_PW='비밀번호' node scripts/lock_guide.mjs "<대역본.html 경로>"
import { readFileSync, writeFileSync } from "node:fs";
import { webcrypto as c } from "node:crypto";

const pw = process.env.GUIDE_PW;
if (!pw) { console.error("GUIDE_PW 가 필요해요"); process.exit(1); }
const plain = readFileSync(process.argv[2]);
const ITER = 600000;
const salt = c.getRandomValues(new Uint8Array(16)), iv = c.getRandomValues(new Uint8Array(12));
const base = await c.subtle.importKey("raw", new TextEncoder().encode(pw), "PBKDF2", false, ["deriveKey"]);
const key = await c.subtle.deriveKey({ name: "PBKDF2", salt, iterations: ITER, hash: "SHA-256" }, base, { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
const ct = new Uint8Array(await c.subtle.encrypt({ name: "AES-GCM", iv }, key, plain));
const b64 = u => Buffer.from(u).toString("base64");
const payload = JSON.stringify({ iter: ITER, salt: b64(salt), iv: b64(iv), ct: b64(ct) });

const page = `<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>잠긴 페이지</title>
<style>
:root { --bg: #F6F7F5; --card: #FFFFFF; --ink: #16202B; --muted: #5C6A75; --line: #DCE1E0; --accent: #14635C; --no: #B3261E; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root { --bg: #12171C; --card: #182027; --ink: #E4E9EC; --muted: #93A1AB; --line: #2C3840; --accent: #5BB3A6; --no: #F2A09A; color-scheme: dark; } }
* { box-sizing: border-box; }
body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: var(--bg); color: var(--ink); font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; padding: 16px; }
form { width: min(360px, 100%); background: var(--card); border: 1px solid var(--line); padding: 22px 20px; display: grid; gap: 12px; }
h1 { margin: 0; font-size: 18px; }
p { margin: 0; color: var(--muted); font-size: 14px; }
input[type=password] { font: inherit; font-size: 16px; padding: 10px 12px; border: 1px solid var(--line); background: var(--bg); color: var(--ink); width: 100%; }
label.keep { display: flex; gap: 8px; align-items: center; font-size: 14px; color: var(--muted); }
button { font: inherit; font-weight: 700; padding: 11px; border: 0; background: var(--accent); color: #FFFFFF; cursor: pointer; }
button:disabled { opacity: .6; }
.err { color: var(--no); min-height: 1.4em; }
</style>
</head>
<body>
<form id="f">
  <h1>비밀번호를 입력하세요</h1>
  <p>개인 학습용 페이지예요.</p>
  <input type="password" id="pw" autocomplete="current-password" autofocus aria-label="비밀번호">
  <label class="keep"><input type="checkbox" id="keep"> 이 기기에서 기억하기</label>
  <button id="go">열기</button>
  <p class="err" id="err" role="alert"></p>
</form>
<script>
const D = ${payload};
const KEY = "ccaf-guide-pw";
const u8 = s => Uint8Array.from(atob(s), ch => ch.charCodeAt(0));
async function open(pw) {
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(pw), "PBKDF2", false, ["deriveKey"]);
  const key = await crypto.subtle.deriveKey({ name: "PBKDF2", salt: u8(D.salt), iterations: D.iter, hash: "SHA-256" }, base, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
  const html = new TextDecoder().decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv: u8(D.iv) }, key, u8(D.ct)));
  document.open(); document.write(html); document.close();
}
const f = document.getElementById("f"), btn = document.getElementById("go"), err = document.getElementById("err");
f.addEventListener("submit", async e => {
  e.preventDefault();
  const pw = document.getElementById("pw").value;
  if (!pw) return;
  btn.disabled = true; btn.textContent = "여는 중…"; err.textContent = "";
  try {
    if (document.getElementById("keep").checked) { try { localStorage.setItem(KEY, pw); } catch (x) {} }
    await open(pw);
  } catch (x) {
    try { localStorage.removeItem(KEY); } catch (y) {}
    err.textContent = "비밀번호가 틀렸어요.";
    btn.disabled = false; btn.textContent = "열기";
  }
});
let saved = null;
try { saved = localStorage.getItem(KEY); } catch (x) {}
if (saved) open(saved).catch(() => { try { localStorage.removeItem(KEY); } catch (y) {} });
</script>
</body>
</html>
`;
writeFileSync(new URL("../locked/guide.html", import.meta.url), page);
console.log("locked/guide.html", page.length, "bytes");
