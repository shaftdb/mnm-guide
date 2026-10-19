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
 ok(await waitFor('document.querySelectorAll("#qres a[href]").length>3'),'search results appear once search-index.js loads ('+sz('search-index.js')+' KB, only when searching)');
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
 await send('Network.setBlockedURLs',{urls:['*search-index.js','*quick-c-bard.js']});
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
 ok(errs.length===0,'no JS exceptions'+(errs.length?': '+errs.slice(0,2).join(' | '):''));
 console.log(passes+' passed, '+fails+' failed');ws.close();chrome.kill();srv.kill();process.exit(fails?1:0);
})().catch(e=>{console.error(e);chrome.kill();srv.kill();process.exit(1)});
