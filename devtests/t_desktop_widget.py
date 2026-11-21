# 🖥️ the desktop widgets (v3.36.72 · p123 · the Windows program 2.1) — the owner (21-11): «نقدر انسوي ويدجت للحاسوب … ويدجت نفسه الي
#   بالموبايل نفسه الي بالحاسوب بالشكل».
#   A closed folder (no network · no keys): the dashboard's own server in a thread + a real browser (Playwright):
#   ① GET /widget is a page with NO data (public like the login page) · GET /api/widget = the phone widget's answer, behind the sign-in and
#      the PIN · /api/app/widget stays for a linked device only
#   ② the page draws the phone's two widgets: «Holy» (the six numbers + every bot) · «Holy · الأسعار» (the coins' tiles) — the same words the
#      app 2.3 speaks · a bigger window holds more tiles · the device key in the address's #part is read, sent as the header (not in the
#      request line) and wiped from the address bar · not signed in ⇒ «افتح Holy وادخل إلى لوحتك مرة واحدة» · a click opens the dashboard
#   ③ the 💻 panel: in a browser «🖥️ ويدجت لأي حاسوب» (opens /widget as a small window) · inside the program 2.1 «🟣 ويدجت Holy» ·
#      «🪙 ويدجت الأسعار» · «📌 فوق كل النوافذ» (they send hw:bots · hw:px · hw:top and follow the program's state)
#   ④ the Windows program 2.1 source: frameless tool windows (not on the taskbar) · rounded · position kept · on top · with Windows ·
#      --widget=… · the key only after «#» and never logged · display only
#   python3 devtests/t_desktop_widget.py [Holy_Dashboard.pyw] [-q]     (run with `unset TMPDIR`)
import importlib.machinery, importlib.util, json, os, re, shutil, socket, subprocess, sys, tempfile, threading, time, urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
SRC = open(DASH, encoding="utf-8").read()
WIN = open(os.path.join(H, "..", "windows", "holy_win.c"), encoding="utf-8").read()
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1500]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


