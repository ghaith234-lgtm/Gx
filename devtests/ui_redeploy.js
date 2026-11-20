// ♻️ v3.36.65 in a real browser (run through ui_redeploy.py — every kind of bot in a closed folder · launches faked · no network):
//   the owner (20-11): «اريد عند مسح بوت اقدر ارجعه يعني انسخ اعداداته ويبدي من جديد واقدر اعدل عليه قبل ما انشره ، يعني حولني تلقائيا وكانما نشر البوت»
//   ① 🗄️ the archive: every deleted bot has «♻️ انشره من جديد»
//   ② for every bot on the page: 🗑 (the page's own delete) ⇒ the offer «♻️ حُذف البوت — هل تنشره من جديد؟» ⇒ its own deploy form opens,
//     filled, with the line «♻️ من الأرشيف …» on top ⇒ «🚀 انشر وشغّل» (the page's own button) ⇒ a new bot (ui_redeploy.py compares the settings)
//   ③ the form can be edited before deploying (a changed field goes out as typed)
//   ④ no key ever reaches the page (the archive and the re-deploy answers) · a wrong name ⇒ a clear message, nothing opens
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2], OUT = process.argv[3], Q = process.argv.includes('-q');
const res = [], J = {};
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 1200)));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const br = await chromium.launch();
  const errs = [];
  const ctx = await br.newContext({ viewport: { width: 1280, height: 900 } });
  await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 15, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await sleep(1200);
  // every answer the page gets — for the key check and the deploy results
  await pg.evaluate(() => { const o = api; window.__ANS = []; api = async (p, b, q) => { const r = await o(p, b, q); window.__ANS.push({ p, r }); return r } });
  const bots = await pg.evaluate(() => DATA.bots.map(b => ({ dir: b.dir, sym: b.symbol, t: b.bot_type, demo: !!b.demo, plus: !!(b.dca && b.dca.plus) })));
  const FORM = { grid: 'n', grid_range: 'n', grid_plus: 'n', grid_step: 'st', dca: 'dn', dca_buy: 'dn', rec_buy: 'rd', rec_sell: 'rd', rec_va: 'vd' };
  const done = [];
  let first = true;
  for (const b of bots) {
    // 🗑 the page's own delete (the same call as the drawer's «🗑 أرشفة فقط» after its confirm)
    await pg.evaluate(d => ctl(d, 'delete'), b.dir);
    await pg.waitForFunction(() => { const h = document.querySelector('#modal h2'); return h && h.textContent.includes('حُذف البوت') }, null, { timeout: 15000 }).catch(() => {});
    const off = await pg.evaluate(() => { const h = document.querySelector('#modal h2'), bt = [...document.querySelectorAll('#modal .mbtns button')].map(x => x.textContent);
      return { h: h ? h.textContent : '', bt, p: (document.querySelector('#modal p') || {}).textContent || '' } });
    if (first) ok(`② 🗑 a delete ⇒ the offer comes: «${off.h}» · ${off.bt.join(' | ')}`, off.h.includes('♻️ حُذف البوت — هل تنشره من جديد؟') && off.bt[0].includes('♻️ افتح نموذج النشر بإعداداته')
       && off.bt[1] === 'لا' && off.p.includes('🗄️ الأرشيف'), off);
    await pg.evaluate(() => [...document.querySelectorAll('#modal .mbtns button')][0].click());
    const p = FORM[b.t];
    await pg.waitForFunction(p => !!document.getElementById(p + '_go') && !!document.querySelector('#modal .rdnote'), p, { timeout: 15000 }).catch(() => {});
    await sleep(b.plus ? 900 : 350);
    const f = await pg.evaluate(([p, b]) => {
      const note = (document.querySelector('#modal .rdnote') || {}).textContent || '';
      const body = { n: () => gridFormBody(), st: () => stBody(), dn: () => dcaFormBody(), rd: () => recFormBody(), vd: () => vaFormBody() }[p]();
      const dv = demoVal(p);
      return { note, body, dv, wallet: (document.getElementById(p + '_wallet') || {}).value, go: !!document.getElementById(p + '_go') };
    }, [p, b]);
    const okForm = f.go && f.note.includes('♻️ من الأرشيف') && f.note.includes(b.sym) && f.body.symbol === b.sym;
    if (b.demo) {
      J.demo = { ok: okForm && f.dv.demo === true && +f.dv.demo_usd === 432.5 && +f.dv.demo_coin === 2.75 && f.note.includes('🧪 ديمو'), f };
      ok(`② 🧪 ${b.sym} (demo): its form opened as a demo with its starting balances (${f.dv.demo_usd}$ · ${f.dv.demo_coin})`, J.demo.ok, f);
      await pg.evaluate(() => hideModal()); await sleep(400);
      continue;
    }
    if (first) {
      // ③ the form can be edited before deploying: change the symbol's amount field and put it back — the body follows what is typed
      const ed = await pg.evaluate(p => { const id = { n: 'n_usd', st: 'st_q', dn: 'dn_ex', rd: 'rd_amt', vd: 'vd_start' }[p], e = document.getElementById(id), v0 = e.value;
        e.value = '77'; e.dispatchEvent(new Event('input', { bubbles: true }));
        const got = ({ n: () => gridFormBody().usd_value, st: () => stBody().usd_value, dn: () => dcaFormBody().exchange_orders, rd: () => recFormBody().amount, vd: () => vaFormBody().start_usd })[p]();
        e.value = v0; e.dispatchEvent(new Event('input', { bubbles: true })); return { got, back: e.value === v0 } }, p);
      ok(`③ the filled form is editable before deploying (a field changed to 77 goes out as ${ed.got}) · the line on top: «${f.note.slice(0, 120)}…»`, ed.got === '77' && ed.back, ed);
      first = false;
    }
    const n0 = await pg.evaluate(() => window.__ANS.length);
    await pg.evaluate(p => document.getElementById(p + '_go').click(), p);
    await pg.waitForFunction(n0 => window.__ANS.slice(n0).some(a => /^\/api\/deploy/.test(a.p)), n0, { timeout: 20000 }).catch(() => {});
    const dep = await pg.evaluate(n0 => (window.__ANS.slice(n0).find(a => /^\/api\/deploy/.test(a.p)) || {}), n0);
    done.push({ sym: b.sym, t: b.t, plus: b.plus, wallet: f.wallet, ok: !!(dep.r && dep.r.ok), msg: dep.r && dep.r.msg, p: dep.p });
    await sleep(300);
    await pg.evaluate(() => { try { hideModal() } catch (e) {} }); await sleep(250);
  }
  const bad = done.filter(x => !x.ok || x.wallet !== 'main');
  ok(`② every real bot (${done.length}): deleted ⇒ its own form, filled, its wallet «main» chosen ⇒ «🚀 انشر وشغّل» ⇒ deployed (${[...new Set(done.map(x => x.p))].join(' · ')})`,
     done.length >= 14 && !bad.length, bad.length ? bad : done.map(x => x.sym + ' ' + x.msg));
  // ① the archive
  await pg.evaluate(() => openArchive()); await sleep(1500);
  const ar = await pg.evaluate(() => { const rows = [...document.querySelectorAll('#modal .arch')];
    return { n: rows.length, btn: rows.filter(r => [...r.querySelectorAll('button')].some(b => b.textContent.includes('♻️ انشره من جديد'))).length,
      head: ((document.querySelector('#ar_body') || {}).textContent || '').slice(0, 300) } });
  ok(`① 🗄️ the archive: every deleted bot (${ar.n}) has «♻️ انشره من جديد» (${ar.btn}) · the head says what it does`, ar.n === bots.length && ar.btn === ar.n && ar.head.includes('♻️ انشره من جديد'), ar);
  const ab = await pg.evaluate(async () => { const r = [...document.querySelectorAll('#modal .arch')].find(x => x.textContent.includes('DOGE-USDT'));
    [...r.querySelectorAll('button')].find(b => b.textContent.includes('♻️'))?.click(); await new Promise(z => setTimeout(z, 1500));
    return { note: ((document.querySelector('#modal .rdnote') || {}).textContent || ''), type: (document.getElementById('dn_type') || {}).value, sym: (document.getElementById('dn_sym') || {}).value,
      n: (document.getElementById('dn_n') || {}).value } });
  ok(`① … its button opens that bot's form filled (DOGE-USDT · 📉 DCA: type ${ab.type} · ${ab.n} safety orders)`, ab.note.includes('DOGE-USDT') && ab.type === 'dca' && ab.sym === 'DOGE-USDT' && ab.n === '4', ab);
  await pg.evaluate(() => hideModal()); await sleep(300);
  // ④ no key reaches the page · a wrong name
  const keys = await pg.evaluate(() => { const s = JSON.stringify(window.__ANS.filter(a => /^\/api\/(archive|archive_redeploy|control)/.test(a.p)));
    return { n: window.__ANS.filter(a => a.p.startsWith('/api/archive_redeploy')).length, leak: ['KEYA', 'SECA', 'PASA', 'devtests-k', 'api_key', 'secret_key', 'passphrase'].filter(k => s.includes(k)) } });
  ok(`④ no key in any answer the page got (${keys.n} re-deploy answers · the archive · the deletes)`, keys.n >= 15 && !keys.leak.length, keys);
  const wr = await pg.evaluate(async () => { const m0 = document.getElementById('modal').innerHTML; const r = await rdOpen('../../etc'); await new Promise(z => setTimeout(z, 400));
    return { r, modal: document.getElementById('modal').innerHTML !== m0, toast: ((document.querySelector('.toast,#toast') || {}).textContent || '') } });
  ok(`④ a wrong name (../../etc) ⇒ nothing opens · «${wr.toast.slice(0, 60)}»`, wr.r === null && !wr.modal, wr);
  ok(`no page error (${errs.length})`, !errs.length, errs.slice(0, 3));
  fs.writeFileSync(OUT, JSON.stringify(J));
  await br.close();
  const n = res.filter(Boolean).length;
  console.log(n === res.length ? `✅ ui_redeploy.js: ${n}/${res.length}` : `❌ ui_redeploy.js: ${n}/${res.length}`);
  process.exit(n === res.length ? 0 : 1);
})().catch(e => { console.log('❌ crash ' + e); try { fs.writeFileSync(OUT, JSON.stringify(J)) } catch (x) {} process.exit(1) });
