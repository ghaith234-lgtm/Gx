# 📈 patch 34 (dashboard · the trial path — the engines are not touched) — the owner (8-11): «ضعه داخل المسار التجريبي ، ولكل البوتات مع الهادئ
#   ، عادي والعنيف واضف الحقيقي ، زيد خيارات المدة ثلاث اشهر و6 … ومن اين اتجيب بيانات الاصلية وهل يقرا الجارتات بالمليم حتى يعطيني ارباح حقيقية».
#   ① a 4th market «📈 حقيقي»: OKX's own candles for the chosen period (public market data · no keys) — a week on 1-minute candles, a month
#      on 5-minute, 3 months on 15-minute, 6 months on 30-minute, a year on 1-hour · each candle walked open → low/high → close (a level
#      touched inside the candle fills) · path 1 = the last period, path 2 = the one before it … · the dashboard fetches them (the sealed
#      worker has no network) into Holy_Backtest/candles (the next test reuses them), with its progress on the screen.
#   ② every bot kind (the same box): the bot deployed at the window's first price (its settings as written — its absolute prices: base,
#      floor, range, the periodic bot's lo/hi — moved by the same ratio to that price · the coins' dollar value as written) · the price does NOT come back ⇒ the result shows the real profit at the end price · what holding the wallet would have
#      made · the bot against holding — next to the usual «what the bot made at the start price» and «buy & sell profit».
#   ③ two more periods for every market: 3 months · 6 months (~8,700 price points each, like the others).
#   python3 devtests/step/patches/p34_bt_real.py Holy_Dashboard.pyw
import os, sys

