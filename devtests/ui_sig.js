// 🎯 v3.36.66 in a real browser (run through ui_sig.py — a closed folder with a catalog, a scan and the live record · no network):
//   ① 🎯 the window: 5 tabs · «🎯 المؤشرات» = the tables (v3.36.73): «🌐 السوق» + a table per coin · ranked by the lowest % we trust ·
//     «قيد الاختبار» · ⏸ per row · a row opens to its meanings
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
  // ① 📋 the indicator tables (v3.36.73: «🎯 المؤشرات» = a table for the whole market and one per coin · counted from zero)
  await pg.evaluate(() => openSig('now'));                                     // the old name still opens it
  await pg.waitForFunction(() => document.querySelector('#sg_body .sb-r'), null, { timeout: 20000 }).catch(() => {});
  const w1 = await pg.evaluate(() => ({ h2: (document.querySelector('#modal h2') || {}).textContent || '', tabs: [...document.querySelectorAll('#sg_tabs button')].map(b => b.textContent),
    tab: SGTAB, sb: [...document.querySelectorAll('#sg_body .sb-tabs button')].map(b => b.textContent), on: (document.querySelector('#sg_body .sb-tabs button.on') || {}).textContent || '',
    rows: document.querySelectorAll('#sg_body .sb-r').length, top: (document.querySelector('#sg_body .sb-top') || {}).textContent || '' }));
  ok(`① 🧠 one window «${w1.h2}» · tabs ${w1.tabs.join(' | ')} — «now» opens «🎯 المؤشرات»`, w1.h2.startsWith('📊 المؤشرات — المحلل') && w1.tab === 'ind'
     && w1.tabs.join('|') === '🧠 المحلل|🎯 المؤشرات|📚 المجموعات|📜 السجل|⚙️ الإشعارات', w1);
  ok(`① the tables: «${w1.sb.join(' · ')}» — «🌐 السوق» first and open · its 70 rows · «${w1.top.replace(/\s+/g, ' ').trim().slice(0, 90)}…»`,
     w1.sb[0] === '🌐 السوق' && w1.on === '🌐 السوق' && w1.sb.includes('SOL') && w1.sb.includes('XRP') && w1.rows === 70 && w1.top.includes('جدول السوق كله')
     && w1.top.includes('العدّ بدأ'), w1);
  await pg.evaluate(() => sbLoad('SOL-USDT'));
  await pg.waitForFunction(() => SBV && SBV.s === 'SOL-USDT' && document.querySelector('#sg_body .sb-r'), null, { timeout: 15000 }).catch(() => {});
  const w2 = await pg.evaluate(() => { const R = [...document.querySelectorAll('#sg_body .sb-r')];
    const secs = [...document.querySelectorAll('#sg_body .sb-sec')].map(x => x.textContent);
    const first = R[0], cells = first ? [...first.querySelectorAll('.sb-cell')].map(c => c.textContent.replace(/\s+/g, ' ').trim()) : [];
    return { on: (document.querySelector('#sg_body .sb-tabs button.on') || {}).textContent || '', order: R.map(r => +r.dataset.n), secs, cells,
      nm: R.map(r => (r.querySelector('.sb-nm b') || {}).textContent || ''), job: first ? (first.querySelector('.sb-job') || {}).textContent : '',
      off: R.filter(r => r.classList.contains('off')).map(r => +r.dataset.n), avg: !!document.querySelector('#sg_body .ind-avg'),
      ten: !!((INDV && INDV.rows) || []).find(r => r.sym === 'SOL-USDT') } });
  J.board = w2.order.slice(0, 6);
  ok(`① SOL's table: the truest first — 20 (40 ✅ · 10 ❌ on 🕓) before 12 (60 · 30 on ⏱) · 5 (3 of 3) stays «قيد الاختبار» · ⏸ 33 at the bottom (${w2.order.slice(0, 4).join(' · ')} … ${w2.order.slice(-2).join(' · ')})`,
     w2.on === 'SOL' && w2.order[0] === 20 && w2.order[1] === 12 && w2.order.indexOf(5) > 1 && w2.order[w2.order.length - 1] === 33 && w2.off.join() === '33'
     && w2.secs.length === 3 && w2.secs[0].includes('لها نتائج كافية') && w2.secs[1].includes('قيد الاختبار') && w2.secs[2].includes('موقوفة'), w2);
  ok(`① each row: its number · plain name (no Latin) · its job («${w2.job}») · ⏱ الآن · 🕓 4 ساعات · 📅 يوم with ✅ ❌ and % («${w2.cells.join(' | ')}»)`,
     w2.nm.length === 70 && w2.nm.every(t => t && !/[A-Za-z]/.test(t)) && w2.job.trim() && w2.cells.length === 3 && w2.cells[0].includes('⏱ الآن')
     && w2.cells[1].includes('🕓 4 ساعات') && w2.cells[1].includes('✅ 40') && w2.cells[1].includes('❌ 10') && w2.cells[1].includes('80%') && w2.cells[2].includes('📅 يوم'), w2);
  ok(`① the coin table keeps «📊 اتجاه المؤشرات الآن» when the ten indicators have SOL (${w2.ten ? 'they have' : 'not in this closed folder'})`, w2.avg === w2.ten, w2);
  await pg.evaluate(() => sbSort('n'));
  await sleep(200);
  ok('① «# الرقم» ⇒ every working row by its number (1 · 2 · 3 …) · no sections', await pg.evaluate(() => [...document.querySelectorAll('#sg_body .sb-r:not(.off)')].slice(0, 3).map(r => +r.dataset.n).join() === '1,2,3'
     && document.querySelectorAll('#sg_body .sb-sec').length === 1), '');
  await pg.evaluate(() => sbSort('best'));
  await pg.evaluate(() => { document.querySelector('#sg_body .sb-r[data-n="12"] .sb-h').click() });
  await sleep(250);
  const w3 = await pg.evaluate(() => (document.querySelector('#sg_body .sb-r[data-n="12"] .sb-det') || {}).textContent || '');
  ok(`① a tap opens the row: both meanings and the technical name («${w3.replace(/\s+/g, ' ').trim().slice(0, 80)}…»)`, w3.includes('⬆️') && w3.includes('⬇️'), w3);
  await pg.evaluate(() => { document.querySelector('#sg_body .sb-r[data-n="7"] .sb-sw').click() });
  await pg.waitForFunction(() => SBV && (SBV.rows.find(r => r.n === 7) || {}).off, null, { timeout: 10000 }).catch(() => {});
  const w4 = await pg.evaluate(() => { const R = [...document.querySelectorAll('#sg_body .sb-r')]; return { last2: R.slice(-2).map(r => +r.dataset.n), sw: (document.querySelector('#sg_body .sb-r[data-n="7"] .sb-sw') || {}).textContent } });
  ok(`① ▶️ → ⏸ turns row 7 off in SOL's table (it sinks to the bottom: ${w4.last2.join(' · ')})`, w4.last2.includes(7) && (w4.sw || '').includes('⏸'), w4);
  J.off7 = true;
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
  ok('⓪ «📋 جدول مؤشرات العملة ←» on a card opens that coin\'s table', await pg.evaluate(() => SGTAB === 'ind' && SBS !== 'MKT' && (document.querySelector('#sg_body .sb-tabs button.on') || {}).textContent !== '🌐 السوق'), '');
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
