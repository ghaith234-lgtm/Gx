// 🌌🃏📊 v3.36.39 in a real browser (run through ui_live.py — every card kind in a closed folder) — the owner (13-11):
//   «عند تحريك كروت البوتات الخلفية متحركه تقف · عندما قللت الفريمات الى ال٦٠ صارت ما اتقطع ·
//    انميشن الكرت اريده وخليه داخل وخلي في امثلة تتحرك حتى واحد يعرف ماذا يختار · كلهم ضيفهم ، لا تضع سرعة الوصول لokx»
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
const wait = ms => new Promise(r => setTimeout(r, ms));
async function open(br, errs, o) {
  o = o || {};
  const ctx = await br.newContext({ viewport: { width: 412, height: 860 }, isMobile: true, hasTouch: true, reducedMotion: o.rm ? 'reduce' : 'no-preference' });
  await ctx.addInitScript(o => { try { localStorage.setItem('dash_stick', 'off'); for (const k in (o.ls || {})) localStorage.setItem(k, o.ls[k]) } catch (e) {}
    if (o.app) {   // the Android app's bridge: status() with the screen · setFps saves like the app does
      const st = { fps: o.app.fps, calls: [] }; window.__app = st;
      const own = { status: () => JSON.stringify({ code: o.app.code, fps: st.fps, hz: st.fps === 60 ? 60 : 120, rates: [60, 90, 120] }), setFps: f => { st.fps = f; st.calls.push(f) } };
      window.HolyApp = new Proxy(own, { get: (t, k) => (k in t ? t[k] : () => ''), has: () => true });
    } }, o);
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9 && typeof HW !== 'undefined', null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(1200);
  return { ctx, pg };
}
// a small fingerprint of what the moving background shows now
const SNAP = `(() => { const c = document.getElementById('hbg'); if (!c || !c.width) return null; const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
  let h = 0; for (let i = 0; i < d.length; i += 4 * 97) h = (h * 31 + d[i] * 3 + d[i + 1] * 5 + d[i + 2] * 7) >>> 0; return h })()`;
(async () => {
  const br = await chromium.launch();
  const errs = [];
  // ── 🌌 the moving background keeps moving while the cards scroll
  let { ctx, pg } = await open(br, errs, { ls: { dash_bg: 'waves', dash_anim: 'none' } });
  const s0 = await pg.evaluate(async snap => { const f = new Function('return ' + snap); const shots = [];
    const t0 = performance.now(); let n = 0;
    while (performance.now() - t0 < 1500) { scrollBy(0, n++ % 2 ? -140 : 160); dispatchEvent(new Event('scroll')); await new Promise(r => setTimeout(r, 120)); shots.push(f()) }
    return { scr: document.documentElement.classList.contains('scrolling'), uniq: new Set(shots).size, n: shots.length, raf: !!HB.raf } }, SNAP);
  ok(`🌌 the moving background keeps moving while the cards scroll (${s0.uniq} different pictures in ${s0.n} looks during the scroll)`, s0.scr && s0.raf && s0.uniq >= Math.floor(s0.n * 0.6), s0);
  const s1 = await pg.evaluate(async snap => { const f = new Function('return ' + snap); const a = f(), w = HB.w;
    // the phone browser's address bar hides while scrolling ⇒ a small height change ⇒ the background must not start over
    const d0 = HB.draw; Object.defineProperty(window, 'innerHeight', { configurable: true, get: () => 860 - 56 }); dispatchEvent(new Event('resize'));
    await new Promise(r => setTimeout(r, 450)); const same = HB.draw === d0;
    Object.defineProperty(window, 'innerWidth', { configurable: true, get: () => 700 }); dispatchEvent(new Event('resize')); await new Promise(r => setTimeout(r, 450));
    const re = HB.draw !== d0 && HB.w === 700; delete window.innerHeight; delete window.innerWidth; return { same, re, a: !!a, w } }, SNAP);
  ok('🌌 the address bar hiding (a small height change) ⇒ the background does not start over · a real resize (width) ⇒ it is drawn again', s1.same && s1.re, s1);
  await ctx.close();
  // ── 🎞️ the app (1.5+): a device that never chose starts at 60 — once · a choice made before stays · the browser stays at 120
  ({ ctx, pg } = await open(br, errs, { app: { code: 12, fps: 120 }, ls: { dash_anim: 'none' } }));
  const f0 = await pg.evaluate(async () => { const a = { calls: window.__app.calls.slice(), ls: localStorage.getItem('dash_fps'), cap: FPSCAP, ui: uiFps() };
    openSettings(); stTog('fps'); await new Promise(r => setTimeout(r, 250));
    a.val = document.querySelector('#modal .sx[data-k="fps"] .sval').textContent; a.note = document.querySelector('#modal .sx[data-k="fps"] .snote').textContent;
    a.on = (document.querySelector('#fpsRow button.on') || {}).textContent; hideModal(); return a });
  ok(`🎞️ the app, never chosen ⇒ 60 (the screen asked once) · ⚙️ «${f0.val}» · «${(f0.note.match(/60[^·]*/) || [''])[0].trim()}»`,
    f0.calls.join() === '60' && f0.ls === '60' && f0.cap === 60 && f0.ui === 60 && /60/.test(f0.val) && f0.on === '60' && /الأسلس/.test(f0.note) && !/هسه|ياكل/.test(f0.note), f0);
  const f1 = await pg.evaluate(async () => { setFps(120); await new Promise(r => setTimeout(r, 100)); hideModal(); fpsFirst(); return { calls: window.__app.calls.slice(), ls: localStorage.getItem('dash_fps') } });
  ok('🎞️ the owner picks 120 afterwards ⇒ it stays 120 (no second switch)', f1.calls.join() === '60,120' && f1.ls === '120', f1);
  await ctx.close();
  ({ ctx, pg } = await open(br, errs, { app: { code: 12, fps: 120 }, ls: { dash_anim: 'none', dash_fps: '120' } }));
  const f2 = await pg.evaluate(() => ({ calls: window.__app.calls.slice(), ui: uiFps() }));
  ok('🎞️ the app, 120 chosen before this version ⇒ it stays 120', !f2.calls.length && f2.ui === 120, f2);
  await ctx.close();
  ({ ctx, pg } = await open(br, errs, { app: { code: 5, fps: 120 }, ls: { dash_anim: 'none' } }));
  const f3 = await pg.evaluate(() => ({ calls: window.__app.calls.slice(), ls: localStorage.getItem('dash_fps') }));
  ok('🎞️ an app older than 1.5 (the screen cannot change) ⇒ nothing changes', !f3.calls.length && f3.ls === null, f3);
  await ctx.close();
  ({ ctx, pg } = await open(br, errs, { ls: { dash_anim: 'none' } }));
  const f4 = await pg.evaluate(() => ({ ui: uiFps(), ls: localStorage.getItem('dash_fps') }));
  ok('🎞️ in a browser ⇒ 120 as before (the screen sets its own rate there)', f4.ui === 120 && f4.ls === null, f4);
  await ctx.close();
  //@@CARDS@@
  //@@MBAR@@
  ok('no page errors', !errs.length, errs);
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_live: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('crash', e); process.exit(1) });
