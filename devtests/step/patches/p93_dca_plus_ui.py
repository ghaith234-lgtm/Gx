# ⚡ patch 93 (dashboard v3.36.56 · DCA+) — the owner (15-11): «واريد انا اتحكم فيه ويظهر لي بالجدول والمخطط وانا اختار الخروج ويبين
#   لي بالرسم نفسه الي موجود بالdca». Everything a DCA+ bot shows and lets you control (the engine — patches 91/92 — does the work):
#   · the card (every look: classic · C · B · OKX): «⚡ DCA+ بيعي» · a «⚡ الخروج بالطبقات» button with its state · the card's own drawing
#     (dcaViz — the same one as the DCA) draws each filled layer's exit line «⚡ أمان n» (grey = switched off) · the status line counts
#     the layers that exited this cycle
#   · 📋 the table: a «⚡ خروج الطبقة» column — the exit price of every filled layer (and the one each waiting order will get), switched
#     off · below the start layer · too small · plus what exited (count · profit)
#   · ⚡ the control window (showModal · rule 14): on/off · the bounce % · the start layer · re-open · every open layer with its exit
#     price, its distance, «⛔ لا يخرج وحده / ⚡ يخرج وحده» and «⏏ أخرجها الآن» (your decision: a confirm with what it would make now)
#     · the last exits
#   · the server: `_dcap_view` (the card's data) · control actions lx_set · lx_layer · lx_now (state fields only — the engine sends the
#     orders; no new caller of _okx_post)
#   · deploy: «⚡ DCA+ بيعي» in the DCA form with its three settings (the bounce · the start layer · re-open — off by default: the owner
#     wants out fast) · the preview table shows each layer's exit price · 🧪 the trial path runs DCA+ from the form
#   · 📖 the tutorial: a «DCA+» tab in the DCA form's tutorial · the buttons explained
#   python3 devtests/step/patches/p93_dca_plus_ui.py Holy_Dashboard.pyw
import os, sys

VIEW = '''def _dcap_view(cfg, st, cp):
    """⚡ v3.36.56: DCA+ في الكرت — إعدادات الخروج بالطبقات الفعلية (الكرت أولاً ثم الإعدادات) · كل طبقة منفّذة وسعر خروجها · ما خرج"""
    def pick(k, d):
        v = st.get(k)
        return cfg.get(k, d) if v is None else v
    try:
        pct = min(10.0, max(0.3, float(pick("lx_pct", 0.5))))
    except Exception:
        pct = 0.5
    try:
        frm = max(1, int(float(pick("lx_from", 1))))
    except Exception:
        frm = 1
    def ints(xs):
        out = []
        for x in xs or []:
            try:
                out.append(int(x))
            except Exception:
                pass
        return out
    off, now, on = set(ints(st.get("lx_off"))), set(ints(st.get("lx_now"))), bool(pick("lx_on", True))
    layers = []
    for f in st.get("filled") or []:
        if not isinstance(f, dict):
            continue
        try:
            n = int(f.get("n", 0))
            ns = [int(x) for x in (f.get("ns") or [])] if n < 0 else [n]
            px, q = float(f.get("price") or 0), float(f.get("qty") or 0)
        except Exception:
            continue
        if not ns or min(ns) < 1 or px <= 0:
            continue
        ex = px * (1 - pct / 100.0)
        fid = int(f.get("fid") or 0)
        layers.append({"fid": fid, "ns": ns, "px": _pv_sig(px), "q": round(q, 8), "ex": _pv_sig(ex), "off": bool(set(ns) & off),
                       "low": min(ns) < frm, "small": bool(f.get("lx_small")), "now": fid in now,
                       "elig": on and min(ns) >= frm and not (set(ns) & off) and not f.get("lx_small"),
                       "dist": round((cp / ex - 1) * 100, 3) if ex > 0 and cp > 0 else None,
                       "net": round(float(f.get("net") or 0), 6)})
    log = [{k: e.get(k) for k in ("ts", "ns", "sold", "px", "out", "in", "profit", "manual", "whole")} for e in (st.get("lx_log") or [])[-8:]
           if isinstance(e, dict)]
    return {"on": on, "pct": pct, "from": frm, "reopen": bool(pick("lx_reopen", True)), "off": sorted(off), "layers": layers,
            "n": int(st.get("lx_count") or 0), "p": round(float(st.get("lx_profit") or 0), 8),
            "cn": int(st.get("lx_cycle_n") or 0), "cp": round(float(st.get("lx_cycle_p") or 0), 8), "log": log[::-1],
            "max": int(cfg.get("max_safety_orders", 5) or 5)}


def _dca_snapshot(b, st):'''

