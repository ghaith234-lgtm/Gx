# 🪜 the owner-approved fixes of the review (REVIEW.md) as must-pass tests — each part fails on the engine before its fix
#   F9  the save after a fill fails 1–3 times, then a power cut around the writing of its log line ⇒ the line once · log = books
#   F10 every number in a log line is a plain decimal (the dashboard read «+9e-05$» as 9$) · the log's profit = the books exactly
#   F8  💣 while the cancels are lost / the internet is down / an order fills meanwhile ⇒ withdraws only when OKX confirms every
#       order gone · fills booked · no new order meanwhile · never trades again · the dashboard refuses to delete unconfirmed
#   python3 devtests/step/t_fixes.py [Holy_Dashboard.pyw] [-q] [--only=F9,...]        (STEP_ENGINE=… tests another engine copy)
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, Cut

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
DASHP = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:700]}"), flush=True)


def want(n):
    return ONLY is None or n in ONLY


PR = re.compile(r"الربح: ([+-][0-9.]+)\$")
TOL = 1e-9          # the log's profit is the books' own 10 decimals (F10)


def log_profit(b):
    return sum(float(PR.search(m).group(1)) for m in b.hist() if m.startswith("🔴") and PR.search(m))


# ── F9: fill lines are written only after the state holding the fill is on disk
if want("F9"):
    bad = []
    for fails in (1, 2, 3):
        for mode in ("before the line", "after the line", "at the save after it"):
            ph = {"fails": fails, "cut": 0}
            c = Clock(); ex = Ex(c, base=100, quote=1000)
            b = Bot(ex)
            _orig = b._load

            def _load9(_orig=_orig, ph=ph, mode=mode):
                m = _orig()
                sv, lg = m.save_json, m.log_trade_history

                def sj(path, data):
                    if path == m.STATE_FILE and isinstance(data, dict):
                        fx = data.get("fx_log") or {}
                        if ph["fails"] > 0 and any(str(x[1]).startswith("🔴") for x in fx.get("lines") or []):
                            ph["fails"] -= 1
                            return False                     # the state file held by another program / disk full
                        if mode == "at the save after it" and ph["cut"] == 1 and not data.get("fx_log"):
                            ph["cut"] = 2
                            raise Cut("cut at the save after the line")
                    return sv(path, data)

                def lt(sym, msg):
                    if msg.startswith("🔴") and ph["fails"] == 0 and ph["cut"] == 0:
                        ph["cut"] = 1
                        if mode == "before the line":
                            ph["cut"] = 2
                            raise Cut("cut before the line")
                        lg(sym, msg)
                        if mode == "after the line":
                            ph["cut"] = 2
                            raise Cut("cut after the line")
                        return
                    lg(sym, msg)
                m.save_json, m.log_trade_history = sj, lt
                return m
            b._load = _load9
            b.run(walk([1.0, 1.0101, 1.0101, 1.0101, 1.0101], 20))
            n_fill = sum(1 for x in ex.fills if x[2] == "sell")
            n_line = sum(1 for m_ in b.hist() if m_.startswith("🔴"))
            tp = float(b.disk().get("total_profit") or 0)
            if ph["cut"] != 2 or n_fill != n_line or abs(tp - log_profit(b)) > TOL * max(1, n_line) or b.errors:
                bad.append((fails, mode, ph["cut"], n_fill, n_line, tp, log_profit(b), b.errors[:1]))
    ok("F9: the save after a sell fails 1–3 times, then a power cut before / after its log line / at the save after it (9 cases) ⇒ "
       "the line in the log exactly once · the log's profit = the books · books = wallet every loop", not bad, bad[:3])

