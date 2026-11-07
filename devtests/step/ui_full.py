# 🪜🃏 v3.36.20 the card made clear, in a real browser — the real dashboard (closed folder · fake keys · no network) serving two
#   🪜 bots built by the REAL engine on the mock OKX:
#     XRP — the owner's settings (25$ · 0.6% · 3 parts 0.45/0.60/0.75 · 1 level from coins) with reinvest 100%: level 0 (above the
#           start) and level −1 (under it) each sold twice
#     ADA — the owner's big example (100$ · 20 parts · first sell 0.3% · then 1% · 20 levels from coins ⇒ 1,260 slots)
#   the steps in ui_full.js: a sell's tap names its own buy · a buy's tap lists its own sells · «🪜 السلم» = the full ladder by level
#   (counts = the engine's slots · filters) · «💠 سلّم الإعادة» one page (below the price reachable · only-with-reinvest · small
#   amounts in full) · the big bot: the card's copy is cut, the full ladder and the 💠 screen still get every slot · /api/step_ladder
#   refuses an unknown folder and a path outside the dashboard
#   python3 devtests/step/ui_full.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import json, os, shutil, socket, subprocess, sys, tempfile, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
from okxsim import Clock, Ex, Bot, walk

Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_full_")
P1 = port()
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
json.dump({"port": P1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "FAKE-KEY", "sec": "FAKE-SECRET", "pass": "FAKE-PASS"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
P0 = 1.1698
OWN = {"usd_value": 25.0, "step_parts": 3, "step_first": 0.0045, "step_sell": 0.0015, "grid_percentage": 0.006, "min_price": 0.9,
       "up_groups": 1, "forced_base_price": P0, "step_window": 8, "fee_rate": 0.0008, "taker_rate": 0.001, "reinvest": True, "reinvest_pct": 100}
c = Clock(t0=time.time() - 3 * 3600)
ex = Ex(c, sym="XRP-USDT", price=P0, base=100, quote=1000)
os.makedirs(os.path.join(R, "step_xrp")); os.makedirs(os.path.join(R, "step_ada"))
b = Bot(ex, OWN, folder=os.path.join(R, "step_xrp"))
bp1, sp0 = P0 / 1.006, round(P0 * 1.0046, 4)
dn, up = round(bp1 * 0.9995, 4), round(bp1 * 1.0080, 4)
b.run(walk([P0, P0, sp0, sp0, round(P0 * 0.9995, 4), sp0, sp0, dn, dn, up, up, dn, dn, up, up, round(P0 * 0.998, 4), round(P0 * 0.998, 4)], 20))
assert not b.errors, b.errors[:2]
c2 = Clock(t0=time.time() - 3 * 3600)
ex2 = Ex(c2, sym="ADA-USDT", price=P0, base=2000, quote=3000)
b2 = Bot(ex2, dict(OWN, usd_value=100.0, step_parts=20, step_first=0.003, step_sell=0.01, up_groups=20), folder=os.path.join(R, "step_ada"))
b2.run(walk([P0, P0, round(P0 * 1.004, 4), round(P0 * 1.004, 4), round(P0 * 0.985, 4), round(P0 * 0.985, 4), round(P0 * 0.994, 4),
             round(P0 * 0.994, 4), round(P0 * 0.97, 4), round(P0 * 0.97, 4), round(P0 * 0.982, 4), round(P0 * 0.982, 4)], 20))
assert not b2.errors, b2.errors[:2]
TRUTH = {}
for nm, bb in (("step_xrp", b), ("step_ada", b2)):
    st = bb.disk()
    S = st["slots"]
    TRUTH[nm] = {"slots": len(S), "levels": len({s["j"] for s in S.values()}),
                 "pb": sum(1 for s in S.values() if s["side"] == "buy" and (s.get("o") or {}).get("st") == "live"),
                 "ps": sum(1 for s in S.values() if s["side"] == "sell" and (s.get("o") or {}).get("st") == "live"),
                 "mb": sum(1 for s in S.values() if s["side"] == "buy" and not s.get("o")),
                 "ms": sum(1 for s in S.values() if s["side"] == "sell" and not s.get("o")),
                 "bp": {f'{s["j"]}:{s["k"]}': s["bp"] for s in S.values()},
                 "grown": sorted(k for k, v in ((st.get("reinvest") or {}).get("levels") or {}).items() if float(v.get("grown_qty") or 0) > 0)}
json.dump(TRUTH, open(os.path.join(R, "truth.json"), "w"))
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
rc, d = 1, None
try:
    d = subprocess.Popen([sys.executable, os.path.join(H, "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    r = subprocess.run(["node", os.path.join(H, "ui_full.js"), f"http://127.0.0.1:{P1}/", os.path.join(R, "truth.json")] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=400, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:])
    rc = r.returncode
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
sys.exit(rc)
