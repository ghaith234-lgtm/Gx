# 🎶 patch 53 (dashboard · a continuous tone) — the owner (13-11): «ضيف نغمه مستمرة تنعاد ونقدر انطفيها من الاعدادات اريدها مثل خلفية الps4»
#   ⇒ the examples page ⇒ «خلي الخلفيات والنغمات كلهن».
#   ⚙️ 🔊 «🎶 النغمة المستمرة» (this device): بلا (default) · سكون · فضاء · قطرات · بحر + its own volume.
#   Generated in the page (Web Audio — no sound file, nobody's rights) · never the same twice (the notes are picked each time) ·
#   it starts after the first touch (browsers and the app's WebView allow sound only after one) · it rests when the dashboard is hidden
#   (another app · the screen off) and comes back · it steps aside for a moment when the profit or the unlock sound plays.
#   python3 devtests/step/patches/p53_tone.py Holy_Dashboard.pyw
import os, sys

JS = r'''/* 🎶 v3.36.37 (المالك 13-11): نغمة مستمرة (لهذا الجهاز) — مولّدة بالمتصفح (لا ملف صوت ولا حقوق لأحد) · ما تتكرر بالحرف ·
   تبدي بعد أول لمسة (المتصفح والتطبيق يمنعون الصوت قبلها) · تهدأ لما تطلع من اللوحة أو تنطفي الشاشة · تخفت لحظة صوت الربح وفتح القفل */
const HTONE=[['off','بلا'],['calm','سكون'],['space','فضاء'],['drops','قطرات'],['sea','بحر']];
const HT={ac:null,m:null,verb:null,k:'off',stop:null,armed:0};
function uiTone(){const v=_ls('dash_tone');return HTONE.some(x=>x[0]===v)?v:'off'}
function toneVol(){const v=parseInt(_ls('dash_tone_vol')||'40',10);return isFinite(v)?Math.max(0,Math.min(100,v)):40}
function htVol(){return Math.pow(toneVol()/100,1.6)*.8}
function setTone(v){if(!HTONE.some(x=>x[0]===v))v='off';_ls('dash_tone',v==='off'?null:v);htApply(true);openSettings();
  toast(v==='off'?'🔇 النغمة المستمرة: متوقفة':'🎶 النغمة المستمرة: '+HTONE.find(x=>x[0]===v)[1],true)}
function setToneVol(v){_ls('dash_tone_vol',String(Math.max(0,Math.min(100,+v||0))));if(HT.m)HT.m.gain.setTargetAtTime(htVol(),HT.ac.currentTime,.08)}
function htInit(){if(HT.ac)return;HT.ac=new (window.AudioContext||window.webkitAudioContext)();const ac=HT.ac;
  HT.m=ac.createGain();HT.m.gain.value=htVol();const cp=ac.createDynamicsCompressor();cp.threshold.value=-18;cp.ratio.value=3;HT.m.connect(cp).connect(ac.destination);
  const n=Math.round(ac.sampleRate*4),b=ac.createBuffer(2,n,ac.sampleRate);for(let ch=0;ch<2;ch++){const d=b.getChannelData(ch);for(let i=0;i<n;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/n,2.4)}
  HT.verb=ac.createConvolver();HT.verb.buffer=b;const wet=ac.createGain();wet.gain.value=.7;HT.verb.connect(wet).connect(HT.m)}
const htHz=m=>440*Math.pow(2,(m-69)/12),htR=(a,b)=>a+Math.random()*(b-a);
function htBus(send){const ac=HT.ac,g=ac.createGain();g.gain.value=0;g.gain.setTargetAtTime(1,ac.currentTime,.6);g.connect(HT.m);const s=ac.createGain();s.gain.value=send;g.connect(s).connect(HT.verb);return g}
function htVoice(out,f,t0,dur,o){o=o||{};const ac=HT.ac,os=ac.createOscillator();os.type=o.type||'sine';os.frequency.value=f;os.detune.value=o.det||0;
  const g=ac.createGain(),att=o.att||.02,rel=o.rel||1,pk=o.peak||.2;g.gain.setValueAtTime(0,t0);g.gain.linearRampToValueAtTime(pk,t0+att);
  g.gain.setValueAtTime(pk,t0+Math.max(att,dur-rel));g.gain.exponentialRampToValueAtTime(.0001,t0+dur);let n=os;
  if(o.cut){const f2=ac.createBiquadFilter();f2.type='lowpass';f2.frequency.value=o.cut;f2.Q.value=.4;os.connect(f2);n=f2}
  if(o.pan&&ac.createStereoPanner){const p=ac.createStereoPanner();p.pan.value=o.pan;n.connect(p);n=p}
  n.connect(g).connect(out);os.start(t0);os.stop(t0+dur+.05)}
function htSched(step,every){const ac=HT.ac;let next=ac.currentTime+.1;const run=()=>{while(next<ac.currentTime+1.2)next+=step(next)};run();return setInterval(run,every||250)}
const HTONES={
  calm(){const out=htBus(.55),CH=[[57,64,67,71,76],[53,60,64,69,72],[55,62,67,71,74],[52,59,64,67,71]];let i=0;
    const id=htSched(t=>{const ch=CH[i++%CH.length];for(const m of ch){htVoice(out,htHz(m),t,10.5,{type:'triangle',att:2.6,rel:3.4,peak:.05,det:-6,cut:1400});
      htVoice(out,htHz(m),t,10.5,{type:'sawtooth',att:2.6,rel:3.4,peak:.018,det:7,cut:900})}htVoice(out,htHz(ch[0]-12),t,10.5,{att:2,rel:3,peak:.09});return 8},400);
    return()=>{clearInterval(id);return out}},
  space(){const ac=HT.ac,out=htBus(.85),D=[];
    for(const [m,p] of [[33,.1],[40,.06],[45,.04]]){const o=ac.createOscillator();o.frequency.value=htHz(m);const g=ac.createGain();g.gain.value=0;g.gain.setTargetAtTime(p,ac.currentTime,2);
      const l=ac.createOscillator();l.frequency.value=.07+Math.random()*.05;const lg=ac.createGain();lg.gain.value=p*.35;l.connect(lg).connect(g.gain);o.connect(g).connect(out);o.start();l.start();D.push(o,l)}
    const P=[69,72,74,76,79,81,84,86,88];
    const id=htSched(t=>{const m=P[Math.floor(Math.random()*P.length)],pn=htR(-.7,.7);htVoice(out,htHz(m),t,5,{att:.01,rel:4.6,peak:.06,pan:pn});
      htVoice(out,htHz(m)*2.01,t,3,{att:.01,rel:2.8,peak:.015,pan:pn});return htR(1.6,4.2)});
    return()=>{clearInterval(id);D.forEach(o=>{try{o.stop(ac.currentTime+2.5)}catch(e){}});return out}},
  drops(){const out=htBus(.6),P=[57,60,62,64,67,69,72,74,76,79];
    const pad=htSched(t=>{for(const m of [45,52,57,64])htVoice(out,htHz(m),t,13,{type:'triangle',att:4,rel:4.5,peak:.025,cut:700});return 12},500);
    const id=htSched(t=>{htVoice(out,htHz(P[Math.floor(Math.random()*P.length)]),t,1.6,{type:'triangle',att:.005,rel:1.5,peak:.09,pan:htR(-.6,.6)});return htR(.45,1.3)});
    return()=>{clearInterval(id);clearInterval(pad);return out}},
  sea(){const ac=HT.ac,out=htBus(.35),n=ac.sampleRate*4,b=ac.createBuffer(1,n,ac.sampleRate),d=b.getChannelData(0);let l=0;
    for(let i=0;i<n;i++){l=(l+.02*(Math.random()*2-1))/1.02;d[i]=l*3.5}
    const src=ac.createBufferSource();src.buffer=b;src.loop=true;const f=ac.createBiquadFilter();f.type='lowpass';f.frequency.value=700;
    const g=ac.createGain();g.gain.value=.12;const lf=ac.createOscillator();lf.frequency.value=.11;const lg=ac.createGain();lg.gain.value=.1;lf.connect(lg).connect(g.gain);
    const lf2=ac.createGain();lf2.gain.value=350;lf.connect(lf2).connect(f.frequency);src.connect(f).connect(g).connect(out);src.start();lf.start();
    const pad=htSched(t=>{for(const m of [50,57,62,66])htVoice(out,htHz(m),t,15,{att:5,rel:5,peak:.03});return 14},500);
    return()=>{clearInterval(pad);try{src.stop(ac.currentTime+2.5);lf.stop(ac.currentTime+2.5)}catch(e){}return out}},
};
function htStop(){if(!HT.stop){HT.k='off';return}const out=HT.stop();HT.stop=null;HT.k='off';
  try{const t=HT.ac.currentTime;out.gain.cancelScheduledValues(t);out.gain.setTargetAtTime(0,t,.5);setTimeout(()=>{try{out.disconnect()}catch(e){}},4000)}catch(e){}}
function htArm(){if(HT.armed)return;HT.armed=1;const go=()=>{removeEventListener('pointerdown',go,true);removeEventListener('keydown',go,true);HT.armed=0;htApply(true)};
  addEventListener('pointerdown',go,true);addEventListener('keydown',go,true)}
function htApply(user){const k=uiTone();if(k==='off'){htStop();return}
  try{if(!HT.ac){if(!user){htArm();return}htInit()}
    if(HT.k!==k){htStop();HT.k=k;HT.stop=HTONES[k]()}
    if(HT.ac.state==='suspended'&&!document.hidden)HT.ac.resume()}catch(e){}}
function htDuck(){try{if(!HT.m||HT.k==='off')return;const t=HT.ac.currentTime,g=HT.m.gain;g.cancelScheduledValues(t);g.setTargetAtTime(htVol()*.2,t,.04);g.setTargetAtTime(htVol(),t+1.4,.5)}catch(e){}}
document.addEventListener('visibilitychange',()=>{if(!HT.ac)return;try{if(document.hidden)HT.ac.suspend();else if(HT.k!=='off')HT.ac.resume()}catch(e){}});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>htApply(false));else setTimeout(()=>htApply(false),0);
'''

