// 🔤 v3.36.36 in a real browser (run through ui_fonts.py — every card kind in a closed folder): the chosen font reaches every Arabic
//   letter — the owner (13-11): «هناك بعض الخطوط الي في الواجهة وداخل الكروت لم تتغير».
//   The chosen font here is «أميري» (Amiri), mapped to a font installed on this machine (FreeSerif — no network) · for every visible
//   element with Arabic letters, Chrome's own report of the fonts it drew with (CSS.getPlatformFontsForNode) must show all its Arabic
//   letters drawn with that font — in every card look, in a window and in a page.
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 1200)));
}
const AR = /[؀-ۿ]/g;
async function scan(pg, cdp, root) {
  const n = await pg.evaluate(root => {
    document.querySelectorAll('[data-fchk]').forEach(e => e.removeAttribute('data-fchk'));
    const base = root ? document.querySelector(root) : document.body; let i = 0;
    const w = document.createTreeWalker(base, NodeFilter.SHOW_TEXT); let t;
    while ((t = w.nextNode()) && i < 400) {
      const el = t.parentElement; if (!el || el.closest('script,style,.hwclone,#splash') || el.hasAttribute('data-fchk')) continue;
      if (!/[؀-ۿ]/.test(t.nodeValue)) continue;
      const r = el.getBoundingClientRect(); if (!r.width || !r.height || getComputedStyle(el).visibility === 'hidden') continue;
      if (r.bottom < 0 || r.top > innerHeight * 3) continue;
      el.setAttribute('data-fchk', String(i++));
    }
    return i;
  }, root || null);
  const doc = await cdp.send('DOM.getDocument', { depth: 0 });
  const { nodeIds } = await cdp.send('DOM.querySelectorAll', { nodeId: doc.root.nodeId, selector: '[data-fchk]' });
  const bad = [];
  for (const id of nodeIds) {
    const { fonts } = await cdp.send('CSS.getPlatformFontsForNode', { nodeId: id });
    const info = await cdp.send('DOM.describeNode', { nodeId: id, depth: 1 });
    const own = (info.node.children || []).filter(c => c.nodeType === 3).map(c => c.nodeValue).join('');
    const ar = (own.match(AR) || []).length; if (!ar || !fonts.length) continue;   // no fonts = not drawn yet (a card off screen)
    const fs = fonts.find(f => /FreeSerif/i.test(f.familyName)), got = fs ? fs.glyphCount : 0;
    if (got < ar) bad.push({ text: own.trim().slice(0, 40), cls: (info.node.attributes || []).join(' ').slice(0, 80), fonts: fonts.map(f => f.familyName + ':' + f.glyphCount).join(' · ') });
  }
  return { n, bad };
}
async function open(br, skin, errs) {
  const ctx = await br.newContext({ viewport: { width: 412, height: 900 } });
  await ctx.addInitScript(s => {
    try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none'); localStorage.setItem('dash_font', 'amiri'); if (s) localStorage.setItem('dash_skin', s) } catch (e) {}
    const st = document.createElement('style'); st.textContent = "@font-face{font-family:'Amiri';src:local('FreeSerif')}@font-face{font-family:'Amiri';font-weight:700;src:local('FreeSerif Bold'),local('FreeSerif')}";
    const put = () => (document.head || document.documentElement).appendChild(st);
    if (document.documentElement) put(); else document.addEventListener('DOMContentLoaded', put);
  }, skin);
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(1800);
  const cdp = await ctx.newCDPSession(pg); await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
  return { ctx, pg, cdp };
}
(async () => {
  const br = await chromium.launch();
  const errs = [];
  for (const [skin, nm] of [[null, 'القديم'], ['c', 'ج'], ['b', 'ب'], ['o', 'OKX']]) {
    const { ctx, pg, cdp } = await open(br, skin, errs);
    const ff = await pg.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--ff').trim());
    const r = await scan(pg, cdp);
    ok(`🔤 ${nm}: every Arabic letter on the dashboard and in the cards drawn with the chosen font (${r.n} texts · ${ff})`, r.n > 40 && !r.bad.length && /Amiri/.test(ff), r.bad.slice(0, 8));
    if (!skin) {
      await pg.evaluate(() => openSettings()); await pg.waitForTimeout(300);
      await pg.evaluate(() => { stTog('fps'); stTog('poll') }); await pg.waitForTimeout(200);
      const s = await scan(pg, cdp, '#modal');
      ok(`🔤 a window (⚙️): every Arabic letter in the chosen font (${s.n} texts)`, s.n > 20 && !s.bad.length, s.bad.slice(0, 8));
      await pg.evaluate(() => hideModal());
      await pg.evaluate(() => gridDetails(DATA.bots.find(b => b.bot_type === 'grid'))); await pg.waitForTimeout(600);
      const g = await scan(pg, cdp, '#modal');
      ok(`🔤 a bot's details window: every Arabic letter in the chosen font (${g.n} texts)`, g.n > 10 && !g.bad.length, g.bad.slice(0, 8));
      await pg.evaluate(() => hideModal());
      await pg.evaluate(() => openReports()); await pg.waitForTimeout(1500);
      const p = await scan(pg, cdp, '#page_reports');
      ok(`🔤 a page (📊 التقارير): every Arabic letter in the chosen font (${p.n} texts)`, p.n > 5 && !p.bad.length, p.bad.slice(0, 8));
    }
    await ctx.close();
  }
  ok('no page errors', !errs.length, errs);
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_fonts: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('crash', e); process.exit(1) });
