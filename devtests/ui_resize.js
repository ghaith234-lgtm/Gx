// ⚠️ run through ui_resize.py: a 🔁 bot's order box through 6 resizes — no ResizeObserver loop error, no «خلل واجهة» toast, the box fits 3
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
(async () => {
  const br = await chromium.launch();
  const ctx = await br.newContext({ viewport: { width: 430, height: 900 } });
  await ctx.addInitScript(() => {
    window.__err = []; window.__toast = [];
    window.addEventListener('error', e => window.__err.push(String(e.message || e)), true);
    new MutationObserver(() => { const t = document.getElementById('toast'); if (t && t.className.includes('show')) { const s = t.textContent;
      if (window.__toast[window.__toast.length - 1] !== s) window.__toast.push(s) } }).observe(document, { subtree: true, childList: true, attributes: true, characterData: true });
  });
  await ctx.routeWebSocket(/.*/, () => {});             // the page's OKX live-price socket: answered here, never the network
  const pg = await ctx.newPage();
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => document.querySelectorAll('.rclots .rcl').length >= 8, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  const fits = [];
  const fit = () => pg.evaluate(() => { const n = document.querySelector('.rclots'), r = n.children;
    return { mh: n.style.maxHeight, want: (r[3].offsetTop - r[0].offsetTop) + 'px', h: Math.round(n.getBoundingClientRect().height) } });
  await pg.waitForTimeout(1500); fits.push(await fit());
  for (const w of [1280, 360, 900, 430, 1600, 430]) { await pg.setViewportSize({ width: w, height: 900 }); await pg.waitForTimeout(700); fits.push(await fit()) }
  const st = await pg.evaluate(() => ({ err: window.__err.slice(), toast: window.__toast.slice() }));
  const ro = st.err.filter(m => /ResizeObserver/.test(m)), tw = st.toast.filter(t => /خلل واجهة/.test(t));
  ok(`① open + 6 resizes (phone ⇄ wide) with a 🔁 bot holding 8 orders: no ResizeObserver loop error (${ro.length}) · no «خلل واجهة» toast (${tw.length})`,
     !ro.length && !tw.length, st);
  ok(`② the order box still fits exactly 3 orders after every resize (${fits.map(f => f.mh).join(' · ')})`,
     fits.every(f => f.mh === f.want && f.mh !== 'none'), fits);
  await pg.evaluate(() => window.dispatchEvent(new ErrorEvent('error', { message: 'ResizeObserver loop completed with undelivered notifications.' })));
  await pg.waitForTimeout(400);
  const ext = await pg.evaluate(() => window.__toast.filter(t => /ResizeObserver/.test(t)));
  ok('… the same browser note from anywhere else (another observer · an extension) never becomes a toast', !ext.length, ext);
  await pg.evaluate(() => setTimeout(() => { throw new Error('devtests real page error') }, 0)); await pg.waitForTimeout(400);
  const real = await pg.evaluate(() => window.__toast.slice());
  ok('… a real page error still shows its «⚠️ خلل واجهة» toast (only the browser\'s harmless ResizeObserver note is skipped)',
     real.some(t => /خلل واجهة: .*devtests real page error/.test(t)), real);
  await br.close();
  console.log(`${res.filter(Boolean).length} ok · ${res.length - res.filter(Boolean).length} failed`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ crash ' + e); process.exit(1); });
