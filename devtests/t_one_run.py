# 🔒 v3.36.62 — ONE engine per bot folder (p106). The owner (16-11): his demo DCA+ bot «ما يكتب ربح» and its log showed «⚡ بوت DCA+
#   انطلق» twice in the same second, then «تعذّر التأكد من إلغاء بعض أوامر البيع» every 5 minutes for hours · «اهم شي ضاىعات لا يوجد …
#   ولكل البوتات». Two copies of one engine on one folder: reproduced here on v3.36.61 — the cycle closed TWICE (bought back twice).
#   A closed folder · the price from a local file (HOLY_DEMO_FEED — no network) · real processes (the dashboard's own launch()):
#   ① a demo DCA+ bot starts through holy_one.py: one engine process · the folder's lock is held · is_alive says so even with the
#     process table empty and the Linux /proc scan off (as on Windows) · bot_pids gives its pid from the lock (the Windows path)
#   ② two launches at the same moment (the watchdog's first pass and «start all» at the program's start) ⇒ still ONE process, the same pid
#   ③ a copy started from outside (another dashboard · a forgotten window) ⇒ leaves at once with «HOLY-ONE», touching nothing (no line
#     in the bot's log · the state file not written)
#   ④ the price reaches the target ⇒ the cycle closes ONCE (one «💰 إغلاق الدورة» · the paper wallet = the books)
#   ⑤ ⏹ stops it (the lock is free again) · ▶️ starts it again (one process) · a killed engine (kill -9) frees the lock by itself
#   ⑥ a real (non-demo) bot goes through the same runner (a stand-in engine file — the folder's own script runs unchanged)
#   python3 devtests/t_one_run.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, os, shutil, signal, subprocess, sys, tempfile, threading, time, urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1200]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="t_one_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_one", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_one", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.ROOT = R
SYM, P0 = "XRP-USDT", 1.0
SPEC = {"tickSz": 0.0001, "lotSz": 0.000001, "minSz": 1}
m._bt_spec = lambda s: dict(SPEC)
m._acc_price = lambda s: P0
m.PX[SYM] = P0
TG = []
m.tg_send = lambda t, *a, **k: TG.append(t) or True
m._okx_get = lambda *a, **k: (_ for _ in ()).throw(AssertionError("the demo called OKX's private side"))
FEED = os.path.join(R, "feed.json")


def feed(p):
    json.dump(dict(SPEC, last=p), open(FEED + ".tmp", "w"))
    os.replace(FEED + ".tmp", FEED)


feed(P0)
os.environ["HOLY_DEMO_FEED"] = FEED


def wait(cond, sec=60):
    t = time.time()
    while time.time() - t < sec:
        if cond():
            return True
        time.sleep(0.3)
    return False


def procs(d):
    """every engine process whose working folder is d (the /proc scan — independent of the lock)"""
    out = []
    real = os.path.realpath(d)
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            if os.path.realpath(f"/proc/{pid}/cwd") == real and b"holy_" in open(f"/proc/{pid}/cmdline", "rb").read():
                out.append(int(pid))
        except Exception:
            pass
    return out


ROWS = [{"d": 0, "q": 5, "x": 0.6}, {"d": 1, "q": 5, "x": 0.6}, {"d": 1.5, "q": 10, "x": 0.5}, {"d": 2, "q": 20, "x": 0.4}]
r = m.deploy_demo("dca_plus", {"symbol": SYM, "dca_type": "dca_plus", "plus_rows": json.dumps(ROWS), "exchange_orders": "2", "cycle_wait_sec": "600",
                               "demo": True, "demo_usd": "50", "demo_coin": "200", "auto": True})
D = os.path.join(R, r.get("dir") or "x")
cfg = json.load(open(os.path.join(D, f"config_{SYM}.json"), encoding="utf-8")) if os.path.isdir(D) else {}
b = {"dir": D, "symbol": SYM, "cfg": cfg, "cfg_path": os.path.join(D, f"config_{SYM}.json")}
HP = m.paths_of(b)[1]
hist = lambda: json.load(open(HP, encoding="utf-8")) if os.path.exists(HP) else []
wait(lambda: any("بيع الأساس" in e.get("msg", "") for e in hist()), 60)
p1 = procs(D)
lin = m.bot_pids
ok(f"① the demo DCA+ bot runs through holy_one.py: one engine process ({p1}) · the folder's lock held · its pid in the lock file",
   r.get("ok") and len(p1) == 1 and m._one_held(D) and m._one_pid(D) == p1[0] and os.path.exists(os.path.join(D, "holy_one.py")), (r, p1, m._one_pid(D)))
m.PROCS.pop(D, None)
_name = m.os.name
m.bot_pids = lambda full, ttl=4.0: []
al = m.is_alive(D, m.paths_of(b)[0])
m.bot_pids = lin
ok(f"① … with the process table empty and the /proc scan off (as on Windows): is_alive still sees it ({al})", al[0] and al[1] in ("lock", "external"), al)
# ② two launches at once
outs = []
ths = [threading.Thread(target=lambda: outs.append(m.launch(b))) for _ in range(2)]
[t.start() for t in ths]
[t.join() for t in ths]
time.sleep(3)
p2 = procs(D)
ok(f"② two launches at the same moment (the watchdog and «start all» at the program's start): still ONE engine process ({p2}) — "
   f"«{outs[0][1]}» · «{outs[1][1]}»", len(p2) == 1 and all(o[0] for o in outs), (outs, p2))
