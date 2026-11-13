// 🪟 v3.36.34 in a real browser (run through ui_windows.py — every card kind in a closed folder): the one window frame · the dialogs that
//   keep their size · the seven motions from ⚙️ · the back button (app: holyBack · phone browser: history) · the order of windows
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
async function open(br, vw, vh, anim, errs, extra) {
  const ctx = await br.newContext({ viewport: { width: vw, height: vh } });
  await ctx.addInitScript(([a, x]) => { try { localStorage.setItem('dash_stick', 'off'); if (a) localStorage.setItem('dash_anim', a); else localStorage.removeItem('dash_anim');
    if (x) localStorage.setItem('dash_skin', x) } catch (e) {} }, [anim, extra || null]);
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9 && typeof HW !== 'undefined', null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(1500);
  return { ctx, pg };
}
const FULL = [   // [name, opener] — every kind of big window
  ['⚙️ الإعدادات', 'openSettings()'], ['🗄️ الأرشيف', 'openArchive()'], ['📉 الخسائر', 'openLosses()'], ['🛡️ الرقابة', 'openGuard()'],
  ['📱 أندرويد', 'openAppPanel()'], ['💻 ويندوز', 'openWinPanel()'], ['📊 المؤشرات', 'openInd()'], ['🔮 التوقعات', 'openFc()'],
  ['📈 الشريط', 'openTicker()'], ['🧾 سجل اليوم', 'openDayLog()'], ['📖 الدليل', 'openGuide()'], ['🧰 المكتبات', 'openLibs()'],
  ['📄 التقرير التشخيصي', 'openExport()'], ['🐧 الإقلاع', 'openBoot()'], ['🔐 الحماية', 'openSecurity()'], ['➕ نشر جرد', 'openDeploy()'],
  ['📊 نشر DCA', 'openDeployDca()'], ['🪜 نشر متدرج', 'openDeployStep()'], ['🔁 نشر دوري', 'openDeployRec()'], ['💹 نشر مسار', 'openDeployVa()'],
  ['⚙ تفاصيل ♾️', "gridDetails(DATA.bots.find(b=>b.bot_type==='grid'))"], ['⚙ تفاصيل DCA', "dcaDetails(DATA.bots.find(b=>b.bot_type==='dca'))"],
  ['⚙ تفاصيل 🔁', "recDetails(DATA.bots.find(b=>b.bot_type==='rec_buy'))"], ['⚙ تفاصيل 💹', "vaDetails(DATA.bots.find(b=>b.bot_type==='rec_va'))"],
  ['📜 سجل بوت', "botHist(DATA.bots.find(b=>b.bot_type==='grid'))"], ['📋 جدول DCA', "dcaTable(DATA.bots.find(b=>b.bot_type==='dca'))"],
];
const SMALL = [
  ['🗑 متأكد؟', "askConfirm('🗑 حذف البوت؟','سيُلغى كل أوامره.',()=>{})"], ['🛡️ الدرع', "dcaShield(DATA.bots.find(b=>b.bot_type==='dca'))"],
  ['🏁 آخر دورة', "dcaLast(DATA.bots.find(b=>b.bot_type==='dca'))"], ['🛒 اشتري هسه', "recNow(DATA.bots.find(b=>b.bot_type==='rec_buy'))"],
  ['📏 النطاق', "recRange(DATA.bots.find(b=>b.bot_type==='rec_buy'))"],
];
(async () => {
  const br = await chromium.launch();
  const errs = [];
  // ── the frame on a computer
  let { ctx, pg } = await open(br, 1440, 900, 'none', errs);
  const geo = [], badSmall = [];
  for (const [nm, js] of FULL) {
    await pg.evaluate(js); await pg.waitForTimeout(250);
    geo.push(await pg.evaluate(nm => { const bg = document.getElementById('mbg'), m = document.getElementById('modal'), r = m.getBoundingClientRect(),
      x = m.querySelector(':scope>.hwx'), xr = x ? x.getBoundingClientRect() : null, h = m.querySelector('.hwb>h2:first-child');
      const closeBtns = [...m.querySelectorAll('.hwb button')].filter(b => b.offsetParent && /^(إغلاق|رجوع)$/.test(b.textContent.trim()) && (b.getAttribute('onclick') || '').replace(/\s/g, '') === 'hideModal()').length;
      return { nm, open: !bg.hidden, full: bg.classList.contains('full'), w: Math.round(r.width), h: Math.round(r.height), top: Math.round(r.top),
        x: !!xr, xin: xr ? xr.left - r.left < 70 && xr.top - r.top < 60 && xr.width >= 30 : false, head: h ? getComputedStyle(h).position : null, closeBtns } }, nm));
    await pg.evaluate(() => hideModal());
  }
  const off = geo.filter(g => !(g.open && g.full && g.w === 1180 && g.h === 900 - 44 && g.top === 22 && g.x && g.xin && g.head === 'sticky' && g.closeBtns === 0));
  ok(`🪟 computer: ${FULL.length} kinds of window — one frame (1180 × ${900 - 44} with 22 px around) · the title stays on top · ✕ in the same corner · no lone «إغلاق»`, !off.length, off);
  for (const [nm, js] of SMALL) {
    await pg.evaluate(js); await pg.waitForTimeout(200);
    const g = await pg.evaluate(() => { const bg = document.getElementById('mbg'), m = document.getElementById('modal'), r = m.getBoundingClientRect(), x = m.querySelector(':scope>.hwx');
      return { small: bg.classList.contains('small'), w: Math.round(r.width), h: Math.round(r.height), x: !!x, btns: [...m.querySelectorAll('.hwb .mbtns button')].filter(b => b.offsetParent).length } });
    if (!(g.small && g.w <= 860 && g.h < 900 - 44 && g.x && g.btns >= 1)) badSmall.push([nm, g]);
    await pg.evaluate(() => hideModal());
  }
  ok(`🪟 confirmations and their kind (${SMALL.length}): their size as before (≤ 860 px · not the full height) in the new look — ✕ and their own buttons («إلغاء» · «تأكيد» …)`, !badSmall.length, badSmall);
  // pages · trial · notifications
  await pg.evaluate(() => openReports()); await pg.waitForTimeout(300);
  const pr = await pg.evaluate(() => { const p = document.getElementById('page_reports'), w = p.querySelector('.pwrap').getBoundingClientRect(), x = p.querySelector('.phead .x').getBoundingClientRect(), h = p.querySelector('.phead');
    return { w: Math.round(w.width), top: Math.round(w.top), xin: x.left - w.left < 80 && x.width >= 30, head: getComputedStyle(h).position } });
  ok('🪟 the pages (📊 التقارير …): the same frame (1180 · 22 px around) · ✕ in the same corner · the title stays on top', pr.w === 1180 && pr.top === 22 && pr.xin && pr.head === 'sticky', pr);
  // ── the order and the back button (computer = a browser: history)
  await pg.evaluate(() => openSettings()); await pg.waitForTimeout(300);
  const z = await pg.evaluate(() => ({ m: +getComputedStyle(document.getElementById('mbg')).zIndex, p: +getComputedStyle(document.getElementById('page_reports')).zIndex, st: HW.st.map(x => x.k), hs: history.state }));
  ok(`↩️ a window over a page is drawn above it (z ${z.m} > ${z.p}) · the stack «${z.st.join(' › ')}» · the browser has an entry for it`, z.m > z.p && z.st.join() === 'page_reports,modal' && z.hs && z.hs.hw === 'modal', z);
  let b1 = await pg.evaluate(() => holyBack()); await pg.waitForTimeout(250);
  let s1 = await pg.evaluate(() => ({ m: !document.getElementById('mbg').hidden, p: document.getElementById('page_reports').classList.contains('on') }));
  let b2 = await pg.evaluate(() => holyBack()); await pg.waitForTimeout(250);
  let s2 = await pg.evaluate(() => ({ p: document.getElementById('page_reports').classList.contains('on'), st: HW.st.length }));
  let b3 = await pg.evaluate(() => holyBack());
  ok('↩️ back closes the top first: the window (the page stays) · then the page · then nothing is open ⇒ «false» (the app leaves)', b1 && !s1.m && s1.p && b2 && !s2.p && s2.st === 0 && b3 === false, { b1, s1, b2, s2, b3 });
  await pg.evaluate(() => openSettings()); await pg.waitForTimeout(200);
  await pg.goBack().catch(() => null); await pg.waitForTimeout(400);
  const hb = await pg.evaluate(() => ({ m: !document.getElementById('mbg').hidden, url: location.href, st: HW.st.length }));
  ok('↩️ the phone browser\'s back closes the window (and stays on the dashboard)', !hb.m && hb.st === 0 && hb.url.startsWith(URL.replace(/\/$/, '')), hb);
  await pg.evaluate(() => openSettings()); await pg.waitForTimeout(200);
  await pg.evaluate(() => document.querySelector('#modal>.hwx').click()); await pg.waitForTimeout(400);
  const hx = await pg.evaluate(() => ({ m: !document.getElementById('mbg').hidden, hs: history.state }));
  ok('↩️ closed with ✕ ⇒ its browser entry goes too (the next back is not wasted)', !hx.m && !(hx.hs && hx.hs.hw), hx);
  // ↩️ v3.36.35: a close and an open in one step (a confirmation whose «تأكيد» opens a window) — the browser stays on the dashboard
  //   (v3.36.34: the closing's back took the new window's entry ⇒ closing that window went back out of the dashboard)
  await pg.evaluate(() => askConfirm('🧪', 'x', () => openSettings())); await pg.waitForTimeout(300);
  await pg.evaluate(() => document.getElementById('cf_y').click()); await pg.waitForTimeout(400);
  const cw1 = await pg.evaluate(() => ({ m: !document.getElementById('mbg').hidden, st: HW.st.map(x => x.k + (x.h ? '*' : '')).join(), hs: history.state && history.state.hw }));
  await pg.goBack().catch(() => null); await pg.waitForTimeout(400);
  const cw2 = await pg.evaluate(() => ({ m: !document.getElementById('mbg').hidden, url: location.href })).catch(() => ({ gone: true }));
  await pg.evaluate(() => openSettings()).catch(() => null); await pg.waitForTimeout(300);
  await pg.evaluate(() => { hideModal(); setTimeout(openSettings, 1) }).catch(() => null); await pg.waitForTimeout(400);
  const cw3 = await pg.evaluate(() => ({ m: !document.getElementById('mbg').hidden, st: HW.st.map(x => x.k + (x.h ? '*' : '')).join() })).catch(() => ({ gone: true }));
  await pg.evaluate(() => hideModal()).catch(() => null); await pg.waitForTimeout(400);
  const cw4 = await pg.evaluate(() => ({ url: location.href, st: HW.st.length, skip: HW.skip, pend: HW.pend })).catch(() => ({ gone: true }));
  const home = u => !!u && u.startsWith(URL.replace(/\/$/, ''));
  ok('↩️ «تأكيد» that opens a window · back closes that window · close-then-open a moment later · close: the browser stays on the dashboard every time',
    cw1.m && cw1.st === 'modal*' && cw1.hs === 'modal' && !cw2.gone && !cw2.m && home(cw2.url) && cw3.m && cw3.st === 'modal*' && !cw4.gone && home(cw4.url) && cw4.st === 0 && !cw4.skip && !cw4.pend,
    { cw1, cw2, cw3, cw4 });
  await pg.evaluate(() => btOpen({ dir: DATA.bots.find(b => b.bot_type === 'grid').dir })); await pg.waitForTimeout(600);
  const bt0 = await pg.evaluate(() => ({ on: !!document.getElementById('btov'), st: HW.st.map(x => x.k) }));
  const btb = await pg.evaluate(() => holyBack()); await pg.waitForTimeout(250);
  const bt1 = await pg.evaluate(() => !!document.getElementById('btov'));
  ok('↩️ the trial window: in the stack · back closes it (it used to leave the app)', bt0.on && bt0.st.includes('bt') && btb && !bt1, { bt0, btb, bt1 });
  await pg.evaluate(() => toggleNotif()); await pg.waitForTimeout(250);
  const npb = await pg.evaluate(() => holyBack()); await pg.waitForTimeout(250);
  ok('↩️ the notifications: back closes them', npb && !(await pg.evaluate(() => npOpen)), npb);
  await pg.keyboard.press('Escape');
  await pg.evaluate(() => { openReports(); openSettings() }); await pg.waitForTimeout(250);
  await pg.keyboard.press('Escape'); await pg.waitForTimeout(250);
  const esc = await pg.evaluate(() => ({ m: !document.getElementById('mbg').hidden, p: document.getElementById('page_reports').classList.contains('on') }));
  ok('↩️ Esc = back: the top only (the window), the page stays', !esc.m && esc.p, esc);
  await pg.evaluate(() => { while (holyBack()); });
  // ── ⚙️ the motions
  await pg.evaluate(() => openSettings()); await pg.waitForTimeout(250);
  const ar = await pg.evaluate(() => [...document.querySelectorAll('#animRow button')].map(b => [b.dataset.anim, b.textContent, b.classList.contains('on')]));
  ok(`🎬 ⚙️ «حركة فتح النوافذ»: ${ar.length} choices (${ar.map(a => a[1]).join(' · ')})`, ar.length === 7 && ar.map(a => a[0]).join() === 'none,up,zoom,side,btn,blur,spring', ar);
  await pg.evaluate(() => setAnim('blur')); await pg.waitForTimeout(900);
  const sa = await pg.evaluate(() => ({ ls: localStorage.getItem('dash_anim'), open: !document.getElementById('mbg').hidden, on: (document.querySelector('#animRow button.on') || {}).dataset }));
  ok('🎬 choosing one keeps it on this device and opens ⚙️ again with it (so it is seen)', sa.ls === 'blur' && sa.open && sa.on && sa.on.anim === 'blur', sa);
  await pg.evaluate(() => hideModal());
  await ctx.close();
  const mot = [];
  for (const a of ['none', 'up', 'zoom', 'side', 'btn', 'blur', 'spring']) {
    ({ ctx, pg } = await open(br, 1440, 900, a === 'zoom' ? null : a, errs));
    await pg.mouse.move(300, 200); await pg.mouse.down(); await pg.mouse.up();
    const r = await pg.evaluate(() => { openSettings(); const m = document.getElementById('modal');
      const an = m.getAnimations().map(x => { const k = x.effect.getKeyframes()[0] || {}; return Object.keys(k).filter(z => !/^(offset|easing|composite|computedOffset)$/.test(z)).join('+') });
      return { an, style: hwStyle() } });
    await pg.waitForTimeout(600);
    const c0 = await pg.evaluate(() => { document.querySelector('#modal>.hwx').click(); return { hidden: document.getElementById('mbg').hidden, clone: document.querySelectorAll('.hwclone').length } });
    await pg.waitForTimeout(700);
    const c1 = await pg.evaluate(() => document.querySelectorAll('.hwclone').length);
    mot.push({ a, ...r, c0, c1 });
    await ctx.close();
  }
  const want = { none: '', up: 'transform', zoom: 'opacity+transform', side: 'opacity+transform', btn: 'opacity+transform',   // v3.36.35: grows from the tapped point by scale (was a clip)
    blur: 'filter+opacity+transform', spring: 'opacity+transform' };
  const badM = mot.filter(m => (m.an[0] || '') !== want[m.a] || !m.c0.hidden || (m.a === 'none' ? m.c0.clone !== 0 : m.c0.clone !== 1) || m.c1 !== 0 || (m.a === 'zoom' && m.style !== 'zoom'));
  ok(`🎬 each of the 7 opens with its own motion (default «تكبير ناعم») · closing: the window is closed at once and a copy plays it backwards, then is gone`, !badM.length, badM.length ? badM : mot.map(m => m.a + ':' + (m.an[0] || '—')));
  ({ ctx, pg } = await open(br, 1440, 900, 'spring', errs));
  const lite = await pg.evaluate(() => { document.documentElement.classList.add('lite'); openSettings(); return document.getElementById('modal').getAnimations().length });
  ok('🎬 «⚡ الوضع الخفيف» ⇒ no motion even when one is chosen', lite === 0, lite);
  await ctx.close();
  // ── the phone: everything fills the screen · the confirmation keeps its size · the card «⋯» menu closes on back
  ({ ctx, pg } = await open(br, 412, 860, 'none', errs, 'b'));
  const ph = [];
  for (const [nm, js] of FULL.slice(0, 6)) {
    await pg.evaluate(js); await pg.waitForTimeout(200);
    ph.push(await pg.evaluate(nm => { const r = document.getElementById('modal').getBoundingClientRect(); return { nm, w: Math.round(r.width), h: Math.round(r.height), t: Math.round(r.top) } }, nm));
    await pg.evaluate(() => hideModal());
  }
  ok('📱 phone: every window fills the screen (412 × 860)', ph.every(g => g.w === 412 && g.h === 860 && g.t === 0), ph);
  await pg.evaluate(() => askConfirm('🗑 حذف؟', 'نص قصير', () => {})); await pg.waitForTimeout(200);
  const pc = await pg.evaluate(() => { const r = document.getElementById('modal').getBoundingClientRect(); return { w: Math.round(r.width), h: Math.round(r.height) } });
  ok(`📱 phone: the confirmation keeps its size (${pc.w} × ${pc.h})`, pc.w < 412 && pc.h < 500, pc);
  await pg.evaluate(() => hideModal());
  await pg.evaluate(() => { const c = document.querySelector('.card.sk[data-dir]'); skAct(c, 'menu') }); await pg.waitForTimeout(150);
  const mb = await pg.evaluate(() => { const c = document.querySelector('.card.sk[data-dir]'), before = !!c._skm, r = holyBack(); return { before, r, after: !!c._skm, st: HW.st.length } });
  ok('📱 the card «⋯» menu: back closes it (and only it)', mb.before && mb.r && !mb.after && mb.st === 0, mb);
  await ctx.close();
  ok('no page error', errs.length === 0, errs);
  await br.close();
  console.log(`ui_windows ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_windows crashed — ' + e); process.exit(1) });