CTL = '''    if action in ("lx_set", "lx_layer", "lx_now"):              # ⚡ v3.36.56: DCA+ — الخروج بالطبقات من الكرت (حقول الحالة فقط — المحرك يرسل)
        if b["cfg"].get("bot_type") != "dca" or not b["cfg"].get("dca_plus"):
            return {"ok": False, "msg": "الخروج بالطبقات لبوتات DCA+ فقط"}
        sp, _, _ = paths_of(b)
        stt = load_json(sp) or {}
        v = value if isinstance(value, dict) else {}
        upd = {}
        def _ints(xs):
            out = []
            for x in xs or []:
                try:
                    out.append(int(x))
                except Exception:
                    pass
            return out
        if action == "lx_set":
            try:
                if "pct" in v:
                    p_ = float(v["pct"])
                    if not (p_ == p_) or p_ < 0.3 or p_ > 10:
                        return {"ok": False, "msg": "ارتداد الخروج بالطبقات بين 0.3% و10% (أقل من 0.3% لا يغطي العمولة)"}
                    upd["lx_pct"] = round(p_, 4)
                if "from" in v:
                    f_ = int(float(v["from"]))
                    mx = int(b["cfg"].get("max_safety_orders", 5) or 5)
                    if f_ < 1 or f_ > mx:
                        return {"ok": False, "msg": f"الخروج بالطبقات يبدأ من أمر أمان بين 1 و{mx}"}
                    upd["lx_from"] = f_
            except Exception:
                return {"ok": False, "msg": "تأكد من أرقام الخروج بالطبقات"}
            if "on" in v:
                upd["lx_on"] = bool(v["on"])
            if "reopen" in v:
                upd["lx_reopen"] = bool(v["reopen"])
            if not upd:
                return {"ok": False, "msg": "لا يوجد تغيير"}
            msg = "⚡ حُفظت إعدادات الخروج بالطبقات — يطبّقها البوت خلال ثوانٍ"
        elif action == "lx_layer":
            try:
                n_ = int(v.get("n"))
            except Exception:
                return {"ok": False, "msg": "طلب غير صالح"}
            off = set(_ints(stt.get("lx_off")))
            if v.get("off"):
                off.add(n_)
            else:
                off.discard(n_)
            upd["lx_off"] = sorted(off)
            msg = (f"⛔ لن يخرج أمر الأمان {n_} وحده — يبقى لهدف الدورة" if v.get("off") else f"⚡ أمر الأمان {n_} يخرج وحده من جديد")
        else:
            try:
                fid = int(v.get("fid"))
            except Exception:
                return {"ok": False, "msg": "طلب غير صالح"}
            if stt.get("phase") != "selling" or not any(isinstance(f, dict) and str(f.get("fid")) == str(fid) for f in stt.get("filled") or []):
                return {"ok": False, "msg": "هذه الطبقة لم تعد مفتوحة"}
            now = _ints(stt.get("lx_now"))
            if fid not in now:
                now.append(fid)
            upd["lx_now"] = now
            msg = "⏏ أُرسل طلب الخروج — يشتري البوت كمية هذه الطبقة الآن بسعر السوق"
        if not save_state_keys(sp, upd):
            stt.update(upd)
            save_json_atomic(sp, stt)
        return {"ok": True, "msg": msg}
    if action in ("trail_on", "trail_off"):
        if b["cfg"].get("bot_type") not in ("dca", "dca_buy"):
            return {"ok": False, "msg": "الدرع لبوتات DCA فقط"}'''