PY = '''# ═══════════ 📈 v3.36.29: الأسعار الحقيقية (شموع OKX العامة · تجيبها اللوحة قبل العامل — العامل بلا شبكة) ═══════════
_BT_BAR = {"week": ("1m", 60), "month": ("5m", 300), "q3": ("15m", 900), "h6": ("30m", 1800), "year": ("1H", 3600)}
BT_CANDLES = os.path.join(BT_DIR, "candles")
_BT_FETCH = {}


def _bt_hist(sym, bar, sec, t0, t1, stop_fp=None, on_page=None):
    """📈 شموع OKX الحقيقية المسكّرة بين t0 و t1 (الأقدم أول) — من التخزين المحلي أولاً، والناقص صفحة صفحة للخلف"""
    os.makedirs(BT_CANDLES, exist_ok=True)
    fp = os.path.join(BT_CANDLES, re.sub(r"[^A-Z0-9-]", "", sym.upper()) + f"_{bar}.json")
    have = {}
    try:
        for r_ in (load_json(fp) or {}).get("r") or []:
            have[int(r_[0])] = r_
    except Exception:
        have = {}
    cur, got_new = t1, False
    while cur > t0:
        if stop_fp and os.path.exists(stop_fp):
            break
        lo = max(t0, cur - 100 * sec)
        if all(t in have for t in range(lo // sec * sec if lo % sec == 0 else (lo // sec + 1) * sec, cur, sec)):
            cur = lo
            continue
        pg = [c for c in _fc_okx_rows(sym, bar, after=cur * 1000, hist=True, limit=100) if c[6] and c[0] < cur]
        if on_page:
            on_page()
        if not pg:
            break
        for c in pg:
            have[int(c[0])] = [int(c[0]), c[1], c[2], c[3], c[4]]
        got_new = True
        cur = min(int(c[0]) for c in pg)
        time.sleep(0.11)                                  # حد OKX العام
    if got_new:
        try:
            keep = sorted(have)[-300000:]
            save_json_atomic(fp, {"r": [have[t] for t in keep]})
        except Exception:
            pass
    return [have[t] for t in sorted(have) if t0 <= t < t1]


def _bt_ohlc(W):
    """🕯️ كل شمعة ⇒ 4 نقاط: الفتح ← الأدنى ← الأعلى ← الإغلاق (الصاعدة) أو الفتح ← الأعلى ← الأدنى ← الإغلاق (الهابطة)"""
    out = []
    for o, h, l, c in zip(W.get("o") or [], W.get("h") or [], W.get("l") or [], W.get("c") or []):
        out.extend((o, l, h, c) if c >= o else (o, h, l, c))
    return [float(x) for x in out]


def _bt_spawn(jd, w):
    procs = []
    flags = (0x08000000 | 0x00004000) if os.name == "nt" else 0          # بلا نافذة · أولوية أقل من العادية (ويندوز)
    for k in range(w):
        lf = open(os.path.join(jd, f"w{k}.log"), "w", encoding="utf-8")
        procs.append(subprocess.Popen([PYTHON_EXE, "-u", os.path.abspath(__file__), "--holy-bt", jd, str(k), str(w)], cwd=jd,
                                      stdout=lf, stderr=lf, creationflags=flags, env={**os.environ, "PYTHONIOENCODING": "utf-8"}))
    return procs


def _bt_real_prep(jid, jd, w):
    """📈 بالخلفية: لكل مسار فترته من الماضي (1 = الأخيرة · 2 = التي قبلها …) ⇒ px_n.json ⇒ ثم العمّال"""
    job = load_json(os.path.join(jd, "job.json")) or {}
    sym, per, n = job["sym"], job["period"], int(job.get("paths") or 1)
    bar, sec = _BT_BAR[per]
    days = _BT_PER[per][0]
    t_end = int(time.time()) // sec * sec
    stop_fp = os.path.join(jd, "stop.flag")
    got = 0
    F = _BT_FETCH.setdefault(jid, {"done": 0, "total": n, "pg": 0})
    try:
        for k in range(n):
            if os.path.exists(stop_fp):
                break
            t1 = t_end - k * days * 86400
            t0 = t1 - days * 86400

            def _pg():
                F["pg"] = int(F.get("pg") or 0) + 1
            rows = _bt_hist(sym, bar, sec, t0, t1, stop_fp, _pg)
            if len(rows) < 0.9 * (t1 - t0) / sec:
                break                                     # العملة أحدث من الفترة (أو المنصة ما عندها) ⇒ نكتفي بما قبلها
            save_json_atomic(os.path.join(jd, f"px_{k}.json"), {"t0": t0, "t1": t1, "sec": sec, "bar": bar,
                                                                "o": [r_[1] for r_ in rows], "h": [r_[2] for r_ in rows],
                                                                "l": [r_[3] for r_ in rows], "c": [r_[4] for r_ in rows]})
            got += 1
            F["done"] = got
        if os.path.exists(stop_fp):
            return
        if not got:
            save_json_atomic(os.path.join(jd, "err_f.json"), {"msg": "ما وصلت أسعار حقيقية كافية لهذه المدة — العملة أحدث من الفترة أو تعذّر الاتصال بالمنصة"})
            return
        if got < n:
            job["paths"] = got
            job["note"] = f"تاريخ العملة الحقيقي يكفي {got} من {n} مسار"
            save_json_atomic(os.path.join(jd, "job.json"), job)
        procs = _bt_spawn(jd, min(w, got))
        with _BT_LK:
            _BT_JOBS[jid] = {"procs": procs, "t": time.time(), "dir": jd}
    except Exception as e:
        save_json_atomic(os.path.join(jd, "err_f.json"), {"msg": f"تعذّر جلب الأسعار الحقيقية: {type(e).__name__}: {e}"})
    finally:
        with _BT_LK:
            j = _BT_JOBS.get(jid)
            if j and j.get("fetch"):
                j["fetch"] = False


'''

