// 🪜🎨 run through ui_lines.py: the 🪜 card's ruler as the page draws it (dark · light) + a tap on a dotted line + the palettes
const { chromium } = require('playwright');
(async () => {
  const URL = process.argv[2];
  const br = await chromium.launch();
  const pg = await br.newPage({ viewport: { width: 430, height: 900 } });
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});      // the page's OKX live-price socket: answered here, never the network
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.some(b => b.bot_type === 'grid_step' && (b.sl || []).length), null, { timeout: 60000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(500);
  const out = await pg.evaluate(() => {
    const b = DATA.bots.find(x => x.bot_type === 'grid_step'), h = document.documentElement, t0 = h.dataset.theme;
    const dark = stLad(b, b.cp, { w: SK_W });
    h.dataset.theme = 'light'; const light = stLad(b, b.cp, { w: SK_W });
    if (t0) h.dataset.theme = t0; else delete h.dataset.theme;
    const m = dark.match(/data-stl="(r:-?\d+)"/); let pop = null;
    if (m) { stPop(b, m[1], { clientX: 200, clientY: 200 }); const p = document.getElementById('stpop'); pop = p ? p.innerText : null; if (p) p.style.display = 'none' }
    const pal = typeof ST_PAL_L !== 'undefined' ? { D: ST_PAL, L: ST_PAL_L } : (typeof ST_PAL !== 'undefined' ? { D: ST_PAL, L: ST_PAL } : null);
    return { b: { cp: b.cp, sl: b.sl, sl_far: b.sl_far, scfg: b.scfg }, dark, light, pop, pal };
  });
  out.errs = errs;
  console.log(JSON.stringify(out));
  await br.close();
})().catch(e => { console.log(JSON.stringify({ err: String(e) })); process.exit(1) });
