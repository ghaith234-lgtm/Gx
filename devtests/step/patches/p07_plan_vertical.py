# 🪜 patch 07 (dashboard · the owner 6-11: «بالطول أفضل مفهوم أكثر») — the plan table before deploy: one row per sell
#   (the level · its fixed buy · its amount span the level's rows) with the sell's number · price · distance from the buy ·
#   net profit · a small profit is shown with 6 decimals (not «+0.0000$»).
#   python3 devtests/step/patches/p07_plan_vertical.py Holy_Dashboard.pyw      (in place · only HTML_PAGE changes)
import ast, os, sys

R = [
    ('''  h+=`<div class="stwrap"><table class="sttab"><thead><tr><th>المستوى</th><th>الشراء الثابت</th><th>البيعات (السعر · الربح الصافي)</th><th>المبلغ</th></tr></thead><tbody>`;
  (P.rows||[]).forEach(r=>{
    h+=`<tr class="${r.side==='inv'?'stinv':''}${r.j===0?' st0':''}"><td>${r.j}</td><td dir="ltr">${stN(r.bp)}${r.side==='inv'?' <small>(من عملاتك)</small>':''}</td>
      <td>${r.sells.map(s=>`<span class="stsl${s.skip?' skip':''}" dir="ltr">${stN(s.sp)} · <b class="${s.pr>0?'pos':'neg'}">${s.pr>0?'+':''}${(+s.pr).toFixed(4)}$</b></span>`).join(' ')}</td>
      <td dir="ltr">${r.side==='inv'?stN(r.coins)+' '+B:d2(r.usd)+'$'}</td></tr>`});
''',
     '''  const fp=v=>{v=+v||0;return (v>0?'+':'')+(Math.abs(v)<0.01?v.toFixed(6):v.toFixed(4))+'$'};   // 🪜 v3.36.17: بيعة لكل سطر (بالطول)
  h+=`<div class="stwrap"><table class="sttab"><thead><tr><th>المستوى</th><th>الشراء الثابت</th><th>البيعة</th><th>سعر البيع</th><th>البعد عن الشراء</th><th>الربح الصافي</th><th>المبلغ</th></tr></thead><tbody>`;
  (P.rows||[]).forEach(r=>{const L=(r.sells&&r.sells.length)?r.sells:[null],n=L.length,cls=`${r.side==='inv'?'stinv':''}`;
    L.forEach((s,i)=>{const sk=s&&s.skip?' stsk':'';
      h+=`<tr class="${cls}${i===0?' stg':''}${i===0&&r.j===0?' st0':''}" data-j="${r.j}"${s?` data-k="${s.k}"`:''}>`;
      if(i===0)h+=`<td rowspan="${n}">${r.j}</td><td rowspan="${n}" dir="ltr">${stN(r.bp)}${r.side==='inv'?' <small>(من عملاتك)</small>':''}</td>`;
      h+=s?`<td class="stk${sk}">${s.k}/${n}</td><td class="stsp${sk}" dir="ltr">${stN(s.sp)}</td><td class="stdi${sk}" dir="ltr">+${(((+s.sp)/(+r.bp)-1)*100).toFixed(3)}%</td><td class="stpr${sk}" dir="ltr"><b class="${s.pr>0?'pos':'neg'}">${fp(s.pr)}</b></td>`
          :'<td></td><td></td><td></td><td></td>';
      if(i===0)h+=`<td rowspan="${n}" dir="ltr">${r.side==='inv'?stN(r.coins)+' '+B:d2(r.usd)+'$'}</td>`;
      h+='</tr>'})});
'''),
    ('.stsl.skip{opacity:.4;text-decoration:line-through}',
     '.stsl.skip{opacity:.4;text-decoration:line-through}.sttab tr.stg td{border-top:1px solid rgb(var(--cyan-rgb)/.35)}'
     '.sttab td.stsk{opacity:.4;text-decoration:line-through}.sttab .pos{color:var(--green)}.sttab .neg{color:var(--red)}'
     '.sttab td[rowspan]{vertical-align:middle}'),
]


def main(path):
    src0 = open(path, encoding="utf-8").read()
    src = src0
    for i, (a, b) in enumerate(R):
        if src.count(a) != 1:
            print(f"❌ replacement {i}: found {src.count(a)} times — nothing written"); sys.exit(1)
        src = src.replace(a, b)
    t0 = {getattr(n, "name", None) or ast.dump(n)[:60]: ast.dump(n) for n in ast.parse(src0).body}
    t1 = {getattr(n, "name", None) or ast.dump(n)[:60]: ast.dump(n) for n in ast.parse(src).body}
    other = [k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k) and "HTML_PAGE" not in k]
    if other:
        print(f"❌ something besides HTML_PAGE changed: {other[:3]} — nothing written"); sys.exit(1)
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        fh.write(src)
    os.replace(path + ".tmp", path)
    print(f"✅ {len(R)} replacements · only HTML_PAGE · {path}")


if __name__ == "__main__":
    main(sys.argv[1])
