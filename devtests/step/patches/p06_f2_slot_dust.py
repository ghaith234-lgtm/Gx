# 🪜 patch 06 (engine · F2) — a coarse quantity step (DOGE: whole coins): the coins under the step went to ONE pool for the whole
#   bot at ZERO cost, while the sell that kept them back was charged the whole buy ⇒ that sell booked a loss (−0.09$) and a later
#   sell of another level got the coins free (booked more). The money was right, the profit of each sell was not.
#   Now every slot keeps its own leftover coins WITH their cost (`dq` coins · `dc` dollars): a buy's coins + the slot's leftover
#   share one cost per coin · the sell is charged exactly the coins it sold · what it could not sell stays with the slot at its
#   cost. Coins from the wallet: «as if bought» for exactly the coins they sell (sq·bp/(1−fee) — before: q·bp for fewer coins).
#   ⇒ every sell's booked profit = its real profit (> 0 by the no-loss rule).
#   python3 devtests/step/patches/p06_f2_slot_dust.py ENGINE.py      (in place · every old text found once)
import os, sys

R = [
    # birth: the wallet slots carry their «as if bought» basis · every slot starts with no leftover
    ('''    S = {}
    for r in lay:
        S[_skey(r["j"], r["k"])] = {"j": r["j"], "k": r["k"], "bp": r["bp"], "sp": r["sp"], "q": r["q"],
                                   "side": r["side"], "sq": r["sq"], "cost": 0.0, "acc": 0.0, "accv": 0.0, "accf": 0.0,
                                   "cyc": 0, "n": 0, "o": None}
''',
     '''    S = {}
    fee = float(stp["f"])
    for r in lay:
        S[_skey(r["j"], r["k"])] = {"j": r["j"], "k": r["k"], "bp": r["bp"], "sp": r["sp"], "q": r["q"],
                                   "side": r["side"], "sq": r["sq"], "cost": 0.0, "acc": 0.0, "accv": 0.0, "accf": 0.0,
                                   "spent": round(r["sq"] * r["bp"] / (1.0 - fee), 10) if r["side"] == "sell" else 0.0,
                                   "dq": 0.0, "dc": 0.0, "cyc": 0, "n": 0, "o": None}      # 🪙 الباقي تحت خطوة الكمية بكلفته (F2)
'''),
    # a buy done: its coins + the slot's own leftover share one cost per coin
    ('''        bought, spent, fc = s["acc"], s["accv"], s["accf"]
        avail = bought - fc + float(state.get("fee_dust") or 0)
        sq = _lot_floor(avail)
        state["fee_dust"] = round(max(0.0, avail - sq), 12)
        s.update(side="sell", sq=sq, spent=round(spent, 10), cost=round(spent / bought, 12), bq=round(bought, 12),
                 acc=0.0, accv=0.0, accf=0.0, cyc=int(s.get("cyc") or 0) + 1)
''',
     '''        bought, spent, fc = s["acc"], s["accv"], s["accf"]
        old = float(state.get("fee_dust") or 0)                  # (حوض قديم بلا كلفة — بوت قبل v3.36.17)
        avail = bought - fc + float(s.get("dq") or 0) + old
        tot = spent + float(s.get("dc") or 0)
        sq = _lot_floor(avail)
        basis = tot * (sq / avail) if avail > 0 else tot          # كلفة العملات اللي تنباع بالضبط (F2)
        if old:
            state["fee_dust"] = 0.0
        s.update(side="sell", sq=sq, spent=round(basis, 10), dq=round(max(0.0, avail - sq), 12), dc=round(tot - basis, 10),
                 cost=round(spent / bought, 12), bq=round(bought, 12), acc=0.0, accv=0.0, accf=0.0, cyc=int(s.get("cyc") or 0) + 1)
'''),
    # a sell done: charged exactly the coins it sold · the unsold stays with the slot at its cost
    ('''        basis = float(s.get("spent") or 0) if float(s.get("cost") or 0) > 0 else float(s["q"]) * float(s["bp"])
        cost = basis * (min(1.0, sold / sq) if sq > 0 else 1.0)
        profit = round(net - cost, 10)
        if sq - sold > 1e-12:
            state["fee_dust"] = round(float(state.get("fee_dust") or 0) + (sq - sold), 12)   # ما انباع (أصغر من حد المنصة) ⇒ مع البيعات الجاية
        state["total_profit"] = round(float(state.get("total_profit") or 0) + profit, 10)
        cb = round(basis / sold, 10) if sold > 0 else s["bp"]
''',
     '''        basis = float(s["spent"]) if float(s.get("spent") or 0) > 0 else float(s["q"]) * float(s["bp"])   # (بلا spent = بوت قديم)
        cost = basis * (min(1.0, sold / sq) if sq > 0 else 1.0)
        profit = round(net - cost, 10)
        if sq - sold > 1e-12:                                     # ما انباع (أصغر من حد المنصة) ⇒ يبقى للخانة بكلفته (F2)
            s["dq"] = round(float(s.get("dq") or 0) + (sq - sold), 12)
            s["dc"] = round(float(s.get("dc") or 0) + (basis - cost), 10)
        state["total_profit"] = round(float(state.get("total_profit") or 0) + profit, 10)
        cb = round(cost / sold, 10) if sold > 0 else s["bp"]
'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
