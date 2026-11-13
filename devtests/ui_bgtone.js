// 🌌🎶 v3.36.37 in a real browser (run through ui_bgtone.py — every card kind in a closed folder): the moving backgrounds and the tone —
//   the owner (13-11): «خلي الخلفيات والنغمات كلهن · الالوان على حدى والخلفيات على حدى حتى الخلفيات متحركه تتلون وخلي اختيار الاصلي مافيه
//   انميشن يعني الوضع الاعتيادي , وبالمستقبل انضيف بعد»
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
async function open(br, errs, init) {
  const ctx = await br.newContext({ viewport: { width: 412, height: 900 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(i => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none'); for (const k in i) localStorage.setItem(k, i[k]) } catch (e) {} }, init || {});
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9 && typeof HB !== 'undefined', null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(1200);
  return { ctx, pg };
}
// a small fingerprint of what the background shows now (and its mean colour)
const SNAP = `(() => { const c = document.getElementById('hbg'); if (!c || !c.width) return null; const x = c.getContext('2d'), d = x.getImageData(0, 0, c.width, c.height).data;
  let h = 0, r = 0, g = 0, b = 0, n = 0; for (let i = 0; i < d.length; i += 4 * 97) { h = (h * 31 + d[i] * 3 + d[i + 1] * 5 + d[i + 2] * 7) >>> 0; r += d[i]; g += d[i + 1]; b += d[i + 2]; n++ }
  return { h, r: Math.round(r / n), g: Math.round(g / n), b: Math.round(b / n) } })()`;
(async () => {
  const br = await chromium.launch();
  const errs = [];
  let { ctx, pg } = await open(br, errs);
  // ── the original: as it was
  const o = await pg.evaluate(() => ({ k: uiBg(), abg: document.documentElement.classList.contains('abg'), cv: getComputedStyle(document.getElementById('hbg')).display, orb: getComputedStyle(document.querySelector('.orb')).display, raf: HB.raf }));
  ok('🌌 «الأصلية» by default: the background as it was (its orbs) · nothing drawn, nothing running', o.k === 'orig' && !o.abg && o.cv === 'none' && o.orb !== 'none' && !o.raf, o);
  // ── ⚙️: the colours and the backgrounds apart · a live little preview on each
  await pg.evaluate(() => { openSettings(); stTog('bg') }); await pg.waitForTimeout(400);
  const st = await pg.evaluate(() => { const rows = [...document.querySelectorAll('#modal .sgrp')][0].querySelectorAll('.sgl>.sitem .stt b');
    const bs = [...document.querySelectorAll('#bgRow .bgb')].map(b => { const c = b.querySelector('canvas'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let mn = 255, mx = 0;
      for (let i = 0; i < d.length; i += 4 * 13) { const v = d[i] + d[i + 1] + d[i + 2]; mn = Math.min(mn, v); mx = Math.max(mx, v) } return { k: b.dataset.bg, t: b.textContent.trim(), on: b.classList.contains('on'), drawn: mx - mn > 12 } });
    return { rows: [...rows].map(b => b.textContent), bs } });
  ok(`🎨🌌 ⚙️: «الألوان» and «الخلفية» are two rows · ${st.bs.length} backgrounds (${st.bs.map(b => b.t).join(' · ')}) each with its live preview`,
    st.rows[0] === 'الألوان' && st.rows[1] === 'الخلفية' && st.bs.map(b => b.k).join() === 'orig,waves,dust,aurora,beams,stars,silk' && st.bs.every(b => b.drawn) && st.bs[0].on, st);
  // ── each moving background draws, moves, and the original returns
  const mv = [];
  for (const k of ['waves', 'dust', 'aurora', 'beams', 'stars', 'silk']) {
    await pg.evaluate(k => { setBg(k); hideModal() }, k); await pg.waitForTimeout(500);
    const a = await pg.evaluate(SNAP); await pg.waitForTimeout(700); const b = await pg.evaluate(SNAP);
    const s = await pg.evaluate(() => ({ abg: document.documentElement.classList.contains('abg'), cv: getComputedStyle(document.getElementById('hbg')).display, orb: getComputedStyle(document.querySelector('.orb')).display, w: document.getElementById('hbg').width }));
    mv.push({ k, moves: !!(a && b && a.h !== b.h), ...s });
  }
  ok(`🌌 each of the 6 moving backgrounds draws and moves (${mv.filter(m => m.moves).length}/6) · the orbs rest · a surface the size of the screen`,
    mv.every(m => m.moves && m.abg && m.cv === 'block' && m.orb === 'none' && m.w >= 400), mv);
  // ── its colours follow «🎨 الألوان»
  await pg.evaluate(() => setBg('aurora')); await pg.evaluate(() => hideModal()); await pg.waitForTimeout(300);
  const c1 = await pg.evaluate(SNAP);
  await pg.evaluate(() => { setTheme('emerald'); hideModal() }); await pg.waitForTimeout(400);
  const c2 = await pg.evaluate(SNAP);
  await pg.evaluate(() => { setTheme('holy'); hideModal() }); await pg.waitForTimeout(300);
  ok(`🎨 the moving background takes the chosen colours (بنفسجي rgb ${c1.r},${c1.g},${c1.b} ⇒ زمردي rgb ${c2.r},${c2.g},${c2.b})`, c1 && c2 && c2.g - c2.r > c1.g - c1.r + 8, { c1, c2 });
  // ── it stops behind a window and comes back
  await pg.waitForTimeout(300);
  const w0 = await pg.evaluate(async snap => { openSettings(); await new Promise(r => setTimeout(r, 200)); const a = eval(snap); await new Promise(r => setTimeout(r, 600)); const b = eval(snap);
    hideModal(); await new Promise(r => setTimeout(r, 300)); const c = eval(snap); await new Promise(r => setTimeout(r, 600)); const d = eval(snap);
    return { still: a.h === b.h, back: c.h !== d.h, cov: document.documentElement.classList.contains('covered') } }, SNAP);
  ok('⏸️ it stops behind a window (nothing to redraw) and moves again after', w0.still && w0.back && !w0.cov, w0);
  // ── the light mode ⇒ one still frame
  const lt = await pg.evaluate(async snap => { uiLiteToggle(); hideModal(); await new Promise(r => setTimeout(r, 300)); const a = eval(snap); await new Promise(r => setTimeout(r, 700)); const b = eval(snap);
    const raf = HB.raf; uiLiteToggle(); hideModal(); await new Promise(r => setTimeout(r, 400)); const c = eval(snap); await new Promise(r => setTimeout(r, 600)); const d = eval(snap);
    return { still: a && b && a.h === b.h, raf, again: c.h !== d.h } }, SNAP);
  ok('⚡ «الوضع الخفيف» ⇒ the background stands still (one frame, no loop) · off again ⇒ it moves', lt.still && !lt.raf && lt.again, lt);
  // ── back to the original
  const og = await pg.evaluate(async () => { setBg('orig'); hideModal(); await new Promise(r => setTimeout(r, 200));
    return { k: uiBg(), ls: localStorage.getItem('dash_bg'), abg: document.documentElement.classList.contains('abg'), raf: HB.raf, orb: getComputedStyle(document.querySelector('.orb')).display } });
  ok('🌌 back to «الأصلية»: the orbs again · nothing running · nothing kept', og.k === 'orig' && og.ls === null && !og.abg && !og.raf && og.orb !== 'none', og);
  // ── 🎶 the tone
  await pg.evaluate(() => { openSettings(); stTog('tone') }); await pg.waitForTimeout(300);
  const tr = await pg.evaluate(() => ({ b: [...document.querySelectorAll('#toneRow button')].map(b => b.textContent), on: (document.querySelector('#toneRow button.on') || {}).textContent, vol: (document.getElementById('toneVol') || {}).value,
    grp: [...[...document.querySelectorAll('#modal .sgrp')].find(g => /الأصوات/.test(g.textContent)).querySelectorAll('.sgl>.sitem .stt b')].map(b => b.textContent) }));
  ok(`🎶 ⚙️ 🔊 «النغمة المستمرة»: ${tr.b.join(' · ')} · «بلا» at first · its own volume`, tr.b.join() === 'بلا,سكون,فضاء,قطرات,بحر' && tr.on === 'بلا' && tr.vol === '40' && tr.grp.join('|') === 'صوت الربح|صوت فتح القفل|النغمة المستمرة', tr);
  const t0 = await pg.evaluate(() => ({ ac: !!HT.ac, k: HT.k }));
  await pg.click('#toneRow button[data-tone="calm"]'); await pg.waitForTimeout(1500);
  const t1 = await pg.evaluate(() => ({ ac: !!HT.ac, st: HT.ac && HT.ac.state, k: HT.k, ls: localStorage.getItem('dash_tone'), g: HT.m && +HT.m.gain.value.toFixed(3) }));
  ok(`🎶 choosing «سكون» plays it (sound ${t1.st}) and keeps it on this device`, !t0.ac && t1.ac && t1.st === 'running' && t1.k === 'calm' && t1.ls === 'calm' && t1.g > 0, { t0, t1 });
  const t2 = await pg.evaluate(async () => { chime(); await new Promise(r => setTimeout(r, 250)); const low = +HT.m.gain.value.toFixed(3); await new Promise(r => setTimeout(r, 2600)); return { low, back: +HT.m.gain.value.toFixed(3), full: +htVol().toFixed(3) } });
  ok(`🎶 the profit sound: the tone steps aside for a moment (${t2.low}) and comes back (${t2.back})`, t2.low < t2.full * .5 && t2.back > t2.full * .8, t2);
  const t3 = await pg.evaluate(async () => { setToneVol(90); await new Promise(r => setTimeout(r, 400)); const g = +HT.m.gain.value.toFixed(3); setToneVol(40); return { g, ls: localStorage.getItem('dash_tone_vol') } });
  ok('🎶 its volume follows the slider and is kept', t3.g > .5 && t3.ls === '40', t3);
  for (const k of ['space', 'drops', 'sea']) await pg.evaluate(k => { setTone(k) }, k), await pg.waitForTimeout(700);
  const t4 = await pg.evaluate(() => ({ k: HT.k, st: HT.ac.state }));
  await pg.evaluate(() => setTone('off')); await pg.waitForTimeout(300);
  const t5 = await pg.evaluate(() => ({ k: HT.k, stop: !!HT.stop, ls: localStorage.getItem('dash_tone') }));
  ok('🎶 فضاء · قطرات · بحر play one after the other · «بلا» stops it and forgets it', t4.k === 'sea' && t4.st === 'running' && t5.k === 'off' && !t5.stop && t5.ls === null, { t4, t5 });
  await ctx.close();
  // ── after a reload: the chosen tone waits for the first touch
  ({ ctx, pg } = await open(br, errs, { dash_tone: 'drops', dash_bg: 'waves' }));
  const r0 = await pg.evaluate(() => ({ ac: !!HT.ac, armed: HT.armed, bg: uiBg(), abg: document.documentElement.classList.contains('abg') }));
  await pg.mouse.click(200, 300); await pg.waitForTimeout(800);
  const r1 = await pg.evaluate(() => ({ ac: !!HT.ac, st: HT.ac && HT.ac.state, k: HT.k }));
  ok('🎶 after reopening: the chosen tone waits for the first touch, then plays · the chosen background is back at once', !r0.ac && r0.armed && r0.bg === 'waves' && r0.abg && r1.ac && r1.st === 'running' && r1.k === 'drops', { r0, r1 });
  await ctx.close();
  ok('no page errors', !errs.length, errs);
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_bgtone: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('crash', e); process.exit(1) });