PANEL = r'''/* ⚡ v3.36.56: DCA+ — نافذة الخروج بالطبقات (المالك: «واريد انا اتحكم فيه … وانا اختار الخروج») */
function dcaPlusPanel(b){
  const d=b.dca||{},P=d.plus;if(!P){toast('هذا البوت ليس DCA+',false);return}
  const base=d.base_coin||'',cp=(window.JPX&&JPX[b.symbol])||b.cp||0,sg=v=>(v>=0?'+':'')+v;
  const lb=ns=>ns.length>1?`أمان ${ns[0]}–${ns[ns.length-1]}`:`أمان ${ns[0]}`;
  let h=`<h2>⚡ DCA+ — الخروج بالطبقات · ${b.symbol}</h2>
  <p style="color:var(--mut);font-size:12.5px;line-height:1.9;margin-bottom:10px">كل أمر أمان منفّذ يخرج وحده حين يعود السعر تحت سعر بيعه بالنسبة التي تختارها — ربح صغير بدل انتظار هدف الدورة كاملاً. الأساس والأوامر قبل «يبدأ من» تبقى لهدف الدورة.</p>
  <div class="dnsum">
    <div class="dnstat"><span>⚡ خرجت (كل الدورات)</span><b class="num">${P.n}</b><small style="color:var(--green)">${sg(P.p)} ${base}</small></div>
    <div class="dnstat"><span>⚡ خرجت في هذه الدورة</span><b class="num">${P.cn}</b><small style="color:var(--green)">${sg(P.cp)} ${base}</small></div>
    <div class="dnstat"><span>🎯 هدف الدورة (الباقي)</span><b class="num" style="color:var(--green)">${d.target_price?f4(d.target_price):'—'}</b></div>
  </div>
  <div class="dpxset">
    <label class="ck"><input type="checkbox" id="dpx_on" ${P.on?'checked':''}> ⚡ الخروج بالطبقات يعمل</label>
    <div class="fld"><label>ارتداد الخروج %</label><input id="dpx_pct" class="num" value="${P.pct}"><small>0.3–10 · أقل من 0.3% لا يغطي العمولة</small></div>
    <div class="fld"><label>يبدأ من أمر الأمان</label><input id="dpx_from" class="num" value="${P.from}"><small>1–${P.max} · ما قبله يبقى لهدف الدورة</small></div>
    <label class="ck"><input type="checkbox" id="dpx_re" ${P.reopen?'checked':''}> ↩️ أعِد فتح الطبقة بعد خروجها</label>
    <small class="dpxhint">إعادة الفتح: إذا عاد السعر إلى مستواها تُباع من جديد — ربح أكثر لكن يبقى البوت مفتوحاً أطول. بلا إعادة فتح: يخرج أسرع ويبقى معرّضاً أقل.</small>
    <button class="primary" onclick="dcaPlusSave('${b.dir}')">💾 حفظ الإعدادات</button>
  </div>`;
  const L=P.layers||[];
  h+=`<div class="dnsec">🧩 الطبقات المفتوحة الآن (${L.length})</div>`;
  if(!L.length)h+='<p style="color:var(--mut);font-size:12px">لا طبقة أمان منفّذة الآن — تظهر هنا حين ينفّذ البوت أوامر الأمان.</p>';
  else{h+=`<div style="overflow-x:auto"><table class="dntbl"><thead><tr><th>الطبقة</th><th>بيعت بسعر</th><th>الكمية ${base}</th><th>⚡ تخرج عند</th><th>البعد الآن</th><th>الحالة</th><th></th></tr></thead><tbody>`;
    L.forEach(x=>{const st=x.now?'⏏ تخرج الآن':x.off?'⛔ لا تخرج وحدها':x.small?'صغيرة — لهدف الدورة':x.low?'قبل «يبدأ من» — لهدف الدورة':!P.on?'الخروج متوقف':'⚡ تخرج وحدها';
      const n0=x.ns[0];
      h+=`<tr><td>${lb(x.ns)}</td><td class="num">${f4(x.px)}</td><td class="num">${x.q}</td><td class="num" style="color:var(--green)">${f4(x.ex)}</td>
        <td class="num" style="color:var(--mut)">${x.dist==null?'—':(x.dist>0?'▼ '+x.dist+'%':'✓ وصل')}</td><td style="white-space:nowrap">${st}</td>
        <td style="white-space:nowrap"><button class="dpxb" onclick="dcaPlusLayer('${b.dir}',${n0},${x.off?0:1})">${x.off?'⚡ يخرج وحده':'⛔ أوقف خروجه'}</button>
        <button class="dpxb dz" onclick="dcaPlusNow('${b.dir}',${x.fid})" ${x.now?'disabled':''}>⏏ أخرجها الآن</button></td></tr>`});
    h+='</tbody></table></div>'}
  const G=P.log||[];
  if(G.length){h+=`<div class="dnsec">🧾 آخر الخروجات</div><div style="overflow-x:auto"><table class="dntbl"><thead><tr><th>الوقت</th><th>الطبقة</th><th>بيعت</th><th>اشترى</th><th>الربح ${base}</th></tr></thead><tbody>`;
    G.forEach(e=>{const t=new Date((+e.ts||0)*1000);h+=`<tr><td class="num">${t.toLocaleString('ar-IQ',{hour12:false,month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'})}</td>
      <td>${lb(e.ns||[])}${e.manual?' · يدوي':''}${e.whole===false?' · جزء':''}</td><td class="num">${f4(e.sold)}</td><td class="num">${f4(e.px)}</td>
      <td class="num" style="color:${(+e.profit||0)>=0?'var(--green)':'var(--red)'}">${sg(+(+e.profit||0).toFixed(8))}</td></tr>`});
    h+='</tbody></table></div>'}
  showModal(h)}
function dcaPlusSave(dir){const g=id=>($('#'+id)||{});
  ctl(dir,'lx_set',{on:!!g('dpx_on').checked,pct:g('dpx_pct').value,from:g('dpx_from').value,reopen:!!g('dpx_re').checked});hideModal()}
async function dcaPlusLayer(dir,n,off){hideModal();await ctl(dir,'lx_layer',{n,off:!!off});setTimeout(()=>{const b=botOf(dir);if(b&&$('#mbg').hidden)dcaPlusPanel(b)},900)}
function dcaPlusNow(dir,fid){const b=botOf(dir)||{},d=b.dca||{},P=d.plus||{},x=(P.layers||[]).find(z=>z.fid===fid);if(!x)return;
  const cp=(window.JPX&&JPX[b.symbol])||b.cp||0,base=d.base_coin||'',est=cp>0?(x.net/cp*0.999-x.q):0,sg=v=>(v>=0?'+':'')+v.toFixed(6);
  askConfirm('⏏ أخرج هذه الطبقة الآن؟',`يشتري البوت كمية ${x.ns.length>1?'الأوامر '+x.ns.join('، '):'أمر الأمان '+x.ns[0]} (${x.q} ${base}) بسعر السوق الآن، بدولار بيعها.<br>بيعت بسعر <b>${f4(x.px)}</b> · السعر الآن <b>${f4(cp)}</b> ⇐ النتيجة التقريبية <b style="color:${est>=0?'var(--green)':'var(--red)'}">${sg(est)} ${base}</b>${est<0?' (خسارة — قرارك)':''}.<br>لا تعود هذه الطبقة للمخزون بعد الخروج اليدوي.`,
    ()=>{ctl(dir,'lx_now',{fid});hideModal()})}
'''

