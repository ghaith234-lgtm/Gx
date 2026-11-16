// ⚡ v3.36.57 in a real browser — the new DCA+ (the free ladder): the owner (15-11) «انا اتحكم بالجدول البياني في وضع الاوردرات» ·
//   «اقدر اضيفه يدوي لكل اوردر واقدر اضيف عبر الرسم البياني». node ui_dca_plus.js URL DIR [-q]   (DIR = the DCA+ bot's folder · see ui_dca_plus.py)
//   Prints «JSON {...}» lines that ui_dca_plus.py reads (the rows the editor showed before saving / deploying).
const { chromium, devices } = require('playwright');
const URL = process.argv[2], DIR = process.argv[3], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const br = await chromium.launch();
  const errs = [];
  async function open(opt) {
    const ctx = await br.newContext(opt || { viewport: { width: 1280, height: 900 } });
    await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
    const pg = await ctx.newPage();
    pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
    await pg.routeWebSocket(/.*/, () => {});
    await pg.goto(URL, { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length, null, { timeout: 30000 });
    await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
    await pg.waitForTimeout(2500);
    return { ctx, pg };
  }
  // the client point of a price on the editor's chart (x = a fraction of the width)
  async function at(pg, price, fx) {
    return pg.evaluate(([price, fx]) => { let r = PLX.svg.getBoundingClientRect();
      if (r.top < 0 || r.bottom > innerHeight) { PLX.svg.scrollIntoView({ block: 'center' }); r = PLX.svg.getBoundingClientRect() }   // the chart in view first
      return { x: r.left + r.width * fx, y: r.top + PLX.Y(price) / PLX.H * r.height } }, [price, fx]);
  }
  async function drag(pg, a, b) {
    await pg.mouse.move(a.x, a.y); await pg.mouse.down(); await sleep(60);
    for (let i = 1; i <= 8; i++) { await pg.mouse.move(a.x + (b.x - a.x) * i / 8, a.y + (b.y - a.y) * i / 8); await sleep(25) }
    await pg.mouse.up(); await sleep(250);
  }
  const snap = pg => pg.evaluate(() => ({ rows: PLX.rows.map(r => ({ d: +r.d, q: +r.q, x: +r.x })), p: PLX.calc.map(c => +c.p), sel: PLX.sel,
    tr: [...PLX.box.querySelectorAll('.plxtbl tbody tr')].map(tr => ({ cls: tr.className, d: (tr.querySelector('input[data-k="d"]') || {}).value, q: tr.querySelector('input[data-k="q"]').value,
      x: tr.querySelector('input[data-k="x"]').value, dd: !!(tr.querySelector('input[data-k="d"]') || {}).disabled, qd: tr.querySelector('input[data-k="q"]').disabled,
      p: tr.querySelector('[data-c="p"]').textContent, del: !!tr.querySelector('.plxdel') })) }));

  let { ctx, pg } = await open();
  // ① the card
  const c = await pg.evaluate(dir => {
    const el = CARDS.get(dir), b = DATA.bots.find(x => x.dir === dir), dg = DATA.bots.find(x => x.symbol === 'DOGE-USDT'), eg = CARDS.get(dg.dir);
    return { tag: el.querySelector('.dcatag').textContent, btn: el._r.dplus.textContent, shown: el._r.dplus.style.display !== 'none', plus: b.dca && b.dca.plus,
      dtag: eg.querySelector('.dcatag').textContent, dshown: eg._r.dplus.style.display !== 'none' };
  }, DIR);
  ok(`① the DCA+ card: «${c.tag}» · the button «${c.btn}» · the card's data: 6 rows · locked 0–2 · the cycle's base 2000`,
    /⚡ DCA\+ بيعي/.test(c.tag) && c.shown && /✏️ أوامر DCA\+ \(5 أمر أمان\)/.test(c.btn) && c.plus && c.plus.rows.length === 6
    && JSON.stringify(c.plus.locked) === '[0,1,2]' && c.plus.base === 2000 && !c.plus.pending, c);
  ok(`① the normal sell DCA next to it: «${c.dtag}» · no ✏️ button`, /📉 DCA بيعي/.test(c.dtag) && !c.dshown, c);
  const lb = await pg.evaluate(dir => { const svg = CARDS.get(dir)._r.viz.querySelector('svg');
    return [...svg.querySelectorAll('text')].filter(t => /^\d/.test(t.textContent)).map(t => ({ t: t.textContent, x: +t.getBBox().x.toFixed(1) })) }, DIR);
  ok(`① the card's drawing: prices of 1000 and more fit — no label starts outside the frame (${lb.slice(0, 2).map(o => o.t).join(' · ')})`,
    lb.length >= 6 && lb.every(o => o.x >= 0) && lb.some(o => o.t.startsWith('2207')), lb);   // 🔎 v3.36.58 (p98): «2207.9000» was «207.9000»
  // ② 📋 the card's table: the exit % of each row
  const t = await pg.evaluate(async dir => {
    CARDS.get(dir)._r.dtable.click(); await new Promise(r => setTimeout(r, 400));
    const m = document.getElementById('modal'), th = [...m.querySelectorAll('th')].map(x => x.textContent), rows = [...m.querySelectorAll('tbody tr')].map(r => [...r.children].map(td => td.textContent.trim()));
    hideModal(); return { th, rows };
  }, DIR);
  const xc = t.th.findIndex(x => x.startsWith('نسبة'));
  ok('② 📋 the card\'s table has the exit % of every row (0.5 · 0.6 · 0.8 · 0.7 · 0.5 · 0.4%)', xc > 0 && t.rows.map(r => r[xc]).join() === '0.5%,0.6%,0.8%,0.7%,0.5%,0.4%', t);
  // ③ ⚙ the details window
  const dt = await pg.evaluate(async dir => { dcaDetails(botOf(dir)); await new Promise(r => setTimeout(r, 300));
    const m = document.getElementById('modal'), tb = m.querySelectorAll('table.dntbl'); const o = { sec: [...m.querySelectorAll('.dnsec')].map(x => x.textContent).join('|'),
      rows: [...tb[0].querySelectorAll('tbody tr')].map(r => [...r.children].map(td => td.textContent.trim())), hidden: tb[1] && tb[1].style.display === 'none', note: m.textContent.includes('✏️ أوامر DCA+') };
    hideModal(); return o }, DIR);
  ok('③ ⚙ the details window shows the rows (✅ the filled ones) instead of the classic settings · says the orders are edited from ✏️',
    /أوامر DCA\+/.test(dt.sec) && dt.rows.length === 6 && /^✅ الأساسي/.test(dt.rows[0][0]) && /^✅ أمان 2/.test(dt.rows[2][0]) && dt.rows[3][1] === '▲ 2%' && dt.hidden && dt.note, dt);
  // ④ ✏️ the editor on the running bot
  await pg.evaluate(dir => CARDS.get(dir)._r.dplus.click(), DIR);
  await pg.waitForFunction(() => PLX && PLX.cd && PLX.cd.length > 0, null, { timeout: 8000 }).catch(() => {});
  await sleep(300);
  const e0 = await pg.evaluate(() => { const m = document.getElementById('modal'); return { first: m.querySelector('.hwb').firstElementChild.tagName, h2: m.querySelector('h2').textContent,
    cand: PLX.g.querySelectorAll('rect').length, base: PLX.base, cp: PLX.cp, txt: [...PLX.g.querySelectorAll('text')].map(t => t.textContent), sel: PLX.sel, mode: PLX.mode } });
  let s0 = await snap(pg);
  ok(`④ «✏️ أوامر DCA+» opens the editor (rule 14: <h2> first · «${e0.h2}») on the cycle's base 2000 · the coin's candles behind (${e0.cand} shapes) · the price now 2025`,
    e0.first === 'H2' && /أوامر DCA\+/.test(e0.h2) && e0.base === 2000 && e0.cp === 2025 && e0.cand >= 72 && e0.mode === 'edit' && e0.txt.some(x => /⚡ الآن/.test(x)), e0);
  ok('④ the table: 6 orders · base + safety 1–2 ✅ locked (distance and size closed · no ✕) · their exit % open · safety 3–5 open with ✕',
    s0.tr.length === 6 && [0, 1, 2].every(i => /lk/.test(s0.tr[i].cls) && s0.tr[i].qd && (i === 0 || s0.tr[i].dd) && !s0.tr[i].del)
    && [3, 4, 5].every(i => !s0.tr[i].qd && !s0.tr[i].dd && s0.tr[i].del) && s0.tr[3].d === '2' && s0.tr[5].x === '0.4', s0.tr);
  // drag safety 4's line up on the chart
  const p4 = s0.p[4], p5 = s0.p[5];
  let a = await at(pg, p4, 0.25), b = await at(pg, p4 * 1.004, 0.25);
  await drag(pg, a, b);
  let s1 = await snap(pg);
  ok(`④ dragging safety 4's line up on the chart: its price rises (${p4.toFixed(2)} → ${s1.p[4].toFixed(2)}) · safety 5 stays where it was (${s1.p[5].toFixed(2)}) · the table follows (its distance and price cells)`,
    s1.sel === 4 && s1.p[4] > p4 * 1.002 && Math.abs(s1.p[5] - p5) < 0.02 && s1.p[3] === s0.p[3] && s1.tr[4].d !== s0.tr[4].d && s1.tr[4].p !== s0.tr[4].p, { p4, p5, now: s1.p, d: s1.tr.map(x => x.d) });
  // drag a filled order: nothing moves
  a = await at(pg, s1.p[2], 0.25); b = await at(pg, s1.p[2] * 1.003, 0.25);
  await drag(pg, a, b);
  let s2 = await snap(pg);
  ok('④ dragging a filled order (safety 2 ✅): it does not move (only selected)', s2.sel === 2 && s2.p[2] === s1.p[2] && JSON.stringify(s2.rows.slice(0, 3)) === JSON.stringify(s1.rows.slice(0, 3)), s2.p);
  // the size of safety 5: drag its circle to the left
  await pg.evaluate(() => plxSel(5)); await sleep(100);
  const q5 = (await snap(pg)).rows[5].q;
  const hx = await pg.evaluate(() => { const C = PLX.calc, qm = Math.max(...C.map(c => c.q)), r = PLX.svg.getBoundingClientRect();
    return { x: r.left + (640 - 10 - plxLen(C[5].q, qm)) / 640 * r.width, y: r.top + PLX.Y(C[5].p) / PLX.H * r.height, w: r.width } });
  await drag(pg, hx, { x: hx.x - 40, y: hx.y });
  let s3 = await snap(pg);
  ok(`④ dragging safety 5's circle sideways changes its size (${q5} → ${s3.rows[5].q}) · the table's size cell follows · its price stays`,
    s3.rows[5].q > q5 && s3.tr[5].q === String(s3.rows[5].q) && Math.abs(s3.p[5] - s2.p[5]) < 1e-9, { q5, now: s3.rows[5], cell: s3.tr[5].q });
  // the exit % of safety 3 (live): select it, drag its 🎯 line
  await pg.evaluate(() => plxSel(3)); await sleep(100);
  const c3 = await pg.evaluate(() => ({ tgt: PLX.calc[3].tgt, avg: PLX.calc[3].avg, x: PLX.rows[3].x }));
  a = await at(pg, c3.tgt, 0.7); b = await at(pg, c3.avg * (1 - 0.004), 0.7);
  await drag(pg, a, b);
  let s4 = await snap(pg);
  ok(`④ selecting safety 3 and dragging its green 🎯 line: its exit % changes (${c3.x}% → ${s4.rows[3].x}%) · the table's exit cell follows · no price moved`,
    Math.abs(s4.rows[3].x - 0.4) < 0.06 && s4.tr[3].x === String(s4.rows[3].x) && JSON.stringify(s4.p) === JSON.stringify(s3.p), { c3, now: s4.rows[3], cell: s4.tr[3].x });
  // the exit % of a filled order can change (in the table)
  await pg.fill('.plxtbl tbody tr[data-i="1"] input[data-k="x"]', '0.45'); await sleep(150);
  // tap an empty place above the last order: a new order there
  const top = (await snap(pg)).p[5];
  const tp = await at(pg, top * 1.012, 0.3);
  await pg.mouse.click(tp.x, tp.y); await sleep(300);
  let s5 = await snap(pg);
  ok(`④ tapping an empty place above the last order adds safety 6 there (≈ ${(top * 1.012).toFixed(2)}) · selected · the table has 7 rows · a filled row's exit % typed in the table (0.45)`,
    s5.rows.length === 7 && s5.tr.length === 7 && s5.sel === 6 && Math.abs(s5.p[6] / (top * 1.012) - 1) < 0.003 && s5.rows[1].x === 0.45, { n: s5.rows.length, p6: s5.p[6], sel: s5.sel });
  // tapping below the base or between filled orders is refused
  const nb = await pg.evaluate(() => PLX.rows.length);
  const bp = await at(pg, s5.p[1] * 1.001, 0.3);
  await pg.mouse.click(bp.x, bp.y); await sleep(300);
  ok('④ tapping between filled orders adds nothing (the additions go above the last filled order)', (await pg.evaluate(() => PLX.rows.length)) === nb);
  // typing a distance in the table moves the chart (the following orders follow — the distance is from the one before)
  const before = (await snap(pg)).p;
  await pg.fill('.plxtbl tbody tr[data-i="5"] input[data-k="d"]', '3.5'); await sleep(200);
  let s6 = await snap(pg);
  const lab = await pg.evaluate(() => ({ t: [...PLX.g.querySelectorAll('text')].map(t => t.textContent).filter(t => /أمان 5/.test(t)), f: f4(PLX.calc[5].p) }));
  ok('④ typing safety 5\'s distance (3.5%) in the table: its price on the chart moves · the orders after it follow (each is a distance from the one before)',
    Math.abs(s6.p[5] / s6.p[4] - 1.035) < 1e-9 && s6.p[6] > before[6] && lab.t.some(t => t.includes(lab.f)), { p: s6.p, lab });
  // a bad value shows red and the save is refused
  await pg.fill('.plxtbl tbody tr[data-i="4"] input[data-k="q"]', '0'); await sleep(150);
  const bad = await pg.evaluate(() => ({ red: !!PLX.q('warn').querySelector('.plxred'), cls: PLX.box.querySelector('.plxtbl tbody tr[data-i="4"] input[data-k="q"]').classList.contains('bad') }));
  await pg.click('#plx_save'); await sleep(400);
  const still = await pg.evaluate(() => !document.getElementById('mbg').hidden && !!document.querySelector('#plx_save'));
  ok('④ a size of 0 turns red with the reason · 💾 refuses (the window stays open)', bad.red && bad.cls && still, bad);
  await pg.fill('.plxtbl tbody tr[data-i="4"] input[data-k="q"]', '0.06'); await sleep(150);
  // a low exit warns
  await pg.fill('.plxtbl tbody tr[data-i="6"] input[data-k="x"]', '0.1'); await sleep(150);
  const amb = await pg.evaluate(() => (PLX.q('warn').querySelector('.plxamb') || {}).textContent || '');
  ok('④ an exit under 0.20% warns that the bot uses 0.20%', /0\.20%/.test(amb) && /أمان 6/.test(amb), amb);
  await pg.fill('.plxtbl tbody tr[data-i="6"] input[data-k="x"]', '0.3'); await sleep(150);
  // the JS sums = the server's (the deploy preview's) for the same rows
  const cmp = await pg.evaluate(async () => { const rows = plxRows(), base = PLX.base, C = plxCalc(rows, base, false);
    const r = await api('/api/dca_preview', { dca_type: 'dca_plus', plus_rows: JSON.stringify(rows), base_price: base, symbol: 'ETH-USDT' });
    const S = r.rows || []; let worst = 0;
    S.forEach((s, i) => { const c = C[i]; worst = Math.max(worst, Math.abs(s.price - c.p) / c.p, Math.abs(s.avg - c.avg) / c.avg, Math.abs(s.target - c.tgt) / c.tgt, Math.abs(s.exit_profit - c.prof) / 1e-2) });   // the server rounds the profit to 6 decimals
    return { n: S.length, m: C.length, worst } });
  ok(`④ the editor's numbers = the server's (the engine's sums) for the same rows (worst difference ${cmp.worst.toExponential(1)})`, cmp.n === 7 && cmp.m === 7 && cmp.worst < 1e-4, cmp);
  s6 = await snap(pg);
  console.log('JSON ' + JSON.stringify({ edit_rows: s6.rows.map((r, i) => ({ d: i ? r.d : 0, q: r.q, x: r.x })) }));
  await pg.click('#plx_save'); await sleep(1200);
  const af = await pg.evaluate(dir => ({ open: !document.getElementById('mbg').hidden && !!document.querySelector('#plx_save'), btn: CARDS.get(dir)._r.dplus.textContent, toast: (document.querySelector('.toast') || {}).textContent || '' }), DIR);
  ok(`④ 💾 saved: the window closes · the card says «${af.btn}» (the edit waits for the bot)`, !af.open && /ينتظر البوت/.test(af.btn), af);
  // ⑤ the deploy form
  await pg.evaluate(() => document.getElementById('bDcap').click()); await sleep(500);     // ⚡ v3.36.59: its own button on the main bar
  await pg.selectOption('#dn_type', 'dca_plus'); await sleep(400);
  const f0 = await pg.evaluate(() => ({ hid: ['dn_base', 'dn_avg', 'dn_dev', 'dn_step', 'dn_size', 'dn_n', 'dn_tp'].every(id => document.getElementById(id).closest('.fld').style.display === 'none'),
    shown: ['dn_sym', 'dn_bp', 'dn_ex', 'dn_wait', 'dn_wallet'].every(id => document.getElementById(id).closest('.fld').style.display !== 'none'),
    ed: !!document.querySelector('#dn_preview .plx'), rows: PLX && PLX.rows.length, desc: document.getElementById('dn_desc').textContent }));
  ok('⑤ the deploy form: «⚡ DCA+ بيعي» hides the classic fields (sizes · distance · multipliers · count · target) and puts the editor in the preview\'s place (6 rows to start)',
    f0.hid && f0.shown && f0.ed && f0.rows === 6 && /DCA\+/.test(f0.desc), f0);
  await pg.fill('#dn_sym', 'SOL-USDT');
  await pg.waitForFunction(() => PLX && PLX.cd && PLX.cd.length > 0, null, { timeout: 8000 }).catch(() => {});
  await sleep(300);
  const f1 = await pg.evaluate(() => ({ bp: document.getElementById('dn_bp').value, base: PLX.base, cd: PLX.cd.length, last: PLX.cd[PLX.cd.length - 1][4] }));
  ok(`⑤ typing the symbol loads its candles and the preview price follows the last close (${f1.bp})`, f1.cd > 100 && +f1.bp === f1.last && f1.base === f1.last, f1);
  // the quick fill
  await pg.evaluate(() => { PLX.box.querySelector('details.plxfill').open = true });
  const fill = { n: '8', d1: '0.8', dg: '0.4', q0: '2', q1: '2', qm: '1.4', x0: '0.6', x1: '0.25' };
  for (const k in fill) await pg.fill(`#dn_preview [data-f="${k}"]`, fill[k]);
  await pg.click('#dn_preview .plxfill button.primary'); await sleep(300);
  let g0 = await snap(pg);
  ok('⑤ ⚡ the quick fill: 8 safety orders · distances 0.8% growing 0.4% each · sizes ×1.4 · exit from 0.6% down to 0.25% on the last',
    g0.rows.length === 9 && g0.rows[1].d === 0.8 && Math.abs(g0.rows[8].d - 3.6) < 1e-9 && g0.rows[0].q === 2 && Math.abs(g0.rows[8].q - 2 * Math.pow(1.4, 7)) < 0.01
    && g0.rows[0].x === 0.6 && g0.rows[8].x === 0.25, g0.rows);
  await pg.fill('#dn_preview .plxtbl tbody tr[data-i="3"] input[data-k="q"]', '5'); await sleep(150);
  // a bad row blocks the deploy
  await pg.fill('#dn_preview .plxtbl tbody tr[data-i="2"] input[data-k="d"]', '0'); await sleep(150);
  const nbots = await pg.evaluate(() => DATA.bots.length);
  await pg.click('#dn_go'); await sleep(900);
  ok('⑤ a distance of 0 blocks 🚀 (the form stays · no bot)', (await pg.evaluate(() => !document.getElementById('mbg').hidden && !!document.querySelector('#dn_go'))) && (await pg.evaluate(() => DATA.bots.length)) === nbots);
  await pg.fill('#dn_preview .plxtbl tbody tr[data-i="2"] input[data-k="d"]', '1.2'); await sleep(150);
  // the trial path takes the rows from the form
  const bt = await pg.evaluate(async () => { const body = dcaFormBody(); const r = await api('/api/bt_prep', { kind: 'dca', body });
    return { ok: r.ok, base_def: r.base_def, need: plxRows().reduce((s, x) => s + x.q, 0), msg: r.msg } });
  ok(`⑤ 🧪 the trial path from the form: prepared · its wallet = the coins the rows need (${bt.base_def})`, bt.ok && Math.abs(bt.base_def - bt.need * 1.02) < 1e-6, bt);
  g0 = await snap(pg);
  console.log('JSON ' + JSON.stringify({ deploy_rows: g0.rows.map((r, i) => ({ d: i ? r.d : 0, q: r.q, x: r.x })) }));
  await pg.click('#dn_go'); await sleep(1800);
  const dep = await pg.evaluate(() => ({ open: !document.getElementById('mbg').hidden && !!document.querySelector('#dn_go'), sol: DATA.bots.filter(b => b.symbol === 'SOL-USDT' && b.dca && b.dca.plus).length }));
  ok('⑤ 🚀 deploys: the form closes · a SOL-USDT DCA+ card appears', !dep.open && dep.sol === 1, dep);
  // ⑥ the skins: the same button
  const sk = await pg.evaluate(async dir => { const el = CARDS.get(dir), b = botOf(dir); if (typeof skModel !== 'function') return { none: 1 };
    const M = skModel(el, b, 'dca'); return { menu: (M.menu || []).filter(Boolean).map(x => x.t || x.text || ''), chips: M.chips || '' } }, DIR).catch(e => ({ err: String(e) }));
  ok('⑥ the card looks (C · B · OKX): «✏️ أوامر DCA+» in the menu and its state among the chips', sk.none || (sk.menu.some(t => /أوامر DCA\+/.test(t)) && /أوامر DCA\+|تعديل الأوامر/.test(sk.chips)), sk);
  // ⑦ 📖 the tutorial: the DCA+ tab
  await pg.evaluate(() => { openDeployDca('plus') }); await sleep(400);
  await pg.selectOption('#dn_type', 'dca_plus'); await sleep(200);
  const tu = await pg.evaluate(async () => { tutQ(null, 'dcap'); await new Promise(r => setTimeout(r, 400)); const m = document.getElementById('modal');
    return { txt: (m.querySelector('.tuthwb') || m).textContent } });
  ok('⑦ 📖 the DCA+ form\'s tutorial («📖 شرح DCA+») opens on the DCA+ البيعي tab (its idea · the ✏️ button explained)', /DCA\+ البيعي/.test(tu.txt) && /✏️ أوامر DCA\+/.test(tu.txt) && /أعمق أمر/.test(tu.txt), tu.txt.slice(0, 300));
  await pg.evaluate(() => hideModal());
  ok(`no page error on the computer (${errs.length})`, errs.length === 0, errs);
  await ctx.close();
  // ⑧ the phone
  const e2 = errs.length;
  ({ ctx, pg } = await open({ ...devices['iPhone 13'] }));
  await pg.evaluate(dir => dcaPlusEdit(botOf(dir)), DIR); await sleep(700);
  const ph = await pg.evaluate(() => { const r = PLX.svg.getBoundingClientRect(); return { k: PLX.k, H: PLX.H, w: r.width, sw: document.documentElement.scrollWidth, iw: innerWidth,
    fs: +((PLX.g.querySelector('text') || {}).getAttribute ? PLX.g.querySelector('text').getAttribute('font-size') : 0) } });
  ok(`⑧ the phone: the chart fits the width (${Math.round(ph.w)}px) · taller (${ph.H}) · its text scaled up (font ${ph.fs.toFixed(1)} units ≈ ${(ph.fs * ph.w / 640).toFixed(1)}px) · no sideways page scroll`,
    ph.w <= ph.iw && ph.H === 560 && ph.fs * ph.w / 640 >= 9 && ph.sw <= ph.iw + 1, ph);
  const q0 = await pg.evaluate(() => ({ p: PLX.calc[4].p }));
  const t1 = await at(pg, q0.p, 0.25), t2 = await at(pg, q0.p * 1.003, 0.25);
  await pg.touchscreen.tap(t1.x, t1.y); await sleep(150);
  await drag(pg, t1, t2);
  const q1 = await pg.evaluate(() => ({ p: PLX.calc[4].p, sel: PLX.sel }));
  ok('⑧ on the phone an order is selected and dragged with the finger (pointer events)', q1.sel === 4 && q1.p > q0.p, { q0, q1 });
  ok(`no page error on the phone (${errs.length - e2})`, errs.length === e2, errs.slice(e2));
  await ctx.close();
  await br.close();
  console.log((res.every(Boolean) ? '✅' : '❌') + ` ui_dca_plus.js: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_dca_plus.js crashed: ' + String(e && e.stack || e).slice(0, 1500)); process.exit(1) });
