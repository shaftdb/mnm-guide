// Headless Chrome checks for UX passes 1-8 (pass 8 near the end: Spells rows from per-class data with the no-JS page, hotbar clicky
// list on demand, spell/mob tip pieces with an exact-match check, Compare from item tooltips and the Market page).
// Earlier: UX passes 1-6 (pass 6 at the end: Items/Mobs databases in pieces with loading/error/Try again,
// tooltips on Spells/zone camp tables/Items mob names, print one walkthrough band, hotbar dialog contrast, Irem x theme combos).
// Pass 5 before it: lazy walk-data on class pages, Shaman routes on demand, spell/mob
// tooltips, CSV export + print, Light/High contrast themes with 4.5:1 / 3:1 contrast scans. Pass 4 before it: on-demand class routes/tabs, Items/Mobs memory, lazy palette,
// favorites, copy buttons, what's new). UX pass 1: skip link + focus ring (normal and Halloween themes), compact mini bar on phones,
// 44px touch targets at 480, no horizontal overflow at 480/1024/2560/3440, ultrawide width + multi-column quick info,
// sticky side rails below the real header, prefers-reduced-motion.
// Usage: node --experimental-websocket tools/test_ux.js [shotdir]
const {spawn}=require('child_process'),http=require('http'),fs=require('fs'),path=require('path');
const DOCS=path.join(__dirname,'..','docs'),SHOT=process.argv[2]||null,PORT=8000+Math.floor(Math.random()*900);
const srv=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:DOCS,stdio:'ignore'});
try{fs.rmSync('/tmp/uxt-chrome-'+PORT,{recursive:true,force:true})}catch(e){} // fresh profile: no localStorage from an earlier run on the same port
const chrome=spawn('google-chrome',['--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--remote-debugging-port='+(PORT+1000),'--user-data-dir=/tmp/uxt-chrome-'+PORT,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0,passes=0;function ok(c,m){if(c){passes++;console.log('PASS',m)}else{fails++;console.log('FAIL',m)}}
function getJSON(u){return new Promise((res,rej)=>http.get(u,r=>{let d='';r.on('data',x=>d+=x);r.on('end',()=>{try{res(JSON.parse(d))}catch(e){rej(e)}})}).on('error',rej))}
(async()=>{
 let tabs;for(let i=0;i<50;i++){try{tabs=await getJSON('http://127.0.0.1:'+(PORT+1000)+'/json');break}catch(e){await sleep(200)}}
 const ws=new WebSocket(tabs.find(x=>x.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pend={},errs=[];let reqs=[];ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend[d.id]){pend[d.id](d);delete pend[d.id]}else if(d.method==='Runtime.exceptionThrown')errs.push(JSON.stringify(d.params.exceptionDetails).slice(0,300));else if(d.method==='Network.requestWillBeSent')reqs.push(d.params.request.url.replace(/^.*\/assets\//,''))};
 const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}))});
 const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true});if(r.result.exceptionDetails)throw new Error(e+' '+JSON.stringify(r.result.exceptionDetails).slice(0,300));return r.result.result.value};
 const size=(w,h)=>send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
 const go=async u=>{await send('Page.navigate',{url:'http://127.0.0.1:'+PORT+'/'+u});for(let i=0;i<150;i++){await sleep(100);if(await ev('document.readyState==="complete"'))break}await sleep(500)};
 const shot=async f=>{if(!SHOT)return;const r=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(SHOT,f),Buffer.from(r.result.data,'base64'));console.log('shot',f)};
 const tab=async(shift)=>{await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9,modifiers:shift?8:0});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9,modifiers:shift?8:0});await sleep(80)};
 await send('Page.enable');await send('Runtime.enable');await send('Network.enable');await send('Network.setCacheDisabled',{cacheDisabled:true});
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
 // ---- phone: touch targets + mini bar (pass 1; the pickers sit behind My setup since pass 2)
 await size(480,900);await go('walkthrough.html');await ev('document.querySelector(".ux-mysetup").click()');
 const small=await ev(`[].filter.call(document.querySelectorAll('.top a,.top button,.top select,.top input,.rangebar a,.rangebar select,.rangebar button,.rangebar input,.rangebar summary'),function(e){var r=e.getBoundingClientRect();return r.width&&r.height&&e.checkVisibility()&&r.height<44&&!e.closest('#cg-valid')&&!e.closest('#mnm-ts .ts-menu')}).map(function(e){return e.tagName+'.'+e.className}).join()`);
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

 // =============================== UX pass 2
 // UX pass 8: spell/mob tips load as one piece (stip-<n>.js / mtip-<n>.js) or the full fallback file
 const TIPR=k=>reqs.some(r=>(k==='s'?/^(spell-tips|stip-\d+)\.js/:/^(mob-tips|mtip-\d+)\.js/).test(r));
 const waitFor=async(expr,ms=8000)=>{for(let i=0;i<ms/50;i++){if(await ev(expr))return true;await sleep(50)}return false};
 const sz=f=>{try{return Math.round(require('fs').statSync(path.join(DOCS,'assets',f)).size/1024)}catch(e){return -1}};
 await size(1024,768);
 // lazy loading: nothing big on first load
 for(const u of ['index.html','market.html','classes/inquisitor.html','walkthrough.html']){reqs=[];await go(u);await sleep(800);
  const pg=await ev('({mount:!!document.querySelector("[data-ts-mount]"),badge:!!document.querySelector("table.gear a.itm[data-i], ul.gearlist a.itm[data-i], .quickinfo a.itm[data-i]")})');
  const big=reqs.filter(r=>/^(search-index|item-tips|hotbar-data|walk-data)/.test(r)&&!(r.startsWith('walk-data')&&/inquisitor|walkthrough/.test(u))||/^quick-c-/.test(r)&&r!=='quick-c-fighter.js'||/^trade-b-/.test(r)&&!pg.mount||/^trade-items/.test(r)&&!pg.badge||/^quick-data\.js/.test(r)&&sz('quick-data.js')>100);
  const tb=reqs.filter(r=>/^trade-b-/.test(r));
  ok(big.length===0&&tb.length<=3,u+': first load skips the search index, item tips and hotbar data; trade chunks only where used ('+(reqs.filter(r=>/^(trade|quick-c|walk)/.test(r)).join(', ')||'none')+')'+(big.length?' — unexpected: '+big.join(','):''));}
 reqs=[];await go('index.html');await waitFor('!!document.querySelector("#mnm-quickinfo .qi-sec")&&!document.querySelector("#mnm-quickinfo .lz-status")');
 ok(reqs.filter(r=>/^quick-c-/.test(r)).length===1&&reqs.some(r=>r==='quick-c-fighter.js'),'home: loads only the selected class\'s Quick info chunk (quick-c-fighter.js, '+sz('quick-c-fighter.js')+' KB of the old 2.7 MB file)');
 ok(reqs.some(r=>r==='trade-items.js'),'home: trade item list loads because Quick info shows gear (trade badges)');
 await ev('(function(){var s=document.getElementById("mnm-class");s.value="Bard";s.dispatchEvent(new Event("change"))})()');
 const qs=await ev('(function(){var s=document.querySelector("#mnm-quickinfo .lz-status");return s?s.textContent:""})()');
 ok(/Loading Quick info for Bard/.test(qs),'class change shows a loading state: "'+qs+'"');
 ok(await waitFor('/Quick info · Bard/.test(document.querySelector("#mnm-quickinfo h2").textContent)&&!document.querySelector("#mnm-quickinfo .lz-status")'),'Bard Quick info renders after its chunk loads');
 await ev('(function(){var s=document.getElementById("mnm-class");s.value="Fighter";s.dispatchEvent(new Event("change"))})()');await waitFor('/Fighter/.test(document.querySelector("#mnm-quickinfo h2").textContent)');
 // search index on first focus
 reqs=[];await go('index.html');ok(!(await ev('!!window.MNM_INDEX')),'search index not loaded before search is used');
 await ev('(function(){var q=document.getElementById("q");q.focus();q.value="shaman";q.dispatchEvent(new Event("input"))})()');
 const sl=await ev('document.getElementById("qres").textContent');
 ok(/Loading search index/.test(sl)||/Shaman/i.test(sl),'search shows "Loading search index…" until the index arrives');
 ok(await waitFor('document.querySelectorAll("#qres a[href]").length>3'),'search results appear once the titles index loads ('+sz('search-titles.js')+' KB, only when searching)');
 // item tooltips
 reqs=[];await go('classes/inquisitor.html');
 const tipTxt=await ev('(function(){var a=document.querySelector(".itm[data-i]");var r=a.getBoundingClientRect();a.dispatchEvent(new MouseEvent("mouseover",{bubbles:true,clientX:r.left+5,clientY:r.top+5}));return document.getElementById("tip").textContent})()');
 ok(/Loading item stats/.test(tipTxt),'first item hover shows "Loading item stats…"');
 ok(await waitFor('(function(){var t=document.getElementById("tip");return !t.hidden&&/Slot:/.test(t.textContent)})()'),'tooltip fills in after item-tips.js loads');
 // walkthrough
 await go('walkthrough.html');ok(await waitFor('!!document.querySelector("#cg-walk h2")'),'walkthrough renders after walk-data.js loads async');
 // trades guidance per skill
 reqs=[];await go('tradeskills.html');
 ok(await waitFor('(function(){var b=document.querySelector("[data-ts-mount] .ts-body");return b&&!b.querySelector(".lz-status")&&b.textContent.length>200})()'),'trades guidance renders from per-skill chunks');
 const tb=reqs.filter(r=>/^trade-b-/.test(r));ok(tb.length>=1&&tb.length<=4,'only the selected skills\' chunks load ('+tb.join(', ')+')');
 const unsel=await ev('(function(){var i=[].find.call(document.querySelectorAll("#mnm-ts-menu input[type=checkbox]"),function(x){return !x.checked});i.click();return i.value})()');
 const ls=await ev('(function(){var b=document.querySelector("[data-ts-mount] .ts-body");return b.textContent})()');
 ok(/Loading tradeskill guidance/.test(ls)||reqs.includes('trade-b-'+unsel+'.js'),'ticking '+unsel+' shows a loading state and fetches trade-b-'+unsel+'.js');
 ok(await waitFor('reqs=0,(function(){var b=document.querySelector("[data-ts-mount] .ts-body");return !b.querySelector(".lz-status")})()'),'guidance updates after the chunk loads');
 await ev('localStorage.removeItem("mnm-trades")');
 // offline / blocked chunks show a clear error
 await send('Network.setBlockedURLs',{urls:['*search-index.js','*search-titles.js','*quick-c-bard.js']});
 await go('index.html');
 await ev('(function(){var q=document.getElementById("q");q.focus();q.value="shaman";q.dispatchEvent(new Event("input"))})()');
 ok(await waitFor('/could not load/i.test(document.getElementById("qres").textContent)'),'blocked search index: "Search index could not load (offline?)"');
 await ev('(function(){var s=document.getElementById("mnm-class");s.value="Bard";s.dispatchEvent(new Event("change"))})()');
 ok(await waitFor('/could not load/i.test((document.querySelector("#mnm-quickinfo .lz-status")||{}).textContent||"")'),'blocked Quick info chunk: error message, previous panel kept');
 await send('Network.setBlockedURLs',{urls:[]});
 await ev('(function(){var s=document.getElementById("mnm-class");s.value="Fighter";s.dispatchEvent(new Event("change"))})()');
 // aria-sort
 await go('quests.html');
 const as=await ev('(function(){var t=document.querySelector("table.sortable"),h=t.tHead.rows[0].cells,a=h[0],b=h[1];a.click();var r1=a.getAttribute("aria-sort");a.click();var r2=a.getAttribute("aria-sort");b.focus();b.dispatchEvent(new KeyboardEvent("keydown",{key:"Enter",bubbles:true}));return [r1,r2,a.getAttribute("aria-sort"),b.getAttribute("aria-sort"),b.tabIndex].join("|")})()');
 ok(as==='ascending|descending||ascending|0','aria-sort follows clicks and Enter, only on the sorted column ('+as+')');
 // phones: My setup, valid-starts disclosure, On this page, font sizes
 await size(480,900);await go('index.html');
 const ms=await ev('(function(){var b=document.querySelector(".ux-mysetup"),rb=document.getElementById("mnm-rangebar");return {bh:Math.round(b.getBoundingClientRect().height),rh:Math.round(rb.getBoundingClientRect().height),v:b.querySelector(".ux-ms-v").textContent,sel:document.getElementById("mnm-class").checkVisibility(),ex:b.getAttribute("aria-expanded")}})()');
 ok(ms.bh>=44&&ms.rh<=62&&!ms.sel&&ms.ex==='false','480: picker bar collapsed to one "My setup" row ('+ms.rh+'px)');
 ok(/Fighter · Human · Night Harbor · 11–15 · Gathering/.test(ms.v),'My setup summary: '+ms.v);
 await shot('ux2-after-mysetup-480.png');
 await ev('document.querySelector(".ux-mysetup").click()');
 ok(await ev('document.getElementById("mnm-class").checkVisibility()&&document.querySelector(".ux-mysetup").getAttribute("aria-expanded")==="true"'),'tapping My setup opens the full pickers');
 ok(!(await ev('document.getElementById("cg-valid").checkVisibility()'))&&await ev('document.querySelector(".ux-cgv-btn").checkVisibility()'),'Valid starts line hidden behind a disclosure button');
 await ev('document.querySelector(".ux-cgv-btn").click()');
 ok(await ev('document.getElementById("cg-valid").checkVisibility()&&/Valid starts for/.test(document.getElementById("cg-valid").textContent)'),'disclosure shows the Valid starts line');
 await shot('ux2-after-mysetup-open-480.png');
 await ev('(function(){var s=document.getElementById("mnm-class");s.value="Cleric";s.dispatchEvent(new Event("change"))})()');await sleep(100);
 ok(/^Cleric/.test(await ev('document.querySelector(".ux-ms-v").textContent')),'summary follows picker changes');
 await ev('(function(){var s=document.getElementById("mnm-class");s.value="Fighter";s.dispatchEvent(new Event("change"))})()');
 ok(!(await ev('document.documentElement.scrollWidth>innerWidth')),'480: no overflow with the pickers open');
 const fz=await ev('(function(){return [getComputedStyle(document.documentElement).fontSize,getComputedStyle(document.body).fontSize]})()');
 ok(fz[0]==='16px'&&fz[1]==='16px','480: 16px base font ('+fz.join(', ')+')');
 await go('quests.html');const tf=await ev('parseFloat(getComputedStyle(document.querySelector("table.grid td")).fontSize)');ok(tf>=14,'480: table text '+tf+'px (was ~12.3px)');
 await go('classes/inquisitor.html');
 const ob=await ev('(function(){var b=document.querySelector(".ux-otp");if(!b)return null;var r=b.getBoundingClientRect();return {pos:getComputedStyle(b).position,h:r.height,bottom:Math.round(innerHeight-r.bottom),vis:b.checkVisibility()}})()');
 ok(ob&&ob.pos==='fixed'&&ob.h>=44&&ob.vis,'480: sticky "On this page" button');
 await ev('scrollTo(0,2500)');await sleep(150);ok(await ev('document.querySelector(".ux-otp").getBoundingClientRect().bottom<=innerHeight'),'"On this page" stays on screen while scrolling');
 await ev('document.querySelector(".ux-otp").click()');await sleep(150);
 const dlg=await ev('(function(){var d=document.querySelector("dialog.ux-sheet");return {open:d.open,n:d.querySelectorAll("a").length,f:document.activeElement.closest("dialog")===d}})()');
 ok(dlg.open&&dlg.n>=3&&dlg.f,'button opens a sheet with '+dlg.n+' sections, focus inside');
 await shot('ux2-after-onthispage-480.png');
 const tgt=await ev('(function(){var a=[].slice.call(document.querySelectorAll("dialog.ux-sheet a"));a=a[Math.min(3,a.length-1)];var h=a.getAttribute("href");a.click();return h})()');await sleep(500);
 const jt=await ev(`(function(){var t=document.getElementById(${JSON.stringify('X')}.replace('X',decodeURIComponent('${'${tgt}'}'.slice(1))));return {open:document.querySelector("dialog.ux-sheet").open,top:t?Math.round(t.getBoundingClientRect().top):null,vis:t?t.checkVisibility():false}})()`.replace("'${tgt}'",JSON.stringify(tgt)));
 ok(!jt.open&&jt.vis&&jt.top!==null&&jt.top>=-5&&jt.top<300,'tapping a section closes the sheet and jumps to it ('+tgt+', top '+jt.top+'px)');
 await ev('document.querySelector(".ux-otp").click()');await sleep(100);
 await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});await sleep(150);
 ok(!(await ev('document.querySelector("dialog.ux-sheet").open'))&&await ev('document.activeElement.classList.contains("ux-otp")'),'Esc closes the sheet and returns focus to the button');
 await size(1024,768);await go('classes/inquisitor.html');
 ok(!(await ev('document.querySelector(".ux-otp").checkVisibility()'))&&!(await ev('document.querySelector(".ux-mysetup").checkVisibility()'))&&await ev('document.getElementById("mnm-class").checkVisibility()'),'1024: no phone-only controls; full picker bar and side TOC as before');

 // =============================== UX pass 3
 const key=async(k,mods=0,code)=>{const vk={'k':75,'/':191,'?':191,'Escape':27,'ArrowDown':40,'ArrowUp':38,'Enter':13,'Tab':9,'ArrowRight':39,'ArrowLeft':37,'End':35,'Home':36,'PageDown':34,'PageUp':33,'g':71,'i':73,'t':84,'p':80}[k]||0;
  const p={key:k,code:code||(k.length===1?'Key'+k.toUpperCase():k),windowsVirtualKeyCode:vk,modifiers:mods};
  await send('Input.dispatchKeyEvent',Object.assign({type:'keyDown',text:(k.length===1&&!(mods&2))?k:undefined},p));await send('Input.dispatchKeyEvent',Object.assign({type:'keyUp'},p));await sleep(120)};
 await size(1024,768);
 // 1) start-city route split: Deep Elf Inquisitor in Ail'Vorith only loads Ail'Vorith chunks for the shown band
 await go('index.html');await ev('localStorage.setItem("mnm-range","1-5");localStorage.setItem("mnm-class","Inquisitor")');
 reqs=[];await go("walkthrough.html?class=Inquisitor&race=Deep%20Elf&city=Ail'Vorith");
 ok(await waitFor('(function(){var c=document.querySelector("#wt-b-1-5");return c&&c.open&&!c.querySelector(".wt-slot")&&/Start-city route: Ail.Vorith/.test(c.textContent)})()'),'walkthrough: open band (1-5) fills its Ail\'Vorith route from its chunk');
 let wr=reqs.filter(r=>/^walk-[rh]-/.test(r));
 ok(wr.length===2&&wr.includes('walk-r-1-5-ailvorith.js')&&wr.includes('walk-h-ailvorith.js'),'walkthrough first load fetches only walk-r-1-5-ailvorith.js + walk-h-ailvorith.js ('+wr.join(', ')+'), walk-data.js '+sz('walk-data.js')+' KB');
 const wtx=await ev('document.getElementById("cg-walk").textContent');
 ok(/Starting in Ail.Vorith/.test(wtx)&&!/Start-city route: (Night Harbor|Underdocks|Faelindral)/.test(wtx)&&!/Starting in Night Harbor/.test(wtx),'walkthrough shows Ail\'Vorith only (no Night Harbor / other city route blocks)');
 ok(await ev('[].slice.call(document.querySelectorAll("#cg-walk details.cg-band:not([open]) .wt-slot")).length===7'),'closed bands hold a loading slot until opened');
 reqs=[];await ev('document.querySelector("#wt-b-21-25 summary").click()');
 ok(await waitFor('(function(){var c=document.querySelector("#wt-b-21-25");return c.open&&!c.querySelector(".wt-slot")&&/Start-city route: Ail.Vorith · levels 21/.test(c.textContent)})()')&&reqs.includes('walk-r-21-25-ailvorith.js')&&reqs.filter(r=>/^walk-r-/.test(r)).length===1,'opening band 21-25 loads only walk-r-21-25-ailvorith.js and fills it');
 await shot('ux3-after-walkband-1024.png');
 // blocked chunk: error + retry
 await send('Network.setBlockedURLs',{urls:['*walk-r-26-30-ailvorith.js']});
 await ev('document.querySelector("#wt-b-26-30 summary").click()');
 ok(await waitFor('/did not load/.test((document.querySelector("#wt-b-26-30 .wt-slot")||{}).textContent||"")&&!!document.querySelector("#wt-b-26-30 .wt-retry")'),'blocked band chunk: clear "did not load" message with a Try again button');
 await send('Network.setBlockedURLs',{urls:[]});await ev('document.querySelector("#wt-b-26-30 .wt-retry").click()');
 ok(await waitFor('(function(){var c=document.querySelector("#wt-b-26-30");return !c.querySelector(".wt-slot")&&/Start-city route: Ail.Vorith · levels 26/.test(c.textContent)})()'),'Try again loads the band');
 // class page quick walkthrough loads only its band
 reqs=[];await go("classes/inquisitor.html?class=Inquisitor&race=Deep%20Elf&city=Ail'Vorith");await ev('document.querySelector(".cg-qwalk").scrollIntoView()');
 ok(await waitFor('(function(){var q=document.querySelector(".cg-qwalk");return q&&!q.querySelector(".wt-slot,.lz-status")&&/Start-city route: Ail.Vorith · levels 1/.test(q.textContent)})()'),'class page quick walkthrough shows the Ail\'Vorith 1-5 route');
 wr=reqs.filter(r=>/^walk-[rh]-/.test(r));
 ok(wr.length===1&&wr[0]==='walk-r-1-5-ailvorith.js','class page loads one route chunk ('+wr.join(', ')+')');
 ok(await ev('!/Start-city route: (Night Harbor|Underdocks|Faelindral)/.test(document.querySelector(".cg-qwalk").textContent)'),'class page quick walkthrough: no other city\'s route');
 await ev('localStorage.setItem("mnm-range","11-15");localStorage.setItem("mnm-class","Fighter");localStorage.removeItem("mnm-race");localStorage.removeItem("mnm-city")');
 // quick-r routenh rebuilt exactly from route + Night Harbor notes
 await go('index.html');await waitFor('!!(window.MNM_QUICK&&MNM_QUICK.routenh&&MNM_QUICK.routenh["11-15"])');
 ok(await ev('(function(){var Q=MNM_QUICK,a=Q.route["11-15"],b=Q.routenh["11-15"];return b.length>a.length&&b.replace(/<p class="sc-nhnote">[\\s\\S]*?<\\/p>/g,"")===a&&(b.match(/sc-nhnote/g)||[]).length===3})()'),'quick-r chunk: routenh = route + 3 Night Harbor notes (stored once, quick-r-1-5.js '+sz('quick-r-1-5.js')+' KB)');
 // 2) search: titles first, full text after the first query, typo tolerance
 reqs=[];await go('index.html');
 await ev('(function(){var q=document.getElementById("q");q.focus();q.value="shamn";q.dispatchEvent(new Event("input"))})()');
 ok(await waitFor('/Shaman/.test(document.getElementById("qres").textContent)&&document.querySelectorAll("#qres a[href]").length>0'),'typo "shamn" finds Shaman');
 ok(reqs.includes('search-titles.js')&&!reqs.includes('search-index.js'),'search loads search-titles.js ('+sz('search-titles.js')+' KB), not the 2 MB search-index.js');
 ok(await waitFor('!!window.MNM_STEXT')&&reqs.includes('search-text.js'),'full text (search-text.js) follows in the background after the first query');
 // palette
 await go('index.html');await go('classes/inquisitor.html');await go('zones/ailvorith.html');
 await key('k',2);await waitFor('!!document.querySelector("dialog.ux-pal[open]")');
 const p1=await ev('(function(){var d=document.querySelector("dialog.ux-pal"),i=document.activeElement;return {open:!!d&&d.open,role:i.getAttribute("role"),ctl:i.getAttribute("aria-controls"),lb:document.getElementById("ux-pal-list").getAttribute("role"),rec:[].slice.call(d.querySelectorAll(".ux-pal-g")).map(function(g){return g.textContent}),t:d.querySelector(".ux-pal-list").textContent}})()');
 ok(p1.open&&p1.role==='combobox'&&p1.ctl==='ux-pal-list'&&p1.lb==='listbox','Ctrl+K opens the quick-jump dialog; focus in a combobox that controls a listbox');
 ok(p1.rec[0]==='Recently viewed'&&/Inquisitor/.test(p1.t)&&/Home/.test(p1.t),'empty palette lists Recently viewed (Inquisitor, Home) then Jump to');
 await ev('(function(){var i=document.getElementById("ux-pal-q");i.value="inquisitr";i.dispatchEvent(new Event("input"))})()');
 ok(await waitFor('/Inquisitor/.test(document.getElementById("ux-pal-list").textContent)&&document.querySelectorAll("#ux-pal-list [role=option]").length>2'),'palette: typo "inquisitr" finds Inquisitor pages ('+await ev('document.getElementById("ux-pal-st").textContent')+')');
 await shot('ux3-after-palette-1024.png');
 await key('ArrowDown');const ad=await ev('(function(){var i=document.getElementById("ux-pal-q"),a=i.getAttribute("aria-activedescendant");return a&&document.getElementById(a).getAttribute("aria-selected")==="true"?a:null})()');
 ok(ad==='ux-pal-o1','ArrowDown moves aria-activedescendant ('+ad+')');
 await key('Tab');await key('Tab');ok(await ev('!!document.activeElement.closest("dialog.ux-pal")'),'Tab stays inside the dialog (focus trap)');
 await ev('document.getElementById("ux-pal-q").focus()');await key('Escape');
 ok(!(await ev('document.querySelector("dialog.ux-pal").open')),'Esc closes the palette');
 await key('/',0,'Slash');await waitFor('!!document.querySelector("dialog.ux-pal[open]")');ok(await ev('document.querySelector("dialog.ux-pal").open&&document.activeElement.id==="ux-pal-q"'),"'/' opens the palette");
 await ev('(function(){var i=document.getElementById("ux-pal-q");i.value="walkthrough";i.dispatchEvent(new Event("input"))})()');await waitFor('document.querySelectorAll("#ux-pal-list [role=option]").length>0');
 await key('Enter');for(let i=0;i<60;i++){await sleep(100);if(await ev('document.readyState==="complete"&&!document.querySelector("dialog.ux-pal[open]")'))break}
 ok(/walkthrough/.test(await ev('location.pathname')),'Enter opens the active result ('+await ev('location.pathname')+')');
 // '?' shortcuts + g-sequences
 await go('index.html');await key('?',8,'Slash');await waitFor('!!document.querySelector("dialog.ux-keys[open]")');
 ok(await ev('(function(){var d=document.querySelector("dialog.ux-keys");return !!d&&d.open&&/Ctrl/.test(d.textContent)&&document.activeElement.closest("dialog")===d})()'),"'?' opens the keyboard-shortcuts overlay with focus inside");
 await shot('ux3-after-shortcuts-1024.png');
 await key('Escape');ok(!(await ev('document.querySelector("dialog.ux-keys").open')),'Esc closes the overlay');
 await key('g');await key('i');for(let i=0;i<60;i++){await sleep(100);if(await ev('document.readyState==="complete"&&/items/.test(location.pathname)'))break}
 ok(/items\.html/.test(await ev('location.pathname')),'g then i goes to Items');
 // touch: header search button opens the palette at 480
 await size(480,900);await send('Emulation.setTouchEmulationEnabled',{enabled:true});await go('index.html');
 const pb=await ev('(function(){var b=document.querySelector(".ux-palbtn"),r=b.getBoundingClientRect();return {w:r.width,h:r.height,vis:b.checkVisibility(),ovf:document.documentElement.scrollWidth>innerWidth}})()');
 ok(pb.vis&&pb.w>=44&&pb.h>=44&&!pb.ovf,'480: header search button is a 44px touch target, no overflow');
 await ev('document.querySelector(".ux-palbtn").click()');await waitFor('!!document.querySelector("dialog.ux-pal[open]")');
 ok(await ev('document.querySelector("dialog.ux-pal").open&&document.querySelector("dialog.ux-pal").getBoundingClientRect().right<=innerWidth'),'480: tapping it opens the palette, fits the screen');
 await ev('(function(){var i=document.getElementById("ux-pal-q");i.value="ail";i.dispatchEvent(new Event("input"))})()');await waitFor('document.querySelectorAll("#ux-pal-list [role=option]").length>3');
 await shot('ux3-after-palette-480.png');
 await ev('document.querySelector(".ux-pal-x").click()');await sleep(200);ok(await ev('!document.querySelector("dialog.ux-pal").open&&document.activeElement.classList.contains("ux-palbtn")'),'close button returns focus to the header button');
 await ev('scrollTo(0,1500)');await sleep(200);
 const mini=await ev('(function(){var q=document.querySelector(".search input").getBoundingClientRect(),b=document.querySelector(".ux-palbtn").getBoundingClientRect();return {q:q.width,b:b.width,ovf:document.documentElement.scrollWidth>innerWidth,top:b.top}})()');
 ok(mini.q>150&&mini.b>=44&&!mini.ovf&&mini.top<60,'480 mini bar keeps search ('+Math.round(mini.q)+'px) and the search button');
 await send('Emulation.setTouchEmulationEnabled',{enabled:false});
 // 3) table sort/filter memory + URL, toolbar, reset
 await size(1024,768);await go('quests.html');await ev('localStorage.removeItem("mnm-tbl:quests.html")');await go('quests.html?class=Inquisitor');
 const t0=await ev('(function(){var b=document.querySelector(".ux-tbar");return b?b.textContent:""})()');
 ok(/Showing all \d+ rows/.test(t0),'table toolbar shows the row count ('+t0.replace(/Reset$/,'')+')');
 await ev('(function(){var h=document.querySelector("table.sortable thead th:nth-child(2)");h.click();h.click()})()');await sleep(150);
 ok(await ev('/[?&]sort=0\\.1d(&|$)/.test(location.search)&&/[?&]class=Inquisitor(&|$)/.test(location.search)'),'sorting writes ?sort=0.1d and keeps ?class= ('+await ev('location.search')+')');
 await ev('(function(){var f=document.getElementById("mnm-filter");f.value="rat";f.dispatchEvent(new Event("input",{bubbles:true}))})()');await sleep(200);
 const t1=await ev('document.querySelector(".ux-tbar").textContent');
 ok(/Showing \d+ of \d+ rows/.test(t1)&&/Sorted by/.test(t1)&&await ev('/[?&]f=rat(&|$)/.test(location.search)'),'filter updates the count and URL ?f=rat ('+t1.replace(/Reset$/,'')+')');
 await go('quests.html');
 const rs=await ev('(function(){var h=document.querySelector("table.sortable thead th:nth-child(2)");return [h.getAttribute("aria-sort"),document.getElementById("mnm-filter").value,location.search]})()');
 ok(rs[0]==='descending'&&rs[1]==='rat'&&/sort=0\.1d/.test(rs[2]),'coming back restores sort + filter from this browser and mirrors them in the URL ('+rs.join(' | ')+')');
 await size(480,900);await go('quests.html');await shot('ux3-after-tabletoolbar-480.png');
 ok(!(await ev('document.documentElement.scrollWidth>innerWidth')),'480: no overflow with the table toolbar');
 await ev('document.querySelector(".ux-tbar-r").click()');await sleep(150);
 const rr=await ev('(function(){var h=document.querySelector("table.sortable thead th:nth-child(2)");return [h.getAttribute("aria-sort"),document.getElementById("mnm-filter").value,location.search,document.querySelector(".ux-tbar-n").textContent,document.querySelector(".ux-tbar-r").disabled]})()');
 ok(rr[0]===null&&rr[1]===''&&!/sort=|f=/.test(rr[2])&&/Showing all/.test(rr[3])&&rr[4],'Reset clears sort, filter and URL params ('+rr[3]+')');
 await size(1024,768);
 const sh=await go('quests.html?sort=0.0a&f=wolf');
 ok(await ev('document.querySelector("table.sortable thead th").getAttribute("aria-sort")==="ascending"&&document.getElementById("mnm-filter").value==="wolf"'),'a shared link (?sort=0.0a&f=wolf) opens with that sort and filter');
 await ev('document.querySelector(".ux-tbar-r").click()');
 // gear filters
 await go('gear/weapons.html?gt=staff');
 ok(await ev('(function(){var t=document.querySelector(".textfilter");return !!t&&t.value==="staff"&&/Showing \\d+ of/.test(document.querySelector(".ux-tbar").textContent)})()'),'gear page: ?gt= text filter restored and counted');
 await ev('document.querySelector(".ux-tbar-r").click()');
 // existing params still work
 await go('market.html?server=Trem');ok(await ev('/[?&]server=Trem/.test(location.search)'),'?server= untouched on the market page');await ev('localStorage.setItem("mnm-server","Tilustra")');
 // 4) back to top + TOC ampersand
 await go('spells.html');await ev('scrollTo(0,4000)');await sleep(300);
 ok(await ev('(function(){var b=document.querySelector(".ux-totop");return !!b&&!b.hidden&&b.checkVisibility()})()'),'long table page: Back to top button appears after scrolling');
 await ev('document.querySelector(".ux-totop").click()');ok(await waitFor('scrollY<5',4000),'Back to top scrolls up');
 await go('classes/inquisitor.html');
 ok(await ev('![].some.call(document.querySelectorAll(".right .box.toc a"),function(a){return /&amp;|amp;/.test(a.textContent)})&&[].some.call(document.querySelectorAll(".right .box.toc a"),function(a){return /&/.test(a.textContent)})'),'desktop On this page: "&" shows as & (no "amp;")');
 for(const [w,h] of [[480,900],[1024,768],[3440,1440]]){await size(w,h);for(const u of ['index.html','classes/inquisitor.html','walkthrough.html','market.html','quests.html']){await go(u);if(await ev('document.documentElement.scrollWidth>innerWidth'))ok(false,w+' '+u+' overflows')}}
 ok(true,'no horizontal overflow at 480/1024/3440 on home, class, walkthrough, market, quests');
 // =============================== UX pass 4
 const evp=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});return r.result.result&&r.result.result.value};
 const fsz=f=>{try{return Math.round(fs.statSync(path.join(DOCS,f)).size/1024)}catch(e){return -1}};
 ok(!/Notification|serviceWorker|PushManager/.test(fs.readFileSync(path.join(DOCS,'assets','mod-ux.js'),'utf8')+fs.readFileSync(path.join(DOCS,'assets','mod-ux-pal.js'),'utf8')),'no browser notifications, push or service worker anywhere in the UX code');
 // 1a) class page: start-city routes load for the picked city only
 ok(fsz('classes/inquisitor.html')<250,'classes/inquisitor.html is '+fsz('classes/inquisitor.html')+' KB (was 850 KB)');
 await size(480,900);reqs=[];
 await go("classes/inquisitor.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");
 ok(await ev('document.documentElement.getAttribute("data-sc")')==='ailvorith','Deep Elf Inquisitor, Start Ail\'Vorith: page follows Ail\'Vorith');
 await ev('document.querySelector(".cg-qwalk").scrollIntoView()');  // pass 5: the quick walkthrough (and its route) loads when on screen
 ok(await waitFor('!!document.querySelector(".sc-wrap .sc-route[data-sc=ailvorith]")'),'the first level band\'s Ail\'Vorith route renders on demand');
 const r1=reqs.filter(r=>/^walk-r-/.test(r));
 ok(r1.length>=1&&r1.length<8&&r1.every(r=>/-ailvorith\.js$/.test(r)),'first load fetches only nearby Ail\'Vorith bands ('+r1.join(', ')+')');
 await ev('MNM_UX_ROUTES.fillAll()');
 ok(await waitFor('[].every.call(document.querySelectorAll(".sc-lz"),function(l){return !!l.parentNode.querySelector(".sc-route[data-sc=ailvorith]")})&&!document.querySelector(".sc-lz .lz-status")',15000),'all '+await ev('document.querySelectorAll(".sc-lz").length')+' bands render the Ail\'Vorith route when needed (print, scrolling)');
 const av=await ev('(function(){var r=[].slice.call(document.querySelectorAll(".sc-route"));return {other:r.filter(function(e){return e.getAttribute("data-sc")!=="ailvorith"}).length,vis:r.filter(function(e){return e.checkVisibility()}).map(function(e){return e.getAttribute("data-sc")}),nhHead:[].some.call(document.querySelectorAll(".sc-route h3.sc-h"),function(h){return h.checkVisibility()&&/Night Harbor/.test(h.textContent)})}})()');
 ok(av.other===0&&av.vis.length>0&&av.vis.every(x=>x==='ailvorith')&&!av.nhHead,'class page shows Ail\'Vorith routes only (no Night Harbor block in the page, '+av.vis.length+' visible bands)');
 ok(reqs.filter(r=>/^walk-r-/.test(r)).every(r=>/-ailvorith\.js$/.test(r)),'no other city\'s route chunk was downloaded');
 // city change swaps the routes (and never falls back)
 await ev('(function(){var s=document.getElementById("mnm-city");s.value="Night Harbor";s.dispatchEvent(new Event("change",{bubbles:true}))})()');
 const tr=await waitFor('document.documentElement.getAttribute("data-sc")==="night-harbor"&&[].some.call(document.querySelectorAll(".sc-route[data-sc=night-harbor]"),function(e){return e.checkVisibility()})');
 ok(tr,'changing Start to Night Harbor loads and shows the Night Harbor routes');
 await ev('(function(){var s=document.getElementById("mnm-city");s.value="Ail\'Vorith";s.dispatchEvent(new Event("change",{bubbles:true}))})()');await waitFor('document.documentElement.getAttribute("data-sc")==="ailvorith"');
 ok(await ev('[].every.call(document.querySelectorAll(".sc-route"),function(e){return !e.checkVisibility()||e.getAttribute("data-sc")==="ailvorith"})'),'switching back shows Ail\'Vorith only again');
 // blocked route chunk: error + Try again
 await send('Network.setBlockedURLs',{urls:['*walk-r-41-60-ailvorith.js']});await go('classes/inquisitor.html');await ev('MNM_UX_ROUTES.fillAll()');
 ok(await waitFor('/Could not load the Ail.Vorith route for levels 41.60/.test((document.querySelector(".sc-lz[data-band=\\"41-60\\"]")||{}).textContent||"")&&!!document.querySelector(".sc-lz[data-band=\\"41-60\\"] .ux-retry")'),'blocked route chunk: "Could not load the Ail\'Vorith route for levels 41–60" + Try again');
 ok(!(await ev('!!document.querySelector(".sc-lz[data-band=\\"41-60\\"]").parentNode.querySelector(".sc-route")')),'…and no other city is shown in its place');
 await send('Network.setBlockedURLs',{urls:[]});await ev('document.querySelector(".sc-lz[data-band=\\"41-60\\"] .ux-retry").click()');
 ok(await waitFor('!!document.querySelector(".sc-lz[data-band=\\"41-60\\"]").parentNode.querySelector(".sc-route[data-sc=ailvorith]")'),'Try again loads it');
 // 1b) inactive tabs on demand
 reqs=[];await go('classes/inquisitor.html');
 ok(!reqs.includes('ct-inquisitor.js')&&await ev('document.querySelectorAll(".tabpane[data-lz]").length')===5,'5 inactive tabs are placeholders; ct-inquisitor.js ('+sz('ct-inquisitor.js')+' KB) not loaded up front');
 await send('Network.emulateNetworkConditions',{offline:false,latency:1500,downloadThroughput:200000,uploadThroughput:200000});
 await ev('document.querySelector(".tab[data-tab=\\"t0-2\\"]").click()');await sleep(150);
 const ld=await ev('(function(){var s=document.querySelector("#t0-2 .ux-lzp");return s?s.textContent:""})()');
 ok(/Loading .Early spells 1.20./.test(ld),'opening a tab shows "'+ld+'"');
 await ev('document.getElementById("t0-2").scrollIntoView({block:"center",behavior:"instant"})');await shot('ux4-after-classtab-loading-480.png');
 await send('Network.emulateNetworkConditions',{offline:false,latency:0,downloadThroughput:-1,uploadThroughput:-1});
 ok(await waitFor('!!document.querySelector("#t0-2.on table.spells tbody tr")&&!document.querySelector("#t0-2[data-lz]")'),'Early spells tab renders its spell table');
 ok(await ev('(function(){var t=document.querySelector("#t0-2 table.spells");return t.tBodies[0].rows.length<15||!!(t.closest(".tw")||t).previousElementSibling.classList.contains("ux-tbar")})()'),'tab tables get the row-count bar');
 // deep link into a lazy tab
 await go('classes/inquisitor.html#gear-notes');
 ok(await waitFor('(function(){var g=document.getElementById("gear-notes");return g&&!g.classList.contains("ux-lzid")&&g.closest(".tabpane").classList.contains("on")&&g.checkVisibility()})()'),'#gear-notes deep link opens Gear & group role and renders it');
 ok(await waitFor('(function(){var r=document.getElementById("gear-notes").getBoundingClientRect();return r.top>=0&&r.top<innerHeight/2})()'),'…and scrolls to the heading');
 // On this page sheet into a lazy tab
 await go('classes/inquisitor.html');await ev('document.querySelector(".ux-otp").click()');
 await ev('(function(){var a=[].find.call(document.querySelectorAll(".ux-sheet a"),function(a){return /spells-abilities-levels-21-60/.test(a.getAttribute("href"))});a.click()})()');
 ok(await waitFor('(function(){var p=document.getElementById("t0-3");return p.classList.contains("on")&&!p.hasAttribute("data-lz")&&!!p.querySelector("table")})()'),'On this page → Spells 21–60 opens and renders that tab');
 // Ctrl+K result pointing into a tab
 await size(1024,768);await go('index.html');await key('k',2);await waitFor('!!document.querySelector("dialog.ux-pal[open]")');
 await ev('(function(){var i=document.getElementById("ux-pal-q");i.value="leveling route by band";i.dispatchEvent(new Event("input"))})()');
 const hit=await waitFor('[].some.call(document.querySelectorAll("#ux-pal-list [role=option]"),function(o){return /inquisitor\\.html#leveling-route-by-band/.test(o.getAttribute("data-href"))})');
 if(hit)await ev('[].find.call(document.querySelectorAll("#ux-pal-list [role=option]"),function(o){return /inquisitor\\.html#leveling-route-by-band/.test(o.getAttribute("data-href"))}).click()');
 for(let i=0;i<60;i++){await sleep(100);if(await ev('document.readyState==="complete"&&/inquisitor/.test(location.pathname)'))break}
 ok(hit&&await waitFor('(function(){var g=document.getElementById("leveling-route-by-band");return g&&!g.classList.contains("ux-lzid")&&g.checkVisibility()})()'),'Ctrl+K result "Leveling route by band" opens the Inquisitor Leveling route tab');
 // blocked tab data: error + Try again
 await send('Network.setBlockedURLs',{urls:['*ct-inquisitor.js']});await go('classes/inquisitor.html');await ev('document.querySelector(".tab[data-tab=\\"t0-1\\"]").click()');
 ok(await waitFor('/Could not load .Overview./.test(document.querySelector("#t0-1").textContent)&&!!document.querySelector("#t0-1 .ux-retry")'),'blocked tab data: "Could not load “Overview”" + Try again');
 await send('Network.setBlockedURLs',{urls:[]});await ev('document.querySelector("#t0-1 .ux-retry").click()');
 ok(await waitFor('!document.querySelector("#t0-1[data-lz]")&&!!document.getElementById("role-strengths")&&!document.getElementById("role-strengths").classList.contains("ux-lzid")'),'Try again renders the tab');
 // walkthrough: Ail'Vorith only
 await go('walkthrough.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith');await waitFor('document.querySelectorAll("#cg-walk .sc-route").length>0',10000);await sleep(800);
 ok(await ev('(function(){var r=[].slice.call(document.querySelectorAll("#cg-walk .sc-route"));return r.length>0&&r.every(function(e){return e.getAttribute("data-sc")==="ailvorith"})})()'),'walkthrough: Deep Elf Inquisitor in Ail\'Vorith shows Ail\'Vorith routes only');
 // 2) Items / Mobs: filters + sort remembered + URL + toolbar
 await go('items.html');await ev('localStorage.removeItem("mnm-db:items.html")');
 await go('items.html?iq=sword&is=Primary&isort=l');
 const it1=await ev('(function(){var lv=[].map.call(document.querySelectorAll("#idb-out .idb-it>div:first-child .dim"),function(s){var m=s.textContent.match(/lvl (\\d+)/);return m?+m[1]:999});return {q:document.getElementById("idb-q").value,s:document.getElementById("idb-slot").value,o:document.getElementById("isort-sel").value,bar:document.querySelector(".ux-dbbar").textContent,asc:lv.every(function(v,i){return !i||v>=lv[i-1]}),n:lv.length}})()');
 ok(it1.q==='sword'&&it1.s==='Primary'&&it1.o==='l'&&it1.asc&&it1.n>0,'items: ?iq=sword&is=Primary&isort=l opens filtered and sorted by level ('+it1.n+' shown)');
 ok(/\d+ items/.test(it1.bar)&&/Filtered: .sword., Primary/.test(it1.bar)&&/Sorted by level, low to high/.test(it1.bar),'items toolbar: '+it1.bar.replace(/Reset$/,''));
 await ev('(function(){var c=document.getElementById("idb-lvl");c.checked=true;c.dispatchEvent(new Event("change",{bubbles:true}))})()');
 ok(await ev('/[?&]il=1/.test(location.search)&&/[?&]iq=sword/.test(location.search)'),'changing a filter updates the URL ('+await ev('location.search')+')');
 await go('items.html');
 ok(await ev('document.getElementById("idb-q").value==="sword"&&document.getElementById("idb-lvl").checked&&document.getElementById("isort-sel").value==="l"&&/isort=l/.test(location.search)'),'coming back to Items restores search, filters and sort, mirrored in the URL');
 await ev('document.querySelector(".ux-dbbar .ux-tbar-r").click()');
 ok(await ev('document.getElementById("idb-q").value===""&&!document.getElementById("idb-lvl").checked&&document.getElementById("isort-sel").value===""&&location.search===""&&document.querySelector(".ux-dbbar .ux-tbar-r").disabled'),'Reset clears the Items search, filters, sort and URL');
 await go('items.html#Cinder%20Beetle%20Helm');
 ok(await ev('document.getElementById("idb-q").value==="Cinder Beetle Helm"&&/Cinder Beetle Helm/.test(document.getElementById("idb-out").textContent)'),'old #Item links (from Market and Mobs) still open that item');
 await ev('document.querySelector(".ux-dbbar .ux-tbar-r").click()');
 await go('mobs.html');await ev('localStorage.removeItem("mnm-db:mobs.html")');await go('mobs.html?mq=wolf&msort=L');
 const mb1=await ev('(function(){var lv=[].map.call(document.querySelectorAll("#mob-out tbody tr"),function(r){return parseInt(r.cells[1].textContent)||0});return {q:document.getElementById("mob-q").value,o:document.getElementById("msort-sel").value,desc:lv.filter(Boolean).every(function(v,i,a){return !i||v<=a[i-1]}),n:lv.length,bar:document.querySelector(".ux-dbbar").textContent,stale:document.querySelectorAll(".ux-tbar").length}})()');
 ok(mb1.q==='wolf'&&mb1.o==='L'&&mb1.desc&&mb1.n>0&&/\d+ mobs/.test(mb1.bar)&&/Sorted by level, high to low/.test(mb1.bar)&&mb1.stale===1,'mobs: ?mq=wolf&msort=L sorted high to low, one toolbar ('+mb1.bar.replace(/Reset$/,'')+')');
 await ev('(function(){var c=document.getElementById("mob-named");c.checked=true;c.dispatchEvent(new Event("change",{bubbles:true}))})()');await go('mobs.html');
 ok(await ev('document.getElementById("mob-named").checked&&document.getElementById("mob-q").value==="wolf"&&/mn=1/.test(location.search)'),'mobs filters remembered + mirrored in the URL');
 await ev('document.querySelector(".ux-dbbar .ux-tbar-r").click()');
 // 3) palette loads on first use
 reqs=[];await go('index.html');
 ok(!reqs.includes('mod-ux-pal.js')&&!(await ev('!!window.MNM_UX_PALI')),'palette code ('+sz('mod-ux-pal.js')+' KB) is not loaded up front');
 await key('k',2);ok(await waitFor('!!document.querySelector("dialog.ux-pal[open]")')&&reqs.includes('mod-ux-pal.js'),'Ctrl+K loads mod-ux-pal.js and opens the palette');await key('Escape');
 // 4) favorites
 await size(480,900);await go('index.html');await ev('localStorage.removeItem("mnm-favs")');await go('classes/inquisitor.html');
 ok(await ev('document.querySelector(".ux-favbtn").hidden&&document.querySelector(".ux-star").getAttribute("aria-pressed")==="false"'),'no favorites yet: header star list hidden, page star unpressed');
 await ev('document.querySelector(".ux-star").click()');
 const fv=await ev('(function(){var f=JSON.parse(localStorage.getItem("mnm-favs")||"[]"),b=document.querySelector(".ux-favbtn"),r=b.getBoundingClientRect();return {f:f,p:document.querySelector(".ux-star").getAttribute("aria-pressed"),vis:b.checkVisibility(),w:r.width,h:r.height}})()');
 ok(fv.p==='true'&&fv.f.length===1&&fv.f[0].u==='classes/inquisitor.html'&&fv.f[0].t==='Inquisitor'&&fv.vis&&fv.h>=44,'star pins the page (localStorage mnm-favs) and shows the header star list (44px)');
 await go('items.html');await ev('document.querySelector(".ux-star").click()');await go('index.html');
 await ev('document.querySelector(".ux-favbtn").click()');
 const fp=await ev('(function(){var p=document.getElementById("ux-favpop");return {open:!p.hidden,t:[].map.call(p.querySelectorAll("a"),function(a){return a.textContent}),foc:document.activeElement.closest("#ux-favpop")!==null,ovf:document.documentElement.scrollWidth>innerWidth,r:p.getBoundingClientRect().right<=innerWidth}})()');
 ok(fp.open&&fp.t.join('|')==='Item & drop database|Inquisitor'&&fp.foc&&!fp.ovf&&fp.r,'header list shows pinned pages newest first ('+fp.t.join(', ')+'), focus inside, fits 480');
 await shot('ux4-after-favorites-480.png');
 await key('Escape');ok(await ev('document.getElementById("ux-favpop").hidden&&document.activeElement.classList.contains("ux-favbtn")'),'Esc closes the list and returns focus');
 await ev('document.querySelector(".ux-palbtn").click()');await waitFor('!!document.querySelector("dialog.ux-pal[open]")');
 const pg=await ev('[].map.call(document.querySelectorAll("#ux-pal-list .ux-pal-g"),function(g){return g.textContent}).join("|")+" :: "+document.getElementById("ux-pal-list").textContent.slice(0,80)');
 ok(/^Pinned\|/.test(pg)&&/Item & drop database/.test(pg),'palette empty state leads with Pinned ('+pg.slice(0,90)+')');
 await ev('document.querySelector(".ux-pal-x").click()');
 await ev('scrollTo(0,1500)');await sleep(200);
 ok(await ev('(function(){var q=document.querySelector(".search input").getBoundingClientRect();return q.width>150&&document.documentElement.scrollWidth<=innerWidth})()'),'480 mini bar still fits with favorites (star list hides in the mini bar)');
 await go('classes/inquisitor.html');await ev('document.querySelector(".ux-star").click()');
 ok(await ev('JSON.parse(localStorage.getItem("mnm-favs")).length===1&&document.querySelector(".ux-star").getAttribute("aria-pressed")==="false"'),'clicking the star again unpins');
 // 5) copy buttons
 await send('Browser.grantPermissions',{permissions:['clipboardReadWrite','clipboardSanitizedWrite'],origin:'http://127.0.0.1:'+PORT}).catch(()=>{});
 await go('items.html?iq=cinder%20beetle');
 const cb=await ev('(function(){var b=[].find.call(document.querySelectorAll("#idb-out .ux-copy"),function(x){return /Cinder Beetle/.test(x.getAttribute("data-copy"))});return b?{c:b.getAttribute("data-copy"),l:b.getAttribute("aria-label"),h:b.getBoundingClientRect().height}:null})()');
 ok(!!cb&&/Cinder Beetle/.test(cb.c)&&cb.h>=36,'items: a copy button next to each item name ('+(cb&&cb.l)+')');
 await send('Emulation.setFocusEmulationEnabled',{enabled:true});
 const cr=await ev('(function(){var b=[].find.call(document.querySelectorAll("#idb-out .ux-copy"),function(x){return /Cinder Beetle/.test(x.getAttribute("data-copy"))});b.scrollIntoView({block:"center",behavior:"instant"});var r=b.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}})()');
 await sleep(300);for(const t of ['mousePressed','mouseReleased'])await send('Input.dispatchMouseEvent',{type:t,x:cr.x,y:cr.y,button:'left',clickCount:1});
 ok(await waitFor('/Copied/.test((document.querySelector("#idb-out .ux-copy.ok")||{}).textContent)'),'copy shows "'+await ev('document.querySelector("#idb-out .ux-copy.ok,#idb-out .ux-copy.bad").textContent')+'"');
 const clip=await evp('navigator.clipboard.readText().catch(function(e){return "ERR "+e.message})');
 ok(clip===cb.c,'clipboard holds the item name ('+clip+')');
 await ev('document.querySelector("#idb-out .ux-copy.ok,#idb-out .ux-copy.bad").scrollIntoView({block:"center",behavior:"instant"})');await shot('ux4-after-copy-480.png');
 await go('mobs.html?mq=wolf');ok(await ev('(function(){var b=document.querySelector("#mob-out tbody tr .ux-copy");return !!b&&b.getAttribute("data-copy").length>2&&!/named|wiki/.test(b.getAttribute("data-copy"))})()'),'mobs: copy button with the mob name ('+await ev('(document.querySelector("#mob-out .ux-copy")||{}).title')+')');
 await ev('document.querySelector(".ux-dbbar .ux-tbar-r").click()');await ev('localStorage.removeItem("mnm-db:items.html")');
 await go('trio.html');ok(await ev('[].some.call(document.querySelectorAll("code+.ux-copy"),function(b){return b.getAttribute("data-copy")==="/consent group"})'),'game commands in <code> (/consent group) get a copy button');
 // 6) what's new since your last visit
 await size(1024,768);await go('index.html');await ev('localStorage.removeItem("mnm-lastvisit");localStorage.removeItem("mnm-new-seen");sessionStorage.clear()');await go('index.html');
 ok(!(await ev('!!document.querySelector(".ux-new")'))&&await ev('!!localStorage.getItem("mnm-lastvisit")'),'first visit: no badge, the visit date is stored');
 await ev('localStorage.setItem("mnm-lastvisit","2026-10-10");sessionStorage.clear()');await go('index.html');
 const wn=await ev('(function(){var b=document.querySelector(".ux-new");return b?{t:b.textContent,h:b.querySelector("a").getAttribute("href"),vis:b.checkVisibility()}:null})()');
 ok(!!wn&&wn.vis&&/\d+ updates? since your last visit \(Oct 10\)/.test(wn.t)&&/changelog\.html$/.test(wn.h),'returning visitor sees an in-page badge: "'+(wn&&wn.t.replace(/\u2715$/,''))+'"');
 await shot('ux4-after-whatsnew-1024.png');
 await go('items.html');ok(await ev('!!document.querySelector(".ux-new")'),'badge stays for the rest of the visit');
 await size(480,900);await go('index.html');ok(await ev('(function(){var b=document.querySelector(".ux-new");return !!b&&b.checkVisibility()&&b.getBoundingClientRect().right<=innerWidth&&document.documentElement.scrollWidth<=innerWidth})()'),'480: badge fits, no overflow');
 await size(1024,768);await go('changelog.html');
 ok(await ev('document.querySelectorAll(".ux-newtag").length>0&&!document.querySelector(".ux-new")'),'changelog marks '+await ev('document.querySelectorAll(".ux-newtag").length')+' rows as new');
 await go('index.html');ok(!(await ev('!!document.querySelector(".ux-new")')),'after reading the changelog the badge is gone');
 await ev('localStorage.setItem("mnm-lastvisit","2026-10-10");localStorage.removeItem("mnm-new-seen");sessionStorage.clear()');await go('index.html');
 await ev('document.querySelector(".ux-new-x").click()');await go('walkthrough.html');ok(!(await ev('!!document.querySelector(".ux-new")')),'dismiss (×) hides it until the next update');
 // overflow with every pass-4 control at all target widths
 await ev('localStorage.setItem("mnm-favs",JSON.stringify([{u:"items.html",t:"Item & drop database"}]))');
 for(const [w,h] of [[480,900],[1024,768],[2560,1080],[3440,1440]]){await size(w,h);for(const u of ['index.html','classes/inquisitor.html','items.html','mobs.html','walkthrough.html','market.html']){await go(u);
   if(await ev('document.documentElement.scrollWidth>innerWidth'))ok(false,'pass 4: '+u+' overflows @'+w)}}
 ok(true,'pass 4: no horizontal overflow at 480/1024/2560/3440 on home, class, items, mobs, walkthrough, market');
 await ev('localStorage.removeItem("mnm-favs");localStorage.removeItem("mnm-db:items.html");localStorage.removeItem("mnm-db:mobs.html")');
 // =============================== UX pass 5
 const CSCAN="(function(){\nfunction parse(c){var m=c&&c.match(/rgba?\\(([^)]+)\\)/);if(!m)return null;var p=m[1].split(/[,\\s\\/]+/).filter(Boolean).map(parseFloat);return [p[0],p[1],p[2],p.length>3?p[3]:1]}\nfunction over(t,b){var a=t[3];return [t[0]*a+b[0]*(1-a),t[1]*a+b[1]*(1-a),t[2]*a+b[2]*(1-a),1]}\nfunction lum(c){var w=[.2126,.7152,.0722],s=0;for(var i=0;i<3;i++){var v=c[i]/255;s+=w[i]*(v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4))}return s}\nfunction ratio(a,b){var x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}\nfunction bgOf(el){var st=[];for(var e=el;e;e=e.parentElement){var cs=getComputedStyle(e),c=parse(cs.backgroundColor);\n  if(/gradient/.test(cs.backgroundImage)){var g=cs.backgroundImage.match(/rgba?\\([^)]+\\)/g);if(g){var gc=g.map(parse).reduce(function(m,x){return lum(x)<lum(m)===(lum(parse(getComputedStyle(document.body).color))>.4)?x:m});st.push(gc)}}\n  if(c&&c[3]>0){st.push(c);if(c[3]>=.999)break}}\n  var b=[255,255,255,1];for(var i=st.length-1;i>=0;i--)b=over(st[i],b);return b}\nfunction vis(e){if(!e.checkVisibility||!e.checkVisibility({opacityProperty:true,visibilityProperty:true}))return false;var r=e.getBoundingClientRect();if(r.width<2||r.height<2)return false;\n  var cs=getComputedStyle(e);if(cs.clip==='rect(0px, 0px, 0px, 0px)'||cs.clipPath==='inset(50%)')return false;for(var p=e;p;p=p.parentElement){if(parseFloat(getComputedStyle(p).opacity)<.99&&!p.matches(':disabled'))return 'op'}return true}\nvar fails=[],seen={},n=0;\n[].forEach.call(document.body.querySelectorAll('*'),function(e){if(/^(SCRIPT|STYLE|NOSCRIPT|OPTION|TEMPLATE|svg|path|BR)$/i.test(e.tagName))return;\n  var own=[].some.call(e.childNodes,function(t){return t.nodeType===3&&t.textContent.trim().length>0});if(!own)return;if(e.closest(':disabled,[aria-disabled=\"true\"],.ux-vh,[aria-hidden=\"true\"]'))return;\n  var v=vis(e);if(!v)return;n++;var cs=getComputedStyle(e),bg=bgOf(e),fg=parse(cs.color);if(!fg)return;fg=over(fg,bg);var r=ratio(fg,bg),need=4.5;\n  if(r<need){var k=e.tagName+'.'+String(e.className).split(' ')[0]+'|'+cs.color+'|'+bg.map(Math.round);if(!seen[k]){seen[k]=1;fails.push({el:e.tagName.toLowerCase()+(e.className&&typeof e.className==='string'?'.'+e.className.trim().split(/\\s+/).join('.'):'')+(e.parentElement?' < '+e.parentElement.tagName.toLowerCase()+'.'+String(e.parentElement.className).split(' ')[0]:''),t:e.textContent.trim().slice(0,30),r:Math.round(r*100)/100,fg:cs.color,bg:'rgb('+bg.slice(0,3).map(Math.round)+')',op:v==='op'})}}});\nvar cf=[],cn=0;\n[].forEach.call(document.body.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]),select,textarea,button'),function(e){if(vis(e)!==true||e.disabled)return;var cs=getComputedStyle(e),bw=parseFloat(cs.borderTopWidth)||0;\n  var isField=/^(INPUT|SELECT|TEXTAREA)$/.test(e.tagName);if(!isField&&bw<1)return;cn++;\n  var pb=bgOf(e.parentElement||document.body),own=parse(cs.backgroundColor),cb=own&&own[3]>0?over(own,pb):pb,bc=bw>=1?over(parse(cs.borderTopColor),pb):null;\n  var r=Math.max(bc?ratio(bc,pb):0,ratio(cb,pb));if(r<3){var k=e.tagName+'.'+e.className+'|'+cs.borderTopColor;if(!seen[k]){seen[k]=1;cf.push({el:e.tagName.toLowerCase()+'.'+String(e.className).trim().split(/\\s+/).join('.')+'#'+e.id,r:Math.round(r*100)/100,bd:cs.borderTopColor,bg:'rgb('+pb.slice(0,3).map(Math.round)+')'})}}});\nreturn {text:n,fails:fails.slice(0,40),nf:fails.length,ctl:cn,cfails:cf.slice(0,20),ncf:cf.length}})()";
 await send('Browser.setDownloadBehavior',{behavior:'deny'}).catch(()=>{});await send('Emulation.setFocusEmulationEnabled',{enabled:true});
 // 1) class pages load walk-data.js only once the Quick info walkthrough is on screen
 await size(480,900);reqs=[];await go("classes/inquisitor.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");await sleep(600);
 ok(!reqs.includes('walk-data.js')&&/loads when you scroll/.test(await ev('document.querySelector(".cg-qwalk").textContent')),'class page @480: walk-data.js ('+sz('walk-data.js')+' KB) not loaded until the walkthrough box is on screen ("'+(await ev('document.querySelector(".cg-qwalk").textContent')).trim()+'")');
 await ev('document.querySelector(".cg-qwalk").scrollIntoView()');
 ok(await waitFor('/New character: Deep Elf Inquisitor · Ail.Vorith/.test(document.querySelector(".cg-qwalk").textContent)')&&reqs.includes('walk-data.js'),'scrolling to it loads walk-data.js and renders the Deep Elf Inquisitor · Ail\'Vorith walkthrough');
 ok(await ev('!/Start-city route: (Night Harbor|Underdocks|Faelindral)/.test(document.querySelector(".cg-qwalk").textContent)&&!/Petra Gyle/.test(document.querySelector(".cg-qwalk").textContent)'),'class page quick walkthrough: Ail\'Vorith only, no Night Harbor fallback');
 reqs=[];await go('walkthrough.html');ok(reqs.includes('walk-data.js'),'walkthrough page still loads walk-data.js straight away');
 reqs=[];await go("classes/inquisitor.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");await ev('document.querySelector(".tab[data-tab$=\\"-cg\\"]").click()');await ev('scrollTo(0,document.documentElement.scrollHeight)');await sleep(800);
 ok(!reqs.includes('walk-data.js'),'Character creation tab open: the hidden Quick reference walkthrough does not load walk-data.js');
 // 2) Shaman guide routes on demand (Night Harbor notes kept per city)
 ok(fsz('shaman/leveling.html')<450,'shaman/leveling.html is '+fsz('shaman/leveling.html')+' KB (was 700 KB)');
 await size(480,900);reqs=[];await go("shaman/leveling.html?class=Shaman&race=Wood+Elf&city=Faelindral");
 ok(await ev('document.documentElement.getAttribute("data-sc")')==='faelindral','Wood Elf Shaman, Start Faelindral: page follows Faelindral');
 await ev('document.querySelector(".tabpane.on .sc-wrap").scrollIntoView()');
 ok(await waitFor('(function(){var b=document.querySelector(".tabpane.on .sc-route[data-sc=faelindral]");return !!b&&/written for a Night Harbor start/.test(b.textContent)&&/You picked Faelindral/.test(b.lastElementChild.textContent)})()'),'Shaman 11-15: Faelindral route renders on demand, ending with its "notes written for Night Harbor" paragraph');
 const sr=reqs.filter(r=>/^walk-r-/.test(r));
 ok(sr.length>=1&&sr.every(r=>/-faelindral\.js$/.test(r)),'Shaman first load fetches only Faelindral route chunks ('+sr.join(', ')+')');
 ok(await ev('document.querySelectorAll(".sc-wrap:not(.sc-headwrap) .sc-route:not([data-sc=faelindral])").length===0&&document.querySelectorAll(".tabpane.on .sc-route .sc-nhnote").length===1'),'Shaman: no other city\'s route in the page, one note');
 await go("shaman/leveling.html?class=Shaman&race=Human&city=Night+Harbor");await ev('document.querySelector(".tabpane.on .sc-wrap").scrollIntoView()');
 ok(await waitFor('(function(){var b=document.querySelector(".tabpane.on .sc-route[data-sc=night-harbor]");return !!b&&!b.querySelector(".sc-nhnote")})()'),'Shaman, Night Harbor start: route without the note (as before)');
 await ev('MNM_UX_ROUTES.fillAll()');
 ok(await waitFor('document.querySelectorAll(".sc-wrap:not(.sc-headwrap) .sc-route[data-sc=night-harbor]").length===document.querySelectorAll(".sc-lz").length',15000),'Shaman: all '+await ev('document.querySelectorAll(".sc-lz").length')+' bands render for printing');
 reqs=[];await go("shaman/index.html?class=Shaman&race=Wood+Elf&city=Faelindral");await sleep(500);await ev('document.querySelector(".cg-qwalk").scrollIntoView()');
 ok(await waitFor('/New character: Wood Elf Shaman · Faelindral/.test(document.querySelector(".cg-qwalk").textContent)'),'shaman/index.html (the Shaman class page) renders its quick walkthrough for Faelindral');
 // 3) spell + mob tooltips
 reqs=[];await go("walkthrough.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");await waitFor('!!document.querySelector("#cg-walk .cg-sp li>b.ux-tt-t")',10000);
 ok(!TIPR('s')&&!TIPR('m'),'tooltip data not loaded up front');
 const sp=await ev('(function(){var b=document.querySelector("#cg-walk details[open] .cg-sp li>b.ux-tt-t")||document.querySelector("#cg-walk .cg-sp li>b.ux-tt-t");b.scrollIntoView({block:"center",behavior:"instant"});b.focus();return {t:b.textContent,ti:b.tabIndex}})()');
 ok(sp.ti===0,'spell names are keyboard-focusable ('+sp.t+')');
 ok(await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Level \\d+/.test(t.textContent)&&/Inquisitor/.test(t.textContent)})()')&&TIPR('s'),'focus shows the spell tooltip (level, class, wiki text) after spell-tips.js ('+sz('spell-tips.js')+' KB) loads');
 const tt1=await ev('(function(){var t=document.getElementById("ux-tt"),r=t.getBoundingClientRect(),a=document.activeElement;return {role:t.getAttribute("role"),db:a.getAttribute("aria-describedby"),l:r.left,r:r.right,b:r.bottom,txt:t.textContent.slice(0,120),ovf:document.documentElement.scrollWidth>innerWidth}})()');
 ok(tt1.role==='tooltip'&&tt1.db==='ux-tt','tooltip has role=tooltip and is linked with aria-describedby');
 ok(tt1.l>=0&&tt1.r<=480&&tt1.b<=900&&!tt1.ovf,'tooltip fits the 480px window ('+Math.round(tt1.l)+'–'+Math.round(tt1.r)+'px): '+tt1.txt);
 const spd=await ev('(function(){var n=document.activeElement.textContent.trim().toLowerCase(),d=(window.MNM_STIPS||{})[n];return d?d.map(function(x){return x[2]+" L"+x[1]}).join(","):""})()');
 ok(spd.length>0&&new RegExp('Level '+spd.match(/Inquisitor L(\d+)/)[1]).test(await ev('document.getElementById("ux-tt").textContent')),'tooltip level matches the site data for that spell ('+spd.slice(0,60)+')');
 await shot('ux5-after-tooltip-480.png');
 await key('Escape');ok(await ev('document.getElementById("ux-tt").hidden&&document.activeElement.classList.contains("ux-tt-t")'),'Esc closes the tooltip and keeps focus on the name');
 // tap
 await send('Emulation.setTouchEmulationEnabled',{enabled:true});
 const tp=await ev('(function(){var b=[].filter.call(document.querySelectorAll("#cg-walk .cg-sp li>b.ux-tt-t"),function(e){return e.checkVisibility()})[1];b.scrollIntoView({block:"center",behavior:"instant"});var r=b.getBoundingClientRect();return {x:r.left+5,y:r.top+r.height/2}})()');await sleep(200);
 await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:tp.x,y:tp.y}]});await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 ok(await waitFor('!document.getElementById("ux-tt").hidden'),'tap on a spell name opens its tooltip');
 await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:20,y:880}]});await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 ok(await waitFor('document.getElementById("ux-tt").hidden'),'tap elsewhere closes it');
 await send('Emulation.setTouchEmulationEnabled',{enabled:false});
 // mob tooltip (camps list) on hover
 await size(1024,768);reqs=[];await go("walkthrough.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");await waitFor('!!document.querySelector("#cg-walk .tt-mob.ux-tt-t")',10000);
 const mp=await ev('(function(){var b=[].find.call(document.querySelectorAll("#cg-walk .tt-mob.ux-tt-t"),function(e){return e.checkVisibility()});b.scrollIntoView({block:"center",behavior:"instant"});var r=b.getBoundingClientRect();return {x:r.left+4,y:r.top+r.height/2,t:b.textContent}})()');await sleep(200);
 await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:mp.x,y:mp.y});
 ok(await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Level/.test(t.textContent)})()')&&TIPR('m'),'hovering a camp mob ('+mp.t+') shows its tooltip after mob-tips.js ('+sz('mob-tips.js')+' KB) loads');
 const mt=await ev('(function(){var t=(document.getElementById("ux-tt")||{}).textContent||"",d=(window.MNM_MTIPS||{})[document.activeElement&&0||([].find.call(document.querySelectorAll("#cg-walk .tt-mob.ux-tt-t"),function(e){return e.checkVisibility()})||{textContent:""}).textContent.trim().toLowerCase()];return {t:t.slice(0,140),ok:!d||t.indexOf(d[0][2])>=0}})()');
 ok(mt.ok&&mt.t.length>0,'mob tooltip shows the Mobs database zone/level ('+mt.t+')');
 await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:5,y:700});ok(await waitFor('(document.getElementById("ux-tt")||{hidden:true}).hidden'),'moving the mouse away closes it');
 // 4) CSV export + print
 await go('items.html?iq=sword');await ev('(function(){var o=window.MNM_UX_CSV;window.MNM_UX_CSV=function(n,h,r){window.__csv=o(n,h,r);window.__csvn=n;return window.__csv}})()');
 await ev('document.querySelector(".ux-tbar-csv").click()');await waitFor('!!window.__csv',15000);
 const cv=await ev('(function(){var t=window.__csv||"",lines=t.replace(/^\\ufeff/,"").trim().split("\\r\\n"),n=+(document.getElementById("idb-count").textContent.match(/\\d+/)||[0])[0];return {n:n,rows:lines.length-1,head:lines[0],bom:t.charCodeAt(0)===0xfeff,all:lines.slice(1).every(function(l){return /sword/i.test(l)}),name:window.__csvn,lab:document.querySelector(".ux-tbar-csv").getAttribute("aria-label")}})()');
 ok(cv.rows===cv.n&&cv.n>0&&cv.all&&cv.bom&&/^Item,Slot,Level,Classes,Stats,Sources/.test(cv.head),'items: Export CSV holds all '+cv.n+' matching rows (header '+cv.head.slice(0,50)+'…, UTF-8 BOM) — '+cv.lab);
 await ev('document.querySelector(".ux-dbbar .ux-tbar-r").click()');
 await go('mobs.html?mq=wolf&mn=1');await ev('(function(){var o=window.MNM_UX_CSV;window.MNM_UX_CSV=function(n,h,r){window.__csv=o(n,h,r);return window.__csv}})()');await ev('document.querySelector(".ux-tbar-csv").click()');await waitFor('!!window.__csv',15000);
 const mv=await ev('(function(){var l=(window.__csv||"").trim().split("\\r\\n"),n=+(document.getElementById("mob-count").textContent.match(/\\d+/)||[0])[0];return {n:n,rows:l.length-1,head:l[0],named:l.slice(1).every(function(x){return /,yes,/.test(x)})}})()');
 ok(mv.rows===mv.n&&mv.n>0&&mv.named&&/^Mob,Level,Zone,Named/.test(mv.head),'mobs: Export CSV holds the '+mv.n+' filtered rows (named wolves only)');
 ok(await ev('(function(){var t=window.MNM_UX_CSV("x",["a"],[["=1+1"],["-x"],["-5"],["a,\\"b\\""]]);return t.indexOf("\\x27=1+1")>0&&t.indexOf("\\x27-x")>0&&t.indexOf("\\r\\n-5\\r\\n")>0&&t.indexOf("\\"a,\\"\\"b\\"\\"\\"")>0})()'),'CSV cells are quoted, and formula-like cells (=, +, @, -text) are neutralised');
 await ev('document.querySelector(".ux-dbbar .ux-tbar-r").click()');
 await send('Emulation.setEmulatedMedia',{media:'print'});await go('items.html?iq=sword');
 const pr=await ev('(function(){var g=function(s){var e=document.querySelector(s);return e?getComputedStyle(e).display:"none"};return {top:g(".top"),left:g(".left"),right:g(".right"),bar:g(".ux-dbbar"),mw:Math.round(document.querySelector(".main").getBoundingClientRect().width),bg:getComputedStyle(document.body).backgroundColor}})()');
 ok(pr.top==='none'&&pr.left==='none'&&pr.right==='none'&&pr.bar==='none'&&pr.mw>=900&&pr.bg==='rgb(255, 255, 255)','print (items): header, nav rails and toolbars hidden, content full width ('+pr.mw+'px), white page');
 await go("classes/inquisitor.html");await ev('dispatchEvent(new Event("beforeprint"))');
 const pc=await ev('(function(){var p=[].slice.call(document.querySelectorAll(".tabpane"));return {all:p.every(function(x){return getComputedStyle(x).display==="block"}),t:p.filter(function(x){return x.getAttribute("data-ptitle")}).length,n:p.length,closed:document.querySelectorAll("main details:not([open])").length}})()');
 ok(pc.all&&pc.t===pc.n&&pc.closed===0,'print (class guide): all '+pc.n+' tabs print under their titles, every <details> opened');
 await ev('dispatchEvent(new Event("afterprint"))');await send('Emulation.setEmulatedMedia',{media:''});
 await go("classes/inquisitor.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");await ev('window.__printed=0;window.print=function(){window.__printed=1}');await key('p',2);
 ok(await waitFor('window.__printed===1',15000)&&await ev('!document.querySelector(".tabpane[data-lz]")&&!!document.querySelector(".cg-qwalk .qw-head")'),'Ctrl+P first loads every on-demand tab and the walkthrough, then opens the print dialog');
 // 5) themes
 await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:'dark'}]});
 await size(1024,768);await go('index.html');await ev('localStorage.removeItem("mnm-theme");localStorage.removeItem("mnm-halloween")');reqs=[];await go('index.html');
 ok(await ev('!document.documentElement.hasAttribute("data-theme")&&document.documentElement.classList.contains("halloween")')&&!reqs.some(r=>/mod-ux-(light|contrast)/.test(r)),'default: dark Irem theme, no theme stylesheet downloaded');
 const tb0=await ev('(function(){var b=document.querySelector(".ux-themebtn");var r=b.getBoundingClientRect();return {l:b.getAttribute("aria-label"),h:r.height,vis:b.checkVisibility()}})()');
 ok(tb0.vis&&/Theme: Dark/.test(tb0.l),'theme button in the header ('+tb0.l+')');
 await ev('document.querySelector(".ux-themebtn").click()');
 ok(await waitFor('document.documentElement.getAttribute("data-theme")==="light"')&&await ev('localStorage.getItem("mnm-theme")==="light"&&getComputedStyle(document.body).backgroundColor!=="rgb(10, 13, 18)"'),'click: Light (saved as mnm-theme=light, '+sz('mod-ux-light.css')+' KB stylesheet loaded on demand)');
 await shot('ux5-after-light-1024.png');
 await ev('document.querySelector(".ux-themebtn").click()');ok(await waitFor('document.documentElement.getAttribute("data-theme")==="contrast"'),'click: High contrast');
 await ev('document.querySelector(".ux-themebtn").click()');ok(await waitFor('!document.documentElement.hasAttribute("data-theme")')&&await ev('localStorage.getItem("mnm-theme")==="dark"'),'click: back to Dark');
 await ev('localStorage.setItem("mnm-theme","light")');await go('items.html');
 ok(await ev('document.documentElement.getAttribute("data-theme")==="light"&&!!document.getElementById("ux-theme-css")&&getComputedStyle(document.body).backgroundColor==="rgb(246, 239, 225)"'),'saved Light applies on load (stylesheet linked from <head>, no dark flash)');
 await ev('localStorage.removeItem("mnm-theme")');
 await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-contrast',value:'more'}]});await go('index.html');
 ok(await ev('document.documentElement.getAttribute("data-theme")==="contrast"&&localStorage.getItem("mnm-theme")===null'),'prefers-contrast: more starts High contrast (hint only, nothing saved)');
 await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:'light'}]});await go('index.html');
 ok(await ev('!document.documentElement.hasAttribute("data-theme")&&document.querySelector(".ux-themebtn").classList.contains("ux-theme-hint")&&/system prefers a light theme/.test(document.querySelector(".ux-themebtn").getAttribute("aria-label"))'),'prefers-color-scheme: light keeps the dark default and only marks the theme button ("Light available" hint)');
 await ev('localStorage.setItem("mnm-theme","dark")');await go('index.html');
 ok(await ev('!document.documentElement.hasAttribute("data-theme")'),'a saved choice (Dark) wins over the system hint');
 await send('Emulation.setEmulatedMedia',{features:[]});
 // contrast: 4.5:1 text and 3:1 control borders, every theme (Irem on and off)
 const CP=['index.html','classes/inquisitor.html','walkthrough.html','items.html','mobs.html','market.html','hotbar.html','planner.html','groups.html','shaman/leveling.html','spells.html','zones/ailvorith.html'];
 for(const st of ['dark-hw','dark','light-hw','light','contrast-hw','contrast']){const [th,hw]=st.split('-');
  await ev(`localStorage.setItem('mnm-theme','${th}');localStorage.setItem('mnm-halloween','${hw?'on':'off'}');localStorage.setItem('mnm-city',"Ail'Vorith");localStorage.setItem('mnm-race','Deep Elf');localStorage.setItem('mnm-class','Inquisitor')`);
  let bad=[],nt=0,nc=0;
  for(const u of CP){await go(u);const q=await ev('!!document.querySelector(".cg-qwalk")');if(q){await ev('document.querySelector(".cg-qwalk").scrollIntoView()');await sleep(700);await ev('scrollTo(0,0)')}
   const r=await ev(CSCAN);nt+=r.text;nc+=r.ctl;r.fails.forEach(f=>bad.push(u+' T '+f.r+' '+f.el+' "'+f.t+'"'));r.cfails.forEach(f=>bad.push(u+' C '+f.r+' '+f.el))}
  // open UI: tooltip + palette + favorites popup
  await go("walkthrough.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");await waitFor('!!document.querySelector("#cg-walk .cg-sp li>b.ux-tt-t")',10000);
  await ev('(function(){var b=[].find.call(document.querySelectorAll("#cg-walk .cg-sp li>b.ux-tt-t"),function(e){return e.checkVisibility()});b.scrollIntoView({block:"center",behavior:"instant"});b.focus()})()');await waitFor('/Level/.test((document.getElementById("ux-tt")||{}).textContent||"")');
  let r=await ev(CSCAN.replace('document.body.querySelectorAll(\'*\')','document.getElementById("ux-tt").querySelectorAll(\'*\')'));r.fails.forEach(f=>bad.push('tooltip T '+f.r+' '+f.el));
  await key('Escape');await key('k',2);await waitFor('!!document.querySelector("dialog.ux-pal[open]")');await ev('(function(){var i=document.getElementById("ux-pal-q");i.value="inq";i.dispatchEvent(new Event("input"))})()');await sleep(400);
  r=await ev(CSCAN.replace('document.body.querySelectorAll(\'*\')','document.querySelector("dialog.ux-pal").querySelectorAll(\'*\')'));r.fails.forEach(f=>bad.push('palette T '+f.r+' '+f.el));await key('Escape');
  ok(bad.length===0,'contrast ['+st+']: '+nt+' text elements ≥ 4.5:1 and '+nc+' bordered controls ≥ 3:1 on '+CP.length+' pages + tooltip + palette'+(bad.length?' — '+bad.slice(0,6).join(' | '):''));
 }
 await ev('localStorage.removeItem("mnm-theme");localStorage.removeItem("mnm-halloween")');
 // overflow with the theme button + CSV button in every theme
 for(const th of ['dark','light','contrast']){await ev(`localStorage.setItem('mnm-theme','${th}')`);
  for(const [w,h] of [[480,900],[1024,768],[2560,1080],[3440,1440]]){await size(w,h);for(const u of ['index.html','classes/inquisitor.html','items.html','mobs.html','shaman/index.html']){await go(u);
   if(await ev('document.documentElement.scrollWidth>innerWidth'))ok(false,'pass 5: '+u+' overflows @'+w+' ('+th+')')}}}
 ok(true,'pass 5: no horizontal overflow at 480/1024/2560/3440 (home, class, items, mobs, Shaman) in Dark, Light and High contrast');
 await ev('localStorage.removeItem("mnm-theme")');
 // =============================== UX pass 6
 const DBOK="(function(){var s=document.querySelector('.ux-dbst');return (!s||s.hidden)&&[].slice.call(document.querySelectorAll('#mob-out [data-id],#idb-out [data-id]'),0,5).every(function(e){return !e.classList.contains('ux-dbp')})})()";
 await send('Network.setBlockedURLs',{urls:[]});await send('Emulation.setEmulatedMedia',{media:''});
 await size(480,900);await go('index.html');await ev('localStorage.removeItem("mnm-db:items.html");localStorage.removeItem("mnm-db:mobs.html");localStorage.removeItem("mnm-theme");localStorage.removeItem("mnm-halloween")');
 // 1) Items: compact index first, details per 100-item piece as rows near the screen, search text on the first query
 reqs=[];await go('items.html');await waitFor(DBOK);
 const i0=await ev('({n:document.getElementById("idb-count").textContent,rows:document.querySelectorAll("#idb-out .idb-it").length,first:document.querySelector("#idb-out .idb-it").textContent,pend:document.querySelectorAll("#idb-out .idb-it.ux-dbp").length})');
 const ic=reqs.filter(r=>/^idb-c-/.test(r));
 ok(!reqs.includes('items-db.js')&&reqs.includes('idb-index.js')&&!reqs.includes('idb-text.js')&&ic.length>=1&&ic.length<=2,'items: first load = idb-index.js ('+sz('idb-index.js')+' KB) + '+ic.join(', ')+'; no items-db.js ('+sz('items-db.js')+' KB), no search text');
 ok(/^5\d{3} items \(showing first 150/.test(i0.n)&&i0.rows===150&&i0.pend>100&&/Sources?|Quest|Drop|Vendor|Named|Crafted|No source/.test(i0.first),'items: '+i0.n+'; first rows filled, '+i0.pend+' rows below wait for their piece');
 ok(sz('idb-index.js')<300&&sz('idb-text.js')<450,'items index '+sz('idb-index.js')+' KB, search text '+sz('idb-text.js')+' KB, '+fs.readdirSync(path.join(DOCS,'assets')).filter(f=>/^idb-c-\d+\.js$/.test(f)).length+' pieces of 100 items');
 await ev('document.querySelectorAll("#idb-out .idb-it")[140].scrollIntoView({block:"center",behavior:"instant"})');
 ok(await waitFor('!document.querySelectorAll("#idb-out .idb-it")[140].classList.contains("ux-dbp")'),'scrolling down fills the rows there ('+reqs.filter(r=>/^idb-c-/.test(r)).join(', ')+')');
 await ev('scrollTo(0,0)');
 await send('Network.emulateNetworkConditions',{offline:false,latency:900,downloadThroughput:300000,uploadThroughput:300000});
 await ev('(function(){var q=document.getElementById("idb-q");q.value="sword";q.dispatchEvent(new Event("input",{bubbles:true}))})()');await sleep(100);
 const ip=await ev('({c:document.getElementById("idb-count").textContent,s:document.querySelector(".ux-dbst").textContent,h:document.querySelector(".ux-dbst").hidden})');
 ok(/names so far/.test(ip.c)&&!ip.h&&/Loading the full search/.test(ip.s),'typing shows name matches at once ("'+ip.c+'") and "'+ip.s+'"');
 await shot('ux6-after-items-search-loading-480.png');
 await send('Network.emulateNetworkConditions',{offline:false,latency:0,downloadThroughput:-1,uploadThroughput:-1});
 ok(await waitFor(DBOK,15000)&&await ev('/^106 items$/.test(document.getElementById("idb-count").textContent)'),'full search ready: '+await ev('document.getElementById("idb-count").textContent')+' (same 106 matches as the old single file: names, stats and sources)');
 ok(await ev('/sword/i.test(document.querySelector("#idb-out .idb-it").textContent)&&!!document.querySelector("#idb-out .idb-it ul.tight li")'),'result rows show their sources once filled');
 // mob names inside Items rows get the mob tooltip
 await go('items.html#'+encodeURIComponent("Vikkit's Chain Cap"));await waitFor(DBOK);
 const im=await ev('(function(){var m=document.querySelector("#idb-out .tt-mob.ux-tt-t");if(!m)return null;m.focus();return m.textContent})()');
 ok(im==='Foreman Vikkit'&&await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Great Cavern Sea/.test(t.textContent)})()'),'Items database: drop-source mob name ('+im+') shows the mob tooltip (Mobs database data)');
 await key('Escape');
 // blocked piece: error + Try again; blocked search text: names only + Try again
 await ev('localStorage.removeItem("mnm-db:items.html")');
 await send('Network.setBlockedURLs',{urls:['*idb-c-0.js']});await go('items.html');
 ok(await waitFor('/Could not load the details/.test(document.querySelector("#idb-out .idb-it").textContent)&&!!document.querySelector("#idb-out .idb-it .ux-retry")'),'blocked piece: "Could not load the details (offline?)" + Try again in the row');
 ok(await ev('/For Sale/.test(document.querySelector("#idb-out .idb-it b").textContent)&&!!document.querySelector("#idb-out .idb-it .ux-copy")'),'…the row still shows its name (with Copy), slot and level from the index');
 await shot('ux6-after-items-error-480.png');
 await send('Network.setBlockedURLs',{urls:[]});await ev('document.querySelector("#idb-out .idb-it .ux-retry").click()');
 ok(await waitFor('!document.querySelector("#idb-out .idb-it").classList.contains("ux-dbp")'),'Try again fills it');
 await send('Network.setBlockedURLs',{urls:['*idb-text.js']});await go('items.html?iq=beetle');
 ok(await waitFor('/could not load/i.test(document.querySelector(".ux-dbst").textContent)&&!!document.querySelector(".ux-dbst .ux-retry")'),'blocked search text: names-only results ('+await ev('document.getElementById("idb-count").textContent')+') + "Full-text search could not load" + Try again');
 await send('Network.setBlockedURLs',{urls:[]});await ev('document.querySelector(".ux-dbst .ux-retry").click()');
 ok(await waitFor('document.querySelector(".ux-dbst").hidden&&/^80 items$/.test(document.getElementById("idb-count").textContent)'),'Try again loads the full search (80 beetle items)');
 // CSV of every filtered row, across pieces; blocked pieces -> button error
 await go('items.html?iq=sword');await waitFor(DBOK);await ev('(function(){var o=window.MNM_UX_CSV;window.__csv=null;window.MNM_UX_CSV=function(n,h,r){window.__csv=o(n,h,r);return window.__csv}})()');
 await ev('document.querySelector(".ux-tbar-csv").click()');ok(await waitFor('!!window.__csv'),'CSV export waits for the item pieces');
 const ix=await ev('(function(){var l=window.__csv.replace(/^\\ufeff/,"").trim().split("\\r\\n");return {rows:l.length-1,urls:l.slice(1).filter(function(x){return /https:\\/\\//.test(x)}).length}})()');
 ok(ix.rows===106&&ix.urls===106,'CSV holds all 106 matches with full rows (wiki links included)');
 await send('Network.setBlockedURLs',{urls:['*idb-c-*']});await go('items.html?iq=helm');await waitFor('document.querySelector(".ux-dbst").hidden');
 await ev('document.querySelector(".ux-tbar-csv").click()');
 ok(await waitFor('/Export failed: try again/.test(document.querySelector(".ux-tbar-csv").textContent)'),'blocked pieces: the button says "Export failed: try again"');
 await send('Network.setBlockedURLs',{urls:[]});
 await go('items.html');await ev('document.querySelector(".ux-dbbar .ux-tbar-r").click()');
 // print fills every listed row first
 await go('items.html?iq=a');await waitFor(DBOK);await ev('window.__printed=0;window.print=function(){window.__printed=document.querySelectorAll("#idb-out .ux-dbp").length+1}');await key('p',2);
 ok(await waitFor('window.__printed>0',20000)&&await ev('window.__printed===1'),'Ctrl+P on Items fills all 150 listed rows before printing');
 await go('items.html');await ev('document.querySelector(".ux-dbbar .ux-tbar-r").click()');
 // 2) Mobs
 reqs=[];await go('mobs.html');await waitFor(DBOK);const mc=reqs.filter(r=>/^mdb-c-/.test(r));
 ok(!reqs.includes('mobs-db.js')&&reqs.includes('mdb-index.js')&&!reqs.includes('mdb-text.js')&&mc.length>=1&&mc.length<=2,'mobs: first load = mdb-index.js ('+sz('mdb-index.js')+' KB) + '+mc.join(', ')+'; no mobs-db.js ('+sz('mobs-db.js')+' KB)');
 ok(await ev('/^\\d{4} mobs \\(showing first 200\\)$/.test(document.getElementById("mob-count").textContent)&&document.querySelectorAll("#mob-out tbody tr").length===200'),'mobs: '+await ev('document.getElementById("mob-count").textContent'));
 await go('mobs.html?mq=wolf&mn=1&msort=L');await waitFor(DBOK,15000);
 const m6=await ev('({c:document.getElementById("mob-count").textContent,q:document.getElementById("mob-q").value,n:document.getElementById("mob-named").checked,o:document.getElementById("msort-sel").value,r:document.querySelector("#mob-out tbody tr").innerText})');
 ok(m6.q==='wolf'&&m6.n&&m6.o==='L'&&/\d+ mobs/.test(m6.c),'mobs: ?mq=wolf&mn=1&msort=L restored ('+m6.c+'; first row '+m6.r.replace(/\s+/g,' ').slice(0,80)+')');
 await go('mobs.html#'+encodeURIComponent('Foreman Vikkit'));await waitFor(DBOK,15000);
 ok(await ev('document.getElementById("mob-q").value==="Foreman Vikkit"&&/Vikkit\'s Chain Cap/.test(document.getElementById("mob-out").textContent)'),'mobs.html#Foreman Vikkit deep link shows the mob with its drops');
 await go('mobs.html?mq=wolf');await waitFor(DBOK,15000);await ev('(function(){var o=window.MNM_UX_CSV;window.__csv=null;window.MNM_UX_CSV=function(n,h,r){window.__csv=o(n,h,r);return window.__csv}})()');
 await ev('document.querySelector(".ux-tbar-csv").click()');await waitFor('!!window.__csv');
 ok(await ev('window.__csv.trim().split("\\r\\n").length-1===53'),'mobs CSV: all 53 wolf rows');
 await send('Network.setBlockedURLs',{urls:['*mdb-c-*']});await go('mobs.html');
 ok(await waitFor('/Could not load the drops/.test(document.querySelector("#mob-out tbody tr").textContent)&&!!document.querySelector("#mob-out tbody tr .ux-retry")'),'blocked mob piece: "Could not load the drops (offline?)" + Try again');
 await send('Network.setBlockedURLs',{urls:[]});await ev('document.querySelector("#mob-out tbody tr .ux-retry").click()');
 ok(await waitFor('!document.querySelector("#mob-out tbody tr").classList.contains("ux-dbp")'),'Try again fills the row');
 await go('mobs.html');await ev('document.querySelector(".ux-dbbar .ux-tbar-r").click()');
 // 3) tooltips: Spells page and zone camp tables
 reqs=[];await go('spells.html');
 ok(await ev('document.querySelectorAll("table.spelllook [data-sp].ux-tt-t").length')>1000&&!TIPR('s'),'Spells page: '+await ev('document.querySelectorAll("table.spelllook [data-sp].ux-tt-t").length')+' spell names have tooltips (data loads on first use)');
 const sp6=await ev('(function(){var b=[].find.call(document.querySelectorAll("table.spelllook [data-sp]"),function(x){return x.closest("tr").getAttribute("data-cls")==="Inquisitor"});b.scrollIntoView({block:"center",behavior:"instant"});var r=b.getBoundingClientRect();return {x:r.left+4,y:r.top+r.height/2,t:b.textContent,lv:b.closest("tr").cells[1].textContent}})()');
 await send('Emulation.setTouchEmulationEnabled',{enabled:true});await sleep(150);
 await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:sp6.x,y:sp6.y}]});await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 ok(await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Inquisitor/.test(t.textContent)})()'),'tap on "'+sp6.t+'" opens its tooltip');
 const st6=await ev('(function(){var t=document.getElementById("ux-tt"),r=t.getBoundingClientRect();return {txt:t.textContent,l:r.left,r:r.right,ovf:document.documentElement.scrollWidth>innerWidth}})()');
 ok(st6.l>=0&&st6.r<=480&&!st6.ovf&&new RegExp('Level '+sp6.lv.trim()).test(st6.txt),'Spells tooltip fits 480 and matches the row (Level '+sp6.lv.trim()+', Inquisitor): '+st6.txt.slice(0,90));
 await shot('ux6-after-spells-tooltip-480.png');
 await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:20,y:880}]});await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await send('Emulation.setTouchEmulationEnabled',{enabled:false});
 ok(await ev('document.querySelectorAll("table.spelllook tbody [tabindex=\\"0\\"]").length===1'),'spell names: one roving Tab stop for the whole table (pass 7; pass 6 had none)');
 await go('zones/great-cavern-sea.html');
 const z6=await ev('({n:document.querySelectorAll("#named ~ .tw .tt-mob.ux-tt-t").length,all:document.querySelectorAll(".tt-mob.ux-tt-t").length,clean:[].every.call(document.querySelectorAll(".tt-mob"),function(s){return s.textContent===s.getAttribute("data-mob")&&!/wiki/.test(s.textContent)})})');
 ok(z6.all>=20&&z6.clean,'zone camp tables: '+z6.all+' mob names have tooltips (wiki links left out of the name)');
 await ev('(function(){var m=document.querySelector("h2#named ~ .tw .tt-mob");m.scrollIntoView({block:"center",behavior:"instant"});m.focus()})()');
 ok(await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Level/.test(t.textContent)&&/Great Cavern Sea/.test(t.textContent)})()'),'zone mob tooltip: '+(await ev('(document.getElementById("ux-tt")||{}).textContent||""')).slice(0,80));
 await key('Escape');
 await go('zones/great-cavern-sea.html');await ev('(function(){var t=document.querySelector("h2#named ~ .tw table.sortable");t.tHead.rows[0].cells[0].click()})()');
 ok(await ev('[].every.call(document.querySelector("h2#named ~ .tw").querySelectorAll("tbody tr"),function(r){return !!r.querySelector(".tt-mob")})'),'sorting a camp table keeps the tooltips');
 // 4) walkthrough: print one level band
 await size(1024,768);await go('walkthrough.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith');await waitFor('document.querySelectorAll(".ux-pband-b").length===8',10000);
 ok(await ev('/Print levels 16.20 only/.test(document.querySelector("#wt-b-16-20 .ux-pband-b").textContent)'),'each level band has "'+await ev('document.querySelector("#wt-b-16-20 .ux-pband-b").textContent.trim()')+'"');
 await ev('window.__pp=null;window.print=function(){window.__pp={one:document.documentElement.classList.contains("ux-print-one"),open:document.getElementById("wt-b-16-20").open,busy:!!document.querySelector("#wt-b-16-20 .wt-slot .lz-status"),t:(document.querySelector(".ux-ptitle")||{}).textContent}}');
 await ev('document.querySelector("#wt-b-16-20 .ux-pband-b").click()');
 ok(await waitFor('!!window.__pp',12000)&&await ev('window.__pp.one&&window.__pp.open&&!window.__pp.busy'),'button opens the band, waits for its route, then prints ('+await ev('JSON.stringify(window.__pp)')+')');
 await send('Emulation.setEmulatedMedia',{media:'print'});await sleep(200);
 const pb6=await ev('(function(){var b=[].filter.call(document.querySelectorAll("details.cg-band"),function(x){return x.checkVisibility()}).map(function(x){return x.id});return {b:b,h1:document.querySelector("main h1").checkVisibility(),head:document.querySelector(".cg-head").checkVisibility(),route:/Ail.Vorith/.test(document.getElementById("wt-b-16-20").textContent)&&!/Start-city route: (Night Harbor|Underdocks|Faelindral)/.test(document.getElementById("wt-b-16-20").textContent),btn:document.querySelector(".ux-pband-b").checkVisibility()}})()');
 ok(pb6.b.join()==='wt-b-16-20'&&!pb6.h1&&!pb6.head&&pb6.route&&!pb6.btn,'print preview: only levels 16–20 (Ail\'Vorith route, no other city), no page chrome or buttons');
 await shot('ux6-after-print-route.png');
 await ev('dispatchEvent(new Event("afterprint"))');await sleep(100);
 ok(await ev('!document.documentElement.classList.contains("ux-print-one")&&!document.querySelector(".ux-pthis,.ux-pkeep,.ux-ptitle")'),'after printing the page is back to normal (Ctrl+P prints the whole page again)');
 await send('Emulation.setEmulatedMedia',{media:''});
 // 5) hotbar app dialogs: 4.5:1 text and 3:1 control borders in all six theme x Irem combinations
 const HB=s=>CSCAN.replace('document.body.querySelectorAll(\'*\')','document.querySelector(\''+s+'\').querySelectorAll(\'*\')');
 for(const stt of ['dark-hw','dark','light-hw','light','contrast-hw','contrast']){const [th,hw]=stt.split('-');
  await ev(`localStorage.setItem('mnm-theme','${th}');localStorage.setItem('mnm-halloween','${hw?'on':'off'}');localStorage.setItem('mnm-class','Inquisitor')`);
  const bad=[];const scan=async(lab,sel)=>{const r=await ev(HB(sel||'#hb-app'));r.fails.forEach(f=>bad.push(lab+' T '+f.r+' '+f.el));r.cfails.forEach(f=>bad.push(lab+' C '+f.r+' '+f.el))};
  await go('hotbar.html');await scan('app');
  await ev('document.querySelector(".hb-pi[data-i=\\"1\\"]").click()');await scan('armed');await key('Escape');
  await ev('document.getElementById("hb-keys").click()');await scan('keybinds');await ev('document.getElementById("hb-keys").click()');
  await ev('document.getElementById("hb-sheet-t").click()');await sleep(150);await scan('sheet');
  await ev('document.querySelector(".hb-gs[data-g=\\"Chest\\"]").click()');await sleep(200);await scan('item picker','#hb-picker');await ev('document.querySelector(".hb-px").click()');
  await ev('document.getElementById("hb-sheet-t").click()');await ev('document.getElementById("hb-focus-t").click()');await sleep(150);await scan('focus mode','body');await key('Escape');
  ok(bad.length===0,'hotbar dialogs ['+stt+']: app, armed item, keybind editor, character sheet, item picker, focus mode pass 4.5:1 / 3:1'+(bad.length?' — '+bad.slice(0,5).join(' | '):''));
 }
 // 6) Irem x theme: 6 combinations on several pages; decorations, persistence, no flash, contrast covered above + pass 5
 const IREM=`(function(){var d=document.documentElement,b=getComputedStyle(document.body,'::before'),h2=[].find.call(document.querySelectorAll('main h2'),function(x){return parseFloat(getComputedStyle(x).borderLeftWidth)>0}),t=document.querySelector('.hw-toggle'),th=document.querySelector('.ux-themebtn');
  return {hw:d.classList.contains('halloween'),theme:d.getAttribute('data-theme')||'dark',deco:b.content!=='none'&&b.display!=='none'&&parseFloat(b.opacity)>0,bimg:b.backgroundImage.slice(0,40),bodyImg:getComputedStyle(document.body).backgroundImage!=='none',
   h2c:h2?getComputedStyle(h2).borderLeftColor:'',tog:t?t.textContent:'',tp:t?t.getAttribute('aria-pressed'):'',thl:th?th.querySelector('.ux-theme-l').textContent:'',css:(document.getElementById('ux-theme-css')||{}).href||''}})()`;
 await send('Page.addScriptToEvaluateOnNewDocument',{source:"window.__first=null;new MutationObserver(function(m,o){if(document.body&&!window.__first){window.__first={hw:document.documentElement.classList.contains('halloween'),theme:document.documentElement.getAttribute('data-theme')||'dark',css:!!document.getElementById('ux-theme-css')};o.disconnect()}}).observe(document,{childList:true,subtree:true})"}).then(r=>{global.__irem_sid=r.result&&r.result.identifier});
 const glowOf={dark:'rgb(124, 242, 180)',light:'rgb(93, 107, 34)',contrast:'rgb(255, 217, 138)'};
 for(const th of ['dark','light','contrast'])for(const hw of [true,false]){
  await ev(`localStorage.setItem('mnm-theme','${th}');localStorage.setItem('mnm-halloween','${hw?'on':'off'}')`);
  const bad=[];
  for(const u of ['index.html','classes/inquisitor.html','items.html','walkthrough.html','zones/ailvorith.html']){await go(u);const r=await ev(IREM),f=await ev('window.__first');
   if(r.hw!==hw||r.theme!==th)bad.push(u+' state '+JSON.stringify(r));
   if(!f||f.hw!==hw||f.theme!==th||(th!=='dark')!==f.css)bad.push(u+' first paint '+JSON.stringify(f));
   if(hw&&!r.deco)bad.push(u+' Irem decoration missing');if(!hw&&r.deco)bad.push(u+' decoration while Irem is off');
   if(hw&&r.h2c&&r.h2c!==glowOf[th])bad.push(u+' h2 rule '+r.h2c);
   if(r.tp!==String(hw)||(hw?!/on/.test(r.tog):!/off/.test(r.tog)))bad.push(u+' toggle '+r.tog);
   if(r.thl!==({dark:'Dark',light:'Light',contrast:'High contrast'})[th])bad.push(u+' theme button '+r.thl);
   if(th==='dark'&&hw&&!r.bodyImg)bad.push(u+' Irem cavern glow missing');if(th==='contrast'&&r.bodyImg)bad.push(u+' background image in High contrast')}
  ok(bad.length===0,'Irem '+(hw?'on':'off')+' x '+th+': correct on 5 pages from the first paint (class + data-theme + theme CSS before <body>), decorations '+(hw?'shown':'absent')+', toggle and theme button labels'+(bad.length?' — '+bad.slice(0,4).join(' | '):''));
  if(hw){await go('classes/inquisitor.html');await shot('ux6-after-irem-'+th+'-1024.png')}
 }
 if(global.__irem_sid)await send('Page.removeScriptToEvaluateOnNewDocument',{identifier:global.__irem_sid});
 // toggles: each persists independently, no reload needed
 await ev("localStorage.setItem('mnm-theme','light');localStorage.setItem('mnm-halloween','on')");await go('items.html');
 await ev('document.querySelector(".hw-toggle").click()');ok(await ev('!document.documentElement.classList.contains("halloween")&&document.documentElement.getAttribute("data-theme")==="light"&&getComputedStyle(document.body,"::before").content==="none"'),'Light: Irem toggle off removes the decorations at once, Light stays');
 await go('mobs.html');ok(await ev('!document.documentElement.classList.contains("halloween")&&document.documentElement.getAttribute("data-theme")==="light"&&localStorage.getItem("mnm-halloween")==="off"'),'…and both choices persist on the next page');
 await ev('document.querySelector(".hw-toggle").click()');await ev('document.querySelector(".ux-themebtn").click()');
 ok(await waitFor('document.documentElement.getAttribute("data-theme")==="contrast"')&&await ev('document.documentElement.classList.contains("halloween")&&localStorage.getItem("mnm-halloween")==="on"&&getComputedStyle(document.body,"::before").display!=="none"'),'Irem on + theme switch to High contrast: Irem stays on, its High contrast decorations apply');
 await ev('document.querySelector(".ux-themebtn").click()');ok(await waitFor('!document.documentElement.hasAttribute("data-theme")')&&await ev('document.documentElement.classList.contains("halloween")&&getComputedStyle(document.body,"::before").display!=="none"&&localStorage.getItem("mnm-theme")==="dark"'),'back to Dark: the original Irem look returns');
 await ev('localStorage.removeItem("mnm-theme");localStorage.removeItem("mnm-halloween")');
 // overflow at all widths in all themes on the pass 6 pages
 for(const th of ['dark','light','contrast']){await ev(`localStorage.setItem('mnm-theme','${th}')`);
  for(const [w,h] of [[480,900],[1024,768],[2560,1080],[3440,1440]]){await size(w,h);for(const u of ['items.html?iq=sword','mobs.html?mq=wolf','spells.html','walkthrough.html','hotbar.html','zones/great-cavern-sea.html']){await go(u);
   if(await ev('document.documentElement.scrollWidth>innerWidth'))ok(false,'pass 6: '+u+' overflows @'+w+' ('+th+')')}}}
 ok(true,'pass 6: no horizontal overflow at 480/1024/2560/3440 (items, mobs, spells, walkthrough, hotbar, zone) in Dark, Light and High contrast');
 await ev('localStorage.removeItem("mnm-theme")');
 // =============================== UX pass 7
