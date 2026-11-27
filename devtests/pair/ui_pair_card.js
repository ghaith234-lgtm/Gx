// 🔀 «شبكة عملتين» — its card in a real browser (run through ui_pair_card.py · a LINK/XRP bot planted as its engine leaves it):
//   ① the card: LINK/XRP · 🔀 · the profit in XRP (≈ $ beside it — never «$» on the XRP number) · the ratio · the next buy/sell · today ·
//     what it holds (with the dollar of the swap in flight) · the status «⏳ تبديل جارٍ»
//   ② ⏸ pause buy ⇒ the state file gets the floor at the ratio · the button turns «▶️ استئناف الشراء» · ▶️ asks first, then clears it
//   ③ 🪜 the levels window (the ratio row between them) · ④ ⚙ its own details window
//   ⑤ the skins ج · ب · OKX: the card reads its own data (LINK/XRP · XRP · the next buy) · ⑥ the compact row: today in XRP
//   ⑦ a phone width: no sideways scroll · no page error
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const URL = process.argv[2], DIR = process.argv[3], SHOTS = process.argv[4] && process.argv[4] !== '-' ? process.argv[4] : '', Q = process.argv.includes('-q');
const SP = path.join(DIR, 'pair_link_ui', 'grid_state_LINK-XRP.json');
const res = [];
function ok(name, cond, det) { res.push(!!cond); if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900))); }
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function page(br, errs, o) {
  o = o || {};
  const ctx = await br.newContext({ viewport: o.vp || { width: 1280, height: 900 }, deviceScaleFactor: SHOTS ? 2 : 1 });
  await ctx.addInitScript(v => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none');
    if (v.skin) localStorage.setItem('dash_skin', v.skin); else localStorage.removeItem('dash_skin');
    if (v.cmp) localStorage.setItem('dash_cmp', 'on'); else localStorage.removeItem('dash_cmp') } catch (e) {} }, { skin: o.skin || '', cmp: !!o.cmp });
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && document.querySelector('.card[data-dir]'), null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await sleep(1500);
  return { ctx, pg };
}
const cardText = pg => pg.evaluate(() => { const el = document.querySelector('.card.pair[data-dir]'); return el ? el.innerText.replace(/\s+/g, ' ') : '' });
(async () => {
  const br = await chromium.launch();
  const errs = [];
  let { ctx, pg } = await page(br, errs);
  // ① the card
  const t = await cardText(pg);
  const pr = await pg.evaluate(() => { const el = document.querySelector('.card.pair[data-dir]'); return el && el._r ? { p: el._r.profit.innerText, u: el._r.usd.innerText } : {} });
  ok('① the card «🔀 شبكة عملتين» LINK/XRP · the profit +1.2 XRP with ≈ 2.40$ beside it (no «$» on the XRP number)',
     /LINK\/XRP/.test(t) && /شبكة عملتين/.test(t) && /\+1\.2 XRP/.test(pr.p || '') && !/\$/.test(pr.p || '') && /2\.40\$/.test(pr.u || ''), { t: t.slice(0, 300), pr });
  ok('① the ratio 7.52 · the next buy 7.352941 · the next sell 7.65 · today +0.4', /7\.52/.test(t) && /7\.352941/.test(t) && /7\.65/.test(t) && /\+0\.4/.test(t), t.slice(0, 600));
  ok('① what it holds: 100 XRP · 3 LINK · 1.2500 USDT between the legs · its value in XRP vs the start', /100 XRP · 3 LINK/.test(t) && /1\.2500 USDT/.test(t) && /123\.185 XRP · [-+][0-9.]+%/.test(t), t);
  ok('① the status: a swap in flight through the dollar', /تبديل جارٍ عبر الدولار/.test(t), t.slice(-200));
  ok('① 6 buy · 5 sell levels · 3 completed sales', /6 شراء · 5 بيع · 3 بيعة مكتملة/.test(t), t);
  if (SHOTS) { await pg.locator('.card.pair[data-dir]').scrollIntoViewIfNeeded(); await sleep(2500);
    await pg.locator('.card.pair[data-dir]').screenshot({ path: path.join(SHOTS, 'pair_card.png') }) }
  // ② ⏸ / ▶️
  await pg.click('.card.pair[data-dir] [data-k="ab"]');
  await sleep(1800);
  let s = JSON.parse(fs.readFileSync(SP));
  ok('② ⏸ pause buy ⇒ the state file: the floor at the ratio (7.52) — the control fields only', Math.abs((+s.buy_floor || 0) - 7.52) < 1e-9 && !s.pause_buy, { bf: s.buy_floor, pb: s.pause_buy });
  await pg.evaluate(() => tick()); await sleep(1500);
  const ab = await pg.evaluate(() => document.querySelector('.card.pair[data-dir] [data-k="ab"]').innerText);
  ok('② … the button now says «▶️ استئناف الشراء» and the next buy «⏸ موقوف»', /استئناف الشراء/.test(ab) && /⏸ موقوف/.test(await cardText(pg)), ab);
  await pg.click('.card.pair[data-dir] [data-k="ab"]');
  await sleep(600);
  const dlg = await pg.evaluate(() => { const h = [...document.querySelectorAll('h2')].map(x => x.innerText).join(' | '); return h });
  s = JSON.parse(fs.readFileSync(SP));
  ok('② ▶️ resume asks first (a confirm window) — nothing changed yet', /استئناف الشراء/.test(dlg) && Math.abs((+s.buy_floor || 0) - 7.52) < 1e-9, dlg);
  await pg.click('#pa_rs'); await sleep(1800);
  s = JSON.parse(fs.readFileSync(SP));
  ok('② ✅ yes ⇒ the floor cleared', !(+s.buy_floor) && !s.pause_buy, { bf: s.buy_floor });
  // ③ the levels
  await pg.evaluate(() => tick()); await sleep(1200);
  await pg.click('.card.pair[data-dir] [data-k="lddr"]'); await sleep(600);
  const lv = await pg.evaluate(() => ({ h: ([...document.querySelectorAll('h2')].pop() || {}).innerText || '', rows: document.querySelectorAll('.pairlv tbody tr').length,
    mid: (document.querySelector('.pairlv tr.pmid') || {}).innerText || '' }));
  ok('③ 🪜 the levels: 11 levels + the ratio row between them', /مستويات/.test(lv.h) && lv.rows === 12 && /7\.52/.test(lv.mid), lv);
  await pg.evaluate(() => hideModal()); await sleep(400);
  // ④ details
  await pg.click('.card.pair[data-dir] .cset'); await sleep(600);
  const dt = await pg.evaluate(() => document.querySelector('#modal') ? document.querySelector('#modal').innerText : '');
  ok('④ ⚙ its own details window (the settings in XRP · the step · 6 · 5 · the guard switch)', /تفاصيل «شبكة عملتين»/.test(dt) && /20 XRP/.test(dt) && /6 · 5/.test(dt) && /الحارس/.test(dt), dt.slice(0, 400));
  await pg.evaluate(() => hideModal());
  if (SHOTS) await pg.screenshot({ path: path.join(SHOTS, 'pair_page.png') });
  await ctx.close();
  // ⑤ the skins
  for (const [sk, nm] of [['c', 'ج'], ['b', 'ب'], ['o', 'OKX']]) {
    ({ ctx, pg } = await page(br, errs, { skin: sk }));
    const k = await pg.evaluate(() => { const el = document.querySelector('.card.pair[data-dir]'); if (!el) return {};
      const b = botOf(el.dataset.dir), sk = el.querySelector('.skin'); return { kind: skKind(el, b), txt: sk ? sk.innerText.replace(/\s+/g, ' ') : '' } });
    ok(`⑤ skin ${nm}: the card reads its own data (LINK/XRP · XRP · the next buy · today in XRP) — not the grid's`,
       k.kind === 'pair' && /LINK\/XRP/.test(k.txt) && /XRP/.test(k.txt) && /الشراء القادم/.test(k.txt) && /\+0\.4 XRP/.test(k.txt) && !/\+0\.4\d*\$/.test(k.txt), k);
    if (SHOTS) { await pg.locator('.card.pair[data-dir]').scrollIntoViewIfNeeded(); await sleep(2500);
      await pg.locator('.card.pair[data-dir]').screenshot({ path: path.join(SHOTS, `pair_skin_${sk}.png`) }) }
    await ctx.close();
  }
  // ⑥ the compact row
  ({ ctx, pg } = await page(br, errs, { cmp: true }));
  const cm = await pg.evaluate(() => { const el = document.querySelector('.card.pair[data-dir]'); const r = el && el._cmr; return r ? r.innerText.replace(/\s+/g, ' ') : '' });
  ok('⑥ the compact row: «🔀 شبكة عملتين» · today +0.4 XRP (not dollars)', /شبكة عملتين/.test(cm) && /\+0\.4 XRP/.test(cm), cm);
  await ctx.close();
  // ⑦ the phone
  ({ ctx, pg } = await page(br, errs, { vp: { width: 390, height: 840 } }));
  const ov = await pg.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  ok('⑦ a phone width (390): the page with the card fits (no sideways scroll)', ov <= 1, ov);
  if (SHOTS) await pg.locator('.card.pair[data-dir]').screenshot({ path: path.join(SHOTS, 'pair_card_390.png') });
  await ctx.close();
  ok('no page error', errs.length === 0, errs.slice(0, 3));
  await br.close();
  const n = res.filter(Boolean).length;
  console.log(`${n === res.length ? '✅' : '❌'} ui_pair_card: ${n}/${res.length}`);
  process.exit(n === res.length ? 0 : 1);
})().catch(e => { console.log('❌ ui_pair_card crashed: ' + e); process.exit(1) });
