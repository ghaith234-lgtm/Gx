// ⏳ v3.36.58 in a real browser — the temporary buy pause (p99). node ui_temp_pause.js URL SOLDIR XRPDIR [-q]   (see ui_temp_pause.py)
const { chromium, devices } = require('playwright');
const URL = process.argv[2], SOL = process.argv[3], XRP = process.argv[4], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const br = await chromium.launch();
  const errs = [];
  async function open(opt) {
    const ctx = await br.newContext(opt || { viewport: { width: 1280, height: 900 } });
    await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
    const pg = await ctx.newPage();
    pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
    await pg.routeWebSocket(/.*/, () => {});
    await pg.goto(URL, { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length, null, { timeout: 30000 });
    await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
    await pg.waitForTimeout(2500);
    await pg.evaluate(() => { const o = window.api; window.api = async (...a) => { const r = await o(...a); if (a[0] === '/api/control') window.__ctl = r; return r } });   // the buttons' own replies (the toast is shared with the 🔔 notices)
    return { ctx, pg };
  }
  const dirOf = (pg, rel) => pg.evaluate(rel => (DATA.bots.find(b => b.dir === rel || b.dir.endsWith(rel)) || {}).dir, rel);
  let { ctx, pg } = await open();
  const sd = await dirOf(pg, SOL), xd = await dirOf(pg, XRP);
  // ① the SOL card: the green chip
  const c1 = await pg.evaluate(dir => { const el = CARDS.get(dir), b = botOf(dir); const ch = el.querySelector('.chip.cashw');
    return { chip: ch && ch.textContent, cls: ch && ch.className, floor: b.floor, tfloor: b.tfloor, ab: el._r.ab && el._r.ab.textContent } }, sd);
  ok(`① the SOL card: «${c1.chip}» (the dollars cover part of the 6 kept) · the card's own ⏸ shows the owner's valve («${c1.ab}» — his floor ${c1.floor}) · the temporary floor ${c1.tfloor}`,
    /🔓 افتح المؤقت \(6\)/.test(c1.chip || '') && /tpo/.test(c1.cls || '') && c1.floor === 0 && c1.tfloor === 181.5 && /⏸ إيقاف الشراء/.test(c1.ab || ''), c1);
  // ② its window
  await pg.evaluate(dir => CARDS.get(dir).querySelector('.chip.cashw').click(), sd);
  await sleep(700);
  const w = await pg.evaluate(() => { const m = document.getElementById('modal'); return { first: m.querySelector('.hwb').firstElementChild.tagName,
    h2: m.querySelector('h2').textContent, txt: m.textContent, btn: [...m.querySelectorAll('button')].map(b => b.textContent) } });
  ok(`② «🔓 افتح المؤقت» opens its window (rule 14: <h2> first · «${w.h2}»): «يكفي 3 من 6» · from the beginning in one order at the market · the DCA's dollars not counted`,
    w.first === 'H2' && /وقف الشراء المؤقت/.test(w.h2) && /يكفي 3 من 6/.test(w.txt) && /بأمر واحد/.test(w.txt) && /DCA البيعي لا يُحسب/.test(w.txt)
    && w.btn.some(t => /🔓 افتح/.test(t)), w);
  await pg.evaluate(() => [...document.querySelectorAll('#modal button')].find(b => /🔓 افتح/.test(b.textContent)).click());
  await sleep(1500);
  const t1 = await pg.evaluate(() => ((window.__ctl || {}).msg || ''));
  ok(`… «🔓 افتح»: «${t1.slice(0, 110)}»`, /فُتح وقف الشراء المؤقت لـ 3 من 6/.test(t1) && /يبقى محفوظاً/.test(t1), t1);
  // ③ the XRP card: both valves — his button opens HIS valve only
  const c2 = await pg.evaluate(dir => { const el = CARDS.get(dir), b = botOf(dir); const ch = el.querySelector('.chip.cashw');
    return { chip: ch && ch.textContent, ab: el._r.ab && el._r.ab.textContent, floor: b.floor, tfloor: b.tfloor } }, xd);
  ok(`③ the XRP card: «${c2.chip}» · his own button «${c2.ab}» (his floor ${c2.floor} · the temporary ${c2.tfloor})`,
    /⏳ مؤقت/.test(c2.chip || '') && /▶️ استئناف الشراء/.test(c2.ab || '') && c2.floor === 2.4 && c2.tfloor === 2.43, c2);
  await pg.evaluate(dir => CARDS.get(dir)._r.ab.click(), xd);
  await sleep(600);
  const w2 = await pg.evaluate(() => { const m = document.getElementById('modal'); return { h2: m.querySelector('h2').textContent, txt: m.textContent } });
  ok(`… it opens «${w2.h2}» — no market order: the temporary pause stays closed`, /رفع إيقافك/.test(w2.h2) && /ما زال مغلقاً/.test(w2.txt), w2);
  await pg.evaluate(() => [...document.querySelectorAll('#modal button')].find(b => /ارفع إيقافي/.test(b.textContent)).click());
  await sleep(1500);
  const t2 = await pg.evaluate(() => ((window.__ctl || {}).msg || ''));
  ok(`… «▶️ ارفع إيقافي»: «${t2.slice(-110)}»`, /رُفع إيقافك/.test(t2) && /المؤقت ما زال مغلقاً/.test(t2), t2);
  ok(`no page error on the computer (${errs.length})`, errs.length === 0, errs);
  await ctx.close();
  // ④ the phone
  const e0 = errs.length;
  ({ ctx, pg } = await open({ ...devices['iPhone 13'] }));
  await pg.evaluate(dir => CARDS.get(dir).scrollIntoView({ block: 'center' }), xd);
  await sleep(400);
  const ph = await pg.evaluate(dir => { const ch = CARDS.get(dir).querySelector('.chip.cashw'); const r = ch.getBoundingClientRect();
    return { l: r.left, r: r.right, iw: innerWidth, sw: document.documentElement.scrollWidth } }, xd);
  await pg.evaluate(dir => CARDS.get(dir).querySelector('.chip.cashw').click(), xd);
  await sleep(700);
  const pw = await pg.evaluate(() => { const m = document.getElementById('modal'), r = m.getBoundingClientRect(); return { h2: m.querySelector('h2').textContent, w: r.width, iw: innerWidth } });
  ok(`④ the phone: the chip inside the screen · its window fits (${Math.round(pw.w)}px of ${pw.iw}) · no sideways scroll`,
    ph.l >= 0 && ph.r <= ph.iw + 1 && ph.sw <= ph.iw + 1 && /وقف الشراء المؤقت/.test(pw.h2) && pw.w <= pw.iw + 1, { ph, pw });
  ok(`no page error on the phone (${errs.length - e0})`, errs.length === e0, errs.slice(e0));
  await ctx.close();
  await br.close();
  console.log((res.every(Boolean) ? '✅' : '❌') + ` ui_temp_pause.js: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_temp_pause.js crashed: ' + String(e && e.stack || e).slice(0, 1500)); process.exit(1) });
