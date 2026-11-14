// 📖 v3.36.46–47 in a real browser (run through ui_tut.py — every card kind in a closed folder): the owner (14-11): «اريد كل بوت فيه زر تعليم
//   يوضح كيف شغل البوت بالتفصيل اجزاء مقتطعه ومثال متحرك وشرح واساله واجوبه بالاخير … وكذلك شرح على ازرار الكرت» ⇒ (v3.36.47) «عند الدخول الى
//   زر الشبكي فيه ثلاث بوتات كل بوت فيه زر اضغط عليه يخرج لي شرح» · the bar button and the card button: «أشيل الاثنين»
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
  const gone = await pg.evaluate(() => ({ card: document.querySelectorAll('#grid .ctut').length,
    bar: [...document.querySelectorAll('nav.actions button')].filter(b => b.textContent.includes('📖')).length }));
  ok('no 📖 on the cards and none in the top bar (the owner: «أشيل الاثنين»)', gone.card === 0 && gone.bar === 0, gone);

  // the five forms — each kind has its own 📖 inside the form
  const FORMS = [['openDeploy', '.gtsel .tutq', ['grid', 'grid_range', 'grid_plus']], ['openDeployDca', '.tutrow button', ['dca', 'dca_buy']],
                 ['openDeployRec', '.tutrow button', ['rec_buy', 'rec_sell']], ['openDeployStep', '.tutrow button', ['grid_step']], ['openDeployVa', '.tutrow button', ['rec_va']]];
  const NAME = { grid: 'الشبكة اللانهائية', grid_range: 'المدى', grid_plus: 'بلس', dca: 'DCA البيعي', dca_buy: 'DCA الشرائي', rec_buy: 'الشراء الدوري',
                 rec_sell: 'البيع الدوري', grid_step: 'المتدرج', rec_va: 'مسار القيمة' };
  const seen = [];
  for (const [fn, sel, kinds] of FORMS) {
    for (let j = 0; j < kinds.length; j++) {
      await pg.evaluate(f => { try { hideModal() } catch (e) {} ; window[f]() }, fn);
      await pg.waitForTimeout(900);
      const pre = await pg.evaluate(([sel, j]) => {
        const bs = [...document.querySelectorAll('#modal .hwb ' + sel)], gt0 = (document.getElementById('n_gtype') || {}).value;
        const inp = [...document.querySelectorAll('#modal .hwb input')].find(i => i.type !== 'hidden' && i.type !== 'checkbox' && i.offsetParent);
        if (inp) inp.value = '7.77';
        if (bs[j]) bs[j].click();
        return { n: bs.length, gt0, inp: inp ? inp.id : null };
      }, [sel, j]);
      await pg.waitForTimeout(450);
      const r0 = await pg.evaluate(() => { const m = document.getElementById('modal');
        return { h2: (m.querySelector('h2') || {}).textContent || '', secs: [...m.querySelectorAll('.tutsec h3')].map(h => h.textContent),
          steps: m.querySelectorAll('.tutsteps li').length, btns: m.querySelectorAll('.tutbtns > div').length, qa: m.querySelectorAll('.tutqa').length,
          back: !![...m.querySelectorAll('button')].find(x => x.textContent.includes('رجوع إلى النموذج')) } });
      await pg.waitForTimeout(4200);
      const r1 = await pg.evaluate(() => ({ marks: document.querySelectorAll('#tutSvg circle').length, ev: (document.getElementById('tutEv') || {}).textContent || '',
        pl: (document.getElementById('tutPl') || {}).textContent || '', line: !!document.querySelector('#tutSvg polyline') }));
      const r2 = await pg.evaluate(id => { const b = [...document.querySelectorAll('#modal button')].find(x => x.textContent.includes('رجوع إلى النموذج')); if (b) b.click();
        const e = id && document.getElementById(id);
        return { kept: id ? !!(e && e.value === '7.77') : true, gt1: (document.getElementById('n_gtype') || {}).value, form: !!document.querySelector('#modal .hwb ' + (id ? '#' + id : 'h2')) } }, pre.inp);
      seen.push({ fn, kind: kinds[j], n: pre.n, ...r0, ...r1, ...r2, gt0: pre.gt0 });
    }
  }
  const need = ['💡 الفكرة', '🧩 خطوة بخطوة', '🎬 مثال متحرك', '🔘 أزرار البطاقة', '❓ أسئلة وأجوبة'];
  ok('📖 inside every deploy form, one for each of its bots: the grid form 3 (♾️ · 🎚️ · ➕ — inside their kind buttons) · DCA 2 · the recurring 2 · 🪜 1 · 💹 1',
     seen.filter(s => s.fn === 'openDeploy').every(s => s.n === 3) && seen.filter(s => s.fn === 'openDeployDca' || s.fn === 'openDeployRec').every(s => s.n === 2)
     && seen.filter(s => s.fn === 'openDeployStep' || s.fn === 'openDeployVa').every(s => s.n === 1), seen.map(s => [s.fn, s.n]));
  ok('… each opens the explanation of ITS bot: «📖 كيف يعمل بوت <name>» with the idea · step by step · a moving example · the card\'s buttons · questions and answers',
     seen.length === 9 && seen.every(s => s.h2.includes('كيف يعمل بوت') && s.h2.includes(NAME[s.kind]) && need.every(n => s.secs.includes(n)) && s.steps >= 3 && s.btns >= 8 && s.qa >= 10),
     seen.map(s => [s.kind, s.h2.slice(0, 40), s.secs.length]));
  ok('… the moving example moves (the price line · the trades as they happen · the profit)',
     seen.every(s => s.line && s.marks >= 2 && s.ev.length > 5 && s.ev !== '…' && /الربح/.test(s.pl)), seen.map(s => [s.kind, s.marks, s.ev.slice(0, 40)]));
  ok('… «↩️ رجوع إلى النموذج» brings the form back with what was typed · the grid\'s 📖 does not change the kind chosen',
     seen.every(s => s.back && s.kept && s.form) && seen.filter(s => s.fn === 'openDeploy').every(s => s.gt1 === s.gt0), seen.map(s => [s.kind, s.back, s.kept, s.gt0, s.gt1]));
  // pause · closing
  await pg.evaluate(() => { hideModal(); openDeployVa() }); await pg.waitForTimeout(900);
  await pg.evaluate(() => document.querySelector('#modal .tutrow button').click()); await pg.waitForTimeout(1500);
  await pg.evaluate(() => tutPause());
  const a = await pg.evaluate(() => document.getElementById('tutEv').textContent + '|' + document.getElementById('tutSvg').innerHTML.length);
  await pg.waitForTimeout(1500);
  const b2 = await pg.evaluate(() => document.getElementById('tutEv').textContent + '|' + document.getElementById('tutSvg').innerHTML.length);
  ok('… «⏸ إيقاف المثال» stops it', a === b2, [a, b2]);
  await pg.evaluate(() => hideModal()); await pg.waitForTimeout(400);
  ok('… and closing the window stops its loop', await pg.evaluate(() => TUT_RUN === null || !document.getElementById('tutSvg')), null);
  ok('no page errors', !errs.length, errs.slice(0, 3));
  await br.close();
  console.log(res.every(Boolean) ? `✅ ui_tut: ${res.filter(Boolean).length}/${res.length}` : `❌ ui_tut: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_tut crashed — ' + String(e).slice(0, 300)); process.exit(1) });
