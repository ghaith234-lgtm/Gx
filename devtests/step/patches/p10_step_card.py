# 🪜 patch 10 (dashboard · the owner 6-11) — the graded grid's card, every skin (old · ج · ب · OKX): a vertical price ruler — each
#   line at its real distance from the current price · one line per buy level with its count (published · in memory) · every sell its
#   own line, no number · a level and its sells share one colour (overlaps show) · tap a line ⇒ its details · the horizontal strip
#   is not drawn for this bot. The server adds every slot to the card's data (`sl`: level · part · side · price · quantity · on the
#   exchange / on its way / in memory · buy and sell prices · cost).
#   python3 devtests/step/patches/p10_step_card.py Holy_Dashboard.pyw      (in place · only the named definitions change)
import ast, os, re, sys

JS = r'''/* 🪜 v3.36.18 (المالك 6-11): بطاقة الشبكي المتدرج لكل الأشكال — مسطرة سعر بالطول: كل خط بمكانه حسب بعده عن السعر الحالي ·
   شراء المستوى خط واحد بعدّاده (المنشور · اللي بالذاكرة) · كل بيعة خطها بلا رقم · المستوى وبيعاته نفس اللون (يبين التداخل) ·
   اضغط أي خط ⇒ تفاصيله · sl = [المستوى, الجزء, 'b'/'s', السعر, الكمية الباقية, 'L' منشور / 'P' بالطريق / 'M' بالذاكرة, الشراء, البيع, كمية البيع, الكلفة, من عملاتك] */
const ST_PAL=['#38bdf8','#c084fc','#fbbf24','#34d399','#f472b6','#60a5fa','#a3e635','#fb923c','#2dd4bf','#e879f9','#facc15','#818cf8'];   // (بلا أحمر: الأحمر خسارة)
function stCol(j){const n=ST_PAL.length;return ST_PAL[((+j%n)+n)%n]}
function stCount(b){const c={pb:0,ps:0,mb:0,ms:0};(b.sl||[]).forEach(x=>{c[(x[5]==='M'?'m':'p')+(x[2]==='b'?'b':'s')]++});return c}
function stCap(b){const c=stCount(b);return `على المنصة ${c.pb} شراء · ${c.ps} بيع — بالذاكرة ${c.mb} شراء · ${c.ms} بيع`}
function stLad(b,cp,o){o=o||{};const W=o.w||SK_W,H=o.h||(o.mini?220:290),SL=b.sl||[],dir=SKE(b.dir||'');cp=+cp||0;
  const lv={};
  SL.forEach(x=>{if(x[2]!=='b')return;const g=lv[x[0]]||(lv[x[0]]={j:x[0],p:+x[6],pub:0,mem:0,pend:0});
    if(x[5]==='M')g.mem++;else{g.pub++;if(x[5]==='P')g.pend++;g.p=+x[3]}});
  const B=Object.values(lv).filter(g=>g.pub>0).sort((a,z)=>z.p-a.p),S=SL.filter(x=>x[2]==='s'&&x[5]!=='M').sort((a,z)=>z[3]-a[3]);
  if(!cp||(!B.length&&!S.length))return `<svg class="stlad" viewBox="0 0 ${W} 54" data-stl-bot="${dir}">${skAR(W-8,32,'لا أوامر منشورة بالمنصة الآن','r',12,'var(--mut)')}</svg>`;
  const ps=[cp].concat(B.map(g=>g.p),S.map(x=>+x[3]));let lo=Math.min(...ps),hi=Math.max(...ps);
  const span=Math.max(hi-lo,cp*0.008),pad=span*0.07;lo-=pad;hi+=pad;       // من أوطى أمر لأعلى أمر — البعد بنسبته الحقيقية
  const t0=14,t1=H-14,Y=p=>t0+(t1-t0)*(hi-p)/(hi-lo),pu=(hi/cp-1)*100,pd=(1-lo/cp)*100,xl=44,xr=W-70;
  const sp=[0.1,0.25,0.5,1,2,5,10,20,50].find(s=>Math.max(pu,pd)/s<=3)||100;
  let g='';
  for(let k=-Math.floor(pd/sp);k<=Math.floor(pu/sp);k++){if(!k)continue;const y=Y(cp*(1+k*sp/100));
    g+=`<line x1="${xl}" y1="${y}" x2="${xr}" y2="${y}" stroke="rgb(var(--ov-rgb)/.08)" stroke-dasharray="2 4"/><text x="3" y="${y+3.5}" font-size="9.5" fill="var(--mut2)" direction="ltr">${k>0?'+':'−'}${+(Math.abs(k)*sp).toFixed(2)}%</text>`}
  const used=[Y(cp)],free=y=>!used.some(u=>Math.abs(u-y)<12);     // (the price badge's place is kept free)
  B.forEach(gr=>{const y=Y(gr.p),c=stCol(gr.j),lab=free(y);if(lab)used.push(y);
    g+=`<g class="stl" data-stl="b:${gr.j}"><rect x="0" y="${y-8}" width="${W}" height="16" fill="transparent"/>`+
      `<line x1="${xl}" y1="${y}" x2="${xr}" y2="${y}" stroke="${c}" stroke-width="3.4" stroke-linecap="round"${gr.pend?' stroke-dasharray="7 4"':''}/>`+
      (lab?`<text x="${W-3}" y="${y+4}" text-anchor="end" font-size="11" font-weight="700" fill="${c}" direction="ltr">${f4(gr.p)}</text>`+
        skAR(xr-4,y-5,`🛒 ${gr.pub}${gr.mem?` · ${gr.mem} بالذاكرة`:''}`,'r',10.5,c):'')+`</g>`});
  S.forEach(x=>{const y=Y(+x[3]),c=stCol(x[0]),lab=free(y);if(lab)used.push(y);
    g+=`<g class="stl" data-stl="s:${x[0]}:${x[1]}"><rect x="0" y="${y-6}" width="${W}" height="12" fill="transparent"/>`+
      `<line x1="${xl+26}" y1="${y}" x2="${xr}" y2="${y}" stroke="${c}" stroke-width="2" stroke-linecap="round" opacity=".9"${x[5]==='P'?' stroke-dasharray="4 3"':''}/>`+
      `<circle cx="${xr}" cy="${y}" r="3.2" fill="${c}"/>`+
      (lab?`<text x="${W-3}" y="${y+4}" text-anchor="end" font-size="10.5" fill="var(--tx)" direction="ltr">${f4(+x[3])}</text>`:'')+`</g>`});
  const yc=Y(cp);
  g+=`<g class="stcp"><line x1="${xl-6}" y1="${yc}" x2="${xr+4}" y2="${yc}" stroke="var(--cyan)" stroke-width="1.8" stroke-dasharray="4 3"/>`+
    `<rect x="${W-68}" y="${yc-10}" width="66" height="20" rx="8" fill="rgb(var(--cyan-rgb)/.18)" stroke="rgb(var(--cyan-rgb)/.6)"/>`+
    `<text x="${W-35}" y="${yc+4.5}" text-anchor="middle" font-size="11.5" font-weight="700" fill="var(--cyan)" direction="ltr">${f4(cp)}${o.dn==null?'':(o.dn?' ▼':' ▲')}</text></g>`;
  return `<svg class="stlad" viewBox="0 0 ${W} ${H}" data-stl-bot="${dir}" role="img" aria-label="أوامر الشبكي المتدرج بالطول حسب بعدها عن السعر">${g}</svg>`}
function stPop(b,key,ev){const SL=b.sl||[],N=+((b.scfg||{}).N)||1,f=+((b.scfg||{}).f)||0.0008,cp=+b.cp||0,P=key.split(':');
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
      `<div>ربحها لو باعت بسعرها ≈ <b style="color:${pr>0?'var(--green)':'var(--red)'}">${pr>0?'+':''}${pr.toFixed(4)}$</b> (بعد العمولة)</div>`}
  let e=document.getElementById('stpop');if(!e){e=document.createElement('div');e.id='stpop';document.body.appendChild(e)}
  e.innerHTML=h;e.style.display='block';const r=e.getBoundingClientRect(),vw=innerWidth,vh=innerHeight;
  e.style.left=Math.max(8,Math.min(vw-r.width-8,(ev.clientX||vw/2)-r.width/2))+'px';e.style.top=Math.max(8,Math.min(vh-r.height-8,(ev.clientY||vh/2)+14))+'px';
  clearTimeout(e._t);e._t=setTimeout(()=>{e.style.display='none'},9000)}
document.addEventListener('click',e=>{const p=document.getElementById('stpop');
  const t=e.target&&e.target.closest&&e.target.closest('[data-stl]');
  if(!t){if(p&&p.style.display==='block'&&!(e.target.closest&&e.target.closest('#stpop')))p.style.display='none';return}
  const sv=t.closest('[data-stl-bot]'),dir=sv&&sv.getAttribute('data-stl-bot'),bot=((DATA&&DATA.bots)||[]).find(x=>x.dir===dir);
  if(!bot)return;e.stopPropagation();e.preventDefault();stPop(bot,t.getAttribute('data-stl'),e)},true);
function stLadOld(R,b,cp){const w=Math.max(280,Math.min(560,(R.mlad.clientWidth||380)));const h=stLad(b,cp,{w,dn:null});
  if(R.mlad._h!==h){R.mlad.innerHTML=h;R.mlad._h=h}
  const ps=R.mlad.parentElement&&R.mlad.parentElement.querySelector('.pstrip');if(ps&&ps.style.display!=='none')ps.style.display='none';
  const t=stCap(b);if(R.ladn.textContent!==t){R.ladn.textContent=t;R.ladn.classList.remove('num');R.ladn.style.fontSize='11px'}}
'''

