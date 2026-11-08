# 🧪⏩ patch 27 (dashboard · the trial path box — the engine is not touched) — the owner (7-11/8): «المتدرج عند فحص المسار التجريبي اضع
#   الاعدادات واشغل يضل ينتظر ما يشتغل ما اعرف فيه تأخير ام ما يشتغل افحصه».
#   It ran — slowly, and with nothing on the screen. The box's clock jumps to the next price point only when the engine sleeps ≥ 2 s
#   (♾️ and the others wait on an event ⇒ one look per point: a day in 0.7 s). The 🪜 engine sleeps 1 s every turn (it reads its
#   config and state each second, checks OKX every 3 s) ⇒ the box walked every virtual second: a week = 604,800 turns ≈ 9 minutes,
#   a month ≈ 40 minutes, a year ≈ 7 hours per path — and the progress line said «⏳ يحضّر المحرك ويشغّل أول مسار…» until a whole
#   path ended (0 of 1, no time left shown).
#   ① the box gives the 🪜 engine `settle` = 6 s at its live pace after each new price point (two OKX checks · its whole window of new
#      orders fits one check: MAX_NEW = 8 = W), then jumps to the next point — the price does not move between points, so nothing
#      the engine would decide changes. Measured on the same paths, slow vs fast: the SAME fills, the same wallet to the last digit
#      (a day at the week's 60 s: 56 fills · ×10 · 3 days at the month's 300 s: 161 fills · ×38). Only the 🪜 gets it.
#   ② the worker writes the running path's progress every second (g_n.json) ⇒ bt_status returns `prog` and a time left from it ⇒
#      the bar moves and says «⏳ يعمل المحرك على المسار — 37% · المتبقي ≈ 0:42».
#   python3 devtests/step/patches/p27_bt_step_fast.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''_BT_T0 = 1798761600.0                                                       # تقويم ثابت للصندوق (2027-01-01 UTC)
''',
     '''_BT_T0 = 1798761600.0                                                       # تقويم ثابت للصندوق (2027-01-01 UTC)
_BT_SETTLE = 6.0      # 🪜 v3.36.25: ثواني بالوتيرة الحية بعد كل نقطة سعر للمتدرج (دورتين فحص) — بعدها النقطة التالية (السعر ثابت بينهما)
'''),
    ('''    JUMP = 2.0
''',
     '''    JUMP = 2.0
    settle = 0.0              # 🪜 v3.36.25: محرك يدور كل ثانية (المتدرج) — بعد `settle` ثانية من النقطة نومة الثانية تقفز للتالية
'''),
    ('''            t = self.t + s
            if s >= self.JUMP:
                t = max(t, self._next())''',
     '''            t = self.t + s
            if s >= self.JUMP or (self.settle and s >= 1.0 and t - (self.t0 + self.i * self.dt) >= self.settle):
                t = max(t, self._next())'''),
    ('''def _bt_run(kind, cfg, sym, px, dt, quote, base, spec, maker=0.0008, taker=0.001, slip=0.0005, samples=1200, stop=None):''',
     '''def _bt_run(kind, cfg, sym, px, dt, quote, base, spec, maker=0.0008, taker=0.001, slip=0.0005, samples=1200, stop=None, prog=None):'''),
    ('''        every = max(1, n // max(1, samples))
''',
     '''        every = max(1, n // max(1, samples))
        pev = max(1, n // 400)                            # ⏳ v3.36.25: تقدّم المسار (العامل يكتبه للوحة)
'''),
    ('''        def on_point(i):
            _pop_check(i)
''',
     '''        def on_point(i):
            _pop_check(i)
            if prog is not None and i % pev == 0:
                prog(i, n)
'''),
    ('''        clock.stop = stop
''',
     '''        clock.stop = stop
        if kind == "grid_step":
            clock.settle = _BT_SETTLE                     # 🪜 v3.36.25: نفس التنفيذات بالضبط · أسرع ×10 (أسبوع) ×38 (شهر)
'''),
    ('''        try:
            r = _bt_run(kind, cfg, sym, px, dt, float(job["quote"]), float(job["base"]), spec, job["maker"], job["taker"], job["slip"], stop=stop)''',
     '''        _pg = {"t": 0.0}

        def _prog(i, nn, _n=n):                           # ⏳ v3.36.25: تقدّم المسار الجاري كل ثانية (اللوحة تعرض النسبة والمتبقي)
            if time.time() - _pg["t"] >= 1.0:
                _pg["t"] = time.time()
                try:
                    save_json_atomic(os.path.join(jd, f"g_{_n}.json"), {"i": int(i), "n": int(nn)})
                except Exception:
                    pass
        try:
            r = _bt_run(kind, cfg, sym, px, dt, float(job["quote"]), float(job["base"]), spec, job["maker"], job["taker"], job["slip"], stop=stop,
                        prog=_prog)'''),
    ('''        eta = round(sum(secs) / len(secs) * (int(job.get("paths") or 0) - len(paths)) / max(1, w), 0)
''',
     '''        eta = round(sum(secs) / len(secs) * (int(job.get("paths") or 0) - len(paths)) / max(1, w), 0)
    prog = None
    if state == "run":                                     # ⏳ v3.36.25: المسارات الجارية من ملف تقدّمها (العامل يكتبه كل ثانية)
        tot, part, got = int(job.get("paths") or 0), 0.0, {p.get("n") for p in paths}
        for n in range(tot):
            if n in got:
                continue
            g = load_json(os.path.join(jd, f"g_{n}.json")) or {}
            try:
                part += min(1.0, max(0.0, float(g.get("i") or 0) / max(1.0, float(g.get("n") or 1))))
            except Exception:
                pass
        prog = round((len(paths) + part) / max(1, tot), 4)
        if eta is None and prog >= 0.02:
            eta = round((time.time() - float(job.get("t") or time.time())) * (1 - prog) / prog, 0)
'''),
    ('''    return {"ok": True, "id": job.get("id"), "state": state, "err": err, "done": len(paths), "total": int(job.get("paths") or 0), "eta": eta,''',
     '''    return {"ok": True, "id": job.get("id"), "state": state, "err": err, "done": len(paths), "total": int(job.get("paths") or 0), "eta": eta, "prog": prog,'''),
    ('''  const pc=s.total?Math.round(s.done/s.total*100):0;
  el.innerHTML=`<div class="btprog"><div class="btbar"><i style="width:${Math.max(3,pc)}%"></i></div>
   <span>${s.state==='prep'||!s.done?'⏳ يحضّر المحرك ويشغّل أول مسار…':`✅ ${s.done} من ${s.total} مسار`}''',
     '''  const pc=Math.round((s.prog!=null?+s.prog:(s.total?s.done/s.total:0))*100),go=+s.prog>0;   // ⏳ v3.36.25: داخل المسار أيضاً
  el.innerHTML=`<div class="btprog"><div class="btbar"><i style="width:${Math.max(3,pc)}%"></i></div>
   <span>${s.state==='prep'||(!s.done&&!go)?'⏳ يحضّر المحرك ويشغّل أول مسار…':!s.done?`⏳ يعمل المحرك على ${s.total>1?'المسارات':'المسار'} — <span class="num">${pc}%</span>`:`✅ ${s.done} من ${s.total} مسار · <span class="num">${pc}%</span>`}'''),
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