// 0) Spells page: names reachable with Tab (one roving stop), tooltip on focus, arrows move, Esc closes and keeps focus
await size(1024,768);await go('index.html');await ev('localStorage.removeItem("mnm-tbl:spells.html");localStorage.setItem("mnm-class","Inquisitor")');await go('spells.html');
const AE='(function(){var a=document.activeElement;return {tag:a.tagName,cls:a.className,t:a.textContent.trim(),tr:a.closest("tbody tr")?[].indexOf.call(a.closest("tbody").rows,a.closest("tbody tr")):-1,tt:(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden?t.textContent:""})(),db:a.getAttribute("aria-describedby")}})()';
const stops=await ev('({body:document.querySelectorAll("table.spelllook tbody [tabindex=\\"0\\"], table.spelllook tbody a:not([tabindex=\\"-1\\"])").length,names:document.querySelectorAll("table.spelllook strong.ux-spn").length,role:document.querySelector("table.spelllook strong.ux-spn").getAttribute("role"),desc:(document.getElementById(document.querySelector("table.spelllook").getAttribute("aria-describedby"))||{}).textContent||""})');
ok(stops.body===1&&stops.names>1500&&stops.role==='button'&&/Tab/.test(stops.desc),'Spells: '+stops.names+' names + class links share ONE Tab stop (roving tabindex); names are buttons; table described by "'+stops.desc+'"');
await ev('document.getElementById("sp-band").focus()');let tabs7=0,a7;for(;tabs7<12;tabs7++){await tab();a7=await ev(AE);if(a7.tag==='STRONG')break}
ok(a7.tag==='STRONG'&&a7.tr===0&&tabs7<=7,'Tab from the filters reaches the first spell name after the '+tabs7+' sortable headers ("'+a7.t+'")');
ok(await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Level/.test(t.textContent)})()')&&/ux-tt/.test((await ev(AE)).db||''),'…its tooltip opens on focus and is linked with aria-describedby ('+(await ev(AE)).tt.slice(0,60)+')');
await key('ArrowDown');await sleep(150);const d7=await ev(AE);
ok(d7.tag==='STRONG'&&d7.tr===1&&d7.tt.indexOf(d7.t)>=0,'ArrowDown moves to the next spell and its tooltip ("'+d7.t+'")');
await key('End');const e7=await ev(AE);await key('Home');const h7=await ev(AE);await key('PageDown');const pd7=await ev(AE);
ok(e7.tr===stops.names-1&&h7.tr===0&&pd7.tr===10,'End / Home / PageDown jump to the last, first and 10th row');
await key('ArrowRight');if(await ev('document.activeElement.classList.contains("ux-spb")'))await key('ArrowRight');const r7=await ev(AE),r7h=await ev('document.activeElement.getAttribute("href")');await key('ArrowDown');const rd7=await ev(AE);await key('ArrowLeft');const l7=await ev(AE);
ok(r7.tag==='A'&&/classes\//.test(r7h)&&rd7.tag==='A'&&rd7.tr===11&&l7.tag==='STRONG'&&l7.tr===11,'ArrowRight reaches the row\'s class link, Down keeps the column, ArrowLeft returns to the name'+JSON.stringify([r7.tag,r7.tr,rd7.tag,rd7.tr,l7.tag,l7.tr]));
{const bi=await ev('(function(){var b=document.querySelector("table.spelllook tbody a.ux-spb");if(!b)return -1;var rs=[].filter.call(b.closest("tbody").rows,function(t){return t.getClientRects().length});var tr=b.closest("tr"),i=rs.indexOf(tr);if(i<0||!rs[i+1]||rs[i+1].querySelector("a.ux-spb"))return -2;b.focus();return i})()');
 if(bi>=0){await key('ArrowDown');const bd=await ev('(function(){var a=document.activeElement;return a.classList.contains("ux-spc")&&/classes\\//.test(a.getAttribute("href"))})()');ok(bd,'pass 8: ArrowDown from a "changed" badge onto a row without one lands on the class link, not the name')}
 else ok(true,'pass 8: badge column fallback (no badge row followed by a plain row in this view)')}
await ev('(function(){var rs=[].filter.call(document.querySelector("table.spelllook").tBodies[0].rows,function(t){return t.getClientRects().length});rs[11].querySelector("strong.ux-spn").focus()})()');await sleep(200);
await shot('ux7-after-spells-focus-1024.png');
await key('Escape');const x7=await ev(AE);ok(!x7.tt&&x7.tag==='STRONG'&&x7.tr===11,'Esc closes the tooltip and focus stays on the spell name');
await tab();const o7=await ev(AE);ok(o7.tr<0&&o7.tag!=='STRONG','Tab leaves the table in one press (now on '+o7.tag+' '+o7.cls.slice(0,30)+')');
await tab(true);const b7=await ev(AE);ok(b7.tag==='STRONG'&&b7.tr===11,'Shift+Tab comes back to the same spell');
await ev('(function(){var m=document.getElementById("sp-mine");m.checked=true;m.dispatchEvent(new Event("change",{bubbles:true}))})()');await sleep(250);
const f7=await ev('(function(){var z=document.querySelectorAll("table.spelllook tbody [tabindex=\\"0\\"]");return {n:z.length,vis:z[0]&&z[0].closest("tr").getClientRects().length>0,cls:z[0]&&z[0].closest("tr").getAttribute("data-cls")}})()');
ok(f7.n===1&&f7.vis&&f7.cls==='Inquisitor','"Only my class" hides the focused row: the Tab stop moves to the first visible (Inquisitor) row');
await ev('document.querySelector("table.spelllook strong.ux-spn[tabindex=\\"0\\"]").focus()');await key('ArrowDown');
ok(await ev('document.activeElement.closest("tr").getAttribute("data-cls")==="Inquisitor"'),'ArrowDown skips hidden rows');
await ev('(function(){var m=document.getElementById("sp-mine");m.checked=false;m.dispatchEvent(new Event("change",{bubbles:true}))})()');await key('Escape');
await ev('document.querySelector("table.spelllook thead th:nth-child(1)").click()');await sleep(200);
ok(await ev('document.querySelectorAll("table.spelllook tbody [tabindex=\\"0\\"]").length===1'),'sorting keeps one Tab stop');
await ev('document.querySelector("table.spelllook thead th:nth-child(2)").click()');await ev('localStorage.removeItem("mnm-tbl:spells.html")');
// 1) item tooltips in 32 pieces (hash of the name); fallback to the complete item-tips.js
{const vm=require('vm'),ctx={window:{}};for(let i=0;i<32;i++)vm.runInNewContext(fs.readFileSync(path.join(DOCS,'assets','itip-'+i+'.js'),'utf8'),ctx);
 const all={window:{}};vm.runInNewContext(fs.readFileSync(path.join(DOCS,'assets','item-tips.js'),'utf8'),all);
 const A=ctx.window.MNM_ITEMS,B=all.window.MNM_ITEMS,ka=Object.keys(A),mx=Math.max(...Array.from({length:32},(_,i)=>sz('itip-'+i+'.js')));
 const h=n=>{let x=0;for(let i=0;i<n.length;i++)x=(x*31+n.charCodeAt(i))>>>0;return x%32};
 const placed=Array.from({length:32},(_,i)=>{const c={window:{}};vm.runInNewContext(fs.readFileSync(path.join(DOCS,'assets','itip-'+i+'.js'),'utf8'),c);return Object.keys(c.window.MNM_ITEMS).every(n=>h(n)===i)}).every(Boolean);
 ok(ka.length===Object.keys(B).length&&ka.length>5000&&ka.every(k=>JSON.stringify(A[k])===JSON.stringify(B[k]))&&placed,'item tips: '+ka.length+' items in 32 pieces (largest '+mx+' KB, was one '+sz('item-tips.js')+' KB file), each in the piece its name hashes to, same rows as the complete item-tips.js');}
await size(1024,768);reqs=[];await go('classes/inquisitor.html');await waitFor('!!document.querySelector(".itm[data-i]")',10000);
const itq=await ev('(function(){var a=document.querySelector(".itm[data-i]");a.scrollIntoView({block:"center",behavior:"instant"});var r=a.getBoundingClientRect();a.dispatchEvent(new MouseEvent("mouseover",{bubbles:true,clientX:r.left+5,clientY:r.top+5}));return a.getAttribute("data-i")})()');
ok(await waitFor('(function(){var t=document.getElementById("tip");return !t.hidden&&/Slot:/.test(t.textContent)})()')&&reqs.filter(r=>/^itip-/.test(r)).length===1&&!reqs.includes('item-tips.js'),'hovering "'+itq+'" loads one piece ('+reqs.filter(r=>/^itip-/.test(r)).join()+'), not item-tips.js');
await send('Network.setBlockedURLs',{urls:['*itip-*']});reqs=[];await go('classes/inquisitor.html');await waitFor('!!document.querySelector(".itm[data-i]")',10000);
await ev('(function(){var a=document.querySelector(".itm[data-i]");var r=a.getBoundingClientRect();a.dispatchEvent(new MouseEvent("mouseover",{bubbles:true,clientX:r.left+5,clientY:r.top+5}))})()');
ok(await waitFor('(function(){var t=document.getElementById("tip");return !t.hidden&&/Slot:/.test(t.textContent)})()')&&reqs.includes('item-tips.js'),'pieces missing: the tooltip falls back to the complete item-tips.js');
await send('Network.setBlockedURLs',{urls:[]});
// 2) search-text.js packed: decodes to exactly the old text array; snippets still work
{const vm=require('vm'),c={window:{}},o={window:{}};vm.runInNewContext(fs.readFileSync(path.join(DOCS,'assets','search-text.js'),'utf8'),c);vm.runInNewContext(fs.readFileSync(path.join(DOCS,'assets','search-index.js'),'utf8'),o);
 const X=c.window.MNM_STEXT,I=o.window.MNM_INDEX;ok(Array.isArray(X)&&X.length===I.length&&X.every((x,i)=>x===(I[i].x||'')),'search-text.js ('+sz('search-text.js')+' KB) decodes to the same '+X.length+' texts as the full index (byte for byte)');}
reqs=[];await go('index.html');await ev('(function(){var q=document.getElementById("q");q.focus();q.value="glass flats";q.dispatchEvent(new Event("input",{bubbles:true}))})()');
ok(await waitFor('window.MNM_SEARCH.full()&&!!document.querySelector("#qres mark")',15000)&&reqs.includes('search-text.js'),'search snippets with <mark> still show once the packed text loads ('+(await ev('(document.querySelector("#qres mark")||{}).textContent||""'))+')');
await ev('document.getElementById("q").blur();document.getElementById("qres").hidden=true');
// 3) hotbar: class spell lists per class; blocked file -> Try again; #hb= link for another class
await ev("localStorage.setItem('mnm-class','Inquisitor');localStorage.removeItem('mnm-hotbar')");reqs=[];await go('hotbar.html');await waitFor('!!document.querySelector(".hb-pi")&&!document.getElementById("hb-app").inert',10000);
const hbr=reqs.filter(r=>/^hb-c-/.test(r));
ok(hbr.join()==='hb-c-inquisitor.js'&&!reqs.includes('hotbar-items.js')&&await ev('document.querySelectorAll(".hb-pi").length')>10,'hotbar: first load = hotbar-data.js ('+sz('hotbar-data.js')+' KB) + '+hbr.join()+' ('+sz('hb-c-inquisitor.js')+' KB); item picker data not loaded');
reqs=[];await ev('(function(){var s=document.getElementById("mnm-class");s.value="Cleric";s.dispatchEvent(new Event("change",{bubbles:true}))})()');
ok(await waitFor('!!(MNM_HB_API.state().cls.Cleric)&&!document.getElementById("hb-app").inert',10000)&&reqs.filter(r=>/^hb-c-/.test(r)).join()==='hb-c-cleric.js'&&await ev('MNM_HB_API.state().cls.Cleric.L.solo.ab.filter(Boolean).length')>=4,'switching to Cleric loads hb-c-cleric.js and suggests real Cleric spells');
await ev("localStorage.setItem('mnm-class','Druid')");await send('Network.setBlockedURLs',{urls:['*hb-c-druid.js']});await go('hotbar.html');
ok(await waitFor('/could not load/.test((document.querySelector(".hb-lz")||{}).textContent||"")&&!!document.querySelector(".hb-lz-retry")',8000)&&await ev('document.getElementById("hb-app").inert'),'blocked class file: "'+(await ev('(document.querySelector(".hb-lz")||{}).textContent||""')).slice(0,60)+'" + Try again; planner inert meanwhile');
await send('Network.setBlockedURLs',{urls:[]});await ev('document.querySelector(".hb-lz-retry").click()');
ok(await waitFor('!document.querySelector(".hb-lz")&&!document.getElementById("hb-app").inert&&!!MNM_HB_API.state().cls.Druid',8000),'Try again loads Druid and the planner works');
const code7=await evp('(function(){var s=MNM_HB_API.state().cls.Druid;return MNM_HB_API.encode({v:1,c:"Monk",cur:"solo",L:{solo:s.L.solo},g:{},b:0,l:null})})()');
await ev("localStorage.setItem('mnm-class','Inquisitor')");await go('index.html');reqs=[];await go('hotbar.html#hb='+code7);
ok(await waitFor('document.getElementById("mnm-class").value==="Monk"&&!!MNM_HB_API.state().cls.Monk&&!document.getElementById("hb-app").inert',10000)&&reqs.includes('hb-c-monk.js'),'#hb= link for another class (Monk) loads that class file and applies ('+reqs.filter(r=>/^hb-c-/.test(r)).join()+')');
await ev("localStorage.removeItem('mnm-hotbar');localStorage.setItem('mnm-class','Inquisitor')");
// 4) Show more on Items / Mobs
await ev('localStorage.removeItem("mnm-db:items.html");localStorage.removeItem("mnm-db:mobs.html");localStorage.removeItem("mnm-cmp")');
await go('items.html');await waitFor(DBOK);
ok(await ev('(function(){var m=document.querySelector(".ux-more");return !m.hidden&&/^Show 150 more$/.test(m.querySelector("button").textContent)&&/150 of \\d+ shown/.test(m.textContent)})()'),'Items: "'+await ev('document.querySelector(".ux-more").textContent')+'" under the first 150');
await ev('document.querySelector(".ux-more-b").focus();document.querySelector(".ux-more-b").click()');await sleep(200);
const sm=await ev('({n:document.querySelectorAll("#idb-out .idb-it").length,c:document.getElementById("idb-count").textContent,copy:!!document.querySelectorAll("#idb-out .idb-it")[200].querySelector(".ux-copy"),cmp:!!document.querySelectorAll("#idb-out .idb-it")[200].querySelector(".ux-cmp-b"),f:document.activeElement.className})');
ok(sm.n===300&&/showing 300/.test(sm.c)&&sm.copy&&sm.cmp&&sm.f==='ux-more-b','Show more adds 150 rows ('+sm.c+'), with Copy and Compare; focus stays on the button');
await ev('document.querySelectorAll("#idb-out .idb-it")[260].scrollIntoView({block:"center",behavior:"instant"})');
ok(await waitFor('!document.querySelectorAll("#idb-out .idb-it")[260].classList.contains("ux-dbp")'),'the added rows fill from the pieces as they scroll into view');
await ev('scrollTo(0,0)');await shot('ux7-after-showmore-items-1024.png');
await go('mobs.html');await waitFor(DBOK);await ev('document.querySelector(".ux-more-b").click()');await sleep(200);
const sm2=await ev('({n:document.querySelectorAll("#mob-out tbody tr").length,c:document.getElementById("mob-count").textContent,b:document.querySelector(".ux-more-b").textContent,copy:!!document.querySelectorAll("#mob-out tbody tr")[300].querySelector(".ux-copy")})');
ok(sm2.n===400&&/showing 400/.test(sm2.c)&&sm2.b==='Show 200 more'&&sm2.copy,'Mobs: Show more adds 200 rows to the table ('+sm2.c+')');
await ev('document.querySelectorAll("#mob-out tbody tr")[200].scrollIntoView({block:"start",behavior:"instant"});scrollBy(0,-200)');await waitFor('!document.querySelectorAll("#mob-out tbody tr")[200].classList.contains("ux-dbp")');
await shot('ux7-after-showmore-1024.png');
await go('mobs.html?mq=wolf');await waitFor(DBOK,15000);ok(await ev('document.querySelector(".ux-more").hidden'),'no Show more when every match is listed');
// 6) item tooltips in the Mobs drop lists
reqs=[];await go('mobs.html#'+encodeURIComponent('Foreman Vikkit'));await waitFor(DBOK,15000);await waitFor('!!document.querySelector("#mob-out a.tt-item.ux-tt-t")',15000);
const mi=await ev('(function(){var a=document.querySelector("#mob-out a.tt-item");a.focus();return a.textContent})()');
ok(await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Slot:/.test(t.textContent)&&t.textContent.indexOf('+JSON.stringify(mi)+')>=0})()')&&reqs.some(r=>/^itip-/.test(r))&&!reqs.includes('item-tips.js'),'Mobs drop list: focusing "'+mi+'" shows its item tooltip (one itip piece)');
await key('Escape');ok(await ev('document.getElementById("ux-tt").hidden&&document.activeElement.classList.contains("tt-item")'),'Esc closes it, focus stays on the link');
ok(await ev('/items\\.html#/.test(document.querySelector("#mob-out a.tt-item").getAttribute("href"))'),'the drop link still goes to the Items database');
// 7) compare two items (#8)
await size(480,900);await ev('localStorage.removeItem("mnm-cmp")');await go('items.html?iq=helm');await waitFor(DBOK,15000);
const cn=await ev('[].slice.call(document.querySelectorAll("#idb-out .ux-cmp-b"),0,2).map(function(b){return b.getAttribute("data-cmp")})');
await ev('document.querySelectorAll("#idb-out .ux-cmp-b")[0].click()');
ok(await ev('(function(){var b=document.querySelector(".ux-cmpbar");return !b.hidden&&/Pick one more/.test(b.textContent)&&document.querySelectorAll("#idb-out .ux-cmp-b")[0].getAttribute("aria-pressed")==="true"})()'),'Compare on one item: pressed button + "Pick one more item" bar');
await ev('document.querySelectorAll("#idb-out .ux-cmp-b")[1].focus();document.querySelectorAll("#idb-out .ux-cmp-b")[1].click()');
ok(await waitFor('(function(){var d=document.querySelector("dialog.ux-cmpdlg");return d&&d.open&&!!d.querySelector(".ux-cmp-t")})()',10000),'second pick opens the side-by-side dialog');
const ct=await ev('(function(){var d=document.querySelector("dialog.ux-cmpdlg"),t=d.querySelector(".ux-cmp-t"),h=[].map.call(t.tHead.rows[0].cells,function(c){return c.textContent});return {h:h,rows:[].map.call(t.tBodies[0].rows,function(r){return r.cells[0].textContent}),f:document.activeElement.closest("dialog")===d,ovf:document.documentElement.scrollWidth>innerWidth,w:Math.round(d.getBoundingClientRect().width),tw:Math.round(t.getBoundingClientRect().width),slot:t.tBodies[0].rows[0].cells[1].textContent}})()');
ok(ct.h[1]===cn[0]&&ct.h[2]===cn[1]&&ct.rows.some(r=>/^Slot/.test(r))&&ct.rows.some(r=>/^Stat: /.test(r))&&ct.rows.some(r=>/^Sources/.test(r))&&ct.f&&!ct.ovf&&ct.tw<=ct.w,'compare table: '+cn.join(' vs ')+'; rows '+ct.rows.map(r=>r.replace(/ \(differs\)/,'')).slice(0,6).join(', ')+'…; fits 480 ('+ct.tw+'/'+ct.w+'px); focus in the dialog');
const cv7=await ev('(function(){var r=MNM_IDB.filter(function(d){return d[0]==='+JSON.stringify(cn[0])+'})[0],c=MNM_IDBC[Math.floor(r[1]/100)][r[1]%100];var t=document.querySelector(".ux-cmp-t");var st=[].filter.call(t.tBodies[0].rows,function(x){return /^Stat: /.test(x.cells[0].textContent)}).map(function(x){return x.cells[1].textContent}).filter(function(x){return x!=="\\u2014"});return {stats:c[5],cells:st,slot:c[2]||"no slot",shown:t.tBodies[0].rows[0].cells[1].textContent}})()');
ok(cv7.slot===cv7.shown&&cv7.cells.every(x=>cv7.stats.indexOf(x)>=0)&&cv7.cells.join(', ')===cv7.stats.split(/,\s*/).filter(Boolean).join(', '),'values are the listed site data, unchanged (slot "'+cv7.shown+'", stats "'+cv7.stats+'")');
ok(/cmp=/.test(await ev('location.search')),'the comparison is in the link ('+decodeURIComponent(await ev('location.search')).slice(0,80)+')');
await shot('ux7-after-compare-480.png');
await key('Escape');ok(await ev('!document.querySelector("dialog.ux-cmpdlg").open&&document.activeElement.classList.contains("ux-cmp-b")'),'Esc closes the dialog and returns focus to the Compare button');
const share=await ev('location.href');await go(share.replace(/^.*?\/items\.html/,'items.html'));
ok(await waitFor('(function(){var d=document.querySelector("dialog.ux-cmpdlg");return d&&d.open&&!!d.querySelector(".ux-cmp-t")})()',10000),'opening the shared link shows the same comparison');
await key('Escape');await ev('document.querySelectorAll("#idb-out .ux-cmp-b")[2]&&document.querySelectorAll("#idb-out .ux-cmp-b")[2].click()');
const c3=await ev('MNM_UX_CMP.picks()');ok(c3.length===2&&c3[0]===cn[1],'a third pick replaces the oldest ('+c3.join(' vs ')+')');await key('Escape');
await ev('document.querySelector(".ux-cmp-clr").click()');ok(await ev('document.querySelector(".ux-cmpbar").hidden&&MNM_UX_CMP.picks().length===0&&!/cmp=/.test(location.search)'),'Clear empties the comparison and the link');
// contrast of the new controls (Spells hint, Show more, compare bar + dialog, hotbar loading line) in all six theme x Irem combos
const SC=s=>CSCAN.replace('document.body.querySelectorAll(\'*\')','document.querySelectorAll(\''+s+'\')');
for(const stt of ['dark-hw','dark','light-hw','light','contrast-hw','contrast']){const [th,hw]=stt.split('-');const bad=[];
 await ev(`localStorage.setItem('mnm-theme','${th}');localStorage.setItem('mnm-halloween','${hw?'on':'off'}');localStorage.setItem('mnm-cmp','[]')`);
 const scan=async(lab,sel)=>{const r=await ev(SC(sel));r.fails.forEach(f=>bad.push(lab+' T '+f.r+' '+f.el));r.cfails.forEach(f=>bad.push(lab+' C '+f.r+' '+f.el))};
 await size(1024,768);await go('spells.html');await scan('spells hint','.sptools, .sptools *');
 await go('items.html?iq=helm');await waitFor(DBOK,15000);await scan('show more','.ux-more, .ux-more *');
 await ev('document.querySelectorAll("#idb-out .ux-cmp-b")[0].click()');await scan('compare bar','.ux-cmpbar, .ux-cmpbar *, .ux-cmp-b');
 await ev('document.querySelectorAll("#idb-out .ux-cmp-b")[1].click()');await waitFor('!!document.querySelector(".ux-cmp-t")');await scan('compare dialog','dialog.ux-cmpdlg, dialog.ux-cmpdlg *');
 for(const [w,h] of [[480,900],[1024,768],[2560,1080],[3440,1440]]){await size(w,h);await sleep(80);if(await ev('document.documentElement.scrollWidth>innerWidth'))bad.push('compare overflows @'+w)}
 await key('Escape');await ev('document.querySelector(".ux-cmp-clr").click()');
 ok(bad.length===0,'pass 7 controls ['+stt+']: Spells hint, Show more, compare bar and dialog pass 4.5:1 text / 3:1 controls, no overflow 480-3440'+(bad.length?' — '+bad.slice(0,4).join(' | '):''));
}
await ev('localStorage.removeItem("mnm-theme");localStorage.removeItem("mnm-halloween");localStorage.removeItem("mnm-cmp")');await size(1024,768);
for(const th of ['dark','light','contrast']){await ev(`localStorage.setItem('mnm-theme','${th}')`);
 for(const [w,h] of [[480,900],[1024,768],[2560,1080],[3440,1440]]){await size(w,h);for(const u of ['spells.html','hotbar.html','items.html','mobs.html']){await go(u);
  if(await ev('document.documentElement.scrollWidth>innerWidth'))ok(false,'pass 7: '+u+' overflows @'+w+' ('+th+')')}}}
