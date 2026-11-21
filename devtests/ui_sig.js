// 🎯 v3.36.66 in a real browser (run through ui_sig.py — a closed folder with a catalog, a scan and the live record · no network):
//   ① 🎯 the window: 5 tabs · «🎯 المؤشرات» (one tab · v3.36.71): your coins first · a coin opens to its indicators on now by family, each in
//     plain words with «صدق … من … مرة» and random beside it
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
  // ① 🎯 the indicators — one tab (v3.36.71: «📈 المؤشرات العشرة» + «🎯 الإشارات الشغّالة» merged · every indicator in plain words)
  await pg.evaluate(() => openSig('now'));                                     // the old name still opens it
  await pg.waitForFunction(() => document.querySelector('#sg_body .sg-c'), null, { timeout: 20000 }).catch(() => {});
  const w1 = await pg.evaluate(() => ({ h2: (document.querySelector('#modal h2') || {}).textContent || '', tabs: [...document.querySelectorAll('#sg_tabs button')].map(b => b.textContent),
    tab: SGTAB, coins: [...document.querySelectorAll('#sg_body > .ind-list > .sg-c .cn')].map(x => x.textContent), others: !!document.querySelector('#sg_body details.sg-more'),
    chips: [...document.querySelectorAll('#sg_body > .ind-list > .sg-c .ind-chip')].map(x => x.textContent) }));
  ok(`① 🧠 one window «${w1.h2}» · tabs ${w1.tabs.join(' | ')} — «now» opens «🎯 المؤشرات»`, w1.h2.startsWith('📊 المؤشرات — المحلل') && w1.tab === 'ind'
     && w1.tabs.join('|') === '🧠 المحلل|🎯 المؤشرات|📚 المجموعات|📜 السجل|⚙️ الإشعارات', w1);
  ok(`① your coins first (${w1.coins.join(' · ')}) · the other measured coins folded below · each «نشطة الآن: 🟢 … · 🔴 …»`, w1.coins.join(',') === 'SOL,XRP' && w1.others
     && w1.chips.length >= 2 && w1.chips.every(t => t.includes('نشطة الآن') && t.includes('🟢') && t.includes('🔴')), w1);
  await pg.evaluate(() => { const c = [...document.querySelectorAll('#sg_body .sg-c')].find(x => x.querySelector('.cn').textContent === 'XRP'); c.click() });
  await sleep(300);
  const w2 = await pg.evaluate(() => { const rows = [...document.querySelectorAll('#sg_body .sg-c.open .sg-pl:not(.ten)')];
    return { n: rows.length, nm: rows.map(r => (r.querySelector('b') || {}).textContent || ''), txt: rows.slice(0, 4).map(r => r.textContent.replace(/\s+/g, ' ').trim()),
      grp: [...document.querySelectorAll('#sg_body .sg-c.open .sg-grp > .sg-frh')].map(x => x.textContent.replace(/\s+/g, ' ').trim()) } });
  ok(`① XRP opens to its indicators on now by family (${w2.grp.map(g => g.split('—')[0].trim()).join(' · ')}) — ${w2.n} indicators, each with its meaning and «صدق … من … · العشوائي …»`,
     w2.n > 0 && w2.grp.length >= 1 && w2.txt.every(t => /صدق \d+ من \d+ مرة/.test(t) && t.includes('العشوائي')), w2);
  ok(`① plain names, no technical letters in them («${w2.nm.slice(0, 3).join('» · «')}») — the technical name only small beside the record`,
     w2.nm.length && w2.nm.every(t => t && !/[A-Za-z]/.test(t)), w2.nm);
  await shot('sig_now');
  // ⓪ 🧠 the analyst (the first tab)
  await pg.evaluate(() => openInd());
  await pg.waitForFunction(() => document.querySelector('#sg_body .an-mkt'), null, { timeout: 20000 }).catch(() => {});
  const a1 = await pg.evaluate(() => ({ tab: SGTAB, mkt: (document.querySelector('#sg_body .an-mkt') || {}).textContent || '',
    cards: [...document.querySelectorAll('#sg_body .an-c')].map(c => ({ cn: c.querySelector('.cn').textContent, w: (c.querySelector('.an-w') || {}).textContent || '',
      hz: [...c.querySelectorAll('.an-hz')].map(z => z.textContent.replace(/\s+/g, ' ').trim()), now: (c.querySelector('.an-now') || {}).textContent || '' })),
    help: (document.querySelector('#sg_body details.ind-help') || {}).textContent || '' }));
  ok(`⓪ 🧠 the analyst opens first · 🌐 «${a1.mkt.replace(/\s+/g, ' ').trim().slice(0, 70)}…»`, a1.tab === 'an' && a1.mkt.includes('🌐 السوق كله الآن') && a1.mkt.includes('🧭'), a1.mkt);
  ok(`⓪ a card for each of your coins (${a1.cards.map(c => c.cn + ' ' + c.w.trim()).join(' · ')}) — one word · «غداً» · «الشهر القادم» · 🔎 the state now`,
     a1.cards.map(c => c.cn).join(',') === 'SOL,XRP' && a1.cards.every(c => /فرصة شراء بحذر|فرصة شراء|انتظر|تجنّب الشراء الآن|خطر نزول/.test(c.w)
       && c.hz.length === 2 && c.hz[0].startsWith('غداً') && c.hz[1].startsWith('الشهر القادم') && c.now.includes('🔎 الآن في السوق') && c.now.includes('ليس توقعاً')), a1.cards);
  ok('⓪ «كيف يعمل المحلل؟» says it: agreeing groups proven in the four periods · no forecast for the next few hours · not a guarantee',
     a1.help.includes('تتفق') && a1.help.includes('الفترات الأربع') && a1.help.includes('أضعف من الصدفة') && a1.help.includes('لا ضمانات'), a1.help.slice(0, 200));
  await shot('sig_analyst');
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#sg_body .an-more button')][0]; if (b) b.click() });
  await sleep(500);
  ok('⓪ «🎯 كل مؤشرات العملة النشطة الآن ←» on a card opens the merged tab with that coin open', await pg.evaluate(() => SGTAB === 'ind' && !!document.querySelector('#sg_body .sg-c.open')), '');
  // ② 📒 the catalog
  await pg.evaluate(() => sgTab('cat'));
  await pg.waitForFunction(() => document.querySelectorAll('#sg_cat .sg-r').length > 0, null, { timeout: 15000 }).catch(() => {});
  const c1 = await pg.evaluate(() => ({ n: document.querySelectorAll('#sg_cat .sg-r').length, head: (document.querySelector('#sg_body .ind-sub') || {}).textContent || '',
    flt: document.querySelectorAll('#sg_body .sg-flt button').length }));
  ok(`② 📒 the catalog: «${c1.head.slice(0, 70)}…» · ${c1.flt} filter buttons · ${c1.n} rows`, c1.n > 0 && c1.flt >= 9 && c1.head.includes('إشارة وتركيبة'), c1);
  await pg.evaluate(() => { SGF.size = '2'; SGF.fr = '1D'; sgRender(); sgCat() });
  await sleep(700);
  const c2 = await pg.evaluate(() => [...document.querySelectorAll('#sg_cat .sg-r .sg-fr')].map(x => x.textContent));
  ok(`② «2 معاً» + «يومي» ⇒ only daily pairs (${c2.length} — 🧠 v3.36.69: only pairs proven in all 4 periods are listed, the random synthetic history may have none)`, c2.every(t => t.includes('يومي') && t.includes('2 معاً')), c2.slice(0, 4));
  await pg.evaluate(() => { SGF.size = ''; SGF.fr = ''; SGF.side = ''; SGF.rare = '1'; sgRender(); sgCat() });
  await sleep(700);
  const c3 = await pg.evaluate(() => [...document.querySelectorAll('#sg_cat .sg-r')].map(r => !!r.querySelector('.sg-b.rare')));
  ok(`② «💎 النادرة فقط» ⇒ nothing (🧠 v3.36.69: no 💎 rare any more — a handful of cases is never proven) (${c3.length})`, c3.length === 0, c3.length);
  await pg.evaluate(() => { SGF.rare = ''; SGF.q = 'الدفع'; sgRender(); sgCat() });
  await sleep(700);
  const c4 = await pg.evaluate(() => [...document.querySelectorAll('#sg_cat .sg-r .sg-k')].map(x => x.textContent));
  ok(`② search «الدفع» (plain words · names and meanings) ⇒ ${c4.length} rows`, c4.length > 0 && c4.filter(t => t.includes('الدفع')).length >= c4.length / 2, c4.slice(0, 3));
  await pg.evaluate(() => { SGF.q = 'MACD'; sgRender(); sgCat() });
  await sleep(700);
  const c5 = await pg.evaluate(() => document.querySelectorAll('#sg_cat .sg-r').length);
  ok(`② search «MACD» (a technical name) still finds its indicators (${c5} rows)`, c5 > 0, c5);
  await pg.evaluate(() => { SGF.q = ''; SGF.side = '1'; sgRender(); sgCat() });
  await sleep(600);
  await shot('sig_catalog');
  // ③ the log
  await pg.evaluate(() => sgTab('log'));
  await sleep(300);
  const l1 = await pg.evaluate(() => (document.querySelector('#sg_body') || {}).textContent || '');
  ok('③ 📜 the log: the live record · «📥 سحب السجل» · the accuracy of what reached you month by month · the last notifications', l1.includes('السجل الحي') && l1.includes('آخر الإشعارات')
     && l1.includes('📥 سحب السجل') && l1.includes('دقة ما وصلك'), l1.slice(0, 200));
  const dl = await pg.evaluate(async () => { let got = null; const keep = holySave; holySave = async (b, n) => { got = { n, t: await b.text() }; return true };
    await sgRecDl(); holySave = keep; return got });
  ok(`③ 📥 the record is saved as a file «${dl && dl.n}» (the header and ${dl ? dl.t.split('\n').length - 1 : 0} rows)`, dl && dl.n === 'holy_analyst_record.csv'
     && dl.t.includes('التاريخ (UTC),العملة,الاتجاه,المدة,المجموعة,النتيجة,الربح %,وصلك إشعارها'), dl && dl.t.slice(0, 200));
  // ④ ⚙️ notifications
  await pg.evaluate(() => sgTab('cfg'));
  await sleep(300);
  const e0 = await pg.evaluate(() => (document.getElementById('sg_est') || {}).textContent || '');
  await pg.evaluate(() => { const s = document.getElementById('sg_thr'); s.value = 90; s.dispatchEvent(new Event('input', { bubbles: true })) });
  await pg.waitForFunction(e0 => { const t = (document.getElementById('sg_est') || {}).textContent || ''; return t && t !== e0 }, e0, { timeout: 8000 }).catch(() => {});
  const e1 = await pg.evaluate(() => ({ est: (document.getElementById('sg_est') || {}).textContent || '', v: (document.getElementById('sg_thr_v') || {}).textContent }));
  const num = t => +((t.match(/نحو ([\d.]+)/) || [])[1] || NaN);
  const one = await pg.evaluate(() => ({ head: ((document.querySelector('#sg_thr') || {}).parentElement || {}).textContent || '', min: !!document.getElementById('sg_min'),
    rnd: [...document.querySelectorAll('#sg_body button')].some(b => b.textContent.includes('أفضل من العشوائي')) }));
  ok(`④ ONE setting: «${one.head.replace(/\s+/g, ' ').trim().slice(0, 70)}…» — no «أقل عدد مرات» slider · no «أفضل من العشوائي» switch (fixed inside)`,
     one.head.includes('لا يصلك إلا ما صدق في') && !one.min && !one.rnd, one);
  ok(`④ the slider to 90% moves the weekly estimate live: «${e0.slice(0, 50)}…» ⇒ «${e1.est.slice(0, 50)}…»`, e1.v === '90%' && num(e1.est) <= num(e0) && e1.est !== e0, { e0, e1 });
  await pg.evaluate(() => { const s = document.getElementById('sg_thr'); s.dispatchEvent(new Event('change', { bubbles: true })) });
  await sleep(900);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#sg_body .sg-flt button')].find(x => x.textContent.includes('🔴 دخول بيع')); b.click() });
  await sleep(900);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#sg_body .sg-flt button')].find(x => x.textContent.trim() === '5'); b.click() });
  await sleep(900);
  const s1 = await pg.evaluate(() => ({ thr: SGV.cfg.thr, sell: SGV.cfg.types.sell, cap: SGV.cfg.cap, on: (document.getElementById('sg_on') || {}).textContent }));
  ok('④ saved: 90% · 🔴 دخول بيع off · the daily cap 5 (the page shows what the server holds)', s1.thr === 90 && s1.sell === false && s1.cap === 5, s1);
  // ④ 🪙 your coins (v3.36.67): the owner «انا اريد انا احدد العملات»
  const k0 = await pg.evaluate(() => ({ mine: [...document.querySelectorAll('#sg_coins .sg-cn')].map(b => b.dataset.c), add: !!document.getElementById('sg_cadd'),
    oth: document.querySelectorAll('#sg_coins details .sg-flt button').length, head: (document.querySelector('#sg_coins .sg-sh') || {}).textContent || '' }));
  ok(`④ 🪙 «${k0.head.replace(/\s+/g, ' ').trim().slice(0, 60)}» · your coins first with ✕ (${k0.mine.join(' · ')}) · «➕ أضف» · the measured ones folded (${k0.oth})`,
     k0.mine.join(',') === 'XRP-USDT,SOL-USDT' && k0.add && k0.oth >= 5 && k0.head.includes('عملات إشعاراتك'), k0);
  await pg.evaluate(() => { const i = document.getElementById('sg_cadd'); i.value = ' pepe '; sgCoinAdd() });
  await sleep(900);
  const k1 = await pg.evaluate(() => ({ coins: SGV.cfg.coins, chips: [...document.querySelectorAll('#sg_coins .sg-cn')].map(b => b.dataset.c), t: (document.querySelector('.toast') || {}).textContent || '' }));
  ok('④ «➕ أضف» any coin by name («pepe» ⇒ PEPE-USDT) — saved and shown first with your coins', JSON.stringify(k1.coins) === JSON.stringify(['XRP-USDT', 'SOL-USDT', 'PEPE-USDT'])
     && k1.chips.includes('PEPE-USDT'), k1);
  await pg.evaluate(() => document.querySelector('#sg_coins .sg-cn[data-c="SOL-USDT"]').click());
  await sleep(900);
  const k2 = await pg.evaluate(() => SGV.cfg.coins);
  ok('④ ✕ on SOL removes it from your notifications (the rest stays)', JSON.stringify(k2) === JSON.stringify(['XRP-USDT', 'PEPE-USDT']), k2);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#sg_coins details .sg-flt button')].find(x => x.dataset.c === 'LINK-USDT'); b.click() });
  await sleep(900);
  const k3 = await pg.evaluate(() => SGV.cfg.coins);
  ok('④ a measured coin from the folded list (LINK) is added with one tap', JSON.stringify(k3) === JSON.stringify(['XRP-USDT', 'PEPE-USDT', 'LINK-USDT']), k3);
  await pg.evaluate(() => { const i = document.getElementById('sg_cadd'); i.value = 'BAD COIN!'; sgCoinAdd() });
  await sleep(500);
  ok('④ a wrong name is refused with a clear message (nothing saved)', JSON.stringify(await pg.evaluate(() => SGV.cfg.coins)) === JSON.stringify(k3), '');
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#sg_coins button')].find(x => x.textContent.includes('مثل الشريط')); b.click() });
  await sleep(900);
  const k4 = await pg.evaluate(() => ({ c: SGV.cfg.coins, chips: [...document.querySelectorAll('#sg_coins .sg-cn')].map(b => b.dataset.c) }));
  ok('④ «↩️ مثل الشريط» ⇒ your coins follow the ticker again (XRP · SOL)', k4.c === null && k4.chips.join(',') === 'XRP-USDT,SOL-USDT', k4);
  await shot('sig_settings');
  // ⑤ 🔮 · 📊 · ⚙️ · the ticker · a notification tap
  await pg.evaluate(() => openFc());
  await pg.waitForFunction(() => document.querySelector('#fc_body .sg-go'), null, { timeout: 15000 }).catch(() => {});
  const f1 = await pg.evaluate(() => ({ top: (document.querySelector('#fc_body .sg-go') || {}).textContent || '', lines: [...document.querySelectorAll('#fc_body .sg-fc')].map(x => x.textContent.replace(/\s+/g, ' ').trim()),
    btn: [...document.querySelectorAll('#modal .mbtns button')].some(b => b.textContent.includes('🎯 المؤشرات')) }));
  ok(`⑤ 🔮 «${f1.top.replace(/\s+/g, ' ').trim().slice(0, 80)}» on top · ${f1.lines.length} coins with their signals line · a 🎯 button`,
     f1.top.includes('🎯 المؤشرات الآن') && f1.top.includes('🧭') && f1.lines.length >= 1 && f1.lines.some(l => l.includes('🎯')) && f1.btn, f1);
  ok(`⑤ 🔮 every coin of yours has «🧠 ملخص المحلل» (${f1.lines.filter(l => l.includes('🧠')).length}) — the word · tomorrow · next month`, f1.lines.filter(l => l.includes('🧠 ملخص المحلل') && l.includes('غداً') && l.includes('الشهر القادم')).length >= 2, f1.lines.filter(l => l.includes('🧠')));
  await shot('sig_forecast');
  await pg.evaluate(() => document.querySelector('#fc_body .sg-go').click());
  await sleep(500);
  ok('⑤ a tap on it opens 📊 the analyst', ((await pg.evaluate(() => (document.querySelector('#modal h2') || {}).textContent || ''))).startsWith('📊 المؤشرات — المحلل'), '');
  await pg.evaluate(() => openInd());
  await sleep(400);
  ok('⑤ 📊 holds «🎯 المؤشرات» as a tab (no separate 🎯 window) and has 🔮', await pg.evaluate(() => [...document.querySelectorAll('#sg_tabs button')].some(b => b.textContent.includes('🎯 المؤشرات'))
     && [...document.querySelectorAll('#modal .mbtns button')].some(b => b.textContent.includes('🔮'))), '');
  await pg.evaluate(() => { hideModal(); openSettings() });
  await sleep(500);
  const row = await pg.evaluate(() => { const b = [...document.querySelectorAll('.sitem')].find(x => x.textContent.includes('المؤشرات وإشعارات المحلل')); return b ? b.textContent.replace(/\s+/g, ' ').trim() : '' });
  ok(`⑤ ⚙️ «${row}» in 🔔 الإشعارات`, row.includes('🎯') && row.includes('بنسبتك'), row);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('.sitem')].find(x => x.textContent.includes('المؤشرات وإشعارات المحلل')); b.click() });
  await sleep(600);
  ok('⑤ … it opens 🎯 on «⚙️ الإشعارات»', await pg.evaluate(() => !!document.getElementById('sg_thr') && SGTAB === 'cfg'), '');
  await pg.evaluate(() => openTicker());
  await sleep(1200);
  ok('⑤ the ticker\'s settings: «🔔 إشعارات المحلل» with its buttons', await pg.evaluate(() => ((document.getElementById('tk_pxa') || {}).textContent || '').includes('🔔 إشعارات المحلل')), '');
  await pg.evaluate(() => { hideModal(); HGO = 'sig'; holyGoNow() });
  await sleep(600);
  ok('⑤ a notification tap («sig») opens 📊 the analyst', ((await pg.evaluate(() => (document.querySelector('#modal h2') || {}).textContent || ''))).startsWith('📊 المؤشرات — المحلل'), '');
  // ⑥ a phone
  await pg.setViewportSize({ width: 390, height: 844 });
  for (const t of ['an', 'ind', 'cat', 'cfg']) {
    await pg.evaluate(t => sgTab(t), t);
    await sleep(700);
    const ov = await pg.evaluate(() => { const b = document.getElementById('sg_body'); return { sw: b.scrollWidth, cw: b.clientWidth, doc: document.documentElement.scrollWidth, vw: innerWidth } });
    ok(`⑥ a phone (390): «${t}» does not spill sideways (${ov.sw} ≤ ${ov.cw} · page ${ov.doc} ≤ ${ov.vw})`, ov.sw <= ov.cw + 1 && ov.doc <= ov.vw + 1, ov);
  }
  if (SHOTS) { await pg.evaluate(() => sgTab('ind')); await sleep(500); await pg.screenshot({ path: `${SHOTS}/sig_phone.png` }) }
  ok('no page error', !errs.length, errs);
  fs.writeFileSync(OUT, JSON.stringify(J));
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_sig.js ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ crash', e); process.exit(1) });
