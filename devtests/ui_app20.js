// 📱 the move to app 2.0 in a real browser (run through t_app20.py — the real dashboard in a closed folder). window.HolyApp stands in for
//   the app's bridge (status() says which app version the phone runs; saveFile() records what the page saves):
//   · inside a 1.x app: the 📱 panel opens by itself once — the version row «نسخة جديدة بتوقيع جديد» + «⬇️ احفظها» · the four steps ·
//     why it is manual · the widget row names the six numbers; «⬇️ احفظها» saves «Holy-2.0.apk» through the app = the very APK
//     (sha256) and copies the dashboard's address; a reload within two days does not open it again
//   · inside 2.0: no panel by itself · no move text · «آخر نسخة» · in a browser: «remove Holy 1.x first» · no page error
const { chromium } = require('playwright');
const URL = process.argv[2], SHA = process.argv[3], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 700)));
}
function bridge(code, name) {
  return `(() => {
    window.__saved = []; window.__copied = [];
    const st = {code: ${code}, name: '${name}', paired: true, notif: true, watching: true, battery: true, running: true, id: 'dev1', android: 34,
                lock: false, lockOk: true, widget: 0, widgetPin: true, origin: location.origin};
    const fixed = {status: () => JSON.stringify(st), needPair: () => false, pairInfo: () => JSON.stringify({name: 'Pixel', iid: 'x', code: ${code}}),
                   saveFile: (n, t, b) => { window.__saved.push({n, t, b}) }, copy: t => { window.__copied.push(String(t)) }, bioUnlock: () => false};
    window.HolyApp = new Proxy(fixed, {get: (o, k) => (k in o ? o[k] : () => undefined)});
  })()`;
}
async function page(ctx, errs) {
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(URL, { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots, null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  return pg;
}
const modalText = pg => pg.evaluate(() => { const m = document.getElementById('modal'); const bg = document.getElementById('mbg');
  return bg && !bg.hidden && m ? m.innerText : '' });
(async () => {
  const br = await chromium.launch();
  const errs = [];
  // ── a phone still on 1.9
  const c1 = await br.newContext({ viewport: { width: 412, height: 900 } });
  await c1.addInitScript(bridge(10, '1.9'));
  let pg = await page(c1, errs);
  await pg.waitForFunction(() => /الانتقال إلى Holy/.test((document.getElementById('modal') || {}).innerText || ''), null, { timeout: 15000 }).catch(() => null);
  let t = await modalText(pg);
  ok('1.9 app: the 📱 panel opens by itself with «⬆️ الانتقال إلى Holy 2.0 — مرة واحدة»', /📱 تطبيق أندرويد/.test(t) && /الانتقال إلى Holy 2\.0 — مرة واحدة/.test(t), t.slice(0, 400));
  ok('… the version row: «1.9 · في اللوحة: 2.0 — نسخة جديدة بتوقيع جديد: تُثبَّت يدوياً مرة واحدة» and «⬇️ احفظها» (no «حدّث» that would fail)',
     /1\.9 · في اللوحة: 2\.0 — نسخة جديدة بتوقيع جديد: تُثبَّت يدوياً مرة واحدة/.test(t) && /⬇️ احفظها/.test(t)
     && !(await pg.evaluate(() => [...document.querySelectorAll('#ap_body button')].some(b => /^(حدّث|افحص)$/.test(b.textContent.trim())))), t);
  const steps = await pg.evaluate(() => [...document.querySelectorAll('#ap_body ol.ap-steps li')].map(li => li.innerText));
  ok('… the four steps: save · remove the current app (the dashboard and bots stay) · install from Files ← Downloads ← Holy · log in with the address, add the widget, unlink the old phone',
     steps.length === 4 && /احفظها/.test(steps[0]) && /Holy-2\.0\.apk/.test(steps[0]) && /إلغاء التثبيت/.test(steps[1]) && /لا تتأثر/.test(steps[1])
     && /الملفات/.test(steps[2]) && /التنزيلات ← Holy/.test(steps[2]) && /Holy-2\.0\.apk/.test(steps[2])
     && steps[3].includes(new globalThis.URL(URL).origin) && /الويدجت/.test(steps[3]) && /افصل الجهاز القديم/.test(steps[3]), steps);
  ok('… why it is manual (a new signing key · once only, then updates are automatic again) and the browser fallback',
     /موقّعة بمفتاح جديد/.test(t) && /مرة واحدة فقط/.test(t) && /يعود التحديث التلقائي/.test(t) && /متصفح الموبايل/.test(t), t.slice(-500));
  ok('… the widget row names the six numbers of 2.0', /ويدجت جديد بلون اللوحة البنفسجي وستة أرقام/.test(t)
     && /اليوم · أمس · آخر 7 أيام · آخر 30 يوماً · هذا الشهر · الإجمالي/.test(t), t);
  await pg.evaluate(() => [...document.querySelectorAll('#ap_body button')].find(b => /احفظها/.test(b.textContent)).click());
  await pg.waitForFunction(() => window.__saved.length > 0, null, { timeout: 15000 }).catch(() => null);
  const sv = await pg.evaluate(async () => {
    const s = window.__saved[0]; if (!s) return null;
    const bin = Uint8Array.from(atob(s.b), c => c.charCodeAt(0));
    const h = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bin))].map(x => x.toString(16).padStart(2, '0')).join('');
    return { n: s.n, t: s.t, len: bin.length, h, copied: window.__copied };
  });
  ok('«⬇️ احفظها» saves «Holy-2.0.apk» through the app (Android package type) = the very APK the dashboard carries (sha256) · copies the address',
     sv && sv.n === 'Holy-2.0.apk' && sv.t === 'application/vnd.android.package-archive' && sv.h === SHA && sv.copied.includes(new globalThis.URL(URL).origin), sv && { ...sv, h: sv.h.slice(0, 16) });
  await pg.reload({ waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof DATA !== 'undefined' && DATA && DATA.bots, null, { timeout: 30000 });
  await pg.waitForTimeout(4000);
  t = await modalText(pg);
  ok('… reloaded within two days: the panel does not open by itself again', !/الانتقال إلى Holy/.test(t), t.slice(0, 200));
  await c1.close();
  // ── a phone on 2.0
  const c2 = await br.newContext({ viewport: { width: 412, height: 900 } });
  await c2.addInitScript(bridge(11, '2.0'));
  pg = await page(c2, errs);
  await pg.waitForTimeout(4500);
  t = await modalText(pg);
  ok('2.0 app: the panel does not open by itself', !/تطبيق أندرويد/.test(t), t.slice(0, 200));
  await pg.evaluate(() => openAppPanel());
  await pg.waitForFunction(() => /نسخة التطبيق/.test((document.getElementById('ap_body') || {}).innerText || ''), null, { timeout: 15000 }).catch(() => null);
  t = await modalText(pg);
  ok('… opened by hand: «2.0 · باللوحة: 2.0 — آخر نسخة» · no move steps · no «⬇️ احفظها»',
     /2\.0 · باللوحة: 2\.0 — آخر نسخة/.test(t) && !/الانتقال إلى Holy/.test(t) && !/احفظها/.test(t) && !/بتوقيع جديد/.test(t), t.slice(0, 600));
  await c2.close();
  // ── a browser
  const c3 = await br.newContext({ viewport: { width: 1280, height: 900 } });
  pg = await page(c3, errs);
  await pg.evaluate(() => openAppPanel());
  await pg.waitForFunction(() => /نزّل التطبيق/.test((document.getElementById('ap_body') || {}).innerText || ''), null, { timeout: 15000 }).catch(() => null);
  t = await modalText(pg);
  ok('browser: «⬇️ نزّل التطبيق — Holy 2.0» with «🔐 عندك Holy 1.x على الموبايل؟ احذفه أولاً … مرة واحدة فقط»',
     /نزّل التطبيق — Holy 2\.0/.test(t) && /عندك Holy 1\.x على الموبايل؟ احذفه أولاً/.test(t) && /مرة واحدة فقط/.test(t), t.slice(0, 600));
  await c3.close();
  ok('no page error', errs.length === 0, errs);
  await br.close();
  console.log(`ui_app20 ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('❌ ui_app20 crashed — ' + e); process.exit(1) });
