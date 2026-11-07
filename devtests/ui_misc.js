// 🧩 the owner's requests 7-11 in a real browser (run through ui_misc.py — the real dashboard in a closed folder):
//   the pages row: «🔗 الارتباط» (no «👛 المحافظ») · «🗄️ الأرشيف» between «🛡️ الرقابة» and «📉 الخسائر» · its dialog lists the deleted
//   bot (type · started/deleted · profit · its settings, no key) · the run time on a bot card and an accumulator card «… · منذ MM-DD»
//   with its start date and hour in the tip · the wallets page titled «🔗 الارتباط» · no page error
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 700)));
}
(async () => {
  const br = await chromium.launch();
  const ctx = await br.newContext({ viewport: { width: 1440, height: 1000 } });
  await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.removeItem('dash_skin') } catch (e) {} });
  const pg = await ctx.newPage();
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});      // the page's OKX live-price socket: answered here, never the network
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length > 0, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(2500);
  const nav = await pg.evaluate(() => [...document.querySelectorAll('#navAct .grp[aria-label="الصفحات"] button')].map(b => b.textContent.trim()));
  const ig = nav.findIndex(t => /🛡️/.test(t)), ia = nav.indexOf('🗄️ الأرشيف'), il = nav.indexOf('📉 الخسائر');
  ok('the pages row: «🔗 الارتباط» (no «👛 المحافظ») · «🗄️ الأرشيف» between «🛡️ الرقابة» and «📉 الخسائر»',
     nav.includes('🔗 الارتباط') && !nav.some(t => /المحافظ/.test(t)) && ig >= 0 && ia === ig + 1 && il === ia + 1, nav);
  await pg.click('#bArch');
  await pg.waitForFunction(() => document.querySelectorAll('#ar_body .arch').length > 0, null, { timeout: 15000 }).catch(() => null);
  const ar = await pg.evaluate(() => { const m = document.getElementById('modal'); return { h: (m.querySelector('h2') || {}).textContent, n: m.querySelectorAll('.arch').length, t: m.innerText } });
  ok('«🗄️ الأرشيف»: the deleted bot — its type, when it was deleted, its coin profit and its settings (no key, no secret)',
     /🗄️ الأرشيف/.test(ar.h) && ar.n === 1 && /SOL-USDT/.test(ar.t) && /DCA بيعي/.test(ar.t) && /⏹ حُذف: 2026-01-01/.test(ar.t) && /0\.01230000 SOL/.test(ar.t)
     && /⚙️ الإعدادات/.test(ar.t) && !/KEYA|SECA|PASA|api_key|secret/.test(ar.t), ar);
  await pg.evaluate(() => { const d = document.querySelector('#ar_body details'); if (d) d.open = true });
  const cfgShown = await pg.evaluate(() => (document.querySelector('#ar_body details pre') || {}).textContent || '');
  ok('… its settings open (the full list)', /usd_value/.test(cfgShown) && !/api_key|secret|passphrase/.test(cfgShown), cfgShown.slice(0, 300));
  await pg.evaluate(() => hideModal());
  const age = await pg.evaluate(() => { const c = document.querySelector('.card[data-dir="grid_xrp"] [data-k="age"]'); return c && { t: c.textContent, tip: c.title } });
  const acc = await pg.evaluate(() => { const c = document.querySelector('[data-acc="A1"] [data-k="aage"]'); return c && { t: c.textContent, tip: c.title } });
  const rx = /^(\d+ (دقيقة|ساعة)|[\d.]+ (يوم|شهر)) · منذ (\d{4}-)?\d\d-\d\d$/;
  ok('⏱️ the bot card: its run time + the day it started (the date and hour in its tip — a fixed date, not the files)',
     age && rx.test(age.t) && /بدأ التشغيل: \d{4}-\d\d-\d\d \d\d:\d\d/.test(age.tip), age);
  ok('⏱️ the accumulator card has its run time too (its own fixed date)', acc && rx.test(acc.t) && /بدأ التشغيل/.test(acc.tip), acc);
  await pg.evaluate(() => openWallets());
  await pg.waitForTimeout(400);
  const wt = await pg.evaluate(() => (document.querySelector('#page_wallets h2') || {}).textContent);
  ok('the page behind it: «🔗 الارتباط — المحافظ وتيليغرام»', wt === '🔗 الارتباط — المحافظ وتيليغرام', wt);
  ok('no page error', errs.length === 0, errs.slice(0, 3));
  await br.close();
  console.log(`${res.filter(Boolean).length} ok · ${res.length - res.filter(Boolean).length} failed`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ crash ' + e); process.exit(1); });
