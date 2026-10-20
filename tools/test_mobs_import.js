// Headless Chrome test for the mob/item import: Great Cavern Sea zone page, Mobs and Items DB, source flags, map link, 480px layout.
// Usage: node --experimental-websocket tools/test_mobs_import.js [shotdir]   (shotdir gets gcs-zone-480.png)
const {spawn}=require('child_process'),http=require('http'),fs=require('fs'),path=require('path');
const DOCS=path.join(__dirname,'..','docs'),SHOT=process.argv[2]||null,PORT=8000+Math.floor(Math.random()*900);
const srv=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:DOCS,stdio:'ignore'});
const chrome=spawn('google-chrome',['--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port='+(PORT+1000),'--user-data-dir=/tmp/mi-chrome-'+PORT,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0,passes=0;function ok(c,m){if(c){passes++;console.log('PASS',m)}else{fails++;console.log('FAIL',m)}}
function getJSON(u){return new Promise((res,rej)=>http.get(u,r=>{let d='';r.on('data',x=>d+=x);r.on('end',()=>{try{res(JSON.parse(d))}catch(e){rej(e)}})}).on('error',rej))}
const SC=JSON.parse(fs.readFileSync(path.join(__dirname,'..','content','source_conflicts.json'),'utf8'));
// conflict examples come from the current data (they change every refresh as the sources catch up)
const MOBC=(SC.conflicts.find(c=>c.type==='mob')||{}).entity,ITEMC=(SC.conflicts.find(c=>c.type==='item')||{}).entity,NCONF=SC.conflicts.length+((SC.manual||[]).length);
(async()=>{try{
 let tabs;for(let i=0;i<50;i++){try{tabs=await getJSON('http://127.0.0.1:'+(PORT+1000)+'/json');break}catch(e){await sleep(200)}}
 const t=tabs.find(x=>x.type==='page');const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pend={},errs=[];ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend[d.id]){pend[d.id](d);delete pend[d.id]}else if(d.method==='Runtime.exceptionThrown')errs.push(JSON.stringify(d.params.exceptionDetails).slice(0,300))};
 const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}))});
 const ev=async(expr)=>{const r=await send('Runtime.evaluate',{expression:expr,awaitPromise:true,returnByValue:true});if(r.result.exceptionDetails)throw new Error(expr.slice(0,200)+'\n'+JSON.stringify(r.result.exceptionDetails).slice(0,600));return r.result.result.value};
 const size=async(w,h)=>send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
 const go=async(u,ready)=>{await send('Page.navigate',{url:'http://127.0.0.1:'+PORT+'/'+u});for(let i=0;i<150;i++){await sleep(100);try{if(await ev(`document.readyState==='complete'&&(${ready||'true'})`))break}catch(e){}}await sleep(300)};
 await send('Page.enable');await send('Runtime.enable');
 // UX pass 6: Items/Mobs rows fill in from on-demand pieces; wait until the first rows and the full search text are in
 const DBOK="(function(){var s=document.querySelector('.ux-dbst');return (!s||s.hidden)&&[].slice.call(document.querySelectorAll('#mob-out [data-id],#idb-out [data-id]'),0,5).every(function(e){return !e.classList.contains('ux-dbp')})})()";const settle=async()=>{for(let i=0;i<100;i++){if(await ev(DBOK))return;await sleep(100)}};
 await size(480,900);await go('zones/great-cavern-sea.html');
 const z=await ev(`(function(){var t=document.body.innerText;return {t:t,ov:document.documentElement.scrollWidth>innerWidth+1,qn:!!document.getElementById('quest-npcs'),named:document.querySelectorAll('#named ~ .tw tbody tr, #named + .tw tbody tr').length}})()`);
 ok(/camps 11–30; named 15–60/.test(z.t),'GCS quick facts show mob level range 11–30 (named to 60)');
 ok(z.qn&&/Sereth Vael'xirith/.test(z.t)&&/Mae'vith Ith'vayen/.test(z.t),'GCS Quest NPCs section lists Sereth and Mae\'vith');
 for(const n of ['Foreman Vikkit','Skerrick','Tibbek','Overseer Vashruk','a strand spider','a goblin stone-sorter','a recess basilisk','Old Brinehide'])ok(z.t.includes(n),'GCS lists '+n);
 ok(!/Example NPC/.test(z.t),'placeholder "Example NPC" row skipped');
 ok(/Vikkit's Chain Cap/.test(z.t)&&/Bundle of Copied Marks/.test(z.t),'GCS shows new drops (Vikkit\'s Chain Cap, Bundle of Copied Marks)');
 ok(!z.ov,'480px: GCS page has no horizontal overflow');
 if(SHOT){const h=await ev(`Math.min(document.documentElement.scrollHeight,5200)`);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:480,height:h,scale:1}});fs.writeFileSync(path.join(SHOT,'gcs-zone-480.png'),Buffer.from(r.result.data,'base64'));console.log('shot gcs-zone-480.png')}
 await go('zones/night-harbor.html');ok(await ev(`!!document.querySelector('a.maplink[href="https://www.mnmatlas.com/night-harbor/"]')`),'Night Harbor zone page has the sourced mnmatlas Map link');
 await go('zones/great-cavern-sea.html');ok(await ev(`!document.querySelector('a.maplink')`),'no Map link where no sourced map address exists (GCS)');
 await size(1280,900);await go('mobs.html','!!window.MNM_MOBS&&'+DBOK);
 await ev(`(function(){var q=document.getElementById('mob-q');q.value='Great Cavern Sea';q.dispatchEvent(new Event('input'))})()`);await sleep(50);await settle();
 const m=await ev(`({c:document.getElementById('mob-count').textContent,t:document.getElementById('mob-out').innerText})`);
 ok(parseInt(m.c)>=30,'Mobs DB: Great Cavern Sea search finds '+m.c);
 ok(/Foreman Vikkit/.test(m.t)&&/quest NPC/.test(m.t),'Mobs DB shows GCS named and quest NPC tags');
 await ev(`(function(){var q=document.getElementById('mob-q');q.value=${JSON.stringify(MOBC||'')};q.dispatchEvent(new Event('input'))})()`);await sleep(50);await settle();
 ok(await ev(`!!document.querySelector('#mob-out .tag.conf')`),'Mobs DB flags a wiki/mnm-db level conflict visibly');
 await ev(`(function(){var q=document.getElementById('mob-q');q.value='a rotting skeleton';q.dispatchEvent(new Event('input'))})()`);await sleep(50);await settle();
 ok(/Seen \(mnm-db/.test(await ev(`document.getElementById('mob-out').innerText`)),'Mobs DB shows mnm-db observed drops');
 await go('items.html#'+encodeURIComponent("Vikkit's Chain Cap"),'!!window.MNM_IDB&&'+DBOK);
 const it=await ev(`document.getElementById('idb-out').innerText`);ok(/Foreman Vikkit/.test(it)&&/Great Cavern Sea/.test(it),'Items DB: Vikkit\'s Chain Cap drops from Foreman Vikkit, Great Cavern Sea');
 await go('items.html?b#'+encodeURIComponent('Bone Chips'),'!!window.MNM_IDB&&'+DBOK);ok(await ev(`/mnm-db/.test(document.getElementById('idb-out').innerText)`),'Items DB shows mnm-db drop sources');
 if(ITEMC){await go('items.html?c#'+encodeURIComponent(ITEMC),'!!window.MNM_IDB&&'+DBOK);ok(await ev(`!!document.querySelector('#idb-out .tag.conf')`),'Items DB flags a source conflict visibly ('+ITEMC+')');}else console.log('SKIP Items DB conflict flag: no item conflicts in this refresh');
 await go('source-conflicts.html');ok(await ev(`document.querySelectorAll('table tbody tr').length>=${NCONF}`),'Source conflicts page lists all '+NCONF+' conflicts');
 const hb=fs.readFileSync(path.join(DOCS,'assets','hotbar-items.js'),'utf8');ok(hb.includes("Vikkit's Chain Cap"),'character sheet data (hotbar-items.js) includes new GCS gear');
 ok(errs.length===0,'no JS exceptions'+(errs.length?' '+errs[0]:''));
}catch(e){fails++;console.log('FAIL exception',e.message)}
 console.log(passes+' passed, '+fails+' failed');chrome.kill();srv.kill();process.exit(fails?1:0)})();
