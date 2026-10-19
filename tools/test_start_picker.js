// Headless Chrome test: walks every race x class x city and checks the Race/Start pickers' enabled/disabled state, reason text,
// the "Valid starts" line and persistence (localStorage + URL) against docs/assets/chargen-data.js.
// Usage: node --experimental-websocket tools/test_start_picker.js [shotdir]
const {spawn}=require('child_process'),http=require('http'),fs=require('fs'),path=require('path');
const DOCS=path.join(__dirname,'..','docs'),SHOT=process.argv[2]||null,PORT=8000+Math.floor(Math.random()*900);
const srv=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:DOCS,stdio:'ignore'});
const chrome=spawn('google-chrome',['--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port='+(PORT+1000),'--user-data-dir=/tmp/sp-chrome-'+PORT,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0,passes=0;function ok(c,m){if(c){passes++;console.log('PASS',m)}else{fails++;console.log('FAIL',m)}}
function getJSON(u){return new Promise((res,rej)=>http.get(u,r=>{let d='';r.on('data',x=>d+=x);r.on('end',()=>{try{res(JSON.parse(d))}catch(e){rej(e)}})}).on('error',rej))}
(async()=>{
 let tabs;for(let i=0;i<50;i++){try{tabs=await getJSON('http://127.0.0.1:'+(PORT+1000)+'/json');break}catch(e){await sleep(200)}}
 const t=tabs.find(x=>x.type==='page');const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pend={},errs=[];ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend[d.id]){pend[d.id](d);delete pend[d.id]}else if(d.method==='Runtime.exceptionThrown')errs.push(JSON.stringify(d.params.exceptionDetails).slice(0,300))};
 const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}))});
 const ev=async(expr)=>{const r=await send('Runtime.evaluate',{expression:expr,awaitPromise:true,returnByValue:true});if(r.result.exceptionDetails)throw new Error(expr.slice(0,200)+'\n'+JSON.stringify(r.result.exceptionDetails).slice(0,600));return r.result.result.value};
 const size=async(w,h)=>send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
 const go=async(u)=>{const url='http://127.0.0.1:'+PORT+'/'+u;await send('Page.navigate',{url});
   for(let i=0;i<100;i++){await sleep(100);try{if(await ev(`document.readyState==='complete'&&!!window.MNM_CHARGEN&&document.getElementById('mnm-race').options.length>0`))break}catch(e){}}await sleep(200)};
 const shot=async(file,sel,h)=>{if(!SHOT)return;const b=await ev(`(function(){var st=document.createElement('style');st.textContent='.top,header,.rangebar,#mnm-rangebar{position:static!important}';document.head.appendChild(st);scrollTo(0,0);var r=document.querySelector(${JSON.stringify(sel)}).getBoundingClientRect();return {w:innerWidth,h:Math.min(r.bottom+scrollY+10,${h})}})()`);
   const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:b.w,height:b.h,scale:1}});fs.writeFileSync(path.join(SHOT,file),Buffer.from(r.result.data,'base64'));console.log('shot',file)};
 await send('Page.enable');await send('Runtime.enable');
 const G=JSON.parse(fs.readFileSync(path.join(DOCS,'assets','chargen-data.js'),'utf8').replace(/^window\.MNM_CG=/,'').replace(/;\s*$/,''));
 const A=JSON.parse(fs.readFileSync(path.join(__dirname,'..','data','start_audit.json'),'utf8'));
 const classes=Object.keys(G.combos).sort(),ALLR=G.playable,CITIES=G.cities;
 ok(classes.length===18&&ALLR.length===9&&CITIES.length===4,'data: 18 classes, 9 playable races, 4 cities');
 ok(G.audit&&G.audit.rev===A.start_table.revid,'audit revision recorded in picker data (rev '+(G.audit||{}).rev+')');
 ok((G.combos.Enchanter.Human||[]).join()==='Night Harbor'&&G.notes['Enchanter|Human|Night Harbor'],'override: Human Enchanter starts in Night Harbor, with a note');
 ok(!(G.combos.Inquisitor['Deep Elf']||[]).includes('Underdocks')&&(G.combos.Archer['Deep Elf']||[]).includes('Underdocks'),'Deep Elf: Underdocks for Archer but not Inquisitor');
 const cfc=(r,c)=>CITIES.filter(t=>(G.combos[c][r]||[]).includes(t));
 const classesFor=r=>classes.filter(c=>G.combos[c][r]);const classesForCity=(r,t)=>classes.filter(c=>(G.combos[c][r]||[]).includes(t));
 await size(480,900);await go('index.html');await ev('localStorage.clear()');await go('index.html');
 let combos=0,bad=[];
 for(const c of classes){
  await sleep(1500); // Chrome throttles history.replaceState (~200 calls / 10 s); pace the walk so URL persistence is real, not throttled
  await ev(`(function(){var s=document.getElementById('mnm-class');s.value=${JSON.stringify(c)};s.dispatchEvent(new Event('change'))})()`);await sleep(60);
  const ro=await ev(`[].map.call(document.getElementById('mnm-race').options,function(o){return {v:o.value,d:o.disabled,a:o.getAttribute('aria-disabled'),t:o.title,x:o.textContent}})`);
  if(ro.map(o=>o.v).join()!==ALLR.slice().sort((a,b)=>(G.large.includes(a))-(G.large.includes(b))||a.localeCompare(b)).join())bad.push(c+': race list '+ro.map(o=>o.v).join());
  for(const o of ro){const valid=!!G.combos[c][o.v];
   if(o.d===valid)bad.push(c+'/'+o.v+': race disabled='+o.d);
   if(!valid){const cs=classesFor(o.v),want=o.v+': not available as '+c+(cs.length?'; '+o.v+' can be '+cs.join(', '):'; not playable in Early Access');
    if(o.t!==want)bad.push(c+'/'+o.v+': race title "'+o.t+'"');if(!o.x.includes('(not for '+c+')'))bad.push(c+'/'+o.v+': race text "'+o.x+'"');if(o.a!=='true')bad.push(c+'/'+o.v+': no aria-disabled');}}
  for(const r of Object.keys(G.combos[c])){
   await ev(`(function(){var s=document.getElementById('mnm-race');s.value=${JSON.stringify(r)};s.dispatchEvent(new Event('change'))})()`);
   const st=await ev(`(function(){return {opts:[].map.call(document.getElementById('mnm-city').options,function(o){return {v:o.value,d:o.disabled,a:o.getAttribute('aria-disabled'),t:o.title,x:o.textContent}}),sel:document.getElementById('mnm-city').value,line:document.getElementById('cg-valid').textContent,why:(document.querySelector('#cg-valid .cg-why')||{}).textContent||''}})()`);
   const okc=cfc(r,c);
   if(st.opts.map(o=>o.v).join()!==CITIES.join())bad.push(c+'/'+r+': city list');
   if(!okc.includes(st.sel))bad.push(c+'/'+r+': selected city '+st.sel+' not valid');
   if(!st.line.includes('Valid starts for '+r+':'))bad.push(c+'/'+r+': no valid-starts line');
   if(!st.line.includes(r+' '+c+': '+(okc.length?okc.join(', '):'no start')))bad.push(c+'/'+r+': current-starts text');
   for(const t of CITIES)if(classesForCity(r,t).length&&!st.line.includes(t+' ('))bad.push(c+'/'+r+': valid line misses '+t);
   for(const o of st.opts){combos++;const valid=okc.includes(o.v);
    if(o.d===valid)bad.push(c+'/'+r+'/'+o.v+': city disabled='+o.d);
    if(!valid){const cs=classesForCity(r,o.v),want=o.v+': not available for '+r+' '+c+(cs.length?'; available for '+r+' '+cs.join(', '):'; not available for any '+r+' class');
     if(o.t!==want)bad.push(c+'/'+r+'/'+o.v+': title "'+o.t+'"');if(!o.x.includes('(not for '+r+' '+c+')'))bad.push(c+'/'+r+'/'+o.v+': text "'+o.x+'"');
     if(o.a!=='true')bad.push(c+'/'+r+'/'+o.v+': no aria-disabled');if(!st.why.includes(want))bad.push(c+'/'+r+'/'+o.v+': reason not in visible list');}}
   for(const t of okc){await ev(`(function(){var s=document.getElementById('mnm-city');s.value=${JSON.stringify(t)};s.dispatchEvent(new Event('change'))})()`);
    const p=await ev(`[localStorage.getItem('mnm-race'),localStorage.getItem('mnm-city'),new URLSearchParams(location.search).get('race'),new URLSearchParams(location.search).get('city'),new URLSearchParams(location.search).get('class')]`);
    if(p.join('|')!==[r,t,r,t,c].join('|'))bad.push(c+'/'+r+'/'+t+': persistence '+p.join('|'));}
  }}
 ok(bad.length===0,'walked '+combos+' race x class x city options: enabled/disabled, reasons, valid line, persistence'+(bad.length?' — '+bad.length+' problems: '+bad.slice(0,8).join(' ; '):''));
 // persistence across reload, invalid URL city rejected
 await go('index.html?class=Inquisitor&race=Deep%20Elf&city=Ail%27Vorith');
 ok(await ev(`[document.getElementById('mnm-class').value,document.getElementById('mnm-race').value,document.getElementById('mnm-city').value].join('|')`)==="Inquisitor|Deep Elf|Ail'Vorith",'URL picks load (Deep Elf Inquisitor, Ail\'Vorith)');
 await go('index.html');
 ok(await ev(`[document.getElementById('mnm-race').value,document.getElementById('mnm-city').value,localStorage.getItem('mnm-race'),localStorage.getItem('mnm-city')].join('|')`)==="Deep Elf|Ail'Vorith|Deep Elf|Ail'Vorith",'picks persist across reload (localStorage)');
 await go('index.html?class=Inquisitor&race=Deep%20Elf&city=Underdocks');
 ok(await ev(`document.getElementById('mnm-city').value`)==="Ail'Vorith",'invalid URL city (Underdocks for Deep Elf Inquisitor) falls back to a valid start');
 const ud=await ev(`(function(){var o=[].find.call(document.getElementById('mnm-city').options,function(o){return o.value==='Underdocks'});return {d:o.disabled,t:o.title,x:o.textContent}})()`);
 ok(ud.d&&/^Underdocks: not available for Deep Elf Inquisitor; available for Deep Elf Archer, Cleric, /.test(ud.t)&&/\(not for Deep Elf Inquisitor\)/.test(ud.x),'Underdocks greyed for Deep Elf Inquisitor with reason: '+ud.t);
 ok(await ev('document.documentElement.scrollWidth-innerWidth')<=1,'480: no horizontal overflow');
 if(SHOT){await ev(`(function(){document.querySelector('#cg-valid .cg-why').open=true;var s=document.getElementById('mnm-city');s.size=4})()`);await shot('start-audit-picker-480.png','#cg-valid',1400);
  await ev(`(function(){document.getElementById('mnm-city').size=0;var s=document.getElementById('mnm-race');s.size=9;document.querySelector('#cg-valid .cg-why').open=true})()`);await shot('start-audit-race-480.png','#cg-valid',1600);}
 await go('index.html?class=Enchanter&race=Human&city=Night%20Harbor');
 ok(/unverified/i.test(await ev(`document.getElementById('cg-valid').textContent`))&&/\(unverified\)/.test(await ev(`document.getElementById('mnm-city').selectedOptions[0].textContent`)),'Human Enchanter Night Harbor marked unverified');
 await ev('localStorage.clear()');
 ok(errs.length===0,'no JS exceptions'+(errs.length?': '+errs.join(' | '):''));
 console.log(passes+' passed, '+fails+' failed');ws.close();chrome.kill();srv.kill();process.exit(fails?1:0);
})().catch(e=>{console.error(e);chrome.kill();srv.kill();process.exit(2)});