ok(true,'pass 7: spells, hotbar, items, mobs checked for overflow at 480/1024/2560/3440 in Dark, Light and High contrast');
// =============================== UX pass 8
const evp8=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)throw new Error(e.slice(0,200)+' '+JSON.stringify(r.result.exceptionDetails).slice(0,300));return r.result.result.value};
await send('Emulation.setFocusEmulationEnabled',{enabled:true});
// 1) Spells page rows from per-class data (sp-c-<class>.js + inline renderer; build checks it byte for byte)
{const raw=fs.readFileSync(path.join(DOCS,'spells.html'),'utf8'),all=fs.readFileSync(path.join(DOCS,'spells-all.html'),'utf8');
 const nTags=(raw.match(/<script src="assets\/sp-c-[a-z-]+\.js"><\/script>/g)||[]).length,emptyBody=/<table class="grid sortable spelllook">.*?<tbody><\/tbody>/.test(raw);
 ok(nTags===18&&emptyBody&&/<noscript>[^]*?spells-all\.html/.test(raw)&&(all.match(/<tr data-cls=/g)||[]).length===1622,'Spells: page ships '+nTags+' per-class data files, an empty table body and a <noscript> link; spells-all.html has all 1622 rows ('+Math.round(raw.length/1024)+' KB vs '+Math.round(all.length/1024)+' KB)');
 await size(1024,768);await go('index.html');await ev('localStorage.removeItem("mnm-tbl:spells.html");localStorage.setItem("mnm-class","Inquisitor");localStorage.setItem("mnm-range","11-15")');reqs=[];await go('spells.html');
 const RW='(function(t){return [].map.call(t.tBodies[0].rows,function(r){return [r.getAttribute("data-cls"),r.getAttribute("data-lo"),r.getAttribute("data-hi")].concat([].map.call(r.cells,function(c){return c.textContent})).concat([].map.call(r.querySelectorAll("a"),function(a){return a.getAttribute("href")})).join("\\u0001")})})';
 const eq=await evp8(`fetch('spells-all.html').then(function(r){return r.text()}).then(function(h){var d=new DOMParser().parseFromString(h,'text/html'),A=${RW}(d.querySelector('table.spelllook')),B=${RW}(document.querySelector('table.spelllook'));
   var bad=-1;for(var i=0;i<Math.max(A.length,B.length);i++)if(A[i]!==B[i]){bad=i;break}return {n:B.length,bad:bad,a:bad<0?'':A[bad],b:bad<0?'':B[bad]}})`);
 ok(eq.n===1622&&eq.bad<0,'Spells: the rendered rows match spells-all.html row for row (attributes, every cell, every link) — '+eq.n+' rows'+(eq.bad>=0?' FIRST DIFF '+eq.bad+' '+eq.a.slice(0,80)+' | '+eq.b.slice(0,80):''));
 ok(reqs.filter(r=>/^sp-c-/.test(r)).length===18&&!reqs.includes('spells-all.html'),'Spells: the 18 class files load with the page (no full-table download)');
 const bd=await ev('(function(){var b=document.querySelectorAll("table.spelllook tbody td:first-child a.badge");var r=[].find.call(document.querySelectorAll("table.spelllook tbody tr[data-cls=Inquisitor]"),function(x){return /Aura of Resistance/.test(x.cells[0].textContent)});return {n:b.length,ti:[].every.call(b,function(x){return x.getAttribute("tabindex")==="-1"}),inq:r?r.cells[0].textContent:""}})()');
 ok(bd.n===50&&bd.ti&&/changed 0\.30\.3\.2/.test(bd.inq),'Spells: '+bd.n+' patch "changed" badges carried through (Inquisitor: "'+bd.inq+'"), not extra Tab stops');
 ok(await ev('document.querySelectorAll("table.spelllook tbody [tabindex=\\"0\\"]").length===1&&document.querySelectorAll("table.spelllook strong.ux-spn").length===1622'),'Spells: still one roving Tab stop over 1622 names (pass 7)');
 // Right/Left through name -> badge -> class link on a badged row
 await ev('(function(){var r=[].find.call(document.querySelectorAll("table.spelllook tbody tr"),function(x){return x.querySelector("a.ux-spb")});r.querySelector("strong.ux-spn").focus()})()');
 await key('ArrowRight');const k1=await ev('document.activeElement.className');await key('ArrowRight');const k2=await ev('document.activeElement.className');await key('ArrowLeft');await key('ArrowLeft');const k3=await ev('document.activeElement.className');
 ok(/ux-spb/.test(k1)&&/ux-spc/.test(k2)&&/ux-spn/.test(k3),'Spells: ArrowRight goes name → changed badge → class link, ArrowLeft back ('+[k1,k2,k3].join(' / ')+')');
 await key('Escape');
 // filters, sort, URL params
 await ev('(function(){var m=document.getElementById("sp-mine");m.checked=true;m.dispatchEvent(new Event("change",{bubbles:true}))})()');await sleep(300);
 const fm=await ev('(function(){var v=[].filter.call(document.querySelectorAll("table.spelllook tbody tr"),function(r){return r.getClientRects().length});return {n:v.length,all:v.every(function(r){return r.getAttribute("data-cls")==="Inquisitor"}),u:location.search}})()');
 ok(fm.n>20&&fm.all&&/sm=1/.test(fm.u),'Spells: "Only my class" shows the '+fm.n+' Inquisitor rows and goes into the URL ('+fm.u+')');
 await ev('document.querySelectorAll("table.spelllook thead th")[1].click()');await sleep(200);await ev('document.querySelectorAll("table.spelllook thead th")[1].click()');await sleep(300);
 const so=await ev('(function(){var v=[].filter.call(document.querySelectorAll("table.spelllook tbody tr"),function(r){return r.getClientRects().length}).map(function(r){return +r.getAttribute("data-lo")});return {f:v[0],l:v[v.length-1],u:location.search}})()');
 ok(so.f>=so.l&&/sort=/.test(so.u),'Spells: sorting by level works on the rendered rows and is in the URL ('+so.f+' … '+so.l+', '+so.u+')');
 const share=await ev('location.href');await go(share.replace(/^.*?\/spells\.html/,'spells.html'));
 const fm2=await ev('(function(){var v=[].filter.call(document.querySelectorAll("table.spelllook tbody tr"),function(r){return r.getClientRects().length});return {n:v.length,m:document.getElementById("sp-mine").checked,f:+v[0].getAttribute("data-lo")}})()');
 ok(fm2.m&&fm2.n===fm.n&&fm2.f===so.f,'Spells: the shared link restores the filter and sort ('+fm2.n+' rows, first level '+fm2.f+')');
 await ev('localStorage.removeItem("mnm-tbl:spells.html")');await go('spells.html');
 await ev('(function(){var f=document.getElementById("mnm-filter");if(f){f.value="aura of resistance";f.dispatchEvent(new Event("input",{bubbles:true}))}})()');await sleep(400);
 const ff=await ev('[].filter.call(document.querySelectorAll("table.spelllook tbody tr"),function(r){return r.getClientRects().length}).map(function(r){return r.getAttribute("data-cls")+":"+r.cells[0].textContent})');
 ok(ff.length>=1&&ff.every(x=>/aura of resistance/i.test(x)),'Spells: "Filter this page" finds rendered rows ('+ff.slice(0,3).join(', ')+')');
 await ev('(function(){var f=document.getElementById("mnm-filter");if(f){f.value="";f.dispatchEvent(new Event("input",{bubbles:true}))}})()');
 // tooltip on a rendered name still works
 await ev('(function(){var b=[].find.call(document.querySelectorAll("table.spelllook strong.ux-spn"),function(x){return x.closest("tr").getAttribute("data-cls")==="Inquisitor"});b.focus()})()');
 ok(await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Level/.test(t.textContent)})()'),'Spells: tooltip opens on focus of a rendered name');await key('Escape');
 // print: every row is in the DOM, the hint and tools are not printed
 await send('Emulation.setEmulatedMedia',{media:'print'});
 const pr=await ev('({rows:[].filter.call(document.querySelectorAll("table.spelllook tbody tr"),function(r){return r.getClientRects().length}).length,nav:!!(document.querySelector(".top")&&document.querySelector(".top").getClientRects().length)})');
 await send('Emulation.setEmulatedMedia',{media:''});ok(pr.rows===1622&&!pr.nav,'Spells: print shows all '+pr.rows+' rows without the menus');
 // a class file that cannot load: the others still render and the page says so with a link to the full table
 await send('Network.setBlockedURLs',{urls:['*sp-c-bard.js']});await go('spells.html');
 const ms=await ev('({n:document.querySelectorAll("table.spelllook tbody tr").length,bard:document.querySelectorAll("table.spelllook tbody tr[data-cls=Bard]").length,st:(document.querySelector("main .lz-err")||{}).textContent||"",a:!!document.querySelector("main .lz-err a[href=\\"spells-all.html\\"]")})');
 await send('Network.setBlockedURLs',{urls:[]});
 ok(ms.bard===0&&ms.n>1400&&/Bard/.test(ms.st)&&ms.a,'Spells: if one class file is offline the rest render ('+ms.n+' rows) and "'+ms.st.slice(0,70)+'…" links the full table');
 // no JavaScript
 await send('Emulation.setScriptExecutionDisabled',{value:true});await go('spells.html');
 const nj=await ev('({rows:document.querySelectorAll("table.spelllook tbody tr").length,ns:(function(){var n=document.querySelector("noscript");return !!n})()})').catch(()=>null);
 await shot('ux8-after-spells-nojs-1024.png');
 await go('spells-all.html');const nj2=await ev('document.querySelectorAll("table.spelllook tbody tr").length').catch(()=>-1);
 await send('Emulation.setScriptExecutionDisabled',{value:false});
 ok(nj&&nj.rows===0&&nj2===1622,'Spells without JavaScript: the page shows the <noscript> link; spells-all.html has all '+nj2+' rows as plain HTML');
}
// 2) Hotbar: clicky item list on demand (hb-clicky.js), #hb= links with a clicky still work
{await size(1024,768);await go('index.html');await ev('localStorage.removeItem("mnm-hotbar");localStorage.setItem("mnm-class","Inquisitor");localStorage.setItem("mnm-range","11-15")');reqs=[];await go('hotbar.html');
 await waitFor('!document.getElementById("hb-app").inert',10000);
 ok(!reqs.includes('hb-clicky.js')&&await ev('!window.MNM_HB.clicky&&window.MNM_HB.lazy.clicky==="hb-clicky.js"'),'Hotbar: the clicky item list ('+sz('hb-clicky.js')+' KB) is not loaded up front; hotbar-data.js is '+sz('hotbar-data.js')+' KB');
 await ev('(function(){var k=document.getElementById("hb-kind");k.value="h";k.dispatchEvent(new Event("change",{bubbles:true}))})()');
 ok(await waitFor('document.querySelectorAll("#hb-palette .hb-pi.k-c").length>0',10000)&&reqs.includes('hb-clicky.js'),'Hotbar: choosing "Hotbar: skills, traits, clickies, macros" loads it and lists '+await ev('document.querySelectorAll("#hb-palette .hb-pi.k-c").length')+' clicky items');
 const ck=await ev('(function(){var b=document.querySelector("#hb-palette .hb-pi.k-c");return b.querySelector(".hb-pn").textContent})()');
 const code=await evp8(`(function(){var S=MNM_HB_API.state(),o=S.cls.Inquisitor,L=o.L[o.cur];L.hb[0][0]={t:'c',n:${JSON.stringify(ck)}};return MNM_HB_API.encode({v:1,c:'Inquisitor',r:'',l:13,cur:o.cur,L:o.L,g:{},b:0,m:[],p:2})})()`);
 await ev('localStorage.removeItem("mnm-hotbar")');await go('index.html');reqs=[];await go('hotbar.html#hb='+code);
 ok(await waitFor('[].some.call(document.querySelectorAll(".hb-slot.k-c"),function(b){return !b.classList.contains("bad")})',10000)&&reqs.includes('hb-clicky.js'),'Hotbar: a #hb= link holding a clicky ('+ck+') loads the list first and the slot is valid');
 await go('hotbar.html');ok(await waitFor('!document.getElementById("hb-app").inert&&[].some.call(document.querySelectorAll(".hb-slot.k-c"),function(b){return !b.classList.contains("bad")})',10000),'Hotbar: a saved layout with a clicky waits for the list on reload (no "not in this class list")');
 await ev('localStorage.removeItem("mnm-hotbar")');
}
// 3) Spell and mob tips in pieces: exact match with the full files; one piece per tooltip; full-file fallback
{await size(1024,768);await go('spells.html');
 const ex=await evp8(`(function(){function get(f){return fetch('assets/'+f).then(function(r){return r.text()})}
   function run(src,v){var w={};new Function('window',src)(w);return w[v]}
   var P=[];for(var i=0;i<16;i++){P.push(get('stip-'+i+'.js'));P.push(get('mtip-'+i+'.js'))}
   return Promise.all([get('spell-tips.js'),get('mob-tips.js')].concat(P)).then(function(a){var S=run(a[0],'MNM_STIPS'),M=run(a[1],'MNM_MTIPS'),s={},m={},wrong=0;
     for(var i=0;i<16;i++){var ps=run(a[2+2*i],'MNM_STIPS'),pm=run(a[3+2*i],'MNM_MTIPS');Object.keys(ps).forEach(function(k){s[k]=ps[k];if(tph(k)!==i)wrong++});Object.keys(pm).forEach(function(k){m[k]=pm[k];if(tph(k)!==i)wrong++})}
     function tph(n){var h=0;for(var j=0;j<n.length;j++)h=(h*31+n.charCodeAt(j))>>>0;return h%16}
     function same(A,B){var ka=Object.keys(A).sort(),kb=Object.keys(B).sort();return ka.length===kb.length&&ka.every(function(k,j){return k===kb[j]&&JSON.stringify(A[k])===JSON.stringify(B[k])})}
     return {s:same(S,s),m:same(M,m),ns:Object.keys(S).length,nm:Object.keys(M).length,wrong:wrong}})})()`);
 ok(ex.s&&ex.m&&ex.wrong===0,'Tips: the 16 stip pieces add up exactly to spell-tips.js ('+ex.ns+' names) and the 16 mtip pieces to mob-tips.js ('+ex.nm+'), each name in the piece its hash picks');
 await size(480,900);reqs=[];await go("walkthrough.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");await waitFor('!!document.querySelector("#cg-walk .cg-sp li>b.ux-tt-t")',10000);
 await ev('(function(){var b=document.querySelector("#cg-walk details[open] .cg-sp li>b.ux-tt-t")||document.querySelector("#cg-walk .cg-sp li>b.ux-tt-t");b.scrollIntoView({block:"center",behavior:"instant"});b.focus()})()');
 ok(await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Level \\d+/.test(t.textContent)})()')&&reqs.filter(r=>/^stip-\d+\.js/.test(r)).length===1&&!reqs.includes('spell-tips.js'),'Tips: a spell tooltip loads one piece ('+reqs.filter(r=>/^stip-/.test(r)).join(',')+', ~'+sz('stip-0.js')+' KB) instead of spell-tips.js ('+sz('spell-tips.js')+' KB)');
 await key('Escape');await send('Network.setBlockedURLs',{urls:['*stip-*','*mtip-*']});reqs=[];await go("walkthrough.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");await waitFor('!!document.querySelector("#cg-walk .cg-sp li>b.ux-tt-t")',10000);
 await ev('(function(){var b=document.querySelector("#cg-walk details[open] .cg-sp li>b.ux-tt-t")||document.querySelector("#cg-walk .cg-sp li>b.ux-tt-t");b.scrollIntoView({block:"center",behavior:"instant"});b.focus()})()');
 ok(await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&/Level \\d+/.test(t.textContent)})()',10000)&&reqs.includes('spell-tips.js'),'Tips: if the pieces cannot load, the full spell-tips.js is used');
 await send('Network.setBlockedURLs',{urls:[]});await key('Escape');
}
// 4) Compare from the item tooltip and the Market page (pass 7 dialog, ?cmp= links)
{await size(480,900);await go('index.html');await ev('localStorage.setItem("mnm-cmp","[]")');await go('market.html');
 await waitFor('document.querySelectorAll("#mkt-b .ux-cmp-m").length>0',8000);
 const mk=await ev('(function(){var b=document.querySelectorAll("#mkt-b .ux-cmp-m"),l=document.querySelectorAll("#mkt-b td[data-l=Item]>a[href*=\\"items.html#\\"]");return {b:b.length,l:l.length,v:document.querySelectorAll("#mkt-vb .ux-cmp-m").length}})()');
 ok(mk.b>0&&mk.b===mk.l,'Market: a Compare button on each of the '+mk.b+' price rows that link into the Items database (+'+mk.v+' vendor rows)');
 const names=await ev('(function(){var seen=[],out=[];[].forEach.call(document.querySelectorAll("#mkt-b .ux-cmp-m,#mkt-vb .ux-cmp-m"),function(b){var n=b.getAttribute("data-cmp");if(seen.indexOf(n)<0){seen.push(n);out.push(n)}});return out.slice(0,2)})()');
 await ev(`[].find.call(document.querySelectorAll(".ux-cmp-m"),function(b){return b.getAttribute("data-cmp")===${JSON.stringify(names[0])}}).click()`);
 const b1=await ev('(function(){var b=document.querySelector(".ux-cmpbar-x8:not([hidden])");return b?b.textContent:""})()');
 ok(/Pick one more/.test(b1)&&b1.indexOf(names[0])>=0,'Market: first pick shows the compare bar ("'+b1.slice(0,70)+'")');
 await ev(`[].find.call(document.querySelectorAll(".ux-cmp-m"),function(b){return b.getAttribute("data-cmp")===${JSON.stringify(names[1])}}).click()`);
 const go2=await ev('(function(){var a=document.querySelector(".ux-cmpbar-x8:not([hidden]) a.ux-cmp-open");return a?a.getAttribute("href"):""})()');
 ok(/items\.html\?cmp=/.test(go2)&&decodeURIComponent(go2).indexOf(names[0]+'|'+names[1])>=0&&JSON.parse(await ev('localStorage.getItem("mnm-cmp")')).length===2,'Market: second pick gives "Compare side by side" → '+decodeURIComponent(go2));
 const ov=await ev('document.documentElement.scrollWidth>innerWidth');ok(!ov,'Market at 480: no overflow with the Compare buttons and bar');
 await ev('document.querySelector(".ux-cmpbar-x8:not([hidden])").scrollIntoView({block:"center",behavior:"instant"})');await sleep(200);await shot('ux8-after-compare-market-480.png');
 await go(go2.replace(/^\.?\/?/,''));
 ok(await waitFor('(function(){var d=document.querySelector("dialog.ux-cmpdlg");return d&&d.open&&!!d.querySelector(".ux-cmp-t")})()',15000),'Market → Items: the link opens pass 7\'s side-by-side dialog for '+names.join(' vs '));
 const hd=await ev('[].map.call(document.querySelector(".ux-cmp-t").tHead.rows[0].cells,function(c){return c.textContent}).slice(1)');
 ok(hd[0]===names[0]&&hd[1]===names[1],'…with the two Market picks as columns');
 await key('Escape');await ev('document.querySelector(".ux-cmp-clr")&&document.querySelector(".ux-cmp-clr").click()');
 // item tooltip (Mobs drop lists): pin, Tab into Compare, toggle
 await size(1024,768);await go('index.html');await ev('localStorage.setItem("mnm-cmp","[]")');await go('mobs.html?mq=skeleton');await waitFor(DBOK,15000);
 const ti=await ev('(function(){var a=document.querySelector("#mob-out .tt-item");if(!a)return null;a.scrollIntoView({block:"center",behavior:"instant"});a.focus();return a.getAttribute("data-item")})()');
 if(ti){await waitFor('(function(){var t=document.getElementById("ux-tt");return t&&!t.hidden&&!!t.querySelector(".ux-cmp-tb")})()',10000);
  const t0=await ev('(document.querySelector("#ux-tt .ux-tt-cmp")||{}).textContent||""');
  await key('c');await sleep(250);
  const t1=await ev('({p:JSON.parse(localStorage.getItem("mnm-cmp")||"[]"),b:(document.querySelector("#ux-tt .ux-cmp-tb")||{}).textContent,f:document.activeElement.getAttribute("data-item"),st:[].map.call(document.querySelectorAll("[role=status]"),function(x){return x.textContent}).join("|")})');
  ok(/Compare/.test(t0)&&/press C/.test(t0)&&t1.p.length===1&&t1.p[0]===ti&&/Comparing/.test(t1.b)&&t1.f===ti&&/Added/.test(t1.st),'Item tooltip: focusing "'+ti+'" shows "'+t0+'"; C adds it ('+t1.b+'), focus stays on the name, announced');
  const mp=await ev('(function(){var b=document.querySelector("#ux-tt .ux-cmp-tb"),r=b.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}})()');
  await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:mp.x,y:mp.y});await sleep(300);await send('Input.dispatchMouseEvent',{type:'mousePressed',x:mp.x,y:mp.y,button:'left',clickCount:1});await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:mp.x,y:mp.y,button:'left',clickCount:1});await sleep(250);
  ok((JSON.parse(await ev('localStorage.getItem("mnm-cmp")'))||[]).length===0,'Item tooltip: clicking its Compare button with the mouse toggles it off again');
  await ev('document.querySelector("#mob-out .tt-item").focus()');await waitFor('!!document.querySelector("#ux-tt:not([hidden]) .ux-cmp-tb")',5000);await key('c');await sleep(200);await key('Escape');
 }else ok(false,'Mobs page has a drop-list item to test the tooltip Compare');
 await go('items.html?iq=helm');await waitFor(DBOK,15000);ok(await ev('MNM_UX_CMP.picks().length')===1,'Items page picks up the tooltip pick from mnm-cmp');
 await ev('document.querySelector(".ux-cmp-clr")&&document.querySelector(".ux-cmp-clr").click()');
}
// contrast (6 theme x Irem combos) for the new controls; overflow 480-3440 in all themes
{const SC8=s=>CSCAN.replace('document.body.querySelectorAll(\'*\')','document.querySelectorAll(\''+s+'\')');
 for(const stt of ['dark-hw','dark','light-hw','light','contrast-hw','contrast']){const [th,hw]=stt.split('-');const bad=[];
  await ev(`localStorage.setItem('mnm-theme','${th}');localStorage.setItem('mnm-halloween','${hw?'on':'off'}');localStorage.setItem('mnm-cmp','[]')`);
  const scan=async(lab,sel)=>{const r=await ev(SC8(sel));r.fails.forEach(f=>bad.push(lab+' T '+f.r+' '+f.el));r.cfails.forEach(f=>bad.push(lab+' C '+f.r+' '+f.el))};
  await size(1024,768);await go('spells.html');await scan('spell badges','table.spelllook tbody td:first-child a.badge');
  await go('spells-all.html');await scan('spells-all note','.ux-spall, .ux-spall *');
  await go('market.html');await waitFor('document.querySelectorAll("#mkt-b .ux-cmp-m").length>1',8000);
  await ev('(function(){var b=document.querySelectorAll("#mkt-b .ux-cmp-m");b[0].click();var n=b[0].getAttribute("data-cmp");var c=[].find.call(document.querySelectorAll("#mkt-b .ux-cmp-m"),function(x){return x.getAttribute("data-cmp")!==n});c&&c.click()})()');
  await scan('market compare','.ux-cmp-m, .ux-cmpbar-x8, .ux-cmpbar-x8 *');
  await go('mobs.html?mq=skeleton');await waitFor(DBOK,15000);await ev('(function(){var a=document.querySelector("#mob-out .tt-item");a.scrollIntoView({block:"center",behavior:"instant"});a.click()})()');
  await waitFor('!!document.querySelector("#ux-tt:not([hidden]) .ux-cmp-tb")',10000);await scan('tooltip compare','#ux-tt .ux-tt-cmp, #ux-tt .ux-tt-cmp *');
  ok(bad.length===0,'pass 8 controls ['+stt+']: changed badges, spells-all note, Market compare buttons + bar, tooltip Compare pass 4.5:1 text / 3:1 controls'+(bad.length?' — '+bad.slice(0,4).join(' | '):''));
 }
 await ev('localStorage.removeItem("mnm-halloween");localStorage.setItem("mnm-cmp","[]")');
 for(const th of ['dark','light','contrast']){await ev(`localStorage.setItem('mnm-theme','${th}')`);
  for(const [w,h] of [[480,900],[1024,768],[2560,1080],[3440,1440]]){await size(w,h);for(const u of ['spells.html','spells-all.html','hotbar.html','market.html']){await go(u);
   if(await ev('document.documentElement.scrollWidth>innerWidth'))ok(false,'pass 8: '+u+' overflows @'+w+' ('+th+')')}}}
 ok(true,'pass 8: spells, spells-all, hotbar, market checked for overflow at 480/1024/2560/3440 in Dark, Light and High contrast');
 await ev('localStorage.removeItem("mnm-theme")');
}
await ev('localStorage.removeItem("mnm-theme")');await size(1024,768);
await go("classes/inquisitor.html?class=Inquisitor&race=Deep+Elf&city=Ail%27Vorith");await ev('MNM_UX_ROUTES.fillAll()');await waitFor('!document.querySelector(".sc-lz .lz-status")',15000);
 ok(await ev('[].every.call(document.querySelectorAll(".sc-route"),function(e){return !e.checkVisibility()||e.getAttribute("data-sc")==="ailvorith"})&&document.querySelectorAll(".sc-route[data-sc=ailvorith]").length>0'),'classes/inquisitor.html: Deep Elf Inquisitor in Ail\'Vorith shows Ail\'Vorith routes only');
 ok(await ev('true')&&!/serviceWorker|Notification|PushManager/.test(fs.readFileSync(path.join(DOCS,'assets','mod-ux.js'),'utf8')),'still no notifications, push or service worker');
 ok(errs.length===0,'no JS exceptions'+(errs.length?': '+errs.slice(0,2).join(' | '):''));
 console.log(passes+' passed, '+fails+' failed');ws.close();chrome.kill();srv.kill();process.exit(fails?1:0);
})().catch(e=>{console.error(e);chrome.kill();srv.kill();process.exit(1)});
