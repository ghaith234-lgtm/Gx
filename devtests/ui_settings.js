// ⚙️ v3.36.35 in a real browser (run through ui_settings.py — every card kind in a closed folder): the settings as a list —
//   the owner (13-11): «الاعدادات سوي الكل لستات يعني المظهر اضغط عليه يظهرن اللوان كذلك الفريمات يعني كلهم · واريد التوزيع يختلف مثلا
//   صوت الربح مع صوت القفل شريط الاسعار مع التليجرام لان اثنينهم خاصه بالاشعارات» · + a window drawn again keeps its scroll place
const { chromium } = require('playwright');
const URL = process.argv[2], Q = process.argv.includes('-q');
const res = [];
function ok(name, cond, det) {
  res.push(!!cond);
  if (!Q || !cond) console.log((cond ? '✅ ' : '❌ ') + name + (cond ? '' : ' — ' + String(JSON.stringify(det)).slice(0, 900)));
}
async function open(br, vw, vh, errs, mobile) {
  const ctx = await br.newContext({ viewport: { width: vw, height: vh }, isMobile: !!mobile, hasTouch: !!mobile });
  await ctx.addInitScript(() => { try { localStorage.setItem('dash_stick', 'off'); localStorage.setItem('dash_anim', 'none') } catch (e) {} });
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
const vis = 'el => !!el && el.offsetHeight > 0';
(async () => {
  const br = await chromium.launch();
  const errs = [];
  let { ctx, pg } = await open(br, 412, 900, errs, true);
  await pg.evaluate(() => openSettings()); await pg.waitForTimeout(300);
  // ── the groups and their order
  const gr = await pg.evaluate(() => [...document.querySelectorAll('#modal .sgrp')].map(g => ({
    t: g.querySelector('.sgt').textContent.trim(), rows: [...g.querySelectorAll('.sgl>.sitem')].map(r => (r.querySelector('.stt b') || {}).textContent) })));
  const GT = ['🖌️ الشكل والحركة', '⚡ الأداء', '🔔 الإشعارات', '🔊 الأصوات', '📱 التطبيقات', '🛡️ الحماية والتشغيل', '🩺 التشخيص', '🖥️ النظام', '⚠️ منطقة الخطر'];
  ok(`⚙️ ${gr.length} groups in order: ${gr.map(g => g.t.split(' — ')[0]).join(' · ')}`, gr.length === 9 && GT.every((t, i) => gr[i] && gr[i].t.startsWith(t)), gr.map(g => g.t));
  const G = t => (gr.find(g => g.t.startsWith(t)) || { rows: [] }).rows;
  ok('🔔 the notifications together: Telegram + the price ticker (its alerts)', G('🔔').join('|') === 'تنبيهات تيليغرام|شريط الأسعار وإشعاراته', G('🔔'));
  ok('🔊 the sounds together: the profit sound + the unlock sound (+ the continuous tone, v3.36.37)', G('🔊').join('|') === 'صوت الربح|صوت فتح القفل|النغمة المستمرة', G('🔊'));
  ok('🖌️ the look: الألوان · الخلفية · البطاقات · الخط · الحركة · حركات البطاقات · الشريط المصغّر · رجل العصا', G('🖌️').join('|') === 'الألوان|الخلفية|شكل البطاقات|خط الكتابة|حركة فتح النوافذ|حركات البطاقات|الشريط المصغّر|رجل العصا', G('🖌️'));
  ok('⚡ the performance: الوضع الخفيف · تحديث الأرقام · الفريمات', G('⚡').join('|') === 'الوضع الخفيف|تحديث الأرقام|الفريمات', G('⚡'));
  // ── every row with choices: closed, shows its value
  const sx = await pg.evaluate(() => [...document.querySelectorAll('#modal .sx')].map(r => ({ k: r.dataset.k, open: r.classList.contains('open'),
    body: r.querySelector('.sbody').offsetHeight, val: r.querySelector('.sval').textContent.trim(), aria: r.querySelector('.shd').getAttribute('aria-expanded') })));
  ok(`⚙️ ${sx.length} rows with choices (${sx.map(x => x.k).join(' · ')}) — all closed at first, their choices hidden`, sx.map(x => x.k).join() === 'theme,bg,skin,font,anim,cfx,poll,fps,tone' && sx.every(x => !x.open && !x.body && x.aria === 'false'), sx);
  const want = await pg.evaluate(() => ({ theme: (THEMES.find(t => t[0] === uiTheme()) || [])[1], font: (HFONTS.find(x => x[0] === uiFont()) || [])[2],
    anim: (HW_ANIMS.find(x => x[0] === uiAnim()) || [])[1], fps: uiFps() + ' فريم', poll: pollMs() === 3000 ? 'عادي 3ث' : '?', skin: 'القديم', bg: 'الأصلية', tone: 'بلا', cfx: '5 من 5 تعمل' }));
  const badV = sx.filter(x => !x.val.startsWith(want[x.k]));
  ok(`⚙️ each row shows its current value without opening it (المظهر «${want.theme}» · الفريمات «${want.fps}» …)`, !badV.length, { badV, want });
  // ── tap المظهر ⇒ the colours · tap again ⇒ hidden
  await pg.click('#modal .sx[data-k="theme"] .shd'); await pg.waitForTimeout(300);
  const t1 = await pg.evaluate(() => { const r = document.querySelector('#modal .sx[data-k="theme"]'); return { open: r.classList.contains('open'), n: r.querySelectorAll('.sbody .thb').length,
    shown: [...r.querySelectorAll('.thb')].filter(b => b.offsetHeight > 0).length, aria: r.querySelector('.shd').getAttribute('aria-expanded'), others: [...document.querySelectorAll('#modal .sx.open')].length } });
  ok(`🎨 a tap on «الألوان» shows the ${t1.n} colours (only that row opens)`, t1.open && t1.n >= 7 && t1.shown === t1.n && t1.aria === 'true' && t1.others === 1, t1);
  await pg.click('#modal .sx[data-k="theme"] .shd'); await pg.waitForTimeout(250);
  const t2 = await pg.evaluate(() => document.querySelector('#modal .sx[data-k="theme"] .sbody').offsetHeight);
  ok('🎨 a second tap closes it', t2 === 0, t2);
  // ── 🎞️ the frames: tap ⇒ the 4 choices + the graphics line
  await pg.click('#modal .sx[data-k="fps"] .shd'); await pg.waitForTimeout(500);
  const f1 = await pg.evaluate(() => ({ b: [...document.querySelectorAll('#fpsRow button')].filter(b => b.offsetHeight > 0).map(b => b.textContent), gpu: (document.getElementById('gpuNote') || {}).textContent || '' }));
  ok(`🎞️ a tap on «الفريمات» shows ${f1.b.join(' · ')} + the graphics line`, f1.b.join() === '240,120,60,30' && f1.gpu.length > 4 && !/^🎮 …$/.test(f1.gpu.trim()), f1);
  // ── a choice draws the window again: the open rows stay open · the place it was scrolled to stays
  await pg.evaluate(() => { const b = document.querySelector('#modal .hwb'); b.scrollTop = 0; document.querySelector('#modal .sx[data-k="fps"]').scrollIntoView({ block: 'start' }) });
  await pg.waitForTimeout(150);
  const y0 = await pg.evaluate(() => document.querySelector('#modal .hwb').scrollTop);
  await pg.evaluate(() => setPoll(6000)); await pg.waitForTimeout(250);
  const r1 = await pg.evaluate(() => ({ y: document.querySelector('#modal .hwb').scrollTop, open: [...document.querySelectorAll('#modal .sx.open')].map(r => r.dataset.k),
    val: document.querySelector('#modal .sx[data-k="poll"] .sval').textContent.trim() }));
  ok(`↕️ a choice (⏱️ 6ث) draws ⚙️ again: still at its place (${y0} → ${r1.y} px) · «الفريمات» still open · the row shows «${r1.val}»`, y0 > 100 && Math.abs(r1.y - y0) <= 2 && r1.open.join() === 'fps' && r1.val.startsWith('موفّر'), { y0, r1 });
  await pg.evaluate(() => setPoll(3000)); await pg.waitForTimeout(150);
  await pg.evaluate(() => { stTog('theme') }); await pg.waitForTimeout(100);
  await pg.evaluate(() => setTheme('ocean')); await pg.waitForTimeout(250);
  const th = await pg.evaluate(() => ({ open: document.querySelector('#modal .sx[data-k="theme"]').classList.contains('open'), val: document.querySelector('#modal .sx[data-k="theme"] .sval').textContent.trim(),
    on: (document.querySelector('#modal .thb.on') || {}).title }));
  ok(`🎨 choosing a colour: «الألوان» stays open · the row and the ✓ follow («${th.val}»)`, th.open && th.val === 'أزرق محيطي' && th.on === 'أزرق محيطي', th);
  await pg.evaluate(() => { setTheme('holy'); stTog('theme'); stTog('fps') }); await pg.waitForTimeout(200);
  await pg.evaluate(() => { document.querySelector('#modal .hwb').scrollTop = 400; showModal('<h2>🧪 نافذة أخرى</h2><div style="height:3000px"></div>') }); await pg.waitForTimeout(150);
  const other = await pg.evaluate(() => document.querySelector('#modal .hwb').scrollTop);
  ok('↕️ a different window opened in its place starts at its top', other === 0, other);
  await pg.evaluate(() => hideModal()); await pg.waitForTimeout(150);
  await pg.evaluate(() => openSettings()); await pg.waitForTimeout(250);
  // ── the switches
  const sw = await pg.evaluate(() => [...document.querySelectorAll('#modal .stg')].map(b => ({ id: b.id, role: b.getAttribute('role'), aria: b.getAttribute('aria-checked'), on: b.classList.contains('on'),
    sw: !!b.querySelector('.ssw'), h: Math.round(b.getBoundingClientRect().height) })));
  const SW = ['bStk', 'bLite', 'sMute', 'sSound', 'bUnl', 'bCLock', 'bWd'];
  ok(`🔘 on/off settings carry a switch on their own row (${sw.map(s => s.id).join(' · ')}) — the switch says the same as the row`, SW.every(id => sw.some(s => s.id === id)) && sw.every(s => s.role === 'switch' && s.sw && s.aria === String(s.on) && s.h >= 48), sw);
  await pg.evaluate(() => localStorage.removeItem('dash_anim'));    // a motion chosen (the default) ⇒ the light mode pauses it
  const l0 = await pg.evaluate(() => ({ lite: document.documentElement.classList.contains('lite'), on: document.getElementById('bLite').classList.contains('on') }));
  await pg.click('#bLite'); await pg.waitForTimeout(250);
  const l1 = await pg.evaluate(() => ({ lite: document.documentElement.classList.contains('lite'), on: document.getElementById('bLite').classList.contains('on'), small: document.querySelector('#bLite small').textContent,
    anim: document.querySelector('#modal .sx[data-k="anim"] .sval').textContent }));
  await pg.click('#bLite'); await pg.waitForTimeout(250);
  const l2 = await pg.evaluate(() => ({ lite: document.documentElement.classList.contains('lite'), on: document.getElementById('bLite').classList.contains('on') }));
  await pg.evaluate(() => localStorage.setItem('dash_anim', 'none'));
  ok(`⚡ the light mode switch: on (${l1.small}) · the motion row says it is paused · off again`, !l0.lite && !l0.on && l1.lite && l1.on && /متوقفة/.test(l1.anim) && !l2.lite && !l2.on, { l0, l1, l2 });
  const s0 = await pg.evaluate(() => soundOn());
  await pg.click('#sSound'); await pg.waitForTimeout(200);
  const s1 = await pg.evaluate(() => ({ snd: soundOn(), on: document.getElementById('sSound').classList.contains('on') }));
  await pg.click('#sSound'); await pg.waitForTimeout(200);
  const u0 = await pg.evaluate(() => uiUnlockOn());
  await pg.click('#bUnl'); await pg.waitForTimeout(450);
  const u1 = await pg.evaluate(() => ({ v: uiUnlockOn(), on: document.getElementById('bUnl').classList.contains('on') }));
  await pg.click('#bUnl'); await pg.waitForTimeout(450);
  ok('🔊 the profit sound and the unlock sound switch on this device (and back)', s0 && !s1.snd && !s1.on && (await pg.evaluate(() => soundOn())) && u0 && !u1.v && !u1.on && (await pg.evaluate(() => uiUnlockOn())), { s0, s1, u0, u1 });
  // ── the server refresh keeps the rows' own classes
  await pg.evaluate(async () => { await tick() }); await pg.waitForTimeout(200);
  const wd = await pg.evaluate(() => ({ c: document.getElementById('bWd').className, w: !!DATA.watchdog }));
  ok(`🤖 the refresh from the server keeps the row (class «${wd.c}»)`, /\bsitem\b/.test(wd.c) && /\bstg\b/.test(wd.c) && /\bon\b/.test(wd.c) === wd.w, wd);
  // ── the windows (rows ending with ‹) and what they call
  const ln = await pg.evaluate(() => [...document.querySelectorAll('#modal .sln')].map(b => { const f = (b.getAttribute('onclick') || '').match(/^\s*([\w$]+)\(/);
    return { t: b.querySelector('.stt b').textContent, f: f && f[1], ok: !!(f && typeof window[f[1]] === 'function'), h: Math.round(b.getBoundingClientRect().height) } }));
  ok(`‹ ${ln.length} rows open a window or a tool — each one's function exists (${ln.map(l => l.f).join(' · ')})`, ln.length >= 12 && ln.every(l => l.ok && l.h >= 48), ln.filter(l => !l.ok || l.h < 48));
  // ── the ids other code and the CI use are all there
  const ids = await pg.evaluate(() => ['bStk', 'bLite', 'sMute', 'sSound', 'bUnl', 'bCLock', 'bWd', 'bApp', 'bWin', 'skinRow', 'fontRow', 'animRow', 'fpsRow', 'gpuNote'].filter(i => !document.getElementById(i)));
  ok('🔗 the old ids are kept (skinRow · fontRow · animRow · fpsRow · gpuNote · every switch)', !ids.length, ids);
  // ── the phone: nothing wider than the screen
  const ph = await pg.evaluate(() => { const b = document.querySelector('#modal .hwb'); return { sw: b.scrollWidth, cw: b.clientWidth,
    wide: [...document.querySelectorAll('#modal .sitem')].filter(r => r.getBoundingClientRect().right > innerWidth + 1 || r.getBoundingClientRect().left < -1).length } });
  ok(`📱 on a phone (412 px): no row wider than the screen (${ph.sw} ≤ ${ph.cw})`, ph.sw <= ph.cw + 1 && !ph.wide, ph);
  // ── MSA in this window (the frames line comes from the app's screen report — its own wording)
  const dia = await pg.evaluate(() => { const c = document.getElementById('modal').cloneNode(true); c.querySelectorAll('.sx[data-k="fps"] .sbody').forEach(n => n.remove());
    return ['شغّال', 'شغّالة', 'مطفي', 'هسه', 'إنت ', 'يرجّع', 'الطايح', 'نزّله', 'ولا زر'].filter(w => c.textContent.includes(w)) });
  ok('🗣️ the settings texts in MSA (no «شغّال · مطفي · هسه …»)', !dia.length, dia);
  // ── lighter to open: the server refresh waits until the motion is over
  const tk = await pg.evaluate(async () => { hideModal(); const t0 = tick; let n = 0; tick = function () { n++; return t0.apply(this, arguments) };
    openSettings(); const a = n; await new Promise(r => setTimeout(r, 700)); const b = n; tick = t0; hideModal(); return { a, b } });
  ok('⚡ opening ⚙️ does not refresh from the server at once — after the opening motion', tk.a === 0 && tk.b >= 1, tk);
  await ctx.close();
  // ── a computer: the list keeps a readable width in the big window
  ({ ctx, pg } = await open(br, 1440, 900, errs));
  await pg.evaluate(() => openSettings()); await pg.waitForTimeout(300);
  const pc = await pg.evaluate(() => { const g = document.querySelector('#modal .sgrid').getBoundingClientRect(), m = document.getElementById('modal').getBoundingClientRect();
    return { g: Math.round(g.width), m: Math.round(m.width), mid: Math.abs((g.left + g.right) / 2 - (m.left + m.right) / 2) < 3 } });
  ok(`🖥️ on a computer: the list ${pc.g} px wide in the middle of the ${pc.m} px window`, pc.g <= 780 && pc.g >= 600 && pc.mid, pc);
  await ctx.close();
  ok('no page errors', !errs.length, errs);
  await br.close();
  console.log(`${res.every(Boolean) ? '✅' : '❌'} ui_settings: ${res.filter(Boolean).length}/${res.length}`);
  process.exit(res.every(Boolean) ? 0 : 1);
})().catch(e => { console.log('crash', e); process.exit(1) });
