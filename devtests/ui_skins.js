// 🃏🔤📈 v3.36.33 in a real browser (run through ui_skins.py — every card kind in a closed folder):
//   · skins ج · ب · OKX: every value the old card shows (each visible label/value row) is on the skin · no text cut with «…» ·
//     no «🗂️ كل التفاصيل (الشكل القديم)» in any «⋯» · every button of the old card reachable (main · icons · «⋯») · the buttons carry
//     their full label
//   · 📈 every card (old and skins) shows «يومي / شهري / سنوي» from the bot's own trading (DATA's rate_daily) · 🔁 and 💹 got the rows
//   · 🔤 ⚙️ «خط الكتابة»: nine fonts, each button in its own font · choosing one sets the page font (the numbers stay monospace), loads
//     only that font, is kept on this device and applied before the page paints after a reload · «خط الجهاز» loads nothing · back to
//     the default forgets the choice · no page error
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
async function open(br, skin, errs) {
  const ctx = await br.newContext({ viewport: { width: 1440, height: 1000 } });
  await ctx.addInitScript(v => { try { localStorage.setItem('dash_stick', 'off'); if (v) localStorage.setItem('dash_skin', v); else localStorage.removeItem('dash_skin') } catch (e) {} }, skin);
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots && DATA.bots.length >= 9 && document.querySelectorAll('.card[data-dir]').length >= 9, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(2500);
  return { ctx, pg };
}
(async () => {
  const br = await chromium.launch();
  const errs = [];
  // ── 📈 the old cards
  let { ctx, pg } = await open(br, null, errs);
  const old = await pg.evaluate(() => [...document.querySelectorAll('.card[data-dir]')].map(el => {
    const b = botOf(el.dataset.dir) || {}, R = el._r || {};
    return { sym: b.symbol, t: b.bot_type, want: rateTxt(b), got: R.rates ? R.rates.textContent.trim() : null,
             gotD: R.rday ? [R.rday.textContent, R.rmon.textContent, R.ryear.textContent].join(' / ') : null, age: R.age ? R.age.textContent.trim() : null,
             tip: R.rates ? R.rates.title : (R.rday ? R.rday.title : ''), rd: b.rate_daily, u: b.rate_unit };
  }));
  const x = old.find(o => o.sym === 'XRP-USDT') || {};
  ok(`📈 ♾️ 💠 100% (counter ~0): the card shows «${x.got}» from its own trading`, x.got === x.want && /^\+0\.8\d{3}\$ \/ \+25\.\d\d\$ \/ \+31\d\.\d\$$/.test(x.got), x);
  const bad = old.filter(o => o.t !== 'dca' && o.t !== 'dca_buy' ? o.got !== o.want || o.got === '—' : !o.gotD || o.gotD.includes('—'));
  ok('📈 every card shows its rate (♾️ ➕ 🎚️ 🪜 · 🔁 🟢/🔴 · 💹 got the rows · DCA daily/monthly/yearly) — none «—»', !bad.length, bad);
  const rv = old.filter(o => /^rec_/.test(o.t));
  ok('📈 🔁 periodic and 💹 value path now carry «⏱️ التشغيل» and «📈 معدل يومي / شهري / سنوي» (the 🔴 one in its coin: XLM)',
     rv.length === 3 && rv.every(o => o.age && o.age !== '—' && o.got !== '—') && (rv.find(o => o.t === 'rec_sell') || {}).got.includes(' XLM'), rv);
  ok('📈 the tip says where it comes from (its own trading · ÷ days · the counter unchanged)', /من تداوله هو/.test(x.tip) && /عدّاد الربح لا يتغيّر/.test(x.tip), x.tip);
  // ── 🔤 the fonts
  await pg.evaluate(() => openSettings());
  await pg.waitForSelector('#fontRow button', { state: 'attached', timeout: 10000 });   // v3.36.35: inside the closed «خط الكتابة» row
  const fr = await pg.evaluate(() => [...document.querySelectorAll('#fontRow button')].map(b => ({ t: b.textContent, f: b.style.fontFamily, on: b.classList.contains('on'), k: b.dataset.font })));
  ok(`🔤 ⚙️ «خط الكتابة»: ${fr.length} fonts, each button written in its own font · the default (IBM Plex) on`,
     fr.length === 9 && fr.every(b => b.f) && (fr.find(b => b.k === 'plex') || {}).on && fr.some(b => /Cairo/.test(b.f)) && fr.some(b => b.k === 'sys'), fr);
  await pg.evaluate(() => setFont('cairo'));
  await pg.waitForTimeout(400);
  let F = await pg.evaluate(() => ({ ff: getComputedStyle(document.documentElement).getPropertyValue('--ff').trim(), body: getComputedStyle(document.body).fontFamily,
    num: getComputedStyle(document.querySelector('.num')).fontFamily, link: (document.getElementById('hfont-cairo') || {}).href || '', ls: localStorage.getItem('dash_font'),
    links: [...document.querySelectorAll('link[id^="hfont-"]')].map(l => l.id) }));
  ok('🔤 «Cairo»: the page font is Cairo · its file asked for (only it) · kept on this device · the numbers in Cairo too (v3.36.37)',
     /Cairo/.test(F.ff) && /^"?Cairo/.test(F.body) && /family=Cairo/.test(F.link) && F.ls === 'cairo' && /^"?'?Cairo/.test(F.num) && F.links.join() === 'hfont-cairo', F);
  await pg.reload({ waitUntil: 'domcontentloaded' });
  F = await pg.evaluate(() => ({ ff: getComputedStyle(document.documentElement).getPropertyValue('--ff').trim(), link: !!document.getElementById('hfont-cairo') }));
  ok('🔤 after a reload: Cairo applied as the page loads (before the first paint — no flash of the old font)', /Cairo/.test(F.ff) && F.link, F);
  await pg.waitForFunction(() => typeof setFont === 'function' && typeof DATA !== 'undefined' && DATA, null, { timeout: 30000 });
  await pg.evaluate(() => setFont('sys'));
  F = await pg.evaluate(() => ({ ff: getComputedStyle(document.documentElement).getPropertyValue('--ff').trim(), ls: localStorage.getItem('dash_font'), sysLink: !!document.getElementById('hfont-sys') }));
  ok('🔤 «خط الجهاز»: the system font, nothing loaded', F.ff === 'system-ui' && F.ls === 'sys' && !F.sysLink, F);
  await pg.evaluate(() => setFont('plex'));
  F = await pg.evaluate(() => ({ ff: getComputedStyle(document.documentElement).getPropertyValue('--ff').trim(), ls: localStorage.getItem('dash_font') }));
  ok('🔤 back to the default: IBM Plex Sans Arabic · the choice forgotten', /IBM Plex Sans Arabic/.test(F.ff) && F.ls === null, F);
  await ctx.close();
  // ── 🃏 the skins
  for (const [sk, nm] of [['c', 'ج'], ['b', 'ب'], ['o', 'OKX']]) {
    ({ ctx, pg } = await open(br, sk, errs));
    const R = await pg.evaluate(() => {
      const nz = s => String(s || '').replace(/\s+/g, ' ').trim();
      const skipK = new Set(['cp', 'profit', 'today', 'delta', 'apl', 'pill', 'apill', 'hb', 'ptrend']);
      const hid = (n, el) => { for (let p = n; p && p !== el; p = p.parentElement) if (p.style && p.style.display === 'none') return true; return false };
      const out = { missing: [], cut: [], full: false, unreach: [], cards: 0, rates: [] };
      document.querySelectorAll('.card.sk').forEach(el => {
        out.cards++;
        const sv = el._skv, sTxt = nz(sv.textContent), M = el._skM || {};      // textContent: a section drawn lazily (content-visibility) has no innerText
        el.querySelectorAll('.row,.dcacell,.rcrow,.dcacyclbl,.rcri,.blbl').forEach(r => {
          if (r.closest('.skin') || hid(r, el)) return;
          const v = [...r.querySelectorAll('[data-k]')].find(n => n.tagName !== 'BUTTON' && !/(fill|bar|row)$/.test(n.dataset.k));
          if (!v || skipK.has(v.dataset.k)) return;
          const t = nz(v.textContent);
          const parts = t.split(/\s+|·/).filter(w => w.length > 1);            // the number and its unit may sit in separate places («+12.3456» · «DOGE»)
          if (t && t !== '—' && parts.some(w => !sTxt.includes(w))) out.missing.push((el.dataset.dir || 'acc') + ' ' + v.dataset.k + '=' + t);
        });
        sv.querySelectorAll('*').forEach(n => { if (n.children.length && !n.matches('button')) return; const cs = getComputedStyle(n);
          if (n.scrollWidth > n.clientWidth + 1 && /hidden/.test(cs.overflow + cs.overflowX) && cs.textOverflow === 'ellipsis') out.cut.push(nz(n.textContent).slice(0, 30)) });
        if ((M.menu || []).some(x => x.k === 'full' || /كل التفاصيل/.test(x.t))) out.full = true;
        const have = new Set([(M.main || {}).k].concat((M.ic || []).map(x => x.k), (M.menu || []).map(x => x.k)));
        el.querySelectorAll('button[data-k]').forEach(n => { if (n.closest('.skin') || hid(n, el)) return; const t = nz(n.textContent) || n.title;
          if (t && t !== '—' && !have.has(n.dataset.k)) out.unreach.push((el.dataset.dir || 'acc') + ' ' + n.dataset.k) });
        const b = el.dataset.dir ? botOf(el.dataset.dir) : null;
        if (b && b.bot_type !== 'dca' && b.bot_type !== 'dca_buy' && rateTxt(b).split(' / ').some(w => !sTxt.includes(w))) out.rates.push(b.symbol);
      });
      const c = document.querySelector('.card.sk[data-dir]');
      skAct(c, 'menu');
      out.menuTxt = nz((c._skv.querySelector('.sk-menu') || {}).innerText || '');
      out.btns = [...c._skv.querySelectorAll('.sk-ft button,.ok-ft>button,.sk-seg button')].map(b => nz(b.textContent));
      skAct(c, 'menu');
      return out;
    });
    ok(`🃏 ${nm}: all ${R.cards} cards — every value of the old card is on the skin`, R.cards === 10 && !R.missing.length, R.missing);
    ok(`🃏 ${nm}: no text cut with «…»`, !R.cut.length, R.cut);
    ok(`🃏 ${nm}: no «🗂️ كل التفاصيل (الشكل القديم)» (the open «⋯»: ${R.menuTxt.slice(0, 80)}…)`, !R.full && R.menuTxt && !/كل التفاصيل/.test(R.menuTxt), R.menuTxt);
    ok(`🃏 ${nm}: every button of the old card reachable · full labels (${R.btns.slice(0, 4).join(' · ')})`,
       !R.unreach.length && R.btns.some(t => /شارت/.test(t)) && R.btns.some(t => /السجل/.test(t)), [R.unreach, R.btns]);
    ok(`🃏 ${nm}: the rate «يومي / شهري / سنوي» on every non-DCA card`, !R.rates.length, R.rates);
    await ctx.close();
  }
  ok('no page error', errs.length === 0, errs);
  await br.close();
  console.log(`ui_skins ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_skins crashed — ' + e); process.exit(1) });
