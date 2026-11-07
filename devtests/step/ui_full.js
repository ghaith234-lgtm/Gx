// 🪜🃏 v3.36.20 the card made clear — the browser steps for ui_full.py (only 127.0.0.1 is reachable)
const { chromium } = require('playwright');
const fs = require('fs');
const [URL, TRUTHF] = process.argv.slice(2);
const Q = process.argv.includes('-q');
const T = JSON.parse(fs.readFileSync(TRUTHF, 'utf8'));
const res = [];
function ok(name, cond, det) { res.push(!!cond); if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + JSON.stringify(det).slice(0, 900))) }
(async () => {
  const br = await chromium.launch();
  const pg = await br.newPage({ viewport: { width: 430, height: 900 } });
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.filter(b => b.bot_type === 'grid_step' && b.ri).length === 2, null, { timeout: 60000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(800);
  const X = 'step_xrp', A = 'step_ada';

  // ── ① a sell's tap names its own buy
  const keys = await pg.evaluate(d => [...document.querySelectorAll(`.card[data-dir="${d}"] [data-stl^="s:"]`)].map(x => x.getAttribute('data-stl')), X);
  let pop = '';
  if (keys.length) {
    const el = await pg.$(`.card[data-dir="${X}"] [data-stl="${keys[0]}"]`); await el.click({ force: true }); await pg.waitForTimeout(250);
    pop = await pg.evaluate(() => (document.getElementById('stpop') || {}).innerText || '');
  }
  const [, sj, sk] = (keys[0] || 's:0:1').split(':');
  const bp = T[X].bp[`${sj}:${sk}`];
  ok(`a sell's tap (${keys[0]}): «🛒 شراؤها الخاص: المستوى ${sj}» at its own buy ${bp && bp.toFixed(4)} · published once among the nearest 8 · its pot · no «++»`,
     keys.length === 3 && pop.includes(`شراؤها الخاص: المستوى ${sj}`) && pop.includes((+bp).toFixed(4)) && pop.includes('أقرب 8') && !pop.includes('++'), { keys, pop });
  await pg.evaluate(() => { const p = document.getElementById('stpop'); if (p) p.style.display = 'none' });
  const bk = await pg.evaluate(d => { const e = document.querySelector(`.card[data-dir="${d}"] [data-stl^="b:"]`); return e && e.getAttribute('data-stl') }, X);
  if (bk) { const el = await pg.$(`.card[data-dir="${X}"] [data-stl="${bk}"]`); await el.click({ force: true }); await pg.waitForTimeout(250) }
  const popb = await pg.evaluate(() => (document.getElementById('stpop') || {}).innerText || '');
  ok("a buy level's tap: its own sells «+0.45% · +0.60% · +0.75% فوقه» and every part (published / memory)",
     popb.includes('بيعاته الخاصة +0.45% · +0.60% · +0.75% فوقه') && (popb.match(/الجزء \d\/3/g) || []).length === 3, popb);
  await pg.evaluate(() => { const p = document.getElementById('stpop'); if (p) p.style.display = 'none' });

  // ── ② «🪜 السلم» = the full ladder by level
  await pg.evaluate(d => openLadder(d), X); await pg.waitForTimeout(900);
  let m = await pg.evaluate(() => document.getElementById('modal').innerText);
  const t = T[X];
  ok("«🪜 السلم» for 🪜 opens the full ladder by level: each level = its fixed buy + its own 3 sells (+0.45 · +0.60 · +0.75%) · the counts = the engine's slots",
     m.includes('🪜 السلّم الكامل') && m.includes('3 بيعات خاصة بيه: +0.45% · +0.60% · +0.75%')
     && m.includes(`على المنصة ${t.pb} شراء · ${t.ps} بيع`) && m.includes(`بالذاكرة ${t.mb} شراء · ${t.ms} بيع`), { m: m.slice(0, 600), t });
  await pg.evaluate(d => stFullDraw(d, 'all'), X); await pg.waitForTimeout(200);
  m = await pg.evaluate(() => document.getElementById('modal').innerText);
  const nLv = (m.match(/🛒 المستوى -?\d+ — شراء/g) || []).length, nParts = (m.match(/الجزء \d+\/3/g) || []).length;
  ok(`… «الكل»: every level (${t.levels}) and every part (${t.slots}) — the far ones in memory too · the price bar in its place`,
     nLv === t.levels && nParts === t.slots && m.includes('السعر الآن') && m.includes('بالذاكرة'), { nLv, nParts, t: { levels: t.levels, slots: t.slots } });
  await pg.evaluate(() => hideModal());

  const riOrder = () => pg.evaluate(() => {          // 💠↕️ the rows of «💠 سلّم الإعادة» as shown: [buy, sell] — coins table · buys table
    const T = [...document.querySelectorAll('#modal table')], num = e => parseFloat(String(e ? e.textContent : '').replace(/,/g, '')) || 0;
    const rd = t => [...t.querySelectorAll('tbody tr')].map(r => { const td = r.querySelectorAll('td'); return [num(td[0].querySelector('b') || td[0]), num(td[1])] });
    return { s: T[0] ? rd(T[0]) : [], b: T[1] ? rd(T[1]) : [] } });
  const desc = a => a.every((v, i) => !i || v <= a[i - 1] + 1e-12);
  // ── ③ «💠 سلّم الإعادة»: one page · below the price reachable · only with reinvest · small amounts in full
  await pg.evaluate(d => openReinvestLadder(d), X); await pg.waitForTimeout(500);
  const ri = await pg.evaluate(() => { const M = document.getElementById('modal');
    const box = [...M.querySelectorAll('div')].some(x => x.style.maxHeight === '56vh');
    const below = document.getElementById('riBelow');
    return { box, below: !!below, txt: M.innerText, scrollable: M.scrollHeight > M.clientHeight } });
  await pg.evaluate(() => document.querySelector('#modal button[onclick*="riBelow"]').click()); await pg.waitForTimeout(300);
  const vis = await pg.evaluate(() => { const M = document.getElementById('modal'), r = document.getElementById('riBelow').getBoundingClientRect(), mr = M.getBoundingClientRect();
    return r.top >= mr.top - 2 && r.top < mr.top + 80 });
  ok("«💠 سلّم الإعادة»: one scrolling page (no 56% box) · «🪙 فوق السعر · 💵 تحت السعر · 💠 بيها إعادة» · «⬇️ تحت السعر» brings the buys under the price to the top",
     !ri.box && ri.below && /🪙 فوق السعر 3 · 💵 تحت السعر \d+ · 💠 بيها إعادة 4/.test(ri.txt) && vis, { box: ri.box, vis, head: ri.txt.slice(0, 400) });
  ok("… small amounts in full: level −1's reinvest «+0.0493 · +0.0737 · +0.0996» (was «0.05 · 0.07 · 0.10»)",
     /\+0\.049\d/.test(ri.txt) && /\+0\.073\d/.test(ri.txt) && /\+0\.099\d/.test(ri.txt), ri.txt.slice(0, 1500));
  const o1 = await riOrder();
  ok(`… 💠↕️ the coins table by its SELL price, high to low: the farthest on top, the nearest right above the price bar (${o1.s.map(x => x[1]).join(' · ')}) · `
     + 'the buys table: the highest buy first, right under the price bar', o1.s.length >= 2 && desc(o1.s.map(x => x[1])) && o1.b.length >= 2 && desc(o1.b.map(x => x[0])), o1);
  await pg.evaluate(() => document.querySelector('#modal button[onclick*="RIF"]').click()); await pg.waitForTimeout(300);
  const only = await pg.evaluate(() => document.getElementById('modal').innerText);
  const rowsOnly = (only.match(/🪜 -?\d+ · \d\/3/g) || []);
  ok(`… «💠 اللي بيها إعادة بس»: only the parts that reinvested (${T[X].grown.join(' · ')})`,
     rowsOnly.length === T[X].grown.length, rowsOnly);
  await pg.evaluate(() => document.querySelector('#modal button[onclick*="RIF"]').click());
  await pg.evaluate(() => hideModal());
  const cardRi = await pg.evaluate(d => { const c = document.querySelector(`.card[data-dir="${d}"]`); return c ? c.innerText : '' }, X);
  ok("the card's 💠 row in full for small amounts (0.2225$ — was «0.22$») · a key under the price ruler",
     /0\.222\d\$/.test(cardRi) && cardRi.includes('اللون = الشراء وبيعاته الخاصة'), cardRi.slice(0, 900));

  // ── ④ the big bot: the card's copy is cut · the full ladder and the 💠 screen still get every slot
  const big = await pg.evaluate(d => { const b = DATA.bots.find(x => x.dir === d); return { sl: (b.sl || []).length, far: (b.sl_far || []).length, c: stCount(b), ri: (b.ri.rows || []).length, n: b.ri.n_rows } }, A);
  const ta = T[A];
  ok(`the big bot (${ta.slots} slots): the card carries ${big.sl} rows + ${big.far} levels in short · its counts = the engine's (${ta.pb}+${ta.ps} published · ${ta.mb}+${ta.ms} memory)`,
     big.sl < 400 && big.far > 0 && big.c.pb === ta.pb && big.c.ps === ta.ps && big.c.mb === ta.mb && big.c.ms === ta.ms && big.n === ta.slots && big.ri < ta.slots, { big, ta });
  await pg.evaluate(d => openLadder(d), A); await pg.waitForTimeout(1200);
  await pg.evaluate(d => stFullDraw(d, 'all'), A); await pg.waitForTimeout(300);
  m = await pg.evaluate(() => document.getElementById('modal').innerText);
  const bLv = (m.match(/🛒 المستوى -?\d+ — شراء/g) || []).length, bParts = (m.match(/الجزء \d+\/20/g) || []).length;
  ok(`… «🪜 السلم» loads the full ladder: ${ta.levels} levels · ${ta.slots} parts (+0.30% · +1.30% · +2.30% … +19.30%) · not «from the card»`,
     bLv === ta.levels && bParts === ta.slots && m.includes('+0.30% · +1.30% · +2.30% … +19.30%') && !m.includes('ما وصل السلّم الكامل'), { bLv, bParts });
  await pg.evaluate(() => hideModal());
  await pg.evaluate(d => openReinvestLadder(d), A); await pg.waitForTimeout(1500);
  const rb = await pg.evaluate(() => document.getElementById('modal').innerText);
  const mm = rb.match(/🪙 فوق السعر (\d+) · 💵 تحت السعر (\d+)/);
  ok(`… «💠 سلّم الإعادة» loads every slot (${ta.slots}): above + below = all · the far ones under the price too`,
     mm && (+mm[1]) + (+mm[2]) === ta.slots && !rb.includes('⏳ أجيب الباقي'), mm && mm.slice(1));
  const o2 = await riOrder(), lv2 = new Set(o2.s.map(x => x[0])).size;
  ok(`… 💠↕️ the big bot's coins table (${o2.s.length} parts of ${lv2} levels, their sells overlapping) in sell order, high to low — the nearest `
     + `(${o2.s.length ? o2.s[o2.s.length - 1][1] : '—'}) right above the price bar · its buys the highest first`,
     o2.s.length > 20 && lv2 >= 3 && desc(o2.s.map(x => x[1])) && desc(o2.b.map(x => x[0])), { s: o2.s.slice(0, 30), b: o2.b.slice(0, 10) });
  await pg.evaluate(() => hideModal());

  // ── ⑤ the endpoint: read only · its own folders only
  const api = await pg.evaluate(async () => {
    const g = async q => { try { return await (await fetch('/api/step_ladder?dir=' + encodeURIComponent(q))).json() } catch (e) { return { err: String(e) } } };
    return { none: await g('nope'), up: await g('../etc'), abs: await g('/etc'), ok: await g('step_xrp') } });
  ok('/api/step_ladder: an unknown folder · a path outside the dashboard (../ · /) ⇒ refused · its own 🪜 folder ⇒ every slot (no keys in it)',
     api.none.ok === false && api.up.ok === false && api.abs.ok === false && api.ok.ok === true && api.ok.sl.length === T[X].slots
     && !JSON.stringify(api.ok).includes('FAKE-'), { none: api.none, up: api.up, abs: api.abs, n: api.ok.sl && api.ok.sl.length });
  ok('no page error', !errs.length, errs);
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_full: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ERR', e.message); process.exit(1) });
