// 📈 v3.36.75 «السوق — الآن والمتوقع» in a real browser (run through ui_sig.py — a closed folder: a scan · the market now · the tables · a notice · no network):
//   ① the window: «📈 السوق — الآن والمتوقع» · 5 tabs (🌐 السوق · 🪙 العملات · 📋 المؤشرات · 📜 السجل · ⚙️ الإشعارات) · the old names open the new tabs
//   ② 🌐 the market now in plain words + Bitcoin's range for 4 hours · tomorrow · the week · «كيف أقرأ» says why there is no direction guess
//   ③ 🪙 your coins: two lines each, a tap opens every fact and its three ranges (the price inside)
//   ④ 📋 the tables (v3.36.73): ranked by the lowest % we trust · «قيد الاختبار» · ⏸ per row · a row opens to its meanings
//   ⑤ 📜 the range's live record + the last notices (what reached you) · ⑥ ⚙️ each type 📲 · 👁 · ⛔ by group (🔴 · 🪙 · 🌐 · saved) · your coins · quiet hours · no %
//   ⑦ 🔮 points to the market · ⚙️ has the row · the ticker's panel · a notification tap opens your coins · ⑧ a phone width · no page error
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2], OUT = process.argv[3], SHOTS = process.argv[4] && process.argv[4] !== '-' ? process.argv[4] : '', Q = process.argv.includes('-q');
const res = [], J = {};
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 1200)));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
const LAT = /[A-Za-z]{2,}/;
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
  const H2 = () => pg.evaluate(() => (document.querySelector('#modal h2') || {}).textContent || '');
  // ① the window
  await pg.evaluate(() => openInd());
  await pg.waitForFunction(() => document.querySelector('#sg_body .an-card'), null, { timeout: 20000 }).catch(() => {});
  const w1 = await pg.evaluate(() => ({ h2: (document.querySelector('#modal h2') || {}).textContent || '', tabs: [...document.querySelectorAll('#sg_tabs button')].map(b => b.textContent),
    tab: SGTAB, on: (document.querySelector('#sg_tabs button.on') || {}).textContent || '' }));
  ok(`① one window «${w1.h2}» · tabs ${w1.tabs.join(' | ')} · «🌐 السوق» opens first`, w1.h2 === '📈 السوق — الآن والمتوقع' && w1.tab === 'mkt' && w1.on === '🌐 السوق'
     && w1.tabs.join('|') === '🌐 السوق|🪙 العملات|📋 المؤشرات|📜 السجل|⚙️ الإشعارات', w1);
  const old = [];
  for (const t of ['now', 'an', 'cat']) { await pg.evaluate(t => openSig(t), t); await sleep(250); old.push(await pg.evaluate(() => SGTAB)) }
  ok(`① the old names still open the window: «now» ⇒ ${old[0]} · «an» ⇒ ${old[1]} · «cat» ⇒ ${old[2]}`, old.join() === 'coins,mkt,ind', old);
  // ② 🌐 the market now
  await pg.evaluate(() => sgTab('mkt'));
  await pg.waitForFunction(() => document.querySelector('#sg_body .an-card .an-l'), null, { timeout: 15000 }).catch(() => {});
  const m1 = await pg.evaluate(() => { const C = [...document.querySelectorAll('#sg_body .an-card')];
    return { cards: C.map(c => (c.querySelector('.an-h b') || {}).textContent || ''), lines: [...(C[0] || document).querySelectorAll('.an-l')].map(l => (l.querySelector('span:last-child') || l).textContent.trim()),
      btc: C[1] ? [...C[1].querySelectorAll('.an-rr')].map(r => r.textContent.replace(/\s+/g, ' ').trim()) : [], help: (document.querySelector('#sg_body details.ind-help') || {}).textContent || '' } });
  ok(`② 🌐 «${(m1.lines[0] || '').slice(0, 70)}…» · ${m1.lines.length} lines in plain words (no Latin)`, m1.cards[0] === '🌐 السوق الآن' && m1.lines.length >= 5
     && m1.lines[0].startsWith('اتجاه السوق') && m1.lines.every(t => !LAT.test(t)), m1);
  ok(`② ₿ Bitcoin's range: ${m1.btc.map(t => t.slice(0, 40)).join(' | ')}`, m1.cards[1] === '₿ البيتكوين' && m1.btc.length === 5 && m1.btc[0].includes('الساعات الأربع القادمة')
     && m1.btc[1].includes('غداً') && m1.btc[2].includes('الأسبوع القادم') && m1.btc[3].includes('الشهر القادم') && m1.btc[4].includes('الأشهر الثلاثة القادمة') && m1.btc.every(t => /–/.test(t) && t.includes('±')), m1.btc);
  ok('② «كيف أقرأ هذه النافذة؟»: facts measured from prices · the range held 80–82% · no direction guess (it did not beat chance) · information, no orders',
     m1.help.includes('🔎 الآن') && m1.help.includes('80–82%') && m1.help.includes('لا تخمين للاتجاه') && m1.help.includes('لا تفتح أمراً'), m1.help.slice(0, 200));
  await shot('mkt_now');
  // ③ 🪙 your coins
  await pg.evaluate(() => sgTab('coins'));
  await pg.waitForFunction(() => document.querySelector('#sg_body .an-coin'), null, { timeout: 15000 }).catch(() => {});
  const c1 = await pg.evaluate(() => [...document.querySelectorAll('#sg_body .an-coin')].map(c => ({ s: c.dataset.s, n: c.querySelectorAll('.an-l').length, r: c.querySelectorAll('.an-rr').length })));
  ok(`③ 🪙 a card for each of your coins (${c1.map(c => c.s).join(' · ')}) — closed: two lines, no range`, c1.map(c => c.s).join() === 'XRP-USDT,SOL-USDT' && c1.every(c => c.n === 2 && c.r === 0), c1);
  await pg.evaluate(() => document.querySelector('#sg_body .an-coin[data-s="SOL-USDT"]').click());
  await sleep(300);
  const c2 = await pg.evaluate(() => { const c = document.querySelector('#sg_body .an-coin[data-s="SOL-USDT"]');
    return { open: c.classList.contains('open'), lines: [...c.querySelectorAll('.an-l')].map(l => (l.querySelector('span:last-child') || l).textContent.trim()), rr: [...c.querySelectorAll('.an-rr')].map(r => r.textContent.replace(/\s+/g, ' ').trim()),
      px: (c.querySelector('.an-h .num') || {}).textContent || '' } });
  const pn = t => +String(t).replace(/[^\d.]/g, '');
  const inside = c2.rr.every(t => { const m = t.match(/([\d.,]+)\s*–\s*([\d.,]+)/); return m && pn(m[1]) < pn(c2.px) && pn(c2.px) < pn(m[2]) });
  ok(`③ a tap opens SOL: ${c2.lines.length} facts («${(c2.lines[0] || '').slice(0, 50)}…» · vs Bitcoin · volatility · support/resistance) · three ranges around ${c2.px} (the price inside)`,
     c2.open && c2.lines.length >= 5 && c2.lines[0].startsWith('الاتجاه اليومي') && c2.lines.some(t => t.startsWith('مقابل البيتكوين')) && c2.lines.some(t => t.startsWith('التذبذب'))
     && c2.lines.every(t => !LAT.test(t)) && c2.rr.length === 5 && inside, c2);
  await shot('mkt_coins');
  // ④ 📋 the indicator groups (🧩 v3.36.77)
  await pg.evaluate(() => sgTab('ind'));
  await pg.waitForFunction(() => document.querySelector('#sg_body .gp-g'), null, { timeout: 20000 }).catch(() => {});
  const w2a = await pg.evaluate(() => ({ secs: [...document.querySelectorAll('#sg_body .gp-secs button')].map(b => b.textContent), on: (document.querySelector('#sg_body .gp-secs button.on') || {}).textContent || '',
    chips: [...document.querySelectorAll('#sg_body .sb-tabs button')].map(b => b.textContent), cards: [...document.querySelectorAll('#sg_body .gp-g')].map(g => g.dataset.g),
    cells: [...document.querySelectorAll('#sg_body .gp-g[data-g="c_trend"] .gp-cell')].map(c => c.textContent.replace(/\s+/g, ' ').trim()),
    live: ((document.querySelector('#sg_body .gp-g[data-g="c_trend"] .gp-nw') || {}).textContent || '').replace(/\s+/g, ' ').trim(),
    ch: ((document.querySelector('#sg_body .gp-g[data-g="c_trend"] .ind-sub') || {}).textContent || '').replace(/\s+/g, ' ').trim(),
    job: ((document.querySelector('#sg_body .gp-g[data-g="c_trend"] .gp-nm small') || {}).textContent || '') }));
  ok(`④ 📋 two sub-tabs «${w2a.secs.join(' · ')}» (🪙 open) · «${w2a.chips.join(' · ')}» · ${w2a.cards.length} coin groups · 📈 الاتجاه: «${w2a.job}» · ${w2a.cells.join(' | ')}`,
     w2a.secs.join('|') === '🪙 العملات|🌐 السوق' && w2a.on === '🪙 العملات' && w2a.chips.join('|') === 'كل العملات معاً|XRP|SOL' && w2a.cards.length === 8 && w2a.cards[0] === 'c_trend'
     && w2a.job.includes('الجهة') && w2a.cells.length === 3 && w2a.cells[0].includes('⏱ ساعة') && w2a.cells[1].includes('🕓 4 ساعات') && w2a.cells[1].includes('60%')
     && w2a.cells[1].includes('✅') && w2a.cells[1].includes('العادي 50%') && w2a.cells[2].includes('📅 يوم'), w2a);
  ok(`④ 🔔 what fired now on your coins: «${w2a.live}» · ⭐ «${w2a.ch.slice(0, 80)}»`, w2a.live.includes('SOL') && w2a.live.includes('يُتوقع أن يكمل الصعود') && w2a.ch.startsWith('⭐ الأبطال: 🕓'), w2a);
  await pg.evaluate(() => gpCoin('SOL-USDT'));
  await sleep(250);
  const w2 = await pg.evaluate(() => ({ on: (document.querySelector('#sg_body .sb-tabs button.on') || {}).textContent || '', top: ((document.querySelector('#sg_body .sb-top') || {}).textContent || '').replace(/\s+/g, ' ').trim(),
    cell: ((document.querySelectorAll('#sg_body .gp-g[data-g="c_trend"] .gp-cell')[1]) || {}).textContent.replace(/\s+/g, ' ').trim(), avg: !!document.querySelector('#sg_body .ind-avg'),
    ten: !!((INDV && INDV.rows) || []).find(r => r.sym === 'SOL-USDT') }));
  ok(`④ SOL alone: «${w2.top.slice(0, 60)}» · 🕓 on SOL «${w2.cell}» · «📊 اتجاه المؤشرات الآن» when the ten have SOL (${w2.ten ? 'they have' : 'not in this folder'})`,
     w2.on === 'SOL' && w2.top.includes('SOL') && w2.cell.includes('58%') && w2.cell.includes('من 120') && w2.avg === w2.ten, w2);
  await pg.evaluate(() => document.querySelector('#sg_body .gp-g[data-g="c_trend"] .gp-h').click());
  await sleep(300);
  const w3 = await pg.evaluate(() => { const M = [...document.querySelectorAll('#sg_body .gp-g[data-g="c_trend"] .gp-m')];
    return { n: M.length, frs: [...document.querySelectorAll('#sg_body .gp-g[data-g="c_trend"] .gp-det .sb-tabs button')].map(b => b.textContent), on: (document.querySelector('#sg_body .gp-g[data-g="c_trend"] .gp-det .sb-tabs button.on') || {}).textContent || '',
      champ: M.filter(m => m.classList.contains('s2')).map(m => m.textContent.replace(/\s+/g, ' ').trim()), names: M.map(m => (m.querySelector('.gp-mn') || {}).textContent || ''),
      test: M.filter(m => m.classList.contains('s0')).length } });
  ok(`④ a tap opens the group: «${w3.frs.join(' · ')}» (🕓 open) · ${w3.n} members (indicators + combos) · ⭐ «${(w3.champ[0] || '').slice(0, 70)}» · 🧪 ${w3.test} · plain names (no Latin)`,
     w3.frs.length === 3 && w3.on.includes('🕓') && w3.n >= 18 && w3.champ.length === 1 && w3.champ[0].includes('⭐ بطل') && w3.champ[0].includes('63%') && w3.names.every(t => t && !LAT.test(t)), w3);
  await pg.evaluate(() => gpSec('mkt'));
  await sleep(250);
  const w4 = await pg.evaluate(() => ({ cards: [...document.querySelectorAll('#sg_body .gp-g')].map(g => g.dataset.g), top: ((document.querySelector('#sg_body .sb-top') || {}).textContent || '').replace(/\s+/g, ' ').trim(),
    live: ((document.querySelector('#sg_body .gp-g[data-g="m_trend"] .gp-nw') || {}).textContent || '').replace(/\s+/g, ' ').trim(), chips: document.querySelectorAll('#sg_body > .sb-tabs').length }));
  ok(`④ 🌐 السوق: ${w4.cards.length} groups («${w4.top.slice(0, 50)}…») · 🔔 «${w4.live}» · no coin chips`, w4.cards.length === 7 && w4.cards[0] === 'm_trend' && w4.top.includes('البيتكوين')
     && w4.live.includes('يُتوقع هبوط السوق') && w4.chips === 0, w4);
  await pg.evaluate(() => gpSec('coin'));
  await shot('mkt_groups');
  // ⑤ 📜 the log
  await pg.evaluate(() => sgTab('log'));
  await sleep(400);
  const l1 = await pg.evaluate(() => ({ cards: [...document.querySelectorAll('#sg_body .an-card .an-h b')].map(b => b.textContent), rr: [...document.querySelectorAll('#sg_body .an-card:first-child .an-rr')].map(r => r.textContent.replace(/\s+/g, ' ').trim()),
    txt: (document.querySelector('#sg_body') || {}).textContent || '' }));
  ok(`⑤ 📜 «${l1.cards.join(' · ')}»: the range's record per horizon (${l1.rr.length}) · the target 80% explained · the SOL notice listed with «📲 وصلك»`, l1.cards.join('|') === '📏 صدق المدى المتوقع (حي)|🔔 آخر التنبيهات'
     && l1.rr.length === 5 && l1.txt.includes('الهدف 80%') && l1.txt.includes('SOL') && l1.txt.includes('أكثر من المتوقع') && l1.txt.includes('📲 وصلك'), l1);
  // ⑥ ⚙️ the notifications
  await pg.evaluate(() => sgTab('cfg'));
  await sleep(300);
  const g0 = await pg.evaluate(() => ({ heads: [...document.querySelectorAll('#sg_body .sg-sh')].map(x => x.textContent.replace(/\s+/g, ' ').trim()),
    rows: [...document.querySelectorAll('#sg_body .an-ty')].map(r => r.dataset.k + ':' + ((r.querySelector('.an-seg button.on') || {}).dataset || {}).l),
    btn: [...document.querySelectorAll('#sg_body .an-ty[data-k="vol"] .an-seg button')].map(b => b.textContent.trim()),
    thr: !!document.getElementById('sg_thr'), est: !!document.getElementById('sg_est'), min: !!document.getElementById('sg_min') }));
  const lv = Object.fromEntries(g0.rows.map(x => x.split(':')));
  const grc = await pg.evaluate(() => ((document.querySelector('#sg_body .an-ty[data-k="g_c_trend"] .gp-rc') || {}).textContent || '').trim());
  ok(`⑥ ⚙️ ${g0.heads.slice(0, 5).map(h => h.slice(0, 22)).join(' · ')} — ${g0.rows.length} types (13 facts + 15 groups), each with «${g0.btn.join(' · ')}» · each group with its record («${grc}») · no % setting · no estimate`,
     g0.heads[0].startsWith('🔴 طوارئ') && g0.heads[1].startsWith('🪙 العملة — المجاميع') && g0.heads[2] === '🪙 العملة — حقائق الآن' && g0.heads[3].startsWith('🌐 السوق — المجاميع')
     && g0.heads[4] === '🌐 السوق — حقائق الآن' && g0.rows.length === 28 && g0.btn.join('|') === '📲 فوري|👁 بالنافذة|⛔ متوقف' && grc.includes('🕓 60%') && grc.includes('⏱')
     && ['wave', 'surge', 'bstorm', 'trend', 'lvl', 'out', 'vol', 'mtrend', 'storm', 'g_c_trend', 'g_c_big', 'g_c_rev', 'g_m_trend', 'g_m_shock', 'g_m_vol'].every(k => lv[k] === 'now')
     && ['rs', 'ad', 'season', 'fng', 'g_c_mom', 'g_c_brk', 'g_c_flow', 'g_c_rs', 'g_c_pro', 'g_m_mom', 'g_m_mood', 'g_m_macro', 'g_m_pro'].every(k => lv[k] === 'view') && !('tend' in lv)
     && !g0.thr && !g0.est && !g0.min, g0);
  await pg.evaluate(() => document.querySelector('#sg_body .an-ty[data-k="g_c_mom"] button[data-l="now"]').click());
  await sleep(900);
  ok('⑥ a tap moves the group «⚡ قوة الحركة» to 📲 فوري — saved', await pg.evaluate(() => SGV.cfg.alv.g_c_mom === 'now'), '');
  await pg.evaluate(() => document.querySelector('#sg_body .an-ty[data-k="vol"] button[data-l="view"]').click());
  await sleep(900);
  const g1 = await pg.evaluate(() => ({ vol: SGV.cfg.alv.vol, trend: SGV.cfg.alv.trend, on: ((document.querySelector('#sg_body .an-ty[data-k="vol"] .an-seg button.on') || {}).dataset || {}).l }));
  ok('⑥ a tap moves «📊 حجم تداول غير عادي» to 👁 بالنافذة — saved (the page shows what the server holds) · the others keep theirs', g1.vol === 'view' && g1.trend === 'now' && g1.on === 'view', g1);
  const k0 = await pg.evaluate(() => ({ mine: [...document.querySelectorAll('#sg_coins .sg-cn')].map(b => b.dataset.c), add: !!document.getElementById('sg_cadd'),
    head: (document.querySelector('#sg_coins .sg-sh') || {}).textContent || '' }));
  ok(`⑥ 🪙 «${k0.head.replace(/\s+/g, ' ').trim().slice(0, 60)}» · your coins with ✕ (${k0.mine.join(' · ')}) · «➕ أضف»`,
     k0.mine.join(',') === 'XRP-USDT,SOL-USDT' && k0.add && k0.head.includes('عملات تنبيهاتك'), k0);
  await pg.evaluate(() => { const i = document.getElementById('sg_cadd'); i.value = ' pepe '; sgCoinAdd() });
  await sleep(900);
  const k1 = await pg.evaluate(() => ({ coins: SGV.cfg.coins, chips: [...document.querySelectorAll('#sg_coins .sg-cn')].map(b => b.dataset.c) }));
  ok('⑥ «➕ أضف» any coin by name («pepe» ⇒ PEPE-USDT) — saved and shown with your coins', JSON.stringify(k1.coins) === JSON.stringify(['XRP-USDT', 'SOL-USDT', 'PEPE-USDT'])
     && k1.chips.includes('PEPE-USDT'), k1);
  await pg.evaluate(() => document.querySelector('#sg_coins .sg-cn[data-c="SOL-USDT"]').click());
  await sleep(900);
  const k2 = await pg.evaluate(() => SGV.cfg.coins);
  ok('⑥ ✕ on SOL removes it from your notices (the rest stays)', JSON.stringify(k2) === JSON.stringify(['XRP-USDT', 'PEPE-USDT']), k2);
  await pg.evaluate(() => { const i = document.getElementById('sg_cadd'); i.value = 'BAD COIN!'; sgCoinAdd() });
  await sleep(500);
  ok('⑥ a wrong name is refused with a clear message (nothing saved)', JSON.stringify(await pg.evaluate(() => SGV.cfg.coins)) === JSON.stringify(k2), '');
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#sg_coins button')].find(x => x.textContent.includes('مثل الشريط')); b.click() });
  await sleep(900);
  const k4 = await pg.evaluate(() => ({ c: SGV.cfg.coins, chips: [...document.querySelectorAll('#sg_coins .sg-cn')].map(b => b.dataset.c) }));
  ok('⑥ «↩️ مثل الشريط» ⇒ your coins follow the ticker again (XRP · SOL)', k4.c === null && k4.chips.join(',') === 'XRP-USDT,SOL-USDT', k4);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#sg_body .sg-set')].find(x => ((x.querySelector('.sg-sh') || {}).textContent || '').startsWith('🌙')).querySelector('button'); b.click() });
  await sleep(900);
  const q1 = await pg.evaluate(() => ({ q: SGV.cfg.quiet, sel: !!document.getElementById('sg_q0') }));
  ok('⑥ 🌙 quiet hours on (00:00 – 08:00 by default) with their two hour lists', JSON.stringify(q1.q) === '[0,8]' && q1.sel, q1);
  await shot('mkt_settings');
  // ⑦ 🔮 · ⚙️ · the ticker · a notification tap
  await pg.evaluate(() => openFc());
  await pg.waitForFunction(() => document.querySelector('#fc_body .sg-go'), null, { timeout: 15000 }).catch(() => {});
  const f1 = await pg.evaluate(() => ({ top: (document.querySelector('#fc_body .sg-go') || {}).textContent || '', an: /🧠 (المحلل|ملخص المحلل)/.test((document.querySelector('#fc_body') || {}).textContent || ''),
    btn: [...document.querySelectorAll('#modal .mbtns button')].map(b => b.textContent) }));
  ok(`⑦ 🔮 «${f1.top.replace(/\s+/g, ' ').trim().slice(0, 70)}» on top · no old analyst line («🧠 المحلل») · buttons ${f1.btn.slice(0, 2).join(' · ')}`,
     f1.top.includes('السوق الآن') && !f1.an && f1.btn[0] === '📈 السوق' && f1.btn[1] === '📋 المؤشرات', f1);
  const f2 = await pg.evaluate(() => { const c = [...document.querySelectorAll('#fc_body .fc-c')].find(e => e.innerText.includes('SOL'));
    const rr = c ? [...c.querySelectorAll('.fc-rows .fc-r:not(.fc-hd)')].map(x => x.textContent.replace(/\s+/g, ' ').trim()) : [];
    const sol = ((ANV && ANV.coins) || []).find(x => x.sym === 'SOL-USDT') || {};
    return { old: !!document.querySelector('#fc_body .fc-tdt'), gp: c ? ((c.querySelector('.fc-td') || {}).textContent || '').replace(/\s+/g, ' ').trim() : '', hd: c ? ((c.querySelector('.fc-rows .fc-hd') || {}).textContent || '') : '', rr,
      same: rr.length && sol.rng ? rr[0].includes(fcN(sol.rng['4h'].lo)) && rr[0].includes(fcN(sol.rng['4h'].hi)) : null } });
  ok(`⑦ 🔮 on the same basis: no 🎯 tendency block · SOL's 🧩 group call «${f2.gp.slice(0, 90)}» · SOL's range rows = 📈's numbers (${f2.rr.slice(0, 2).join(' | ')})`,
     !f2.old && f2.gp.startsWith('🧩 📈 🕓 4 ساعات: يُتوقع أن يكمل الصعود') && f2.gp.includes('صدق 63% من 1,000') && f2.hd.includes('بين كم وكم') && f2.rr.length === 5
     && f2.rr[0].includes('الساعات الأربع القادمة') && f2.same !== false, f2);
  if (SHOTS) { await pg.evaluate(() => { const c = [...document.querySelectorAll('#fc_body .fc-c')].find(e => e.innerText.includes('SOL')); if (c) c.click() }); await sleep(400); await shot('mkt_fc') }
  await pg.evaluate(() => document.querySelector('#fc_body .sg-go').click());
  await sleep(500);
  ok('⑦ a tap on it opens 📈 the market on your coins', (await H2()) === '📈 السوق — الآن والمتوقع' && await pg.evaluate(() => SGTAB === 'coins'), '');
  await pg.evaluate(() => { hideModal(); openSettings() });
  await sleep(500);
  const row = await pg.evaluate(() => { const b = [...document.querySelectorAll('.sitem')].find(x => x.textContent.includes('تنبيهات السوق')); return b ? b.textContent.replace(/\s+/g, ' ').trim() : '' });
  ok(`⑦ ⚙️ «${row}» in 🔔 الإشعارات`, row.includes('📈') && row.includes('خارج المدى'), row);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('.sitem')].find(x => x.textContent.includes('تنبيهات السوق')); b.click() });
  await sleep(600);
  ok('⑦ … it opens 📈 on «⚙️ الإشعارات»', await pg.evaluate(() => SGTAB === 'cfg' && !!document.querySelector('#sg_body .an-ty[data-k]')), '');
  await pg.evaluate(() => openTicker());
  await sleep(1200);
  ok('⑦ the ticker\'s settings: «🔔 تنبيهات السوق» with its buttons', await pg.evaluate(() => ((document.getElementById('tk_pxa') || {}).textContent || '').includes('🔔 تنبيهات السوق')), '');
  await pg.evaluate(() => { hideModal(); HGO = 'sig'; holyGoNow() });
  await sleep(600);
  ok('⑦ a notification tap («sig») opens 📈 the market on your coins', (await H2()) === '📈 السوق — الآن والمتوقع' && await pg.evaluate(() => SGTAB === 'coins'), '');
  // ⑧ a phone
  await pg.setViewportSize({ width: 390, height: 844 });
  for (const t of ['mkt', 'coins', 'ind', 'log', 'cfg']) {
    await pg.evaluate(t => sgTab(t), t);
    await sleep(700);
    if (t === 'coins') { await pg.evaluate(() => { const c = document.querySelector('#sg_body .an-coin:not(.open)'); if (c) c.click() }); await sleep(300) }
    const ov = await pg.evaluate(() => { const b = document.getElementById('sg_body'); return { sw: b.scrollWidth, cw: b.clientWidth, doc: document.documentElement.scrollWidth, vw: innerWidth } });
    ok(`⑧ a phone (390): «${t}» does not spill sideways (${ov.sw} ≤ ${ov.cw} · page ${ov.doc} ≤ ${ov.vw})`, ov.sw <= ov.cw + 1 && ov.doc <= ov.vw + 1, ov);
    if (SHOTS && (t === 'mkt' || t === 'coins')) await pg.screenshot({ path: `${SHOTS}/mkt_phone_${t}.png` });
  }
  ok('no page error', !errs.length, errs);
  fs.writeFileSync(OUT, JSON.stringify(J));
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_sig.js ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ crash', e); process.exit(1) });
