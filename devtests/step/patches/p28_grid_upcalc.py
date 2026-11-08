# 🧮 patch 28 (dashboard · the grid deploy form) — the owner (8-11): «اريد اتضيف لبوتات الشبكي حساب للاوردرات البعيدة يعني (مستويات فوق
#   السعر من عملاتك) الي موجودة في المتدرج لكن ليس له علاقة في البوت … الرقم فوق المستويات وخليه مفتوح مو ثابت على رقم وفيه افحص
#   اخر بيع او الي اين يصلل البيعات ، المهم ليس له علاقة لا بالمحرك ولا بأعدادات النشر».
#   A calculator in «➕ نشر بوت جرد» (♾️ · 🎚️ · ➕), folded by default: the number of levels above the price — open, any number — or the
#   last sell price you want (⇒ how many levels reach it; the two fields fill each other). It shows, from the form's grid % · order $ ·
#   base price (or the market price): where the last sell lands (+% above the price) · the coins those sells need · their value now
#   and if all sold at their prices · each level's row (the same formula as the range preview: price × (1+g)^n · coins = the order's $
#   at the level under it) · 🎚️: the levels above the range's top.
#   It is NOT part of the deploy: gridFormBody() does not read its fields, nothing is saved, the engine never sees it — a read-only
#   endpoint (/api/grid_up_calc) that computes and writes nothing.
#   python3 devtests/step/patches/p28_grid_upcalc.py Holy_Dashboard.pyw
import os, sys

PY = '''GRID_UP_MAX = 5000          # 🧮 v3.36.26: سقف أمان لحاسبة المستويات فوق السعر (العدد مفتوح لحد هنا)
GRID_UP_ROWS = 300          # صفوف من كل طرف بالرد (الوسط يختصر لمن العدد كبير)


def grid_up_calc(data):
    """🧮 v3.36.26 (طلب المالك 8-11): حاسبة «مستويات فوق السعر من عملاتك» لبوتات الشبكة — حساب بس قبل التشغيل: ما تدخل بالنشر
    ولا بإعدادات البوت ولا بالمحرك ولا تكتب أي ملف. العدد مفتوح (n) · أو آخر سعر بيع (top) ⇒ كم مستوى يوصله · لكل مستوى: سعر البيع
    = الأساس × (1+النسبة)^م (نفس معاينة النطاق) · العملات = قيمة الأمر بسعر المستوى اللي تحته · وين توصل آخر بيعة · 🎚️ فوق السقف"""
    try:
        g = float(data.get("grid_pct") or 0) / 100.0
        usd = float(data.get("usd_value") or 0)
        fb = float(data.get("forced_base") or 0)
        top = float(data.get("top") or 0)
        upper = float(data.get("upper_price") or 0) if str(data.get("g_type") or "") == "grid_range" else 0.0
    except Exception:
        return {"ok": False, "msg": "تأكد من الأرقام"}
    sym = str(data.get("symbol") or "").strip().upper()
    base, src = (fb, "forced") if fb > 0 else (0.0, "market")
    if base <= 0 and "-" in sym:
        try:
            base = float(PX.get(sym) or 0) or float(_acc_price(sym) or 0)
        except Exception:
            base = 0.0
    if not (g > 0 and usd > 0) or not all(math.isfinite(x) for x in (g, usd, fb, top, upper)):
        return {"ok": False, "msg": "نسبة الشبكة وقيمة الأمر يجب أن تكونا أكبر من صفر"}
    if base <= 0:
        return {"ok": False, "msg": "سعر العملة غير معروف — اكتب الرمز صحيحاً أو حدّد سعر الأساس"}
    step = 1.0 + g
    if top > 0:
        if top < base * step * (1 - 1e-9):
            return {"ok": False, "msg": f"آخر سعر بيع يجب أن يكون عند أول مستوى ({base * step:.8g}) أو فوقه"}
        n = int(math.floor(math.log(top / base) / math.log(step) + 1e-9))
    else:
        try:
            n = int(float(str(data.get("n") or "0").strip()))
        except Exception:
            n = 0
        if n < 1:
            return {"ok": False, "msg": "عدد المستويات من 1 فما فوق"}
    capped = n > GRID_UP_MAX
    n = min(n, GRID_UP_MAX)
    rows, coins, val, above = [], 0.0, 0.0, 0
    for k in range(1, n + 1):
        p = base * step ** k
        q = usd * step / p
        coins += q
        val += q * p
        if upper > 0 and p > upper * (1 + 1e-12):
            above += 1
        if k <= GRID_UP_ROWS or k > n - GRID_UP_ROWS:
            rows.append({"n": k, "p": float(f"{p:.8g}"), "pct": round((step ** k - 1) * 100, 3), "q": float(f"{q:.8g}"), "v": round(q * p, 4),
                         "up": bool(upper > 0 and p > upper * (1 + 1e-12))})
    last = base * step ** n
    return {"ok": True, "base": float(f"{base:.10g}"), "src": src, "n": n, "capped": capped, "max": GRID_UP_MAX, "cut": n > 2 * GRID_UP_ROWS,
            "rows": rows, "last": float(f"{last:.8g}"), "last_pct": round((step ** n - 1) * 100, 3), "coins": float(f"{coins:.10g}"),
            "now_usd": round(coins * base, 4), "sell_usd": round(val, 4), "upper": upper, "above": above, "base_ccy": sym.split("-")[0] if "-" in sym else ""}


'''

