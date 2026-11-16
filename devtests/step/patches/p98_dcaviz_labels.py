# 🔎 patch 98 (dashboard v3.36.58) — the DCA card's drawing (dcaViz — the classic card and the skins C · B · OKX) kept a fixed 60-unit
#   column for the price labels on the left: a price of 1000 or more with its 4 decimals («2207.8963» · BTC «95000.0000») is wider and its
#   first digit was cut by the frame («207.8963»). Found on the v3.36.57 screenshots (ETH). The column now grows with the longest label.
#   python3 devtests/step/patches/p98_dcaviz_labels.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''  const nL=rows.length+3+(pk>0?1:0),W=320,H=Math.max(180,Math.min(340,34+nL*18)),pt=12,pb=14,X0=60,X1=228;
  const ps=rows.map(r=>+r.px).concat([avg,tgt,cp,pk].filter(x=>x>0));''',
     '''  const ps=rows.map(r=>+r.px).concat([avg,tgt,cp,pk].filter(x=>x>0));
  const X0=Math.max(60,Math.ceil(8+6.7*Math.max(...ps.map(p=>f4(p).length))));      // 🔎 v3.36.58: عمود الأسعار بعرض أطولها (1000 فأكثر ما ينقص أول رقم)
  const nL=rows.length+3+(pk>0?1:0),W=320,H=Math.max(180,Math.min(340,34+nL*18)),pt=12,pb=14,X1=228;'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacement · the DCA card's price labels fit (prices ≥ 1000) · compiles · {p}")