TUT = r'''  dca_plus:{t:'DCA+',
    idea:['نسخة من DCA البيعي بإضافة واحدة: الخروج بالطبقات. كل أمر أمان منفّذ يخرج وحده حين يعود السعر تحت سعر بيعه بنسبة صغيرة تختارها (0.5% مثلاً) — يعيد شراء كميته بدولارها بربح صغير، بدل انتظار هدف الدورة كاملاً.',
          'الغاية: الخروج من الأوامر بسرعة على حساب ربح أقل، حتى آخر أمر. الأساس والأوامر قبل «يبدأ من» تبقى لهدف الدورة العادي.'],
    steps:[['كالبيعي','بيع أولي ثم أوامر أمان فوقه تتسع ويكبر حجمها.'],['الطبقة','كل أمر أمان يُنفَّذ أصبح طبقة لها سعر خروج: سعر بيعها ناقص النسبة.'],
           ['الخروج','عاد السعر إلى سعر خروج طبقة ⇐ يشتري كميتها بدولارها بأمر فوري سقفه نقطة التعادل (لا خسارة) ⇐ ربح صغير بالعملة يُسجَّل فوراً.'],
           ['الباقي','المتوسط والهدف يُحسبان من جديد على ما بقي · وإعادة الفتح (اختيارية) تعيد الطبقة للمخزون لتُباع إذا عاد السعر إلى مستواها.']],
    ex:['باع البوت أمان 5 بسعر 110.74 (50 عملة). الخروج بالطبقات 0.5% ⇐ سعر خروجها 110.19.',
        'نزل السعر إلى 110.19 ⇐ اشترى البوت الخمسين عملة بدولارها ⇐ ربح نحو 0.15 عملة بعد العمولتين، وخرجت أكبر طبقة. في DCA العادي كان عليه انتظار نزول 4.37% ليخرج.'],
    btns:['dca_plus','dca_close','dca_trail','dca_last','hist','table','lddr','chart','dca_pause','cset','del'],
    faq:[['متى أختار DCA+؟','حين تريد ألا تبقى عالقاً بكل الأوامر بعد صعود سريع: أكبر الطبقات تخرج عند أول رجوع صغير للسعر.'],
         ['هل يربح أكثر من DCA العادي؟','قِسناه على أسعار حقيقية لسبع عملات في آخر ثلاثة أشهر: مع إعادة الفتح ربح أكثر من DCA العادي، وبلا إعادة فتح ربح أقل لكن زمن البقاء عالقاً بنصف السلم أو أكثر أقل بكثير (نحو 60%). القرار لك من نافذة ⚡.'],
         ['هل يخرج بخسارة؟','الخروج التلقائي لا: سقف أمره نقطة التعادل للطبقة. أما «⏏ أخرجها الآن» فقرارك — يشتري بسعر السوق ولو كان بخسارة، ويُسجَّل خسارة.'],
         ['ماذا تعني «⛔ أوقف خروجه»؟','تبقى هذه الطبقة لهدف الدورة كما في DCA العادي، والباقي يخرج وحده.']]},
'''