R = [
    ('''function uiTheme(){const t=_ls('dash_theme');return THEMES.some(x=>x[0]===t)?t:'holy'}''',
     JS + '''function uiTheme(){const t=_ls('dash_theme');return THEMES.some(x=>x[0]===t)?t:'holy'}'''),
    # the profit and the unlock sounds: the tone steps aside for a moment
    ('''function chime(){try{const c=new(window.AudioContext||window.webkitAudioContext)();''',
     '''function chime(){try{htDuck()}catch(e){}try{const c=new(window.AudioContext||window.webkitAudioContext)();'''),
    ('''function uiChime(){try{const c=new(window.AudioContext||window.webkitAudioContext)(),''',
     '''function uiChime(){try{htDuck()}catch(e){}try{const c=new(window.AudioContext||window.webkitAudioContext)(),'''),
    # ⚙️ 🔊: the row
    ('''     +T('🔊','صوت فتح القفل','uiUnlockToggle()','bUnl',uiUnlockOn(),'يعمل — نغمة عند فتح القفل','متوقف'))}''',
     '''     +T('🔊','صوت فتح القفل','uiUnlockToggle()','bUnl',uiUnlockOn(),'يعمل — نغمة عند فتح القفل','متوقف')
     +X('tone','🎶','النغمة المستمرة',(HTONE.find(x=>x[0]===uiTone())||HTONE[0])[1],
        `<div class="snote">نغمة هادئة تتكرر بلا نهاية — مولّدة هنا، لا تتكرر بالحرف · تبدأ بعد أول لمسة · تهدأ حين تخرج من اللوحة أو تنطفئ الشاشة.</div>
        <div class="pollrow" id="toneRow">${HTONE.map(x=>`<button class="${uiTone()===x[0]?'on':''}" data-tone="${x[0]}" onclick="setTone('${x[0]}')">${x[1]}</button>`).join('')}</div>
        <div class="tvol"><label for="toneVol">🔉 مستوى صوتها</label><input id="toneVol" type="range" min="0" max="100" step="1" value="${toneVol()}" oninput="setToneVol(this.value)"></div>`))}'''),
    ('''.bgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(98px,1fr));gap:8px}''',
     '''.bgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(98px,1fr));gap:8px}
.tvol{display:flex;align-items:center;gap:10px;margin-top:10px;font-size:12px;color:var(--mut)}.tvol input[type=range]{flex:1;max-width:280px;height:26px;padding:0;border:0;background:none;accent-color:rgb(var(--vio-rgb))}'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
