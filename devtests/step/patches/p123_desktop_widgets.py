# 🖥️ patch 123 (dashboard v3.36.72 · the desktop widgets). The owner (21-11): «نقدر انسوي ويدجت للحاسوب … ويدجت نفسه الي بالموبايل نفسه الي
#   بالحاسوب بالشكل».
#   · GET /widget?k=bots|px — a small page that draws the phone's two widgets (the app 2.3's WidgetArt.render · renderPx, line by line, in a
#     canvas: the six numbers + every bot's line · the coins' tiles with their badge, price, change and the last 24 hours) · the bigger the
#     window, the more it holds · refreshed every minute · a click opens the dashboard · it carries NO data (public like the login page):
#     inside the Windows program 2.1 it reads /api/app/widget with the program's device key (from the address's #part — never sent in a
#     request line, never logged); in a browser on any computer it reads GET /api/widget (the same answer, behind the sign-in and the PIN)
#   · 💻 panel «🖥️ ويدجت سطح المكتب»: in the program 2.1 — «🟣 ويدجت Holy» · «🪙 ويدجت الأسعار» · «📌 فوق كل النوافذ» (the program
#     shows its frameless widget windows · they stay where you put them · come back with Windows) · an older program ⇒ «نزّل 2.1» · in a
#     browser — «افتح ويدجت …» as a small window (any computer)
#   · display only: no keys, no balances, no orders
#   python3 devtests/step/patches/p123_desktop_widgets.py Holy_Dashboard.pyw
import os, sys

WIDGET_PAGE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><title>Holy</title>
<style>html,body{margin:0;height:100%;overflow:hidden;background:transparent;user-select:none;-webkit-user-select:none}
canvas{display:block;width:100vw;height:100vh;cursor:pointer;touch-action:none}</style></head>
<body><canvas id="c" role="img" aria-label="Holy"></canvas>
<script>
/* 🖥️ v3.36.72: ويدجت سطح المكتب — نفس رسم ويدجت الهاتف (WidgetArt.render · renderPx في التطبيق 2.3) سطراً بسطر · يتحدّث كل دقيقة ·
   الضغط يفتح اللوحة · السحب يحرّكه (داخل برنامج ويندوز) · عرض فقط: لا مفاتيح ولا أرصدة ولا أوامر */