FORM = '''  <details id="n_upc" class="gupc" ontoggle="if(this.open)nUpCalc()">
    <summary>🧮 حاسبة المستويات فوق السعر (من عملاتك) — للحساب فقط</summary>
    <p class="gupn">لا تدخل في النشر ولا في إعدادات البوت ولا في المحرك. تحسب كم عملة تحتاجها لبيعات مستويات فوق السعر وأين تصل آخر بيعة — بنسبة الشبكة وقيمة الأمر وسعر الأساس المكتوبة أعلاه (أو سعر السوق).</p>
    <div class="frm">
      <div class="fld"><label>عدد المستويات فوق السعر (مفتوح)</label><input id="n_upn" class="num" inputmode="numeric" value="10" oninput="nUpSrc='n';nUpCalc()"></div>
      <div class="fld"><label>أو آخر سعر بيع تريد الوصول إليه</label><input id="n_uptop" class="num" inputmode="decimal" placeholder="—" oninput="nUpSrc='top';nUpCalc()"></div>
    </div>
    <div id="n_upres"></div>
  </details>
'''

JS = '''/* 🧮 v3.36.26: حاسبة «مستويات فوق السعر من عملاتك» لبوتات الشبكة — حساب فقط (لا تدخل في النشر ولا في المحرك · gridFormBody لا يقرأها) */
let nUpSrc='n',_nUpT=0,_nUpSeq=0;
function nUpCalc(){clearTimeout(_nUpT);_nUpT=setTimeout(nUpRun,300)}
async function nUpRun(){const box=$('#n_upres'),d=$('#n_upc');if(!box||!d||!d.open)return;
  const v=id=>(($('#'+id)||{}).value||'').trim(),gt=v('n_gtype');
  const body={symbol:v('n_sym').toUpperCase(),grid_pct:v('n_grid'),usd_value:v('n_usd'),forced_base:v('n_base'),g_type:gt,
    upper_price:gt==='grid_range'?v('n_upper'):0};
  if(nUpSrc==='top'&&v('n_uptop'))body.top=v('n_uptop');else body.n=v('n_upn');
  const my=++_nUpSeq;let R=null;try{R=await api('/api/grid_up_calc',body,true)}catch(e){}
  if(my!==_nUpSeq||!$('#n_upres'))return;
  if(!R||!R.ok){box.innerHTML=`<p class="gupe">❌ ${gEsc((R&&R.msg)||'تعذّر الحساب')}</p>`;return}
  if(nUpSrc==='top'){const e=$('#n_upn');if(e)e.value=R.n}else{const e=$('#n_uptop');if(e)e.value=R.last}
  const B=gEsc(R.base_ccy||'عملة'),P=x=>gEsc(String(x)),m2=x=>(+x).toFixed(2);
  let h=`<div class="gups"><span>🎯 من السعر <b dir="ltr">${P(R.base)}</b> (${R.src==='forced'?'سعر الأساس':'سعر السوق'})</span>
    <span>⬆️ <b>${R.n}</b> مستوى — آخر بيعة عند <b dir="ltr">${P(R.last)}</b> (<b dir="ltr">+${R.last_pct}%</b> فوق السعر)</span>
    <span>🪙 العملات المطلوبة: <b dir="ltr">${P(R.coins)}</b> ${B} — قيمتها الآن ≈ <b>${m2(R.now_usd)}$</b> · ولو بيعت كلها بأسعارها ≈ <b>${m2(R.sell_usd)}$</b></span></div>`;
  if(R.above)h+=`<p class="gupw">⚠️ ${R.above} مستوى فوق حد النطاق الأعلى (<span dir="ltr">${P(R.upper)}</span>) — البوت لا يبيع فوقه</p>`;
  if(R.capped)h+=`<p class="gupw">الحد الأقصى للحاسبة ${R.max} مستوى</p>`;
  h+=`<div class="gupt"><table class="dntbl"><thead><tr><th>المستوى</th><th>سعر البيع</th><th>فوق السعر</th><th>العملات</th><th>قيمتها $</th></tr></thead><tbody>`;
  let prev=0;(R.rows||[]).forEach(r=>{if(prev&&r.n!==prev+1)h+=`<tr><td colspan="5" class="gupg">… ${r.n-prev-1} مستوى في الوسط …</td></tr>`;prev=r.n;
    h+=`<tr${r.up?' class="gupx"':''}><td>${r.n}</td><td dir="ltr">${P(r.p)}</td><td dir="ltr">+${r.pct}%</td><td dir="ltr">${P(r.q)}</td><td dir="ltr">${m2(r.v)}</td></tr>`});
  box.innerHTML=h+'</tbody></table></div>'}
'''

