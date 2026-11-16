# ⏳ v3.36.58 — the temporary buy pause in the browser (p99). Every card kind (devtests/seed_cards.py) with two grid bots in the
#   temporary pause (closed folder · fake keys · no network · nothing launched — only the dashboard writes):
#   · SOL ➕: closed from 181.5 · 6 levels kept under it · the unreserved dollars cover 3 ⇒ the green «🔓 افتح المؤقت (6)» · its window
#     (rule 14: <h2> first) says «يكفي 3 من 6» · «🔓 افتح» ⇒ the floor goes down exactly between the 3rd and the 4th level · the rest kept
#   · XRP ♾️: the owner's own ⏸ (2.40) and the temporary one (2.43): the card's own button shows HIS valve («▶️ استئناف الشراء») · it
#     opens «▶️ رفع إيقافك» (no market order) ⇒ his valve opens, the engine's floor stays the temporary one
#   · the phone: the chip and the window fit · no page error
#   python3 devtests/ui_temp_pause.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import importlib.machinery, importlib.util, json, os, re, shutil, socket, subprocess, sys, tempfile, time

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


LAUNCH = open(os.path.join(H, "ui_dca_plus.py"), encoding="utf-8").read().split("LAUNCH = r'''", 1)[1].split("'''", 1)[0]
R = tempfile.mkdtemp(prefix="ui_tp_")
P1 = port()
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
d = None
try:
    made = seed_cards.seed(R, DASH)
    sol, xrp = made["SOL-USDT"], made["XRP-USDT"]
    ksol, kxrp = os.path.relpath(sol, R), os.path.relpath(xrp, R)
    sp_sol = os.path.join(sol, "grid_state_SOL-USDT.json")
    sp_xrp = os.path.join(xrp, "grid_state_XRP-USDT.json")
    st = json.load(open(sp_sol, encoding="utf-8"))
    lv = [round(181.0 / 1.008 ** i, 2) for i in range(6)]            # 181.00 … 173.86 — the price 173 crossed them all
    q = round(25.0 / 181.0, 4)
    st.update(current_price=173.0, buy_floor=181.5, pause_buy=False, limit_buys={},
              accum_buys={f"a{i}": {"target_price": p, "original_sell_anchor": round(p * 1.008, 4), "locked_qty": q} for i, p in enumerate(lv)})
    json.dump(st, open(sp_sol, "w"))
    sx = json.load(open(sp_xrp, encoding="utf-8"))
    sx.update(buy_floor=2.43, pause_buy=False)
    json.dump(sx, open(sp_xrp, "w"))
    now = time.time()
    json.dump({"bots": {ksol: {"v": 2, "wid": "w1", "q": "USDT", "sym": "SOL-USDT", "type": "grid_plus", "temp": 181.5, "own": 0.0, "need": 25.0,
                               "ts": now - 3600, "freed": 0.0, "n0": 6, "n": 6, "k": 3},
                        kxrp: {"v": 2, "wid": "w1", "q": "USDT", "sym": "XRP-USDT", "type": "grid", "temp": 2.43, "own": 2.40, "need": 25.0,
                               "ts": now - 3600, "freed": 0.0, "n0": 0, "n": 0, "k": 0}},
               "seen": {}, "ok": {}, "opened": {}, "avail": {}}, open(os.path.join(R, "Holy_CashWatch.json"), "w"))
    gp = os.path.join(R, "Holy_Guard.json")
    g = json.load(open(gp, encoding="utf-8")) if os.path.exists(gp) else {}
    g.setdefault("wallets", {})["w1"] = {"label": "main", "coins": {}, "orders": {"missing": {}, "stray": {}},
                                         "quotes": {"USDT": {"avail": 90.0, "dca_hold": 0.0, "min_next": 25.0, "ts": now}}}
    g.setdefault("events", [])
    g["v"] = 2                                                     # the guard file's own version (an older one is migrated — emptied)
    json.dump(g, open(gp, "w"))
    open(os.path.join(R, "_ui_launch.py"), "w").write(LAUNCH)
    d = subprocess.Popen([sys.executable, os.path.join(R, "_ui_launch.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    rr = subprocess.run(["node", os.path.join(H, "ui_temp_pause.js"), f"http://127.0.0.1:{P1}/", ksol, kxrp] + (["-q"] if Q else []),
                        capture_output=True, text=True, timeout=900, cwd="/tmp", env=env)
    out = (rr.stdout or "").strip()
    for ln in out.splitlines():
        if ln.startswith(("✅", "❌")) and not ln.startswith(("✅ ui_temp_pause.js", "❌ ui_temp_pause.js")):
            if not Q or ln.startswith("❌"):
                print(ln, flush=True)
    _m = re.search(r"ui_temp_pause\.js: (\d+)/(\d+)", out)
    if _m:
        res += [True] * int(_m.group(1)) + [False] * (int(_m.group(2)) - int(_m.group(1)))
    else:
        print(out[-1500:], rr.stderr[-1500:])
        res.append(False)
    s2 = json.load(open(sp_sol, encoding="utf-8"))
    cw = json.load(open(os.path.join(R, "Holy_CashWatch.json"), encoding="utf-8"))
    r_sol = (cw.get("bots") or {}).get(ksol) or {}
    mid = (lv[2] + lv[3]) / 2
    ok(f"🔓 «افتح» wrote the floor exactly between the 3rd and the 4th level ({s2.get('buy_floor')} ≈ {mid:.4f}) · the record keeps the rest closed "
       f"under it · the levels themselves untouched (the engine buys)", abs(float(s2.get("buy_floor") or 0) - mid) < 0.01 and abs(r_sol.get("temp", 0) - mid) < 0.01
       and len(s2.get("accum_buys") or {}) == 6, (s2.get("buy_floor"), r_sol))
    s3 = json.load(open(sp_xrp, encoding="utf-8"))
    r_x = (cw.get("bots") or {}).get(kxrp) or {}
    ok(f"▶️ «رفع إيقافك» opened the owner's valve only: own 0 · the engine's floor stays the temporary one ({s3.get('buy_floor')})",
       r_x.get("own") == 0 and abs(float(s3.get("buy_floor") or 0) - 2.43) < 1e-9, (r_x, s3.get("buy_floor")))
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
print(f"✅ ui_temp_pause: {sum(res)}/{len(res)}" if res and all(res) else f"❌ ui_temp_pause: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
