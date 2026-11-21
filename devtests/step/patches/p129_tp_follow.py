# ⏳ patch 129 (dashboard v3.36.74 · the temporary buy pause follows the price). The owner (21-11), a SUI grid bot: «ايقاف الشراء المؤقت
#   ما يتحرك يمشي على اقصى شي افحصه» ⇒ (reproduced with the real engine: 0.72 ⇒ 0.60 ⇒ back to 0.6447 · the store 21 levels and the card's
#   «⏳ مؤقت (21)» · «📦 شراء 21» stayed at the deepest count though 9 of them were already under the price) ⇒ he chose «العدد يلحق السعر».
#   · «⏳ مؤقت (N)» and «📦 شراء N ≈ $» count only the levels ABOVE the price now (the missed ones — bought in one order at the market price
#     when he opens it) — the price rises ⇒ fewer · it falls ⇒ more · the levels under the price «تنتظر بأماكنها» (no orders until he opens
#     it — then they go back to their places on the ladder as usual: the nearest as orders, the rest in memory) — shown beside, not counted
#   · the same in the open window, the «💵 توفر دولار» message and the card's tooltip · the engine is untouched (its own rule: what the price
#     crossed is bought at the market, the rest spreads back) · the floor stays where it closed (unchanged) · the opening is still his
#   python3 devtests/step/patches/p129_tp_follow.py Holy_Dashboard.pyw
import os, sys

