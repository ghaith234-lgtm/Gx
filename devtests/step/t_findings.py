# 🪜 🔎 findings — each probe tries to reproduce one suspected weakness of the graded-grid engine and prints what happened
#   (a reproduced finding waits for the owner's decision; after a fix its probe moves into the normal tests as a must-pass)
#   python3 devtests/step/t_findings.py [--only=F1,F2,...]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, D

ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)


def want(n):
    return ONLY is None or n in ONLY


def say(fid, reproduced, text):
    print(f"🔎 {fid} {'REPRODUCED' if reproduced else 'not reproduced'} — {text}", flush=True)


def live(b, side=None):
    return [o for o in b.mine() if o["state"] in ("live", "partially_filled") and (side is None or o["side"] == side)]


# F1 — fees paid in OKB (OKX's fee discount) are not counted ⇒ the booked profit is higher than the real one
if want("F1"):
    c = Clock(); ex = Ex(c, base=100, quote=1000, fee_mode="okb", okb=5, okb_px="50")
    b = Bot(ex).run(walk([1.0, 1.0101, 1.0, 0.97, 0.98, 0.99, 1.0, 1.0101, 1.0], 20))
    okb_usd = float((D(5) - ex.bal["OKB"]) * ex.okb_px)
    prof = float(b.st["total_profit"])
    say("F1", okb_usd > 1e-9 and not b.errors,
        f"booked profit {prof:.6f}$ · OKB spent on the fees {okb_usd:.6f}$ ⇒ real profit {prof - okb_usd:.6f}$ "
        f"({okb_usd / prof * 100:.1f}% of it is fees the books don't see)")

# F2 — a whole-coin quantity step (DOGE): a sell can be booked under zero though the coins kept back cover it
if want("F2"):
    c = Clock(); ex = Ex(c, sym="DOGE-USDT", price=0.15, tick="0.00001", lot="1", mn="10", base=1000, quote=1000)
    b = Bot(ex, {"forced_base_price": 0.15, "min_price": 0.1, "step_parts": 5, "step_sell": 0.02, "grid_percentage": 0.05})
    b.run(walk([0.15, 0.142, 0.142, 0.1449, 0.148, 0.151, 0.154, 0.157, 0.15], 20))
    neg = [m for m in b.hist() if m.startswith("🔴") and "الربح: -" in m]
    say("F2", bool(neg) and not b.errors,
        f"{len(neg)} of {sum(1 for m in b.hist() if m.startswith('🔴'))} sells booked under zero · fee dust kept {b.st.get('fee_dust')} DOGE · "
        f"e.g. «{neg[0][:120] if neg else ''}» — the money is fine (books = wallet), the log line says a loss")

# F3 — an order that reaches OKX more than 120 s late (after the bot gave up and sent it again) and fills at once
if want("F3"):
    hit = [0]

    def late_first(op, p):
        if op == "place" and not hit[0]:
            hit[0] = 1
            return ("late", 200.0)
        return None
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    ex.fault = late_first
    b = Bot(ex).run(walk([1.0] * 6 + [0.96] * 3, 30))
    say("F3", bool(b.errors),
        "an order lands 200 s late after the bot resent it and the price is already through it ⇒ it fills before the sweep "
        f"cancels it ⇒ {'wallet ≠ books: ' + b.errors[0] if b.errors else 'books still fine'} · in practice OKX refuses a signed "
        "request older than ~30 s, so this needs a delay OKX doesn't allow")

# F4 — more than 100 open orders on the coin (other bots in the same wallet): the stray sweep stops · extra checks every loop
if want("F4"):
    c = Clock(); ex = Ex(c, base=100, quote=5000)
    b = Bot(ex)
    b.run(walk([1.0], 20))
    for i in range(110):                     # another bot's orders, newer than ours (OKX lists the newest first, 100 per page)
        ex._place({"side": "buy", "px": str(0.5 + i * 0.001), "sz": "1", "clOrdId": f"HBOTHERb{i}", "stpMode": ""})
    stray = ex._place({"side": "buy", "px": "0.4", "sz": "2", "clOrdId": b.bot_id + "bzz", "stpMode": ""})["data"][0]["ordId"]
    q0 = ex.calls["order"]
    b.audit_on = False
    b.run(walk([1.0, 1.0, 1.0], 20))
    per_loop = (ex.calls["order"] - q0) / 20.0
    say("F4", ex.orders[stray]["state"] == "live" or per_loop > 1,
        f"110 other orders on the coin ⇒ a stray order with the bot's id {'stays alive' if ex.orders[stray]['state'] == 'live' else 'is canceled'} · "
        f"{per_loop:.1f} order checks per loop (the bot's own orders fall off OKX's first page)")

