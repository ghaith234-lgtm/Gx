// 💻 v3.36.54 in a real browser: the owner (15-11) «تطبيق الحاسوب المفروض يصير x#- … بالداخل مع الاشعارارت وينزال الشريط الفوق (طلبتها سابقا)»
//   — the 2.0 program does it; a computer still on 1.2 now sees a clear bar with a one-click download.
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 700)));
}
(async () => {
  const br = await chromium.launch();
  const errs = [];
  async function open(q, init) {
    const ctx = await br.newContext({ viewport: { width: 1280, height: 860 } });
    await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
    if (init) await ctx.addInitScript(init);
    const pg = await ctx.newPage();
    pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
    await pg.routeWebSocket(/.*/, () => {});
    await pg.goto(URL + q, { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots, null, { timeout: 30000 });
    await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
    await pg.waitForTimeout(3600);
    return { ctx, pg };
  }
  // ① the old 1.2 program (it opens the page with ?holyapp=win and no window.HOLYWIN)
  let { ctx, pg } = await open('?holyapp=win&hv=1.2');
  const a = await pg.evaluate(() => { const b = document.getElementById('winOld'); return b ? { t: b.textContent, btn: [...b.querySelectorAll('button')].map(x => x.textContent), top: b === document.body.firstElementChild } : null });
  ok('① inside the old 1.2 program: a bar at the top says the new program (2.1) is ready — no title bar, — ☐ ✕ beside 🔔 — with a one-click download', a && a.top && /2\.1/.test(a.t) && /— ☐ ✕/.test(a.t) && /1\.2/.test(a.t) && a.btn.some(x => x.includes('نزّله')), a);
  const [dl] = await Promise.all([pg.waitForEvent('download', { timeout: 15000 }).catch(() => null), pg.evaluate(() => winOldGet())]);
  const fn = dl ? dl.suggestedFilename() : '', path = dl ? await dl.path() : null;
  const head = path ? require('fs').readFileSync(path).slice(0, 2).toString() : '';
  ok('… the button downloads TheHolyDashboard.exe (a Windows program — «MZ») with this dashboard\'s address inside', fn === 'TheHolyDashboard.exe' && head === 'MZ' && path && require('fs').readFileSync(path).includes(Buffer.from(URL.replace(/\/$/, ''))), { fn, head });
  await pg.evaluate(() => winOldLater()); await pg.reload({ waitUntil: 'domcontentloaded' }); await pg.waitForTimeout(4200);
  ok('… «لاحقاً» hides it on this computer (also after reopening)', await pg.evaluate(() => !document.getElementById('winOld')));
  await ctx.close();
  // ② 2.0 without WebView2 (it falls back to the Edge window: ?holyapp=win&hv=2.0 · no HOLYWIN)
  ({ ctx, pg } = await open('?holyapp=win&hv=2.0'));
  const b = await pg.evaluate(() => { const x = document.getElementById('winOld'); return x ? x.textContent : null });
  ok('② the 2.0 program that fell back to the Edge window: the bar says to install Microsoft Edge WebView2 (not to download 2.0 again)', b && /WebView2/.test(b) && !/نزّله/.test(b), b);
  await ctx.close();
  // ③ inside 2.0 (window.HOLYWIN + chrome.webview) · ④ a normal browser ⇒ no bar
  ({ ctx, pg } = await open('?holyapp=win&hv=2.0', () => { window.HOLYWIN = { v: '2.0', ncr: false }; window.chrome = window.chrome || {}; window.chrome.webview = { postMessage() {}, addEventListener() {} } }));
  const c = await pg.evaluate(() => ({ bar: !!document.getElementById('winOld'), btns: ['wCls', 'wMax', 'wMin'].map(i => { const e = document.getElementById(i); return e && !e.hidden ? e.textContent : null }), order: [...document.querySelectorAll('#wCls,#wMax,#wMin,#bBell')].map(e => [e.id, Math.round(e.getBoundingClientRect().left)]) }));
  ok('③ inside 2.0: no bar · — ☐ ✕ shown beside 🔔 in the Windows order (— ☐ ✕ left to right, 🔔 next to them)', !c.bar && c.btns.every(Boolean) &&
     c.order.find(x => x[0] === 'wMin')[1] < c.order.find(x => x[0] === 'wMax')[1] && c.order.find(x => x[0] === 'wMax')[1] < c.order.find(x => x[0] === 'wCls')[1], c);
  await ctx.close();
  ({ ctx, pg } = await open(''));
  ok('④ a normal browser: no bar, no window buttons', await pg.evaluate(() => !document.getElementById('winOld') && document.getElementById('wCls').hidden));
  await ctx.close();
  ok('no page errors', !errs.length, errs.slice(0, 3));
  await br.close();
  console.log(res.every(Boolean) ? `✅ ui_winold: ${res.filter(Boolean).length}/${res.length}` : `❌ ui_winold: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_winold crashed — ' + String(e).slice(0, 300)); process.exit(1) });
