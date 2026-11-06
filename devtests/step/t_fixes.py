# 🪜 the owner-approved fixes of the review (REVIEW.md) as must-pass tests — each part fails on the engine before its fix
#   F9  the save after a fill fails 1–3 times, then a power cut around the writing of its log line ⇒ the line once · log = books
#   F10 every number in a log line is a plain decimal (the dashboard read «+9e-05$» as 9$) · the log's profit = the books exactly
#   python3 devtests/step/t_fixes.py [-q] [--only=F9,...]        (STEP_ENGINE=… tests another engine copy)
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, Cut

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
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
    DASH = os.path.join(H, "..", "..", "Holy_Dashboard.pyw")
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

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