R = tempfile.mkdtemp(prefix="t_dwg_")
json.dump({"port": 1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_dwg", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_dwg", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m._okx_pub = lambda *a, **k: None
m._okx_get = lambda *a, **k: None
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
m._http_json = lambda *a, **k: None
m.tg_send = lambda *a, **k: True
SP = [500 + int(400 * ((i % 13) - 6) / 6) for i in range(49)]
FIX = {"ok": True, "run": 3, "n": 4, "kb": [["اليوم", "+3.42$", "u"], ["أمس", "+5.10$", "u"], ["آخر 7 أيام", "+28.77$", "u"], ["آخر 30 يوماً", "+101.20$", "u"],
                                           ["هذا الشهر", "+77.65$", "u"], ["الإجمالي", "1,240.55$", "z"]],
       "bots": [{"e": "♾️", "s": "SOL", "on": 1, "a": "+1.20$", "b": "", "c": "u", "t": "grid"}, {"e": "➕", "s": "XRP", "on": 1, "a": "+0.84$", "b": "", "c": "u", "t": "grid_plus"},
                {"e": "🪜", "s": "BTC", "on": 1, "a": "+0.61$", "b": "", "c": "u", "t": "grid_step"}, {"e": "📉", "s": "ETH", "on": 0, "a": "—", "b": "", "c": "z", "t": "dca"}],
       "px": [{"s": s, "p": p, "ch": c, "sp": SP} for s, p, c in (("BTC", "91,240", 2.31), ("ETH", "3,105.4", 1.12), ("SOL", "138.62", -3.47), ("XRP", "2.0418", -0.85),
                                                                 ("DOGE", "0.15214", 4.2), ("LINK", "14.83", 0.4), ("BNB", "612.4", -1.1), ("ADA", "0.4123", 2.0))]}
m.app_widget_view = lambda: dict(FIX)
DEV = {"tok": "dEvKeY_1234567890abcdefXYZ"}
_real_dev = m.app_dev_auth
m.app_dev_auth = lambda t: ({"id": "d1", "name": "💻 Windows"} if t == DEV["tok"] else None)


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


P = port()
srv = m.ThreadingHTTPServer(("127.0.0.1", P), m.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{P}"


def get(path, hdr=None):
    rq = urllib.request.Request(B + path, headers=hdr or {})
    try:
        with urllib.request.urlopen(rq, timeout=10) as r:
            return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), dict(e.headers)


try:
    # ── ①
    st, body, hd = get("/widget?k=px")
    ok("① /widget is the widget page (a canvas · Arabic right to left) and carries no data — no number, no coin, no key in it",
       st == 200 and "<canvas" in body and 'dir="rtl"' in body and "91,240" not in body and "BTC" not in body.split("COINC")[0] and "X-Holy-Device" in body,
       (st, body[:200]))
    st2, b2, _ = get("/api/widget")
    j2 = json.loads(b2) if st2 == 200 else {}
    ok("① no password set ⇒ /api/widget answers the phone widget's own data (the six numbers · the bots · the coins)", st2 == 200 and j2.get("kb") and j2.get("px"), (st2, b2[:200]))
    _cfg0 = m.auth_cfg
    m.auth_cfg = lambda: dict(_cfg0(), hash="x" * 64)
    st3, b3, _ = get("/api/widget")
    st4, b4, _ = get("/widget?k=bots")
    st5, b5, _ = get("/api/app/widget")
    st6, b6, _ = get("/api/app/widget", {"X-Holy-Device": DEV["tok"]})
    m.auth_cfg = _cfg0
    ok("① with the sign-in on: /api/widget ⇒ 401 for a browser that is not signed in · /widget (no data) still opens · /api/app/widget needs a linked "
       "device's key (without ⇒ 401 · with ⇒ the data)", st3 == 401 and st4 == 200 and st5 == 401 and st6 == 200 and json.loads(b6).get("kb"), (st3, st4, st5, st6))
    _pin0 = m.dash_cfg
    m.dash_cfg = lambda: dict(_pin0(), pin="4321")
    st7, _, _ = get("/api/widget")
    st8, _, _ = get("/api/widget", {"X-Dash-Pin": "4321"})
    m.dash_cfg = _pin0
    ok("① …and the dashboard's PIN: without it 401 · with it the data (the page sends the PIN the dashboard saved in this browser)", st7 == 401 and st8 == 200, (st7, st8))

    # ── ② ③ in a browser
    JS = r'''
const { chromium } = require('playwright');
(async () => {
  const B = process.argv[2], DEV = process.argv[3], out = {};
  const br = await chromium.launch();
  const one = async (k, w, h, hash, hdrs) => {
    const ctx = await br.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    const pg = await ctx.newPage(); const errs = []; pg.on('pageerror', e => errs.push(String(e)));
    const seen = [];
    await pg.route('**/*', rt => { const r = rt.request(), u = r.url(); if (!u.startsWith(B)) return rt.abort();
      if (u.includes('/api/')) seen.push([u.replace(B, ''), r.headers()['x-holy-device'] || '']); return rt.continue() });
    await pg.addInitScript(() => { window.__opened = []; window.open = (u, n) => { window.__opened.push([u, n]); return { focus() {} } } });
    await pg.goto(B + '/widget?k=' + k + (hash || '')); await pg.waitForTimeout(900);
    const r = await pg.evaluate(() => ({ al: document.getElementById('c').getAttribute('aria-label'), loc: location.href,
      px: (() => { const c = document.getElementById('c'), x = c.getContext('2d'), d = x.getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 3; i < d.length; i += 4000) if (d[i] > 0) n++; return n })() }));
    await pg.mouse.click(Math.round(w / 2), Math.round(h / 2)); await pg.waitForTimeout(200);
    r.opened = await pg.evaluate(() => window.__opened);
    r.seen = seen; r.errs = errs;
    if (process.env.SHOT) await pg.screenshot({ path: process.env.SHOT + '/' + k + '_' + w + 'x' + h + '.png' });
    await ctx.close(); return r };
  out.bots = await one('bots', 330, 200);
  out.px = await one('px', 340, 236);
  out.pxBig = await one('px', 440, 380);
  out.tok = await one('bots', 330, 200, '#d=' + DEV);
  out.badTok = await one('px', 340, 236, '#d=WRONGKEY12345678');
  // ③ the 💻 panel — a browser
  const ctx = await br.newContext({ viewport: { width: 1200, height: 900 } }); const pg = await ctx.newPage(); const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
  await pg.route('**/*', rt => (rt.request().url().startsWith(B) ? rt.continue() : rt.abort()));
  await pg.goto(B + '/'); await pg.waitForFunction(() => typeof openWinPanel === 'function', null, { timeout: 30000 });
  await pg.evaluate(() => { const s = document.getElementById('splash'); if (s) s.remove(); window.__opened = []; window.open = (u, n, f) => { window.__opened.push([u, n, f]); return {} } });
  await pg.evaluate(() => openWinPanel()); await pg.waitForTimeout(1500);
  out.panel = await pg.evaluate(() => ({ t: (document.getElementById('wn_body') || {}).innerText || '', b: [...document.querySelectorAll('#wn_body button')].map(b => b.textContent) }));
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#wn_body button')].find(x => x.textContent.includes('افتح ويدجت الأسعار')); b && b.click() });
  out.panelOpen = await pg.evaluate(() => window.__opened);
  out.panelErrs = errs; await ctx.close();
  // ③ the 💻 panel — inside the program 2.1 (its bridge simulated: window.HOLYWIN · chrome.webview)
  const c2 = await br.newContext({ viewport: { width: 1200, height: 900 } }); const p2 = await c2.newPage(); const e2 = []; p2.on('pageerror', e => e2.push(String(e)));
  await p2.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {}
    window.__sent = []; const L = []; window.HOLYWIN = { v: '2.1.0', ncr: false, wg: 1 };
    window.chrome = window.chrome || {}; window.chrome.webview = { postMessage: m => { window.__sent.push(m);
        if (m === 'hw:state' || m.startsWith('hw:')) setTimeout(() => L.forEach(f => f({ data: { t: 'hw', bots: m === 'hw:bots' ? 1 : 0, px: 0, top: 1 } })), 30) },
      addEventListener: (t, f) => { if (t === 'message') L.push(f) } } });
  await p2.route('**/*', rt => (rt.request().url().startsWith(B) ? rt.continue() : rt.abort()));
  await p2.goto(B + '/?holyapp=win&hv=2.1.0'); await p2.waitForFunction(() => typeof openWinPanel === 'function', null, { timeout: 30000 });
  await p2.evaluate(() => { const s = document.getElementById('splash'); if (s) s.remove() });
  await p2.evaluate(() => openWinPanel()); await p2.waitForTimeout(1500);
  out.win = await p2.evaluate(() => ({ t: (document.getElementById('wn_body') || {}).innerText || '', b: [...document.querySelectorAll('#wn_wg button')].map(b => [b.textContent, b.className]) }));
  await p2.evaluate(() => document.querySelector('#wn_wg button[data-k="bots"]').click()); await p2.waitForTimeout(300);
  out.winAfter = await p2.evaluate(() => ({ sent: window.__sent, b: [...document.querySelectorAll('#wn_wg button')].map(b => [b.dataset.k, b.className]) }));
  out.winErrs = e2; await c2.close();
  await br.close(); console.log(JSON.stringify(out));
})().catch(e => { console.log(JSON.stringify({ err: String(e) })); process.exit(1) });
'''
    jsf = os.path.join(R, "w.js")
    open(jsf, "w").write(JS)
    env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
    rr = subprocess.run(["node", jsf, B, DEV["tok"]], capture_output=True, text=True, timeout=300, cwd="/tmp", env=env)
    U = json.loads(rr.stdout.strip().splitlines()[-1]) if rr.stdout.strip() else {"err": rr.stderr[-800:]}
    bo, px, pb, tk, bt = (U.get(k) or {} for k in ("bots", "px", "pxBig", "tok", "badTok"))
    ok("② «Holy» drawn like the phone's: «Holy — 3 من 4 بوتات تعمل · اليوم +3.42$ · … · SOL +1.20$» (the app 2.3's own words) · no page error",
       (bo.get("al") or "").startswith("Holy — 3 من 4 بوتات تعمل · اليوم +3.42$") and "SOL +1.20$" in bo.get("al", "") and bo.get("px", 0) > 20 and not bo.get("errs"),
       {k: bo.get(k) for k in ("al", "px", "errs")} if bo else U)
    ok("② «Holy · الأسعار»: every coin with its price and change («BTC 91,240 ارتفع 2.31% · SOL 138.62 انخفض 3.47%») · drawn", "BTC 91,240 ارتفع 2.31%" in (px.get("al") or "")
       and "SOL 138.62 انخفض 3.47%" in px.get("al", "") and px.get("px", 0) > 20 and not px.get("errs"), {k: px.get(k) for k in ("al", "px", "errs")})
    ok("② a click opens the dashboard (in a browser: the dashboard's own tab «holy_main»)", (bo.get("opened") or [[None]])[0][:2] == ["/", "holy_main"], bo.get("opened"))
    ok("② in a browser it reads /api/widget (no key) · with the program's key in the #part it reads /api/app/widget sending the key as the header — "
       "and the #part is wiped from the address", all(u.startswith("/api/widget") and not h for u, h in bo.get("seen") or [["x", "x"]])
       and any(u.startswith("/api/app/widget") and h == DEV["tok"] for u, h in tk.get("seen") or []) and "#" not in (tk.get("loc") or "#")
       and (tk.get("al") or "").startswith("Holy — 3 من 4"), {k: tk.get(k) for k in ("seen", "loc", "al")})
    ok("② a wrong or unlinked key ⇒ «Holy — افتح Holy وادخل إلى لوحتك مرة واحدة» (the phone's own words) · nothing private shown",
       (bt.get("al") or "") == "Holy — افتح Holy وادخل إلى لوحتك مرة واحدة", bt.get("al"))
    ok("② the same answer in a bigger window still draws every coin (the bigger, the more tiles)", "ADA 0.4123" in (pb.get("al") or "") and pb.get("px", 0) > 20, pb.get("al"))
    pn = U.get("panel") or {}
    ok("③ 💻 in a browser: «🖥️ ويدجت لأي حاسوب» with «🟣 افتح ويدجت Holy» · «🪙 افتح ويدجت الأسعار» ⇒ /widget?k=px as a small window",
       "ويدجت لأي حاسوب" in pn.get("t", "") and any("افتح ويدجت Holy" in b for b in pn.get("b") or []) and (U.get("panelOpen") or [[""]])[0][0] == "/widget?k=px"
       and "popup" in ((U.get("panelOpen") or [["", "", ""]])[0][2] or "") and not U.get("panelErrs"), {k: U.get(k) for k in ("panel", "panelOpen", "panelErrs", "err")})
    w = U.get("win") or {}
    wa = U.get("winAfter") or {}
    ok("③ 💻 inside the program 2.1: «🖥️ ويدجت سطح المكتب» · «🟣 ويدجت Holy» · «🪙 ويدجت الأسعار» · «📌 فوق كل النوافذ» (the program's state: on top ✓)",
       "ويدجت سطح المكتب" in w.get("t", "") and [b[0] for b in w.get("b") or []] == ["🟣 ويدجت Holy", "🪙 ويدجت الأسعار", "📌 فوق كل النوافذ"]
       and (w.get("b") or [[0, ""]] * 3)[2][1] == "on", w)
    ok("③ …a tap sends «hw:bots» to the program and the button follows its answer (on) · the panel asked for the state («hw:state»)",
       "hw:bots" in (wa.get("sent") or []) and "hw:state" in (wa.get("sent") or []) and dict(wa.get("b") or []).get("bots") == "on" and not U.get("winErrs"), wa)

    # ── ④ the Windows program 2.1
    ok("④ the program 2.1 (build 210): a «HolyWidget» window class · frameless tool windows (not on the taskbar) · rounded (20 dp) · the rim resizes "
       "· on top (📌) · the place and size kept in holy.ini · back with Windows (wg_boot)", 'APP_VER   L"2.1.0"' in WIN and "#define APP_BUILD 210" in WIN
       and 'L"HolyWidget"' in WIN and "WS_EX_TOOLWINDOW" in WIN and "CreateRoundRectRgn" in WIN and "HWND_TOPMOST" in WIN and "wg_save(" in WIN
       and "wg_boot();" in WIN and "WM_EXITSIZEMOVE" in WIN, "")
    ok("④ the tray menu · the 💻 panel (hw:bots · hw:px · hw:top · hw:state) · «--widget=bots|px» all reach the same switch", all(x in WIN for x in (
       "ويدجت Holy على سطح المكتب", "ويدجت الأسعار على سطح المكتب", 'L"hw:bots"', 'L"hw:px"', 'L"hw:top"', 'L"hw:state"', 'L"--widget=bots"', 'L"--widget=px"', 'L"wg:bots"')), "")
    wu = WIN[WIN.index("static void wg_url("):WIN.index("static void wg_top(")]
    ok("④ the device key reaches the widget only after «#» (never in a request line) and no log line carries the widget's address",
       'L"#d="' in wu and "hlog" not in wu and not re.search(r"hlog\([^;]*wg_url", WIN), wu[:300])
    ok("④ display only: the widget windows open nothing but the dashboard (the same address check as the window · no orders · no keys shown)",
       "ICoreWebView2_add_NavigationStarting(w->wv, &g_navH" in WIN and "_okx" not in WIN, "")
finally:
    try:
        srv.shutdown()
    except Exception:
        pass
    os.chdir(H)
    shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_desktop_widget: {sum(res)}/{len(res)} (the desktop widgets)")
sys.exit(0 if all(res) else 1)
