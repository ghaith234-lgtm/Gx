# 🪜 ⚡ a power cut at EVERY moment of a graded-grid story
#   moments = before/after every state save · every call to OKX (an order sent: «after» = OKX took it and the process died
#   before hearing the answer) · every cancel · every log line — the first moments are the bot's own birth.
#   Each cut: the process dies (BaseException), starts again from its files at once and the story goes on ⇒ the SAME fills,
#   the same profit, the same slots, the same log lines as the run with no cut (nothing twice, nothing lost) · books = wallet
#   at every loop. Each price is held 150 s: an order whose sending was cut waits SEND_WAIT (120 s) before it is resent
#   (OKX may still be receiving it) — by design, so the story gives it the time.  --move: the price moves while the bot is off (orders fill while it's down) ⇒ books = wallet, log once.
#   python3 devtests/step/t_cut.py [--move] [-q] [-jN] [--every=K]
import os, shutil, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk

MOVE = "--move" in sys.argv
Q = "-q" in sys.argv
NJ = int(next((a[2:] for a in sys.argv[1:] if a.startswith("-j") and a[2:].isdigit()), "4"))
EVERY = int(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--every=")), "1"))
STORY = [1.0, 1.0101, 1.0101, 1.0, 1.0, 0.97, 0.9705, 0.95, 0.9806, 0.9903, 1.0, 1.0205, 1.0305, 1.0, 1.0, 1.0, 1.0]


def _ri_view(rb):
    if not rb:
        return None
    return (round(float(rb.get("credited") or 0), 9), int(rb.get("cycles") or 0), bool(rb.get("on")),
            sorted((k, round(float(lv.get("usd_book") or 0), 9), round(float(lv.get("grown_qty") or 0), 12), int(lv.get("cycles") or 0))
                   for k, lv in (rb.get("levels") or {}).items()))


def story(cuts=(), move=False):
    c = Clock(); ex = Ex(c, base=100, quote=1000, partial=0.5)
    b = Bot(ex, {"step_window": 4})
    steps = walk(STORY, hold=150.0)          # > SEND_WAIT (120 s): an order cut before it was sent is resent within the same price
    off_steps = []
    if move and cuts:                        # while the bot is off, the market goes to the next price of the story
        k = min(cuts)
        off_steps = [("px", STORY[(k * 7) % len(STORY)], 0)]
    b.run(steps, cuts=cuts, off=30.0 if move else 0.0, off_steps=off_steps)
    out = {"fills": sorted((x[2], str(x[3]), str(x[4])) for x in ex.fills),
           "profit": round(float(b.st.get("total_profit") or 0), 9) if b.st else None,
           "slots": sorted((k, s["side"], s["cyc"], s.get("n", 0)) for k, s in (b.st or {}).get("slots", {}).items()),
           "log": sorted(m for m in b.hist() if m.startswith(("🟢", "🔴", "💠"))),
           "ri": _ri_view((b.st or {}).get("reinvest")),     # 💠 the pots too (STEP_CFG='{"reinvest": true, ...}')
           "errors": b.errors, "cuts": b.cuts, "moments": b.moments, "restarts": b.restarts}
    shutil.rmtree(b.dir, ignore_errors=True)
    return out


def one(k):
    try:
        r = story(cuts=(k,), move=MOVE)
    except BaseException as e:               # the runner itself must never die
        return k, None, f"{type(e).__name__}: {e}"
    return k, r, None


if __name__ == "__main__":
    ref = story()
    M = ref["moments"]
    res, bad = 0, []
    if ref["errors"] or not ref["fills"]:
        print("❌ the story itself fails:", ref["errors"][:3]); sys.exit(1)
    ks = list(range(1, M + 1, EVERY))
    with Pool(NJ) as pool:
        for k, r, e in pool.imap_unordered(one, ks, chunksize=4):
            if e or r is None:
                bad.append((k, "crash", e)); continue
            if r["cuts"] != 1:
                bad.append((k, "the cut never happened", r["moments"])); continue
            if r["errors"]:
                bad.append((k, "books", r["errors"][:2])); continue
            if not MOVE:
                for key in ("fills", "profit", "slots", "log", "ri"):
                    if r[key] != ref[key]:
                        bad.append((k, key, "differs from the run with no cut")); break
                else:
                    res += 1
            else:                            # the market moved while it was off: fills differ — the books/log audit is the check
                res += 1
    name = "t_cut --move" if MOVE else "t_cut"
    print(f"{'✅' if not bad else '❌'} {name}: {res}/{len(ks)} cuts ok · {M} moments in the story · {len(ref['fills'])} fills"
          + ("" if not bad else f" — {sorted(bad)[:4]}"))
    sys.exit(0 if not bad else 1)
