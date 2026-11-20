// 📏 v3.36.63 in a real browser (run through ui_compact.py — every card kind + 🏦 + one demo bot in a closed folder): the compact cards (p107).
//   The owner (20-11): «اريدها طوليه بعرض الكروت من اضغط عليها تتمدد يعني فيها انميشن وتدفع الي تحت ، بحيث يتناسق مع كل اشكال الكروت
//   حتى لو ضفنا اشكال كروت جديدة · ربح اليوم ، الحاله ، نوع البوت ، سعر العملة» · «كذلك الديمو مختصر ، والمراكم كذلك سويه مختصر»
//   ① off by default (the cards as before) · the ⚙️ switch «📏 الكروت المختصرة» turns it on (this device)
//   ② every card (bots · 🧪 demo · 🏦 accumulator) is one row as wide as the card: the row first, everything else hidden · short
//   ③ the row says the truth: the bot's type · its state · today's profit in its own unit · the coin's live price · the demo 🧪 · the 🏦
//   ④ a tap opens the card with a height animation and pushes the cards below down · another tap brings it back to a row
//   ⑤ the same in every look (القديم · ج · ب · OKX) · a look added later (a new layer inside the card) is hidden in the row and shown open
//   ⑥ the page's refresh keeps an open card open (one row per card, still first) · ⚡ lite ⇒ no animation · off ⇒ every card full again
//   ⑦ at phone width: nothing spills out of a row · the page has no sideways scroll · no page error
//   ⑨ v3.36.64: the motion always ends — a dropped animation · the page moving the card meanwhile · no end event (found under load)
//   ⑧ v3.36.64 (the owner: «مشكلة في قفل الكرت ما يفتح اذا مقفول ، خليه يفتح الكرت بس ما يفتح القفل»): a locked card opens from its row · the lock stays
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 1200)));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function open(br, errs, o) {
  const ctx = await br.newContext(o.ctx || { viewport: { width: 1280, height: 900 } });
  await ctx.addInitScript(ls => { try { localStorage.setItem('dash_stick', 'off'); for (const k in ls) ls[k] == null ? localStorage.removeItem(k) : localStorage.setItem(k, ls[k]) } catch (e) {} }, o.ls || {});
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 10 && DATA.accum && DATA.accum.length && ACARDS.size, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await sleep(1500);
  return { ctx, pg };
}
// what every card shows now (bots · accumulator)
const NAT = async () => {                                        // each card's own height once drawn (the page skips drawing cards far from the screen)
  const out = {};
  for (const el of [...document.querySelectorAll('#grid .card[data-dir],#grid .card[data-acc]')].filter(e => e.style.display !== 'none')) {
    el.scrollIntoView({ block: 'center' }); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); out[el.dataset.dir || ('acc:' + el.dataset.acc)] = el.offsetHeight;
    out['_' + (el.dataset.dir || el.dataset.acc)] = [...el.children].filter(k => !k.classList.contains('cmini')).map(k => (k.className || k.tagName).split(' ')[0] + ':' + getComputedStyle(k).display).join(',') }
  scrollTo(0, 0); return out;
};
const STATE = () => {
  const cards = [...document.querySelectorAll('#grid .card[data-dir],#grid .card[data-acc]')].filter(e => e.style.display !== 'none');
  return cards.map(el => {
    const kids = [...el.children], row = el._cmr;
    const shown = kids.filter(k => getComputedStyle(k).display !== 'none' && k.getClientRects().length);
    return { id: el.dataset.dir || ('acc:' + el.dataset.acc), acc: !!el.dataset.acc, cmp: el.classList.contains('cmp'), o: el.classList.contains('cmpo'),
      h: el.offsetHeight, top: el.getBoundingClientRect().top + scrollY,
      rowFirst: !!row && kids[0] === row, rows: el.querySelectorAll(':scope>.cmini').length,
      rowShown: !!row && getComputedStyle(row).display !== 'none', others: shown.filter(k => k !== row).length,
      txt: row ? { sym: row.querySelector('.cm-sym').textContent, typ: row.querySelector('.cm-typ').textContent, st: row.querySelector('.cm-st').textContent,
        stc: row.querySelector('.cm-st').className, pl: row.querySelector('.cm-pf small').textContent, pf: row.querySelector('.cm-pf b').textContent,
        pfc: row.querySelector('.cm-pf').className, px: row.querySelector('.cm-px .num').textContent } : null,
      demo: el.classList.contains('isdemo'), dashed: getComputedStyle(el).borderTopStyle === 'dashed',
      spill: row ? row.scrollWidth - row.clientWidth : 0 };
  });
};
(async () => {
  const br = await chromium.launch();
  const errs = [];
  let { ctx, pg } = await open(br, errs, { ls: { dash_cmp: null, dash_skin: null } });

  // ① off by default
  const S0 = await pg.evaluate(STATE), N0 = await pg.evaluate(NAT);
  ok(`① off by default: every card as before (${S0.length} cards · none short · no row shown)`, S0.length >= 11 && S0.every(c => !c.cmp && !c.rowShown && c.others > 1), S0.filter(c => c.cmp || c.rowShown));
  await pg.evaluate(() => openSettings()); await sleep(600);
  const sw = await pg.evaluate(() => { const b = document.getElementById('bCmp'); return b ? { on: b.classList.contains('on'), aria: b.getAttribute('aria-checked'), t: b.textContent.replace(/\s+/g, ' ').trim(),
    grp: (() => { const k = document.querySelector('#modal [onclick*="setSkin"],#skinRow'); return !!k })() } : null });
  ok(`① ⚙️ has the switch «📏 الكروت المختصرة» — off («${sw && sw.t}»)`, sw && !sw.on && sw.aria === 'false' && sw.t.includes('الكروت المختصرة') && sw.t.includes('كاملة'), sw);
  await pg.evaluate(() => document.getElementById('bCmp').click()); await sleep(700);
  const sw2 = await pg.evaluate(() => { const b = document.getElementById('bCmp'); return { on: b.classList.contains('on'), aria: b.getAttribute('aria-checked'), t: b.textContent.replace(/\s+/g, ' ').trim(), ls: localStorage.getItem('dash_cmp') } });
  ok(`① a tap turns it on for this device (dash_cmp=${sw2.ls}) · its line says what a row holds («${sw2.t.slice(0, 90)}»)`, sw2.on && sw2.aria === 'true' && sw2.ls === 'on'
     && sw2.t.includes('نوعه') && sw2.t.includes('حالته') && sw2.t.includes('السعر') && sw2.t.includes('ربح اليوم'), sw2);
  await pg.evaluate(() => hideModal()); await sleep(500);

  // ② every card is one row
  const S1 = await pg.evaluate(STATE);
  const nb = S1.filter(c => !c.acc).length, na = S1.filter(c => c.acc).length, nd = S1.filter(c => c.demo).length;
  ok(`② every card is one row (${nb} bots · ${nd} 🧪 demo · ${na} 🏦): the row first and shown · nothing else of the card shown`,
     nb >= 10 && na >= 1 && nd === 1 && S1.every(c => c.cmp && !c.o && c.rowFirst && c.rows === 1 && c.rowShown && c.others === 0), S1.filter(c => !(c.cmp && c.rowFirst && c.rowShown && c.others === 0)));
  const hs = S1.map(c => Math.round(c.h)), full = N0;
  ok(`② … short, even the cards far below the screen: every row ${Math.min(...hs)}–${Math.max(...hs)} px (the full cards were ${Math.min(...Object.keys(N0).filter(k => k[0] !== '_').map(k => N0[k]))}–${Math.max(...Object.keys(N0).filter(k => k[0] !== '_').map(k => N0[k]))} px) · the page got shorter`,
     Math.max(...hs) < 130 && S1.every(c => c.h < full[c.id] * 0.5), hs);
  const wid = await pg.evaluate(() => { const r = [...document.querySelectorAll('#grid .card[data-dir]')].map(e => [e.getBoundingClientRect().width, e._cmr.getBoundingClientRect().width]); return r });
  ok('② … the row fills the card\'s width', wid.every(([cw, rw]) => rw > cw * 0.85), wid);

  // ③ the row says the truth
  const T = await pg.evaluate(() => {
    const f = x => f4(+x);
    const want = DATA.bots.map(b => {
      const t = b.bot_type || 'grid', v = +b.today || 0, a = Math.abs(v);
      const coin = t === 'dca' ? ((b.dca || {}).base_coin || b.symbol.split('-')[0]) : t === 'rec_sell' ? ((b.rec || {}).base || b.symbol.split('-')[0]) : '';
      const typ = (b.dca && b.dca.plus) ? (t === 'dca_buy' ? 'DCA+ شرائي' : 'DCA+ بيعي') : ({ grid: 'شبكة', grid_range: 'مدى', grid_plus: 'بلس', grid_step: 'متدرج', dca: 'DCA بيعي', dca_buy: 'DCA شرائي',
        rec_buy: 'دوري شرائي', rec_sell: 'دوري بيعي', rec_va: 'مسار القيمة' })[t];
      const cp = (window.JPX && JPX[b.symbol]) || b.cp || (b.rec || {}).cp || (b.dca || {}).cp;
      const el = CARDS.get(b.dir), r = el._cmr;
      return { s: b.symbol, t, demo: !!b.demo, alive: !!b.alive, v, coin, typ, px: cp ? f(cp) : '—',
        got: { sym: r.querySelector('.cm-sym').textContent, typ: r.querySelector('.cm-typ').textContent, st: r.querySelector('.cm-st').textContent, stc: r.querySelector('.cm-st').className,
          pl: r.querySelector('.cm-pf small').textContent, pf: r.querySelector('.cm-pf b').textContent, pfc: r.querySelector('.cm-pf').className, px: r.querySelector('.cm-px .num').textContent,
          img: !!r.querySelector('.cm-ic img,.cm-ic b'), rgb: el.style.getPropertyValue('--cm-rgb') } };
    });
    return want;
  });
  const bad3 = T.filter(x => !(x.got.sym.startsWith(x.s) && x.got.typ.includes(x.typ) && x.got.px === x.px && x.got.pl === 'اليوم' && x.got.img && x.got.rgb));
  ok(`③ every bot's row: its pair · its type (${[...new Set(T.map(x => x.got.typ))].join(' · ')}) · the live price · «اليوم» · its coin · a colour by its kind`, !bad3.length && T.length >= 10, bad3);
  const badU = T.filter(x => x.coin ? !x.got.pf.endsWith(' ' + x.coin) : !x.got.pf.endsWith('$'));
  const badV = T.filter(x => { const n = parseFloat(x.got.pf.replace('−', '-').replace(/[^0-9.+-]/g, '')); return Math.abs(n - x.v) > Math.max(0.006, Math.abs(x.v) * 0.002) });
  ok(`③ today's profit in its own unit — $ for the grids/🪜/buy DCA/periodic buy/value path · the coin for the sell DCA and the periodic sell (${T.map(x => x.got.pf).join(' | ')})`,
     !badU.length && !badV.length, { badU, badV });
  ok('③ … its colour: green when it made money today · grey at zero', T.every(x => x.v > 1e-12 ? x.got.pfc.includes('up') : x.v < -1e-12 ? x.got.pfc.includes('dn') : x.got.pfc.includes('z')), T.map(x => [x.v, x.got.pfc]));
  ok('③ the state: «نشط» (green) for a running bot · «متوقف» for a stopped one', T.every(x => x.alive ? (x.got.stc.includes('on') || x.got.stc.includes('tp') || x.got.stc.includes('bad')) : (x.got.st === 'متوقف' && x.got.stc.includes('off'))), T.map(x => [x.s, x.alive, x.got.st]));
  const D = S1.find(c => c.demo);
  ok(`③ the 🧪 demo is short too: «${D && D.txt.sym}» · its dashed border stays · still under the demo line`, D && D.txt.sym.includes('🧪') && D.dashed
     && await pg.evaluate(id => { const k = [...document.querySelectorAll('#grid > *')]; return k.indexOf(CARDS.get(id)) > k.indexOf(document.getElementById('demoSep')) }, D.id), D);
  const A = await pg.evaluate(() => { const a = DATA.accum[0], el = ACARDS.get(a.id), r = el._cmr;
    return { a: { name: a.name, en: a.enabled, pl: a.pl, coin: a.coin, cp: a.cp, base: a.base }, sym: r.querySelector('.cm-sym').textContent, typ: r.querySelector('.cm-typ').textContent,
      st: r.querySelector('.cm-st').textContent, pl: r.querySelector('.cm-pf small').textContent, pf: r.querySelector('.cm-pf b').textContent, px: r.querySelector('.cm-px .num').textContent, f: a.cp ? f4(+a.cp) : '—' } });
  ok(`③ the 🏦 accumulator is short too: «${A.sym} · ${A.typ} · ${A.st} · ${A.pl} ${A.pf} · ${A.px}» (its state · its profit now, or its coins before any)`,
     A.typ.includes('مُراكِم') && A.st === (A.a.en ? 'يجمع' : 'موقوف') && A.px === A.f && (A.a.pl != null ? A.pl === 'الربح' : (A.pl === 'المخزون' && A.pf.endsWith(' ' + A.a.base))), A);

  // ④ a tap opens it with motion and pushes the cards below
  const op = await pg.evaluate(async () => {
    const els = [...document.querySelectorAll('#grid .card[data-dir]')].filter(e => e.style.display !== 'none');
    const el = els[1], L0 = el.getBoundingClientRect().left, T0 = el.getBoundingClientRect().top;
    const below = els.find(e => Math.abs(e.getBoundingClientRect().left - L0) < 2 && e.getBoundingClientRect().top > T0 + 5);
    const side = els.filter(e => e !== el && Math.abs(e.getBoundingClientRect().top - T0) < 2);
    const b0 = below.getBoundingClientRect().top, h0 = el.getBoundingClientRect().height;
    el._cmr.click();
    const an = el.getAnimations().filter(a => a.effect && a.effect.getKeyframes().some(k => k.height));
    const fr = [];await new Promise(r => { const t0 = performance.now(); const f = () => { fr.push([el.getBoundingClientRect().height, below.getBoundingClientRect().top]);
      performance.now() - t0 < 600 ? requestAnimationFrame(f) : r() }; requestAnimationFrame(f) });
    const mids = fr.filter(x => x[0] > h0 + 5 && x[0] < fr[fr.length - 1][0] - 5), mid = mids.length ? mids[Math.floor(mids.length / 2)][0] : h0, bMid = mids.length ? mids[Math.floor(mids.length / 2)][1] : b0;
    const h1 = el.getBoundingClientRect().height, b1 = below.getBoundingClientRect().top;
    const shown = [...el.children].filter(k => getComputedStyle(k).display !== 'none' && k.getClientRects().length).length;
    const sideH = side.map(e => Math.round(e.getBoundingClientRect().height));
    return { n: an.length, h0, mid, frames: mids.length, h1, b0, bMid, b1, sideH, below: below.dataset.dir, o: el.classList.contains('cmpo'), aria: el._cmr.getAttribute('aria-expanded'), shown, left: el.getAnimations().length, dir: el.dataset.dir };
  });
  ok(`④ a tap opens the card with an animation (${op.n} height animation · ${Math.round(op.h0)} → ${Math.round(op.mid)} → ${Math.round(op.h1)} px · ${op.frames} frames in between) · the full card shows (${op.shown} parts)`,
     op.n === 1 && op.frames >= 3 && op.mid > op.h0 + 5 && op.mid < op.h1 - 5 && op.h1 > op.h0 * 3 && op.o && op.aria === 'true' && op.shown > 2 && op.left === 0, op);
  ok(`④ … and pushes the card below down (${Math.round(op.b0)} → ${Math.round(op.bMid)} → ${Math.round(op.b1)} px: by the card's growth) · the cards beside it (several columns on a computer) stay rows (${op.sideH.join(' · ')} px)`,
     op.bMid > op.b0 + 3 && Math.abs((op.b1 - op.b0) - (op.h1 - op.h0)) < 2 && op.sideH.length >= 1 && op.sideH.every(h => Math.abs(h - op.h0) < 1.5), op);
  const cl = await pg.evaluate(async dd => { const [d, bd] = dd.split('|');
    const el = CARDS.get(d), below = CARDS.get(bd), b0 = below.getBoundingClientRect().top, h0 = el.getBoundingClientRect().height;
    el._cmr.click();
    const n = el.getAnimations().filter(a => a.effect && a.effect.getKeyframes().some(k => k.height)).length;
    const fr = [];await new Promise(r => { const t0 = performance.now(); const f = () => { fr.push([el.getBoundingClientRect().height, [...el.children].filter(k => getComputedStyle(k).display !== 'none').length]);
      performance.now() - t0 < 600 ? requestAnimationFrame(f) : r() }; requestAnimationFrame(f) });
    const mids = fr.filter(x => x[0] < h0 - 5 && x[0] > fr[fr.length - 1][0] + 5), mid = mids.length ? mids[Math.floor(mids.length / 2)][0] : h0, shownMid = mids.length ? Math.min(...mids.map(x => x[1])) : 0;
    return { n, h0, mid, frames: mids.length, h1: el.getBoundingClientRect().height, b0, b1: below.getBoundingClientRect().top, o: el.classList.contains('cmpo'), aria: el._cmr.getAttribute('aria-expanded'),
      shownMid, others: [...el.children].filter(k => k !== el._cmr && getComputedStyle(k).display !== 'none').length };
  }, [op.dir, op.below].join('|'));
  ok(`④ another tap closes it with an animation (${Math.round(cl.h0)} → ${Math.round(cl.mid)} → ${Math.round(cl.h1)} px · the card stays whole while it shrinks) · back to the row's height · the card below comes back up`,
     cl.n === 1 && cl.frames >= 3 && cl.mid < cl.h0 - 5 && cl.mid > cl.h1 + 5 && cl.shownMid > 2 && !cl.o && cl.aria === 'false' && cl.others === 0 && Math.abs(cl.h1 - op.h0) < 1.5 && Math.abs(cl.b1 - op.b0) < 1.5, cl);
  const qk = await pg.evaluate(async d => { const el = CARDS.get(d), tap = async ms => { el._cmr.click(); await new Promise(r => setTimeout(r, ms)) };
    await tap(60); await tap(60); await tap(150);
    const midOpen = el.classList.contains('cmpa') && el.getBoundingClientRect().height > 100;
    await new Promise(r => setTimeout(r, 650)); const a = { o: el.classList.contains('cmpo'), anim: el.getAnimations().length, cmpa: el.classList.contains('cmpa'), h: el.getBoundingClientRect().height };
    await tap(60); await tap(700); const b = { o: el.classList.contains('cmpo'), anim: el.getAnimations().length, h: el.getBoundingClientRect().height };
    return { midOpen, a, b } }, op.dir);
  ok(`④ fast taps: open·close·open ⇒ ends open and still (${Math.round(qk.a.h)} px · no animation left · clipped while moving) · close·open·… ⇒ each tap turns it the other way (${Math.round(qk.b.h)} px)`,
     qk.midOpen && qk.a.o && !qk.a.anim && !qk.a.cmpa && Math.abs(qk.a.h - op.h1) < 2 && qk.b.o && !qk.b.anim && Math.abs(qk.b.h - op.h1) < 2, qk);
  await pg.evaluate(async d => { const el = CARDS.get(d); el._cmr.click(); await new Promise(r => setTimeout(r, 600)) }, op.dir);
  const ac = await pg.evaluate(async () => { const el = [...ACARDS.values()][0], h0 = el.getBoundingClientRect().height; el._cmr.click(); await new Promise(r => setTimeout(r, 600));
    const h1 = el.getBoundingClientRect().height, btn = [...el.querySelectorAll('button[data-k]')].filter(b => getComputedStyle(b).display !== 'none' && b.getClientRects().length).length;
    el._cmr.click(); await new Promise(r => setTimeout(r, 600)); return { h0, h1, h2: el.getBoundingClientRect().height, btn } });
  ok(`④ the 🏦 card opens the same way (${Math.round(ac.h0)} → ${Math.round(ac.h1)} px · its buttons back: ${ac.btn}) and closes`, ac.h1 > ac.h0 * 3 && ac.btn >= 3 && Math.abs(ac.h2 - ac.h0) < 1.5, ac);

  // ⑥ the refresh keeps an open card · lite ⇒ no animation · off ⇒ full again
  const kp = await pg.evaluate(async () => {
    const el = [...document.querySelectorAll('#grid .card[data-dir]')][3]; el._cmr.click(); await new Promise(r => setTimeout(r, 500));
    await tick(); await new Promise(r => setTimeout(r, 400)); await tick(); await new Promise(r => setTimeout(r, 400));
    const ok1 = el.classList.contains('cmpo') && el.firstElementChild === el._cmr && el.querySelectorAll(':scope>.cmini').length === 1;
    const all1 = [...document.querySelectorAll('#grid .card')].every(e => e.querySelectorAll(':scope>.cmini').length <= 1);
    el._cmr.click(); await new Promise(r => setTimeout(r, 500));
    return { ok1, all1, closed: !el.classList.contains('cmpo'), cmO: el._cmO, cmC: el._cmC, an: el.getAnimations().length, cls: el.className };
  });
  ok('⑥ the page\'s refresh (twice) keeps an open card open · one row per card, still first', kp.ok1 && kp.all1 && kp.closed, kp);
  const li = await pg.evaluate(async () => { document.documentElement.classList.add('lite');
    const el = [...document.querySelectorAll('#grid .card[data-dir]')][2], h0 = el.getBoundingClientRect().height; el._cmr.click();
    const n = el.getAnimations().length, h1 = el.getBoundingClientRect().height; el._cmr.click(); const h2 = el.getBoundingClientRect().height;
    document.documentElement.classList.remove('lite'); return { n, h0, h1, h2 } });
  ok(`⑥ «⚡ الوضع الخفيف»: it opens and closes at once, no animation (${Math.round(li.h0)} → ${Math.round(li.h1)} → ${Math.round(li.h2)} px)`, li.n === 0 && li.h1 > li.h0 * 3 && Math.abs(li.h2 - li.h0) < 1.5, li);
  const wa = await pg.evaluate(async () => { localStorage.setItem('dash_anim', 'none');
    const el = [...document.querySelectorAll('#grid .card[data-dir]')][2]; el._cmr.click(); const n = el.getAnimations().length; await new Promise(r => setTimeout(r, 600)); el._cmr.click();
    await new Promise(r => setTimeout(r, 600)); localStorage.removeItem('dash_anim'); return n });
  ok('⑥ … the windows\' «بلا حركة» does not stop it (only ⚡ lite or the device\'s «reduce motion»)', wa === 1, wa);
  await pg.evaluate(() => { openSettings() }); await sleep(500);
  await pg.evaluate(() => document.getElementById('bCmp').click()); await sleep(700);
  await pg.evaluate(() => hideModal()); await sleep(400);
  const S2 = await pg.evaluate(STATE), N2 = await pg.evaluate(NAT);
  const left = await pg.evaluate(() => [...document.querySelectorAll('#grid .card')].filter(e => e.style.height || e.getAnimations().length || /\bcmp/.test(e.className)).length);
  // (the heights follow the data — a longer value takes a wider box — so the check is: the same parts shown as at first · nothing left from the row)
  ok(`⑥ turned off ⇒ every card full again, as at first (${S2.length}: ${Object.keys(N2).filter(k => k[0] !== '_').map(k => N2[k]).join(' · ')} px) · the same parts of each card shown as at first · nothing left on the cards`,
     S2.every(c => !c.cmp && !c.rowShown && c.others > 1) && !left && Object.keys(N0).every(k => k[0] !== '_' || N2[k] === N0[k]) && Object.keys(N0).every(k => k[0] === '_' || N2[k] > 300)
     && await pg.evaluate(() => localStorage.getItem('dash_cmp')) === null, { left, diff: Object.keys(N0).filter(k => k[0] === '_' && N2[k] !== N0[k]).map(k => [k, N0[k], N2[k]]) });
  await pg.evaluate(() => { openSettings() }); await sleep(500);
  await pg.evaluate(() => document.getElementById('bCmp').click()); await sleep(700);
  await pg.evaluate(() => hideModal()); await sleep(400);

  // ⑤ every look
  for (const [sk, nm] of [['old', 'القديم'], ['c', 'ج'], ['b', 'ب'], ['o', 'OKX']]) {
    const r = await pg.evaluate(async sk => {
      setSkin(sk); await new Promise(r => setTimeout(r, 900));
      const els = [...document.querySelectorAll('#grid .card[data-dir],#grid .card[data-acc]')].filter(e => e.style.display !== 'none');
      const short = els.every(el => el.classList.contains('cmp') && el.firstElementChild === el._cmr && [...el.children].every(k => k === el._cmr || getComputedStyle(k).display === 'none'));
      const el = els[0]; el._cmr.click(); await new Promise(r => setTimeout(r, 600));
      const sl = el.querySelector(':scope>.skin');
      const vis = sl ? getComputedStyle(sl).display !== 'none' && sl.getBoundingClientRect().height > 100 : null;
      const full = [...el.children].filter(k => getComputedStyle(k).display !== 'none' && k.getClientRects().length).length, h = el.getBoundingClientRect().height;
      el._cmr.click(); await new Promise(r => setTimeout(r, 600));
      return { short, n: els.length, vis, full, h, back: el.getBoundingClientRect().height, sk: uiSkin(), first: el.firstElementChild === el._cmr };
    }, sk);
    ok(`⑤ look «${nm}»: every card stays one row (${r.n}) · opened, the look draws the whole card (${sk === 'old' ? r.full + ' parts' : 'its layer shown'} · ${Math.round(r.h)} px) · closed again (${Math.round(r.back)} px)`,
       r.short && r.sk === sk && r.first && r.h > 300 && r.back < 130 && (sk === 'old' ? r.full > 3 : r.vis === true), r);
  }
  await pg.evaluate(() => setSkin('old')); await sleep(600);
  const fut = await pg.evaluate(async () => {
    const el = [...document.querySelectorAll('#grid .card[data-dir]')][0], n = document.createElement('div');
    n.className = 'skin-future'; n.style.cssText = 'height:200px;background:red'; n.textContent = 'شكل جديد'; el.appendChild(n);
    const hid = getComputedStyle(n).display === 'none';
    el._cmr.click(); await new Promise(r => setTimeout(r, 600));
    const shown = getComputedStyle(n).display !== 'none' && n.getBoundingClientRect().height === 200;
    el._cmr.click(); await new Promise(r => setTimeout(r, 600));
    const hid2 = getComputedStyle(n).display === 'none'; n.remove();
    return { hid, shown, hid2 };
  });
  ok('⑤ a look added later (a new layer inside the card, not known to the compact code) is hidden in the row and shown when the card opens', fut.hid && fut.shown && fut.hid2, fut);

  // ⑧ v3.36.64 — the card lock: «خليه يفتح الكرت بس ما يفتح القفل»
  const lk = await pg.evaluate(async () => {
    const W = ms => new Promise(r => setTimeout(r, ms));
    localStorage.setItem('dash_clock', 'on'); CLK.open.clear(); cardLockAll(); await W(300);
    const el = [...document.querySelectorAll('#grid .card[data-dir]')][4], k = cardKey(el), row = el._cmr;
    const r0 = { locked: cardLocked(el), cls: el.classList.contains('lk'), op: getComputedStyle(row).opacity, mark: getComputedStyle(row.querySelector('.cm-sym'), '::after').content };
    row.click(); await W(600);
    const r1 = { o: el.classList.contains('cmpo'), locked: cardLocked(el), timer: CLK.open.has(k), btn: el._lk ? el._lk.textContent : '' };
    let hit = 0; const t = document.createElement('button'); t.type = 'button'; t.textContent = 'x'; t.onclick = () => { hit++ }; el.appendChild(t);
    t.click(); t.remove();
    const r2 = { hit, locked: cardLocked(el), timer: CLK.open.has(k) };
    row.click(); await W(600);
    const r3 = { o: el.classList.contains('cmpo'), locked: cardLocked(el), timer: CLK.open.has(k) };
    cardLockFlip(el); const until = CLK.open.get(k); await W(50); row.click(); await W(600);
    const r4 = { o: el.classList.contains('cmpo'), open: !cardLocked(el), same: CLK.open.get(k) === until }; row.click(); await W(600);
    const acc = [...ACARDS.values()][0]; acc._cmr.click(); await W(600); const r5 = { o: acc.classList.contains('cmpo'), locked: cardLocked(acc) }; acc._cmr.click(); await W(600);
    localStorage.removeItem('dash_clock'); CLK.open.clear(); cardLockAll();
    return { r0, r1, r2, r3, r4, r5 };
  });
  ok(`⑧ 🔒 a locked card: its row is not dimmed (opacity ${lk.r0.op}) and shows the lock («${lk.r0.mark}»)`, lk.r0.locked && lk.r0.cls && lk.r0.op === '1' && lk.r0.mark.includes('🔒'), lk.r0);
  ok('⑧ … a tap on the row opens the locked card · the lock stays (still 🔒 · no open minute started)', lk.r1.o && lk.r1.locked && !lk.r1.timer && lk.r1.btn === '🔒', lk.r1);
  ok('⑧ … a button inside the opened locked card still does nothing until 🔒 is pressed (as before)', lk.r2.hit === 0 && lk.r2.locked && !lk.r2.timer, lk.r2);
  ok('⑧ … another tap closes it · still locked', !lk.r3.o && lk.r3.locked && !lk.r3.timer, lk.r3);
  ok('⑧ … an unlocked card (🔓 its minute) opens from the row too · the row does not stretch its minute · a locked 🏦 opens too', lk.r4.o && lk.r4.open && lk.r4.same && lk.r5.o && lk.r5.locked, lk);

  // ⑨ v3.36.64 — the motion always ends (found under load: the page re-sorted the cards while one shrank ⇒ it stayed open, clipped)
  const en = await pg.evaluate(async () => {
    const W = ms => new Promise(r => setTimeout(r, ms));
    const el = [...document.querySelectorAll('#grid .card[data-dir]')][5], st = () => ({ o: el.classList.contains('cmpo'), a: el.classList.contains('cmpa'), c: el._cmC || 0, n: el.getAnimations().length });
    const open = async () => { if (!el.classList.contains('cmpo')) { el._cmr.click(); await W(700) } };
    await open(); el._cmr.click(); await W(60); el.getAnimations().forEach(x => x.cancel()); await W(150); const cancel = st();
    await open(); el._cmr.click(); await W(60); { const p = el.parentNode, nx = el.nextSibling; p.appendChild(el); p.insertBefore(el, nx) } await W(900); const moved = st();
    await open(); el._cmr.click(); el._cmA.onfinish = null; el._cmA.oncancel = null; await W(900); const silent = st();
    el._cmr.click(); await W(60); el.getAnimations().forEach(x => x.cancel()); await W(150); const openCancel = st();
    el._cmr.click(); await W(700);
    return { cancel, moved, silent, openCancel, end: st() };
  });
  const shut = x => !x.o && !x.a && !x.c && !x.n;
  ok(`⑨ closing, the animation dropped from outside ⇒ the card still ends as a row (${JSON.stringify(en.cancel)})`, shut(en.cancel), en);
  ok(`⑨ closing, the page moves the card meanwhile (a re-sort) ⇒ it ends as a row (${JSON.stringify(en.moved)})`, shut(en.moved), en);
  ok(`⑨ closing, no end event at all ⇒ it ends as a row after the animation's time (${JSON.stringify(en.silent)})`, shut(en.silent), en);
  ok(`⑨ opening, the animation dropped ⇒ it stays open, not clipped (${JSON.stringify(en.openCancel)}) · and closes again`, en.openCancel.o && !en.openCancel.a && !en.openCancel.c && shut(en.end), en);

  await ctx.close();

  // ⑦ phone width · kept after a reload
  ({ ctx, pg } = await open(br, errs, { ls: { dash_cmp: 'on', dash_skin: 'c' }, ctx: { viewport: { width: 360, height: 780 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 } }));
  const ph = await pg.evaluate(STATE);
  const sx = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  ok(`⑦ the choice stays after a reload (this device) · at phone width (360 px): every card one row (${Math.round(Math.min(...ph.map(c => c.h)))}–${Math.round(Math.max(...ph.map(c => c.h)))} px) · nothing spills out of a row · no sideways scroll (${sx})`,
     ph.every(c => c.cmp && c.rowShown && c.others === 0 && c.spill <= 1 && c.h < 140) && sx <= 0, { sx, bad: ph.filter(c => !(c.cmp && c.rowShown && c.others === 0 && c.spill <= 1 && c.h < 140)) });
  const tp = await pg.evaluate(async () => { const el = [...document.querySelectorAll('#grid .card[data-dir]')][1]; const r = el._cmr.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2, el.dataset.dir] });
  await pg.touchscreen.tap(tp[0], tp[1]); await sleep(700);
  const tp2 = await pg.evaluate(d => ({ o: CARDS.get(d).classList.contains('cmpo'), modal: !!document.querySelector('#modal.show,#modal[open]') }), tp[2]);
  ok('⑦ a finger tap on the row opens the card (no window opens)', tp2.o && !tp2.modal, tp2);
  await ctx.close();
  ok(`no page error (${errs.length})`, !errs.length, errs.slice(0, 3));
  await br.close();
  const n = res.filter(Boolean).length;
  console.log(n === res.length ? `✅ ui_compact: ${n}/${res.length}` : `❌ ui_compact: ${n}/${res.length}`);
  process.exit(n === res.length ? 0 : 1);
})().catch(e => { console.log('❌ crash ' + e); process.exit(1) });
