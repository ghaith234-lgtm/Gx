# 🔒 v3.36.53 — the full audit, batch 4 (protection). A closed folder with a password set:
#   ① no /api · /app · /font · export path answers without a session (GET and POST) — only the login page, the app's own key-checked
#      paths and «logout» ② a forged session is refused ③ wrong passwords ⇒ locked ④ no wallet key in what a session reads
#   ⑤ changing the password does NOT write it in the journal (it did — «new»/«cur» in clear text) ⑥ a line written by an older
#      version is masked in the journal file at start
#   python3 devtests/t_secrets.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import http.client, json, os, re, shutil, socket, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
sys.path.insert(0, H)
_a = sys.argv; sys.argv = [_a[0], tempfile.gettempdir()]
import seed_cards                                             # noqa: E402
sys.argv = _a
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


src = open(DASH, encoding="utf-8").read()
i = src.index("HTML_PAGE = r"); j = src.index('"""', src.index('"""', i) + 3); server = src[:i] + src[j:]
PATHS = sorted(set(re.findall(r"""["'](/(?:api|app|font|export|backup|download)[A-Za-z_0-9/.\-]*)["']""", server)))
R = tempfile.mkdtemp(prefix="t_secrets_")
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
seed_cards.seed(R, DASH)
OLD = "Old-Pass-777"
os.makedirs(os.path.join(R, "Holy_Journal"), exist_ok=True)
JF = os.path.join(R, "Holy_Journal", time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400)) + ".jsonl")   # yesterday (older files are pruned)
with open(JF, "w", encoding="utf-8") as f:                      # a line as an older version wrote it
    f.write(json.dumps({"t": time.time() - 86400, "c": "user", "lv": "ok", "m": "👤 set_pw — 🔐 حُفظت", "d": {"path": "/api/set_pw", "request": {"new": OLD, "cur": "", "mins": 30}, "ok": True}}, ensure_ascii=False) + "\n")
    f.write(json.dumps({"t": time.time() - 86399, "c": "user", "lv": "ok", "m": "👤 mute", "d": {"path": "/api/control", "request": {"action": "mute"}}}, ensure_ascii=False) + "\n")


def start():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close()
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(p)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", p), timeout=0.3).close(); break
        except OSError:
            time.sleep(0.1)
    return d, p


d, P = start()


def req(m, p, body=None, hdr=None):
    c = http.client.HTTPConnection("127.0.0.1", P, timeout=30)
    h = dict(hdr or {}); b = None
    if body is not None:
        b = json.dumps(body).encode(); h["Content-Type"] = "application/json"
    c.request(m, p, body=b, headers=h); r = c.getresponse(); t = r.read(); ck = r.getheader("Set-Cookie"); c.close()
    return r.status, t, ck


try:
    raw = open(JF, encoding="utf-8").read()
    ok("⑥ a password an older version wrote in the journal is masked in the file at start (the line stays · the other line untouched)",
       OLD not in raw and '"new": "***"' in raw and "👤 mute" in raw and raw.count("\n") >= 1, raw[:300])
    NEW = "Secret-123-xyz"
    st, t, _ = req("POST", "/api/set_pw", {"new": NEW, "mins": 30})
    st2, t2, ck = req("POST", "/api/login", {"pw": NEW})
    tok = (re.search(r"holy_tok=([^;]+)", ck or "") or [None, ""])[1]
    ok("a password is set and the login gives a session (HttpOnly · SameSite=Strict)", st == 200 and st2 == 200 and tok and "HttpOnly" in ck and "SameSite=Strict" in ck, (st, st2, ck))
    C = {"Cookie": "holy_tok=" + tok}
    ALLOW_GET = {"/api/app/feed", "/api/app/widget", "/api/app/info", "/app/holy.apk", "/app/holy.exe"}       # checked by the device's own key
    ALLOW_POST = {"/api/logout", "/api/login", "/api/app/bio_unlock"}
    og, op = [], []
    for p in PATHS:
        s1, b1, _ = req("GET", p)
        if s1 != 401 and p not in ALLOW_GET and not (s1 == 200 and b"<form" in b1[:8000]):
            og.append((p, s1, b1[:60]))
        s2, b2, _ = req("POST", p, {})
        if s2 not in (401, 429) and p not in ALLOW_POST:
            op.append((p, s2, b2[:60]))
    ok(f"① without a session nothing answers ({len(PATHS)} paths · GET and POST): only the login page, «logout» and the app's key-checked paths", not og and not op, (og[:4], op[:4]))
    s3, b3, _ = req("GET", "/")
    ok("① … «/» without a session is the login page — no bot, no symbol, no key in it", s3 == 200 and b"SOL-USDT" not in b3 and b"api_key" not in b3, len(b3))
    ok("② a forged session is refused · the real one works", req("GET", "/api/overview", hdr={"Cookie": "holy_tok=" + tok[:-3] + "abc"})[0] == 401 and req("GET", "/api/overview", hdr=C)[0] == 200)
    leaks = []
    for p in ("/api/overview", "/api/settings", "/api/journal", "/api/report", "/api/guard"):
        s4, b4, _ = req("GET", p, hdr=C)
        for w in (NEW.encode(), OLD.encode(), b'"secret_key"', b'"passphrase"', b'"pw_hash"'):
            if w in b4:
                leaks.append((p, w))
    ok("④ ⑤ nothing a session reads holds the password just set, the old one, a wallet secret or the password's hash (the journal held the new password)", not leaks, leaks)
    disk = "".join(open(os.path.join(R, "Holy_Journal", f), encoding="utf-8", errors="ignore").read() for f in os.listdir(os.path.join(R, "Holy_Journal")) if f.endswith(".jsonl"))
    ok("⑤ … nor the journal files on disk — the change itself is still recorded («set_pw» with «***»)", NEW not in disk and OLD not in disk and "/api/set_pw" in disk and '"new": "***"' in disk, disk[-300:])
    codes = [req("POST", "/api/login", {"pw": "wrong%d" % k})[0] for k in range(12)]
    ok("③ wrong passwords: refused, then locked («429») before the 9th", codes[0] == 401 and 429 in codes[:9] and codes[-1] == 429, codes)
finally:
    d.kill()
    shutil.rmtree(R, ignore_errors=True)
print(f"✅ t_secrets: {sum(res)}/{len(res)}" if all(res) else f"❌ t_secrets: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
