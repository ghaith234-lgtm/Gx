# 🧪 patch 68 (dashboard · the trial sandbox's fake exchange) — found while examining the plus bot in the sandbox: the fake OKX answered
#   prices and sizes with Python's repr of a float sum («62.970000000000006» · «99.10000000000001» · «1.4200000000000002»), and the
#   engines wrote them into their log lines (🟢 [شراء فوري] السعر: 62.970000000000006 …) — the real OKX answers clean text («62.97»).
#   The sandbox now rounds those numbers to 12 decimals before it answers (what OKX would send) · px · avgPx · sz · accFillSz · fillSz ·
#   last · bidPx · askPx. The economics are unchanged (1e-12) — the books and the result read the same.
#   python3 devtests/step/patches/p68_bt_okx_numbers.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''        return {"instId": self.sym, "ordId": o["id"], "clOrdId": o["cl"], "side": o["side"], "ordType": o["type"], "sz": repr(o["sz"]),
                "px": repr(o["px"]) if o["type"] != "market" else "", "accFillSz": repr(o["acc"]), "fillSz": repr(o["acc"]),
                "avgPx": repr(o["avg"]) if o["acc"] else "", "state": st, "fee": repr(o["fee"]), "feeCcy": o["feeCcy"],''',
     '''        _n = _bt_num                                     # 🔢 v3.36.44: نص نظيف مثل OKX (كان repr لمجموع: 62.970000000000006)
        return {"instId": self.sym, "ordId": o["id"], "clOrdId": o["cl"], "side": o["side"], "ordType": o["type"], "sz": _n(o["sz"]),
                "px": _n(o["px"]) if o["type"] != "market" else "", "accFillSz": _n(o["acc"]), "fillSz": _n(o["acc"]),
                "avgPx": _n(o["avg"]) if o["acc"] else "", "state": st, "fee": repr(o["fee"]), "feeCcy": o["feeCcy"],'''),
    ('''            return {"code": "0", "msg": "", "data": [{"instId": self.sym, "last": repr(self.p), "bidPx": repr(self.bid()), "askPx": repr(self.ask()),''',
     '''            return {"code": "0", "msg": "", "data": [{"instId": self.sym, "last": _bt_num(self.p), "bidPx": _bt_num(self.bid()), "askPx": _bt_num(self.ask()),'''),
    ('''class _BtEx:
''',
     '''def _bt_num(v):
    """🔢 v3.36.44: رقم الصندوق المغلق كنص مثل ما ترده OKX — بلا ذيل الأعداد العشرية (repr(0.1 * 3) = 0.30000000000000004)"""
    return repr(round(float(v), 12))


class _BtEx:
'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
