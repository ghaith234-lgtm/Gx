# ⚡ v3.36.59 — «⚡ DCA+» on its own button with the new DCA+ الشرائي, in the browser (p103). Every card kind (devtests/seed_cards.py) ·
#   closed folder · fake keys · no network (the candles come from a fake public feed — ui_dca_plus.py's launcher) · nothing launched.
#   The steps are in ui_dca_plus_buy.js (the bar · the two forms · the buy editor both ways on the chart · the server's own sums · the
#   trial · the tutorial · 🚀 · ✏️ · the details · the phone); afterwards this file reads what the deploy wrote:
#   · a buy DCA (bot_type dca_buy) with dca_plus and exactly the editor's rows · its folder holds DCA+ الشرائي (not the buy DCA's engine)
#   python3 devtests/ui_dca_plus_buy.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import json, os, re, shutil, socket, subprocess, sys, tempfile, base64, zlib

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
sys.path.insert(0, H)
if len(sys.argv) < 2:
    sys.argv.append(DASH)
import seed_cards                                             # noqa: E402

res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1200]}"), flush=True)


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def lit(src, var):
    i = src.index(var + " = (")
    j = src.index("\n)\n", i)
    return zlib.decompress(base64.b64decode("".join(re.findall(r'"([A-Za-z0-9+/=]+)"', src[i:j])))).decode("utf-8")


LAUNCH = open(os.path.join(H, "ui_dca_plus.py"), encoding="utf-8").read().split("LAUNCH = r'''", 1)[1].split("'''", 1)[0]
R = tempfile.mkdtemp(prefix="ui_dcapb_")
P1 = port()
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
d = None
try:
    seed_cards.seed(R, DASH)
    open(os.path.join(R, "_ui_launch.py"), "w").write(LAUNCH)
    d = subprocess.Popen([sys.executable, os.path.join(R, "_ui_launch.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    rr = subprocess.run(["node", os.path.join(H, "ui_dca_plus_buy.js"), f"http://127.0.0.1:{P1}/"] + (["-q"] if Q else []),
                        capture_output=True, text=True, timeout=900, cwd="/tmp", env=env)
    out = (rr.stdout or "").strip()
    J = {}
    for ln in out.splitlines():
        if ln.startswith("JSON "):
            J.update(json.loads(ln[5:]))
        elif ln.startswith(("✅", "❌")) and not ln.startswith(("✅ ui_dca_plus_buy.js", "❌ ui_dca_plus_buy.js")):
            if not Q or ln.startswith("❌"):
                print(ln, flush=True)
    _m = re.search(r"ui_dca_plus_buy\.js: (\d+)/(\d+)", out)
    if _m:
        res += [True] * int(_m.group(1)) + [False] * (int(_m.group(2)) - int(_m.group(1)))
    else:
        print(out[-1500:], rr.stderr[-1500:])
        res.append(False)
    src = open(DASH, encoding="utf-8").read()
    want = J.get("deploy_rows") or []
    bd = os.path.join(R, J.get("dir") or "x")
    cp = os.path.join(bd, "config_SOL-USDT.json")
    cfg = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    eng = open(os.path.join(bd, "dca.py"), encoding="utf-8").read() if os.path.exists(os.path.join(bd, "dca.py")) else ""
    got = [{"d": float(r["d"]), "q": float(r["q"]), "x": float(r["x"])} for r in (cfg.get("plus_rows") or [])]
    exp = [{"d": round(float(r["d"]), 6) if i else 0.0, "q": float(r["q"]), "x": round(float(r["x"]), 6)} for i, r in enumerate(want)]
    ok(f"🚀 the deploy wrote a buy DCA with dca_plus and exactly the editor's {len(want)} rows · its folder holds DCA+ الشرائي (not the buy DCA's engine)",
       cfg.get("bot_type") == "dca_buy" and cfg.get("dca_plus") is True and got == exp and eng == lit(src, "_DCAPB_B64") and eng != lit(src, "_DCAB_B64"),
       (cfg.get("bot_type"), cfg.get("dca_plus"), got[:3], exp[:3]))
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
print(f"✅ ui_dca_plus_buy: {sum(res)}/{len(res)}" if res and all(res) else f"❌ ui_dca_plus_buy: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
