// 🪜 the graded grid's card in a real browser, every skin (old · ج · ب · OKX) — run through ui_card.py (the real dashboard + the real
//   engine on the mock OKX): the vertical price ruler matches the bot's slots (one buy line per level with its published count ·
//   one line per published sell · each line at its price · a level and its sells one colour · the old strip hidden) · a tap ⇒ the
//   details of that level / sell · a ♾️ grid card next to it keeps its own ladder and strip · no page error
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 700)));
}
(async () => {
  const br = await chromium.launch();
  for (const sk of ['old', 'c', 'b', 'o']) {
    const ctx = await br.newContext({ viewport: { width: 1440, height: 1000 } });
    await ctx.addInitScript(v => { try { localStorage.setItem('dash_stick', 'off'); if (v !== 'old') localStorage.setItem('dash_skin', v); else localStorage.removeItem('dash_skin') } catch (e) {} }, sk);
    const pg = await ctx.newPage();
    const errs = []; pg.on('pageerror', e => errs.push(String(e)));
    await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
    await pg.goto(URL, { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.some(b => b.bot_type === 'grid_step' && (b.sl || []).length), null, { timeout: 30000 });
    await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
    await pg.waitForTimeout(2500);
    let r = null;
    for (let i = 0; i < 6; i++) {                     // (the card and DATA refresh every second — check a frame where they agree)
      r = await pg.evaluate(() => {
        const b = DATA.bots.find(x => x.bot_type === 'grid_step'), sv = [...document.querySelectorAll('svg.stlad')].find(s => s.getAttribute('data-stl-bot') === b.dir);
        if (!sv) return { none: true };
        const SL = b.sl || [], lv = {};
        SL.forEach(x => { if (x[2] === 'b' && x[5] !== 'M') { lv[x[0]] = (lv[x[0]] || 0) + 1 } });
        const sells = SL.filter(x => x[2] === 's' && x[5] !== 'M');
        const ln = g => { const l = g.querySelector('line'); return { y: +l.getAttribute('y1'), c: l.getAttribute('stroke') } };
        const BL = [...sv.querySelectorAll('[data-stl^="b:"]')].map(g => ({ j: +g.getAttribute('data-stl').split(':')[1], t: g.textContent, ...ln(g) }));
        const SLN = [...sv.querySelectorAll('[data-stl^="s:"]')].map(g => { const [, j, k] = g.getAttribute('data-stl').split(':'); return { j: +j, k: +k, ...ln(g) } });
        const px = {}; SL.forEach(x => { if (x[2] === 'b' && x[5] !== 'M') px['b:' + x[0]] = +x[3]; if (x[2] === 's') px['s:' + x[0] + ':' + x[1]] = +x[3] });
        const pts = BL.map(l => ({ p: px['b:' + l.j], y: l.y })).concat(SLN.map(l => ({ p: px['s:' + l.j + ':' + l.k], y: l.y })));
        pts.sort((a, z) => z.p - a.p);
        let mono = true; for (let i = 1; i < pts.length; i++) if (pts[i].p < pts[i - 1].p - 1e-12 && !(pts[i].y > pts[i - 1].y - 1e-6)) mono = false;
        const col = {}; BL.forEach(l => col[l.j] = l.c); const same = SLN.every(l => !(l.j in col) || col[l.j] === l.c);
        const cnt = BL.every(l => l.t.includes(String(lv[l.j])));
        const strip = sk => { const c = document.querySelector(`.card[data-dir="${CSS.escape(b.dir)}"] .pstrip`); return c ? getComputedStyle(c).display : 'none' };
        const other = DATA.bots.find(x => x.bot_type === 'grid');
        const oc = other ? document.querySelector(`.card[data-dir="${CSS.escape(other.dir)}"]`) : null;
        return { nb: BL.length, nlv: Object.keys(lv).length, ns: SLN.length, nsl: sells.length, mono, same, cnt, red: BL.concat(SLN).some(l => /#ef4444|hsl\(0 /i.test(l.c)),
                 strip: strip(), otherStlad: oc ? !!oc.querySelector('svg.stlad') : null, otherStrip: oc ? getComputedStyle(oc.querySelector('.pstrip')).display : null };
      });
      if (r && !r.none && r.nb === r.nlv && r.ns === r.nsl && r.mono && r.same && r.cnt) break;
      await pg.waitForTimeout(350);
    }
    ok(`[${sk}] the ruler matches the slots: ${r.nb} buy lines = ${r.nlv} levels with published buys (each with its count) · ${r.ns} sell lines = ${r.nsl} published sells`,
       r && !r.none && r.nb === r.nlv && r.ns === r.nsl && r.cnt, r);
    ok(`[${sk}] every line at its price (higher = higher on the card) · a level's buy line and its sells one colour · no red`, r && r.mono && r.same && !r.red, r);
    if (sk === 'old') ok('[old] the horizontal strip is not drawn for the graded grid · a ♾️ grid card keeps its ladder and strip',
       r && r.strip === 'none' && r.otherStlad === false && r.otherStrip !== 'none', r);
    const pop = async sel => {                    // (the card redraws every second: tap the line as it is now, not a handle to an old one)
      const hit = await pg.evaluate(sel => { const el = document.querySelector(sel); if (!el) return false; const r = el.getBoundingClientRect();
        el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 })); return true }, sel);
      if (!hit) return null; await pg.waitForTimeout(300);
      return pg.evaluate(() => { const p = document.getElementById('stpop'); const t = p && p.style.display === 'block' ? p.innerText : null; if (p) p.style.display = 'none'; return t }) };
    const pb = await pop('svg.stlad [data-stl^="b:"]'), ps = await pop('svg.stlad [data-stl^="s:"]');
    ok(`[${sk}] tap a buy line ⇒ the level's details (its fixed buy · every part where it is) · tap a sell ⇒ its part, price, distance and profit`,
       pb && /المستوى/.test(pb) && /الجزء 1\//.test(pb) && (ps === null || (/بيعة الجزء \d+\/\d+ من المستوى/.test(ps) && /ربحها/.test(ps))), { pb, ps });
    ok(`[${sk}] no page error`, errs.length === 0, errs.slice(0, 3));
    await ctx.close();
  }
  await br.close();
  console.log(`${res.filter(Boolean).length} ok · ${res.length - res.filter(Boolean).length} failed`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ crash ' + e); process.exit(1); });
