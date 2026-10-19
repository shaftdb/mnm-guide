// Headless Chrome test for the Market page (incl. the server picker: default Tilustra, localStorage mnm-server, ?server=, ordering, badges) and the Items -> Market link.
// Usage: node --experimental-websocket tools/test_market_ui.js [shotdir]   (serves docs/ on a local port, needs google-chrome)
const {spawn}=require('child_process'),http=require('http'),fs=require('fs'),path=require('path');
const DOCS=path.join(__dirname,'..','docs'),SHOT=process.argv[2]||null,PORT=8000+Math.floor(Math.random()*900);
const srv=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:DOCS,stdio:'ignore'});
const chrome=spawn('google-chrome',['--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port='+(PORT+1000),'--user-data-dir=/tmp/mkt-chrome-'+PORT,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0,passes=0;function ok(c,m){if(c){passes++;console.log('PASS',m)}else{fails++;console.log('FAIL',m)}}
function getJSON(u){return new Promise((res,rej)=>http.get(u,r=>{let d='';r.on('data',x=>d+=x);r.on('end',()=>{try{res(JSON.parse(d))}catch(e){rej(e)}})}).on('error',rej))}
(async()=>{
 let tabs;for(let i=0;i<50;i++){try{tabs=await getJSON('http://127.0.0.1:'+(PORT+1000)+'/json');break}catch(e){await sleep(200)}}
 const t=tabs.find(x=>x.type==='page');const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pend={},errs=[];ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend[d.id]){pend[d.id](d);delete pend[d.id]}else if(d.method==='Runtime.exceptionThrown')errs.push(JSON.stringify(d.params.exceptionDetails).slice(0,300))};
 const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}))});
 const ev=async(expr)=>{const r=await send('Runtime.evaluate',{expression:expr,awaitPromise:true,returnByValue:true});if(r.result.exceptionDetails)throw new Error(expr+'\n'+JSON.stringify(r.result.exceptionDetails));return r.result.result.value};
 const size=async(w,h)=>send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
 const go=async(u,ready)=>{const url='http://127.0.0.1:'+PORT+'/'+u;await send('Page.navigate',{url});
   for(let i=0;i<100;i++){await sleep(100);try{if(await ev(`document.readyState==='complete'&&!!(${ready||'window.MNM_MKT'})`))break}catch(e){}}await sleep(200)};
 const shot=async(file,maxH)=>{if(!SHOT)return;const b=await ev(`(function(){var st=document.createElement('style');st.textContent='.top,header,.rangebar,#mnm-rangebar,.topbar{position:static!important}';document.head.appendChild(st);scrollTo(0,0);return {w:innerWidth,h:Math.min(document.documentElement.scrollHeight,${maxH})}})()`);
   const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:b.w,height:b.h,scale:1}});fs.writeFileSync(path.join(SHOT,file),Buffer.from(r.result.data,'base64'));console.log('shot',file)};
 await send('Page.enable');await send('Runtime.enable');
 const P=JSON.parse(fs.readFileSync(path.join(__dirname,'..','content','prices.json'),'utf8'));
 for(const W of [480,1280]){
  await size(W,900);await go('market.html?server=all');
  ok(await ev('MNM_MKT.rows.length')===P.entries.length,W+': all '+P.entries.length+' entries in market-db.js');
  ok(await ev('document.querySelectorAll("#mkt-b tr").length')===P.entries.length,W+': price table shows every row');
  ok(await ev('document.documentElement.scrollWidth-innerWidth')<=1,W+': no horizontal overflow');
  await ev('(function(){var q=document.getElementById("mkt-q");q.value="staff";q.dispatchEvent(new Event("input"))})()');
  const st=await ev('[].map.call(document.querySelectorAll("#mkt-b tr td:first-child"),function(td){return td.textContent})');
  ok(st.length>=4&&st.every(s=>/staff/i.test(s)),W+': search "staff" filters ('+st.length+' rows)');
  await ev('(function(){var q=document.getElementById("mkt-q");q.value="";q.dispatchEvent(new Event("input"));var k=document.getElementById("mkt-k");k.value="vendor_buys";k.dispatchEvent(new Event("change"))})()');
  ok(await ev('document.querySelectorAll("#mkt-b tr").length')===P.entries.filter(e=>e.kind==='vendor_buys').length,W+': type filter = vendor values only');
  await ev('(function(){var k=document.getElementById("mkt-k");k.value="";k.dispatchEvent(new Event("change"));var s=document.getElementById("mkt-sort");s.value="cp:-1";s.dispatchEvent(new Event("change"))})()');
  const first=await ev('document.querySelector("#mkt-b tr td:nth-child(2) b").textContent');
  const maxe=P.entries.reduce((a,e)=>e.cp>a.cp?e:a);ok(first===maxe.price,W+': sort price high-low puts '+maxe.price+' first (got '+first+')');
  if(W>600){await ev('document.querySelector("#mkt-t th[data-s=d] button").click()');const d=await ev('[].map.call(document.querySelectorAll("#mkt-b tr td:nth-child(5)"),function(td){return td.textContent.slice(0,10)})');
   ok(d.join()===d.slice().sort().reverse().join(),W+': header click sorts by date (newest first)');}
  const v=await ev('[].map.call(document.querySelectorAll("#mkt-vb tr"),function(tr){return tr.cells[0].textContent})');
  ok(v.length===P.entries.filter(e=>e.kind==='vendor_buys').length,W+': vendor values table rows');
  ok(await ev('document.querySelectorAll("#mkt-camps details").length')===P.camps.length,W+': '+P.camps.length+' money camps');
  ok(await ev('document.querySelectorAll("#mkt-camps a[href*=\'mobs.html#\']").length')>5,W+': camps link mobs');
  ok(await ev('document.querySelectorAll("#mkt-camps a[href*=\'zones/\'],#mkt-camps a[href*=\'dungeons/\']").length')>=P.camps.length,W+': camps link zones/dungeons');
  ok(await ev('!!document.querySelector("#mkt-cities details[open]")&&/Ail.Vorith/.test(document.querySelector("#mkt-cities details[open] summary").textContent)'),W+': Ail\'Vorith money notes open');
  ok(await ev('document.querySelectorAll(".nav a[href$=\'market.html\'], nav a[href$=\'market.html\']").length')>0,W+': nav entry for Market');
  await ev('document.getElementById("mkt-sort").value="i:1";document.getElementById("mkt-sort").dispatchEvent(new Event("change"))');
  
 }

 // ---- server picker
 const PK=['player_ask','player_bid','player_sale'],players=P.entries.filter(e=>PK.includes(e.kind)),tilu=players.filter(e=>e.server==='Tilustra');
 ok(P.entries.every(e=>e.server&&(PK.includes(e.kind)?e.server!=='all':e.server==='all')),'data: every entry has a server; vendor/official use "all"');
 await size(480,900);await go('market.html');await ev('localStorage.clear()');await go('market.html');
 ok(await ev('document.getElementById("mkt-s").value')==='Tilustra','default server is Tilustra');
 ok(await ev('localStorage.getItem("mnm-server")')==='Tilustra','default saved to localStorage mnm-server');
 ok(await ev('/[?&]server=Tilustra(&|$)/.test(location.search)'),'default written to URL ?server=Tilustra');
 const rows=await ev('[].map.call(document.querySelectorAll("#mkt-b tr"),function(tr){var b=tr.querySelector(".mkt-svb");return {sv:tr.getAttribute("data-sv"),k:tr.getAttribute("data-k"),g:+(tr.className.match(/mkt-g(\\d)/)||[0,9])[1],b:b?b.className+"|"+b.textContent:"",all:!!tr.querySelector(".mkt-svall")}})');
 ok(rows.length===P.entries.length,'Tilustra view still shows every row ('+rows.length+')');
 ok(rows.slice(0,tilu.length).every(r=>r.sv==='Tilustra'&&PK.includes(r.k))&&tilu.length>0,'Tilustra player prices first ('+tilu.length+')');
 ok(rows.every((r,i)=>i===0||rows[i-1].g<=r.g),'order: my server, then all-server vendor values, then other servers');
 ok(rows.filter(r=>r.sv==='Tilustra').every(r=>/mkt-mine/.test(r.b)&&/Your server: Tilustra/.test(r.b)),'Tilustra rows badged "Your server"');
 ok(rows.filter(r=>PK.includes(r.k)&&r.sv!=='Tilustra').every(r=>/mkt-other/.test(r.b)&&/Other server: /.test(r.b)),'every other-server player row badged "Other server"');
 ok(rows.filter(r=>!PK.includes(r.k)).every(r=>r.all&&!r.b),'vendor/official rows marked "All servers", no server badge');
 ok(await ev('document.querySelectorAll("#mkt-vb tr").length')===P.entries.filter(e=>e.kind==='vendor_buys').length,'vendor values table shows all vendor values on Tilustra');
 ok(/Tilustra:.*1 player price/.test(await ev('document.getElementById("mkt-snote").textContent')),'note counts Tilustra player prices');
 ok(await ev('document.documentElement.scrollWidth-innerWidth')<=1,'480: no horizontal overflow with server picker');
 await shot('market-server-480.png',2200);
 await ev('(function(){var b=document.getElementById("mkt-only");b.checked=true;b.dispatchEvent(new Event("change"))})()');
 ok(await ev('document.querySelectorAll("#mkt-b .mkt-other").length')===0&&await ev('document.querySelectorAll("#mkt-b tr").length')===P.entries.length-players.length+tilu.length,'"Hide other servers" hides only other-server player prices');
 await ev('(function(){var b=document.getElementById("mkt-only");b.checked=false;b.dispatchEvent(new Event("change"));var s=document.getElementById("mkt-s");s.value="Trem";s.dispatchEvent(new Event("change"))})()');
 ok(await ev('localStorage.getItem("mnm-server")')==='Trem'&&await ev('/[?&]server=Trem(&|$)/.test(location.search)'),'changing to Trem updates localStorage and URL');
 ok(await ev('document.querySelector("#mkt-b tr").getAttribute("data-sv")')==='Trem','Trem rows first after switching');
 await go('market.html');
 ok(await ev('document.getElementById("mkt-s").value')==='Trem','Trem persists across reload (localStorage)');
 await go('market.html?server=Estaire');
 ok(await ev('document.getElementById("mkt-s").value')==='Estaire'&&await ev('localStorage.getItem("mnm-server")')==='Estaire','URL ?server=Estaire overrides and is saved');
 await go('market.html?server=Tulistra');
 ok(await ev('document.getElementById("mkt-s").value')==='Tilustra','?server=Tulistra (misspelling) maps to Tilustra');
 await go('market.html?server=Nunavoth');
 const nn=await ev('document.getElementById("mkt-snote").textContent');
 ok(/No player listings for Nunavoth yet/.test(nn),'server with no listings says so plainly');
 ok(await ev('document.querySelectorAll("#mkt-b tr").length')===P.entries.length,'...and still shows every row (nothing hidden)');
 await go('market.html?server=all');
 ok(await ev('document.getElementById("mkt-s").value')===''&&await ev('document.querySelectorAll("#mkt-b .mkt-other").length')===0,'?server=all: no preference, no "other server" badges');
 await ev('localStorage.clear()');
 await size(1280,900);await go('market.html?server=all#Wolf%20Blood');
 ok(await ev('document.querySelectorAll("#mkt-b tr").length')===2,'hash prefill market.html#Wolf Blood shows 2 rows');
 await go('items.html#Cracked%20Elderwood%20Staff','window.MNM_IDB');
 const ml=await ev('(function(){var a=document.querySelector("#idb-out a.idb-mkt");return a?a.getAttribute("href")+"|"+a.textContent:null})()');
 ok(ml&&/market\.html#Cracked%20Elderwood%20Staff/.test(ml)&&/27 sp 17 cp/.test(ml),'Items page shows Market link with price ('+ml+')');
 ok(await ev('!!document.querySelector("a[href$=\'market.html\']")'),'Items page links to Market');
 ok(errs.length===0,'no JS exceptions'+(errs.length?': '+errs.join(' | '):''));
 console.log(passes+' passed, '+fails+' failed');ws.close();chrome.kill();srv.kill();process.exit(fails?1:0);
})().catch(e=>{console.error(e);chrome.kill();srv.kill();process.exit(2)});