# F5 — a crossed order (the price jumped past a level) is sent at the market ± 0.2% with «cancel the maker» self-trade
#      prevention: it can cancel ANOTHER bot's resting order in that 0.2% band (same account)
if want("F5"):
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex, {"step_window": 1})          # one buy on OKX, the others in memory
    b.run(walk([1.0], 20))
    ex.move("0.94")                           # a jump through levels −1 and −2 (0.9708 · 0.9426): those in memory are «crossed»
    other = ex._place({"side": "sell", "px": "0.9412", "sz": "3", "clOrdId": "HBOTHERs1", "stpMode": ""})["data"][0]["ordId"]
    b.run(walk([0.94, 0.94], 20))
    st = ex.orders[other]
    say("F5", st["state"] == "canceled" and st.get("stp"),
        f"another bot's sell at 0.9412 (0.13% over the price) when our crossed buys go out at the market +0.2% ⇒ {st['state']}"
        f"{' by self-trade prevention' if st.get('stp') else ''}")

# F6 — the wallet's coins for the levels above are checked only at birth: if they go (another bot / by hand), a rejected
#      wallet sell (51008) calms the WHOLE sell side — do the sells of bought coins still go out?
if want("F6"):
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex)
    b.run(walk([1.0, 0.97, 0.965, 0.965], 20))      # level −1 bought (its sells are due at 0.9806 · 0.9903 · 1.0)

    def take_coins(bb):                              # another bot / the owner takes the wallet's free coins
        free = bb.ex.avail(bb.ex.base)
        bb.ex.bal[bb.ex.base] -= free - D("15.5")   # leaves only what level −1 bought
        bb.coin0 -= free - D("15.5")
    b.audit_on = False
    for o in live(b, "sell"):
        ex._cancel(o["ordId"])                      # (so every sell must be placed again after the coins went)
    take_coins(b)                                   # while the bot is between two loops (here: before it starts again)
    b.run(walk([0.965] * 3 + [0.975, 0.985, 0.995, 1.005, 1.012, 1.02], 60))
    sold = [m for m in b.hist() if m.startswith("🔴") and "المستوى -1" in m]
    rej = [m for m in b.hist() if m.startswith("⚠️ [رفض أمر بيع")]
    say("F6", len(sold) < 3,
        f"wallet coins taken after birth ⇒ {len(rej)} sell rejections logged · level −1's 3 bought parts sold {len(sold)}/3 "
        "as the price rose through their prices")

# F8 — 💣 delete while the cancels don't reach OKX (a network blip): the bot still writes «destruct_done», logs «أُلغي N أمر»
#      and exits — the dashboard trusts destruct_done and skips its own cancel ⇒ the bot's orders stay live with no bot
if want("F8"):
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex)
    b.run(walk([1.0, 1.0], 20))
    n0 = len(live(b))
    ex.fault = lambda op, p: "drop" if op == "cancel" else None
    b.audit_on = False
    b.run([("do", lambda bb: (lambda pth: (lambda d: (d.update(self_destruct=True), __import__("json").dump(d, open(pth, "w"))))(
        __import__("json").load(open(pth))))(os.path.join(bb.dir, f"grid_state_{bb.ex.sym}.json"))), ("wait", 6)])
    left = live(b)
    say("F8", bool(left) and b.disk().get("destruct_done") is True,
        f"{n0} live orders · every cancel lost ⇒ destruct_done = {b.disk().get('destruct_done')} · the log: "
        f"«{next((m for m in b.hist() if m.startswith('💣')), '')}» · {len(left)} orders still live on OKX with no bot")

# F9 — the save after a fill fails (the state file held by another program · disk full) and keeps failing until the next
#      loop: the loop writes the pending log lines first, then saves — a power cut between the two ⇒ on restart the fill is
#      processed again (the state on disk never had it) ⇒ its log line twice (the dashboard books from the log)
if want("F9"):
    from okxsim import Cut
    ph = {"n": 0}
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex)
    _orig = b._load

    def _load9():
        m = _orig()
        inner = m.save_json

        def sj(path, data):
            if path == m.STATE_FILE and isinstance(data, dict):
                fx = data.get("fx_log") or {}
                if ph["n"] == 0 and any(str(x[1]).startswith("🔴") for x in fx.get("lines") or []):
                    ph["n"] = 1
                if ph["n"] == 1:
                    if data.get("fx_log"):
                        return False                    # every save fails while the fill's lines are pending
                    ph["n"] = 2
                    raise Cut("power cut after the flush, before its save")
            return inner(path, data)
        m.save_json = sj
        return m
    b._load = _load9
    b.audit_on = False
    b.run(walk([1.0, 1.0101, 1.0101, 1.0101], 20))
    s01 = [m_ for m_ in b.hist() if m_.startswith("🔴") and "المستوى 0 · الجزء 1/" in m_]
    fills = [x for x in ex.fills if x[2] == "sell"]
    say("F9", ph["n"] == 2 and len(s01) > len(fills),
        f"phase {ph['n']} · {len(fills)} sell fill on OKX · {len(s01)} sell lines in the log for it · books on disk "
        f"{b.disk().get('total_profit')} · log sum {sum(float(x.split('الربح: ')[1].split('$')[0]) for x in s01) if s01 else 0}")
