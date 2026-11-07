# 💠↕️ patch 25 (dashboard · «💠 سلّم الإعادة») — the owner (7-11, his screenshot of the 💠 table): «ترتيب العملات … بعيدات عن السعر
#   1.17 صايرات فوق 1.18 … عندما يصعد السعر ايهم يصير بالمقدمه … الاقرب هو يصير بالمقدمة» — then «فقط ترتيب جدول اعادة استثمار».
#   The coins table (🪙 holding coins, above the price bar) was sorted by the BUY price only. For 🪜 every part of a level has the same
#   buy price ⇒ the parts kept their part order (1/3 · 2/3 · 3/3 = the NEAREST sell on top, the farthest next to the price bar), and
#   with overlapping settings a level's far sells sat above another level's near ones. Now the coins table is sorted by the SELL price,
#   high to low: the farthest on top, the nearest right above the price bar — the order they sell in as the price rises (the same as
#   the card's ruler and the full ladder: higher = higher). Ties by the buy price. ♾️ grid: one sell per buy ⇒ the same order as before.
#   The buys table (under the price) is unchanged: the highest buy first, right under the price bar.
#   python3 devtests/step/patches/p25_ri_order.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''  const S=all.filter(x=>x.s==='sell').sort((a,z)=>z.p-a.p);''',
     '''  const S=all.filter(x=>x.s==='sell').sort((a,z)=>(sp(z)-sp(a))||(z.p-a.p));   // 💠↕️ v3.36.23: بسعر البيع — الأقرب لاصق بخط السعر'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