(function(){
const Q=new URLSearchParams(location.search),K=Q.get('k')==='px'?'px':'bots';
let TOK='';const hm=(location.hash||'').match(/[#&]d=([A-Za-z0-9_\-]{8,200})/);
if(hm){TOK=hm[1];try{history.replaceState(null,'',location.pathname+location.search)}catch(e){}}
const HOST=!!(window.chrome&&window.chrome.webview);
const C=document.getElementById('c'),X=C.getContext('2d');
let J=null,T=0,BUSY=false,SAID=0;
const BG_TOP='#1B1233',BG_BOT='#0F0B1D',VIO='#A78BFA',VIO_T='#C4B5FD',EDGE='rgba(167,139,250,.333)',SEP='rgba(167,139,250,.22)',
  MUT='#A39BC4',TX='#F3F0FF',UP='#34D399',DN='#F87171',WARN='#F4C95D';
const UPr=[52,211,153],DNr=[248,113,113];
const col=c=>c==='u'?UP:c==='d'?DN:TX;
function kind(t){t=t||'';if(t==='grid_range')return '#60A5FA';if(t==='grid_plus')return '#F472B6';
  if(t==='grid_step'||t==='rec_buy'||t==='rec_sell')return '#22D3EE';if(t==='dca'||t==='dca_buy')return '#F4C95D';if(t==='rec_va')return '#34D399';return VIO}
const SANS='"Segoe UI",Roboto,"Noto Sans Arabic",Tahoma,sans-serif',MONO='Consolas,"Roboto Mono",monospace';
function font(sz,bold,mono){return (bold?'bold ':'')+sz.toFixed(2)+'px '+(mono?MONO:SANS)}
const AR=/[؀-ۿ]/;
function txt(s,x,y,max,sz,color,bold,mono,align){s=s==null?'':String(s);           // يصغّر الخط حتى يتسع (لا أقل من 6)
  X.direction=AR.test(s)?'rtl':'ltr';X.textAlign=align||'right';X.fillStyle=color;X.textBaseline='alphabetic';
  let z=sz;X.font=font(z,bold,mono);while(z>6&&X.measureText(s).width>max){z-=0.5;X.font=font(z,bold,mono)}
  X.fillText(s,x,y);return X.measureText(s).width}
function fitW(s,max,sz,bold,mono){let z=sz;X.font=font(z,bold,mono);while(z>6&&X.measureText(s).width>max){z-=0.5;X.font=font(z,bold,mono)}return [X.measureText(s).width,z]}
function rr(l,t,r,b,rad){const w=r-l,h=b-t;rad=Math.min(rad,w/2,h/2);X.beginPath();X.moveTo(l+rad,t);X.arcTo(r,t,r,b,rad);X.arcTo(r,b,l,b,rad);X.arcTo(l,b,l,t,rad);X.arcTo(l,t,r,t,rad);X.closePath()}
function card(W,H,d,padV){const g=X.createLinearGradient(W,0,0,H);g.addColorStop(0,BG_TOP);g.addColorStop(1,BG_BOT);
  rr(0,0,W,H,20*d);X.fillStyle=g;X.fill();rr(.5,.5,W-.5,H-.5,20*d);X.lineWidth=Math.max(1,d);X.strokeStyle=EDGE;X.stroke();
  const b=X.createLinearGradient(0,padV,0,H-padV);b.addColorStop(0,VIO);b.addColorStop(1,'rgba(167,139,250,.2)');rr(W-4*d,padV,W-1*d,H-padV,2*d);X.fillStyle=b;X.fill()}
function hhmm(t){const z=new Date(t);return String(z.getHours()).padStart(2,'0')+':'+String(z.getMinutes()).padStart(2,'0')}
function dot(x,y,r,c){X.beginPath();X.arc(x,y,r,0,Math.PI*2);X.fillStyle=c;X.fill()}

function render(j,t,wDp,hDp,d){                                              // = WidgetArt.render (التطبيق 2.3)
  const W=C.width,H=C.height;X.clearRect(0,0,W,H);
  const v=d*Math.max(0.62,Math.min(1,hDp/122)),pad=14*d,padV=14*v;card(W,H,d,padV);
  const yh=padV+14*v;txt('Holy',W-pad,yh,W,16*v,VIO_T,true,false,'right');
  const stale=t>0&&Date.now()-t>900000,hm=t>0?hhmm(t):'';
  if(!j){txt('افتح Holy وادخل إلى لوحتك مرة واحدة',W-pad,yh+30*v,W-2*pad,12.5*v,TX,false,false,'right');
    txt('ليرتبط الجهاز وتظهر بوتاتك وأرباحك هنا',W-pad,yh+50*v,W-2*pad,11*v,MUT,false,false,'right');
    if(H>=yh+50*v+30*v)txt('اضغط للفتح',W-pad,H-8*v,W-2*pad,11*v,MUT,false,false,'right');return}
  const run=+j.run||0,n=+j.n||0,st=(stale?'⚠️ ':'')+run+'/'+n+' يعمل'+(hm?' · '+hm:'');
  const sw=txt(st,pad,yh,W*0.55,11.5*v,stale?WARN:MUT,false,false,'left');
  dot(pad+sw+7*d,yh-4*v,3.2*v,stale?WARN:(run>0?UP:DN));
  const k=j.kb||j.k||[],nk=Math.min(k.length,6),y0=yh+12*v,colW=(W-2*pad)/3,rowH=37*v,rows=Math.floor((nk+2)/3);
  X.strokeStyle=SEP;X.lineWidth=Math.max(1,d);
  for(let ci=1;ci<3&&rows>0;ci++){const x=W-pad-ci*colW;X.beginPath();X.moveTo(x,y0+2*v);X.lineTo(x,y0+rows*rowH-6*v);X.stroke()}
  for(let i=0;i<nk;i++){const e=k[i];if(!e)continue;const r=Math.floor(i/3),ci=i%3,xr=W-pad-ci*colW-(ci===0?0:9*d),wmax=colW-(ci===0?9*d:14*d),yl=y0+r*rowH+11*v;
    txt(e[0],xr,yl,wmax,10.5*v,MUT,false,false,'right');txt(e[1],xr,yl+18*v,wmax,15*v,col(e[2]),true,true,'right')}
  const ydiv=y0+rows*rowH,b=j.bots||[],nb=b.length,rh=21*v,foot=18*v,room=H-ydiv-4*v-foot,fit=Math.floor(room/rh),show=Math.max(0,Math.min(nb,fit)),footer=H-ydiv>=foot+2*v;
  if(rows>0&&footer){X.beginPath();X.moveTo(pad,ydiv);X.lineTo(W-pad,ydiv);X.strokeStyle=SEP;X.stroke()}
  for(let i=0;i<show;i++){const o=b[i];if(!o)continue;const yc=ydiv+4*v+i*rh+rh/2;
    rr(W-pad-3*d,yc-7*v,W-pad,yc+7*v,1.5*d);X.fillStyle=kind(o.t);X.fill();
    const nw=txt((o.e||'')+' '+(o.s||''),W-pad-9*d,yc+4.5*v,colW*1.05-20*d,12.5*v,TX,false,false,'right');
    dot(W-pad-9*d-nw-7*d,yc,3*v,(+o.on===1)?UP:DN);
    txt(o.a,pad,yc+4.5*v,colW*1.1,12*v,col(o.c),true,true,'left')}
  if(nb===0&&fit>0)txt('لا توجد بوتات بعد',W-pad,ydiv+4*v+rh/2+4.5*v,W-2*pad,12*v,MUT,false,false,'right');
  if(footer){const rest=nb-show,more=show===0&&nb>0?(nb===1?'بوت واحد':nb===2?'بوتان':nb+' بوتات')+' — اضغط للفتح':rest<=0?'اضغط للفتح'
      :(rest===1?'وبوت آخر':rest===2?'وبوتان آخران':'و '+rest+' بوتات أخرى')+' — اضغط للفتح';
    txt(more,W-pad,H-8*v,W-2*pad,11*v,MUT,false,false,'right')}}

const COINC={BTC:'#F7931A',ETH:'#627EEA',SOL:'#9945FF',XRP:'#23292F',DOGE:'#C2A633',LINK:'#2A5ADA',BNB:'#F3BA2F',ADA:'#0033AD',TRX:'#FF060A',AVAX:'#E84142',
  SUI:'#4DA2FF',LTC:'#345D9D',DOT:'#E6007A',TON:'#0098EA',SHIB:'#E42D04',PEPE:'#4C8F3C',BCH:'#0AC18E',XLM:'#3E5BA9'};
function jhash(s){let h=0;for(let i=0;i<s.length;i++)h=(Math.imul(31,h)+s.charCodeAt(i))|0;return h}   // = String.hashCode في جافا
function coinColor(s){s=s||'';if(COINC[s])return COINC[s];const pal=['#8B5CF6','#0EA5E9','#14B8A6','#F59E0B','#EC4899','#22C55E','#6366F1','#EF4444'];return pal[(jhash(s)&0x7fffffff)%pal.length]}
function poly(x0,y0,k,xy){X.moveTo(x0+xy[0]*k,y0+xy[1]*k);for(let i=2;i+1<xy.length;i+=2)X.lineTo(x0+xy[i]*k,y0+xy[i+1]*k);X.closePath()}
function badge(s,cx,cy,r){                                                     // = WidgetArt.badge — شكل العملة بخطوط بسيطة (بلا صور شعارات)
  dot(cx,cy,r,coinColor(s));
  if(s==='XRP'){X.beginPath();X.arc(cx,cy,r-r/18,0,Math.PI*2);X.lineWidth=Math.max(1,r/9);X.strokeStyle='#5B6470';X.stroke()}
  const k=r/9,x0=cx-r,y0=cy-r,m=s||'';X.fillStyle='#FFFFFF';X.strokeStyle='#FFFFFF';X.lineCap='round';X.lineJoin='round';X.lineWidth=1.6*k;
  X.beginPath();
  if(m==='ETH'){poly(x0,y0,k,[9,2.6,13.4,9.4,9,12,4.6,9.4]);X.fill();X.beginPath();poly(x0,y0,k,[9,12.9,13.4,10.3,9,15.6,4.6,10.3]);X.globalAlpha=190/255;X.fill();X.globalAlpha=1}
  else if(m==='SOL'){for(let i=0;i<3;i++){const y=5.6+i*2.7;if(i===1)poly(x0,y0,k,[4.2,y,12.2,y,13.6,y+1.4,5.6,y+1.4]);else poly(x0,y0,k,[5.6,y,13.6,y,12.2,y+1.4,4.2,y+1.4])}X.fill()}
  else if(m==='XRP'){X.moveTo(x0+4.6*k,y0+5*k);X.lineTo(x0+7.4*k,y0+7.8*k);X.quadraticCurveTo(x0+9*k,y0+9.3*k,x0+10.6*k,y0+7.8*k);X.lineTo(x0+13.4*k,y0+5*k);
    X.moveTo(x0+4.6*k,y0+13*k);X.lineTo(x0+7.4*k,y0+10.2*k);X.quadraticCurveTo(x0+9*k,y0+8.7*k,x0+10.6*k,y0+10.2*k);X.lineTo(x0+13.4*k,y0+13*k);X.lineWidth=1.5*k;X.stroke()}
  else if(m==='LINK'){poly(x0,y0,k,[9,3.8,13.5,6.4,13.5,11.6,9,14.2,4.5,11.6,4.5,6.4]);X.lineWidth=1.7*k;X.stroke()}
  else if(m==='BNB'){[[9,5.6,2],[5.6,9,2],[12.4,9,2],[9,12.4,2],[9,9,1.1]].forEach(q=>poly(x0,y0,k,[q[0],q[1]-q[2],q[0]+q[2],q[1],q[0],q[1]+q[2],q[0]-q[2],q[1]]));X.fill()}
  else if(m==='ADA'){[[9,4],[9,14],[4.7,6.5],[13.3,6.5],[4.7,11.5],[13.3,11.5]].forEach(q=>dot(x0+q[0]*k,y0+q[1]*k,1.05*k,'#FFFFFF'));dot(cx,cy,2*k,'#FFFFFF')}
  else if(m==='AVAX'){poly(x0,y0,k,[9,4,13.8,13,10.9,13,9,9.4,7.1,13,4.2,13]);X.fill()}
  else if(m==='SUI'){X.moveTo(x0+9*k,y0+3.6*k);X.bezierCurveTo(x0+11.6*k,y0+7*k,x0+12.6*k,y0+8.6*k,x0+12.6*k,y0+10.6*k);
    X.bezierCurveTo(x0+12.6*k,y0+15.4*k,x0+5.4*k,y0+15.4*k,x0+5.4*k,y0+10.6*k);X.bezierCurveTo(x0+5.4*k,y0+8.6*k,x0+6.4*k,y0+7*k,x0+9*k,y0+3.6*k);X.closePath();X.fill()}
  else if(m==='DOT'){dot(cx,cy,2.2*k,'#FFFFFF');X.beginPath();X.ellipse(x0+9*k,y0+4.6*k,2.6*k,1.3*k,0,0,Math.PI*2);X.fill();X.beginPath();X.ellipse(x0+9*k,y0+13.4*k,2.6*k,1.3*k,0,0,Math.PI*2);X.fill()}
  else if(m==='TRX'){poly(x0,y0,k,[4,5,14.2,6.6,8.6,14]);X.moveTo(x0+4*k,y0+5*k);X.lineTo(x0+11.2*k,y0+8.7*k);X.lineTo(x0+14.2*k,y0+6.6*k);X.lineWidth=1.2*k;X.stroke()}
  else{const g=m==='BTC'?'B':m==='DOGE'?'Ð':m==='LTC'?'Ł':(m?m[0]:'?');X.font=font(r*(m==='BTC'?1.2:1.05),true,false);X.textAlign='center';X.direction='ltr';X.fillText(g,cx,cy+r*0.42);
    if(m==='BTC'){X.lineWidth=1.2*k;X.lineCap='butt';[-1.1,1.1].forEach(dx=>{X.beginPath();X.moveTo(cx+dx*k,cy-r*0.62);X.lineTo(cx+dx*k,cy-r*0.42);X.moveTo(cx+dx*k,cy+r*0.48);X.lineTo(cx+dx*k,cy+r*0.66);X.stroke()})}}
  X.lineCap='butt'}
function spark(sp,up,l,t,r,b,d){const n=sp?sp.length:0;if(n<2||r-l<4||b-t<3)return;const c=up?UPr:DNr;  // = WidgetArt.spark: خط آخر 24 ساعة بتظليل تحته
  const P=[];for(let i=0;i<n;i++){const x=l+(r-l)*i/(n-1),y=b-(b-t)*Math.max(0,Math.min(1000,+sp[i]||0))/1000;P.push([x,y])}
  X.beginPath();P.forEach((p,i)=>i?X.lineTo(p[0],p[1]):X.moveTo(p[0],p[1]));X.lineTo(r,b);X.lineTo(l,b);X.closePath();
  const g=X.createLinearGradient(0,t,0,b);g.addColorStop(0,`rgba(${c},.32)`);g.addColorStop(1,`rgba(${c},0)`);X.fillStyle=g;X.fill();
  X.beginPath();P.forEach((p,i)=>i?X.lineTo(p[0],p[1]):X.moveTo(p[0],p[1]));X.lineWidth=Math.max(1,1.5*d);X.lineJoin='round';X.strokeStyle=`rgb(${c})`;X.stroke()}
function renderPx(j,t,wDp,hDp,d){                                            // = WidgetArt.renderPx (التطبيق 2.3)
  const W=C.width,H=C.height;X.clearRect(0,0,W,H);
  const v=d*Math.max(0.7,Math.min(1,hDp/120)),pad=14*d,padV=12*v;card(W,H,d,padV);
  const yh=padV+13*v;X.font=font(15*v,true,false);const hw=X.measureText('Holy').width;
  txt('Holy',W-pad,yh,W,15*v,VIO_T,true,false,'right');txt('الأسعار',W-pad-hw-6*d,yh,W,11*v,MUT,false,false,'right');
  const stale=t>0&&Date.now()-t>900000,hm=t>0?hhmm(t):'';
  if(hm)txt((stale?'⚠️ ':'')+hm,pad,yh,W*0.4,11*v,stale?WARN:MUT,false,true,'left');
  const px=j?j.px:null;
  if(!j||!px||!px.length){const m1=!j?'افتح Holy وادخل إلى لوحتك مرة واحدة':!px?'حدّث لوحتك لتظهر الأسعار هنا':'أضف عملات إلى شريط الأسعار في اللوحة';
    txt(m1,W-pad,yh+28*v,W-2*pad,12.5*v,TX,false,false,'right');if(H>=yh+28*v+30*v)txt('اضغط للفتح',W-pad,H-8*v,W-2*pad,11*v,MUT,false,false,'right');return}
  const cols=Math.max(2,Math.floor((wDp-24)/100));let rows=Math.max(1,Math.floor((hDp-58)/63));const fit=Math.min(px.length,cols*rows);
  if(fit<cols*rows)rows=Math.max(1,Math.floor((fit+cols-1)/cols));
  const gx=12*d,gap=7*d,top=yh+9*v,foot=17*v,bottom=H-foot-2*v,tw=(W-2*gx-(cols-1)*gap)/cols,th=Math.min(96*v,(bottom-top-(rows-1)*gap)/rows);
  for(let i=0;i<fit;i++){const o=px[i];if(!o)continue;const r=Math.floor(i/cols),ci=i%cols,R=W-gx-ci*(tw+gap),L=R-tw,Tt=top+r*(th+gap),B=Tt+th;
    rr(L,Tt,R,B,12*d);X.fillStyle='rgba(167,139,250,.05)';X.fill();X.lineWidth=Math.max(1,d);X.strokeStyle=SEP;X.stroke();
    const s=o.s||'',ch=+o.ch||0,up=ch>=0,br=8*v,by=Tt+6*v+br;badge(s,R-8*d-br,by,br);
    const nw=txt(s,R-8*d-2*br-5*d,by+4.3*v,tw*0.42,12.5*v,TX,true,false,'right');
    const cs=(up?'▲':'▼')+Math.abs(ch).toFixed(2)+'%',room=tw-16*d-2*br-5*d-nw-6*d,fz=fitW(cs,Math.max(10*d,room-8*d),9.5*v,true,true);
    rr(L+8*d,by-6.4*v,L+8*d+fz[0]+8*d,by+6.4*v,6*d);X.fillStyle=up?'rgba(52,211,153,.133)':'rgba(248,113,113,.133)';X.fill();
    X.font=font(fz[1],true,true);X.textAlign='left';X.direction='ltr';X.fillStyle=up?UP:DN;X.fillText(cs,L+8*d+4*d,by+3.6*v);
    const yp=by+br+14*v;txt(o.p,R-8*d,yp,tw-16*d,12.5*v,TX,true,true,'right');spark(o.sp,up,L+6*d,yp+4*v,R-6*d,B-4*v,d)}
  const rest=px.length-fit,more=rest<=0?'اضغط للفتح':(rest===1?'وعملة أخرى':rest===2?'وعملتان أخريان':'و '+rest+' عملات أخرى')+' — اضغط للفتح';
  txt(more,W-pad,H-7*v,W-2*pad,10.5*v,MUT,false,false,'right')}
function speak(j){if(!j)return 'Holy — افتح Holy وادخل إلى لوحتك مرة واحدة';
  if(K==='px'){const p=j.px||[];return 'Holy الأسعار'+(p.length?p.slice(0,20).map(o=>` · ${o.s} ${o.p} ${(+o.ch||0)>=0?'ارتفع':'انخفض'} ${Math.abs(+o.ch||0).toFixed(2)}%`).join(''):' — لا توجد عملات بعد')}
  let s='Holy — '+(+j.run||0)+' من '+(+j.n||0)+' بوتات تعمل';(j.kb||j.k||[]).slice(0,6).forEach(e=>{s+=' · '+e[0]+' '+e[1]});(j.bots||[]).slice(0,6).forEach(o=>{s+=' · '+o.s+' '+o.a});return s}
function draw(){const d=window.devicePixelRatio||1,w=Math.max(1,innerWidth),h=Math.max(1,innerHeight);
  const W=Math.max(1,Math.min(Math.round(w*d),2800)),H=Math.max(1,Math.min(Math.round(h*d),2200));if(C.width!==W)C.width=W;if(C.height!==H)C.height=H;
  if(K==='px')renderPx(J,T,w,h,d);else render(J,T,w,h,d);C.setAttribute('aria-label',speak(J))}
async function load(){if(BUSY)return;BUSY=true;
  let pin='';try{pin=localStorage.getItem('dash_pin')||''}catch(e){}           // (جلسة المتصفح: رمز القفل نفسه الذي تحفظه اللوحة)
  try{const r=await fetch(TOK?'/api/app/widget':'/api/widget',{cache:'no-store',credentials:'same-origin',headers:TOK?{'X-Holy-Device':TOK}:(pin?{'X-Dash-Pin':pin}:{})});
    if(r.status===401||r.status===403){J=null;T=0}else if(r.ok){const j=await r.json();if(j&&j.ok!==false){J=j;T=Date.now()}}}catch(e){}
  BUSY=false;draw();
  if(HOST&&!SAID){SAID=1;try{chrome.webview.postMessage('hw:drawn '+innerWidth+'x'+innerHeight+(J?' data':' nodata'))}catch(e){}}}
window.HOLYW={draw,load,set:(j,t)=>{J=j;T=t||Date.now();draw()}};
addEventListener('resize',draw);
// الضغط يفتح اللوحة · السحب يحرّك الويدجت (برنامج ويندوز يحرّك نافذته) · الزر الأيمن: قائمة البرنامج
let P0=null;
C.addEventListener('pointerdown',e=>{if(e.button!==0)return;P0={x:e.screenX,y:e.screenY,drag:false}});
C.addEventListener('pointermove',e=>{if(!P0||P0.drag||!(e.buttons&1))return;if(Math.abs(e.screenX-P0.x)+Math.abs(e.screenY-P0.y)>4){P0.drag=true;if(HOST)chrome.webview.postMessage('hw:drag')}});
C.addEventListener('pointerup',e=>{const p=P0;P0=null;if(!p||p.drag||e.button!==0)return;
  if(HOST)chrome.webview.postMessage('hw:open');else{const w=window.open('/','holy_main');try{w&&w.focus()}catch(x){}}});
C.addEventListener('contextmenu',e=>{if(HOST){e.preventDefault();chrome.webview.postMessage('hw:menu')}});
draw();load();setInterval(load,60000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)load()});
})();
</script></body></html>
"""

PY = """

