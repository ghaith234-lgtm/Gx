// 📖 v3.36.46 in a real browser (run through ui_tut.py — every card kind in a closed folder): the owner (14-11): «اريد كل بوت فيه زر تعليم
//   يوضح كيف شغل البوت بالتفصيل اجزاء مقتطعه ومثال متحرك وشرح واساله واجوبه بالاخير لعمل الابوات كليا وكذلك شرح على ازرار الكرت»
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
(async () => {
  const br = await chromium.launch();
  const errs = [];
  const ctx = await br.newContext({ viewport: { width: 412, height: 900 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(1200);
  const kinds = await pg.evaluate(() => DATA.bots.map(b => [b.dir, b.bot_type || 'grid', !!(CARDS.get(b.dir) && CARDS.get(b.dir).querySelector('.ctut'))]));
  ok(`📖 every card (${kinds.length}) has the tutorial button next to ⚙`, kinds.length >= 9 && kinds.every(k => k[2]), kinds);
  const seen = [];
  for (const [dir, kind] of kinds) {
    await pg.evaluate(d => { try { hideModal() } catch (e) {} ; CARDS.get(d).querySelector('.ctut').click() }, dir);
    await pg.waitForTimeout(500);
    const r0 = await pg.evaluate(() => { const m = document.getElementById('modal');
      return { h2: (m.querySelector('h2') || {}).textContent || '', secs: [...m.querySelectorAll('.tutsec h3')].map(h => h.textContent),
        steps: m.querySelectorAll('.tutsteps li').length, btns: m.querySelectorAll('.tutbtns > div').length, qa: m.querySelectorAll('.tutqa').length,
        svg: !!m.querySelector('#tutSvg') } });
    await pg.waitForTimeout(4200);                                       // the moving example runs
    const r1 = await pg.evaluate(() => ({ marks: document.querySelectorAll('#tutSvg circle').length, ev: (document.getElementById('tutEv') || {}).textContent || '',
      pl: (document.getElementById('tutPl') || {}).textContent || '', line: !!document.querySelector('#tutSvg polyline') }));
    seen.push({ kind, ...r0, ...r1 });
  }
  const need = ['💡 الفكرة', '🧩 خطوة بخطوة', '🎬 مثال متحرك', '🔘 أزرار البطاقة', '❓ أسئلة وأجوبة'];
  ok('… each opens one window «📖 كيف يعمل بوت …» with its five parts: the idea · step by step · a moving example · the card\'s buttons · questions and answers',
     seen.every(s => /كيف يعمل بوت/.test(s.h2) && need.every(n => s.secs.includes(n)) && s.steps >= 3 && s.btns >= 8 && s.qa >= 10 && s.svg), seen.map(s => [s.kind, s.secs.length, s.steps, s.btns, s.qa]));
  ok('… the moving example moves: the price line is drawn and the trades appear as they happen (markers · the event line · the profit)',
     seen.every(s => s.line && s.marks >= 2 && s.ev.length > 5 && s.ev !== '…' && /الربح/.test(s.pl)), seen.map(s => [s.kind, s.marks, s.ev.slice(0, 40), s.pl]));
  const kk = new Set(seen.map(s => s.kind));
  ok(`… nine kinds, each with its own text (${[...kk].join(' · ')})`, kk.size >= 9 && new Set(seen.map(s => s.h2.split('—')[0])).size >= 9, seen.map(s => s.h2));
  // the pause button stops the example
  await pg.evaluate(() => tutPause());
  const a = await pg.evaluate(() => document.getElementById('tutEv').textContent + '|' + document.querySelectorAll('#tutSvg circle').length + '|' + document.getElementById('tutSvg').innerHTML.length);
  await pg.waitForTimeout(1500);
  const b2 = await pg.evaluate(() => document.getElementById('tutEv').textContent + '|' + document.querySelectorAll('#tutSvg circle').length + '|' + document.getElementById('tutSvg').innerHTML.length);
  ok('… «⏸ إيقاف المثال» stops it', a === b2, [a, b2]);
  await pg.evaluate(() => hideModal());
  await pg.waitForTimeout(400);
  ok('… and closing the window stops its loop (nothing keeps running)', await pg.evaluate(() => TUT_RUN === null || !document.getElementById('tutSvg')), null);
  ok('no page errors', !errs.length, errs.slice(0, 3));
  await br.close();
  console.log(res.every(Boolean) ? `✅ ui_tut: ${res.filter(Boolean).length}/${res.length}` : `❌ ui_tut: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_tut crashed — ' + String(e).slice(0, 300)); process.exit(1) });
