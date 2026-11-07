# 🪜🃏 patch 20 (dashboard · the 🪜 card made clear — the owner 7-11: «صلح الكرت وسويه مفهوم اكثر … واتشوف الذاكرة حتى لو الشراء عن
#   البيع بعيد»). The engine is not touched.
#   ① a sell's tap: «🛒 شراؤها الخاص: المستوى j بسعر … (البعد عن السعر · البيعة +x% فوقه)» · after it sells the same part buys back
#      there — published once among the nearest step_window buys, waiting in the bot's memory before that however far · the level's
#      parts (buys published / memory · sells) · its pot (💠 grown coins / dollars, cycles) · a buy level's tap: its own sells
#      (+d1 … above it) and each part's pot
#   ② «🪜 السلم» for 🪜 = the FULL ladder by level (was the grid's price list without the level/part link): every level — its fixed
#      buy, its N parts (buy or sell · published / in flight / memory · price · +x% above its buy · distance from the price · 💠) —
#      the price bar in its place · filters: levels holding coins or with an order (default) · near the price · all · loaded on
#      demand from /api/step_ladder (every slot, never cut)
#   ③ «💠 سلّم الإعادة»: one scrolling page (the two tables sat in a box of 56% of the screen — the part under the price showed 2 rows
#      of 129 on a phone) · «🪙 فوق السعر n · 💵 تحت السعر m · 💠 بيها إعادة k» · «⬇️ تحت السعر» · «💠 اللي بيها إعادة بس» · small
#      amounts in full (0.0244 — was «0.02») · the full list loaded on demand (the card's copy was cut at the 300 HIGHEST slots: with
#      thousands of slots — 20 parts × many levels — nothing near or under the price reached the screen)
#   ④ big settings (more than STEP_SL_MAX = 400 slots, e.g. 20 parts × 200 levels): the card's copy carries the levels that matter in
#      full (any order on OKX · a partial fill · the 10 nearest to the price) and the rest as [level, buy, buys waiting, sells
#      holding coins] — the phone no longer receives thousands of rows every refresh (the full ladder loads them all on demand)
#   ⑤ the card's 💠 row in full for small amounts · a one-line key under the price ruler
#   python3 devtests/step/patches/p20_step_card2.py Holy_Dashboard.pyw
import os, sys

