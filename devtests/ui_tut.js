// 📖 v3.36.46–47 in a real browser (run through ui_tut.py — every card kind in a closed folder): the owner (14-11): «اريد كل بوت فيه زر تعليم
//   يوضح كيف شغل البوت بالتفصيل اجزاء مقتطعه ومثال متحرك وشرح واساله واجوبه بالاخير … وكذلك شرح على ازرار الكرت» ⇒ (v3.36.47) «عند الدخول الى
//   زر الشبكي فيه ثلاث بوتات كل بوت فيه زر اضغط عليه يخرج لي شرح» · the bar button and the card button: «أشيل الاثنين» ⇒ (p79) «خليه فوق زر
//   واحد وبداخله ثلاث شروحات والباقي كذلك»
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
  pg.on('pageerror', e => errs.push(String(e.stack || e).slice(0, 400)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(1200);
  const gone = await pg.evaluate(() => ({ card: document.querySelectorAll('#grid .ctut').length,
    bar: [...document.querySelectorAll('nav.actions button')].filter(b => b.textContent.includes('📖')).length }));
  ok('no 📖 on the cards and none in the top bar (the owner: «أشيل الاثنين»)', gone.card === 0 && gone.bar === 0, gone);

  // the five forms — ONE 📖 per form (the owner: «خليه فوق زر واحد وبداخله ثلاث شروحات والباقي كذلك») ⇒ one window, a tab per bot
  await pg.evaluate(() => { const o = tutDraw; window._tutStale = 0;
    window.tutDraw = function (S) { if (TUT_RUN && S !== TUT_RUN.S) window._tutStale++; return o.apply(this, arguments) } });
  const FORMS = [['openDeploy', ['grid', 'grid_range', 'grid_plus'], 'grid_range', "gType('grid_range')", 'n_gtype'],
                 ['openDeployDca', ['dca', 'dca_buy'], 'dca_buy', "(document.getElementById('dn_type').value='dca_buy',dcaTypeSwitch())", 'dn_type'],
                 ['openDeployRec', ['rec_buy', 'rec_sell'], 'rec_sell', "(document.getElementById('rd_type').value='rec_sell',recFormSync())", 'rd_type'],
                 ['openDeployStep', ['grid_step'], 'grid_step', '0', null], ['openDeployVa', ['rec_va'], 'rec_va', '0', null]];
  const NAME = { grid: 'الشبكة اللانهائية', grid_range: 'المدى', grid_plus: 'بلس', dca: 'DCA البيعي', dca_buy: 'DCA الشرائي', rec_buy: 'الشراء الدوري',
                 rec_sell: 'البيع الدوري', grid_step: 'المتدرج', rec_va: 'مسار القيمة' };
  const forms = [], seen = [];
  for (const [fn, kinds, pick, pickJs, selId] of FORMS) {
    await pg.evaluate(f => { try { hideModal() } catch (e) {} ; window[f]() }, fn);
    await pg.waitForTimeout(900);
    const pre = await pg.evaluate(([pickJs, selId]) => {
      eval(pickJs);
      const one = [...document.querySelectorAll('#modal .hwb .tutone')], old = document.querySelectorAll('#modal .hwb .tutq, #modal .hwb .gtsel button span').length;
      const h2 = document.querySelector('#modal .hwb h2'), first = one[0] && h2 && h2.nextElementSibling && h2.nextElementSibling.contains(one[0]);
      const inp = [...document.querySelectorAll('#modal .hwb input')].find(i => i.type !== 'hidden' && i.type !== 'checkbox' && i.offsetParent);
      if (inp) inp.value = '7.77';
      const sel0 = selId ? document.getElementById(selId).value : null;
      if (one[0]) one[0].click();
      return { n: one.length, old, first: !!first, inp: inp ? inp.id : null, sel0, txt: one[0] ? one[0].textContent : '' };
    }, [pickJs, selId]);
    await pg.waitForTimeout(400);
    const win = await pg.evaluate(() => { const t = [...document.querySelectorAll('#modal .tuttabs button')];
      return { tabs: t.map(x => x.textContent), on: t.filter(x => x.classList.contains('on')).map(x => x.textContent), h2: (document.querySelector('#modal .tuthwb h2') || {}).textContent || '',
      hid: (() => { const f = document.querySelector('#modal .hwb:not(.tuthwb)'); return !!(f && f.isConnected && getComputedStyle(f).display === 'none' && f.querySelector('.tutone')) })() } });
    forms.push({ fn, ...pre, ...win, pick });
    for (const k of kinds) {
      if (kinds.length > 1) { await pg.evaluate(i => document.querySelectorAll('#modal .tuttabs button')[i].click(), kinds.indexOf(k)); await pg.waitForTimeout(300) }
      const st0 = await pg.evaluate(() => window._tutStale);
      const r0 = await pg.evaluate(() => { const m = document.getElementById('modal');
        return { h2: (m.querySelector('.tuthwb h2') || {}).textContent || '', secs: [...m.querySelectorAll('.tutsec h3')].map(h => h.textContent),
          steps: m.querySelectorAll('.tutsteps li').length, btns: m.querySelectorAll('.tutbtns > div').length, qa: m.querySelectorAll('.tutqa').length,
          on: [...m.querySelectorAll('.tuttabs button.on')].map(x => x.textContent).join('|'),
          back: !![...m.querySelectorAll('button')].find(x => x.textContent.includes('رجوع إلى النموذج')) } });
      await pg.waitForTimeout(4200);
      const r1 = await pg.evaluate(() => ({ marks: document.querySelectorAll('#tutSvg circle').length, ev: (document.getElementById('tutEv') || {}).textContent || '',
        pl: (document.getElementById('tutPl') || {}).textContent || '', line: !!document.querySelector('#tutSvg polyline'), stale: window._tutStale }));
      seen.push({ fn, kind: k, ...r0, ...r1, stale: r1.stale - st0 });
    }
    const r2 = await pg.evaluate(([id, selId]) => { const b = [...document.querySelectorAll('#modal button')].find(x => x.textContent.includes('رجوع إلى النموذج')); if (b) b.click();
      const e = id && document.getElementById(id);
      return { kept: id ? !!(e && e.value === '7.77') : true, sel1: selId ? (document.getElementById(selId) || {}).value : null,
               form: !!document.querySelector('#modal .hwb .tutone') && getComputedStyle(document.querySelector('#modal .hwb')).display !== 'none' && !document.querySelector('#modal .tuthwb'),
               run: TUT_RUN === null } }, [pre.inp, selId]);
    Object.assign(forms[forms.length - 1], r2);
  }
  const need = ['💡 الفكرة', '🧩 خطوة بخطوة', '🎬 مثال متحرك', '🔘 أزرار البطاقة', '❓ أسئلة وأجوبة'];
  ok('ONE «📖 شرح …» per deploy form, right under its title · nothing left inside the grid\'s kind buttons',
     forms.length === 5 && forms.every(f => f.n === 1 && f.old === 0 && f.first && f.txt.includes('📖')), forms.map(f => [f.fn, f.n, f.old, f.first]));
  ok('… it opens one window with a tab for each of the form\'s bots (the grid 3 · DCA 2 · the recurring 2 · 🪜 and 💹 none) — on the kind chosen in the form · the form waits hidden in place (its own updates — DCA\'s table — still land in it)',
     forms.every((f, i) => { const n = FORMS[i][1].length; return (n > 1 ? f.tabs.length === n && f.on.length === 1 && f.on[0].includes(NAME[f.pick]) : f.tabs.length === 0) && f.h2.includes(NAME[f.pick]) && f.hid }),
     forms.map(f => [f.fn, f.tabs, f.on, f.h2.slice(0, 40)]));
  ok('… every tab is ITS bot\'s explanation: «📖 كيف يعمل بوت <name>» with the idea · step by step · a moving example · the card\'s buttons · questions and answers',
     seen.length === 9 && seen.every(s => s.h2.includes('كيف يعمل بوت') && s.h2.includes(NAME[s.kind]) && need.every(n => s.secs.includes(n)) && s.steps >= 3 && s.btns >= 8 && s.qa >= 10
       && (s.fn === 'openDeployStep' || s.fn === 'openDeployVa' || s.on.includes(NAME[s.kind]))), seen.map(s => [s.kind, s.h2.slice(0, 40), s.secs.length, s.on]));
  ok('… the moving example moves on every tab — and only one at a time (no frame of the tab before draws into it)',
     seen.every(s => s.line && s.marks >= 2 && s.ev.length > 5 && s.ev !== '…' && /الربح/.test(s.pl) && s.stale === 0), seen.map(s => [s.kind, s.marks, s.ev.slice(0, 30), s.stale]));
  ok('… «↩️ رجوع إلى النموذج» brings the form back with what was typed and the kind still chosen · the example stops',
     forms.every(f => f.kept && f.form && f.run && f.sel1 === f.sel0), forms.map(f => [f.fn, f.kept, f.form, f.sel0, f.sel1, f.run]));
  // pause · closing
  await pg.evaluate(() => { hideModal(); openDeployVa() }); await pg.waitForTimeout(900);
  await pg.evaluate(() => document.querySelector('#modal .tutone').click()); await pg.waitForTimeout(1500);
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