# ── F10: plain decimals in the log · the dashboard's own PROFIT_RE reads every sell's profit exactly
if want("F10"):
    import ast, math
    H = os.path.dirname(os.path.abspath(__file__))
    DASH = DASHP
    src = open(DASH, encoding="utf-8").read()
    PROFIT_RE = next(eval(compile(ast.Expression(n.value), DASH, "eval"), {"re": re}) for n in ast.parse(src).body
                     if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PROFIT_RE")
    import okxsim
    ns = {"Decimal": __import__("decimal").Decimal}
    for n in ast.parse(open(okxsim.ENGINE, encoding="utf-8").read()).body:
        if isinstance(n, ast.FunctionDef) and n.name == "_n":
            exec(compile(ast.Module([n], []), "eng", "exec"), ns)
    fn = ns.get("_n")
    cases = {9e-05: "0.00009", 1.23e-05: "0.0000123", 0.041923232: "0.041923232", 100.0: "100", 0.0: "0", -0.0: "0",
             1e-11: "0", 2.5: "2.5", 65000.1: "65000.1"}
    got = {k: (fn(k) if fn else None) for k in cases}
    ok("F10: the engine's number format: 9e-05 ⇒ 0.00009 · 1.23e-05 ⇒ 0.0000123 · 100 ⇒ 100 · −0 ⇒ 0 (no scientific notation)",
       fn and all(got[k] == v for k, v in cases.items()), got)
    c = Clock(); ex = Ex(c, base=100, quote=1000, tick="0.00001")     # (a fine price step: the sell is not rounded up past 0.0001$)
    b = Bot(ex, {"usd_value": 2.0, "step_parts": 1, "step_sell": 0.01, "step_first": 0.00165, "up_groups": 1})
    b.run(walk([1.0, 1.00166, 1.0, 1.00166, 1.0, 1.00166, 1.0, 1.00166, 1.0], 20))
    sells = [m_ for m_ in b.hist() if m_.startswith("🔴")]
    read = [float(PROFIT_RE.search(m_).group(1)) if PROFIT_RE.search(m_) else None for m_ in sells]
    tp = float(b.disk().get("total_profit") or 0)
    sci = [m_ for m_ in b.hist() if re.search(r"[0-9]e-[0-9]", m_)]
    ok(f"F10: first sell 0.165% (just above the two fees) · {len(sells)} sells each under 0.0001$ ⇒ the dashboard's PROFIT_RE reads "
       "each one right · their sum = the books (10 decimals) · no number in scientific notation anywhere in the log",
       len(sells) >= 3 and all(r is not None and 0 < r < 1e-4 for r in read) and abs(sum(read) - tp) < 1e-9 and not sci and not b.errors,
       (read, tp, sci[:2], b.errors[:1]))

# ── F8: 💣 withdraws only when OKX confirms that no order of the bot is left
if want("F8"):
    import json

    def press(bb, **kv):
        pth = os.path.join(bb.dir, f"grid_state_{bb.ex.sym}.json")
        d = json.load(open(pth))
        d.update(kv)
        json.dump(d, open(pth + ".dash", "w"))
        os.replace(pth + ".dash", pth)

    def mine_live(bb):
        return [o for o in bb.mine() if o["state"] in ("live", "partially_filled")]

    def scenario(name, during, after=None, n_drop=0):
        c = Clock(); ex = Ex(c, base=100, quote=1000)
        b = Bot(ex)
        b.run(walk([1.0, 1.0], 20))
        n0 = len(mine_live(b))
        k0 = len([o for o in b.mine()])
        drops = {"n": n_drop}

        def fault(op, p):
            if op == "cancel" and drops["n"] > 0:
                drops["n"] -= 1
                return "drop"
            return None
        ex.fault = fault
        steps = [("do", lambda bb: press(bb, self_destruct=True))] + during + [("wait", 200)]
        b.run(steps)
        made = len(b.mine()) - k0
        d = b.disk()
        lines = [m_ for m_ in b.hist() if m_.startswith("💣")]
        return b, ex, n0, made, d, lines

    # A — the first 20 cancels never reach OKX (a network blip)
    b, ex, n0, made, d, lines = scenario("blip", [], n_drop=20)
    ok(f"F8: 💣 while the first 20 cancels are lost ⇒ waits («الحذف ينتظر») · withdraws only when OKX confirms · 0 orders left of {n0} · "
       "no new order meanwhile · books = wallet",
       d.get("destruct_done") is True and not mine_live(b) and made == 0 and any("الحذف ينتظر" in x for x in lines)
       and any("كلها تأكد إلغاؤها" in x for x in lines) and not b.errors, (d.get("destruct_done"), len(mine_live(b)), made, lines[:3], b.errors[:2]))

    # B — the internet is down for 60 s after the press
    def down(bb):
        bb.ex.down = True

    def up(bb):
        bb.ex.down = False
    b, ex, n0, made, d, lines = scenario("down", [("do", down), ("wait", 60), ("do", up)])
    ok("F8: 💣 with the internet down 60 s ⇒ nothing withdrawn while down · back online ⇒ every order canceled and confirmed · no new order",
       d.get("destruct_done") is True and not mine_live(b) and made == 0 and not b.errors, (d.get("destruct_done"), len(mine_live(b)), made, b.errors[:2]))

    # C — a sell fills between the press and its (lost) cancel ⇒ booked
    b, ex, n0, made, d, lines = scenario("fill", [("px", 1.0101, 0)], n_drop=6)
    sold = [m_ for m_ in b.hist() if m_.startswith("🔴")]
    ok("F8: 💣 and a sell fills before its cancel arrives ⇒ the fill is booked (its 🔴 line · books = wallet every loop) · then withdraws",
       d.get("destruct_done") is True and not mine_live(b) and sold and not b.errors, (len(sold), d.get("destruct_done"), b.errors[:2]))

    # D — a bot that withdrew never trades again (the watchdog may start it)
    k1 = len(b.mine())
    b.run(walk([0.97, 1.02, 1.0], 30))
    ok("F8: started again after it withdrew ⇒ exits at once · no order placed", len(b.mine()) == k1 and not b.errors, (len(b.mine()) - k1, b.errors[:1]))

    # E — the dashboard's delete of a 🪜 bot: refused unless no order of the bot is confirmed left
    import importlib.machinery, importlib.util, shutil, tempfile
    H = os.path.dirname(os.path.abspath(__file__))
    R = tempfile.mkdtemp(prefix="t_fixes_")
    json.dump({"port": 8095}, open(os.path.join(R, "dashboard_config.json"), "w"))
    json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
    shutil.copy(DASHP, os.path.join(R, "Holy_Dashboard.pyw"))
    cwd0 = os.getcwd(); os.chdir(R)
    ld = importlib.machinery.SourceFileLoader("hd_fixes", os.path.join(R, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_fixes", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    os.chdir(cwd0)

    def fake_bot(kind):
        d_ = tempfile.mkdtemp(prefix="bot_", dir=R)
        cfg = {"api_key": "KEYA-tfx", "secret_key": "SECA-tfx", "passphrase": "PASA-tfx", "symbol": "XRP-USDT", "bot_type": kind,
               "bot_id": "HBTFX0000001", "auto_restart": True}
        cp_ = os.path.join(d_, "config_XRP-USDT.json")
        json.dump(cfg, open(cp_, "w"))
        json.dump({"total_profit": 0}, open(os.path.join(d_, "grid_state_XRP-USDT.json"), "w"))
        return {"dir": d_, "cfg_path": cp_, "cfg": cfg, "symbol": "XRP-USDT"}
    deleted = []
    m.is_alive = lambda *a, **k: (False, None)
    m.delete_bot = lambda bb: (deleted.append(bb["dir"]) or {"ok": True, "msg": "deleted"})
    m.tg_send = lambda *a, **k: True
    mine2 = [{"ordId": "1", "clOrdId": "HBTFX0000001s1"}, {"ordId": "2", "clOrdId": "HBTFX0000001b2"}, {"ordId": "9", "clOrdId": "OTHER1"}]
    seq = {"get": [], "posts": 0}
    m._okx_get = lambda *a, **k: seq["get"].pop(0) if seq["get"] else None
    m._okx_post = lambda *a, **k: (seq.__setitem__("posts", seq["posts"] + 1) or {"code": "0", "data": [{"sCode": "0"}, {"sCode": "0"}]})
    out = []
    for name, gets, kind, want_ok in (("no connection", [None, None], "grid_step", False),
                                      ("2 orders stay after the cancel", [{"code": "0", "data": mine2}, {"code": "0", "data": mine2}], "grid_step", False),
                                      ("canceled and confirmed", [{"code": "0", "data": mine2}, {"code": "0", "data": mine2[2:]}], "grid_step", True),
                                      ("never started (no order possible)", [None, None], "grid_step", None),
                                      ("♾️ bot, no connection (unchanged)", [None, None], "grid", True)):
        bb = fake_bot(kind)
        if want_ok is None:
            bb["cfg"].pop("bot_id")
            want_ok = True
        seq["get"] = list(gets)
        n_del = len(deleted)
        r = m.delete_purge(bb)
        auto = json.load(open(bb["cfg_path"])).get("auto_restart")
        good = bool(r.get("ok")) == want_ok and (len(deleted) > n_del) == want_ok and (want_ok or (auto is False and "لم يُحذف" in r.get("msg", "")))
        out.append((name, good, r.get("msg", "")[:90], auto))
    shutil.rmtree(R, ignore_errors=True)
    ok("F8: the dashboard deletes a 🪜 bot only when no order of it is confirmed left (no connection ⇒ refused · 2 left ⇒ refused · "
       "canceled and confirmed ⇒ deleted · never started ⇒ deleted) · refusal turns its auto-restart off · other kinds unchanged",
       all(x[1] for x in out), [x for x in out if not x[1]] or out)

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
