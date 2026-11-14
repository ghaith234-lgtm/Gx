// 🎨 v3.36.43 in a real browser (run through ui_themes.py — every card kind in a closed folder): the colour sets —
//   the owner (14-11): «5 و 8 … اريدها هادئة مو صارخه» ⇒ ❄️ «جليدي» (dark) and 🩵 «سماوي نهاري» (light) join ⚙️ «🎨 الألوان».
//   Also a guard for every set, today's and the next ones (rule 15 «🧭 النسق الثابت»): the text stays readable on its own background.
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
async function open(br, errs, init) {
  const ctx = await br.newContext({ viewport: { width: 412, height: 900 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(i => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none'); for (const k in i) localStorage.setItem(k, i[k]) } catch (e) {} }, init || {});
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(800);
  return { ctx, pg };
}
// the readability of a set: --tx and --mut against --bg1 (WCAG contrast)
const READ = `(() => { const cs = getComputedStyle(document.documentElement), v = k => cs.getPropertyValue(k).trim();
  const rgb = h => { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16) / 255) };
  const L = c => { const [r, g, b] = rgb(c).map(x => x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4)); return 0.2126 * r + 0.7152 * g + 0.0722 * b };
  const C = (a, b) => { const x = L(a), y = L(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05) };
  return { bg: v('--bg1'), tx: C(v('--tx'), v('--bg1')), mut: C(v('--mut'), v('--bg1')) } })()`;
(async () => {
  const br = await chromium.launch();
  const errs = [];
  let { ctx, pg } = await open(br, errs);

  const T = await pg.evaluate(() => THEMES.map(t => [t[0], t[1]]));
  ok(`🎨 ⚙️ «الألوان» lists ${T.length} sets — with ❄️ «جليدي» after «رمادي هادئ» and 🩵 «سماوي نهاري» after «نهاري فاتح»`,
     T.length === 9 && T.findIndex(t => t[0] === 'arctic') === T.findIndex(t => t[0] === 'graphite') + 1 && T.findIndex(t => t[0] === 'sky') === T.findIndex(t => t[0] === 'light') + 1
     && T.find(t => t[0] === 'arctic')[1] === 'جليدي' && T.find(t => t[0] === 'sky')[1] === 'سماوي نهاري', T);
  await pg.evaluate(() => openSettings());
  await pg.waitForTimeout(600);
  const btn = await pg.evaluate(() => [...document.querySelectorAll('#modal .thb')].map(b => b.getAttribute('title')));
  ok('… and the ⚙️ row draws a button for each (titled with its name)', btn.length === 9 && btn.includes('جليدي') && btn.includes('سماوي نهاري'), btn);

  // ❄️ arctic
  await pg.evaluate(() => setTheme('arctic'));
  await pg.waitForTimeout(500);
  const a = await pg.evaluate(() => { const cs = getComputedStyle(document.documentElement);
    return { th: document.documentElement.dataset.theme, ls: localStorage.getItem('dash_theme'), bg1: cs.getPropertyValue('--bg1').trim(), vio: cs.getPropertyValue('--vio-rgb').trim(),
      meta: (document.querySelector('meta[name="theme-color"]') || {}).content, pc: pcPal().d, tv: tvTheme() } });
  ok('❄️ «جليدي»: the page takes it (its own background and ice-blue accent) · saved for this device · the phone/browser bar colour · dark charts',
     a.th === 'arctic' && a.ls === 'arctic' && a.bg1 === '#0d141c' && a.vio === '186 230 253' && a.meta === '#0d141c' && a.pc === '#0aa5c4' && a.tv === 'dark', a);
  await ctx.close();
  ({ ctx, pg } = await open(br, errs, { dash_theme: 'arctic' }));
  const a2 = await pg.evaluate(() => ({ th: document.documentElement.dataset.theme, bg1: getComputedStyle(document.documentElement).getPropertyValue('--bg1').trim() }));
  ok('… and it is there from the first paint when the dashboard opens again', a2.th === 'arctic' && a2.bg1 === '#0d141c', a2);

  // 🩵 sky
  await pg.evaluate(() => setTheme('sky'));
  await pg.waitForTimeout(500);
  const s = await pg.evaluate(() => { const cs = getComputedStyle(document.documentElement), b = document.querySelector('button.primary');
    return { th: document.documentElement.dataset.theme, bg1: cs.getPropertyValue('--bg1').trim(), scheme: cs.colorScheme, vio: cs.getPropertyValue('--vio-rgb').trim(),
      btn: b ? getComputedStyle(b).color : null, glint: cs.getPropertyValue('--glint').trim(), pc: pcPal().d, tv: tvTheme(), st: stCol(0) === ST_PAL_L[0] } });
  ok('🩵 «سماوي نهاري»: a light set — white page · sky-blue accent · light scroll bars and form controls · white text on the filled buttons · its own logo glint',
     s.th === 'sky' && s.bg1 === '#ffffff' && /light/.test(s.scheme) && s.vio === '3 105 161' && s.btn === 'rgb(255, 255, 255)' && s.glint === '#0284c7', s);
  ok('… and everything that follows a light set does (the profit chart colours · the TradingView chart · the 🪜 line colours)', s.pc === '#0891b2' && s.tv === 'light' && s.st, s);

  // every set: readable
  const bad = [];
  for (const [k] of T) {
    await pg.evaluate(t => applyTheme(t), k);
    await pg.waitForTimeout(150);
    const r = await pg.evaluate(READ);
    if (!(r.tx >= 7 && r.mut >= 4.5)) bad.push({ k, ...r });
  }
  ok(`🔎 every set (${T.length}) is readable: the text ≥ 7:1 and the grey text ≥ 4.5:1 against its background (rule 15)`, !bad.length, bad);

  ok('no page errors', !errs.length, errs.slice(0, 3));
  await br.close();
  console.log(res.every(Boolean) ? `✅ ui_themes: ${res.filter(Boolean).length}/${res.length}` : `❌ ui_themes: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_themes crashed — ' + String(e).slice(0, 300)); process.exit(1) });
