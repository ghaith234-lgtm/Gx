// 📌🎬📲 v3.36.38 in a real browser (run through ui_device.py — every card kind in a closed folder): the device's own options —
//   the owner (13-11): «خلي هذا الشريط في الاعدادات اختياري · الازرار الي تحت الخاصة بالموبايل غير ظاهرة خليها كذلك اختيارة اظهارها اما لا ·
//   انميشن في برنامج الحاسوب لن يشتغل»
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
async function open(br, errs, o) {
  o = o || {};
  const ctx = await br.newContext({ viewport: { width: 412, height: 860 }, isMobile: true, hasTouch: true, reducedMotion: o.rm ? 'reduce' : 'no-preference' });
  await ctx.addInitScript(o => { try { localStorage.setItem('dash_stick', 'off'); for (const k in (o.ls || {})) localStorage.setItem(k, o.ls[k]) } catch (e) {}
    if (o.app) {   // the Android app's bridge (any method answers '' · 2.1 has setNavBar/navBar · an older app has neither)
      const st = { nav: false, calls: [] }; window.__nav = st;
      const own = o.app === '2.1' ? { setNavBar: v => { st.nav = !!v; st.calls.push(!!v) }, navBar: () => st.nav } : {};
      window.HolyApp = new Proxy(own, { get: (t, k) => (k in t ? t[k] : (o.app !== '2.1' && (k === 'setNavBar' || k === 'navBar') ? undefined : () => '')), has: () => true });
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
const rowsOf = t => `[...[...document.querySelectorAll('#modal .sgrp')].find(g => g.querySelector('.sgt').textContent.includes('${t}')).querySelectorAll('.sgl>.sitem')].map(r => ({ t: (r.querySelector('.stt b') || {}).textContent, id: r.id, sw: r.classList.contains('stg'), on: r.classList.contains('on'), sub: (r.querySelector('.stt small') || {}).textContent }))`;
(async () => {
  const br = await chromium.launch();
  const errs = [];
  // ── 📌 the small top bar
  let { ctx, pg } = await open(br, errs);
  const m0 = await pg.evaluate(async () => { scrollTo(0, 2500); dispatchEvent(new Event('scroll')); await new Promise(r => setTimeout(r, 400)); mbarSync && mbarSync();
    return { shown: getComputedStyle(document.getElementById('mbar')).display !== 'none', on: uiMbar() } });
  await pg.evaluate(() => { localStorage.setItem('dash_anim', 'none'); openSettings() }); await pg.waitForTimeout(250);
  const r0 = await pg.evaluate(new Function('return ' + rowsOf('الشكل')));
  await pg.click('#bMbar'); await pg.waitForTimeout(300);
  const m1 = await pg.evaluate(async () => { hideModal(); await new Promise(r => setTimeout(r, 200)); scrollTo(0, 2600); mbarSync && mbarSync(); await new Promise(r => setTimeout(r, 200));
    return { shown: getComputedStyle(document.getElementById('mbar')).display !== 'none', ls: localStorage.getItem('dash_mbar'), cls: document.documentElement.classList.contains('nombar') } });
  ok(`📌 «الشريط المصغّر»: a switch in ⚙️ 🖌️ (on as before) · off ⇒ it no longer comes down when scrolling`, m0.shown && m0.on && r0.some(r => r.id === 'bMbar' && r.sw && r.on) && !m1.shown && m1.ls === 'off' && m1.cls, { m0, r0: r0.map(r => r.t), m1 });
  await ctx.close();
  ({ ctx, pg } = await open(br, errs, { ls: { dash_mbar: 'off' } }));
  const m2 = await pg.evaluate(async () => { const early = document.documentElement.classList.contains('nombar'); scrollTo(0, 2600); mbarSync && mbarSync(); await new Promise(r => setTimeout(r, 200));
    const hid = getComputedStyle(document.getElementById('mbar')).display === 'none'; uiMbarToggle(); hideModal(); await new Promise(r => setTimeout(r, 200)); mbarSync && mbarSync();
    return { early, hid, back: getComputedStyle(document.getElementById('mbar')).display !== 'none', ls: localStorage.getItem('dash_mbar') } });
  ok('📌 kept on this device (applied before the page is drawn) · on again ⇒ it comes down again', m2.early && m2.hid && m2.back && m2.ls === null, m2);
  await ctx.close();
  // ── 🎬 a device set to «reduce motion» (Windows: «Animation effects» off)
  ({ ctx, pg } = await open(br, errs, { rm: true }));
  const d0 = await pg.evaluate(async () => { const st = hwStyle(); openSettings(); stTog('anim'); await new Promise(r => setTimeout(r, 200));
    const v = document.querySelector('#modal .sx[data-k="anim"] .sval').textContent, warn = (document.querySelector('#modal .sx[data-k="anim"] .sbody .snote') || {}).textContent || '',
      btn = (document.getElementById('motForce') || {}).textContent; return { st, v, warn, btn } });
  ok(`🎬 «تقليل الحركة» on the device: the motion stops and ⚙️ says why («${d0.v}») with «${d0.btn}»`, d0.st === 'none' && /إعداد الجهاز/.test(d0.v) && /تقليل الحركة/.test(d0.warn) && /ويندوز/.test(d0.warn) && /رغم/.test(d0.btn || ''), d0);
  await pg.click('#motForce'); await pg.waitForTimeout(400);
  const d1 = await pg.evaluate(async () => { const st = hwStyle(), ls = localStorage.getItem('dash_motion_force'); hideModal(); await new Promise(r => setTimeout(r, 500));
    openSettings(); const an = document.getElementById('modal').getAnimations().length; await new Promise(r => setTimeout(r, 500)); hideModal(); await new Promise(r => setTimeout(r, 400));
    setBg('waves'); hideModal(); await new Promise(r => setTimeout(r, 300)); const raf = !!HB.raf; setBg('orig'); hideModal(); return { st, ls, an, raf } });
  ok('🎬 «▶️ شغّل الحركة رغم إعداد الجهاز» ⇒ the windows move again (and the moving background) · kept on this device', d1.st === 'zoom' && d1.ls === 'on' && d1.an > 0 && d1.raf, d1);
  const d2 = await pg.evaluate(async () => { setMotionForce(false); hideModal(); await new Promise(r => setTimeout(r, 300)); const st = hwStyle();
    await motionCheck(); await new Promise(r => setTimeout(r, 200)); return { st, toast: (document.getElementById('toast') || {}).textContent || '', ls: localStorage.getItem('dash_motion_force') } });
  ok('🎬 back to the device\'s setting ⇒ no motion · the motion check says why and where to switch it', d2.st === 'none' && d2.ls === null && /تقليل الحركة/.test(d2.toast) && /رغم إعداد الجهاز/.test(d2.toast), d2);
  await ctx.close();
  ({ ctx, pg } = await open(br, errs, { ls: { dash_lite: 'on' } }));
  const d3 = await pg.evaluate(async () => { openSettings(); await new Promise(r => setTimeout(r, 150)); const v = document.querySelector('#modal .sx[data-k="anim"] .sval').textContent; const b = !!document.getElementById('motForce'); hideModal(); return { v, b } });
  ok(`🎬 the light mode on: «${d3.v}» (no device warning when the device allows motion)`, /الوضع الخفيف/.test(d3.v) && !d3.b, d3);
  await ctx.close();
  // ── 📲 the phone's buttons (the app 2.1)
  ({ ctx, pg } = await open(br, errs, { app: '2.1' }));
  await pg.evaluate(() => { localStorage.setItem('dash_anim', 'none'); openSettings() }); await pg.waitForTimeout(250);
  const a0 = await pg.evaluate(new Function('return ' + rowsOf('التطبيقات')));
  await pg.click('#bNav'); await pg.waitForTimeout(500);
  const a1 = await pg.evaluate(() => ({ nav: window.__nav.nav, calls: window.__nav.calls, row: (() => { const r = document.getElementById('bNav'); return r && { on: r.classList.contains('on'), sub: r.querySelector('small').textContent } })() }));
  await pg.click('#bNav'); await pg.waitForTimeout(500);
  const a2 = await pg.evaluate(() => ({ nav: window.__nav.nav, calls: window.__nav.calls }));
  const nb = a0.find(r => r.id === 'bNav');
  ok(`📲 inside the app 2.1: ⚙️ 📱 «أزرار الهاتف» — a switch (hidden as before) · on ⇒ the app shows them («${a1.row && a1.row.sub}») · off ⇒ hidden again`,
    nb && nb.sw && !nb.on && a1.nav === true && a1.row && a1.row.on && a2.nav === false && a2.calls.join() === 'true,false', { a0: a0.map(r => r.t + (r.sw ? '·switch' : '')), a1, a2 });
  await ctx.close();
  ({ ctx, pg } = await open(br, errs, { app: '2.0' }));
  await pg.evaluate(() => { localStorage.setItem('dash_anim', 'none'); openSettings() }); await pg.waitForTimeout(250);
  const o0 = await pg.evaluate(new Function('return ' + rowsOf('التطبيقات')));
  const on0 = o0.find(r => r.id === 'bNav');
  ok(`📲 an older app (2.0): the row says to update («${on0 && on0.sub}»)`, on0 && !on0.sw && /2\.1/.test(on0.sub || ''), o0);
  await ctx.close();
  ({ ctx, pg } = await open(br, errs));
  await pg.evaluate(() => { localStorage.setItem('dash_anim', 'none'); openSettings() }); await pg.waitForTimeout(250);
  const w0 = await pg.evaluate(() => !!document.getElementById('bNav'));
  ok('📲 in a browser (not the app): no «أزرار الهاتف» row', !w0, w0);
  await ctx.close();
  ok('no page errors', !errs.length, errs);
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_device: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('crash', e); process.exit(1) });
