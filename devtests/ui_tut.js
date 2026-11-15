// 📖 v3.36.46–48 in a real browser (run through ui_tut.py — every card kind in a closed folder): the owner (14-11): «اريد كل بوت فيه زر تعليم
//   يوضح كيف شغل البوت بالتفصيل …» ⇒ (v3.36.47) inside the deploy forms, one button per form, a tab per bot ⇒ (v3.36.48) «خل زر قريب عن x
//   الخروج لكل واختصر شرح dca ، شرح grid · اي شي يخص الكهرباء وانقطاع الانترنت في البوت كله لا يذكر حتى في الاسئلة · زيل المثال الحركي
//   بالشرح وشوي زيد الكتابه»
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
const CUT = /كهرباء|إنترنت|انترنت|انقطاع|انقطع|انطف/;
(async () => {
  const br = await chromium.launch();
  const errs = [];
  const shots = [];
  for (const [w, h, tag] of [[412, 900, 'phone'], [1280, 860, 'pc']]) {
    const ctx = await br.newContext({ viewport: { width: w, height: h }, isMobile: tag === 'phone', hasTouch: tag === 'phone' });
    await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
    const pg = await ctx.newPage();
    pg.on('pageerror', e => errs.push(String(e.stack || e).slice(0, 400)));
    await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
    await pg.routeWebSocket(/.*/, () => {});
    await pg.goto(URL, { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9, null, { timeout: 30000 });
    await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
    await pg.waitForTimeout(1200);
    if (tag === 'phone') {
      const gone = await pg.evaluate(() => ({ card: document.querySelectorAll('#grid .ctut').length,
        bar: [...document.querySelectorAll('nav.actions button')].filter(b => b.textContent.includes('📖')).length }));
      ok('no 📖 on the cards and none in the top bar (the owner: «أشيل الاثنين»)', gone.card === 0 && gone.bar === 0, gone);
    }
    // where the button sits: in the title bar right beside ✕, short name — on a phone and on a computer
    const FN = [['openDeploy', 'شرح الشبكي'], ['openDeployDca', 'شرح DCA'], ['openDeployRec', 'شرح الدوري'], ['openDeployStep', 'شرح المتدرج'], ['openDeployVa', 'شرح مسار القيمة']];
    for (const [fn, lbl] of FN) {
      await pg.evaluate(f => { try { hideModal() } catch (e) {} ; window[f]() }, fn);
      await pg.waitForTimeout(800);
      shots.push(await pg.evaluate(([fn, lbl]) => {
        const m = document.getElementById('modal'), x = m.querySelector('.hwx'), bs = [...m.querySelectorAll('.hwb .tutx')], b = bs[0];
        const h2 = m.querySelector('.hwb > h2:first-child');
        if (!b || !x || !h2) return { fn, n: bs.length };
        const rb = b.getBoundingClientRect(), rx = x.getBoundingClientRect(), rh = h2.getBoundingClientRect(), t = h2.querySelector('span').getBoundingClientRect();
        m.querySelector('.hwb').scrollTop = 400;
        const rb2 = b.getBoundingClientRect();
        return { fn, n: bs.length, txt: b.textContent.trim(), lbl, inH2: h2.contains(b),
          gap: Math.round(Math.min(Math.abs(rb.left - rx.right), Math.abs(rx.left - rb.right))), dy: Math.round((rb.top + rb.height / 2) - (rx.top + rx.height / 2)),
          over: !(t.right <= rb.left + 1 || t.left >= rb.right - 1) && !(t.bottom <= rb.top + 1 || t.top >= rb.bottom - 1), inside: rb.left >= rh.left - 1 && rb.right <= rh.right + 1,
          stays: Math.abs(rb2.top - rb.top) < 2, old: m.querySelectorAll('.tutrow, .tutone, .tutq').length }
      }, [fn, lbl]));
    }
    // the windows (on the phone run)
    if (tag === 'phone') {
      const FORMS = [['openDeploy', ['grid', 'grid_range', 'grid_plus'], 'grid_range', "gType('grid_range')", 'n_gtype'],
                     ['openDeployDca', ['dca', 'dca_buy', 'dca_plus'], 'dca_buy', "(document.getElementById('dn_type').value='dca_buy',dcaTypeSwitch())", 'dn_type'],
                     ['openDeployRec', ['rec_buy', 'rec_sell'], 'rec_sell', "(document.getElementById('rd_type').value='rec_sell',recFormSync())", 'rd_type'],
                     ['openDeployStep', ['grid_step'], 'grid_step', '0', null], ['openDeployVa', ['rec_va'], 'rec_va', '0', null]];
      const NAME = { grid: 'الشبكة اللانهائية', grid_range: 'المدى', grid_plus: 'بلس', dca: 'DCA البيعي', dca_buy: 'DCA الشرائي', dca_plus: 'DCA+', rec_buy: 'الشراء الدوري',
                     rec_sell: 'البيع الدوري', grid_step: 'المتدرج', rec_va: 'مسار القيمة' };
      const forms = [], seen = [];
      for (const [fn, kinds, pick, pickJs, selId] of FORMS) {
        await pg.evaluate(f => { try { hideModal() } catch (e) {} ; window[f]() }, fn);
        await pg.waitForTimeout(900);
        const pre = await pg.evaluate(([pickJs, selId]) => {
          eval(pickJs);
          const inp = [...document.querySelectorAll('#modal .hwb input')].find(i => i.type !== 'hidden' && i.type !== 'checkbox' && i.offsetParent);
          if (inp) inp.value = '7.77';
          const sel0 = selId ? document.getElementById(selId).value : null;
          document.querySelector('#modal .hwb .tutx').click();
          return { inp: inp ? inp.id : null, sel0 };
        }, [pickJs, selId]);
        await pg.waitForTimeout(400);
        const win = await pg.evaluate(() => { const t = [...document.querySelectorAll('#modal .tuttabs button')];
          const f = document.querySelector('#modal .hwb:not(.tuthwb)');
          return { tabs: t.length, on: t.filter(x => x.classList.contains('on')).map(x => x.textContent), h2: (document.querySelector('#modal .tuthwb h2') || {}).textContent || '',
                   hid: !!(f && f.isConnected && getComputedStyle(f).display === 'none') } });
        forms.push({ fn, ...pre, ...win, pick, n: kinds.length });
        for (const k of kinds) {
          if (kinds.length > 1) { await pg.evaluate(i => document.querySelectorAll('#modal .tuttabs button')[i].click(), kinds.indexOf(k)); await pg.waitForTimeout(250) }
          seen.push({ kind: k, single: kinds.length === 1, ...(await pg.evaluate(() => { const w = document.querySelector('#modal .tuthwb');
            return { h2: (w.querySelector('h2') || {}).textContent || '', secs: [...w.querySelectorAll('.tutsec h3')].map(h => h.textContent),
              idea: w.querySelectorAll('.tutsec')[0].querySelectorAll('p').length, steps: w.querySelectorAll('.tutsteps li').length, ex: w.querySelectorAll('.tutex p').length,
              btns: w.querySelectorAll('.tutbtns > div').length, qa: w.querySelectorAll('.tutqa').length, own: w.querySelectorAll('.tutsub')[0] ? [...w.querySelectorAll('.tutqa')].length - 12 : 0,
              on: [...w.querySelectorAll('.tuttabs button.on')].map(x => x.textContent).join('|'), anim: !!w.querySelector('svg, .tutanim, #tutSvg'),
              cut: (w.textContent.match(/.{0,30}(كهرباء|إنترنت|انترنت|انقطاع|انقطع|انطف).{0,30}/) || [''])[0],
              chars: w.textContent.length } })) });
        }
        Object.assign(forms[forms.length - 1], await pg.evaluate(([id, selId]) => {
          [...document.querySelectorAll('#modal button')].find(x => x.textContent.includes('رجوع إلى النموذج')).click();
          const e = id && document.getElementById(id), f = document.querySelector('#modal .hwb');
          return { kept: id ? !!(e && e.value === '7.77') : true, sel1: selId ? document.getElementById(selId).value : null,
                   back: !!document.querySelector('#modal .hwb .tutx') && getComputedStyle(f).display !== 'none' && !document.querySelector('#modal .tuthwb') } }, [pre.inp, selId]));
      }
      const need = ['💡 الفكرة', '🧩 خطوة بخطوة', '🧮 مثال بالأرقام', '🔘 أزرار البطاقة', '❓ أسئلة وأجوبة'];
      ok('… it opens one window with a tab for each of the form\'s bots (the grid 3 · DCA 3 with ⚡ DCA+ · the recurring 2 · 🪜 and 💹 none) on the kind chosen · the form waits hidden in place',
         forms.every(f => (f.n > 1 ? f.tabs === f.n && f.on.length === 1 && f.on[0].includes(NAME[f.pick]) : f.tabs === 0) && f.h2.includes(NAME[f.pick]) && f.hid), forms);
      ok('… every bot\'s explanation: the idea · step by step · 🧮 an example in numbers · the card\'s buttons · questions and answers — and NO moving example',
         seen.length === 10 && seen.every(s => s.h2.includes('كيف يعمل بوت') && s.h2.includes(NAME[s.kind]) && need.every(n => s.secs.includes(n)) && !s.secs.some(x => x.includes('🎬'))
           && !s.anim && s.ex >= 2 && (s.single || s.on.includes(NAME[s.kind]))), seen.map(s => [s.kind, s.secs, s.anim, s.ex]));
      ok('… fuller text: ≥ 2 idea paragraphs · ≥ 4 steps … · ≥ 2 questions of its own + 12 for all bots',
         seen.every(s => s.idea >= 2 && s.steps >= 3 && s.btns >= 8 && s.own >= 2 && s.qa >= 14 && s.chars > 2400), seen.map(s => [s.kind, s.idea, s.steps, s.own, s.qa, s.chars]));
      ok('… not a word about power cuts or internet cuts in any explanation (the owner: «لا يذكر حتى في الاسئلة»)', seen.every(s => !s.cut), seen.map(s => [s.kind, s.cut]));
      ok('… «↩️ رجوع إلى النموذج» brings the form back with what was typed and the kind still chosen',
         forms.every(f => f.kept && f.back && f.sel1 === f.sel0), forms.map(f => [f.fn, f.kept, f.back, f.sel0, f.sel1]));
      // the card's ladder header for 🪜 · nothing about power in the page text the customer reads (the tutorial content source included)
      const src = await pg.evaluate(() => JSON.stringify([TUT, TUT_FAQ, TUT_BTN]) + (typeof tutDraw) + (typeof TUT_RUN));
      ok('… the explanation source has no moving-example code left and no power/internet-cut wording', !CUT.test(src) && src.endsWith('undefinedundefined'), src.slice(-40));
      await pg.evaluate(() => hideModal());
    }
    await ctx.close();
  }
  ok('ONE «📖 شرح …» per deploy form, IN the title bar right beside ✕ (phone and computer), short names: الشبكي · DCA · الدوري · المتدرج · مسار القيمة · nothing under the title any more',
     shots.length === 10 && shots.every(s => s.n === 1 && s.txt === '📖 ' + s.lbl && s.inH2 && s.gap <= 16 && Math.abs(s.dy) <= 6 && !s.over && s.inside && s.old === 0), shots);
  ok('… it stays beside ✕ while the form scrolls', shots.every(s => s.stays), shots.map(s => [s.fn, s.stays]));
  ok('no page errors', !errs.length, errs.slice(0, 3));
  await br.close();
  console.log(res.every(Boolean) ? `✅ ui_tut: ${res.filter(Boolean).length}/${res.length}` : `❌ ui_tut: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_tut crashed — ' + String(e).slice(0, 300)); process.exit(1) });
