// 🎯 v3.36.66 in a real browser (run through ui_sig.py — a closed folder with a catalog, a scan and the live record · no network):
//   ① 🎯 the window: «<h2>🎯 الإشارات …» · 4 tabs · 🧭 the compass with its 60 days · your coins first · a coin opens to its signals with
//     «صدقت … من … مرة» and random beside it
//   ② 📒 the catalog: filters (frame · side · size · 💎) · search · every row has its record
//   ③ 🧾 the log · ④ ⚙️ the notifications: the slider moves the weekly estimate live and saves on release · type and cap buttons save
//   ⑤ 🔮 the forecasts: «🎯 الإشارات الآن» on top + every coin's line · a tap opens 🎯 · 📊 has the button · ⚙️ has the row · the ticker's
//     settings have the panel · a notification tap («sig») opens 🎯 · ⑥ a phone width: nothing spills sideways · no page error
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2], OUT = process.argv[3], SHOTS = process.argv[4] && process.argv[4] !== '-' ? process.argv[4] : '', Q = process.argv.includes('-q');
const res = [], J = {};
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 1200)));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const br = await chromium.launch();
  const errs = [];
  const ctx = await br.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: SHOTS ? 2 : 1 });
  await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && typeof openSig === 'function', null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await sleep(800);
  const shot = async n => { if (SHOTS) { await sleep(450); await pg.locator('#modal .modal-box, #modal > div').first().screenshot({ path: `${SHOTS}/${n}.png` }).catch(async () => pg.screenshot({ path: `${SHOTS}/${n}.png` })) } };
  // ① 🎯 now
  await pg.evaluate(() => openSig('now'));
  await pg.waitForFunction(() => document.querySelector('#sg_body .sg-c'), null, { timeout: 20000 }).catch(() => {});
  const w1 = await pg.evaluate(() => ({ h2: (document.querySelector('#modal h2') || {}).textContent || '', tabs: [...document.querySelectorAll('#sg_tabs button')].map(b => b.textContent),
    comp: (document.querySelector('.sg-comp') || {}).textContent || '', hist: document.querySelectorAll('.sg-hist i').length,
    coins: [...document.querySelectorAll('#sg_body > .ind-list > .sg-c .cn')].map(x => x.textContent), others: !!document.querySelector('#sg_body details.sg-more') }));
  ok(`① 🎯 «${w1.h2}» · tabs ${w1.tabs.join(' | ')}`, w1.h2.startsWith('🎯 الإشارات') && w1.tabs.join('|') === '🎯 الآن|📒 الدليل|🧾 السجل|⚙️ الإشعارات', w1);
  ok(`① 🧭 the compass on top with its last ${w1.hist} days («${w1.comp.slice(0, 60)}…»)`, w1.comp.includes('🧭 السوق الآن') && w1.hist >= 30 && /صاعد|مختلط|نازل/.test(w1.comp), w1);
  ok(`① your coins first (${w1.coins.join(' · ')}) · the other measured coins folded below`, w1.coins.join(',') === 'SOL,XRP' && w1.others, w1);
  await pg.evaluate(() => { const c = [...document.querySelectorAll('#sg_body .sg-c')].find(x => x.querySelector('.cn').textContent === 'XRP'); c.click() });
  await sleep(300);
  const w2 = await pg.evaluate(() => { const rows = [...document.querySelectorAll('#sg_body .sg-c.open .sg-r')];
    return { n: rows.length, txt: rows.slice(0, 3).map(r => r.textContent.replace(/\s+/g, ' ').trim()), fr: [...document.querySelectorAll('#sg_body .sg-c.open .sg-frh')].map(x => x.textContent) } });
  ok(`① XRP opens to its signals (${w2.n} rows · ${w2.fr.map(x => x.split('·')[0].trim()).join(' / ')}) — each «صدقت … من … مرة · العشوائي … · المتوسط بعد …»`,
     w2.n > 0 && w2.txt.every(t => /صدقت \d+ من \d+ مرة/.test(t) && t.includes('العشوائي') && t.includes('المتوسط بعد')) && w2.fr.length >= 1, w2);
  await shot('sig_now');
  // ② 📒 the catalog
  await pg.evaluate(() => sgTab('cat'));
  await pg.waitForFunction(() => document.querySelectorAll('#sg_cat .sg-r').length > 0, null, { timeout: 15000 }).catch(() => {});
  const c1 = await pg.evaluate(() => ({ n: document.querySelectorAll('#sg_cat .sg-r').length, head: (document.querySelector('#sg_body .ind-sub') || {}).textContent || '',
    flt: document.querySelectorAll('#sg_body .sg-flt button').length }));
  ok(`② 📒 the catalog: «${c1.head.slice(0, 70)}…» · ${c1.flt} filter buttons · ${c1.n} rows`, c1.n > 0 && c1.flt >= 10 && c1.head.includes('إشارة وتركيبة'), c1);
  await pg.evaluate(() => { SGF.size = '2'; SGF.fr = '1D'; sgRender(); sgCat() });
  await sleep(700);
  const c2 = await pg.evaluate(() => [...document.querySelectorAll('#sg_cat .sg-r .sg-fr')].map(x => x.textContent));
  ok(`② «2 معاً» + «يومي» ⇒ only daily pairs (${c2.length})`, c2.length > 0 && c2.every(t => t.includes('يومي') && t.includes('2 معاً')), c2.slice(0, 4));
  await pg.evaluate(() => { SGF.size = ''; SGF.fr = ''; SGF.side = ''; SGF.rare = '1'; sgRender(); sgCat() });
  await sleep(700);
  const c3 = await pg.evaluate(() => [...document.querySelectorAll('#sg_cat .sg-r')].map(r => !!r.querySelector('.sg-b.rare')));
  ok(`② «💎 النادرة فقط» ⇒ every row is 💎 (${c3.length})`, c3.length > 0 && c3.every(Boolean), c3.length);
  await pg.evaluate(() => { SGF.rare = ''; SGF.q = 'بولنجر'; sgRender(); sgCat() });
  await sleep(700);
  const c4 = await pg.evaluate(() => [...document.querySelectorAll('#sg_cat .sg-r .sg-k')].map(x => x.textContent));
  ok(`② search «بولنجر» ⇒ ${c4.length} rows, every one has it`, c4.length > 0 && c4.every(t => t.includes('بولنجر')), c4.slice(0, 3));
  await pg.evaluate(() => { SGF.q = ''; SGF.side = '1'; sgRender(); sgCat() });
  await sleep(600);
  await shot('sig_catalog');
  // ③ the log
  await pg.evaluate(() => sgTab('log'));
  await sleep(300);
  const l1 = await pg.evaluate(() => (document.querySelector('#sg_body') || {}).textContent || '');
  ok('③ 🧾 the log: the live record and the last notifications', l1.includes('السجل الحي') && l1.includes('آخر الإشعارات'), l1.slice(0, 200));
  // ④ ⚙️ notifications
  await pg.evaluate(() => sgTab('cfg'));
  await sleep(300);
  const e0 = await pg.evaluate(() => (document.getElementById('sg_est') || {}).textContent || '');
  await pg.evaluate(() => { const s = document.getElementById('sg_thr'); s.value = 90; s.dispatchEvent(new Event('input', { bubbles: true })) });
  await pg.waitForFunction(e0 => { const t = (document.getElementById('sg_est') || {}).textContent || ''; return t && t !== e0 }, e0, { timeout: 8000 }).catch(() => {});
  const e1 = await pg.evaluate(() => ({ est: (document.getElementById('sg_est') || {}).textContent || '', v: (document.getElementById('sg_thr_v') || {}).textContent }));
  const num = t => +((t.match(/نحو ([\d.]+)/) || [])[1] || NaN);
  ok(`④ the slider to 90% moves the weekly estimate live: «${e0.slice(0, 50)}…» ⇒ «${e1.est.slice(0, 50)}…»`, e1.v === '90%' && num(e1.est) <= num(e0) && e1.est !== e0, { e0, e1 });
  await pg.evaluate(() => { const s = document.getElementById('sg_thr'); s.dispatchEvent(new Event('change', { bubbles: true })) });
  await sleep(900);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#sg_body .sg-flt button')].find(x => x.textContent.includes('🔴 بيع')); b.click() });
  await sleep(900);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#sg_body .sg-flt button')].find(x => x.textContent.trim() === '5'); b.click() });
  await sleep(900);
  const s1 = await pg.evaluate(() => ({ thr: SGV.cfg.thr, sell: SGV.cfg.types.sell, cap: SGV.cfg.cap, on: (document.getElementById('sg_on') || {}).textContent }));
  ok('④ saved: 90% · 🔴 بيع off · the daily cap 5 (the page shows what the server holds)', s1.thr === 90 && s1.sell === false && s1.cap === 5, s1);
  await shot('sig_settings');
  // ⑤ 🔮 · 📊 · ⚙️ · the ticker · a notification tap
  await pg.evaluate(() => openFc());
  await pg.waitForFunction(() => document.querySelector('#fc_body .sg-go'), null, { timeout: 15000 }).catch(() => {});
  const f1 = await pg.evaluate(() => ({ top: (document.querySelector('#fc_body .sg-go') || {}).textContent || '', lines: [...document.querySelectorAll('#fc_body .sg-fc')].map(x => x.textContent.replace(/\s+/g, ' ').trim()),
    btn: [...document.querySelectorAll('#modal .mbtns button')].some(b => b.textContent.includes('🎯 الإشارات')) }));
  ok(`⑤ 🔮 «${f1.top.replace(/\s+/g, ' ').trim().slice(0, 80)}» on top · ${f1.lines.length} coins with their signals line · a 🎯 button`,
     f1.top.includes('🎯 الإشارات الآن') && f1.top.includes('🧭') && f1.lines.length >= 1 && f1.lines[0].includes('🎯') && f1.btn, f1);
  await shot('sig_forecast');
  await pg.evaluate(() => document.querySelector('#fc_body .sg-go').click());
  await sleep(500);
  ok('⑤ a tap on it opens 🎯', ((await pg.evaluate(() => (document.querySelector('#modal h2') || {}).textContent || ''))).startsWith('🎯'), '');
  await pg.evaluate(() => openInd());
  await sleep(400);
  ok('⑤ 📊 has «🎯 الإشارات»', await pg.evaluate(() => [...document.querySelectorAll('#modal .mbtns button')].some(b => b.textContent.includes('🎯 الإشارات'))), '');
  await pg.evaluate(() => { hideModal(); openSettings() });
  await sleep(500);
  const row = await pg.evaluate(() => { const b = [...document.querySelectorAll('.sitem')].find(x => x.textContent.includes('الإشارات وإشعاراتها')); return b ? b.textContent.replace(/\s+/g, ' ').trim() : '' });
  ok(`⑤ ⚙️ «${row}» in 🔔 الإشعارات`, row.includes('🎯') && row.includes('بنسبتك'), row);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('.sitem')].find(x => x.textContent.includes('الإشارات وإشعاراتها')); b.click() });
  await sleep(600);
  ok('⑤ … it opens 🎯 on «⚙️ الإشعارات»', await pg.evaluate(() => !!document.getElementById('sg_thr') && SGTAB === 'cfg'), '');
  await pg.evaluate(() => openTicker());
  await sleep(1200);
  ok('⑤ the ticker\'s settings: «🎯 إشعارات الإشارات» with its buttons', await pg.evaluate(() => ((document.getElementById('tk_pxa') || {}).textContent || '').includes('🎯 إشعارات الإشارات')), '');
  await pg.evaluate(() => { hideModal(); HGO = 'sig'; holyGoNow() });
  await sleep(600);
  ok('⑤ a notification tap («sig») opens 🎯', ((await pg.evaluate(() => (document.querySelector('#modal h2') || {}).textContent || ''))).startsWith('🎯'), '');
  // ⑥ a phone
  await pg.setViewportSize({ width: 390, height: 844 });
  for (const t of ['now', 'cat', 'cfg']) {
    await pg.evaluate(t => sgTab(t), t);
    await sleep(700);
    const ov = await pg.evaluate(() => { const b = document.getElementById('sg_body'); return { sw: b.scrollWidth, cw: b.clientWidth, doc: document.documentElement.scrollWidth, vw: innerWidth } });
    ok(`⑥ a phone (390): «${t}» does not spill sideways (${ov.sw} ≤ ${ov.cw} · page ${ov.doc} ≤ ${ov.vw})`, ov.sw <= ov.cw + 1 && ov.doc <= ov.vw + 1, ov);
  }
  if (SHOTS) { await pg.evaluate(() => sgTab('now')); await sleep(500); await pg.screenshot({ path: `${SHOTS}/sig_phone.png` }) }
  ok('no page error', !errs.length, errs);
  fs.writeFileSync(OUT, JSON.stringify(J));
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_sig.js ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ crash', e); process.exit(1) });