R = [
    ('''def _dca_snapshot(b, st):''', VIEW),
    ('''    _ts, _tt = st.get("trail_s") or {}, st.get("trail_t") or {}
''', '''    _ts, _tt = st.get("trail_s") or {}, st.get("trail_t") or {}
    plus = _safe(_dcap_view, cfg, st, cp, default=None) if cfg.get("dca_plus") else None    # ⚡ v3.36.56: DCA+
'''),
    ('''        "is_buy": is_buy,
        "cycles": int(st.get("cycles_done") or 0),''', '''        "is_buy": is_buy, "plus": plus,
        "cycles": int(st.get("cycles_done") or 0),'''),
    ('''    if action in ("trail_on", "trail_off"):
        if b["cfg"].get("bot_type") not in ("dca", "dca_buy"):
            return {"ok": False, "msg": "الدرع لبوتات DCA فقط"}''', CTL),
    ('''        elif kind in ("dca", "dca_buy"):
            b["dca_type"] = kind''', '''        elif kind in ("dca", "dca_buy"):
            b["dca_type"] = kind
            if str(body.get("dca_type") or "") == "dca_plus":   # ⚡ v3.36.56: DCA+ من النموذج
                b["dca_plus"] = "1"'''),
    # ── 🧪 a demo DCA+ from the form («dca_type: dca_plus»): the sell DCA's kind — the body keeps dca_plus (the trial's _bt_dry_cfg above)
    ('''    if getattr(sys, "frozen", False):
        return {"ok": False, "msg": "الديمو يحتاج نسخة بايثون من اللوحة"}
    if kind not in _BT_KINDS:''', '''    if getattr(sys, "frozen", False):
        return {"ok": False, "msg": "الديمو يحتاج نسخة بايثون من اللوحة"}
    if kind == "dca_plus":                                   # ⚡ v3.36.56: DCA+ = البيعي + dca_plus
        kind = "dca"
    if kind not in _BT_KINDS:'''),
    ('''    _lbl = (_BOT_KINDS.get(kind) or {}).get("ico", "") + " " + (_BOT_KINDS.get(kind) or {}).get("lbl", kind)
    return {"ok": ok, "dir": folder, "msg": (f"🧪 انطلق بوت ديمو ({_lbl.strip()})''',
     '''    _lbl = (_BOT_KINDS.get(kind) or {}).get("ico", "") + " " + (_BOT_KINDS.get(kind) or {}).get("lbl", kind)
    if cfg.get("dca_plus"):
        _lbl = "⚡ DCA+ بيعي"
    return {"ok": ok, "dir": folder, "msg": (f"🧪 انطلق بوت ديمو ({_lbl.strip()})'''),
    # ── the card
    ('''    <span class="dcatag">${b.bot_type==='dca_buy'?'📈 DCA شرائي':'📉 DCA بيعي'}</span>''',
     '''    <span class="dcatag">${b.bot_type==='dca_buy'?'📈 DCA شرائي':(b.dca&&b.dca.plus?'⚡ DCA+ بيعي':'📉 DCA بيعي')}</span>'''),
    ('''    <div class="dcaopts x3"><button class="dcashield" data-k="dtrail">🛡️ الدرع —</button>''',
     '''    <button class="dcaplusb" data-k="dplus" style="display:${b.dca&&b.dca.plus?'':'none'}">⚡ الخروج بالطبقات</button>
    <div class="dcaopts x3"><button class="dcashield" data-k="dtrail">🛡️ الدرع —</button>'''),
    ('''  R.dtrail.onclick=()=>dcaShield(botOf(b.dir)||b);''', '''  R.dtrail.onclick=()=>dcaShield(botOf(b.dir)||b);
  R.dplus.onclick=()=>dcaPlusPanel(botOf(b.dir)||b);      // ⚡ v3.36.56: DCA+'''),
    ('''  R.dpause.textContent=d.paused?'▶️ استئناف':'⏸ إيقاف';
}
function dcaViz(el,d,cp){''', '''  R.dpause.textContent=d.paused?'▶️ استئناف':'⏸ إيقاف';
  if(R.dplus){const P=d.plus;R.dplus.style.display=P?'':'none';      // ⚡ v3.36.56: DCA+
    if(P){R.dplus.className='dcaplusb'+(P.on?' on':'');
      R.dplus.textContent=P.on?`⚡ الخروج بالطبقات ✓ ${P.pct}%${P.cn?` · خرجت ${P.cn} في هذه الدورة`:''}`:'⚡ الخروج بالطبقات: متوقف';
      R.dplus.title='اضغط للتحكم: النسبة · من أي أمر · إعادة الفتح · كل طبقة وحدها · أخرجها الآن';
      const t=el.querySelector('.dcatag');if(t&&!/DCA\\+/.test(t.textContent))t.textContent='⚡ DCA+ بيعي';
      if(P.cn&&R.status)R.status.textContent+=` · ⚡ ${P.cn} طبقة خرجت`}}
}
function dcaViz(el,d,cp){'''),
    # ── the card's drawing (the same one as the DCA): each filled layer's exit line
    ('''  const key=JSON.stringify([rows.map(r=>[r.n,r.st,r.px]),d.avg_price,d.target_price,cp,d.trail_on&&d.trail_peak,d.is_buy]);''',
     '''  const LX=(d.plus&&d.plus.layers)||[];      // ⚡ v3.36.56: DCA+ — خط خروج كل طبقة منفّذة
  const key=JSON.stringify([rows.map(r=>[r.n,r.st,r.px]),d.avg_price,d.target_price,cp,d.trail_on&&d.trail_peak,d.is_buy,LX.map(x=>[x.fid,x.ex,x.elig,x.off]),d.plus&&d.plus.on]);'''),
    ('''  const nL=rows.length+3+(pk>0?1:0),W=320''', '''  const nL=rows.length+3+(pk>0?1:0)+LX.length,W=320'''),
    ('''  const ps=rows.map(r=>+r.px).concat([avg,tgt,cp,pk].filter(x=>x>0));''',
     '''  const ps=rows.map(r=>+r.px).concat([avg,tgt,cp,pk].filter(x=>x>0)).concat(LX.map(x=>+x.ex).filter(x=>x>0));'''),
    ('''  const yc=y(cp);g+=`<line x1="${X0-4}"''', '''  LX.forEach(x=>{const yx=y(+x.ex),cl=x.elig?'var(--green)':'var(--mut2)';
    g+=`<line x1="${X0+14}" y1="${yx}" x2="${X1-14}" y2="${yx}" stroke="${cl}" stroke-width="1.3" stroke-dasharray="3 3" opacity="${x.elig?0.95:0.55}"/>`;
    L.push({y:yx,l:f4(x.ex),r:'⚡ '+(x.ns.length>1?'أمان '+x.ns[0]+'–'+x.ns[x.ns.length-1]:'أمان '+x.ns[0])+(x.off?' ⛔':''),c:cl})});
  const yc=y(cp);g+=`<line x1="${X0-4}"'''),
    ('''<span style="color:var(--amber)">┅ المتوسط</span></div>`;''',
     '''<span style="color:var(--amber)">┅ المتوسط</span>${d.plus?'<span style="color:var(--green)">┄ ⚡ خروج الطبقة</span>':''}</div>`;'''),
    # ── 📋 the table
    ('''<th>الأمر</th><th>السعر</th><th>الكمية ${base}</th><th>الحالة</th><th>بعده عن السعر</th><th>المتوسط<br><small>لو نفّذ</small></th><th>🎯 الخروج<br><small>لو نفّذ</small></th><th>💎 ربح صافي<br><small>لو خرج</small></th></tr></thead><tbody>`;''',
     '''<th>الأمر</th><th>السعر</th><th>الكمية ${base}</th><th>الحالة</th><th>بعده عن السعر</th><th>المتوسط<br><small>لو نفّذ</small></th><th>🎯 الخروج<br><small>لو نفّذ</small></th><th>💎 ربح صافي<br><small>لو خرج</small></th>${d.plus?`<th>⚡ خروج الطبقة<br><small>رجوع ${d.plus.pct}%</small></th>`:''}</tr></thead><tbody>`;'''),
    ('''      <td class="num" style="color:${r.prof>=0?'var(--green)':'var(--red)'}">${sg(r.prof)}</td></tr>`});''',
     '''      <td class="num" style="color:${r.prof>=0?'var(--green)':'var(--red)'}">${sg(r.prof)}</td>${d.plus?dcaPlusCell(d.plus,r):''}</tr>`});'''),
    ('''function cfb(el,b){if(el.dataset.alt)''', r'''function dcaPlusCell(P,r){      // ⚡ v3.36.56: خانة «خروج الطبقة» لصف من جدول الدورة
  if(r.n===0)return '<td style="color:var(--mut2)">هدف الدورة</td>';
  const x=(P.layers||[]).find(z=>z.ns.includes(r.n));
  if(x)return `<td class="num" style="color:${x.elig?'var(--green)':'var(--mut)'};white-space:nowrap">${f4(x.ex)}${x.off?' ⛔':x.low?' <small>لهدف الدورة</small>':x.small?' <small>صغيرة</small>':''}</td>`;
  if(r.n<P.from)return '<td style="color:var(--mut2)">هدف الدورة</td>';
  return `<td class="num" style="color:var(--mut)">${f4(r.px*(1-P.pct/100))}<small> إن نُفّذ</small></td>`}
function cfb(el,b){if(el.dataset.alt)'''),
    ('''function dcaLast(b){''', PANEL + '''function dcaLast(b){'''),
    # ── the skins (C · B · OKX): the same button and state
    ('''    M.chips=[skText(el,'dtrail'),skText(el,'dlast')].filter(Boolean).map((t,i)=>`<span class="chip ${(i===0&&d.trail_on)||(i===1&&d.stop_after)?'gOn':''}">${SKE(t)}</span>`).join('');''',
     '''    M.chips=[skText(el,'dtrail'),skText(el,'dlast')].filter(Boolean).map((t,i)=>`<span class="chip ${(i===0&&d.trail_on)||(i===1&&d.stop_after)?'gOn':''}">${SKE(t)}</span>`).join('')
      +(d.plus?`<span class="chip ${d.plus.on?'gOn':''}" data-sk="dplus" style="cursor:pointer">${SKE(skText(el,'dplus'))}</span>`:'');'''),
    ('''    M.menu=[ME('🪜 السلم','dladder'),ME(null,'dtrail'),ME(null,'dlast'),''',
     '''    M.menu=[ME('🪜 السلم','dladder'),d.plus?ME('⚡ الخروج بالطبقات','dplus'):null,ME(null,'dtrail'),ME(null,'dlast'),'''),
    # ── the deploy form
    ('''    <option value="dca_buy">📈 شرائي — يشتري عند النزول، يجمّع الدولار (الربح بالدولار)</option>''',
     '''    <option value="dca_buy">📈 شرائي — يشتري عند النزول، يجمّع الدولار (الربح بالدولار)</option>
    <option value="dca_plus">⚡ DCA+ بيعي — مثل البيعي، وكل أمر أمان يخرج وحده بسرعة</option>'''),
    ('''  <button class="primary" onclick="dcaPreview()" style="width:100%;margin-top:14px;background:linear-gradient(94deg,var(--cyan),var(--vio))">🔍 احسب الجدول والمخطط</button>''',
     '''  <div id="dn_lx_box" style="display:none;margin-top:10px;padding:10px 12px;border:1px solid rgb(var(--green-rgb)/.35);border-radius:10px;background:rgb(var(--green-rgb)/.06)">
    <div class="frm">
      <div class="fld"><label>⚡ ارتداد الخروج %</label><input id="dn_lx_pct" class="num" value="0.5" oninput="dcaPreview()"><small style="color:var(--mut2);font-size:10px">0.3–10 · كم يعود السعر تحت سعر بيع الطبقة لتخرج</small></div>
      <div class="fld"><label>يبدأ من أمر الأمان</label><input id="dn_lx_from" class="num" value="1" oninput="dcaPreview()"><small style="color:var(--mut2);font-size:10px">ما قبله يبقى لهدف الدورة</small></div>
    </div>
    <label class="ck" style="margin-top:8px"><input type="checkbox" id="dn_lx_re"> ↩️ أعِد فتح الطبقة بعد خروجها</label>
    <p style="color:var(--mut);font-size:11.5px;line-height:1.8;margin-top:6px">كل أمر أمان منفّذ يخرج وحده بربح صغير حين يعود السعر تحت سعر بيعه بهذه النسبة (لا خسارة). بلا إعادة فتح يخرج البوت أسرع ويبقى معرّضاً أقل؛ مع إعادة الفتح يربح أكثر ويبقى مفتوحاً أطول. تتحكم بكل شيء لاحقاً من زر ⚡ في البطاقة.</p>
  </div>
  <button class="primary" onclick="dcaPreview()" style="width:100%;margin-top:14px;background:linear-gradient(94deg,var(--cyan),var(--vio))">🔍 احسب الجدول والمخطط</button>'''),
    ('''  const t=$('#dn_type').value;
  const buy=t==='dca_buy';''', '''  const t=$('#dn_type').value;
  const buy=t==='dca_buy';
  {const lb=$('#dn_lx_box');if(lb)lb.style.display=t==='dca_plus'?'':'none'}      // ⚡ v3.36.56: DCA+'''),
    ('''    dca_type:$('#dn_type').value,''', '''    dca_type:$('#dn_type').value,
    ...($('#dn_type').value==='dca_plus'?{dca_plus:'1',lx_pct:($('#dn_lx_pct')||{}).value,lx_from:($('#dn_lx_from')||{}).value,lx_reopen:!!($('#dn_lx_re')||{}).checked}:{}),'''),
    ('''<th>${buy?'الصعود':'الرجوع'} للخروج</th><th>💎 ربح صافي<br><small>${unit}</small></th></tr></thead><tbody>`;''',
     '''<th>${buy?'الصعود':'الرجوع'} للخروج</th><th>💎 ربح صافي<br><small>${unit}</small></th>${body.dca_plus?`<th>⚡ خروج الطبقة<br><small>رجوع ${+body.lx_pct||0}%</small></th>`:''}</tr></thead><tbody>`;'''),
    ('''    <td class="num" style="color:${ep?'var(--green)':'var(--red)'}">${sg(r.exit_profit)}</td></tr>`});''',
     '''    <td class="num" style="color:${ep?'var(--green)':'var(--red)'}">${sg(r.exit_profit)}</td>${body.dca_plus?(r.n>=(+body.lx_from||1)?`<td class="num" style="color:var(--green)">${f4(r.price*(1-(+body.lx_pct||0)/100))}</td>`:'<td style="color:var(--mut2)">هدف الدورة</td>'):''}</tr>`});'''),
    # ── 🧪 the trial path from the form: DCA+ is a sell DCA with dca_plus
    ('''  const k=kind==='rec'?(body.rec_type||'rec_buy'):kind==='dca'?(body.dca_type||'dca'):''',
     '''  const k=kind==='rec'?(body.rec_type||'rec_buy'):kind==='dca'?(body.dca_type==='dca_buy'?'dca_buy':'dca'):'''),
    # ── 📖 the tutorial
    ('''  rec_buy:{t:'الشراء الدوري',''', TUT + '''  rec_buy:{t:'الشراء الدوري','''),
    ('''const TUT_SETS={grid:['grid','grid_range','grid_plus'],dca:['dca','dca_buy'],''', '''const TUT_SETS={grid:['grid','grid_range','grid_plus'],dca:['dca','dca_buy','dca_plus'],'''),
    ('''  const IC={grid:'♾️',grid_plus:'➕',grid_range:'🎚️',grid_step:'🪜',dca_buy:'📈',dca:'📉',''', '''  const IC={grid:'♾️',grid_plus:'➕',grid_range:'🎚️',grid_step:'🪜',dca_buy:'📈',dca:'📉',dca_plus:'⚡','''),
    ('''  dca_last:['🏁 آخر دورة ويخرج',''', '''  dca_plus:['⚡ الخروج بالطبقات','DCA+ فقط: نافذة التحكم — تشغيل وإيقاف الخروج بالطبقات · نسبة الارتداد · من أي أمر أمان يبدأ · إعادة الفتح · كل طبقة مفتوحة بسعر خروجها، مع «⛔ أوقف خروجه» و«⏏ أخرجها الآن».'],
  dca_last:['🏁 آخر دورة ويخرج','''),
    # ── the look
    ('''.dcaopts.x3{grid-template-columns:1fr 1fr auto}''', '''.dcaopts.x3{grid-template-columns:1fr 1fr auto}
.dcaplusb{width:100%;padding:9px 10px;margin-bottom:6px;border-radius:10px;font-size:12.5px;border:1px solid var(--line);background:rgb(var(--ov-rgb)/.03);color:var(--mut);text-align:center}
.dcaplusb.on{border-color:rgb(var(--green-rgb)/.5);background:rgb(var(--green-rgb)/.10);color:var(--green)}
.dpxset{display:grid;gap:8px;margin:12px 0;padding:10px 12px;border:1px solid rgb(var(--green-rgb)/.3);border-radius:10px;background:rgb(var(--green-rgb)/.05)}
.dpxset .fld small,.dpxhint{color:var(--mut2);font-size:10.5px;line-height:1.7}
.dpxb{padding:5px 8px;border-radius:8px;font-size:11.5px;margin:1px}
.dpxb.dz{color:var(--red);border-color:rgb(var(--red-rgb)/.4)}'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    s = s.replace('APP_VERSION = "3.36.55"', 'APP_VERSION = "3.36.56"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · DCA+ on the card (drawing · table · ⚡ window · skins) · deploy form · trial · tutorial · compiles · {p}")
