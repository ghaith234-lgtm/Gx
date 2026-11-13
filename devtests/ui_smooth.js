// 🎬 v3.36.35 in a real browser (run through ui_smooth.py — every card kind in a closed folder): the window motions without hitches —
//   the owner (13-11): «بعض الانميشن يقطع افحصهم كلهم» · on a phone screen with the CPU slowed ×4 (a mid phone)
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
async function open(br, vw, vh, anim, errs, mobile) {
  const ctx = await br.newContext({ viewport: { width: vw, height: vh }, isMobile: !!mobile, hasTouch: !!mobile, deviceScaleFactor: mobile ? 2 : 1 });
  await ctx.addInitScript(a => { try { localStorage.setItem('dash_stick', 'off'); if (a) localStorage.setItem('dash_anim', a); else localStorage.removeItem('dash_anim') } catch (e) {} }, anim);
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9 && typeof HW !== 'undefined', null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(1500);
  return { ctx, pg };
}
const STYLES = ['up', 'zoom', 'side', 'btn', 'blur', 'spring'];
(async () => {
  const br = await chromium.launch();
  const errs = [];
  // ── ① every motion waits for the window's first frame, then plays whole · ④ the scrim is not animated
  const st = [];
  for (const a of STYLES) {
    const { ctx, pg } = await open(br, 412, 900, a === 'zoom' ? null : a, errs, true);
    await pg.mouse.click(300, 120);
    const r = await pg.evaluate(async () => {
      openSettings(); const m = document.getElementById('modal'), A = m.getAnimations()[0];
      const at0 = A ? { ps: A.playState, ct: Math.round(A.currentTime || 0), keys: Object.keys(A.effect.getKeyframes()[0] || {}).filter(z => !/^(offset|easing|composite|computedOffset)$/.test(z)).join('+'),
        kf: JSON.stringify(A.effect.getKeyframes()), fill: A.effect.getTiming().fill, origin: m.style.transformOrigin } : null;
      const scrim = document.getElementById('mbg').getAnimations().length;
      await new Promise(r => setTimeout(r, 260));
      const at1 = A ? A.playState : null;
      await new Promise(r => setTimeout(r, 700));
      return { at0, at1, scrim, end: A ? A.playState : null, origin: m.style.transformOrigin, busy: HW.busy > 0 };
    });
    st.push({ a, ...r });
    await ctx.close();
  }
  const bad1 = st.filter(s => !s.at0 || s.at0.ps !== 'paused' || s.at0.ct !== 0 || !['running', 'finished'].includes(s.at1) || s.end !== 'finished' || s.scrim !== 0);
  ok(`🎬 the ${st.length} motions wait at their first pose until the window is drawn, then play whole (none jumps over its start) · the scrim is not animated`, !bad1.length, bad1.length ? bad1 : st.map(s => s.a));
  const btn = st.find(s => s.a === 'btn'), blur = st.find(s => s.a === 'blur');
  ok(`🎬 «تتوسّع من الزر» grows from the tapped point by scale (${btn.at0 && btn.at0.keys}, from ${btn.at0 && btn.at0.origin}) — not a clip redrawn every frame · the point is cleared after`,
    btn.at0 && btn.at0.keys === 'opacity+transform' && !/clip/i.test(btn.at0.kf) && /scale\(0?\.06\)/.test(btn.at0.kf) && /px \d+px$/.test(btn.at0.origin) && !btn.origin, btn);
  ok('🎬 «تلاشٍ مع ضبابية» lighter: blur 6 px (was 14)', blur.at0 && /blur\(6px\)/.test(blur.at0.kf) && !/14px/.test(blur.at0.kf), blur.at0);
  // ── ③⑤ the blur: none behind what covers the whole phone · the closing copy carries none · the computer keeps it
  let { ctx, pg } = await open(br, 412, 900, null, errs, true);
  const ph = await pg.evaluate(async () => {
    openSettings(); await new Promise(r => setTimeout(r, 500)); const full = getComputedStyle(document.getElementById('mbg')).backdropFilter;
    hideModal(); const c = document.querySelector('.hwclone'); const cb = c ? c.style.backdropFilter : 'no copy';
    await new Promise(r => setTimeout(r, 900)); const gone = !document.querySelector('.hwclone');
    openReports(); await new Promise(r => setTimeout(r, 400)); const page = getComputedStyle(document.getElementById('page_reports')).backdropFilter; closePage('reports');
    await new Promise(r => setTimeout(r, 500));
    askConfirm('🧪', 'x', () => {}); await new Promise(r => setTimeout(r, 400)); const small = getComputedStyle(document.getElementById('mbg')).backdropFilter; hideModal();
    return { full, cb, gone, page, small };
  });
  ok(`📱 a phone: no background blur behind a full window or a page (nothing of it shows) · the closing copy without it · a small confirmation keeps it («${ph.small}»)`,
    ph.full === 'none' && ph.page === 'none' && ph.cb === 'none' && ph.gone && ph.small !== 'none', ph);
  // ⑥ the background's motion pauses behind the trial window too
  const cv = await pg.evaluate(async () => { const a = document.documentElement.classList.contains('covered');
    btOpen({ dir: DATA.bots.find(b => b.bot_type === 'grid').dir }); await new Promise(r => setTimeout(r, 600)); const b = document.documentElement.classList.contains('covered');
    btClose(); await new Promise(r => setTimeout(r, 600)); return { a, b, c: document.documentElement.classList.contains('covered') } });
  ok('⏸️ the background\'s ambient motion pauses behind the trial window (and comes back)', !cv.a && cv.b && !cv.c, cv);
  // ⑦ the refresh from the server waits for a running motion
  const rf = await pg.evaluate(async () => { await new Promise(r => setTimeout(r, 300)); const d0 = DATA;
    openSettings(); tick(); await new Promise(r => setTimeout(r, 150)); const mid = DATA === d0;
    await new Promise(r => setTimeout(r, 900)); const after = DATA !== d0; hideModal(); return { mid, after } });
  ok('⏳ the refresh from the server (every 3 s) draws the cards after a running motion, not in its middle', rf.mid && rf.after, rf);
  const fr = await pg.evaluate(async () => { await new Promise(r => setTimeout(r, 1200)); const d0 = DATA; const t = performance.now(); await tick(); return { ms: Math.round(performance.now() - t), changed: DATA !== d0 } });
  ok(`⏳ with no motion running it does not wait (${fr.ms} ms)`, fr.changed && fr.ms < 400, fr);
  await ctx.close();
  ({ ctx, pg } = await open(br, 1440, 900, null, errs));
  const pc = await pg.evaluate(async () => { openSettings(); await new Promise(r => setTimeout(r, 400)); const f = getComputedStyle(document.getElementById('mbg')).backdropFilter; hideModal(); return f });
  ok(`🖥️ a computer: the frosted background behind the big window stays («${pc}»)`, pc && pc !== 'none', pc);
  await ctx.close();
  // ── v3.36.36: ⚙️ 🩺 «فحص سلاسة الحركة» measures on the device itself (display only)
  ({ ctx, pg } = await open(br, 412, 900, null, errs, true));
  const mc = await pg.evaluate(async () => { const row = [...document.querySelectorAll('#modal .sln')].length; openSettings(); stTog('anim');
    const has = !!document.querySelector('#modal .sln[onclick="motionCheck()"]'); hideModal(); await new Promise(r => setTimeout(r, 400));
    await motionCheck(); await new Promise(r => setTimeout(r, 300));
    const m = document.getElementById('modal'), rows = [...m.querySelectorAll('.mtab tr')].slice(1).map(tr => [...tr.children].map(td => td.textContent.trim()));
    return { has, open: !document.getElementById('mbg').hidden, title: (m.querySelector('h2') || {}).textContent, rows, head: (m.querySelector('.hwb p') || {}).textContent || '',
      reports: document.getElementById('page_reports').classList.contains('on'), st: HW.st.map(x => x.k).join() } });
  ok(`🎬 ⚙️ 🩺 «فحص سلاسة الحركة»: opens and closes ⚙️ · a confirmation · 📊 with the motion and shows ${mc.rows.length} rows (wait · longest gap · stutters · verdict) + the device`,
    mc.has && mc.open && /سلاسة الحركة/.test(mc.title) && mc.rows.length === 6 && mc.rows.every(r => r.length === 6 && /ms$/.test(r[2]) && /(سلسة|مقبولة|تقطّع)/.test(r[5]))
      && /Hz/.test(mc.head) && /أنوية/.test(mc.head) && !mc.reports && mc.st === 'modal', mc);
  await pg.evaluate(() => hideModal());
  const ml = await pg.evaluate(async () => { localStorage.setItem('dash_lite', 'on'); document.documentElement.classList.add('lite'); await motionCheck(); await new Promise(r => setTimeout(r, 200));
    return { open: !document.getElementById('mbg').hidden, toast: (document.querySelector('#toast,.toast') || {}).textContent || '' } });
  ok('🎬 with «⚡ الوضع الخفيف» it measures nothing and says why', !ml.open && /الخفيف/.test(ml.toast), ml);
  await ctx.close();
  // ── the hitches, measured: frames over 34 ms while ⚙️ opens and closes, every motion, CPU ×4
  const jk = [];
  for (const a of STYLES) {
    ({ ctx, pg } = await open(br, 412, 900, a === 'zoom' ? null : a, errs, true));
    const cdp = await ctx.newCDPSession(pg); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
    for (const ph of ['open', 'close']) {
      const r = await pg.evaluate(async ph => {
        if (ph === 'close') { openSettings(); await new Promise(r => setTimeout(r, 1000)) }
        const t0 = performance.now(); if (ph === 'open') openSettings(); else hideModal();
        const A = ph === 'open' ? document.getElementById('modal').getAnimations()[0]
          : document.getAnimations().find(x => x.effect && x.effect.target && x.effect.target.closest && x.effect.target.closest('.hwclone') && x.effect.target.matches('.modal'));
        const rec = [];
        await new Promise(res => { (function f(t) { if (A) rec.push([t, A.playState]); if (A && A.playState !== 'finished' && performance.now() - t0 < 2500) requestAnimationFrame(f); else res() })(performance.now()) });
        const run = rec.filter(x => x[1] === 'running' || x[1] === 'finished'), g = run.slice(1).map((x, i) => x[0] - run[i][0]);
        if (ph === 'open') hideModal(); await new Promise(r => setTimeout(r, 700));
        return { n: g.length, over: g.filter(x => x > 34).length, max: Math.round(Math.max(0, ...g)) };
      }, ph);
      jk.push({ a, ph, ...r });
    }
    await ctx.close();
  }
  const over = jk.reduce((s, x) => s + x.over, 0), worst = Math.max(...jk.map(x => x.max));
  ok(`📉 ⚙️ opened and closed with all ${STYLES.length} motions at CPU ×4: ${over} frames over 34 ms in all (v3.36.34: ~40) · the longest gap ${worst} ms`,
    jk.every(x => x.n >= 5) && over <= 20 && worst <= 150, jk);   // ≤ half of v3.36.34 — the count wobbles a few frames run to run
  ok('no page errors', !errs.length, errs);
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_smooth: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('crash', e); process.exit(1) });