PY_VIEW = '''def _step_slots_view(st):
    """🪜 v3.36.18: كل خانة للبطاقة (مسطرة السعر بالطول + التفاصيل) — [المستوى, الجزء, 'b'/'s', السعر, الكمية الباقية,
    'L' منشور / 'P' بالطريق / 'M' بالذاكرة, سعر الشراء, سعر البيع, كمية البيع, الكلفة, من عملاتك]"""
    out = []
    for s in (st.get("slots") or {}).values():
        try:
            o = s.get("o") or {}
            buy = s.get("side") == "buy"
            live = bool(o.get("id")) and o.get("st") == "live"
            state = "L" if live else ("P" if o.get("st") == "send" else "M")
            px = float(o.get("px") or 0) if o and o.get("px") else float(s["bp"] if buy else s["sp"])
            rem = max(0.0, (float(s.get("q") or 0) if buy else float(s.get("sq") or 0)) - float(s.get("acc") or 0))
            out.append([int(s["j"]), int(s["k"]), "b" if buy else "s", _pv_sig(px), round(rem, 10), state, float(s["bp"]), float(s["sp"]),
                        round(float(s.get("sq") or 0), 10), round(float(s.get("spent") or 0), 10),
                        1 if (not buy and float(s.get("cost") or 0) <= 0 and int(s["j"]) >= 0) else 0])
        except Exception:
            continue
    return out


'''

