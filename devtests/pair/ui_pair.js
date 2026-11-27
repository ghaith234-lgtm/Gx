// 🔀 «شبكة عملتين» in a real browser (run through ui_pair.py): ① the deploy button · ② the form (h2 · the main coin XRP by default) ·
//   ③ the calculator table = /api/pair_plan (10 buys below from 200 XRP · 3 sells above from 1 SOL · the cycle profit ≈ 0.30 XRP) ·
//   ④ a step under the four fees ⇒ refused in red · ④b the level counts (v3.36.80) · ⑤ the deploy (launch stubbed) · ⑥ the 📖 guide · ⑦ a phone width · no page error
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const URL = process.argv[2], DIR = process.argv[3], SHOTS = process.argv[4] && process.argv[4] !== '-' ? process.argv[4] : '', Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) { res.push(!!cond); if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900))); }
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function open(pg) {
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && typeof openDeployPair === 'function', null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await sleep(500);
}
async function planText(pg) { await sleep(900); return await pg.evaluate(() => (document.getElementById('pa_plan') || {}).innerText || '') }
(async () => {
  const br = await chromium.launch();
  const errs = [];
  const ctx = await br.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: SHOTS ? 2 : 1 });
  await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await open(pg);
  const btn = pg.locator('#navAct button', { hasText: 'شبكة عملتين' });
  ok('① the deploy button «🔀 شبكة عملتين» beside the others', await btn.count() === 1, await btn.count());
  await btn.first().click();
  await sleep(500);
  const h2 = await pg.evaluate(() => { const h = document.querySelector('#modal h2, .modal h2, h2.tuth'); return h ? h.innerText : '' });
  ok('② the form opens (its h2 says «شبكة عملتين») · the main coin is XRP by default', /شبكة عملتين/.test(h2) && await pg.inputValue('#pa_main') === 'XRP', h2);
  await pg.fill('#pa_oth', 'SOL'); await pg.fill('#pa_am', '200'); await pg.fill('#pa_ao', '1');
  let t = await planText(pg);
  const rows = await pg.evaluate(() => document.querySelectorAll('#pa_plan tbody tr').length);
  ok('③ the table: 10 buys below · 3 sells above (13 rows) · 1 SOL = 75 XRP now', rows === 13 && /10 شراء تحت/.test(t) && /3 بيع فوق/.test(t) && /\b75\b/.test(t), { rows, t: t.slice(0, 400) });
  ok('③ the cycle profit after the four fees ≈ 0.30 XRP (≈ 0.60$) · the smallest step ≈ 1.2%', /0\.30\d* XRP|0\.30\d*\s*XRP/.test(t) && /1\.2\d%/.test(t), t.slice(0, 600));
  await pg.fill('#pa_g', '1');
  t = await planText(pg);
  ok('④ a 1% step (under the four fees and the cap) is refused in red', /لا تغطي العمولات الأربع/.test(t) && await pg.locator('#pa_plan .sterr').count() >= 1, t.slice(0, 300));
  await pg.fill('#pa_g', '2');
  await planText(pg);
  // ④b v3.36.80 the counts: «⬇️/⬆️ عدد المستويات» inside the amounts · beyond them it stops where the coins end and says so
  await pg.fill('#pa_dn', '4'); await pg.fill('#pa_up', '2');
  t = await planText(pg);
  const rows2 = await pg.evaluate(() => document.querySelectorAll('#pa_plan tbody tr').length);
  const bodyC = await pg.evaluate(() => { const b = paBody(); return [b.dn_max, b.up_max] });
  ok('④b the counts 4 below · 2 above ⇒ 6 rows (the amounts cover more) · sent with the form', rows2 === 6 && /4 شراء تحت/.test(t) && /2 بيع فوق/.test(t)
     && bodyC[0] === '4' && bodyC[1] === '2', { rows2, bodyC, t: t.slice(0, 300) });
  await pg.fill('#pa_dn', '15'); await pg.fill('#pa_up', '5');
  t = await planText(pg);
  const notesN = await pg.locator('#pa_plan .pa_note').count();
  ok('④b the counts beyond the coins ⇒ 10 of 15 below · 3 of 5 above — it stops there, said in two lines (no refusal)',
     notesN === 2 && /تكفي 10 مستوى تحت من 15/.test(t) && /تكفي 3 مستوى فوق من 5/.test(t) && await pg.locator('#pa_plan .sterr').count() === 0, { notesN, t: t.slice(0, 500) });
  await pg.fill('#pa_dn', ''); await pg.fill('#pa_up', '');
  await planText(pg);
  if (SHOTS) await pg.screenshot({ path: path.join(SHOTS, 'pair_form.png'), fullPage: false });
  await pg.click('#pa_go');
  await sleep(1500);
  const toastT = await pg.evaluate(() => Array.from(document.querySelectorAll('.toast,#toast,.toasts *')).map(n => n.innerText).join(' | '));
  const launched = fs.existsSync(path.join(DIR, '_launched.json')) ? JSON.parse(fs.readFileSync(path.join(DIR, '_launched.json'))) : {};
  ok('⑤ the deploy: the bot folder made and launched (SOL-XRP) · the toast says so', launched.launched === 'SOL-XRP' && /انتشرت/.test(toastT), { launched, toastT });
  // ⑤b the demo: «🧪 ديمو» shows its note, the wallet is not needed (disabled) · the deploy goes to the demo (the two amounts = its paper wallet)
  await btn.first().click(); await sleep(400);
  await pg.fill('#pa_oth', 'SOL'); await pg.fill('#pa_am', '200'); await pg.fill('#pa_ao', '1');
  await pg.check('#pa_demo'); await sleep(300);
  const dm = await pg.evaluate(() => ({ note: getComputedStyle(document.getElementById('pa_dnote')).display !== 'none', wd: document.getElementById('pa_wallet').disabled,
    body: paBody().demo }));
  await planText(pg);
  try { fs.unlinkSync(path.join(DIR, '_launched.json')) } catch (e) {}
  await pg.click('#pa_go'); await sleep(1800);
  const toastD = await pg.evaluate(() => Array.from(document.querySelectorAll('.toast,#toast,.toasts *')).map(n => n.innerText).join(' | '));
  const launchedD = fs.existsSync(path.join(DIR, '_launched.json')) ? JSON.parse(fs.readFileSync(path.join(DIR, '_launched.json'))) : {};
  const dwal = fs.readdirSync(DIR).filter(n => n.startsWith('demo_pair_sol')).map(n => { try { return JSON.parse(fs.readFileSync(path.join(DIR, n, 'demo_wallet.json'))) } catch (e) { return null } })[0] || {};
  ok('⑤b 🧪 the demo: its note shows · no wallet needed · deployed as a demo with the two amounts as its paper wallet (200 XRP · 1 SOL)',
     dm.note && dm.wd && dm.body === true && launchedD.launched === 'SOL-XRP' && /ديمو/.test(toastD) && dwal.pair === true
     && (dwal.bal || {}).XRP === 200 && (dwal.bal || {}).SOL === 1, { dm, launchedD, toastD, bal: dwal.bal });
  await btn.first().click(); await sleep(400);
  await pg.click('button.tutx'); await sleep(500);
  const tut = await pg.evaluate(() => document.body.innerText);
  ok('⑥ the 📖 guide opens with the idea and the example (75 · 20 XRP · 0.30 XRP)', /عملة رئيسية/.test(tut) && /20 XRP/.test(tut) && /0\.30 XRP/.test(tut), tut.slice(0, 200));
  const ph = await ctx.newPage(); ph.on('pageerror', e => errs.push(String(e)));
  await ph.setViewportSize({ width: 390, height: 840 });
  await ph.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await ph.routeWebSocket(/.*/, () => {});
  await open(ph);
  await ph.evaluate(() => openDeployPair({ other: 'SOL', main_amount: 200, other_amount: 1 }));
  await sleep(1300);
  const ov = await ph.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  ok('⑦ a phone width (390): the form fits (no sideways scroll)', ov <= 1, ov);
  if (SHOTS) await ph.screenshot({ path: path.join(SHOTS, 'pair_form_390.png') });
  ok('no page error', errs.length === 0, errs.slice(0, 3));
  await br.close();
  const n = res.filter(Boolean).length;
  console.log(`${n === res.length ? '✅' : '❌'} ui_pair: ${n}/${res.length}`);
  process.exit(n === res.length ? 0 : 1);
})().catch(e => { console.log('❌ ui_pair crashed: ' + e); process.exit(1) });