CSS = '''.gupc{margin-top:12px;border:1px solid var(--line);border-radius:12px;padding:8px 10px;background:rgb(var(--ov-rgb)/.03)}.gupc>summary{cursor:pointer;font-weight:700;font-size:13px;color:var(--cyan)}.gupn{color:var(--mut);font-size:11.5px;line-height:1.7;margin:6px 0}.gups{display:flex;flex-direction:column;gap:4px;font-size:12px;margin:8px 0}.gupw{color:var(--amber);font-size:11.5px;margin:4px 0}.gupe{color:var(--red);font-size:12px}.gupt{max-height:260px;overflow:auto;margin-top:6px}.gupt td,.gupt th{text-align:center}.gupg{color:var(--mut2);font-size:11px}.gupx td{color:var(--amber)}
'''

R = [
    ('''def compute_grid_range_table(cfg, cp):''', PY + '''def compute_grid_range_table(cfg, cp):'''),
    ('''        if path == "/api/grid_range_preview":''',
     '''        if path == "/api/grid_up_calc":                  # 🧮 v3.36.26: حاسبة المستويات فوق السعر (حساب بس · ما تكتب شي)
            return self._json(grid_up_calc(data))
        if path == "/api/grid_range_preview":'''),
    ('''  <div id="n_share"></div>
  <div id="n_gpreview" style="margin-top:14px"></div>''',
     FORM + '''  <div id="n_share"></div>
  <div id="n_gpreview" style="margin-top:14px"></div>'''),
    ('''  setTimeout(()=>shareCheck('n_share',($('#n_sym')||{}).value,{wallet:($('#n_wallet')||{}).value}),0);
  $('#n_go').onclick=async()=>{''',
     '''  setTimeout(()=>shareCheck('n_share',($('#n_sym')||{}).value,{wallet:($('#n_wallet')||{}).value}),0);
  setTimeout(()=>['n_sym','n_grid','n_usd','n_base','n_upper'].forEach(id=>{const e=$('#'+id);if(e)e.addEventListener('input',()=>{const d=$('#n_upc');if(d&&d.open)nUpCalc()})}),0);   // 🧮
  $('#n_go').onclick=async()=>{'''),
    ('''function gridFormBody(){''', JS + '''function gridFormBody(){'''),
    ('''.mlad{display:flex;flex-direction:column;gap:4px}''', CSS.rstrip("\n") + '''.mlad{display:flex;flex-direction:column;gap:4px}'''),
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