R = [
    ('''            "ladder": {"sells": pack_levels(st.get("limit_sells"), "s"),''',
     '''            "sl": (_safe(_step_slots_view, st, default=None) if _bt == "grid_step" else None),     # 🪜 v3.36.18: البطاقة بالطول
            "ladder": {"sells": pack_levels(st.get("limit_sells"), "s"),'''),
    ('''"floor": float(b["cfg"].get("min_price") or 0),''',
     '''"floor": float(b["cfg"].get("min_price") or 0), "f": float(b["cfg"].get("fee_rate") or 0.0008),'''),
    ('''def _step_merge_lv(lv):''', PY_VIEW + '''def _step_merge_lv(lv):'''),
    ('''  const sells=(L.sells||[]).slice().sort((a,z)=>a.p-z.p).slice(0,4).reverse();
''', '''  if(b.bot_type==='grid_step')stLadOld(R,b,cp);else{          // 🪜 v3.36.18: مسطرة السعر بالطول
  const sells=(L.sells||[]).slice().sort((a,z)=>a.p-z.p).slice(0,4).reverse();
'''),
    ('''function skLadder(sells,buys,cp,o){''', JS + '''function skLadder(sells,buys,cp,o){'''),
    ('''    M.gfx=skLadder(L.sells,L.buys,cp,{dn:M.dn,range:''', '''    M.gfx=kd==='step'?stLad(b,cp,{w:SK_W,dn:M.dn}):skLadder(L.sells,L.buys,cp,{dn:M.dn,range:'''),
    ('''    M.cap=`🪜 الأوامر الحية · ${SKE(skText(el,'ladn'))}`''', '''    M.cap=kd==='step'?`🪜 ${SKE(stCap(b))}`:`🪜 الأوامر الحية · ${SKE(skText(el,'ladn'))}`'''),
    ('''.mlad{display:flex;flex-direction:column;gap:4px}''',
     '''.mlad{display:flex;flex-direction:column;gap:4px}.stlad{width:100%;height:auto;display:block}.stlad .stl{cursor:pointer}'''
     '''.stlad .stl:hover line{filter:brightness(1.35) drop-shadow(0 0 4px currentColor)}'''
     '''#stpop{position:fixed;z-index:2147483600;display:none;max-width:340px;background:var(--bg1);border:1px solid rgb(var(--cyan-rgb)/.5);'''
     '''border-radius:12px;padding:10px 12px;font-size:12.5px;line-height:1.7;color:var(--tx);box-shadow:0 10px 30px rgba(0,0,0,.45);direction:rtl}'''
     '''#stpop .stpd{color:var(--mut);font-size:11.5px}'''),
]
ALLOWED = {"bot_snapshot", "_step_slots_view", "HTML_PAGE"}


