// 🪜💠 reinvest on the graded grid's card in a real browser — run through ui_ri.py (the real dashboard + the real engine with
//   reinvest on the mock OKX, paced in real time): the 🔄 chip (no ⚔️) · the «معاد استثماره» row · «💠 سلّم الإعادة» lists every
//   slot with «🪜 j · k/N» · ＋ ⇒ «💉 … المستوى · الجزء» ⇒ the engine applies it (the capital in its pot, the order bigger) ·
//   ➖ ⇒ the capital back · ⚖️ 50% ⇒ the engine says «النسبة صارت 50%» · the deploy form's 💠 box reaches the body · 🔄 off ⇒
//   the engine releases (on = off · «🔄 [تحرير ربح داخلي]») · books = wallet all along · no page error
const { chromium } = require('playwright');
const URL = process.argv[2], SIM = process.argv[3], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
const sim = async () => { const r = await fetch(SIM + '/st.json'); return r.json() };
async function until(f, ms) { const t0 = Date.now(); let v; while (Date.now() - t0 < ms) { v = await f(); if (v) return v; await new Promise(r => setTimeout(r, 400)) } return v }
(async () => {
  const br = await chromium.launch();
  const ctx = await br.newContext({ viewport: { width: 1440, height: 1000 } });
  await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.removeItem('dash_skin') } catch (e) {} });
  const pg = await ctx.newPage();
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.some(b => b.bot_type === 'grid_step' && b.ri && b.ri.usd > 0), null, { timeout: 60000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  const dir = await pg.evaluate(() => DATA.bots.find(b => b.bot_type === 'grid_step').dir);
  const card = await pg.evaluate(d => {
    const c = document.querySelector(`.card[data-dir="${CSS.escape(d)}"]`); if (!c) return null;
    const chips = [...c.querySelectorAll('.chip')].map(x => x.textContent);
    const btn = c.querySelector('[data-k="rilad"]');
    return { chips, rilad: btn ? getComputedStyle(btn).display : 'none', txt: c.innerText };
  }, dir);
  ok('the card: the 🔄 chip «شغالة» · no ⚔️ · «💠 سلّم الإعادة» shown · the reinvested dollars on the card',
     card && card.chips.some(t => /🔄 إعادة استثمار شغالة/.test(t)) && !card.chips.some(t => /⚔️/.test(t)) && card.rilad !== 'none', card && { chips: card.chips, rilad: card.rilad });
  await pg.evaluate(d => openReinvestLadder(d), dir);
  await pg.waitForTimeout(300);
  const lad = await pg.evaluate(() => { const m = document.querySelector('.modal, #modal, .mdl') || document.body; return m.innerText });
  ok('«💠 سلّم الإعادة»: every slot by its level and part («🪜 -1 · 1/3» …) with ＋ and ➖', /🪜 -1 · 1\/3/.test(lad) && /🪜 -1 · 3\/3/.test(lad) && /＋/.test(lad), lad.slice(0, 600));
  const injBtn = await pg.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /riInject\([^)]*'-1:1'/.test(x.getAttribute('onclick') || '')); if (!b) return false; b.click(); return true });
  await pg.waitForTimeout(300);
  const ih = await pg.evaluate(() => (document.querySelector('#modal h2') || {}).textContent || '');
  ok('＋ on slot -1:1 ⇒ «💉 حقن رأس مال — 🪜 المستوى -1 · الجزء 1/3»', injBtn && /🪜 المستوى -1 · الجزء 1\/3/.test(ih), { injBtn, ih });
  const s0 = await sim();
  const kind = (s0.slots['-1:1'] || {}).side;
  await pg.fill('#i_amt', kind === 'sell' ? '1' : '2');
  await pg.click('#i_go');
  const s1 = await until(async () => { const s = await sim(); return (+(s.rb || {}).inj_total || 0) > 0.5 ? s : null }, 25000);
  ok(`… the engine applied it (the ${kind} side): the capital in its pot · «💉» line · books = wallet`,
     s1 && s1.lines.some(l => /^💉 \[حقن\] الخانة -1:1/.test(l)) && !s1.errors.length, s1 ? { inj: s1.rb.inj_total, lines: s1.lines.slice(0, 4), err: s1.errors } : s0.lines.slice(0, 5));
  await pg.waitForFunction(() => { const r = (DATA.bots.find(x => x.bot_type === 'grid_step').ri.rows || []).find(r => r.kk === '-1:1'); return r && r.j > 0 },
                           null, { timeout: 15000 });          // (the card refreshes every second: the capital shows there first)
  await pg.evaluate(d => openReinvestLadder(d), dir);
  await pg.waitForTimeout(300);
  await pg.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /riWithdraw\([^)]*'-1:1'/.test(x.getAttribute('onclick') || '')); if (b) b.click() });
  await pg.waitForTimeout(300);
  const wh = await pg.evaluate(() => (document.querySelector('#modal h2') || {}).textContent || '');
  const capAll = await pg.evaluate(() => {               // «الكل» of the capital, in whichever box it is (coins inside the order · dollars)
    [...document.querySelectorAll('#modal button')].filter(x => /#w_cap(d)?'/.test(x.getAttribute('onclick') || '')).forEach(b => b.click());
    return (+(($('#w_cap') || {}).value || 0)) * (+(DATA.bots.find(x => x.bot_type === 'grid_step').ri.rows.find(r => r.kk === '-1:1') || {}).p || 1)
         * ((((DATA.bots.find(x => x.bot_type === 'grid_step').ri.rows.find(r => r.kk === '-1:1') || {}).s) === 'sell') ? 1 : 0)
         + (+(($('#w_cap') || {}).value || 0)) * ((((DATA.bots.find(x => x.bot_type === 'grid_step').ri.rows.find(r => r.kk === '-1:1') || {}).s) === 'sell') ? 0 : 1)
         + (+(($('#w_capd') || {}).value || 0)) });
  await pg.click('#w_go');
  const s2 = await until(async () => { const s = await sim(); return (s.lines || []).some(l => /^➖ \[سحب\] الخانة -1:1/.test(l)) ? s : null }, 25000);
  ok('➖ on slot -1:1 («🪜 المستوى -1 · الجزء 1/3») · all the capital ⇒ back to the wallet · «➖» line · books = wallet',
     /🪜 المستوى -1 · الجزء 1\/3/.test(wh) && +capAll > 0 && s2 && (+s2.rb.inj_total || 0) < (+s1.rb.inj_total || 0) - 0.5 * (+capAll) && !s2.errors.length,
     { wh, capAll, inj: s2 && s2.rb.inj_total, lines: s2 && s2.lines.slice(0, 4), row: await pg.evaluate(() => DATA.bots.find(x => x.bot_type === 'grid_step').ri.rows.find(r => r.kk === '-1:1')),
       slot: (await sim()).slots['-1:1'], lv: ((await sim()).rb.levels || {})['-1:1'] });
  await pg.evaluate(d => riSetPct(d, 100), dir);
  await pg.waitForTimeout(300);
  await pg.fill('#p_val', '50');
  await pg.click('#p_go');
  const s3 = await until(async () => { const s = await sim(); return (s.lines || []).some(l => /النسبة صارت 50%/.test(l)) ? s : null }, 25000);
  ok('⚖️ 50% ⇒ the engine: «⚖️ … النسبة صارت 50% للأمر نفسه · 50% ربح عادي» (live, no restart)', s3 && s3.rb.pct === 50, s3 && s3.lines.slice(0, 3));
  const fb = await pg.evaluate(async () => {
    await openDeployStep({}); const c = $('#st_ri'); if (!c) return null;
    const vis0 = getComputedStyle($('#st_fri')).display; c.checked = true; stRiSync(); $('#st_rip').value = '70';
    const b = stBody(); hideModal(); return { vis0, vis1: 'shown', ri: b.reinvest, pct: b.reinvest_pct };
  });
  ok('the deploy form: «💠 إعادة الاستثمار من البداية» · its % box shows when checked · both reach the body', fb && fb.vis0 === 'none' && fb.ri === true && fb.pct === '70', fb);
  await pg.evaluate(d => askReinvest(d), dir);
  await pg.waitForTimeout(300);
  const ah = await pg.evaluate(() => document.body.innerText.includes('تتصغّر فوراً'));
  await pg.click('#cf_y');
  const s4 = await until(async () => { const s = await sim(); return s.rb && s.rb.on === false && (s.lines || []).some(l => /^🔄 \[تحرير ربح داخلي\]/.test(l)) ? s : null }, 30000);
  ok('🔄 off (its dialog: the published orders shrink now) ⇒ the engine releases: on = off · «🔄 [تحرير ربح داخلي]» · books = wallet',
     ah && s4 && !s4.errors.length, { ah, rb: s4 && { on: s4.rb.on, rel: s4.rb.released }, lines: s4 && s4.lines.slice(0, 3) });
  await pg.waitForFunction(d => { const b = DATA.bots.find(x => x.dir === d); return b && b.ri && !b.ri.on && !b.ri.cfg_on && b.ri.usd < 1e-6 }, dir,
                           { timeout: 15000 }).catch(() => null);      // (the card refreshes from the bot's file every second or so)
  const after = await pg.evaluate(d => { const b = DATA.bots.find(x => x.dir === d); return b && b.ri && { on: b.ri.on, cfg_on: b.ri.cfg_on, usd: b.ri.usd } }, dir);
  const s5 = await sim();
  ok('… the card follows: 🔄 off · nothing held in the orders any more', after && !after.on && !after.cfg_on && after.usd < 1e-6,
     { after, engine: { on: s5.rb.on, unwind: s5.rb.unwind, released: s5.rb.released, rel_open: s5.rb.rel_open, lines: s5.lines.slice(0, 6) } });
  ok('no page error', errs.length === 0, errs.slice(0, 3));
  await br.close();
  console.log(`${res.filter(Boolean).length} ok · ${res.length - res.filter(Boolean).length} failed`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ crash ' + e); process.exit(1); });
