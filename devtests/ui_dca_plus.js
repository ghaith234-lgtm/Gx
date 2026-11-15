// ⚡ v3.36.56 in a real browser — DCA+: the owner (15-11) «واريد انا اتحكم فيه ويظهر لي بالجدول والمخطط وانا اختار الخروج ويبين لي
//   بالرسم نفسه الي موجود بالdca». node ui_dca_plus.js URL DIR [-q]   (DIR = the DCA+ bot's folder · see ui_dca_plus.py)
const { chromium } = require('playwright');
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
  async function open(ls) {
    const ctx = await br.newContext({ viewport: { width: 1280, height: 900 } });
    await ctx.addInitScript(o => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none'); for (const k in o) localStorage.setItem(k, o[k]) } catch (e) {} }, ls || {});
    const pg = await ctx.newPage();
    pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
    await pg.routeWebSocket(/.*/, () => {});
    await pg.goto(URL, { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length, null, { timeout: 30000 });
    await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
    await pg.waitForTimeout(3000);
    return { ctx, pg };
  }
  let { ctx, pg } = await open();
  // ① the card
  const c = await pg.evaluate(dir => {
    const el = CARDS.get(dir), b = DATA.bots.find(x => x.dir === dir), dg = DATA.bots.find(x => x.symbol === 'DOGE-USDT'), eg = CARDS.get(dg.dir);
    const txt = n => [...n.querySelectorAll('svg text')].map(t => t.textContent);
    return { tag: el.querySelector('.dcatag').textContent, btn: el._r.dplus.textContent, shown: el._r.dplus.style.display !== 'none', on: el._r.dplus.classList.contains('on'),
      viz: txt(el._r.viz), cap: el._r.viz.querySelector('.vcap').textContent, status: el._r.status.textContent, plus: !!(b.dca && b.dca.plus),
      dtag: eg.querySelector('.dcatag').textContent, dshown: eg._r.dplus.style.display !== 'none', dviz: txt(eg._r.viz) };
  }, DIR);
  ok(`① the DCA+ card: «${c.tag}» · the button «${c.btn}» (on · the bounce · the layers that exited this cycle) · the status line counts them`,
    c.plus && /⚡ DCA\+ بيعي/.test(c.tag) && c.shown && c.on && /0\.5%/.test(c.btn) && /خرجت 1/.test(c.btn) && /⚡ 1 طبقة خرجت/.test(c.status), c);
  ok('① the card\'s own drawing (the same one as the DCA) draws each filled layer\'s exit line: «⚡ أمان 1» · «⚡ أمان 3» · «⚡ أمان 2 ⛔» (switched off) · the key says what it is',
    c.viz.includes('⚡ أمان 1') && c.viz.includes('⚡ أمان 3') && c.viz.includes('⚡ أمان 2 ⛔') && /⚡ خروج الطبقة/.test(c.cap), c.viz);
  ok(`① the normal sell DCA next to it: «${c.dtag}» · no ⚡ button · no exit lines in its drawing`,
    /📉 DCA بيعي/.test(c.dtag) && !c.dshown && !c.dviz.some(t => t.startsWith('⚡ أمان')), c);
  // ② 📋 the table
  const t = await pg.evaluate(async dir => {
    const el = CARDS.get(dir); el._r.dtable.click(); await new Promise(r => setTimeout(r, 400));
    const m = document.getElementById('modal'), th = [...m.querySelectorAll('th')].map(x => x.textContent), rows = [...m.querySelectorAll('tbody tr')].map(r => [...r.children].map(td => td.textContent.trim()));
    const out = { h2: m.querySelector('h2').textContent, th, rows }; hideModal(); return out;
  }, DIR);
  const col = t.th.findIndex(x => x.startsWith('⚡ خروج الطبقة'));
  const cell = n => (t.rows[n] || [])[col] || '';
  ok('② 📋 the table has the «⚡ خروج الطبقة» column: the base = the cycle\'s target · safety 1 and 3 their exit price · safety 2 ⛔ · safety 4–5 «if filled»',
    col > 0 && /هدف الدورة/.test(cell(0)) && /^1999\.95/.test(cell(1)) && /⛔/.test(cell(2)) && /^2026/.test(cell(3)) && /إن نُفّذ/.test(cell(4)) && /إن نُفّذ/.test(cell(5)), { th: t.th, col, rows: t.rows.map(r => r[col]) });
  // ③ the ⚡ window
  const w = await pg.evaluate(async dir => {
    CARDS.get(dir)._r.dplus.click(); await new Promise(r => setTimeout(r, 400));
    const m = document.getElementById('modal'), rows = [...m.querySelectorAll('tbody')[0].querySelectorAll('tr')].map(r => [...r.children].map(td => td.textContent.trim()));
    return { h2: m.querySelector('h2').textContent, pct: m.querySelector('#dpx_pct').value, from: m.querySelector('#dpx_from').value, on: m.querySelector('#dpx_on').checked,
      re: m.querySelector('#dpx_re').checked, rows, logs: m.querySelectorAll('tbody').length, first: m.querySelector('.hwb').firstElementChild.tagName };
  }, DIR);
  ok(`③ «⚡ الخروج بالطبقات» opens the window (rule 14: <h2> first): on · 0.5% · from 1 · no re-open · 3 open layers with their exit price and state · the last exits`,
    /DCA\+/.test(w.h2) && w.first === 'H2' && w.on && w.pct === '0.5' && w.from === '1' && !w.re && w.rows.length === 3 && w.rows[1][5] === '⛔ لا تخرج وحدها'
    && w.rows[0][5] === '⚡ تخرج وحدها' && w.logs === 2, w);
  // switch safety 2 back on
  await pg.evaluate(() => { const b = [...document.querySelectorAll('#modal .dpxb')].find(x => x.textContent.includes('يخرج وحده')); b.click() });
  await sleep(2600);
  const w2 = await pg.evaluate(() => { const m = document.getElementById('modal'), bg = document.getElementById('mbg');
    const rows = bg.hidden ? [] : [...m.querySelectorAll('tbody')[0].querySelectorAll('tr')].map(r => [...r.children].map(td => td.textContent.trim()));
    return { open: !bg.hidden, rows } });
  ok('③ «⚡ يخرج وحده» on safety 2: the window reopens by itself with the fresh state — safety 2 «⚡ تخرج وحدها»',
    w2.open && w2.rows.length === 3 && w2.rows[1][5] === '⚡ تخرج وحدها', w2);
  // the settings
  await pg.evaluate(() => { document.getElementById('dpx_pct').value = '0.7'; document.getElementById('dpx_re').checked = true;
    [...document.querySelectorAll('#modal button')].find(x => x.textContent.includes('حفظ الإعدادات')).click() });
  await sleep(1800);
  const card2 = await pg.evaluate(dir => CARDS.get(dir)._r.dplus.textContent, DIR);
  ok(`③ 💾 the settings (0.7% · re-open): saved — the card says «${card2}»`, /0\.7%/.test(card2), card2);
  // a refused value
  const bad = await pg.evaluate(async dir => (await api('/api/control', { dir, action: 'lx_set', value: { pct: '0.1' } })), DIR);
  ok('③ a bounce under 0.3% is refused with the reason (it would not cover the fees)', bad.ok === false && /0\.3%/.test(bad.msg), bad);
  // exit now (your decision)
  await pg.evaluate(dir => CARDS.get(dir)._r.dplus.click(), DIR); await sleep(400);
  const cf = await pg.evaluate(() => { const b = [...document.querySelectorAll('#modal .dpxb.dz')][2]; b.click(); const d = document.getElementById('modal');
    return d.textContent });
  await sleep(300);
  ok('③ «⏏ أخرجها الآن» on safety 3 asks first: what it buys, its sell price, the price now and the rough result', /أخرج هذه الطبقة الآن/.test(cf) && /أمر الأمان 3/.test(cf) && /2,?036/.test(cf), cf.slice(0, 300));
  await pg.evaluate(() => document.getElementById('cf_y').click()); await sleep(1800);
  await ctx.close();
  // ④ the skins C · B · OKX
  for (const sk of ['c', 'b', 'o']) {
    ({ ctx, pg } = await open({ dash_skin: sk }));
    const k = await pg.evaluate(async dir => {
      const el = CARDS.get(dir); const chip = el.querySelector('.chip[data-sk="dplus"]');
      skAct(el, 'menu'); await new Promise(r => setTimeout(r, 60)); const mb = [...el.querySelectorAll('.sk-menu button')].map(x => x.textContent); skAct(el, 'menu');
      const lines = [...el.querySelectorAll('svg text')].map(t => t.textContent).filter(x => x.startsWith('⚡ أمان'));
      skAct(el, 'dplus'); await new Promise(r => setTimeout(r, 400)); const h2 = (document.querySelector('#modal h2') || {}).textContent || ''; hideModal();
      return { chip: chip ? chip.textContent : null, menu: mb.filter(x => x.includes('⚡')), lines, h2 };
    }, DIR);
    ok(`④ skin ${sk.toUpperCase()}: the ⚡ chip «${k.chip}» · the menu «⚡ الخروج بالطبقات» opens the window · the drawing has the exit lines (${k.lines.length})`,
      k.chip && /⚡/.test(k.chip) && k.menu.length === 1 && /DCA\+/.test(k.h2) && k.lines.length >= 2, k);
    await ctx.close();
  }
  // ⑤ the deploy form · the preview · the tutorial
  ({ ctx, pg } = await open());
  const f = await pg.evaluate(async () => {
    await openDeployDca(); await new Promise(r => setTimeout(r, 300));
    const s = document.getElementById('dn_type'), opts = [...s.options].map(o => o.value);
    const hid = document.getElementById('dn_lx_box').style.display === 'none';
    s.value = 'dca_plus'; dcaTypeSwitch(); await new Promise(r => setTimeout(r, 300));
    document.getElementById('dn_sym').value = 'ETH-USDT'; document.getElementById('dn_bp').value = '2000';
    await dcaPreview(); await new Promise(r => setTimeout(r, 400));
    const th = [...document.querySelectorAll('#dn_preview th')].map(x => x.textContent), body = dcaFormBody();
    const tr = [...document.querySelectorAll('#dn_preview tbody tr')].map(r => r.lastElementChild.textContent.trim());
    document.querySelector('.tutx').click(); await new Promise(r => setTimeout(r, 400));
    const tabs = [...document.querySelectorAll('.tuttabs button')].map(x => x.textContent);
    return { opts, hid, shown: document.getElementById('dn_lx_box') ? document.getElementById('dn_lx_box').style.display !== 'none' : null, th, tr, body, tabs,
      tut: (document.querySelector('.tuthwb h2') || {}).textContent || '' };
  });
  ok('⑤ the DCA form: «⚡ DCA+ بيعي» in the type list · its box only for it (the bounce · the start layer · re-open — off by default)',
    f.opts.includes('dca_plus') && f.hid && f.shown && f.body.dca_plus === '1' && f.body.lx_pct === '0.5' && f.body.lx_from === '1' && f.body.lx_reopen === false, f);
  ok('⑤ the preview table shows each safety order\'s exit price («⚡ خروج الطبقة») — the base keeps the cycle\'s target',
    f.th.some(x => x.startsWith('⚡ خروج الطبقة')) && /هدف الدورة/.test(f.tr[0]) && /^\d/.test(f.tr[1]), { th: f.th, tr: f.tr });
  ok(`⑤ 📖 the form's tutorial: the DCA+ tab next to the two DCA (${f.tabs.join(' · ')})`, f.tabs.length === 3 && f.tabs.some(x => /DCA\+/.test(x)), f.tabs);
  // the trial path takes DCA+ from the form (the body the 🧪 button sends · its kind is the sell DCA)
  const k2 = await pg.evaluate(() => { const b = dcaFormBody(); return b.dca_type === 'dca_buy' ? 'dca_buy' : 'dca' });
  ok('⑤ 🧪 the trial path from the form: a sell DCA with dca_plus (the trial runs the DCA+ engine)', k2 === 'dca' && f.body.dca_plus === '1');
  await ctx.close();
  ok('no page error anywhere', errs.length === 0, errs);
  await br.close();
  console.log(res.every(Boolean) ? `✅ ui_dca_plus.js: ${res.filter(Boolean).length}/${res.length}` : `❌ ui_dca_plus.js: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ crash ' + String(e && e.stack || e).slice(0, 900)); process.exit(1) });
