# 🪙 patch 113 (dashboard v3.36.67 · the signals' coins are the owner's). The owner (20-11, with a screenshot of 🎯 ⚙️): «اختيار العملات كان
#   موجود ، في الجديد انت محدد العملات ، انا اريد انا احدد العملات».
#   · 🎯 ⚙️ «🪙 عملات إشعاراتك»: your coins first, each with ✕ (tap ⇒ removed) · «➕ أضف» ANY coin by name (like the ticker: BTC · DOGE · PEPE ⇒
#     -USDT added) · «↩️ مثل الشريط» to follow the ticker again · the other coins the system measures are folded below («اضغط لتضيفها») with a
#     line saying why they are there (more history = a truer record; no notifications from them unless you add them)
#   · a coin you add is measured too: its history is fetched in the background right away (a round starts) · a coin the exchange does not
#     have ⇒ ⚠️ on its chip and a line · a coin with a short history ⇒ ⏳ (its signals come once it has ~50 days of 4-hour candles)
#   python3 devtests/step/patches/p113_signal_coins.py Holy_Dashboard.pyw
import os, sys

R = [
    # server: adding/removing coins starts a round (history of a new coin now · not at the next close)
    ("""    save_app_cfg(c)
    p = sg_cfg()
    return {"ok": True, "msg": ("🎯 إشعارات الإشارات مفعّلة — " + f"{p['thr']}% فأكثر · {_sg_ar(p['min'], 'time')} فأكثر · " + SG_CH[p["ch"]]) if p["on"]
            else "🔕 إشعارات الإشارات متوقفة", "cfg": p, "est": sg_estimate(p)}""",
     """    old = sg_coins()
    save_app_cfg(c)
    p = sg_cfg()
    new = [s for s in sg_coins(p) if s not in old]
    if new and not _SG["busy"]:
        threading.Thread(target=_safe, args=(sg_tick,), daemon=True).start()     # 🪙 v3.36.67: تاريخ العملة الجديدة يُجلب الآن بالخلفية
    msg = (("🎯 إشعارات الإشارات مفعّلة — " + f"{p['thr']}% فأكثر · {_sg_ar(p['min'], 'time')} فأكثر · " + SG_CH[p["ch"]]) if p["on"]
           else "🔕 إشعارات الإشارات متوقفة")
    if new:
        msg = "🪙 أُضيفت " + " · ".join(s.split("-")[0] for s in new) + " — تُجلب بياناتها بالخلفية وتظهر إشاراتها بعد إغلاق الشمعة القادمة"
    return {"ok": True, "msg": msg, "cfg": p, "est": sg_estimate(p)}"""),
    # server: which of your coins the exchange lacks · which have a short history
    ("""         "on": indic_cfg()["on"] or cfg["on"], "log": (st.get("log") or [])[:60]}""",
     """         "on": indic_cfg()["on"] or cfg["on"], "log": (st.get("log") or [])[:60]}
    _ci = _safe(_sg_cidx, default=None) or {"c4": {}, "c": {}}
    v["bad"] = [s for s in v["mine"] if s in (st.get("bad") or [])]                          # 🪙 v3.36.67: المنصة لا تعرفها
    v["short"] = [s for s in v["mine"] if s not in v["bad"] and s in _ci["c4"] and (_ci["c4"].get(s, 0) < 300 or _ci["c"].get(s, 0) < 220)]"""),
    # page: the coins section
    ("""    <div class="sg-set"><div class="sg-sh">🪙 العملات <small>(${mine.length})</small> ${c.coins?`<button onclick="sgSet({coins:null})">↩️ مثل الشريط</button>`:'<small>· مثل الشريط (📊)</small>'}</div>
      <div class="sg-flt">${(V.uni||[]).map(s=>`<button class="${mine.includes(s)?'on':''}" onclick="sgCoinTog('${gEsc(s)}')">${gEsc(s.split('-')[0])}</button>`).join('')}</div></div>""",
     """    <div class="sg-set" id="sg_coins"><div class="sg-sh">🪙 عملات إشعاراتك <small>(${mine.length})</small> ${c.coins?`<button onclick="sgSet({coins:null})">↩️ مثل الشريط</button>`:'<small>· الآن نفس عملات الشريط (📊) — أي تغيير هنا للإشارات فقط</small>'}</div>
      <div class="sg-flt">${mine.map(s=>`<button class="on sg-cn" data-c="${gEsc(s)}" onclick="sgCoinTog('${gEsc(s)}')" title="اضغط لتشيلها من إشعاراتك">${gEsc(s.split('-')[0])}${(V.bad||[]).includes(s)?' ⚠️':(V.short||[]).includes(s)?' ⏳':''} <b>✕</b></button>`).join('')||'<span class="ind-sub">لا توجد عملات — أضف عملة تحت</span>'}</div>
      <div class="sg-add"><input id="sg_cadd" placeholder="أضف عملة — مثل BTC أو DOGE أو PEPE" autocomplete="off" onkeydown="if(event.key==='Enter')sgCoinAdd()"><button onclick="sgCoinAdd()">➕ أضف</button></div>
      ${(V.bad||[]).length?`<div class="ind-sub" style="color:var(--amber)">⚠️ لم تُعثر على بيانات من المنصة لـ ${(V.bad||[]).map(s=>gEsc(s.split('-')[0])).join(' · ')} — تأكد من الاسم</div>`:''}
      ${(V.short||[]).length?`<div class="ind-sub">⏳ تاريخ قصير: ${(V.short||[]).map(s=>gEsc(s.split('-')[0])).join(' · ')} — تظهر إشاراتها حين يصبح لها نحو 50 يوماً من الشموع</div>`:''}
      ${(()=>{const oth=(V.uni||[]).filter(s=>!mine.includes(s));return oth.length?`<details class="sg-more"><summary>عملات يقيسها النظام لبناء السجل (${oth.length}) — اضغط عملة لتضيفها لإشعاراتك</summary>
        <div class="sg-flt">${oth.map(s=>`<button data-c="${gEsc(s)}" onclick="sgCoinTog('${gEsc(s)}')">${gEsc(s.split('-')[0])} ➕</button>`).join('')}</div>
        <div class="ind-sub">تُفحص هذه العملات لتقوية السجل فقط (تاريخ أكثر = نسبة أصدق)، ولا تصلك إشعاراتها إلا إذا أضفتها.</div></details>`:''})()}</div>"""),
    ("""function sgCoinTog(s){""", """function sgCoinAdd(){const el=$('#sg_cadd');if(!el||!SGV)return;let v=(el.value||'').trim().toUpperCase().replace(/[\\/\\s]/g,'');if(!v)return;   // 🪙 v3.36.67
  if(!v.includes('-'))v+='-USDT';
  if(!/^[A-Z0-9]{1,15}-[A-Z0-9]{2,8}$/.test(v)){toast('اكتب اسم العملة فقط — مثل BTC أو PEPE',false);return}
  const cur=(SGV.cfg.coins||SGV.tick||[]).slice();if(cur.includes(v)){toast('موجودة في إشعاراتك',true);return}
  if(cur.length>=40){toast('الحد 40 عملة',false);return}
  cur.push(v);el.value='';sgSet({coins:cur})}
function sgCoinTog(s){"""),
    # css
    (""".sg-go{display:block;""", """.sg-add{display:flex;gap:6px;margin:6px 0}.sg-add input{flex:1;min-width:0;font-size:12.5px;padding:7px 10px;border-radius:10px;border:1px solid var(--line2);background:var(--bg1);color:var(--tx)}
.sg-add button{font-size:12px;padding:6px 14px;border-radius:10px}.sg-cn b{font-size:10px;opacity:.7;margin-inline-start:2px}
.sg-go{display:block;"""),
    # version
    ("""APP_VERSION = "3.36.66\"""", """APP_VERSION = "3.36.67\""""),
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
    print(f"✅ {len(R)} replacements · 🪙 the signals' coins are yours (add any · remove · like the ticker) · compiles · {p}")