CHILD_NEW = '''    cfg = job.get("cfg")
    real = bool(job.get("real"))                          # 📈 v3.36.29: أسعار OKX الحقيقية (الشموع جابتها اللوحة قبل العامل — العامل بلا شبكة)
    if cfg is None and not real:
        cfg, err = _bt_dry_cfg(kind, job.get("body") or {}, sym, spec, p0)
        if cfg is None:
            save_json_atomic(os.path.join(jd, f"err_{k}.json"), {"msg": err})
            return 2
    if k == 0 and not real:
        save_json_atomic(os.path.join(jd, "cfg.json"), {kk: v for kk, v in cfg.items() if kk not in ("api_key", "secret_key", "passphrase", "bot_id")})
    days, dt = _BT_PER[job["period"]]
    for n in range(k, int(job["paths"]), w):
        if stop.is_set():
            break
        seed = int(job["seed"]) + n
        q_n, b_n, p_n, cfg_n, W_ = float(job["quote"]), float(job["base"]), p0, cfg, None
        if real:
            W_ = load_json(os.path.join(jd, f"px_{n}.json")) or {}
            px = _bt_ohlc(W_)
            if len(px) < 8:
                save_json_atomic(os.path.join(jd, f"err_{k}.json"), {"msg": "أسعار الفترة الحقيقية ناقصة"})
                return 2
            dt = float(W_["sec"]) / 4.0
            p_n, seed = px[0], n
            if job.get("cfg") is not None:                # كأنك نشرته ببداية الفترة: حدود السعر المطلقة تنتقل بنفس نسبتها إلى سعر أول الفترة
                cfg_n = dict(job["cfg"])
                ref = float(cfg_n.get("forced_base_price") or 0) or p0
                for kk in ("forced_base_price", "min_price", "lower_price", "upper_price", "lo", "hi"):
                    if float(cfg_n.get(kk) or 0) > 0 and ref > 0:
                        cfg_n[kk] = float(cfg_n[kk]) * p_n / ref
            else:
                body_n = dict(job.get("body") or {})
                for kk in ("forced_base", "min_price", "lower_price", "upper_price", "lo", "hi"):
                    try:
                        if float(body_n.get(kk) or 0) > 0 and p0 > 0:
                            body_n[kk] = repr(float(body_n[kk]) * p_n / p0)
                    except Exception:
                        pass
                cfg_n, err = _bt_dry_cfg(kind, body_n, sym, spec, p_n)
                if cfg_n is None:
                    save_json_atomic(os.path.join(jd, f"err_{k}.json"), {"msg": err})
                    return 2
            if n == 0:
                save_json_atomic(os.path.join(jd, "cfg.json"), {kk: v for kk, v in cfg_n.items() if kk not in ("api_key", "secret_key", "passphrase", "bot_id")})
            if p0 > 0 and p_n > 0:
                b_n = b_n * p0 / p_n                              # نفس قيمة العملات بالدولار ببداية الفترة
        else:
            px = _bt_path(p0, days, dt, float(job["vol"]), seed)
'''