R = [
    # ── ④ the slots for the card: big settings carry the levels that matter
    ('''def _step_slots_view(st):
    """🪜 v3.36.18: كل خانة للبطاقة (مسطرة السعر بالطول + التفاصيل) — [المستوى, الجزء, 'b'/'s', السعر, الكمية الباقية,
    'L' منشور / 'P' بالطريق / 'M' بالذاكرة, سعر الشراء, سعر البيع, كمية البيع, الكلفة, من عملاتك]"""
    out = []
    for s in (st.get("slots") or {}).values():
        try:
''',
     '''STEP_SL_MAX = 400          # 🪜 v3.36.20: فوقها البطاقة تاخذ المستويات المهمة كاملة والباقي مختصر (السلّم الكامل يجيبها كلها عند الطلب)


def _step_keep_levels(st, near=10):
    """🪜 v3.36.20: المستويات اللي تنعرض كاملة بالبطاقة لمن الخانات كثيرة — أي جزء عنده أمر (منشور · بالطريق) أو منفّذ جزئياً ·
    + أقرب `near` مستوى للسعر (الباقي — شراء ينتظر أو عملة ماسكها بالذاكرة — مختصر بعدّاداته · السلّم الكامل يجيبه كله)"""
    keep, lv = set(), {}
    for s in (st.get("slots") or {}).values():
        try:
            j = int(s["j"])
            lv[j] = float(s["bp"])
            if s.get("o") or float(s.get("acc") or 0) > 0:
                keep.add(j)
        except Exception:
            continue
    cp = float(st.get("current_price") or 0)
    if cp > 0:
        keep.update(sorted(lv, key=lambda j: abs(math.log(lv[j] / cp)) if lv[j] > 0 else 1e9)[:near])
    return keep


def _step_sl_far(st):
    """🪜 v3.36.20: المستويات اللي ما انعرضت كاملة (خانات كثيرة) — [المستوى, سعر الشراء, شراء ينتظر بالذاكرة, بيع ماسك عملة بالذاكرة]
    (ولا واحد منهم عنده أمر بالمنصة) · None = كلها كاملة"""
    S = st.get("slots") or {}
    if len(S) <= STEP_SL_MAX:
        return None
    keep, out = _step_keep_levels(st), {}
    for s in S.values():
        try:
            j = int(s["j"])
            if j not in keep:
                out.setdefault(j, [j, float(s["bp"]), 0, 0])[3 if s.get("side") == "sell" else 2] += 1
        except Exception:
            continue
    return sorted(out.values(), key=lambda e: -e[1])


def _step_slots_view(st, full=False):
    """🪜 v3.36.18: كل خانة للبطاقة (مسطرة السعر بالطول + التفاصيل) — [المستوى, الجزء, 'b'/'s', السعر, الكمية الباقية,
    'L' منشور / 'P' بالطريق / 'M' بالذاكرة, سعر الشراء, سعر البيع, كمية البيع, الكلفة, من عملاتك]
    v3.36.20: خانات كثيرة (> STEP_SL_MAX) ⇒ المستويات المهمة بس (الباقي `_step_sl_far`) · full=True ⇒ كلها (السلّم الكامل)"""
    S = st.get("slots") or {}
    keep = _step_keep_levels(st) if (not full and len(S) > STEP_SL_MAX) else None
    out = []
    for s in S.values():
        try:
            if keep is not None and int(s["j"]) not in keep:
                continue
'''),
    ('''            "sl": (_safe(_step_slots_view, st, default=None) if _bt == "grid_step" else None),     # 🪜 v3.36.18: البطاقة بالطول
''',
     '''            "sl": (_safe(_step_slots_view, st, default=None) if _bt == "grid_step" else None),     # 🪜 v3.36.18: البطاقة بالطول
            "sl_far": (_safe(_step_sl_far, st, default=None) if _bt == "grid_step" else None),     # 🪜 v3.36.20: الباقي مختصر
'''),
    ('''                      "slots": len(st.get("slots") or {})}
                     if b["cfg"].get("bot_type") == "grid_step" else None),''',
     '''                      "slots": len(st.get("slots") or {}), "W": int(float(b["cfg"].get("step_window") or 8))}
                     if b["cfg"].get("bot_type") == "grid_step" else None),'''),
    # ── ③ the 💠 rows: the ones that matter (all of them on demand)
    ('''def _step_ri_snapshot(b, st):''', '''def _step_ri_snapshot(b, st, full=False):'''),
    ('''    usd = coin = 0.0
    rows, uws, desync = [], [], []
    for key, s in sorted(S.items(), key=lambda kv: (-float(kv[1].get("bp") or 0), int(kv[1].get("k") or 0))):''',
     '''    usd = coin = 0.0
    rows, uws, desync = [], [], []
    keep = _step_keep_levels(st) if (not full and len(S) > STEP_SL_MAX) else None     # 🪜 v3.36.20: خانات كثيرة ⇒ اللي يهم بالبطاقة
    n_rows = 0
    for key, s in sorted(S.items(), key=lambda kv: (-float(kv[1].get("bp") or 0), int(kv[1].get("k") or 0))):'''),
    ('''            if key in uw:
                row.update(uw=True, s=str((uw.get(key) or {}).get("side") or row["s"]))
                uws.append(row)
            else:
                rows.append(row)
''',
     '''            if key in uw:
                row.update(uw=True, s=str((uw.get(key) or {}).get("side") or row["s"]))
                uws.append(row)
            else:
                n_rows += 1
                if keep is None or int(s.get("j") or 0) in keep or tv > 0 or row["c"] > 0 or io > 0:
                    rows.append(row)
'''),
    ('''            "usd": round(usd, 4), "coin": round(coin, 8), "rows": rows[:300], "cycles": int(ri.get("cycles") or 0), "levels": len(lv),''',
     '''            "usd": round(usd, 4), "coin": round(coin, 8), "rows": rows if full else rows[:2000], "n_rows": n_rows,
            "cycles": int(ri.get("cycles") or 0), "levels": len(lv),'''),
    # ── ② the full ladder on demand (read only · no keys)
    ('''def archive_view():''',
     '''def step_ladder_view(d_rel):
    """🪜 v3.36.20: السلّم الكامل لبوت متدرج عند الطلب — كل الخانات (بلا اختصار) + كل صفوف إعادة الاستثمار · قراءة بس (بلا مفاتيح)"""
    bots = bot_dirs()
    full = os.path.realpath(os.path.join(ROOT, str(d_rel or "")))
    if not full.startswith(os.path.realpath(ROOT)) or full not in bots:
        return {"ok": False, "msg": "مجلد غير معروف"}
    b = bots[full]
    if (b.get("cfg") or {}).get("bot_type") != "grid_step":
        return {"ok": False, "msg": "مو شبكي متدرج"}
    st = load_json(paths_of(b)[0]) or {}
    ri = _safe(_step_ri_snapshot, b, st, True, default=None) or {}
    return {"ok": True, "sl": _step_slots_view(st, full=True), "ri": ri.get("rows") or [],
            "cp": float(PX.get(b["symbol"]) or st.get("current_price") or 0)}


def archive_view():'''),
    ('''        if u.path == "/api/archive":                      # 🗄️ v3.36.18: البوتات المحذوفة (للعرض)
''',
     '''        if u.path == "/api/step_ladder":                  # 🪜 v3.36.20: السلّم الكامل (كل الخانات · كل صفوف 💠) — قراءة بس
            return self._json(_safe(step_ladder_view, q.get("dir", [""])[0], default={"ok": False}))
        if u.path == "/api/archive":                      # 🗄️ v3.36.18: البوتات المحذوفة (للعرض)
'''),
    # ── the page: counts with the far levels · the key under the ruler
    ('''function stCount(b){const c={pb:0,ps:0,mb:0,ms:0};(b.sl||[]).forEach(x=>{c[(x[5]==='M'?'m':'p')+(x[2]==='b'?'b':'s')]++});return c}''',
     '''function stCount(b){const c={pb:0,ps:0,mb:0,ms:0};(b.sl||[]).forEach(x=>{c[(x[5]==='M'?'m':'p')+(x[2]==='b'?'b':'s')]++});
  (b.sl_far||[]).forEach(f=>{c.mb+=+f[2]||0;c.ms+=+f[3]||0});return c}
const RIFULL={},STFULL={},RIF={};                  // 🪜 v3.36.20: السلّم الكامل وصفوف 💠 الكاملة (عند الطلب) · فلتر 💠
const stM=v=>{v=+v||0;const a=Math.abs(v);return (a>0&&a<1)?v.toFixed(4):v.toFixed(2)};     // المبالغ الصغيرة كاملة
const stQ=q=>fmtCoin(q).replace(/^\\+/,'');                     // الكمية بلا «+»
function stRiRow(b,k){const kk=String(k),dir=b&&b.dir;return (((b&&b.ri)||{}).rows||[]).find(r=>r.kk===kk)||(((RIFULL[dir]||{}).rows)||[]).find(r=>r.kk===kk)||null}'''),
    ('''function stLad(b,cp,o){o=o||{};const W=o.w||SK_W,H=o.h||(o.mini?220:290),SL=b.sl||[],dir=SKE(b.dir||'');cp=+cp||0;''',
     '''function stLad(b,cp,o){o=o||{};const W=o.w||SK_W,H=o.h||(o.mini?220:304),SL=b.sl||[],dir=SKE(b.dir||'');cp=+cp||0;'''),
    ('''  const t0=14,t1=H-14,Y=p=>t0+(t1-t0)*(hi-p)/(hi-lo),pu=(hi/cp-1)*100,pd=(1-lo/cp)*100,xl=44,xr=W-70;''',
     '''  const t0=14,t1=H-(o.mini?14:26),Y=p=>t0+(t1-t0)*(hi-p)/(hi-lo),pu=(hi/cp-1)*100,pd=(1-lo/cp)*100,xl=44,xr=W-70;'''),
    ('''  return `<svg class="stlad" viewBox="0 0 ${W} ${H}" data-stl-bot="${dir}" role="img" aria-label="أوامر الشبكي المتدرج بالطول حسب بعدها عن السعر">${g}</svg>`}''',
     '''  if(!o.mini)g+=skAR(W-4,H-3,'اللون = الشراء وبيعاته الخاصة · اضغط أي خط · 🪜 السلم = كل المستويات والذاكرة','r',9.5,'var(--mut2)');
  return `<svg class="stlad" viewBox="0 0 ${W} ${H}" data-stl-bot="${dir}" role="img" aria-label="أوامر الشبكي المتدرج بالطول حسب بعدها عن السعر">${g}</svg>`}'''),
    # ── ① the tap
    ('''function stPop(b,key,ev){const SL=b.sl||[],N=+((b.scfg||{}).N)||1,f=+((b.scfg||{}).f)||0.0008,cp=+b.cp||0,P=key.split(':');
  const d=p=>cp?`${((p/cp-1)*100>=0?'+':'')}${((p/cp-1)*100).toFixed(3)}%`:'';let h='';
  if(P[0]==='b'){const j=+P[1],L=SL.filter(x=>x[0]===j).sort((a,z)=>a[1]-z[1]),pb=L.find(x=>x[2]==='b'&&x[5]!=='M'),bp=pb?+pb[3]:(L.length?+L[0][6]:0);
    h=`<b style="color:${stCol(j)}">🛒 المستوى ${j} — شراء ثابت ${f4(bp)}</b><div class="stpd">البعد عن السعر ${d(bp)}</div>`+L.map(x=>{
      const st=x[5]==='L'?'منشور بالمنصة':x[5]==='P'?'بالطريق للمنصة':'بذاكرة البوت';
      return x[2]==='b'?`<div>الجزء ${x[1]}/${N}: 🟢 شراء ${fmtCoin(x[4])} بـ${f4(+x[3])} · ${st}</div>`
        :`<div>الجزء ${x[1]}/${N}: 🔴 يبيع ${fmtCoin(x[4])} بـ${f4(+x[3])} · ${st}</div>`}).join('')}
  else{const j=+P[1],k=+P[2],x=SL.find(y=>y[0]===j&&y[1]===k);if(!x)return;
    const px=+x[3],q=+x[4],sq=+x[8]||q,sp=+x[9]||0,cost=sq>0?sp*q/sq:0,pr=q*px*(1-f)-cost;
    h=`<b style="color:${stCol(j)}">🔴 بيعة الجزء ${k}/${N} من المستوى ${j}</b>`+
      `<div>السعر ${f4(px)} · البعد ${d(px)} · ${x[5]==='L'?'منشور بالمنصة':x[5]==='P'?'بالطريق للمنصة':'بذاكرة البوت'}</div>`+
      `<div>الكمية ${fmtCoin(q)} · ${x[10]?`من عملاتك (كأنها اشتُريت بـ${f4(+x[6])})`:`اشتراها بكلفة ${f4(q>0?cost/q:0)}`}</div>`+
      `<div>ربحها لو باعت بسعرها ≈ <b style="color:${pr>0?'var(--green)':'var(--red)'}">${pr>0?'+':''}${pr.toFixed(4)}$</b> (بعد العمولة)</div>`}''',
     '''function stPop(b,key,ev){const SL=b.sl||[],N=+((b.scfg||{}).N)||1,f=+((b.scfg||{}).f)||0.0008,cp=+b.cp||0,W=+((b.scfg||{}).W)||8,P=key.split(':');
  const d=p=>cp?`${((p/cp-1)*100>=0?'+':'')}${((p/cp-1)*100).toFixed(3)}%`:'';let h='';
  const stt=s=>s==='L'?'منشور بالمنصة':s==='P'?'بالطريق للمنصة':'بذاكرة البوت';
  const up=x=>`+${((+x[7]/+x[6]-1)*100).toFixed(2)}%`;                // 🪜 v3.36.20: البيعة فوق شرائها الخاص
  const pot=x=>{const r=stRiRow(b,`${x[0]}:${x[1]}`);return r&&(r.g>0||r.k>0)?` · 💠 ${x[2]==='s'?'+'+stQ(r.g)+' عملة':'+'+stM(r.g*r.p+r.k)+'$'}`:''};
  if(P[0]==='b'){const j=+P[1],L=SL.filter(x=>x[0]===j).sort((a,z)=>a[1]-z[1]),pb=L.find(x=>x[2]==='b'&&x[5]!=='M'),bp=pb?+pb[3]:(L.length?+L[0][6]:0);
    h=`<b style="color:${stCol(j)}">🛒 المستوى ${j} — شراء ثابت ${f4(bp)}</b><div class="stpd">البعد عن السعر ${d(bp)} · بيعاته الخاصة ${L.map(up).join(' · ')} فوقه</div>`+L.map(x=>
      x[2]==='b'?`<div>الجزء ${x[1]}/${N}: 🟢 شراء ${stQ(x[4])} بـ${f4(+x[3])} · ${stt(x[5])}${pot(x)}</div>`
        :`<div>الجزء ${x[1]}/${N}: 🔴 يبيع ${stQ(x[4])} بـ${f4(+x[3])} (${up(x)} فوق شرائه · ${d(+x[3])} عن السعر) · ${stt(x[5])}${pot(x)}</div>`).join('')}
  else{const j=+P[1],k=+P[2],x=SL.find(y=>y[0]===j&&y[1]===k);if(!x)return;
    const px=+x[3],q=+x[4],sq=+x[8]||q,sp=+x[9]||0,cost=sq>0?sp*q/sq:0,pr=q*px*(1-f)-cost,bp=+x[6];
    const L=SL.filter(y=>y[0]===j),nb=L.filter(y=>y[2]==='b'),pbn=nb.filter(y=>y[5]!=='M').length,r=stRiRow(b,`${j}:${k}`);
    h=`<b style="color:${stCol(j)}">🔴 بيعة الجزء ${k}/${N} من المستوى ${j}</b>`+
      `<div>السعر ${f4(px)} · البعد ${d(px)} · ${stt(x[5])}</div>`+
      `<div>الكمية ${stQ(q)} · ${x[10]?`من عملاتك (كأنها اشتُريت بـ${f4(bp)})`:`اشتراها بكلفة ${f4(q>0?cost/q:0)}`}</div>`+
      `<div>ربحها لو باعت بسعرها ≈ <b style="color:${pr>0?'var(--green)':'var(--red)'}">${pr>0?'+':''}${pr.toFixed(4)}$</b> (بعد العمولة)</div>`+
      `<div style="border-top:1px dashed ${stCol(j)};margin-top:6px;padding-top:5px">🛒 <b>شراؤها الخاص: المستوى ${j}</b> بسعر <b>${f4(bp)}</b> (${d(bp)} عن السعر · البيعة ${up(x)} فوقه)</div>`+
      `<div style="color:var(--mut)">لمن تبيع يرجع نفس الجزء يشتري بـ${f4(bp)} — ينشر لمن يصير من أقرب ${W} شراء للسعر، وقبلها ينتظر بذاكرة البوت مهما بعد.</div>`+
      `<div style="color:var(--mut2)">أجزاء هالمستوى: 🟢 ${nb.length} شراء (${pbn} منشور) · 🔴 ${L.length-nb.length} بيع</div>`+
      (r&&(r.g>0||r.k>0)?`<div>💠 حصّالة هالجزء: +${stQ(r.g)} عملة داخل البيعة${r.k>=0.00005?' · '+stM(r.k)+'$':''} · ${r.c||0} دورة — ربحها يرجع لشرائها هذا</div>`:'')}'''),
    # ── ② «🪜 السلم» for 🪜 = the full ladder by level
    ('''function stLadOld(R,b,cp){''',
     '''async function stFull(dir){const b=botOf(dir);if(!b)return;              // 🪜 v3.36.20: السلّم الكامل بالمستوى (حتى الذاكرة البعيدة)
  showModal(`<h2>🪜 السلّم الكامل — ${gEsc(b.symbol)}</h2><p style="color:var(--mut);font-size:12px">⏳ أجيب كل المستويات…</p>`);
  let V=null;try{V=await api('/api/step_ladder?dir='+encodeURIComponent(dir),null,1)}catch(e){V=null}
  if(V&&V.ok){STFULL[dir]=Object.assign(STFULL[dir]||{},{t:Date.now(),sl:V.sl||[],cp:+V.cp||0});RIFULL[dir]={t:Date.now(),rows:V.ri||[]}}
  stFullDraw(dir,(STFULL[dir]||{}).flt||'own')}
function stFullDraw(dir,flt){const b=botOf(dir);if(!b)return;const F=STFULL[dir]||(STFULL[dir]={});F.flt=flt;
  const fresh=F.sl&&F.sl.length&&Date.now()-(F.t||0)<120000,SL=fresh?F.sl:(b.sl||[]),cp=+b.cp||+F.cp||0,sc=b.scfg||{};
  const N=+sc.N||1,W=+sc.W||8,G=+sc.G||0,far=fresh?[]:(b.sl_far||[]);
  const d=p=>cp?`${((p/cp-1)*100>=0?'+':'')}${((p/cp-1)*100).toFixed(2)}%`:'';
  const stt=s=>s==='L'?'<span style="color:var(--green)">منشور</span>':s==='P'?'<span style="color:var(--amber)">بالطريق</span>':'<span style="color:var(--mut2)">بالذاكرة</span>';
  const lv={};SL.forEach(x=>{(lv[x[0]]||(lv[x[0]]={j:x[0],bp:+x[6],p:[]})).p.push(x)});
  far.forEach(e=>{if(!lv[e[0]])lv[e[0]]={j:e[0],bp:+e[1],p:[],far:+e[2]||0,fars:+e[3]||0}});
  let L=Object.values(lv).sort((a,z)=>z.bp-a.bp);
  const own=g=>g.fars>0||g.p.some(x=>x[2]==='s'||x[5]!=='M'),dist=g=>cp>0&&g.bp>0?Math.abs(Math.log(g.bp/cp)):0;
  const near=new Set(L.slice().sort((a,z)=>dist(a)-dist(z)).slice(0,10).map(g=>g.j)),all=L.length,nOwn=L.filter(own).length;
  if(flt==='own')L=L.filter(own);else if(flt==='near')L=L.filter(g=>near.has(g.j));
  const c={pb:0,ps:0,mb:0,ms:0};SL.forEach(x=>{c[(x[5]==='M'?'m':'p')+(x[2]==='b'?'b':'s')]++});far.forEach(e=>{c.mb+=+e[2]||0;c.ms+=+e[3]||0});
  const dd=Array.from({length:N},(_,i)=>((+(sc.d1!=null?sc.d1:sc.d)||0)+i*(+sc.d||0))*100);
  const dtxt=N>6?dd.slice(0,3).map(v=>'+'+v.toFixed(2)+'%').join(' · ')+' … +'+dd[N-1].toFixed(2)+'%':dd.map(v=>'+'+v.toFixed(2)+'%').join(' · ');
  const bar=`<div style="text-align:center;margin:8px 0;padding:6px;border-radius:10px;background:rgb(var(--vio-rgb)/.10);border:1px solid var(--line)"><span style="color:var(--vio)">⚡</span> <b class="num">${cp?f4(cp):'—'}</b> <span style="color:var(--mut2);font-size:11px">السعر الآن</span></div>`;
  let h='',cpd=false;
  L.forEach(g=>{if(!cpd&&cp&&g.bp<cp){h+=bar;cpd=true}
    const C=stCol(g.j),P=g.p.slice().sort((a,z)=>a[1]-z[1]),nb=P.filter(x=>x[2]==='b').length+(g.far||0),ns=P.filter(x=>x[2]==='s').length+(g.fars||0);
    h+=`<div style="border-inline-start:4px solid ${C};background:var(--bg1);border-radius:9px;padding:6px 9px;margin:6px 0">
      <div style="display:flex;justify-content:space-between;gap:6px;flex-wrap:wrap"><b style="color:${C}">🛒 المستوى ${g.j} — شراء ${f4(g.bp)}</b><span style="font-size:11px;color:var(--mut)">${d(g.bp)} · 🟢 ${nb} · 🔴 ${ns}</span></div>`+
      (g.far||g.fars?`<div style="font-size:11.5px;color:var(--mut2)">بالذاكرة (بعيد · ولا أمر بالمنصة): ${g.far?`🟢 ${g.far} شراء ينتظر`:''}${g.far&&g.fars?' · ':''}${g.fars?`🔴 ${g.fars} بيع ماسك عملته`:''}</div>`:'')+
      P.map(x=>{const r=stRiRow(b,`${x[0]}:${x[1]}`),pt=r&&(r.g>0||r.k>0)?` · <span style="color:var(--vio)">💠 ${x[2]==='s'?'+'+stQ(r.g):'+'+stM(r.g*r.p+r.k)+'$'}</span>`:'';
        return x[2]==='b'?`<div style="font-size:11.5px;line-height:1.75">الجزء ${x[1]}/${N}: 🟢 شراء ${stQ(x[4])} · ${stt(x[5])}${pt}</div>`
          :`<div style="font-size:11.5px;line-height:1.75">الجزء ${x[1]}/${N}: 🔴 بيع ${stQ(x[4])} بـ<b class="num">${f4(+x[3])}</b> (+${((+x[7]/+x[6]-1)*100).toFixed(2)}% فوق شرائه · ${d(+x[3])}) · ${stt(x[5])}${pt}</div>`}).join('')+`</div>`});
  if(!cpd&&L.length)h+=bar;
  const B=(k,t)=>`<button onclick="stFullDraw('${dir}','${k}')" style="font-size:11.5px;padding:3px 10px;border-radius:7px;${flt===k?'background:var(--cyan);color:var(--on-acc)':''}">${t}</button>`;
  showModal(`<h2>🪜 السلّم الكامل — ${gEsc(b.symbol)}</h2>
   <p style="color:var(--mut);font-size:12px;line-height:1.8;margin:0 0 6px">كل مستوى = <b>شراء ثابت</b>${G?` (بينه وبين اللي فوقه ${(G*100).toFixed(2)}%)`:''} و<b>${N} بيعات خاصة بيه</b>: ${dtxt} فوق سعر شرائه — كل بيعة تبيع عملات شرائها هي بس، ولمن تبيع يرجع نفس الجزء يشتري بنفس السعر.<br>
   على المنصة ${c.pb} شراء · ${c.ps} بيع (الأقرب ${W} لكل جهة) — بالذاكرة ${c.mb} شراء · ${c.ms} بيع${fresh?'':' · ⚠️ ما وصل السلّم الكامل — المعروض من البطاقة'}</p>
   <div style="display:flex;gap:6px;flex-wrap:wrap;margin:0 0 4px">${B('own',`ماسكة عملة أو منشورة (${nOwn})`)}${B('near','قرب السعر (10)')}${B('all',`الكل (${all})`)}</div>
   ${h||'<p style="color:var(--mut2);font-size:12px">— ولا مستوى بهالفلتر —</p>'}
   <div class="mbtns"><button onclick="hideModal()">إغلاق</button></div>`)}
function stLadOld(R,b,cp){'''),
    ('''function openLadder(dir){const b=botOf(dir);if(!b)return;const L=b.ladder;''',
     '''function openLadder(dir){const b=botOf(dir);if(!b)return;if(b.bot_type==='grid_step')return stFull(dir);const L=b.ladder;'''),
    # ── ③ «💠 سلّم الإعادة»: one page · counts · below the price · only with reinvest · the full list on demand · small amounts
    ('''  const rows=(I.rows||[]).slice(), uw=(I.unwind||[]).slice();
  const m2=v=>(+v).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});''',
     '''  const FR=RIFULL[dir],frOk=!!(FR&&Date.now()-FR.t<20000&&FR.rows.length);        // 🪜 v3.36.20: الصفوف كلها عند الطلب
  if(I.step&&(+I.n_rows||0)>(I.rows||[]).length&&!frOk)
    api('/api/step_ladder?dir='+encodeURIComponent(dir),null,1).then(V=>{if(V&&V.ok&&(V.ri||[]).length){RIFULL[dir]={t:Date.now(),rows:V.ri};openReinvestLadder(dir)}}).catch(()=>{});
  const rows0=(frOk?FR.rows:(I.rows||[])).slice(), uw=(I.unwind||[]).slice();
  const hasV=x=>(+x.tv||0)>0||(+x.c||0)>0||(+x.io||0)>0, ONLYV=!!RIF[dir], nV=rows0.filter(hasV).length;
  const rows=ONLYV?rows0.filter(hasV):rows0;
  const m2=v=>(+v).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
  const mS=v=>{const a=Math.abs(+v||0);return (a>0&&a<1)?(+v).toFixed(4):m2(v)};'''),
    ('''  if(!rows.length&&!uw.length){''', '''  if(!rows0.length&&!uw.length){'''),
    ('''<b>+${m2(ad)}</b>''', '''<b>+${mS(ad)}</b>'''),
    ('''<b>+${m2(tg)}</b>''', '''<b>+${mS(tg)}</b>'''),
    ('''    <div style="font-size:12px;color:var(--cyan);margin:2px 0 4px">
      💵 شراء معلّق — ينتظر نزول السعر</div>''',
     '''    <div id="riBelow" style="font-size:12px;color:var(--cyan);margin:2px 0 4px">
      💵 شراء معلّق — ينتظر نزول السعر</div>'''),
    ('''   <div style="max-height:56vh;overflow:auto">${h}</div>''',
     '''   <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:0 0 6px;font-size:11.5px;color:var(--mut)">
     <span>🪙 فوق السعر <b>${S.length}</b> · 💵 تحت السعر <b>${B.length}</b> · 💠 بيها إعادة <b>${nV}</b>${(+I.n_rows||0)>rows0.length?` · ⏳ أجيب الباقي (${I.n_rows})`:''}</span>
     <button onclick="const e=document.getElementById('riBelow');if(e)e.scrollIntoView({block:'start'})" style="font-size:11px;padding:2px 9px;border-radius:7px">⬇️ تحت السعر</button>
     <button onclick="RIF['${dir}']=!RIF['${dir}'];openReinvestLadder('${dir}')" style="font-size:11px;padding:2px 9px;border-radius:7px;${ONLYV?'background:var(--cyan);color:var(--on-acc)':''}">💠 اللي بيها إعادة بس</button></div>
   <div>${h}</div>'''),
    # ── ⑤ the card's 💠 row in full for small amounts
    ('''${m(I.usd)}$</span>''', '''${stM(I.usd)}$</span>'''),
]
RALL = [   # (old, new, count) — the same line in the injection and the withdrawal dialogs
    ('''  const _sl=((b.ri||{}).rows||[]).find(x=>x.kk===String(k));''', '''  const _sl=stRiRow(b,k);''', 2),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for i, (a, b, n) in enumerate(RALL):
        if s.count(a) != n:
            print(f"❌ replace-all {i}: found {s.count(a)} times (want {n}) — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} + {len(RALL)} replacements · compiles · {p}")
