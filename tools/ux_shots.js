// Layout screenshots + quick UX metrics for the UX passes.
// Usage: node --experimental-websocket tools/ux_shots.js <outdir> <tag>   -> <outdir>/ux1-<tag>-<page>-<width>.png
// Also prints per page/width: horizontal overflow, main column width, visible tap targets under 44px, sticky top-bar height.
const {spawn}=require('child_process'),http=require('http'),fs=require('fs'),path=require('path');
const DOCS=path.join(__dirname,'..','docs'),OUT=process.argv[2]||'/tmp',TAG=process.argv[3]||'shot',PFX=process.argv[4]||'ux1',PORT=8000+Math.floor(Math.random()*900);
const srv=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:DOCS,stdio:'ignore'});
const chrome=spawn('google-chrome',['--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--remote-debugging-port='+(PORT+1000),'--user-data-dir=/tmp/ux-chrome-'+PORT,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function getJSON(u){return new Promise((res,rej)=>http.get(u,r=>{let d='';r.on('data',x=>d+=x);r.on('end',()=>{try{res(JSON.parse(d))}catch(e){rej(e)}})}).on('error',rej))}
const ALLP={home:'index.html',class:'classes/inquisitor.html',walkthrough:'walkthrough.html',market:'market.html',items:'items.html',mobs:'mobs.html',shaman:'shaman/index.html','shaman-leveling':'shaman/leveling.html',spells:'spells.html',hotbar:'hotbar.html'};
// UX_PAGES=home,class,... picks pages (default: home,class,walkthrough,market); UX_SHOT_PAGES limits which get screenshots
const PAGES=(process.env.UX_PAGES||'home,class,walkthrough,market').split(',').map(n=>[n,ALLP[n]]),SHOTP=process.env.UX_SHOT_PAGES?process.env.UX_SHOT_PAGES.split(','):null;
const SIZES=(process.env.UX_SIZES||'480x900,1024x768,3440x1440').split(',').map(s=>s.split('x').map(Number));
(async()=>{
 let tabs;for(let i=0;i<50;i++){try{tabs=await getJSON('http://127.0.0.1:'+(PORT+1000)+'/json');break}catch(e){await sleep(200)}}
 const t=tabs.find(x=>x.type==='page');const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0,bytes=0,jsb=0,reqs=0;const pend={},errs=[],rt={};ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend[d.id]){pend[d.id](d);delete pend[d.id]}else if(d.method==='Runtime.exceptionThrown')errs.push(JSON.stringify(d.params.exceptionDetails).slice(0,300));
  else if(d.method==='Network.responseReceived')rt[d.params.requestId]=d.params.type;else if(d.method==='Network.loadingFinished'){bytes+=d.params.encodedDataLength;reqs++;if(rt[d.params.requestId]==='Script')jsb+=d.params.encodedDataLength}};
 const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}))});
 const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true});return r.result.result&&r.result.result.value};
 await send('Page.enable');await send('Runtime.enable');await send('Network.enable');await send('Network.setCacheDisabled',{cacheDisabled:true});const W={};
 for(const [w,h] of SIZES){
  await send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
  if(w<600)await send('Emulation.setTouchEmulationEnabled',{enabled:true});else await send('Emulation.setTouchEmulationEnabled',{enabled:false});
  for(const [name,u] of PAGES){
   bytes=0;jsb=0;reqs=0;await send('Page.navigate',{url:'http://127.0.0.1:'+PORT+'/'+u});
   for(let i=0;i<150;i++){await sleep(100);if(await ev('document.readyState==="complete"'))break}await sleep(1500);
   if(!W[name])W[name]={total_kb:Math.round(bytes/1024),js_kb:Math.round(jsb/1024),requests:reqs,width:w};
   const m=await ev(`(function(){var mn=document.querySelector('.main'),top=document.querySelector('.top');
     var small=0,tot=0;document.querySelectorAll('.top a,.top button,.top select,.top input,.rangebar a,.rangebar select,.rangebar button,.rangebar input').forEach(function(e){var r=e.getBoundingClientRect();if(r.width&&r.height&&(!e.checkVisibility||e.checkVisibility({visibilityProperty:true}))){tot++;if(r.height<44&&r.width<44||r.height<${w<600?44:24})small++}});
     return {ovf:document.documentElement.scrollWidth>innerWidth,main:mn?Math.round(mn.getBoundingClientRect().width):0,topH:top?Math.round(top.getBoundingClientRect().height):0,small:small,tot:tot}})()`);
   console.log(name,w,JSON.stringify(m));
   if(SHOTP&&!SHOTP.includes(name))continue;
   const r=await send('Page.captureScreenshot',{format:'png'});
   fs.writeFileSync(path.join(OUT,`${PFX}-${TAG}-${name}-${w}.png`),Buffer.from(r.result.data,'base64'));
  }
 }
 console.log('WEIGHT '+JSON.stringify(W));if(process.env.UX_WEIGHT_OUT)fs.writeFileSync(process.env.UX_WEIGHT_OUT,JSON.stringify(W,null,1));
 console.log('js errors:',errs.length,errs.slice(0,3).join(' | '));
 ws.close();chrome.kill();srv.kill();process.exit(0);
})().catch(e=>{console.error(e);chrome.kill();srv.kill();process.exit(1)});
