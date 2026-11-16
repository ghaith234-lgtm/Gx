// ⚡ v3.36.59 in a real browser — «⚡ DCA+» on its own button with the new DCA+ الشرائي (p103). The owner (16-11): «Dca + خليه زر
//   بالخارج وضيف معه الشرائية وسويلهم تيست وخليلهم زر شرح». node ui_dca_plus_buy.js URL [-q]   (see ui_dca_plus_buy.py)
//   Prints «JSON {...}» lines that ui_dca_plus_buy.py reads (the rows the editor showed before deploying).
const { chromium, devices } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
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
    await pg.evaluate(() => { const o = window.toast; window.__toasts = []; window.toast = (m, k) => { window.__toasts.push(String(m)); return o(m, k) } });
    return { ctx, pg };
  }
  async function at(pg, price, fx) {
    return pg.evaluate(([price, fx]) => { let r = PLX.svg.getBoundingClientRect();
      if (r.top < 0 || r.bottom > innerHeight) { PLX.svg.scrollIntoView({ block: 'center' }); r = PLX.svg.getBoundingClientRect() }
      return { x: r.left + r.width * fx, y: r.top + PLX.Y(price) / PLX.H * r.height } }, [price, fx]);
  }
  async function drag(pg, a, b) {
    await pg.mouse.move(a.x, a.y); await pg.mouse.down(); await sleep(60);
    for (let i = 1; i <= 8; i++) { await pg.mouse.move(a.x + (b.x - a.x) * i / 8, a.y + (b.y - a.y) * i / 8); await sleep(25) }
    await pg.mouse.up(); await sleep(250);
  }
  const calc = pg => pg.evaluate(() => ({ rows: PLX.rows.map(r => ({ d: +r.d, q: +r.q, x: +r.x })), c: PLX.calc.map(c => ({ p: c.p, avg: c.avg, tgt: c.tgt, prof: c.prof, cv: c.cv, gap: c.gap })),
    buy: PLX.buy, sel: PLX.sel }));

  let { ctx, pg } = await open();
  // ① the main bar: its own button · the two forms
  const nav = await pg.evaluate(() => { const bs = [...document.querySelectorAll('#navAct .grp button')].map(b => b.textContent.trim());
    return { bs, i: bs.indexOf('⚡ DCA+'), j: bs.indexOf('📉 نشر DCA') } });
  ok(`① the main bar: «⚡ DCA+» right after «📉 نشر DCA» (${nav.bs.slice(0, 4).join(' · ')})`, nav.i > 0 && nav.i === nav.j + 1, nav);
  await pg.evaluate(() => openDeployDca()); await sleep(500);
  const cls = await pg.evaluate(() => ({ h2: document.querySelector('#modal h2').textContent, o: [...document.querySelectorAll('#dn_type option')].map(o => o.value) }));
  ok(`① «📉 نشر DCA» keeps the sell and the buy DCA only (${cls.o.join(' · ')}) — DCA+ moved to its own button`,
    JSON.stringify(cls.o) === '["dca","dca_buy"]' && /نشر بوت DCA/.test(cls.h2) && !/DCA\+/.test(cls.h2), cls);
  await pg.evaluate(() => hideModal()); await sleep(300);
  await pg.evaluate(() => document.getElementById('bDcap').click()); await sleep(700);
  const pf = await pg.evaluate(() => { const m = document.getElementById('modal');
    return { first: m.querySelector('.hwb').firstElementChild.tagName, h2: m.querySelector('h2').textContent, o: [...document.querySelectorAll('#dn_type option')].map(o => o.value),
      tut: (m.querySelector('h2 .tutx') || {}).textContent || '', bt: !!m.querySelector('#dn_bt'), demo: !!m.querySelector('#dn_demo'), ed: !!m.querySelector('#dn_preview .plx'),
      hid: ['dn_base', 'dn_avg', 'dn_dev', 'dn_step', 'dn_size', 'dn_n', 'dn_tp'].every(id => document.getElementById(id).closest('.fld').style.display === 'none') } });
  ok(`① «⚡ DCA+» opens its own form (rule 14: <h2> first · «${pf.h2.trim()}»): the two types (${pf.o.join(' · ')}) · the editor in place of the classic fields · «${pf.tut}» beside ✕ · 🧪 trial · 🧪 demo`,
    pf.first === 'H2' && /نشر بوت DCA\+/.test(pf.h2) && JSON.stringify(pf.o) === '["dca_plus","dca_plus_buy"]' && pf.ed && pf.hid && /شرح DCA\+/.test(pf.tut) && pf.bt && pf.demo, pf);
  // ② the buy type: the ladder goes DOWN · the exit ABOVE · dollars
  await pg.fill('#dn_bp', '100'); await sleep(200);
  const sell0 = await calc(pg);
  await pg.selectOption('#dn_type', 'dca_plus_buy'); await sleep(500);
  let b0 = await calc(pg);
  const head = await pg.evaluate(() => ({ th: [...PLX.box.querySelectorAll('.plxtbl th')].map(t => t.textContent).join(' | '), sum: PLX.q('sum').textContent,
    desc: document.getElementById('dn_desc').textContent, hint: PLX.box.querySelector('.plxhint').textContent }));
  ok('② «⚡ DCA+ شرائي»: the same rows (kept from the sell type) · the editor turns to the buy side · its text says so',
    b0.buy === true && sell0.buy === false && JSON.stringify(b0.rows) === JSON.stringify(sell0.rows) && /الشرائي/.test(head.desc) && /تحت السعر/.test(head.hint), { b0: b0.rows, sell0: sell0.rows, head });
  const down = b0.c.every((c, i) => i === 0 || c.p < b0.c[i - 1].p), above = b0.c.every(c => c.tgt > c.avg);
  ok(`② each order is UNDER the one before (${b0.c.map(c => c.p.toFixed(2)).join(' › ')}) · every exit ABOVE its average · a dollar profit on every row`,
    down && above && b0.c.every(c => c.prof > 0) && /يحتاج صعوداً/.test(head.th) && /💎ربحصافٍ\$/.test(head.th.replace(/\s/g, '')), { c: b0.c, th: head.th });
  const need = b0.c[b0.c.length - 1].cv;
  ok(`② the summary: «💵 الدولار لو نُفّذ الكل» = every order × its price (${need.toFixed(2)}$) · the coverage ▼ · the rise it needs ▲`,
    head.sum.includes('💵 الدولار لو نُفّذ الكل') && head.sum.includes(need.toFixed(2) + '$') && /مدى النزول/.test(head.sum) && /يحتاج صعوداً/.test(head.sum), head.sum);
  const srv = await pg.evaluate(async () => { const r = await api('/api/dca_preview', { dca_type: 'dca_plus_buy', plus_rows: JSON.stringify(plxRows()), base_price: 100, symbol: 'SOL-USDT' });
    return { rows: (r.rows || r.table || (r.data && r.data.rows) || []).map(x => ({ p: x.price, t: x.target, pr: x.exit_profit })), raw: Object.keys(r || {}) } });
  const same = srv.rows.length === b0.c.length && srv.rows.every((x, i) => Math.abs(x.p - b0.c[i].p) < 1e-6 && Math.abs(x.t - b0.c[i].tgt) < 1e-6 && Math.abs(x.pr - b0.c[i].prof) < 1e-4);
  ok(`② the page's sums = the server's (the engine's) for every row (${srv.rows.length} rows · price · exit · dollar profit)`, same, { srv: srv.rows.slice(0, 3), page: b0.c.slice(0, 3), raw: srv.raw });
  // ③ the chart: drag · exit · tap to add · tap above the base refused
  const i3 = 3, p3 = b0.c[i3].p, p4 = b0.c[i3 + 1].p, p2 = b0.c[i3 - 1].p;
  await pg.evaluate(i => { PLX.sel = i; plxSoft() }, i3);
  let a = await at(pg, p3, 0.6), b = await at(pg, p3 * 0.993, 0.6);
  await drag(pg, a, b);
  let b1 = await calc(pg);
  ok(`③ drag order ${i3} down on the chart: its price falls (${p3.toFixed(3)} → ${b1.c[i3].p.toFixed(3)}) · the one after stays in its place (${b1.c[i3 + 1].p.toFixed(3)}) · the one before too`,
    b1.c[i3].p < p3 - 1e-6 && Math.abs(b1.c[i3 + 1].p / p4 - 1) < 1e-5 && Math.abs(b1.c[i3 - 1].p - p2) < 1e-9, { p3, p4, n: b1.c.slice(i3 - 1, i3 + 2) });   // the next one's distance is kept to 4 decimals of a percent
  a = await at(pg, b1.c[i3].p, 0.6); b = await at(pg, p2 * 1.02, 0.6);
  await drag(pg, a, b);
  b1 = await calc(pg);
  ok(`③ dragged above the order before it: it stops just under it (${b1.c[i3].p.toFixed(4)} < ${p2.toFixed(4)}) — the ladder keeps its order`,
    b1.c[i3].p < p2 && b1.c[i3].p > p2 * 0.998 && b1.rows[i3].d > 0, b1.c.slice(i3 - 1, i3 + 1));
  const x0 = b1.rows[i3].x, t0 = b1.c[i3].tgt;
  a = await at(pg, t0, 0.46); b = await at(pg, t0 * 1.004, 0.46);
  await drag(pg, a, b);
  b1 = await calc(pg);
  ok(`③ the green 🎯 handle dragged UP: its exit % grows (${x0} → ${b1.rows[i3].x}%) · the exit price above the average follows (${b1.c[i3].tgt.toFixed(3)})`,
    b1.rows[i3].x > x0 && b1.c[i3].tgt > t0 && Math.abs(b1.c[i3].tgt - b1.c[i3].avg * (1 + Math.max(b1.rows[i3].x, 0.2) / 100)) < 1e-9, { x0, x1: b1.rows[i3].x });
  const n0 = b1.rows.length, last = b1.c[n0 - 1].p, tapP = last * 0.985;
  const tp = await at(pg, tapP, 0.3);
  await pg.mouse.click(tp.x, tp.y); await sleep(400);
  b1 = await calc(pg);
  ok(`③ a tap UNDER the last order (≈ ${tapP.toFixed(3)}) adds an order there (${n0 - 1} → ${b1.rows.length - 1} safety orders · ${b1.c[b1.rows.length - 1].p.toFixed(3)})`,
    b1.rows.length === n0 + 1 && Math.abs(b1.c[b1.rows.length - 1].p / tapP - 1) < 0.004, b1.c.slice(-2));
  const upP = await pg.evaluate(() => PLX.P(PLX.H * 0.04));          // an empty place near the top — above the base (not on its line)
  const up = await at(pg, upP, 0.3);
  await pg.evaluate(() => { window.__toasts = [] });
  await pg.mouse.click(up.x, up.y); await sleep(400);
  const b2 = await calc(pg), ts = await pg.evaluate(() => window.__toasts.slice());
  ok(`③ a tap ABOVE the base adds nothing: «${ts[0] || ''}»`, b2.rows.length === b1.rows.length && ts.some(t => /الشرائي تحت سعر الأساس/.test(t)), ts);
  // ④ sell ⇄ buy keeps the rows
  await pg.selectOption('#dn_type', 'dca_plus'); await sleep(400);
  const s1 = await calc(pg);
  await pg.selectOption('#dn_type', 'dca_plus_buy'); await sleep(400);
  const b3 = await calc(pg);
  ok('④ switching to «بيعي» and back keeps every row (the sell ladder goes up, the buy one down)', JSON.stringify(s1.rows) === JSON.stringify(b2.rows)
    && JSON.stringify(b3.rows) === JSON.stringify(b2.rows) && s1.buy === false && b3.buy === true && s1.c[1].p > s1.c[0].p && b3.c[1].p < b3.c[0].p, { s1: s1.rows.length, b3: b3.rows.length });
  // ⑤ 🧪 the trial path from the form
  await pg.fill('#dn_sym', 'SOL-USDT'); await sleep(900);
  await pg.fill('#dn_bp', '100'); await sleep(300);
  const tr = await pg.evaluate(async () => { const body = dcaFormBody(); let got = null; const o = window.btOpen; window.btOpen = x => { got = x };
    try { btFromForm('dca') } finally { window.btOpen = o }
    const r = await api('/api/bt_prep', { kind: got && got.kind, body: got && got.body });
    const need = plxCalc(plxRows(), +r.p0, false, true).slice(-1)[0].cv;        // the trial starts from the live price
    return { kind: got && got.kind, type: body.dca_type, ok: r.ok, q: r.quote_def, b: r.base_def, need, p0: r.p0, msg: r.msg } });
  ok(`⑤ «🧪 جرّب على مسار تجريبي»: the trial gets the buy kind (${tr.kind}) with the rows · prepared · its wallet = the dollars of the rows (+3% +1$ · ${tr.q}$)`,
    tr.kind === 'dca_buy' && tr.type === 'dca_plus_buy' && tr.ok && Math.abs(tr.q - (tr.need * 1.03 + 1)) < 0.02 && !tr.b, tr);
  // ⑥ 📖 the tutorial: two tabs, opens on the chosen type
  const tu = await pg.evaluate(async () => { tutQ(null, 'dcap'); await new Promise(r => setTimeout(r, 450)); const w = document.querySelector('#modal .tuthwb') || document.getElementById('modal');
    return { txt: w.textContent, tabs: [...w.querySelectorAll('button')].map(b => b.textContent.trim()).filter(t => /DCA\+/.test(t)) } });
  ok(`⑥ 📖 «شرح DCA+» opens on the chosen type (DCA+ الشرائي) with both tabs (${tu.tabs.join(' · ')}) · the idea · the steps · an example · questions`,
    /DCA\+ الشرائي/.test(tu.txt) && /زائد نسبة خروج أعمق أمر/.test(tu.txt) && /كم دولاراً يحتاج/.test(tu.txt) && tu.tabs.some(t => /البيعي/.test(t)) && tu.tabs.some(t => /الشرائي/.test(t)), tu);
  await pg.evaluate(() => { try { tutBack() } catch (e) {} }); await sleep(300);
  // ⑦ 🚀 deploy
  const rows = (await calc(pg)).rows;
  console.log('JSON ' + JSON.stringify({ deploy_rows: rows.map((r, i) => ({ d: i ? r.d : 0, q: r.q, x: r.x })) }));
  await pg.evaluate(() => { const g = document.getElementById('dn_go'); g.scrollIntoView({ block: 'center' }); g.click() }); await sleep(2200);
  const dep = await pg.evaluate(() => { const b = DATA.bots.find(x => x.symbol === 'SOL-USDT' && x.bot_type === 'dca_buy' && x.dca && x.dca.plus);
    const el = b && CARDS.get(b.dir); return { open: !document.getElementById('mbg').hidden && !!document.querySelector('#dn_go'), dir: b && b.dir,
      tag: el && el.querySelector('.dcatag').textContent, btn: el && el._r.dplus.textContent, shown: el && el._r.dplus.style.display !== 'none' } });
  ok(`⑦ 🚀 deploys: the form closes · a card «${dep.tag}» · its «${dep.btn}»`, !dep.open && dep.dir && /⚡ DCA\+ شرائي/.test(dep.tag || '') && dep.shown && /✏️ أوامر DCA\+/.test(dep.btn || ''), dep);
  console.log('JSON ' + JSON.stringify({ dir: dep.dir }));
  // ⑧ ✏️ the card's editor in the buy direction · the details window
  await pg.evaluate(dir => CARDS.get(dir)._r.dplus.click(), dep.dir); await sleep(700);
  const ed = await pg.evaluate(() => ({ h2: document.querySelector('#modal h2').textContent, buy: PLX && PLX.buy, n: PLX && PLX.rows.length, down: PLX && PLX.calc.every((c, i) => i === 0 || c.p < PLX.calc[i - 1].p) }));
  ok(`⑧ ✏️ on the card opens «${ed.h2}» — the buy direction (each order under the one before) with the deployed rows`, /أوامر DCA\+ الشرائي/.test(ed.h2) && ed.buy === true && ed.n === rows.length && ed.down, ed);
  await pg.evaluate(() => hideModal()); await sleep(300);
  const dt = await pg.evaluate(dir => { dcaDetails(botOf(dir)); const m = document.getElementById('modal'); return m.textContent }, dep.dir); await sleep(300);
  ok('⑧ ⚙ the details window lists the rows going down (▼ · «تحت الذي قبله»)', /تحت الذي قبله/.test(dt) && /▼ \d/.test(dt), dt.slice(0, 400));
  await pg.evaluate(() => hideModal());
  ok(`no page error on the computer (${errs.length})`, errs.length === 0, errs);
  await ctx.close();
  // ⑨ the phone
  const e2 = errs.length;
  ({ ctx, pg } = await open({ ...devices['iPhone 13'] }));
  await pg.evaluate(() => openDeployDca('plus')); await sleep(600);
  await pg.selectOption('#dn_type', 'dca_plus_buy'); await sleep(500);
  const ph = await pg.evaluate(() => { const r = PLX.svg.getBoundingClientRect(), m = document.getElementById('modal').getBoundingClientRect();
    return { w: r.width, mw: m.width, iw: innerWidth, sw: document.documentElement.scrollWidth, buy: PLX.buy } });
  ok(`⑨ the phone: the DCA+ form and its chart fit (${Math.round(ph.w)}px of ${ph.iw}) · no sideways page scroll`, ph.buy && ph.w <= ph.iw && ph.mw <= ph.iw + 1 && ph.sw <= ph.iw + 1, ph);
  ok(`no page error on the phone (${errs.length - e2})`, errs.length === e2, errs.slice(e2));
  await ctx.close();
  await br.close();
  console.log((res.every(Boolean) ? '✅' : '❌') + ` ui_dca_plus_buy.js: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_dca_plus_buy.js crashed: ' + String(e && e.stack || e).slice(0, 1500)); process.exit(1) });