R = [
    ('APP_VERSION = "3.36.73"', 'APP_VERSION = "3.36.74"'),
    ("""def _tp_cover(lv, cp, budget):""",
     """def _tp_split(lv, cp):
    \"\"\"⏳ v3.36.74 (المالك: «العدد يلحق السعر»): المحفوظ قسمان — الفايتة فوق السعر الآن (تُشترى بأمر واحد بسعر السوق عند الفتح) ·
    والتي تحت السعر تنتظر بأماكنها (لا أوامر حتى الفتح — ثم تعود إلى السلم كالمعتاد) — نفس قاعدة عدّاد 📦 (السعر ≥ الحالي)\"\"\"
    a = [(p, q) for p, q in lv if p >= cp]
    return a, [(p, q) for p, q in lv if p < cp]


def _tp_cover(lv, cp, budget):"""),
    ("""                        if r.get("n") != len(lv) or r.get("k") != kc:
                            r["n"], r["k"] = len(lv), kc
                            ch = True""",
     """                        na = len(_tp_split(lv, cp)[0])     # ⏳ v3.36.74: العدد يلحق السعر — الفايتة فوقه بس · والباقي ينتظر بمكانه
                        if r.get("n") != na or r.get("k") != kc or r.get("w") != len(lv) - na:
                            r["n"], r["k"], r["w"] = na, kc, len(lv) - na
                            ch = True"""),
    ("""                        need = round(sum(q_ * min(cp * 1.005, p) for p, q_ in lv), 2)
                        rows.append(f"{_cw_lbl(i)}: محفوظ {len(lv)} (≈ {need}$) — يكفي الدولار {kc} منها")""",
     """                        la_, lw_ = _tp_split(lv, cp)
                        need = round(sum(q_ * min(cp * 1.005, p) for p, q_ in la_), 2)
                        rows.append(f"{_cw_lbl(i)}: فايتة فوق السعر {len(la_)} (≈ {need}$)" + (f" · تنتظر تحت السعر بأماكنها {len(lw_)}" if lw_ else "")
                                    + f" — يكفي الدولار {kc} من {len(lv)}")"""),
    ("""                    "own": float(r.get("own") or 0), "n": int(r.get("n") or 0), "k": int(r.get("k") or 0)}""",
     """                    "own": float(r.get("own") or 0), "n": int(r.get("n") or 0), "k": int(r.get("k") or 0), "w": int(r.get("w") or 0)}"""),
    ("""        info = {"ok": True, "n": len(lv), "k": kc, "av": round(av, 2), "cost": round(cost, 2), "first": first, "own": own, "temp": temp,
                "one": _tp_kind(b) != "grid_step"}""",
     """        la, lw = _tp_split(lv, cp)                     # ⏳ v3.36.74: الفايتة فوق السعر · والتي تنتظر تحته
        info = {"ok": True, "n": len(lv), "k": kc, "av": round(av, 2), "cost": round(cost, 2), "first": first, "own": own, "temp": temp,
                "one": _tp_kind(b) != "grid_step", "na": len(la), "nw": len(lw), "ka": min(kc, len(la)), "kw": max(0, kc - len(la))}"""),
    ("""            r["n"], r["k"] = len(lv) - kc, 0""",
     """            r["n"], r["k"], r["w"] = len(_tp_split(lv[kc:], cp)[0]), 0, len(_tp_split(lv[kc:], cp)[1])"""),
    ("""    elif new <= 0:
        msg = (f"🔓 فُتح وقف الشراء المؤقت — تُشترى المستويات المحفوظة كلها ({len(lv)}) من البداية {one}بسعر السوق (≈ {cost:.2f}$) · "
               "ويعود البوت إلى الشراء العادي، ويُغلق المؤقت وحده إذا قصر الدولار")
    else:
        msg = (f"🔓 فُتح وقف الشراء المؤقت لـ {kc} من {len(lv)} — تُشترى من البداية {one}بسعر السوق (≈ {cost:.2f}$) · "
               f"والباقي ({len(lv) - kc}) يبقى محفوظاً والمؤقت مغلقاً تحته من {_px_s(new)}")""",
     """    elif new <= 0:
        msg = (f"🔓 فُتح وقف الشراء المؤقت — الفايتة فوق السعر ({len(la)}) تُشترى من البداية {one}بسعر السوق"
               + (f" · والتي تحت السعر ({len(lw)}) تعود إلى أماكنها في السلم كالمعتاد" if lw else "")
               + f" (≈ {cost:.2f}$) · ويعود البوت إلى الشراء العادي، ويُغلق المؤقت وحده إذا قصر الدولار")
    else:
        msg = (f"🔓 فُتح وقف الشراء المؤقت لـ {kc} من {len(lv)} — تُشترى من البداية: {min(kc, len(la))} فايتة {one}بسعر السوق"
               + (f" و{kc - len(la)} تعود إلى أماكنها تحت السعر" if kc > len(la) else "") + f" (≈ {cost:.2f}$) · "
               f"والباقي ({len(lv) - kc}) يبقى محفوظاً والمؤقت مغلقاً تحته من {_px_s(new)}")"""),
    # the page: the chips follow the price (the live 📦 count — the levels the price crossed)
    ("""  if(CW&&CW.tp)c+=(+CW.k>0?`<span class="chip cashw tpo" onclick="event.stopPropagation();tempOpen('${b.dir}')" style="cursor:pointer;color:var(--green);border-color:rgb(var(--green-rgb)/.5);background:rgb(var(--green-rgb)/.10)"
    title="توفر دولار غير محجوز يكفي ${CW.k} من ${CW.n} محفوظة — اضغط لتفتح وقف الشراء المؤقت (يشتري من البداية بقدر الدولار)">🔓 افتح المؤقت (${+CW.n||0})</span>`
    :`<span class="chip cashw tpc" onclick="event.stopPropagation();tempOpen('${b.dir}')" style="cursor:pointer;color:var(--amber);border-color:rgb(var(--amber2-rgb)/.45);background:rgb(var(--amber2-rgb)/.08)"
    title="وقف الشراء المؤقت من ${f4(CW.temp)} — الدولار الحر غير المحجوز لا يكفي: المستويات تُحفظ ولا تُشترى، ولا يأخذ دولار غيره، ولا يُفتح إلا بقرارك · فوقه يبيع ويشتري كالمعتاد">⏳ مؤقت (${+CW.n||0})</span>`);""",
     """  const tpN=CW&&CW.tp?(AX.nb!=null&&AX.kb!=null?+AX.nb:+CW.n||0):0,tpW=CW&&CW.tp?(AX.kb!=null?Math.max(0,(+AX.kb||0)-(+AX.nb||0)):+CW.w||0):0;   // ⏳ v3.36.74: العدد يلحق السعر
  const tpT=tpW?` · ${tpW} تحت السعر تنتظر بأماكنها (لا أوامر حتى تفتحه — ثم تعود إلى السلم كالمعتاد)`:'';
  if(CW&&CW.tp)c+=(+CW.k>0?`<span class="chip cashw tpo" onclick="event.stopPropagation();tempOpen('${b.dir}')" style="cursor:pointer;color:var(--green);border-color:rgb(var(--green-rgb)/.5);background:rgb(var(--green-rgb)/.10)"
    title="توفر دولار غير محجوز يكفي ${CW.k} من ${tpN+tpW} محفوظة — ${tpN} فايتة فوق السعر تُشترى بأمر واحد بسعر السوق${tpT} · اضغط لتفتح وقف الشراء المؤقت">🔓 افتح المؤقت (${tpN})</span>`
    :`<span class="chip cashw tpc" onclick="event.stopPropagation();tempOpen('${b.dir}')" style="cursor:pointer;color:var(--amber);border-color:rgb(var(--amber2-rgb)/.45);background:rgb(var(--amber2-rgb)/.08)"
    title="وقف الشراء المؤقت من ${f4(CW.temp)} — الدولار الحر غير المحجوز لا يكفي: ${tpN} مستوى فاته السعر محفوظ ولا يُشترى${tpT} · لا يأخذ دولار غيره، ولا يُفتح إلا بقرارك · فوقه يبيع ويشتري كالمعتاد">⏳ مؤقت (${tpN})</span>`);"""),
    ("""  if(b.floor>0){if((AX.nb||0)>0){c+=`<span class="chip acc" title="${AX.nb} تُشترى بأمر واحد إن استأنفت الآن · ${Math.max(0,(AX.kb||0)-AX.nb)} محفوظة تعود إلى أماكنها">📦 شراء ${AX.nb} ≈ $${AX.ub}</span>`;
    if(AX.ab!=null&&AX.ab<AX.nb)c+=""",
     """  if(b.floor>0||(CW&&CW.tp)){if((AX.nb||0)>0){c+=`<span class="chip acc" title="${AX.nb} تُشترى بأمر واحد إن ${b.floor>0?'استأنفت':'فتحت المؤقت'} الآن · ${Math.max(0,(AX.kb||0)-AX.nb)} محفوظة تحت السعر تنتظر بأماكنها">📦 شراء ${AX.nb} ≈ $${AX.ub}</span>`;
    if(b.floor>0&&AX.ab!=null&&AX.ab<AX.nb)c+="""),
    ("""  const all=I.k>=I.n,can=!I.n||I.k>0;""",
     """  const all=I.k>=I.n,can=!I.n||I.k>0,NA=I.na!=null?I.na:I.n,NW=I.nw||0;      // ⏳ v3.36.74: الفايتة فوق السعر · والتي تنتظر تحته"""),
    ("""    :all?`يكفي الكل: تُشترى المستويات المحفوظة (${I.n}) من البداية <b>${I.one?'بأمر واحد ':''}بسعر السوق</b> (≈ ${I.cost}$) ويعود البوت إلى الشراء العادي، ويُغلق المؤقت وحده إذا قصر الدولار.`
    :`يكفي ${I.k} من ${I.n}: تُشترى من البداية <b>${I.one?'بأمر واحد ':''}بسعر السوق</b> (≈ ${I.cost}$)، والباقي (${I.n-I.k}) يبقى محفوظاً والمؤقت مغلقاً تحته.`;""",
     """    :all?`يكفي الكل: الفايتة (${NA}) تُشترى من البداية <b>${I.one?'بأمر واحد ':''}بسعر السوق</b>${NW?` · والتي تحت السعر (${NW}) تعود إلى أماكنها في السلم كالمعتاد`:''} (≈ ${I.cost}$) ويعود البوت إلى الشراء العادي، ويُغلق المؤقت وحده إذا قصر الدولار.`
    :`يكفي ${I.k} من ${I.n}: تُشترى من البداية${I.ka?` ${I.ka} فايتة <b>${I.one?'بأمر واحد ':''}بسعر السوق</b>`:''}${I.kw?` و${I.kw} تعود إلى أماكنها تحت السعر`:''} (≈ ${I.cost}$)، والباقي (${I.n-I.k}) يبقى محفوظاً والمؤقت مغلقاً تحته.`;"""),
    ("""    <p style="color:var(--mut);font-size:13px;line-height:1.9;margin-bottom:10px">مغلق من <b class="num">${f4(I.temp)}</b> · المحفوظ <b>${I.n}</b> مستوى · الدولار""",
     """    <p style="color:var(--mut);font-size:13px;line-height:1.9;margin-bottom:10px">مغلق من <b class="num">${f4(I.temp)}</b> · فاته السعر <b>${NA}</b> مستوى${NW?` · و<b>${NW}</b> تحت السعر تنتظر بأماكنها`:''} · الدولار"""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · ⏳ the temporary pause follows the price · compiles · {p}")