def tops(src):
    out, cnt = {}, {}
    for n in ast.parse(src).body:
        nm = getattr(n, "name", None)
        if nm is None and isinstance(n, ast.Assign) and len(n.targets) == 1:
            nm = ast.unparse(n.targets[0])
        if nm is None:
            cnt[type(n).__name__] = cnt.get(type(n).__name__, 0) + 1
            nm = f"<{type(n).__name__}#{cnt[type(n).__name__]}>"
        out.setdefault(nm, []).append(ast.dump(n))
    return out


def main(path):
    src0 = open(path, encoding="utf-8").read()
    src = src0
    for i, (a, b) in enumerate(R):
        if src.count(a) != 1:
            print(f"❌ replacement {i}: found {src.count(a)} times — nothing written: {a[:70]}"); sys.exit(1)
        src = src.replace(a, b)
    m = re.findall(r"\n  R\.ladn\.textContent=`\$\{b\.n_buys\+b\.n_vbuys[^\n]*\n", src)      # the old skin's ladder block ends here
    if len(m) != 1:
        print(f"❌ the ladn line found {len(m)} times — nothing written"); sys.exit(1)
    src = src.replace(m[0], m[0].rstrip("\n") + "}\n")
    compile(src, path, "exec")
    t0, t1 = tops(src0), tops(src)
    changed = {k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k)}
    if changed - ALLOWED:
        print(f"❌ unexpected top-level changes: {sorted(changed - ALLOWED)} — nothing written"); sys.exit(1)
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        fh.write(src)
    os.replace(path + ".tmp", path)
    print(f"✅ {len(R) + 1} replacements · changed {sorted(changed)} · {path}")


if __name__ == "__main__":
    main(sys.argv[1])
