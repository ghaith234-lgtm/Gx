# 🪜 the owner-approved fixes of the review (REVIEW.md) as must-pass tests — each part fails on the engine before its fix
#   F9  the save after a fill fails 1–3 times, then a power cut around the writing of its log line ⇒ the line once · log = books
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
TOL = 5e-7          # the log's profit per line is rounded to 6 decimals (until the exact-profit fix)


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

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
