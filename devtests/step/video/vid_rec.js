// 🎬 records the one-minute video: the dashboard's real 🪜 card (right) + the «OKX side» panel (left, fed by vid_sim.py) ·
//   intro (the settings) · the run (the bot's open orders on the exchange · the price · its fills · profit · books = wallet ·
//   a caption for each step) · the closing summary.   node vid_rec.js DASH_URL SIM_URL OUT_DIR
const { chromium } = require('playwright');
const [DASH, SIM, OUT] = process.argv.slice(2);
const W = 1440, H = 900;
(async () => {
  const br = await chromium.launch();
  const ctx = await br.newContext({ viewport: { width: W, height: H }, recordVideo: { dir: OUT, size: { width: W, height: H } } });
  await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off') } catch (e) {} });
  const pg = await ctx.newPage();
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});      // the page's OKX live-price socket: answered here, never the network
  await pg.goto(DASH, { waitUntil: 'domcontentloaded' });
  await pg.waitForSelector('.card[data-dir]', { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.evaluate((SIM) => {
    const css = document.createElement('style');
    css.textContent = `
#okxp{position:fixed;left:16px;top:16px;width:930px;bottom:16px;z-index:2147480000;background:rgba(10,8,24,.94);border:1px solid rgba(120,200,255,.35);
 border-radius:16px;padding:14px 16px;color:#e8ecff;padding-bottom:100px;font:14px/1.5 system-ui,'Segoe UI',Tahoma,sans-serif;direction:rtl;box-shadow:0 10px 40px rgba(0,0,0,.5)}
#okxp h3{margin:0 0 8px;font-size:17px;color:#7fd7ff}
#okxp .row{display:flex;gap:14px}
#okxp .col{flex:1;min-width:0}
#okxp .px{font:700 30px/1.1 ui-monospace,monospace;direction:ltr;text-align:right}
#okxp .up{color:#3ddc97}#okxp .dn{color:#ff5c7a}
#okxp table{width:100%;border-collapse:collapse;font:12.5px/1.35 ui-monospace,monospace}
#okxp td{padding:2px 6px;border-bottom:1px solid rgba(255,255,255,.06);direction:ltr;text-align:right;white-space:nowrap}
#okxp tr.s td{color:#ff7b93}#okxp tr.b td{color:#43e3a0}
#okxp tr.p td{color:#ffd166;font-weight:700;border-top:2px solid #ffd16688;border-bottom:2px solid #ffd16688}
#okxp td.lv{direction:rtl;font-family:system-ui;color:#aab}
#okxp .ev{font-size:13px;line-height:1.55;max-height:220px;overflow:hidden}
#okxp .ev div{padding:2px 0;border-bottom:1px solid rgba(255,255,255,.05)}
#okxp .st{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13.5px;margin-top:8px}
#okxp .st b{color:#fff}
#okxp .mem{font-size:12.5px;color:#aab;margin:4px 0}
#capb{position:fixed;left:30px;width:902px;bottom:30px;z-index:2147480001;background:linear-gradient(90deg,#1b1240ee,#0b2a3aee);
 border:1px solid #ffd16699;border-radius:14px;padding:12px 18px;color:#fff;font:600 19px/1.5 system-ui,'Segoe UI',Tahoma,sans-serif;
 direction:rtl;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.6)}
#ovl{position:fixed;inset:0;z-index:2147480002;display:flex;align-items:center;justify-content:center;background:rgba(6,4,16,.93);
 color:#fff;font:600 22px/1.8 system-ui,'Segoe UI',Tahoma,sans-serif;direction:rtl;text-align:center;padding:40px}
#ovl .t{font-size:34px;color:#7fd7ff;margin-bottom:14px}
#ovl small{display:block;color:#ffd166;font-size:17px;margin-top:14px}
#offv{position:fixed;left:16px;top:16px;width:930px;bottom:16px;z-index:2147480000;display:none;align-items:center;justify-content:center;
 background:rgba(30,0,8,.9);border-radius:16px;color:#ffd166;font:800 40px/1.6 system-ui;direction:rtl;text-align:center}`;
    document.head.appendChild(css);
    const p = document.createElement('div'); p.id = 'okxp'; document.body.appendChild(p);
    const c = document.createElement('div'); c.id = 'capb'; document.body.appendChild(c);
    const o = document.createElement('div'); o.id = 'offv'; o.innerHTML = '<div>⚡ البوت طافي<div style="font-size:22px;font-weight:600">المنصة تكمل… والسعر يتحرك — أوامره هناك تتنفّذ</div></div>'; document.body.appendChild(o);
    let prev = null;
    const f = (v, d = 4) => (+v).toFixed(d);
    async function poll() {
      let V = null;
      try { V = await (await fetch(SIM + '/okx.json', { cache: 'no-store' })).json() } catch (e) {}
      if (V && V.px) {
        const dir = prev == null ? '' : (V.px > prev ? 'up' : V.px < prev ? 'dn' : ''); prev = V.px;
        const R = V.orders || [];
        const sells = R.filter(r => r.side === 'sell'), buys = R.filter(r => r.side === 'buy');
        const row = r => `<tr class="${r.side === 'sell' ? 's' : 'b'}"><td>${f(r.px)}</td><td>${(+r.sz).toFixed(3)}</td><td class="lv">${r.side === 'sell' ? 'بيع' : 'شراء'} · المستوى ${r.j} · الجزء ${r.k}${r.acc > 0 ? ' · نُفّذ جزء' : ''}</td></tr>`;
        const S = V.stats || {};
        p.innerHTML = `<h3>📡 المنصة (OKX — منصة وهمية بالمحرك الحقيقي، بلا أموال حقيقية): أوامر البوت المفتوحة</h3>
          <div class="row"><div class="col" style="flex:1.15">
            <div class="mem">على المنصة: <b>${buys.length}</b> شراء · <b>${sells.length}</b> بيع (الأقرب للسعر) — بذاكرة البوت: ${(V.mem || {}).buy || 0} شراء · ${(V.mem || {}).sell || 0} بيع</div>
            <table>${sells.map(row).join('')}<tr class="p"><td>${f(V.px)}</td><td colspan="2" class="lv" style="color:#ffd166">◀ السعر الآن</td></tr>${buys.map(row).join('')}</table>
          </div><div class="col">
            <div class="px ${dir}">${f(V.px)} ${dir === 'up' ? '▲' : dir === 'dn' ? '▼' : ''}</div>
            <div class="st"><span>💰 الربح المحقق <b>${(+S.tp || 0).toFixed(4)}$</b></span><span>🟢 شراء <b>${S.nb || 0}</b></span><span>🔴 بيع <b>${S.ns || 0}</b></span>
              <span>⚡ انقطاع <b>${S.cuts || 0}</b></span><span>${S.ok ? '✅' : '❌'} المحفظة = الدفتر <b>${S.audits || 0}</b> فحص</span></div>
            <h3 style="margin-top:10px">🧾 آخر ما صار</h3><div class="ev">${(V.events || []).map(e => `<div>${e}</div>`).join('')}</div>
          </div></div>`;
        c.textContent = V.cap || '';
        o.style.display = V.off ? 'flex' : 'none';
        window.__V = V;
      }
      setTimeout(poll, 250);
    }
    poll();
    setInterval(() => { try { tick() } catch (e) {} }, 1000);       // the card refreshes every second in the video
  }, SIM);
  await pg.evaluate(() => {                     // the card at the top of the screen (kept there: the page re-renders)
    const fix = () => { const c = document.querySelector('.card[data-dir]'); if (!c) return;
      const se = document.scrollingElement || document.documentElement; const y = c.getBoundingClientRect().top + se.scrollTop - 8;
      if (Math.abs(se.scrollTop - y) > 4) se.scrollTop = y };
    fix(); setInterval(fix, 500) });
  // intro
  await pg.evaluate(() => {
    const o = document.createElement('div'); o.id = 'ovl';
    o.innerHTML = `<div><div class="t">🪜 الشبكي المتدرج — شلون يوزّع الأوامر وشلون يربح</div>
      15$ لكل شراء · 3 بيعات لكل شراء · أول بيعة 1% · بين البيعات 0.5% · الشراء كل 3% · الأرضية 0.7 · مستوى واحد من عملاتك · البداية 1.00
      <br>يمين: بطاقة البوت باللوحة نفسها · يسار: أوامره على المنصة
      <small>⚠️ تجربة: المحرك الحقيقي على منصة وهمية — بلا مفاتيح ولا أموال حقيقية · الوقت مسرَّع</small></div>`;
    document.body.appendChild(o);
  });
  await pg.waitForTimeout(5000);
  await pg.evaluate(() => document.getElementById('ovl').remove());
  await pg.evaluate(async (SIM) => { try { await fetch(SIM + '/go') } catch (e) {} }, SIM);
  const t0 = Date.now();
  while (Date.now() - t0 < 52000) {
    const done = await pg.evaluate(() => !!(window.__V && window.__V.done));
    if (done) break;
    await pg.waitForTimeout(400);
  }
  await pg.waitForTimeout(1200);
  // summary
  await pg.evaluate(() => {
    const V = window.__V || {}, S = V.stats || {};
    const o = document.createElement('div'); o.id = 'ovl';
    o.innerHTML = `<div><div class="t">✅ الخلاصة</div>
      🟢 ${S.nb} شراء · 🔴 ${S.ns} بيع · 💰 ربح محقق ${(+S.tp).toFixed(4)}$ · أقل ربح بيعة ${S.minpr != null ? (S.minpr > 0 ? '+' : '') + (+S.minpr).toFixed(4) + '$' : '—'} (بعد العمولتين)
      <br>✋ أمر انمسح بالغلط ⇒ رجع انشر · ⚡ انقطاع كهرباء والسعر يتحرك ⇒ رجع وحسب اللي صار مرة وحدة · 📉 قفزة −5% ⇒ نفّذ بسعر أحسن
      <br>${S.ok ? '✅' : '❌'} المحفظة = الدفتر بكل دورة (${S.audits} فحص) · ولا أمر مرتين ولا تنفيذ ضاع
      <small>العملات نفسها رجعت تنشرى بمكانها — الربح بالدولار</small></div>`;
    document.body.appendChild(o);
  });
  await pg.waitForTimeout(6500);
  const V = await pg.evaluate(() => window.__V);
  await pg.close();
  await ctx.close();
  await br.close();
  console.log(JSON.stringify({ stats: V && V.stats, done: V && V.done }));
})().catch(e => { console.log('❌ ' + e); process.exit(1); });
