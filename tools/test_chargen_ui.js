// Headless Chrome test for "Best races" rankings + Quick info walkthrough summary.
// Usage: node --experimental-websocket tools/test_chargen_ui.js [shotdir]   (serves docs/ on a local port, needs google-chrome)
const {spawn}=require('child_process'),http=require('http'),fs=require('fs'),path=require('path');
const DOCS=path.join(__dirname,'..','docs'),SHOT=process.argv[2]||null,PORT=8000+Math.floor(Math.random()*900);
const srv=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:DOCS,stdio:'ignore'});
const chrome=spawn('google-chrome',['--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port='+(PORT+1000),'--user-data-dir=/tmp/rr-chrome-'+PORT,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0,passes=0;function ok(c,m){if(c){passes++;console.log('PASS',m)}else{fails++;console.log('FAIL',m)}}
function getJSON(u){return new Promise((res,rej)=>http.get(u,r=>{let d='';r.on('data',x=>d+=x);r.on('end',()=>{try{res(JSON.parse(d))}catch(e){rej(e)}})}).on('error',rej))}
(async()=>{
 let tabs;for(let i=0;i<50;i++){try{tabs=await getJSON('http://127.0.0.1:'+(PORT+1000)+'/json');break}catch(e){await sleep(200)}}
 const t=tabs.find(x=>x.type==='page');const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pend={},evw=[];ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend[d.id]){pend[d.id](d);delete pend[d.id]}else evw.forEach(f=>f(d))};
 const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}))});
 const ev=async(expr)=>{const r=await send('Runtime.evaluate',{expression:expr,awaitPromise:true,returnByValue:true});if(r.result.exceptionDetails)throw new Error(expr+'\n'+JSON.stringify(r.result.exceptionDetails));return r.result.result.value};
 const size=async(w,h)=>send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
 const waitQ=async(e,ms=8000)=>{for(let i=0;i<ms/50;i++){if(await ev(e))return true;await sleep(50)}return false};
 const go=async(u)=>{const url='http://127.0.0.1:'+PORT+'/'+u;await send('Page.navigate',{url});
   for(let i=0;i<100;i++){await sleep(100);try{if(await ev(`location.href===${JSON.stringify(url)}&&document.readyState==='complete'&&!!window.MNM_WT`))break}catch(e){}}await sleep(150)};
 const shot=async(file,sel,maxH)=>{if(!SHOT)return;const b=await ev(`(function(){if(!document.getElementById('rr-shotcss')){var st=document.createElement('style');st.id='rr-shotcss';st.textContent='header,.rangebar,#mnm-rangebar,.topbar{position:static!important}';document.head.appendChild(st)}var e=document.querySelector(${JSON.stringify(sel)});e.scrollIntoView();var r=e.getBoundingClientRect();return {x:0,y:r.top+scrollY-8,w:innerWidth,h:Math.min(r.height+16,${maxH||1800})}})()`);
   const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:b.x,y:b.y,width:b.w,height:b.h,scale:1}});fs.writeFileSync(path.join(SHOT,file),Buffer.from(r.result.data,'base64'));console.log('shot',file)};
 const overflow=()=>ev('document.documentElement.scrollWidth-innerWidth');
 await send('Page.enable');await send('Runtime.enable');
 const G=JSON.parse(fs.readFileSync(path.join(DOCS,'assets','chargen-data.js'),'utf8').replace(/^window\.MNM_CG=/,'').replace(/;$/,''));
 const classes=Object.keys(G.combos).sort();ok(classes.length===18,'18 classes in chargen data');
 await size(480,900);
 for(const c of classes){
  const u=c==='Shaman'?'shaman/index.html':'classes/'+c.toLowerCase().replace(/ /g,'-')+'.html';
  await go(u);await ev('localStorage.clear()');await go(u);
  const n=Object.keys(G.combos[c]).length;
  const r=await ev(`(function(){var rr=document.getElementById('best-races');if(!rr)return null;var tb=document.querySelector('.tab[data-tab$="-cg"]');tb&&tb.click();
    return {rows:rr.querySelectorAll('.rr-row').length,vis:rr.offsetHeight>0,why:!!rr.querySelector('.rr-why1'),first:rr.querySelector('.rr-row').getAttribute('data-cg-race'),more:!!rr.querySelector('.rr-more'),
      qw:(document.querySelector('.cg-qwalk .qw-head')||{}).textContent||'',top:rr.querySelectorAll(':scope > .rr-list .rr-row').length}})()`);
  ok(r&&r.rows===n&&r.vis&&r.why,`${c}: Best races renders all ${n} races, visible in Character creation tab`);
  ok(r&&G.large.indexOf(r.first)<0,`${c}: #1 is not a large race (${r&&r.first})`);
  ok(r&&r.top===Math.min(3,n)&&r.more===(n>3),`${c}: top ${Math.min(3,n)} shown, expandable list ${n>3?'present':'absent'}`);
  ok(await overflow()<=0,`${c}: no horizontal overflow at 480px (Character creation tab)`);
  await ev(`document.querySelector('.tab').click()`);ok(await overflow()<=0,`${c}: no horizontal overflow at 480px (quick reference tab)`);
  // UX pass 5: walk-data.js loads once the Quick info walkthrough is on screen, so scroll to it first
  await ev(`(document.querySelector('.cg-qwalk')||document.body).scrollIntoView()`);
  ok(await waitQ(`/New character:/.test((document.querySelector('.cg-qwalk .qw-head')||{}).textContent||'')`),`${c}: Quick info walkthrough summary renders`);
 }
 // expand + click-to-set on Rogue
 await go('classes/rogue.html');await ev('localStorage.clear()');await ev(`localStorage.setItem('mnm-class','Wizard')`);await go('classes/rogue.html');
 await ev(`document.querySelector('.tab[data-tab$="-cg"]').click()`);
 const ex=await ev(`(function(){var d=document.querySelector('.rr-more');var before=d.querySelector('.rr-row').checkVisibility();d.querySelector('summary').click();return {before:before,after:d.querySelector('.rr-row').checkVisibility(),open:d.open,n:d.querySelectorAll('.rr-row').length}})()`);
 ok(ex.before===false&&ex.after===true&&ex.open&&ex.n===5,'Rogue: Show all 8 expands the 5 hidden races '+JSON.stringify(ex));
 ok(await overflow()<=0,'Rogue: no overflow at 480px when expanded');
 await shot('race-rank-expanded-480.png','#best-races',2600);
 const cl=await ev(`(function(){var b=[].find.call(document.querySelectorAll('.rr-use'),x=>x.getAttribute('data-race')==='Gnome');b.click();
   return {race:localStorage.getItem('mnm-race'),cls:localStorage.getItem('mnm-class'),city:localStorage.getItem('mnm-city'),sel:document.getElementById('mnm-race').value,selC:document.getElementById('mnm-class').value,url:location.search,
     hl:document.querySelector('.rr-row.cg-sel').getAttribute('data-cg-race'),msg:(document.querySelector('.rr-msg')||{}).textContent}})()`);
 await sleep(100);
 ok(cl.race==='Gnome'&&cl.sel==='Gnome','click sets Race picker + mnm-race (Gnome)');
 ok(cl.cls==='Rogue'&&cl.selC==='Rogue','click on Rogue page sets Class to Rogue (was Wizard)');
 ok(G.combos.Rogue.Gnome.indexOf(cl.city)>=0,'Start stays valid after click ('+cl.city+')');
 ok(/race=Gnome/.test(cl.url)&&/class=Rogue/.test(cl.url),'URL carries class/race/city: '+cl.url);
 ok(cl.hl==='Gnome'&&/Race set to Gnome/.test(cl.msg||''),'selected row highlighted + confirmation');
 // hash opens the tab
 await go('classes/fighter.html#best-races');await sleep(200);
 ok(await ev(`document.getElementById('best-races').offsetHeight>0`),'#best-races link opens the Character creation tab');
 // Inquisitor: Deep Elf / Ail'Vorith, band changes
 await go('classes/inquisitor.html');await ev('localStorage.clear()');await ev(`localStorage.setItem('mnm-range','1-5')`);await go('classes/inquisitor.html');
 await ev(`document.querySelector('.tab[data-tab$="-cg"]').click()`);
 await shot('race-rank-inquisitor-480.png','#best-races',2400);
 await ev(`[].find.call(document.querySelectorAll('.rr-use'),x=>x.getAttribute('data-race')==='Deep Elf').click()`);await sleep(100);
 ok(await ev(`localStorage.getItem('mnm-city')`)==="Ail'Vorith",'Deep Elf Inquisitor click sets Start to Ail\'Vorith');
 await ev(`document.querySelector('.tab').click()`);await ev(`document.querySelector('.cg-qwalk').scrollIntoView()`);await waitQ(`!!document.querySelector('.cg-qwalk .qw-head')`);
 const q=async()=>ev(`(function(){var e=document.querySelector('.cg-qwalk'),f=e.querySelector('.qw-full'),m=e.querySelector('.qw-more');return {t:e.textContent,full:f?f.getAttribute('href'):'',more:!!m&&!m.hidden}})()`);
 let s=await q();
 ok(/Deep Elf Inquisitor · Ail'Vorith · levels 1–5/.test(s.t),'summary header follows race/city/band');
 ok(/Starter area: Ail'Vorith/.test(s.t)&&/Nurvol Cereveth/.test(s.t)&&/Toilmaster/.test(s.t),'1-5: starter steps + trainer from Ail\'Vorith data');
 ok(!/Petra Gyle|Night Harbor\)/.test(s.t),'1-5: no Night Harbor route fallback');
 ok(/Next up:\s*Levels 6–10/.test(s.t),'Next up points to 6–10');
 ok(/walkthrough\.html\?class=Inquisitor&race=Deep%20Elf&city=Ail'Vorith#wt-b-1-5/.test(s.full),'Open full page link uses current picks: '+s.full);
 ok(await overflow()<=0,'quick info summary: no overflow at 480px');
 await ev(`document.querySelector('.qw-toggle').click()`);s=await q();
 ok(s.more&&/Spells and abilities to buy/.test(s.t)&&/Other level ranges/.test(s.t),'Show full walkthrough expands the full band in place with band links');
 ok(await overflow()<=0,'expanded quick info: no overflow at 480px');
 await ev(`document.querySelector('.qw-toggle').click()`);
 await shot('quickinfo-walkthrough-480.png','.cg-qwalk',2200);
 // band change via the top-bar Levels picker
 await ev(`(function(){var s=document.getElementById('mnm-range');s.value='21-25';s.dispatchEvent(new Event('change'))})()`);await sleep(100);s=await q();
 ok(/levels 21–25/.test(s.t)&&/Beyond the starter area/.test(s.t)&&!/Starter area:/.test(s.t)&&/Next up:\s*Levels 26–30/.test(s.t),'band change to 21–25 updates live: zones/camps, next up 26–30 :: '+s.t.slice(0,400));
 ok(/#wt-b-21-25/.test(s.full),'full page link follows the band');
 // band button in Next up
 await ev(`document.querySelector('.qw-next .qw-band').click()`);await sleep(100);s=await q();
 ok(/levels 26–30/.test(s.t)&&(await ev(`localStorage.getItem('mnm-range')`))==='26-30','Next up button moves to 26–30 and saves the band');
 // race change via top bar updates live
 await ev(`(function(){var s=document.getElementById('mnm-race');s.value='Human';s.dispatchEvent(new Event('change'))})()`);await sleep(100);s=await q();
 ok(/Human Inquisitor · Night Harbor/.test(s.t),'Race picker change updates the summary live');
 // no data for a city -> 'no sourced data yet', no fallback
 await ev(`(function(){delete MNM_WT.cities['Night Harbor'];var s=document.getElementById('mnm-city');s.dispatchEvent(new Event('change'))})()`);await sleep(100);s=await q();
 ok(/No sourced data yet/i.test(s.t)&&!/Starter area|Where to go/.test(s.t),'city with no data shows "no sourced data yet" and no other route');
 // walkthrough page still renders through the shared renderer
 await go("walkthrough.html?class=Inquisitor&race=Deep%20Elf&city=Ail'Vorith");
 const wt=await ev(`({t:document.getElementById('cg-walk').textContent,n:document.querySelectorAll('#cg-walk details.cg-band').length})`);
 ok(/Level 1: first steps in Ail'Vorith/.test(wt.t)&&wt.n===8,'walkthrough.html renders 8 bands for Deep Elf / Ail\'Vorith via walkHTML');
 // desktop shot
 await size(1280,900);await go('classes/rogue.html#best-races');await sleep(300);
 ok(await overflow()<=0,'desktop: no overflow');
 await shot('race-rank-desktop.png','#best-races',1600);
 console.log(`\n${passes} passed, ${fails} failed`);
 ws.close();chrome.kill();srv.kill();process.exit(fails?1:0);
})().catch(e=>{console.error(e);chrome.kill();srv.kill();process.exit(2)});
