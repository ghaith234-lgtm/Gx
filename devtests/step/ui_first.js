// 🪜 📈 the browser half of ui_first.py (run it through ui_first.py — it starts the closed dashboard)
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const SHOT = (process.argv.find(a => a.startsWith('--shot=')) || '').slice(7);   // a picture of the form + table (for a person)
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 600)));
}
(async () => {
  const br = await chromium.launch();
  const pg = await br.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: SHOT ? 2 : 1 });
  const out = [];
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : (out.push(rt.request().url()), rt.abort())));
  const bodies = [];
  pg.on('request', rq => { if (rq.url().includes('/api/step_plan')) bodies.push(rq.postData()); });
  const errs = [];
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof openDeployStep === 'function', null, { timeout: 30000 });
  await pg.evaluate(() => openDeployStep({}));
  await pg.waitForSelector('#st_d1', { timeout: 15000 });
  const labels = await pg.evaluate(() => [...document.querySelectorAll('.fld label')].map(l => l.textContent.trim()));
  ok('the form: «📈 مسافة أول بيعة (%)» then «↔️ المسافة بين البيعات (%)» (the old single field is gone)',
     labels.includes('📈 مسافة أول بيعة (%)') && labels.includes('↔️ المسافة بين البيعات (%)') && !labels.includes('📈 مسافة البيع (%)')
     && labels.indexOf('📈 مسافة أول بيعة (%)') + 1 === labels.indexOf('↔️ المسافة بين البيعات (%)'), labels);
  const fill = async kv => {
    for (const [id, v] of Object.entries(kv)) { await pg.fill('#' + id, String(v)); }
    await pg.waitForTimeout(900);
    await pg.waitForFunction(() => !document.querySelector('#st_plan .vach0'), null, { timeout: 15000 }).catch(() => {});
    await pg.waitForTimeout(300);
  };
  await fill({ st_sym: 'XRP-USDT', st_q: 15, st_n: 3, st_d1: 1, st_d: 0.5, st_g: 3, st_floor: 0.7, st_up: 1, st_p0: 1 });
  const sb = await pg.evaluate(() => stBody());
  ok('stBody sends step_first_pct (the first-sell field) and step_sell_pct (between sells)', sb.step_first_pct === '1' && sb.step_sell_pct === '0.5', sb);
  const last = JSON.parse(bodies[bodies.length - 1] || '{}');
  ok('the table request carries both distances', last.step_first_pct === '1' && last.step_sell_pct === '0.5', last);
  const row0 = await pg.evaluate(() => [...document.querySelectorAll('#st_plan tr[data-j="0"]')].map(tr => ({
    k: tr.dataset.k, sp: ((tr.querySelector('.stsp') || {}).textContent || '').trim(), di: ((tr.querySelector('.stdi') || {}).textContent || '').trim(),
    pr: ((tr.querySelector('.stpr') || {}).textContent || '').trim() })));
  ok('the table is vertical (one row per sell) — the owner\'s example: level 0 = 3 rows · 1.01 · 1.015 · 1.02 · +1.000% · +1.500% · +2.000% '
     + 'from the buy · each a + profit', row0.length === 3 && row0.map(r => r.sp).join('|') === '1.01|1.015|1.02'
     && row0.map(r => r.di).join('|') === '+1.000%|+1.500%|+2.000%' && row0.every(r => r.pr.startsWith('+')), row0);
  const per = await pg.evaluate(() => { const c = {}; document.querySelectorAll('#st_plan tr[data-j]').forEach(tr => { c[tr.dataset.j] = (c[tr.dataset.j] || 0) + 1 }); return c });
  ok('every level has exactly its 3 sell rows (the level · buy · amount span them)', Object.keys(per).length > 5 && Object.values(per).every(n => n === 3), per);
  if (SHOT) {                                    // (the brand splash covers the page for its first seconds)
    await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
    await (await pg.$('.modal') || pg).screenshot({ path: SHOT });
  }
  const err0 = await pg.evaluate(() => [...document.querySelectorAll('#st_plan .sterr')].map(e => e.textContent));
  ok('no refusal for the owner\'s example', err0.length === 0, err0);
  await fill({ st_d1: 0.1 });
  const err1 = await pg.evaluate(() => [...document.querySelectorAll('#st_plan .sterr')].map(e => e.textContent));
  ok('first sell 0.1% ⇒ the table refuses in red: «مسافة أول بيعة 0.1% لا تغطي العمولتين»', err1.some(e => e.includes('مسافة أول بيعة 0.1%') && e.includes('لا تغطي العمولتين')), err1);
  await fill({ st_d1: 'nan' });
  const err2 = await pg.evaluate(() => (document.querySelector('#st_plan') || {}).textContent || '');
  ok('first sell «nan» ⇒ refused («تأكد من الأرقام»)', err2.includes('تأكد من الأرقام'), err2.slice(0, 200));
  const sub = await pg.evaluate(() => {
    const el = document.createElement('div');
    const mk = d1 => { try { return skModel(el, { symbol: 'XRP-USDT', scfg: { N: 3, d: 0.005, d1, G: 0.03, Q: 15 }, ladder: {}, gcfg: {} }, 'step').sub } catch (e) { return 'ERR ' + e } };
    return [mk(0.01), mk(0.005), mk(undefined)];
  });
  ok('the card\'s settings line: both distances when they differ · «البيع» when equal or unknown',
     sub[0] === '3 بيعات لكل شراء · أول بيعة 1% · بين البيعات 0.5% · الشراء 3% · 15$ لكل شراء'
     && sub[1] === '3 بيعات لكل شراء · البيع 0.5% · الشراء 3% · 15$ لكل شراء' && sub[2] === sub[1], sub);
  ok('no page error · nothing left the machine except blocked asset requests', errs.length === 0, { errs, out: out.slice(0, 5) });
  await br.close();
  console.log(`${res.filter(Boolean).length} ok · ${res.length - res.filter(Boolean).length} failed`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ crash ' + e); process.exit(1); });