# ③ a copy from outside
n_h, st_m = len(hist()), os.path.getmtime(m.paths_of(b)[0])
x = subprocess.run([sys.executable, "-u", os.path.join(D, "holy_one.py"), "holy_demo.py", "dca.py", "dca.py"], cwd=D, capture_output=True, text=True, timeout=30,
                   env=dict(os.environ))
time.sleep(0.5)
lines_after = [e for e in hist()[: max(0, len(hist()) - n_h)] if "انطلق" in e.get("msg", "")]
ok(f"③ a copy started from outside leaves at once (code {x.returncode}: «{x.stdout.strip()[:60]}») · no «انطلق» line from it · still one process",
   x.returncode == 3 and "HOLY-ONE" in x.stdout and not lines_after and len(procs(D)) == 1, (x.returncode, x.stdout[-300:], x.stderr[-300:], lines_after))
# ④ the target ⇒ one close
feed(0.99)
wait(lambda: any("إغلاق الدورة" in e.get("msg", "") for e in hist()), 60)
time.sleep(4)
closes = [e for e in hist() if "إغلاق الدورة" in e.get("msg", "")]
w = json.load(open(os.path.join(D, m.DEMO_WALLET), encoding="utf-8"))
fills = w.get("fills") or []
buys = [f for f in fills if f[1] == "buy"]
ok(f"④ the price reaches the target ⇒ the cycle closes ONCE ({len(closes)} «إغلاق الدورة» · {len(buys)} buy-back fill(s))", len(closes) == 1 and len(buys) >= 1
   and len({round(f[0]) for f in buys}) <= 2, ([e["msg"][:80] for e in closes], buys))
# ⑤ stop · start · kill -9
m.stop_bot(b)
ok("⑤ ⏹ stops it: no engine process · the lock is free", wait(lambda: not procs(D) and not m._one_held(D), 20), (procs(D), m._one_held(D)))
ok2, msg2 = m.launch(b)
ok(f"⑤ ▶️ starts it again: one process («{msg2}»)", ok2 and wait(lambda: len(procs(D)) == 1, 20) and m._one_held(D), (msg2, procs(D)))
os.kill(procs(D)[0], signal.SIGKILL)
ok("⑤ a killed engine (kill -9) frees the lock by itself (the operating system)", wait(lambda: not procs(D) and not m._one_held(D), 20), (procs(D), m._one_held(D)))
m.PROCS.pop(D, None)
ok3, msg3 = m.launch(b)
ok("⑤ … and it starts again cleanly", ok3 and wait(lambda: len(procs(D)) == 1, 20), (msg3, procs(D)))
m.stop_bot(b)
wait(lambda: not procs(D), 20)
# ⑥ a real bot (a stand-in engine file — the folder's own script runs unchanged through the runner)
RD = os.path.join(R, "real_xrp")
os.makedirs(RD)
rc = {"symbol": SYM, "bot_type": "grid", "api_key": "k", "secret_key": "s", "passphrase": "p", "auto_restart": False}
json.dump(rc, open(os.path.join(RD, f"config_{SYM}.json"), "w"))
open(os.path.join(RD, "main.py"), "w").write("import os, time, sys\nopen('ran.txt','a').write(f'{os.getpid()} {__name__} {sys.argv}\\n')\nwhile True: time.sleep(1)\n")
rb = {"dir": RD, "symbol": SYM, "cfg": rc, "cfg_path": os.path.join(RD, f"config_{SYM}.json")}
_eo = m._eng_old
o1 = m.launch(rb)
o2 = m.launch(rb)
time.sleep(1)
ran = open(os.path.join(RD, "ran.txt")).read().splitlines() if os.path.exists(os.path.join(RD, "ran.txt")) else []
ok(f"⑥ a real bot goes through the same runner: its own main.py ran once as «__main__» ({ran[:1]}) · a second ▶️ starts nothing («{o2[1]}»)",
   o1[0] and o2[0] and len(ran) == 1 and "__main__" in ran[0] and "main.py" in ran[0] and len(procs(RD)) == 1, (o1, o2, ran, procs(RD)))
m.stop_bot(rb)
ok("⑥ … ⏹ stops it", wait(lambda: not procs(RD), 20), procs(RD))
ok("nothing went to Telegram (the demo is quiet)", not [t for t in TG if "XRP" in t and "real" not in t], TG[:3])
for p_ in list(m.PROCS.values()):
    try:
        p_.kill()
    except Exception:
        pass
os.chdir(H)
shutil.rmtree(R, ignore_errors=True)
print(f"✅ t_one_run: {sum(res)}/{len(res)}" if res and all(res) else f"❌ t_one_run: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
