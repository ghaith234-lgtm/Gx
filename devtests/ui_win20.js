// 💻 v3.36.41 in a real browser (run through ui_win20.py — every card kind in a closed folder): the dashboard inside the Windows program 2.0
//   (WebView2 · no title bar) — a stand-in for the program: window.HOLYWIN + window.chrome.webview (postMessage · message events).
//   The owner (13-11): «اريد تلغي الرموز الفوق الي بالصورة واتخليهم مع ايقونة الاشعارات · كيف احرك المربع كله اذا انزال الشريط الفوق»
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
async function open(br, errs, o) {
  o = o || {};
  const ctx = await br.newContext({ viewport: { width: o.w || 1366, height: o.h || 820 } });
  await ctx.addInitScript(o => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none'); sessionStorage.setItem('holy_splash', '1') } catch (e) {}
    if (o.host) { window.__msgs = []; window.__wvL = [];
      window.HOLYWIN = { v: '2.0', ncr: false };
      window.chrome = window.chrome || {}; window.chrome.webview = { postMessage: m => window.__msgs.push(m), addEventListener: (t, f) => { if (t === 'message') window.__wvL.push(f) } };
      window.__state = d => window.__wvL.forEach(f => f({ data: d })) } }, o);
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL + (o.win ? '?holyapp=win&hv=2.0' : ''), { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9, null, { timeout: 30000 });
  await pg.waitForTimeout(1800);
  return { ctx, pg };
}
(async () => {
  const br = await chromium.launch();
  const errs = [];
  let { ctx, pg } = await open(br, errs, { win: 1, host: 1 });
  const a = await pg.evaluate(() => { const b = id => { const e = document.getElementById(id); const r = e.getBoundingClientRect(); return { show: !e.hidden && r.width > 0, x: Math.round(r.left), t: e.textContent.trim() } };
    return { winf: document.documentElement.classList.contains('winf'), min: b('wMin'), max: b('wMax'), cls: b('wCls'), bell: b('bBell'), msgs: window.__msgs.slice() } });
  const order = [a.bell, a.min, a.max, a.cls].map(x => x.x);
  ok(`💻 inside the Windows program 2.0: — ☐ ✕ beside 🔔 (left to right: 🔔 ${a.min.t} ${a.max.t} ${a.cls.t} · ✕ at the far right)`,
    a.winf && a.min.show && a.max.show && a.cls.show && order[0] < order[1] && order[1] < order[2] && order[2] < order[3] && a.min.t === '—' && a.cls.t === '✕', a);
  ok(`💻 the page asks the program for its state and tells it where its buttons are («${(a.msgs.find(m => /^hello /.test(m)) || '').slice(0, 60)}…»)`,
    a.msgs.includes('win:state') && a.msgs.some(m => /^hello (-?[\d.]+,){7}-?[\d.]+$/.test(m)), a.msgs);
  const clk = async id => { await pg.evaluate(() => { window.__msgs.length = 0 }); await pg.click('#' + id); return pg.evaluate(() => window.__msgs.slice()) };
  const m1 = await clk('wMin'), m2 = await clk('wMax'), m3 = await clk('wCls');
  ok('💻 — ⇒ «win:min» · ☐ ⇒ «win:max» · ✕ ⇒ «win:close»', m1.join() === 'win:min' && m2.join() === 'win:max' && m3.join() === 'win:close', { m1, m2, m3 });
  const st = await pg.evaluate(() => { window.__state({ t: 'win', max: true, fs: false }); const a = document.getElementById('wMax').textContent; window.__state({ t: 'win', max: false, fs: false });
    return { a, b: document.getElementById('wMax').textContent } });
  ok(`💻 ☐ follows the window (maximized ⇒ «${st.a}» · restored ⇒ «${st.b}»)`, st.a === '❐' && st.b === '☐', st);
  // drag: press an empty part of the top bar and move ⇒ «win:drag» once · a press on a button or a profit box ⇒ nothing
  const drag = async sel => { await pg.evaluate(() => { window.__msgs.length = 0 }); const r = await pg.evaluate(s => { const e = document.querySelector(s).getBoundingClientRect(); return { x: e.left + Math.min(30, e.width / 2), y: e.top + e.height / 2 } }, sel);
    await pg.mouse.move(r.x, r.y); await pg.mouse.down(); await pg.mouse.move(r.x + 3, r.y + 1); const early = await pg.evaluate(() => window.__msgs.slice());
    await pg.mouse.move(r.x + 40, r.y + 20, { steps: 4 }); await pg.mouse.up(); return { early, all: await pg.evaluate(() => window.__msgs.slice()) } };
  const HW = await pg.evaluate(() => ['#top .hword', '#top .brand .hwd', '#top .brand'].find(q => { const e = document.querySelector(q); return e && e.getBoundingClientRect().width > 0 }));
  const d1 = await drag(HW), d2 = await drag('#totTrade'); await pg.evaluate(() => { try { hideModal() } catch (e) {} }); await pg.waitForTimeout(400);
  const d3 = await drag('#bBell'); await pg.evaluate(() => { try { if (document.querySelector('#notifPanel.on')) toggleNotif() } catch (e) {} }); await pg.waitForTimeout(400);
  ok('💻 press the top bar\'s empty part and move ⇒ «win:drag» (not before 4 px) · the profit boxes and the buttons don\'t move the window',
    !d1.early.length && d1.all.filter(m => m === 'win:drag').length === 1 && !d2.all.includes('win:drag') && !d3.all.includes('win:drag'), { d1, d2, d3 });
  await pg.evaluate(() => { window.__msgs.length = 0 }); await pg.dblclick(HW); const dbl = await pg.evaluate(() => window.__msgs.slice());
  await pg.evaluate(() => { window.__msgs.length = 0 }); await pg.dblclick('#totTrade').catch(() => {}); await pg.waitForTimeout(300); const dbl2 = await pg.evaluate(() => window.__msgs.slice()); await pg.keyboard.press('Escape'); await pg.evaluate(() => { try { hideModal() } catch (e) {} });
  ok('💻 double-click on the top bar ⇒ maximize/restore · not on a profit box', dbl.includes('win:max') && !dbl2.includes('win:max'), { dbl, dbl2 });
  // the small top bar (after scrolling): the same three · a plain click still goes to the top · press and move ⇒ drag
  await pg.waitForTimeout(900);
  const sm = await pg.evaluate(async () => { scrollTo(0, 2500); dispatchEvent(new Event('scroll')); mbarSync(); await new Promise(r => setTimeout(r, 300));
    const w = document.getElementById('mbW'), r = w.getBoundingClientRect(); return { shown: getComputedStyle(w).display !== 'none' && r.width > 0, n: w.querySelectorAll('button').length } });
  if (!sm.shown) console.log('debug small bar', JSON.stringify(await pg.evaluate(() => ({ past: document.body.classList.contains('pastTop'), y: scrollY, h: document.body.scrollHeight, mbar: getComputedStyle(document.getElementById('mbar')).display, mbw: getComputedStyle(document.getElementById('mbW')).display, top: document.getElementById('top').getBoundingClientRect().bottom }))));
  await pg.evaluate(() => { window.__msgs.length = 0 }); await pg.click('#mwMin'); const sm1 = await pg.evaluate(() => ({ m: window.__msgs.slice(), y: scrollY }));
  await pg.click('#mStat'); await pg.waitForTimeout(900); const y2 = await pg.evaluate(() => scrollY);
  ok(`💻 scrolled down: the small bar carries — ☐ ✕ too (${sm.n}) · its — doesn't scroll to the top · a plain click on the bar still does`, sm.shown && sm.n === 3 && sm1.m.join() === 'win:min' && sm1.y > 1000 && y2 < 50, { sm, sm1, y2 });
  await ctx.close();
  // ⚙️ 💻 the panel says it in MSA
  ({ ctx, pg } = await open(br, errs, { win: 1, host: 1 }));
  const pn = await pg.evaluate(async () => { openWinPanel(); await new Promise(r => setTimeout(r, 1200)); return document.getElementById('wn_body').textContent });
  ok('💻 ⚙️ «برنامج ويندوز» explains it (no title bar · — ☐ ✕ beside 🔔 · how to move the window) — in MSA', /بلا شريط عنوان/.test(pn) && /تحريك النافذة/.test(pn) && /نقرتان/.test(pn) && !/هسه|ينضغط|سكّر|ويّا|بالحاسوب بس/.test(pn), pn.slice(0, 300));
  await ctx.close();
  // the Windows program 1.2 (Edge app window) or a browser ⇒ nothing changes
  for (const [nm, o] of [['the Windows program 1.2 (Edge window)', { win: 1 }], ['a browser', {}]]) {
    ({ ctx, pg } = await open(br, errs, o));
    const n = await pg.evaluate(() => ({ winf: document.documentElement.classList.contains('winf'), b: ['wMin', 'wMax', 'wCls'].map(i => document.getElementById(i).hidden), mbw: getComputedStyle(document.getElementById('mbW')).display }));
    ok(`💻 ${nm}: no window buttons (its own title bar is there)`, !n.winf && n.b.every(Boolean) && n.mbw === 'none', n);
    await ctx.close();
  }
  ok('no page errors', !errs.length, errs);
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_win20: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('crash', e); process.exit(1) });
