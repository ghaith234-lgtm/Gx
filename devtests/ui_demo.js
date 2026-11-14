// 🧪 v3.36.46 in a real browser (run through ui_demo.py — every card kind + one demo bot in a closed folder):
//   the owner (14-11): «نشر demo بنفس المحركات وينشرن تحت بعد الحقيقيات يعني خط فاصل بينهم ما فيه مجموع بينهم فقط كل بوت وكرته وينكتب عليه ديمو»
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
(async () => {
  const br = await chromium.launch();
  const errs = [];
  const ctx = await br.newContext({ viewport: { width: 1280, height: 900 } });
  await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 10, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(1500);

  const L = await pg.evaluate(() => {
    const kids = [...document.querySelectorAll('#grid > *')].filter(e => e.style.display !== 'none');
    const pos = e => kids.indexOf(e);
    const sep = document.getElementById('demoSep');
    const demo = DATA.bots.filter(b => b.demo).map(b => CARDS.get(b.dir));
    const real = DATA.bots.filter(b => !b.demo).map(b => CARDS.get(b.dir));
    return { n: DATA.bots.length, nd: demo.length, sep: sep ? pos(sep) : -1, sepTxt: sep ? sep.textContent : '',
      demoPos: demo.map(pos), realPos: real.map(pos), lastReal: Math.max(...real.map(pos)),
      demoBadge: demo.map(e => !!(e && e.querySelector('.demob') && e.classList.contains('isdemo') && e.querySelector('.demob').textContent.includes('ديمو'))),
      realBadge: real.filter(e => e && (e.querySelector('.demob') || e.classList.contains('isdemo'))).length,
      accPos: [...ACARDS.values()].map(pos), oldChip: demo.filter(e => e && /تجريبي/.test(e.textContent)).length,
      fc: (document.getElementById('fcount') || {}).textContent || '', total: +DATA.total_profit || 0,
      demoProfit: (DATA.bots.find(b => b.demo) || {}).profit };
  });
  ok(`🧪 the demo card comes after every real card, under the separator line «🧪 بوتات ديمو» (${L.nd} demo · ${L.n - L.nd} real)`,
     L.nd === 1 && L.sep > L.lastReal && L.demoPos.every(p => p > L.sep) && L.sepTxt.includes('بوتات ديمو') && L.sepTxt.includes('لا تدخل في أي مجموع'), L);
  ok('… the demo card wears «🧪 ديمو» (and the dashed border — one label, not the old «تجريبي» too) · no real card does',
     L.demoBadge.every(Boolean) && L.realBadge === 0 && L.oldChip === 0, L);
  ok('… the accumulator cards stay with the real ones, above the line', L.accPos.length >= 1 && L.accPos.every(p => p >= 0 && p < L.sep), L);
  ok(`… the counter counts them apart («${L.fc}»)`, /9 بوت/.test(L.fc) && /1 ديمو/.test(L.fc), L.fc);
  ok(`… its profit (999$ in its own state — ${(+L.demoProfit).toFixed(2)}$ on its card after fees) reaches no total (the top total ${L.total.toFixed(2)}$)`,
     L.total < 500 && L.demoProfit > 500, L);
  const shot = await pg.evaluate(() => { const s = document.getElementById('demoSep'); if (s) s.scrollIntoView({ block: 'center' }); return !!s });
  if (shot) await pg.screenshot({ path: '/tmp/ui_demo_cards.png' }).catch(() => {});

  // the five deploy forms
  const forms = [['openDeploy', 'n'], ['openDeployStep', 'st'], ['openDeployDca', 'dn'], ['openDeployRec', 'rd'], ['openDeployVa', 'vd']];
  const got = [];
  for (const [fn, p] of forms) {
    await pg.evaluate(f => { try { hideModal() } catch (e) {} ; window[f]() }, fn);
    await pg.waitForTimeout(900);
    const r = await pg.evaluate(p => {
      const c = document.getElementById(p + '_demo'), box = document.getElementById(p + '_dbox');
      if (!c || !box) return { p, ok: false };
      const hid = getComputedStyle(box).display === 'none';
      c.click();
      const shown = getComputedStyle(box).display !== 'none';
      document.getElementById(p + '_dusd').value = '500'; document.getElementById(p + '_dcoin').value = '2';
      const v = demoVal(p);
      return { p, ok: true, hid, shown, v, n: document.querySelectorAll('#' + p + '_demo').length };
    }, p);
    got.push(r);
  }
  ok('every deploy form (♾️ ➕ 🎚️ · 🪜 · DCA · the recurring · 💹) has «🧪 ديمو» once · its balances appear when ticked · the request carries them',
     got.every(r => r.ok && r.hid && r.shown && r.n === 1 && r.v.demo === true && r.v.demo_usd === '500' && r.v.demo_coin === '2'), got);
  ok('no page errors', !errs.length, errs.slice(0, 3));
  await br.close();
  console.log(res.every(Boolean) ? `✅ ui_demo: ${res.filter(Boolean).length}/${res.length}` : `❌ ui_demo: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_demo crashed — ' + String(e).slice(0, 300)); process.exit(1) });