R = [
    ('''        if os.path.exists(os.path.join(jd, "stop.flag")):
            return True
        n = int((load_json(os.path.join(jd, "job.json")) or {}).get("paths") or 0)''',
     '''        if os.path.exists(os.path.join(jd, "stop.flag")) or os.path.exists(os.path.join(jd, "err_f.json")):   # 📈 جلب الأسعار فشل ⇒ لا عمّال بعده
            return True
        n = int((load_json(os.path.join(jd, "job.json")) or {}).get("paths") or 0)'''),
    ('''            if d not in _BT_JOBS or not any(p.poll() is None for p in _BT_JOBS[d]["procs"]):''',
     '''            if d not in _BT_JOBS or not (any(p.poll() is None for p in _BT_JOBS[d]["procs"]) or _BT_JOBS[d].get("fetch")):'''),
    ('''_BT_MOOD = {"calm": 0.6, "normal": 1.0, "wild": 1.6}
_BT_PER = {"week": (7, 60), "month": (30, 300), "year": (365, 3600)}''',
     '''_BT_MOOD = {"calm": 0.6, "normal": 1.0, "wild": 1.6, "real": 1.0}      # 📈 v3.36.29: «real» = شموع OKX الحقيقية
_BT_PER = {"week": (7, 60), "month": (30, 300), "q3": (91, 900), "h6": (182, 1800), "year": (365, 3600)}   # 📈 + 3 و6 أشهر'''),
    ('''            if any(p.poll() is None for p in j["procs"]) and not _bt_finished(j["dir"]):''',
     '''            if (any(p.poll() is None for p in j["procs"]) or j.get("fetch")) and not _bt_finished(j["dir"]):'''),
    ('''           "vol": _BT_VOL.get(base, _BT_VOL_DEF) * _BT_MOOD[mood], "t": time.time(), "app": APP_VERSION}''',
     '''           "vol": _BT_VOL.get(base, _BT_VOL_DEF) * _BT_MOOD[mood], "t": time.time(), "app": APP_VERSION,
           "real": mood == "real", "bar": _BT_BAR[per][0] if mood == "real" else None}'''),
    ('''    w = min(_bt_workers(), npaths)
    procs = []
    flags = (0x08000000 | 0x00004000) if os.name == "nt" else 0          # بلا نافذة · أولوية أقل من العادية (ويندوز)
    for k in range(w):
        lf = open(os.path.join(jd, f"w{k}.log"), "w", encoding="utf-8")
        procs.append(subprocess.Popen([PYTHON_EXE, "-u", os.path.abspath(__file__), "--holy-bt", jd, str(k), str(w)], cwd=jd,
                                      stdout=lf, stderr=lf, creationflags=flags, env={**os.environ, "PYTHONIOENCODING": "utf-8"}))
    with _BT_LK:
        _BT_JOBS[jid] = {"procs": procs, "t": time.time(), "dir": jd}
    _bt_clean()''',
     '''    w = min(_bt_workers(), npaths)
    if mood == "real":                                    # 📈 v3.36.29: الشموع الحقيقية أولاً (اللوحة · بالخلفية) ثم العمّال
        with _BT_LK:
            _BT_JOBS[jid] = {"procs": [], "t": time.time(), "dir": jd, "fetch": True}
            _BT_FETCH[jid] = {"done": 0, "total": npaths, "pg": 0}
        threading.Thread(target=_safe, args=(_bt_real_prep, jid, jd, w), daemon=True).start()
    else:
        procs = _bt_spawn(jd, w)
        with _BT_LK:
            _BT_JOBS[jid] = {"procs": procs, "t": time.time(), "dir": jd}
    _bt_clean()'''),
    ('''def _bt_finished(jd):''', PY + '''def _bt_finished(jd):'''),
    ('''    alive = bool(j and any(p.poll() is None for p in j["procs"]))''',
     '''    alive = bool(j and any(p.poll() is None for p in j["procs"]))
    fetching = bool(j and j.get("fetch"))                 # 📈 v3.36.29: يجيب الشموع الحقيقية'''),
    ('''    state = "error" if err else ("done" if done else ("stopped" if stopped and not alive else ("run" if alive else "lost")))''',
     '''    state = "error" if err else ("prep" if fetching else ("done" if done else ("stopped" if stopped and not alive else ("run" if alive else "lost"))))'''),
    ('''    cfg_view = load_json(os.path.join(jd, "cfg.json"))''',
     '''    if agg and paths and all((p.get("sum") or {}).get("real") for p in paths):          # 📈 v3.36.29: الحقيقي · المسك · البوت مقابل المسك
        pn, hv, vs = sorted(p["sum"]["pnl"] for p in paths), sorted(p["sum"]["hold"] for p in paths), sorted(p["sum"]["vs"] for p in paths)
        md = lambda a: a[len(a) // 2] if len(a) % 2 else (a[len(a) // 2 - 1] + a[len(a) // 2]) / 2
        agg["real"] = {"pnl_med": md(pn), "pnl_min": pn[0], "pnl_max": pn[-1], "hold_med": md(hv), "vs_med": md(vs), "vs_pos": sum(1 for x in vs if x > 0)}
    cfg_view = load_json(os.path.join(jd, "cfg.json"))'''),
    ('''            "cfg": cfg_view}''',
     '''            "cfg": cfg_view, "fetch": _BT_FETCH.get(job.get("id")) if fetching else None, "note": job.get("note")}'''),
    ('''"paths": sorted(paths, key=lambda p: p["n"]), "agg": agg, "job": {k: job.get(k) for k in ("kind", "sym", "period", "mood", "paths", "seed", "p0", "quote",''',
     '''"paths": sorted(paths, key=lambda p: p["n"]), "agg": agg, "job": {k: job.get(k) for k in ("kind", "sym", "period", "mood", "paths", "seed", "p0", "quote", "real", "bar",'''),
    # ── the worker
    ('''        r = _bt_run(kind, cfg, sym, px, dt, float(job["quote"]), float(job["base"]), spec, job["maker"], job["taker"], job["slip"], stop=stop,
                        prog=_prog)''',
     '''        r = _bt_run(kind, cfg_n, sym, px, dt, q_n, b_n, spec, job["maker"], job["taker"], job["slip"], stop=stop,
                        prog=_prog)'''),
    ('''        s = {"n": n, "seed": seed, "sum": _bt_summary(kind, r, float(job["quote"]), float(job["base"]), p0, dt)}''',
     '''        s = {"n": n, "seed": seed, "sum": _bt_summary(kind, r, q_n, b_n, p_n, dt)}
        if real:                                          # 📈 الربح الحقيقي بسعر النهاية · لو مسكت المحفظة · البوت مقابل المسك
            ex_ = r["ex"]
            pe = float(r["curve"][-1][1]) if r["curve"] else px[-1]
            v0_ = q_n + b_n * p_n
            pnl = ex_.bal[ex_.quote] + ex_.bal[ex_.base] * pe - v0_
            hold = b_n * (pe - p_n)
            s["sum"].update(real=True, p_end=pe, pnl=round(pnl, 8), pnl_pct=round(pnl / v0_ * 100, 4) if v0_ > 0 else 0.0, hold=round(hold, 8),
                            vs=round(pnl - hold, 8), t0=int(W_.get("t0") or 0), t1=int(W_.get("t1") or 0), bar=job.get("bar"))'''),
    # ── the screen
    ('''يتذبذب السعر ثم يعود في النهاية إلى <b>سعر البداية نفسه</b> — فأيّ فرق في المحفظة هو ما صنعه البوت وحده.''',
     '''يتذبذب السعر ثم يعود في النهاية إلى <b>سعر البداية نفسه</b> — فأيّ فرق في المحفظة هو ما صنعه البوت وحده. أو على <b>📈 الأسعار الحقيقية</b> لآخر أسبوع أو شهر أو 3 أو 6 أشهر أو سنة.'''),
    ('''${btSeg('period',[['week','أسبوع'],['month','شهر'],['year','سنة']],'month')}''',
     '''${btSeg('period',[['week','أسبوع'],['month','شهر'],['q3','3 أشهر'],['h6','6 أشهر'],['year','سنة']],'month')}'''),
    ('''${btSeg('mood',[['calm','هادئ'],['normal','عادي'],['wild','عنيف']],'normal')}''',
     '''${btSeg('mood',[['calm','هادئ'],['normal','عادي'],['wild','عنيف'],['real','📈 حقيقي']],'normal')}'''),
    ('''const BT_PER={week:['أسبوع',7,'نقطة سعر كل دقيقة'],month:['شهر',30,'نقطة سعر كل 5 دقائق'],year:['سنة',365,'نقطة سعر كل ساعة']};
const BT_MOOD={calm:'هادئ',normal:'عادي',wild:'عنيف'};''',
     '''const BT_PER={week:['أسبوع',7,'نقطة سعر كل دقيقة','دقيقة'],month:['شهر',30,'نقطة سعر كل 5 دقائق','5 دقائق'],q3:['3 أشهر',91,'نقطة سعر كل 15 دقيقة','15 دقيقة'],
  h6:['6 أشهر',182,'نقطة سعر كل 30 دقيقة','30 دقيقة'],year:['سنة',365,'نقطة سعر كل ساعة','ساعة']};
const BT_MOOD={calm:'هادئ',normal:'عادي',wild:'عنيف',real:'حقيقي'};
function btWin(m){const f=t=>{const d=new Date(t*1000);return d.getUTCDate()+'/'+(d.getUTCMonth()+1)+'/'+String(d.getUTCFullYear()).slice(2)};   // 📈 v3.36.29
  return m&&m.t0?`${f(m.t0)} ← ${f(m.t1-1)}`:''}
function btRealRows(S,B){return `<div class="btendl btri"><span>📈 الربح الحقيقي بسعر النهاية</span><b class="num ${S.pnl>=0?'g':'r'}">${btS(S.pnl)}$ · ${btS(S.pnl_pct)}%</b></div>
   <div class="btendl"><span>🤲 لو مسكت محفظتك بلا بوت</span><b class="num ${S.hold>=0?'g':'r'}">${btS(S.hold)}$</b></div>
   <div class="btendl"><span>⚖️ البوت مقابل المسك</span><b class="num ${S.vs>=0?'g':'r'}">${btS(S.vs)}$</b></div>
   <p class="btopen">أسعار OKX الحقيقية من ${btWin(S)} (شمعة كل ${gEsc((BT_PER[(BT.st&&BT.st.job||{}).period]||[])[3]||'')}) — السعر لا يعود إلى البداية، فالربح الحقيقي = ما صنعه البوت + حركة السوق على ما بقي معك.</p>`}'''),
    ('''  n.innerHTML=`تقلّب ${gEsc(P.base)} اليومي''',
     '''  if(mo==='real'){n.innerHTML=`📈 <b>أسعار OKX الحقيقية</b> لـ${per[0]} (شمعة كل ${per[3]}، تُقرأ كل شمعة بأعلاها وأدناها) · المسار 1 = آخر ${per[0]} والمسار 2 = الذي قبله… · السعر لا يعود إلى البداية: تظهر النتيجة الحقيقية ومقارنتها بمسك المحفظة · البداية = سعر أول الفترة (رقم المسار وسعر البداية هنا لا يُستعملان) · حدود السعر في الإعدادات (الأرضية والنطاق وسعر البداية وحدود الدوري) تنتقل بنفس نسبتها إلى سعر أول الفترة · قيمة العملات بالدولار كما كتبتها`;return}
  n.innerHTML=`تقلّب ${gEsc(P.base)} اليومي'''),
    ('''  const pc=Math.round((s.prog!=null?+s.prog:(s.total?s.done/s.total:0))*100),go=+s.prog>0;''',
     '''  const pc=Math.round((s.fetch?0.05*(s.fetch.done/Math.max(1,s.fetch.total)):(s.prog!=null?+s.prog:(s.total?s.done/s.total:0)))*100),go=+s.prog>0;'''),
    ('''   <span>${s.state==='prep'||(!s.done&&!go)?'⏳ يحضّر المحرك ويشغّل أول مسار…':''',
     '''   <span>${s.fetch?`⏳ يجلب أسعار OKX الحقيقية… ${s.fetch.done} من ${s.fetch.total} ${s.fetch.total>1?'فترات':'فترة'} (${s.fetch.pg||0} صفحة)`:s.state==='prep'||(!s.done&&!go)?'⏳ يحضّر المحرك ويشغّل أول مسار…':'''),
    ('''     <small class="btnote">اضغط عموداً لتشاهد مساره يتحرّك.</small></div>`}''',
     '''     ${A.real?`<div class="bttrd"><span>📈 على الأسعار الحقيقية</span><span>الربح الحقيقي الوسيط <b class="num ${A.real.pnl_med>=0?'g':'r'}">${btS(A.real.pnl_med)}$</b></span><span>لو مسكت المحفظة <b class="num">${btS(A.real.hold_med)}$</b></span><span>البوت مقابل المسك <b class="num ${A.real.vs_med>=0?'g':'r'}">${btS(A.real.vs_med)}$</b> (أفضل في ${A.real.vs_pos} من ${A.n})</span></div>`:''}${s.note?`<small class="btnote">${gEsc(s.note)}</small>`:''}
     <small class="btnote">اضغط عموداً لتشاهد مساره يتحرّك.</small></div>`}'''),
    ('''<th>المسار</th><th>النتيجة</th><th>%</th>''', '''<th>المسار</th><th>النتيجة</th><th>%</th>${s.paths.some(p=>p.sum.real)?'<th>📈 الحقيقي · المسك</th>':''}'''),
    ('''<td class="num">${p.n+1} <small>#${p.seed}</small></td><td class="num ${m.result>=0?'g':'r'}">${btS(m.result)}$</td><td class="num">${btS(m.pct)}%</td>''',
     '''<td class="num">${p.n+1} <small>${m.real?btWin(m):'#'+p.seed}</small></td><td class="num ${m.result>=0?'g':'r'}">${btS(m.result)}$</td><td class="num">${btS(m.pct)}%</td>${s.paths.some(p=>p.sum.real)?`<td class="num ${(+m.pnl||0)>=0?'g':'r'}">${m.real?btS(m.pnl)+'$ · '+btS(m.hold)+'$':'—'}</td>`:''}'''),
    ('''<b>🎞️ المسار ${s.n+1}</b> <small class="num">#${s.seed}</small>''', '''<b>🎞️ المسار ${s.n+1}</b> <small class="num">${S.real?btWin(S):'#'+s.seed}</small>'''),
    ('''<h3>🏁 نهاية ${per[0]} — السعر عاد إلى <span class="num">${btP(S.p0)}</span></h3>''',
     '''<h3>${S.real?`🏁 النهاية — ${per[0]} على الأسعار الحقيقية · السعر من <span class="num">${btP(S.p0)}</span> إلى <span class="num">${btP(S.p_end)}</span>`:`🏁 نهاية ${per[0]} — السعر عاد إلى <span class="num">${btP(S.p0)}</span>`}</h3>${S.real?btRealRows(S,B):''}'''),
    ('''<div><span>الفرق = ما صنعه البوت</span>''', '''<div><span>${S.real?'ما صنعه البوت (بسعر البداية — بلا حركة السوق)':'الفرق = ما صنعه البوت'}</span>'''),
    ('''لهذا قد ينقص الدولار في المحفظة بينما تزيد العملات (قيمتها هنا بسعر البداية = سعر النهاية)</p>''',
     '''لهذا قد ينقص الدولار في المحفظة بينما تزيد العملات (قيمتها هنا بسعر البداية${S.real?'':' = سعر النهاية'})</p>'''),
]

BLOCKS = [
    ('''    cfg = job.get("cfg")
    if cfg is None:
        cfg, err = _bt_dry_cfg(kind, job.get("body") or {}, sym, spec, p0)''',
     '''        _pg = {"t": 0.0}

        def _prog(i, nn, _n=n):''', CHILD_NEW),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for i, (a, z, b) in enumerate(BLOCKS):
        if s.count(a) != 1 or s.count(z) != 1 or s.index(a) > s.index(z):
            print(f"❌ block {i}: anchors {s.count(a)} / {s.count(z)} — nothing written: {a[:70]!r}"); sys.exit(1)
        i0, i1 = s.index(a), s.index(z)
        s = s[:i0] + b + s[i1:]
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · {len(BLOCKS)} blocks · compiles · {p}")
