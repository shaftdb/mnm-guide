// Headless Chrome checks for UX pass 1: skip link + focus ring (normal and Halloween themes), compact mini bar on phones,
// 44px touch targets at 480, no horizontal overflow at 480/1024/2560/3440, ultrawide width + multi-column quick info,
// sticky side rails below the real header, prefers-reduced-motion.
// Usage: node --experimental-websocket tools/test_ux.js [shotdir]
const {spawn}=require('child_process'),http=require('http'),fs=require('fs'),path=require('path');
const DOCS=path.join(__dirname,'..','docs'),SHOT=process.argv[2]||null,PORT=8000+Math.floor(Math.random()*900);
const srv=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:DOCS,stdio:'ignore'});
const chrome=spawn('google-chrome',['--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--remote-debugging-port='+(PORT+1000),'--user-data-dir=/tmp/uxt-chrome-'+PORT,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0,passes=0;function ok(c,m){if(c){passes++;console.log('PASS',m)}else{fails++;console.log('FAIL',m)}}
function getJSON(u){return new Promise((res,rej)=>http.get(u,r=>{let d='';r.on('data',x=>d+=x);r.on('end',()=>{try{res(JSON.parse(d))}catch(e){rej(e)}})}).on('error',rej))}
(async()=>{
 let tabs;for(let i=0;i<50;i++){try{tabs=await getJSON('http://127.0.0.1:'+(PORT+1000)+'/json');break}catch(e){await sleep(200)}}
 const ws=new WebSocket(tabs.find(x=>x.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pend={},errs=[];ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend[d.id]){pend[d.id](d);delete pend[d.id]}else if(d.method==='Runtime.exceptionThrown')errs.push(JSON.stringify(d.params.exceptionDetails).slice(0,300))};
 const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}))});
 const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true});if(r.result.exceptionDetails)throw new Error(e+' '+JSON.stringify(r.result.exceptionDetails).slice(0,300));return r.result.result.value};
 const size=(w,h)=>send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
 const go=async u=>{await send('Page.navigate',{url:'http://127.0.0.1:'+PORT+'/'+u});for(let i=0;i<150;i++){await sleep(100);if(await ev('document.readyState==="complete"'))break}await sleep(500)};
 const shot=async f=>{if(!SHOT)return;const r=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(SHOT,f),Buffer.from(r.result.data,'base64'));console.log('shot',f)};
 const tab=async(shift)=>{await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9,modifiers:shift?8:0});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9,modifiers:shift?8:0});await sleep(80)};
 await send('Page.enable');await send('Runtime.enable');
 // ---- focus + skip link, both themes
 for(const theme of ['halloween','normal']){
  await size(1024,768);await go('walkthrough.html');
  await ev(`localStorage.setItem('mnm-halloween','${theme==='normal'?'off':'on'}')`);await go('walkthrough.html');
  ok(await ev('document.documentElement.classList.contains("halloween")')===(theme==='halloween'),theme+' theme active');
  await tab();
  const sk=await ev(`(function(){var a=document.activeElement,cs=getComputedStyle(a),r=a.getBoundingClientRect();return {cls:a.className,top:r.top,ow:cs.outlineWidth,os:cs.outlineStyle,oc:cs.outlineColor}})()`);
  ok(sk.cls==='skip'&&sk.top>=0&&sk.os==='solid'&&parseFloat(sk.ow)>=2,theme+': first Tab shows the Skip to content link with a '+sk.ow+' '+sk.oc+' focus ring');
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,text:'\r'});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await sleep(200);
  ok(await ev('document.activeElement.id')==='content','Enter on skip link moves focus to <main id=content>');
  await ev('document.getElementById("mnm-class").focus({focusVisible:true})');await tab();await tab(true);
  const sf=await ev(`(function(){var a=document.activeElement,cs=getComputedStyle(a);return {id:a.id,os:cs.outlineStyle,ow:cs.outlineWidth,oc:cs.outlineColor}})()`);
  ok(sf.id==='mnm-class'&&sf.os==='solid'&&parseFloat(sf.ow)>=2,theme+': keyboard-focused select has a visible ring ('+sf.ow+' '+sf.oc+')');
  await shot('ux1-after-focus-'+theme+'-1024.png');
 }
 await ev(`localStorage.removeItem('mnm-halloween')`);
 // ---- overflow at every target width, sticky rails clear the header
 for(const [w,h] of [[480,900],[1024,768],[2560,1080],[3440,1440]]){await size(w,h);
  for(const u of ['index.html','classes/inquisitor.html','walkthrough.html','market.html','hotbar.html','items.html']){await go(u);
   ok(!(await ev('document.documentElement.scrollWidth>innerWidth')),'no horizontal overflow: '+u+' @'+w)}
  if(w>=1024){await go('classes/inquisitor.html');await ev('scrollTo(0,1200)');await sleep(200);
   const g=await ev(`(function(){var t=document.querySelector('.top').getBoundingClientRect(),l=document.querySelector('.left').getBoundingClientRect();return {tb:Math.round(t.bottom),lt:Math.round(l.top)}})()`);
   ok(g.lt>=g.tb,'@'+w+': sticky side rail sits below the header (rail top '+g.lt+' >= header bottom '+g.tb+')')}
 }
 await size(3440,1440);await go('index.html');
 const uw=await ev(`(function(){var m=document.querySelector('.wrap').getBoundingClientRect(),q=[].slice.call(document.querySelectorAll('.quickinfo>.qi-sec')).map(function(s){return Math.round(s.getBoundingClientRect().top)});return {w:Math.round(m.width),cols:q.filter(function(t){return t===q[0]}).length}})()`);
 ok(uw.w>=2300&&uw.cols>=3,'3440 ultrawide: layout '+uw.w+'px wide, quick info in '+uw.cols+' columns');
 await size(2560,1080);await go('index.html');
 const lg=await ev(`(function(){var m=document.querySelector('.wrap').getBoundingClientRect(),q=[].slice.call(document.querySelectorAll('.quickinfo>.qi-sec')).map(function(s){return Math.round(s.getBoundingClientRect().top)});return {w:Math.round(m.width),cols:q.filter(function(t){return t===q[0]}).length}})()`);
 ok(lg.w>=1900&&lg.cols>=2,'2560x1080: layout '+lg.w+'px wide, quick info in '+lg.cols+' columns');
 await shot('ux1-after-home-2560.png');
 await go('classes/inquisitor.html');
 const pw=await ev(`(function(){var p=document.querySelector('.main>p');var s=getComputedStyle(p);return {w:p.getBoundingClientRect().width,fs:parseFloat(s.fontSize)}})()`);
 ok(pw.w/pw.fs<=48,'prose measure capped (~78ch): first paragraph '+Math.round(pw.w)+'px at '+pw.fs+'px font');
 // ---- phone: touch targets + mini bar
 await size(480,900);await go('walkthrough.html');
 const small=await ev(`[].filter.call(document.querySelectorAll('.top a,.top button,.top select,.top input,.rangebar a,.rangebar select,.rangebar button,.rangebar input,.rangebar summary'),function(e){var r=e.getBoundingClientRect();return r.width&&r.height&&e.checkVisibility()&&r.height<44&&!e.closest('#cg-valid')}).map(function(e){return e.tagName+'.'+e.className}).join()`);
 ok(small==='','480: every header/picker control is at least 44px tall'+(small?' — '+small:''));
 ok(await ev('getComputedStyle(document.querySelector(".top")).position')!=='sticky','480: tall header is not sticky (no 300px fixed band)');
 await ev('scrollTo(0,1600)');await sleep(300);
 const mb=await ev(`(function(){var t=document.querySelector('.topin'),r=t.getBoundingClientRect(),s=document.querySelector('.ux-setup').getBoundingClientRect(),q=document.getElementById('q').getBoundingClientRect(),b=document.querySelector('.burger').getBoundingClientRect();return {mini:document.body.classList.contains('ux-mini'),pos:getComputedStyle(t).position,top:r.top,h:Math.round(r.height),sw:s.width,sh:s.height,qw:q.width,bh:b.height,y:scrollY}})()`);
 ok(mb.mini&&mb.pos==='fixed'&&mb.top===0&&mb.h<=60&&mb.sh>=44&&mb.bh>=44&&mb.qw>150,'480 scrolled: compact mini bar fixed at top, '+mb.h+'px tall, search '+Math.round(mb.qw)+'px, Setup and menu buttons >=44px');
 ok(Math.abs(mb.y-1600)<2,'mini bar swap does not jump the scroll position');
 await shot('ux1-after-mini-480.png');
 await ev('document.querySelector(".burger").click()');await sleep(150);
 const nv=await ev(`(function(){var n=document.querySelector('.mainnav').getBoundingClientRect();return {top:Math.round(n.top),h:n.height}})()`);
 ok(nv.top>0&&nv.top<=70&&nv.h>100,'480 scrolled: menu opens directly under the mini bar');
 await shot('ux1-after-mini-menu-480.png');
 await ev('document.querySelector(".burger").click()');
 await ev('document.querySelector(".ux-setup").click()');await sleep(900);
 ok(await ev('scrollY')<5&&!(await ev('document.body.classList.contains("ux-mini")'))&&await ev('document.activeElement.id')==='mnm-class','Setup button returns to the top and focuses the Class picker');
 // ---- reduced motion
 await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});await size(1024,768);await go('index.html');
 const rm=await ev(`(function(){var c=document.querySelector('.card')||document.body;var cs=getComputedStyle(c),sig=getComputedStyle(document.querySelector('.logo .sig'));return {t:cs.transitionDuration,a:sig.animationName,ad:sig.animationDuration}})()`);
 ok(parseFloat(rm.t)<=0.001&&(rm.a==='none'||parseFloat(rm.ad)<=0.001),'prefers-reduced-motion: transitions '+rm.t+', logo animation '+rm.a+' '+rm.ad);
 await send('Emulation.setEmulatedMedia',{features:[]});
 ok(errs.length===0,'no JS exceptions'+(errs.length?': '+errs.slice(0,2).join(' | '):''));
 console.log(passes+' passed, '+fails+' failed');ws.close();chrome.kill();srv.kill();process.exit(fails?1:0);
})().catch(e=>{console.error(e);chrome.kill();srv.kill();process.exit(1)});
