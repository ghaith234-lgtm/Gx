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
  const ctx = await br.newContext({ viewport: { width: 412, height: o.vh || 860 }, isMobile: true, hasTouch: true, reducedMotion: o.rm ? 'reduce' : 'no-preference' });
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
  // ── 🃏 the cards' motions: ⚙️ 🖌️ «حركات البطاقات» with a sample card that moves · then the real cards
  const REC = `(() => { if (window.__an) return; window.__an = []; const o = Element.prototype.animate;
    Element.prototype.animate = function (k, op) { const c = this.getAttribute && (this.getAttribute('class') || ''); window.__an.push({ c, id: this.id || '', d: (op && op.delay) || 0, t: performance.now() }); return o.call(this, k, op) } })()`;
  const an = (pg, from) => pg.evaluate(f => window.__an.filter(x => x.t >= f), from || 0);
  const now = pg => pg.evaluate(() => performance.now());
  ({ ctx, pg } = await open(br, errs, { ls: { dash_anim: 'none' } }));
  await pg.evaluate(new Function(REC));
  const c0 = await pg.evaluate(async () => { openSettings(); const g = [...document.querySelectorAll('#modal .sgrp')][0];
    const rows = [...g.querySelectorAll('.sgl>.sitem')].map(r => r.dataset.k || r.id); stTog('cfx'); await new Promise(r => setTimeout(r, 900));
    const row = document.querySelector('#modal .sx[data-k="cfx"]');
    return { rows, t: row.querySelector('.stt b').textContent, v: row.querySelector('.sval').textContent, groups: [...row.querySelectorAll('.cfx-g')].map(x => [x.dataset.g, x.querySelectorAll('button[data-ca]').length, (x.querySelector('button.on') || {}).dataset.ca]),
      card: !!document.getElementById('cfxCard'), minis: document.querySelectorAll('#cfxMinis>div').length, defs: Object.keys(HCA).map(g => uiCa(g)).join() } });
  const a0 = await an(pg);
  ok(`🃏 ⚙️ 🖌️ «${c0.t}» right after «حركة فتح النوافذ» («${c0.v}») · a sample card + 3 small cards · 5 groups (${c0.groups.map(x => x[0] + ':' + x[1]).join(' ')}) · it moves the moment it opens`,
    c0.rows.indexOf('cfx') === c0.rows.indexOf('anim') + 1 && c0.card && c0.minis === 3 && c0.groups.map(x => x[1]).join() === '4,3,5,3,4' && c0.defs === 'pop,grow,both,fill,rise'
      && c0.groups.map(x => x[2]).join() === c0.defs && /5 من 5/.test(c0.v) && a0.filter(x => /cfx-bars|^$/.test(x.c) && !x.id).length >= 7, { c0, a0: a0.length });
  // every choice plays on the sample the moment it is tapped (a real tap on the button)
  const tapCa = async (g, k) => { const t = await now(pg); await pg.click(`#modal .cfx-g[data-g="${g}"] button[data-ca="${k}"]`); await pg.waitForTimeout(120);
    return { t, a: await an(pg, t), ls: await pg.evaluate(g => localStorage.getItem('dash_ca_' + g), g), on: await pg.evaluate(g => (document.querySelector(`#modal .cfx-g[data-g="${g}"] button.on`) || {}).dataset.ca, g),
      d: await pg.evaluate(g => document.querySelector(`#modal .cfx-g[data-g="${g}"] .cfx-d`).textContent, g) } };
  const mStag = await tapCa('menu', 'stag');
  const mn = await pg.evaluate(() => ({ menu: !!document.querySelector('#cfxCard .cfx-menu'), n: document.querySelectorAll('#cfxCard .cfx-menu button').length }));
  ok(`🃏 «⋯ القائمة» ⇒ «تكبير + الأزرار بالتتابع»: the sample menu opens and its ${mn.n} buttons come one after another («${mStag.d}») · saved`,
    mn.menu && mStag.a.filter(x => x.c === 'cfx-menu').length === 1 && mStag.a.filter(x => x.c === '' && x.d >= 60).length === 4 && mStag.ls === 'stag' && mStag.on === 'stag', { mStag, mn });
  const v0 = await pg.evaluate(() => +document.getElementById('cfxV').firstChild.nodeValue);
  const nBoth = await tapCa('num', 'both'); await pg.waitForTimeout(150);
  const mid = await pg.evaluate(() => +document.getElementById('cfxV').firstChild.nodeValue); await pg.waitForTimeout(800);
  const v1 = await pg.evaluate(() => document.getElementById('cfxV').firstChild.nodeValue);
  ok(`🃏 «💰 رقم الربح» ⇒ «عدّ + وميض»: the sample number counts ${v0} → ${v1} (passing ${mid}) and flashes green · the default ⇒ nothing stored`,
    mid > v0 && mid < +v1 && v1 === (v0 + 0.0613).toFixed(4) && nBoth.a.some(x => x.id === 'cfxV') && nBoth.ls === null, { v0, mid, v1, nBoth });
  const nPulse = await tapCa('num', 'pulse');
  ok('🃏 «نبضة للبطاقة»: the whole sample card pulses', nPulse.a.some(x => x.id === 'cfxCard') && nPulse.ls === 'pulse', nPulse);
  const bWave = await tapCa('bars', 'wave');
  const bd = bWave.a.filter(x => x.c === '').map(x => x.d);
  ok(`🃏 «📊 أشرطة السلم» ⇒ «امتلاء متتابع»: the 4 bars fill one after another (delays ${bd.join(' · ')})`, bd.length === 4 && bd.join() === '0,70,140,210' && bWave.ls === 'wave', bWave);
  const eZoom = await tapCa('enter', 'zoom');
  ok('🃏 «🃏 ظهور البطاقات» ⇒ «تكبير ناعم»: the 3 small cards come in', eZoom.a.filter(x => x.c === '').length === 3 && eZoom.ls === 'zoom', eZoom);
  const sFade = await tapCa('sec', 'fade');
  const sb = await pg.evaluate(() => !document.querySelector('#cfxCard .cfx-sb').hidden);
  ok('🃏 «⌄ فتح الأقسام» ⇒ «انزلاق مع تلاشٍ»: the sample ladder opens moving', sb && sFade.a.some(x => x.c === 'cfx-sb') && sFade.ls === 'fade', sFade);
  const sNone = await tapCa('sec', 'none');
  ok('🃏 «بلا حركة» ⇒ the sample section just shows (no motion) · the row says how many work', !sNone.a.some(x => x.c === 'cfx-sb') && sNone.ls === 'none'
    && /4 من 5/.test(await pg.evaluate(() => document.querySelector('#modal .sx[data-k="cfx"] .sval').textContent)), sNone);
  const t9 = await now(pg); await pg.click('#cfxAllB'); await pg.waitForTimeout(2200);
  const all = (await an(pg, t9)).map(x => x.c || x.id);
  ok('🃏 «▶️ شغّل الكل» ⇒ everything plays on the sample one after another (the cards · the bars · the number · the menu)', all.includes('cfx-card') && all.includes('cfx-menu') && all.filter(c => c === '').length >= 7, all);
  await pg.evaluate(() => { ['menu', 'sec', 'num', 'bars', 'enter'].forEach(g => localStorage.removeItem('dash_ca_' + g)); hideModal() });
  // ── the real cards (the old look — the default)
  await pg.waitForTimeout(400);
  const r0 = await pg.evaluate(async () => { const b = DATA.bots.find(x => (x.bot_type || 'grid') === 'grid'); const el = CARDS.get(b.dir);
    const t = performance.now(); b.profit = +(+b.profit + 0.25).toFixed(4); syncCards(DATA.bots); await new Promise(r => setTimeout(r, 60));
    const a = window.__an.filter(x => x.t >= t); return { a: a.map(x => x.c), prof: el._r.profit.getAnimations().length } });
  ok('🃏 the old look: a winning trade on a grid card ⇒ its profit flashes green (it already counts)', r0.prof > 0, r0);
  const r1 = await pg.evaluate(async () => { const b = DATA.bots.find(x => (x.bot_type || 'grid') === 'grid'); const el = CARDS.get(b.dir);
    const t = performance.now(); syncCards(DATA.bots); el._caT = 0; await new Promise(r => setTimeout(r, 60)); const same = window.__an.filter(x => x.t >= t).length;
    b.profit = +(+b.profit - 0.1).toFixed(4); syncCards(DATA.bots); await new Promise(r => setTimeout(r, 60)); return { same, down: window.__an.filter(x => x.t >= t).length } });
  ok('🃏 no motion when the number stays the same or goes down', r1.same === 0 && r1.down === 0, r1);
  const r2 = await pg.evaluate(async () => { localStorage.setItem('dash_ca_num', 'pulse'); const b = DATA.bots.find(x => (x.bot_type || 'grid') === 'grid'); const el = CARDS.get(b.dir);
    el._caT = 0; const t = performance.now(); b.profit = +(+b.profit + 0.3).toFixed(4); syncCards(DATA.bots); await new Promise(r => setTimeout(r, 60));
    localStorage.removeItem('dash_ca_num'); return { card: el.getAnimations().length, a: window.__an.filter(x => x.t >= t).map(x => x.c) } });
  ok('🃏 «نبضة للبطاقة» ⇒ the real card pulses', r2.card > 0 && r2.a.some(c => /\bcard\b/.test(c)), r2);
  const r3 = await pg.evaluate(async () => { const b = DATA.bots.find(x => x.bot_type === 'dca' || x.bot_type === 'dca_buy'); if (!b) return { none: 1 }; const el = CARDS.get(b.dir);
    const t = performance.now(); dcaLadderInline(el, b); await new Promise(r => setTimeout(r, 60)); const box = el._r.ladbox;
    const o = { open: box.style.display !== 'none', a: box.getAnimations().length }; dcaLadderInline(el, b); return o });
  ok('🃏 the old look: «🪜 السلم» inside a DCA card opens growing', r3.open && r3.a > 0, r3);
  const r4 = await pg.evaluate(async () => { const t = performance.now(); const b0 = DATA.bots.find(x => (x.bot_type || 'grid') === 'grid');
    const nb = JSON.parse(JSON.stringify(b0)); nb.dir = b0.dir + '_new39'; nb.symbol = 'NEW-USDT'; DATA.bots.push(nb); FILTER.q = ''; syncCards(DATA.bots);
    await new Promise(r => setTimeout(r, 60)); const el = CARDS.get(nb.dir); const a = el ? el.getAnimations().length : -1;
    DATA.bots = DATA.bots.filter(x => x !== nb); syncCards(DATA.bots); return { a } });
  ok('🃏 a new bot\'s card comes in moving («صعود خفيف»)', r4.a > 0, r4);
  // the bars when a card further down shows for the first time
  const r5 = await pg.evaluate(async () => { const els = [...CARDS.values()].filter(e => e.style.display !== 'none' && e.querySelector('.mrow .ln'));
    const far = els.find(e => e.getBoundingClientRect().top > innerHeight + 200); if (!far) return { none: els.length };
    const t = performance.now(); far.scrollIntoView({ block: 'center' }); await new Promise(r => setTimeout(r, 400));
    const a = window.__an.filter(x => x.t >= t && x.c === 'ln').length; await new Promise(r => setTimeout(r, 50)); scrollTo(0, 0); return { a } });
  ok(`🃏 «📊 أشرطة السلم»: a card further down fills its ladder lines the first time it shows (${r5.a})`, r5.a > 0, r5);
  await ctx.close();
  // the entrance when the dashboard opens (under the splash ⇒ it starts as the splash fades)
  ({ ctx, pg } = await open(br, errs, { vh: 1700, ls: { dash_anim: 'none', dash_ca_enter: 'stagger' } }));
  const e0 = await pg.evaluate(() => [...CARDS.values()].map(e => e.getAnimations().filter(a => !(a instanceof CSSAnimation) && !(a instanceof CSSTransition)).map(a => a.effect.getTiming().delay)).filter(x => x.length));
  ok(`🃏 the dashboard opens ⇒ the cards on screen come in one after another (${e0.length} cards · after the splash)`, e0.length >= 2 && e0.length < 9 && e0[0][0] > 300 && e0[1][0] - e0[0][0] === 40, e0);
  await ctx.close();
  // the skins C · B · OKX: the ⋯ menu · a section · the big number
  for (const sk of ['c', 'b', 'o']) {
    ({ ctx, pg } = await open(br, errs, { ls: { dash_anim: 'none', dash_skin: sk } }));
    const k0 = await pg.evaluate(async () => { const b = DATA.bots.find(x => (x.bot_type || 'grid') === 'grid'); const el = CARDS.get(b.dir);
      skAct(el, 'menu'); await new Promise(r => setTimeout(r, 40)); const m = el.querySelector('.sk-menu'); const menu = m ? m.getAnimations().length : -1; skAct(el, 'menu');
      const N = () => el.querySelector('.sk-big .v,.sk-kpi>div:first-child>b,.ok-pnl .v'), big = () => { const n = N(); return n && parseFloat(n.firstChild.nodeValue) }; const p0 = big();
      el._caT = 0; b.profit = +(+b.profit + 0.5).toFixed(4); syncCards(DATA.bots); await new Promise(r => setTimeout(r, 200)); const mid = big();
      const fl = N().getAnimations().length, unit = N().firstChild.nodeValue.replace(/^[\d.,\s-]+/, ''); await new Promise(r => setTimeout(r, 700)); const p1 = big(), unit1 = N().firstChild.nodeValue.replace(/^[\d.,\s-]+/, '');
      const bars = el.querySelectorAll('rect.skb').length;
      const rc = DATA.bots.find(x => x.bot_type === 'rec_buy' || x.bot_type === 'rec_sell'); let sec = 'no rec';
      if (rc) { const re = CARDS.get(rc.dir); const w = re._skxe || 'lots'; skAct(re, 'x:' + w); await new Promise(r => setTimeout(r, 40)); skAct(re, 'x:' + w); await new Promise(r => setTimeout(r, 40));
        const n = re._skx.querySelector('[data-skx].on'); sec = n ? n.getAnimations().length : -1 }
      return { menu, p0, mid, p1, fl, bars, sec, unit, unit1 } });
    ok(`🃏 skin ${sk.toUpperCase()}: ⋯ menu grows from its button · the big number counts ${k0.p0} → ${k0.p1} (passing ${k0.mid}) and flashes · a section opens growing (${k0.sec}) · the ladder bars are marked (${k0.bars})`,
      k0.menu > 0 && k0.mid > k0.p0 && k0.mid < k0.p1 && Math.abs(k0.p1 - k0.p0 - 0.5) < 1e-6 && k0.fl > 0 && k0.sec > 0 && k0.unit === k0.unit1, k0);
    await ctx.close();
  }
  // the light mode · the device's «reduce motion» ⇒ the cards stand still (the sample still plays when tapped)
  for (const [nm, o] of [['⚡ the light mode', { ls: { dash_anim: 'none', dash_lite: 'on' } }], ['📴 «reduce motion» on the device', { rm: true, ls: { dash_anim: 'none' } }]]) {
    ({ ctx, pg } = await open(br, errs, o));
    await pg.evaluate(new Function(REC));
    const l0 = await pg.evaluate(async () => { const b = DATA.bots.find(x => (x.bot_type || 'grid') === 'grid'); const el = CARDS.get(b.dir);
      const t = performance.now(); el._caT = 0; b.profit = +(+b.profit + 0.4).toFixed(4); syncCards(DATA.bots); await new Promise(r => setTimeout(r, 60));
      const cards = window.__an.filter(x => x.t >= t).length; openSettings(); stTog('cfx'); await new Promise(r => setTimeout(r, 200));
      const v = document.querySelector('#modal .sx[data-k="cfx"] .sval').textContent, note = document.querySelector('#modal .sx[data-k="cfx"] .snote').textContent;
      const t2 = performance.now(); cfxRun('num'); await new Promise(r => setTimeout(r, 60)); const sample = window.__an.filter(x => x.t >= t2 && x.id === 'cfxV').length; hideModal();
      return { cards, v, note, sample } });
    ok(`🃏 ${nm}: the cards stand still · ⚙️ says «${l0.v}» · the sample still moves when tapped`, l0.cards === 0 && /متوقفة/.test(l0.v) && /التجربة هنا فقط/.test(l0.note) && l0.sample > 0, l0);
    await ctx.close();
  }
  // ── 📊 the small bar's second line: this device · the bots' computer · the dashboard — every item on/off in ⚙️ · no OKX speed
  const BAT = `navigator.getBattery = () => Promise.resolve({ level: .82, charging: true, chargingTime: 1200, dischargingTime: Infinity, addEventListener() {} })`;
  ({ ctx, pg } = await open(br, errs, { ls: { dash_anim: 'none' } }));
  const sysReq = []; pg.on('request', r => { if (/\/api\/sys\b/.test(r.url())) sysReq.push(Date.now()) });
  await pg.evaluate(new Function(BAT + `;MB.bat = null; navigator.getBattery().then(b => { MB.bat = { level: b.level, charging: b.charging }; MB.batOk = true })`));
  const api0 = await pg.evaluate(async () => { const r = await fetch('/api/sys', { cache: 'no-store' }); return r.json() });
  ok(`🖥️ /api/sys: the bots' computer — CPU ${api0.cpu}% · memory ${api0.ram}% · free disk ${Math.round(api0.disk_free / 1e9)} GB · on for ${Math.round(api0.up / 60)} min`,
    api0.ok && api0.cpu >= 0 && api0.cpu <= 100 && api0.ram > 0 && api0.ram <= 100 && api0.disk_free > 0 && api0.disk_total >= api0.disk_free && api0.up > 0, api0);
  await pg.waitForTimeout(1500);
  const q0 = sysReq.length;
  const b0 = await pg.evaluate(async () => { scrollTo(0, 2600); dispatchEvent(new Event('scroll')); mbarSync(); await new Promise(r => setTimeout(r, 1300));
    return { items: [...document.querySelectorAll('#mStat span')].map(s => [s.dataset.mb, s.textContent]), keys: MBI.map(x => x[0]).join(), shown: getComputedStyle(document.getElementById('mStat')).display } });
  const it = Object.fromEntries(b0.items);
  ok(`📊 scrolled down: the second line shows ${b0.items.length} items — ${b0.items.map(x => x[1]).join(' · ')}`,
    b0.items.length === 11 && b0.keys === 'bat,net,clk,rtt,cpu,ram,dsk,up,bots,live,last' && /^🔋 82%⚡$/.test(it.bat) && /^🕐 \d\d:\d\d$/.test(it.clk) && /^⏱️ \d+ms$/.test(it.rtt)
      && /^🖥️ \d+%$/.test(it.cpu) && /^🧠 \d+%$/.test(it.ram) && /^💽 [\d.]+(GB|TB|MB)$/.test(it.dsk) && /^⏳ /.test(it.up) && /^🟢 \d+\/9$/.test(it.bots) && /^📡 /.test(it.live) && /^🕑 \d+ث$/.test(it.last), b0);
  ok('📊 no OKX speed item (the owner: «لا تضع سرعة الوصول لokx»)', !b0.items.some(x => /okx|ping|بينغ/i.test(x[1])) && !/okx/i.test(b0.keys), b0.keys);
  const w0 = await pg.evaluate(() => { const r = document.getElementById('mbar').getBoundingClientRect(), L = [...document.querySelectorAll('#mStat span')].map(s => s.getBoundingClientRect());
    return { inside: L.every(x => x.left >= -1 && x.right <= innerWidth + 1 && x.height > 0), h: Math.round(r.height), lines: new Set(L.map(x => Math.round(x.top))).size } });
  ok(`📊 on a phone all 11 fit on screen (${w0.lines} short lines under the profits · the bar ${w0.h}px high)`, w0.inside && w0.lines <= 2 && w0.h <= 80, w0);
  const c1 = await pg.evaluate(async () => { const a = document.querySelector('#mStat [data-mb="clk"]').textContent, l1 = document.querySelector('#mStat [data-mb="last"]').textContent;
    await new Promise(r => setTimeout(r, 2100)); return { l1, l2: document.querySelector('#mStat [data-mb="last"]').textContent } });
  ok(`📊 «آخر تحديث» counts by itself every second (${c1.l1} → ${c1.l2}) — the clock too`, c1.l1 !== c1.l2 || /^🕑 [0-2]ث$/.test(c1.l2), c1);
  const q1 = sysReq.length - q0; await pg.waitForTimeout(3000); const q2 = sysReq.length - q0;
  ok(`🖥️ the computer is asked once when the bar comes down, then at most every 10 s (${q2} in 4 s)`, q1 >= 1 && q2 <= 2, { q1, q2 });
  // ⚙️ 🖌️ «📊 عناصر الشريط المصغّر»: a live preview · tap an item ⇒ hidden there and in the bar · kept on this device
  await pg.evaluate(() => { scrollTo(0, 0); openSettings(); stTog('mbi') }); await pg.waitForTimeout(500);
  const ms0 = await pg.evaluate(() => { const row = document.querySelector('#modal .sx[data-k="mbi"]'), g = [...document.querySelectorAll('#modal .sgrp')][0];
    return { v: row.querySelector('.sval').textContent, rows: [...g.querySelectorAll('.sgl>.sitem')].map(r => r.dataset.k || r.id), prev: document.querySelectorAll('#mbPrev span').length,
      btn: [...row.querySelectorAll('button[data-mbi]')].map(b => b.dataset.mbi + (b.classList.contains('on') ? '+' : '-')).join(' '), grp: [...row.querySelectorAll('.cfx-gt')].map(x => x.textContent) } });
  ok(`📊 ⚙️ 🖌️ «عناصر الشريط المصغّر» after its switch («${ms0.v}») · 3 groups (${ms0.grp.join(' · ')}) · a live preview of ${ms0.prev}`,
    ms0.rows.indexOf('mbi') === ms0.rows.indexOf('bMbar') + 1 && /11 من 11/.test(ms0.v) && ms0.prev === 11 && ms0.grp.length === 3 && ms0.btn.split(' ').every(x => x.endsWith('+')), ms0);
  await pg.click('#modal button[data-mbi="cpu"]'); await pg.click('#modal button[data-mbi="bat"]'); await pg.waitForTimeout(250);
  const ms1 = await pg.evaluate(() => ({ v: document.querySelector('#modal .sx[data-k="mbi"] .sval').textContent, ls: localStorage.getItem('dash_mb_off'),
    prev: [...document.querySelectorAll('#mbPrev span')].map(s => s.dataset.mb).join(), on: document.querySelector('#modal button[data-mbi="cpu"]').getAttribute('aria-pressed') }));
  ok(`📊 tap «المعالج» and «البطارية» ⇒ hidden from the preview («${ms1.v}») · kept on this device`, /9 من 11/.test(ms1.v) && ms1.ls === 'cpu,bat' && !/cpu|bat/.test(ms1.prev) && ms1.on === 'false', ms1);
  const ms2 = await pg.evaluate(async () => { hideModal(); await new Promise(r => setTimeout(r, 300)); scrollTo(0, 2600); mbarSync(); await new Promise(r => setTimeout(r, 300));
    const k = [...document.querySelectorAll('#mStat span')].map(s => s.dataset.mb).join(); openSettings(); stTog('mbi'); await new Promise(r => setTimeout(r, 200));
    document.querySelector('#modal button[data-mbi="cpu"]').click(); document.querySelector('#modal button[data-mbi="bat"]').click(); hideModal();
    return { k, ls: localStorage.getItem('dash_mb_off') } });
  ok('📊 the bar follows (no CPU · no battery) · tapped again ⇒ back (nothing stored)', !/cpu|bat/.test(ms2.k) && ms2.k.split(',').length === 9 && ms2.ls === null, ms2);
  await ctx.close();
  // a computer without a battery · the bar switched off ⇒ the computer is never asked
  ({ ctx, pg } = await open(br, errs, { ls: { dash_anim: 'none', dash_mbar: 'off' } }));
  const sysReq2 = []; pg.on('request', r => { if (/\/api\/sys\b/.test(r.url())) sysReq2.push(1) });
  const n0 = await pg.evaluate(async () => { scrollTo(0, 2600); dispatchEvent(new Event('scroll')); mbarSync(); await new Promise(r => setTimeout(r, 1500));
    openSettings(); stTog('mbi'); await new Promise(r => setTimeout(r, 200)); const note = document.querySelector('#modal .sx[data-k="mbi"] .sbody').textContent; hideModal();
    return { bat: MB.bat, batOk: MB.batOk, note } });
  ok('📊 the bar off ⇒ /api/sys never asked while scrolling · a computer with no battery ⇒ no 🔋 (⚙️ says so)', sysReq2.length <= 1 && !n0.bat && /البطارية: هذا الجهاز لا يعطيها/.test(n0.note) && /مخفي الآن/.test(n0.note), { n: sysReq2.length, n0 });
  await ctx.close();
  ok('no page errors', !errs.length, errs);
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_live: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('crash', e); process.exit(1) });