WIDGET_PAGE = r\'\'\'""" + WIDGET_PAGE + """\'\'\'      # 🖥️ v3.36.72: ويدجت سطح المكتب (صفحة ثابتة بلا بيانات)
"""

R = [
    ("""

def app_feed_wait(since, wait):""", PY + """

def app_feed_wait(since, wait):"""),
    # the routes: the page (no data · before the sign-in guard) · the data for a signed-in browser
    ("""        if u.path in ("/favicon.ico", "/favicon.svg"):           # 🎨 v3.26.0: أيقونة الشعار (حتى بصفحة الدخول)""",
     """        if u.path == "/widget":                                  # 🖥️ v3.36.72: ويدجت سطح المكتب — رسم فقط (البيانات بمفتاح الجهاز أو الجلسة)
            body = WIDGET_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except Exception:
                pass
            return
        if u.path in ("/favicon.ico", "/favicon.svg"):           # 🎨 v3.26.0: أيقونة الشعار (حتى بصفحة الدخول)"""),
    ("""        if u.path == "/api/signals":                      # 🎯 v3.36.66: الإشارات (من الملفات · لا تنتظر الحساب أبداً)""",
     """        if u.path == "/api/widget":                       # 🖥️ v3.36.72: ويدجت سطح المكتب في متصفح (نفس جواب ويدجت الهاتف · بعد الدخول)
            return self._json(_safe(app_widget_view, default={"ok": False, "run": 0, "n": 0, "k": [], "bots": []}))
        if u.path == "/api/signals":                      # 🎯 v3.36.66: الإشارات (من الملفات · لا تنتظر الحساب أبداً)"""),
    # the page: the 💻 panel's section · the program's state messages · the ⚙️ row
    ("""    <div class="ap-h">💻 الحواسيب المربوطة بالإشعارات (${wdevs.length})""",
     """    ${winWgSec()}
    <div class="ap-h">💻 الحواسيب المربوطة بالإشعارات (${wdevs.length})"""),
    ("""async function winUnpair(id){""",
     """let HWST={};                                                                    // 🖥️ v3.36.72: ويدجت سطح المكتب
function winWgSec(){const H=window.HOLYWIN||{};
  if(WINF&&H.wg)return `<div class="ap-h">🖥️ ويدجت سطح المكتب</div><div class="ap-note">نفس ويدجت الهاتف بشكله: «Holy» (الأرقام الستة وسطر كل بوت) و«Holy · الأسعار» (عملات الشريط بأسعارها وخط آخر 24 ساعة) — نافذتان صغيرتان بلا إطار على سطح المكتب.</div>
    <div class="sg-flt" id="wn_wg">${[['bots','🟣 ويدجت Holy'],['px','🪙 ويدجت الأسعار'],['top','📌 فوق كل النوافذ']].map(([k,t])=>`<button data-k="${k}" class="${HWST[k]?'on':''}" onclick="winHw('${k}')">${t}</button>`).join('')}</div>
    <ol class="ap-steps"><li>اسحبه إلى أي مكان ويبقى فيه · اسحب حافته لتكبيره — كلما كبر اتسع لأكثر.</li><li>يتحدّث كل دقيقة · الضغط عليه يفتح اللوحة · الزر الأيمن: قائمته (حدّث · فوق النوافذ · أخفه).</li><li>يعود وحده مع تشغيل ويندوز · وتجده أيضاً في قائمة أيقونة البرنامج قرب الساعة.</li></ol>`;
  if(WINF)return `<div class="ap-h">🖥️ ويدجت سطح المكتب</div><div class="ap-note">نزّل البرنامج بنسخته الأحدث (الزر أعلاه) وافتحه مرة — تظهر هنا أزرار ويدجت Holy وويدجت الأسعار على سطح المكتب.</div>`;
  return `<div class="ap-h">🖥️ ويدجت لأي حاسوب</div><div class="ap-note">نفس ويدجت الهاتف في نافذة صغيرة من هذا المتصفح — يتحدّث كل دقيقة والضغط عليه يفتح اللوحة (يحتاج أن تكون داخلاً إلى اللوحة في هذا المتصفح). في برنامج ويندوز يكون بلا إطار ويبقى في مكانه.</div>
    <div class="sg-flt"><button onclick="wgPop('bots')">🟣 افتح ويدجت Holy</button><button onclick="wgPop('px')">🪙 افتح ويدجت الأسعار</button></div>`}
function winHw(k){try{chrome.webview.postMessage('hw:'+k)}catch(e){}}
function wgSync(){document.querySelectorAll('#wn_wg button[data-k]').forEach(b=>b.classList.toggle('on',!!HWST[b.dataset.k]))}
function wgPop(k){const w=window.open('/widget?k='+k,'holy_w'+k,'popup=yes,width='+(k==='px'?340:330)+',height='+(k==='px'?236:200));
  if(!w)toast('اسمح للنوافذ المنبثقة لهذه اللوحة ثم أعد المحاولة',false)}
async function winUnpair(id){"""),
    ("""  winCmd('state');setTimeout(winHello,1500);addEventListener('resize',()=>{clearTimeout(ht);ht=setTimeout(winHello,600)})}""",
     """  chrome.webview.addEventListener('message',e=>{const d=e.data||{};if(d.t==='hw'){HWST=d;wgSync()}});     // 🖥️ v3.36.72: الويدجت (البرنامج 2.1)
  if((window.HOLYWIN||{}).wg)winHw('state');
  winCmd('state');setTimeout(winHello,1500);addEventListener('resize',()=>{clearTimeout(ht);ht=setTimeout(winHello,600)})}"""),
    ("""     +L('💻','برنامج ويندوز','openWinPanel()',IN_WIN?'أنت داخل من البرنامج الآن':'نافذة خاصة على الحاسوب','bWin'))}""",
     """     +L('💻','برنامج ويندوز','openWinPanel()',(IN_WIN?'أنت داخل من البرنامج الآن':'نافذة خاصة على الحاسوب')+' · 🖥️ ويدجت سطح المكتب','bWin'))}"""),
    ("""APP_VERSION = "3.36.71\"""", """APP_VERSION = "3.36.72\""""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 🖥️ the desktop widgets (/widget · /api/widget · the 💻 panel) · compiles · {p}")
