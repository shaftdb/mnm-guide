// Headless Chrome test for the Hotbar planner (/hotbar.html): drag, tap and keyboard placement, bar rules, layouts, keybinds,
// persistence, URL share (#hb=), import/export, undo, focus mode (+Esc, size, print), character sheet totals, 480px with no overflow.
// Usage: node --experimental-websocket tools/test_hotbar_ui.js [shotdir]   (serves docs/ on a local port, needs google-chrome)
const {spawn}=require('child_process'),http=require('http'),fs=require('fs'),path=require('path');
const DOCS=path.join(__dirname,'..','docs'),SHOT=process.argv[2]||null,PORT=8000+Math.floor(Math.random()*900);
const srv=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:DOCS,stdio:'ignore'});
const chrome=spawn('google-chrome',['--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port='+(PORT+1000),'--user-data-dir=/tmp/hb-chrome-'+PORT,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0,passes=0;function ok(c,m){if(c){passes++;console.log('PASS',m)}else{fails++;console.log('FAIL',m)}}
function getJSON(u){return new Promise((res,rej)=>http.get(u,r=>{let d='';r.on('data',x=>d+=x);r.on('end',()=>{try{res(JSON.parse(d))}catch(e){rej(e)}})}).on('error',rej))}
const HBD=(()=>{const s=fs.readFileSync(path.join(DOCS,'assets','hotbar-data.js'),'utf8');return JSON.parse(s.slice(s.indexOf('=')+1,s.lastIndexOf(';')))})();
(async()=>{
 let tabs;for(let i=0;i<50;i++){try{tabs=await getJSON('http://127.0.0.1:'+(PORT+1000)+'/json');break}catch(e){await sleep(200)}}
 const t=tabs.find(x=>x.type==='page');const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pend={},errs=[];ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend[d.id]){pend[d.id](d);delete pend[d.id]}else if(d.method==='Runtime.exceptionThrown')errs.push(JSON.stringify(d.params.exceptionDetails).slice(0,400))};
 const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}))});
 const ev=async(expr)=>{const r=await send('Runtime.evaluate',{expression:expr,awaitPromise:true,returnByValue:true});if(r.result.exceptionDetails)throw new Error(expr+'\n'+JSON.stringify(r.result.exceptionDetails));return r.result.result.value};
 const size=async(w,h)=>send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
 const go=async(u,ready)=>{const url='http://127.0.0.1:'+PORT+'/'+u;await send('Page.navigate',{url});
   for(let i=0;i<100;i++){await sleep(100);try{if(await ev(`document.readyState==='complete'&&!!(${ready||'window.MNM_HB_API&&document.querySelector(".hb-slot")'})`))break}catch(e){}}await sleep(250)};
 const key=async(k,code,vk)=>{await send('Input.dispatchKeyEvent',Object.assign({type:'keyDown',key:k,code:code||k,windowsVirtualKeyCode:vk||0,nativeVirtualKeyCode:vk||0},k==='Enter'?{text:'\r',unmodifiedText:'\r'}:{}));await send('Input.dispatchKeyEvent',{type:'keyUp',key:k,code:code||k,windowsVirtualKeyCode:vk||0,nativeVirtualKeyCode:vk||0});await sleep(60)};
 const slot=s=>ev(`(function(){var b=document.querySelector('.hb-slot[data-s="${s}"]');return b?b.querySelector('.hb-n').textContent:null})()`);
 const st=()=>ev('JSON.stringify(MNM_HB_API.state())').then(JSON.parse);
 const shot=async(file,maxH)=>{if(!SHOT)return;const b=await ev(`(function(){scrollTo(0,0);return {w:innerWidth,h:Math.min(document.documentElement.scrollHeight,${maxH})}})()`);
   const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:b.w,height:b.h,scale:1}});fs.writeFileSync(path.join(SHOT,file),Buffer.from(r.result.data,'base64'));console.log('shot',file)};
 const shotEl=async(file,sel)=>{if(!SHOT)return;const b=await ev(`(function(){var st=document.createElement('style');st.textContent='.top,header,.rangebar,#mnm-rangebar{position:static!important}';document.head.appendChild(st);var r=document.querySelector('${sel}').getBoundingClientRect();return {x:0,y:Math.max(0,r.top+scrollY-8),w:innerWidth,h:Math.min(r.height+16,2400)}})()`);
   const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:b.x,y:b.y,width:b.w,height:b.h,scale:1}});fs.writeFileSync(path.join(SHOT,file),Buffer.from(r.result.data,'base64'));console.log('shot',file)};
 // synthetic HTML5 drag: dragstart on source, dragover + drop on target, dragend (same DataTransfer object, as a real drag)
 const dnd=(src,dst)=>ev(`(function(){var a=document.querySelector(${JSON.stringify(src)}),b=document.querySelector(${JSON.stringify(dst)});if(!a||!b)return 'missing';var dt=new DataTransfer();
   function f(el,t){var x=new DragEvent(t,{bubbles:true,cancelable:true,dataTransfer:dt});el.dispatchEvent(x);return x}
   f(a,'dragstart');var o=f(b,'dragover');f(b,'drop');f(a,'dragend');return o.defaultPrevented?'accepted':'refused'})()`);
 await send('Page.enable');await send('Runtime.enable');
 const C='Inquisitor',INQ=HBD.classes[C];
 await size(1280,900);await go('hotbar.html');
 await ev(`localStorage.clear();localStorage.setItem('mnm-class','${C}');localStorage.setItem('mnm-race','Deep Elf');localStorage.setItem('mnm-city',"Ail'Vorith");localStorage.setItem('mnm-range','11-15')`);
 await go('hotbar.html');
 ok(await ev('document.getElementById("mnm-class").value')===C&&await ev('document.getElementById("mnm-race").value')==='Deep Elf','reads shared Class/Race pickers');
 ok(await ev('+document.getElementById("hb-level").value')===15,'level defaults to top of the 11-15 band');
 ok(await ev('document.querySelectorAll(".hb-ab .hb-slot").length')===10&&await ev('document.querySelectorAll(".hb-hb .hb-slot").length')===24&&await ev('document.querySelectorAll(".hb-au .hb-slot").length')===10,'bars: 10 ability, 2x12 hotbar (default pages), 10 aura');
 let S=await st();const L0=S.cls[C].L.solo;
 const names=new Set(INQ.spells.map(s=>s[0])),lv=n=>INQ.spells.find(s=>s[0]===n)[1];
 const sab=L0.ab.filter(Boolean);ok(sab.length>=6&&sab.every(e=>names.has(e.n)&&lv(e.n)<=15),'suggested solo ability bar: '+sab.length+' real Inquisitor spells, all level <=15 ('+sab.map(e=>e.n).join(', ')+')');
 ok(Object.keys(L0.why).length>=sab.length,'every suggested pick has a reason');
 ok(L0.au.filter(Boolean).every(e=>/^Aura of/.test(e.n)),'aura bar suggestions are auras only ('+L0.au.filter(Boolean).map(e=>e.n).join(', ')+')');
 const groupAb=S.cls[C].L.group.ab.filter(Boolean).map(e=>e.n);ok(groupAb.slice(0,2).every(n=>INQ.spells.find(s=>s[0]===n)[7].includes('threat')),'group tank layout starts with threat abilities ('+groupAb.slice(0,2).join(', ')+')');
 const pal=await ev('[].map.call(document.querySelectorAll(".hb-pi"),function(b){return b.querySelector(".hb-pn").textContent})');
 ok(pal.length>10&&pal.filter(n=>names.has(n)).every(n=>lv(n)<=15),'palette level-gated: '+pal.length+' items, no spell above 15');
 ok(await ev('(function(){var b=document.querySelector(".hb-pi");b.dispatchEvent(new MouseEvent("mouseover",{bubbles:true}));var t=document.getElementById("hb-tip");return !t.hidden&&/Level/.test(t.textContent)&&/Cost/.test(t.textContent)&&/Source/.test(t.textContent)})()'),'tooltip shows level, cost and source');
 await shot('hotbar-desktop.png',1500);
 // clear and place by drag
 await ev('document.getElementById("hb-clear").click()');ok(await slot('ab:0')==='empty','Clear layout empties the bars');
 const p0=pal[0],p0i=0;
 ok(await dnd('.hb-pi[data-i="0"]','.hb-slot[data-s="ab:0"]')==='accepted'&&await slot('ab:0')===p0,'drag palette -> ability slot 1 places '+p0);
 ok(await dnd('.hb-pi[data-i="1"]','.hb-slot[data-s="hb:0:0"]')==='refused'&&await slot('hb:0:0')==='empty','bar rules: spell refused on the hotbar');
 ok(await dnd('.hb-slot[data-s="ab:0"]','.hb-slot[data-s="ab:5"]')==='accepted'&&await slot('ab:5')===p0&&await slot('ab:0')==='empty','drag slot -> slot moves it');
 // tap / click to place
 await ev('document.querySelector(".hb-pi[data-i=\\"1\\"]").click()');ok(await ev('document.getElementById("hb-app").classList.contains("hb-armed")'),'click palette arms the item');
 await ev('document.querySelector(".hb-slot[data-s=\\"ab:1\\"]").click()');ok(await slot('ab:1')===pal[1],'click slot places '+pal[1]);
 // keyboard: focus palette item 2, Enter, ArrowRight, Enter; then Delete
 await ev('document.querySelector(".hb-pi[data-i=\\"2\\"]").focus()');await key('Enter','Enter',13);
 const f1=await ev('document.activeElement.getAttribute("data-s")');ok(f1==='ab:0','Enter on palette item focuses first empty ability slot ('+f1+')');
 await key('ArrowRight','ArrowRight',39);await key('ArrowRight','ArrowRight',39);const f2=await ev('document.activeElement.getAttribute("data-s")');ok(f2==='ab:2','ArrowRight moves along the bar ('+f2+')');
 await key('Enter','Enter',13);ok(await slot('ab:2')===pal[2],'Enter places '+pal[2]+' with the keyboard');
 await key('ArrowDown','ArrowDown',40);ok(await ev('document.activeElement.getAttribute("data-s")')==='hb:0:2','ArrowDown moves to the hotbar row');
 await key('ArrowUp','ArrowUp',38);await key('Delete','Delete',46);ok(await slot('ab:2')==='empty','Delete clears the focused slot');
 // undo
 await ev('document.getElementById("hb-undo").click()');ok(await slot('ab:2')===pal[2],'Undo restores the cleared slot');
 await ev('document.getElementById("hb-clear").click()');await key('z','KeyZ',90);ok(await slot('ab:1')==='empty','sanity: z alone does nothing');
 await send('Input.dispatchKeyEvent',{type:'keyDown',key:'z',code:'KeyZ',modifiers:2,windowsVirtualKeyCode:90});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'z',code:'KeyZ',modifiers:2,windowsVirtualKeyCode:90});await sleep(80);
 ok(await slot('ab:1')===pal[1],'Ctrl+Z undoes Clear layout');
 // Esc cancels an armed pick
 await ev('document.querySelector(".hb-pi[data-i=\\"3\\"]").click()');await key('Escape','Escape',27);ok(!(await ev('document.getElementById("hb-app").classList.contains("hb-armed")')),'Esc cancels a picked-up item');
 // macro to hotbar
 await ev('(function(){document.getElementById("hb-mname").value="Assist";document.getElementById("hb-mcmd").value="/assist";document.getElementById("hb-macro").requestSubmit()})()');
 const mi=await ev('[].findIndex.call(document.querySelectorAll(".hb-pi"),function(b){return b.querySelector(".hb-pn").textContent==="Assist"})');
 ok(mi>=0&&await dnd('.hb-pi[data-i="'+mi+'"]','.hb-slot[data-s="hb:0:3"]')==='accepted'&&await slot('hb:0:3')==='Assist','macro button goes on the hotbar');
 // keybinds
 await ev('document.getElementById("hb-keys").click()');await ev('(function(){var i=document.querySelector(".hb-kin[data-s=\\"ab:0\\"]");i.value="Q";i.dispatchEvent(new Event("change",{bubbles:true}))})()');
 await ev('document.getElementById("hb-keys").click()');ok(await ev('document.querySelector(".hb-slot[data-s=\\"ab:0\\"] .hb-k").textContent')==='Q','keybind label edited (ab:0 -> Q)');
 // layouts
 await ev('(function(){var s=document.getElementById("hb-layout");s.value="group";s.dispatchEvent(new Event("change"))})()');ok(await slot('ab:0')===groupAb[0],'switch to Group layout');
 await ev('document.getElementById("hb-new").click()');await ev('(function(){var i=document.getElementById("hb-lname");i.value="Ail raid prep";i.dispatchEvent(new Event("change"))})()');
 ok(await ev('document.getElementById("hb-layout").selectedOptions[0].textContent').then(x=>/Ail raid prep/.test(x)),'new custom layout, renamed');
 ok(await slot('ab:0')==='empty','custom layout starts empty');await ev('document.getElementById("hb-suggest").click()');ok(await slot('ab:0')!=='empty','Suggest fills a custom layout');
 ok(await ev('document.getElementById("hb-layout").options.length')===4,'4 layouts: solo, group, raid, custom');
 // persistence
 await go('hotbar.html');ok(await ev('document.getElementById("hb-layout").selectedOptions[0].textContent').then(x=>/Ail raid prep/.test(x)),'reload keeps the current layout (localStorage)');
 await ev('(function(){var s=document.getElementById("hb-layout");s.value="solo";s.dispatchEvent(new Event("change"))})()');
 ok(await slot('ab:1')===pal[1]&&await slot('hb:0:3')==='Assist'&&await ev('document.querySelector(".hb-slot[data-s=\\"ab:0\\"] .hb-k").textContent')==='Q','reload keeps slots, macro and keybind');
 // share URL
 const code=await ev('MNM_HB_API.encode({v:1,c:"Inquisitor",r:"Deep Elf",l:14,cur:"solo",L:MNM_HB_API.state().cls.Inquisitor.L,g:{},b:0,m:MNM_HB_API.state().macros,p:2})');
 ok(/^z[A-Za-z0-9_-]+$/.test(code),'share code is compressed (deflate-raw, '+code.length+' chars)');
 const raw=await ev('JSON.stringify(MNM_HB_API.state().cls.Inquisitor.L).length');ok(code.length<raw,'share code shorter than raw JSON ('+code.length+' < '+raw+')');
 await ev('localStorage.removeItem("mnm-hotbar")');await send('Page.navigate',{url:'about:blank'});await sleep(200);await go('hotbar.html#hb='+code);await sleep(300);
 ok(await slot('ab:1')===pal[1]&&await slot('hb:0:3')==='Assist','share link restores layout in a fresh browser state');
 {const lv14=await ev('+document.getElementById("hb-level").value'),hh=await ev('location.hash');ok(lv14===14&&!/hb=/.test(hh),'share link restores level 14 and cleans the hash (level '+lv14+', hash "'+hh+'")');}
 // export / import
 const exp=await ev(`new Promise(function(res){var o=URL.createObjectURL;URL.createObjectURL=function(b){b.text().then(res);URL.createObjectURL=o;return o.call(URL,b)};document.getElementById("hb-export").click()})`);
 const ej=JSON.parse(exp);ok(ej.type==='mnm-hotbar'&&ej.state.cls.Inquisitor,'Export JSON downloads the full state');
 await ev('document.getElementById("hb-clear").click()');ok(await slot('ab:1')==='empty','cleared before import');
 await ev('MNM_HB_API.importText('+JSON.stringify(exp)+')');ok(await slot('ab:1')===pal[1],'Import JSON restores layouts');
 await ev('MNM_HB_API.undo()');ok(await slot('ab:1')==='empty','Undo reverts an import');
 await ev('MNM_HB_API.undo()');ok(await slot('ab:1')===pal[1],'second Undo reverts the clear');
 ok(await ev('(function(){try{MNM_HB_API.importText("{\\"nope\\":1}");return false}catch(e){return true}})()'),'bad JSON is rejected');
 // file import through the input
 await ev(`(function(){var dt=new DataTransfer();dt.items.add(new File([${JSON.stringify(exp)}],'hb.json',{type:'application/json'}));var i=document.getElementById('hb-import');i.files=dt.files;i.dispatchEvent(new Event('change'))})()`);await sleep(300);
 ok(/Imported all layouts from hb.json/.test(await ev('document.getElementById("hb-msg").textContent')),'file input import works');
 // class change follows the shared picker
 await ev('(function(){var s=document.getElementById("mnm-class");s.value="Cleric";s.dispatchEvent(new Event("change"))})()');await sleep(200);
 const cl=await st();const cab=cl.cls.Cleric.L.solo.ab.filter(Boolean);const CN=new Set(HBD.classes.Cleric.spells.map(s=>s[0]));
 ok(cab.length>0&&cab.every(e=>CN.has(e.n)),'class picker change -> Cleric layouts from Cleric spells only');
 ok(await ev('document.getElementById("hb-ftitle").textContent').then(x=>/^Cleric/.test(x)),'title follows the class picker');
 await ev('(function(){var s=document.getElementById("mnm-class");s.value="Inquisitor";s.dispatchEvent(new Event("change"))})()');await sleep(200);
 await ev('(function(){var s=document.getElementById("mnm-range");s.value="1-5";s.dispatchEvent(new Event("change"))})()');await sleep(200);
 ok(await ev('+document.getElementById("hb-level").value')===5&&await ev('[].every.call(document.querySelectorAll(".hb-pi .hb-pm"),function(m){var x=m.textContent.match(/^L(\\d+)/);return !x||+x[1]<=5})'),'level picker change re-gates the palette (1-5)');
 await ev('(function(){var s=document.getElementById("hb-layout");s.value="group";s.dispatchEvent(new Event("change"))})()');
 ok(await ev('document.querySelectorAll(".hb-slot.hi").length')>0,'slots above your level are flagged after lowering the band');
 await ev('(function(){var s=document.getElementById("mnm-range");s.value="11-15";s.dispatchEvent(new Event("change"))})()');await sleep(200);
 // focus mode
 await ev('document.getElementById("hb-focus-t").click()');
 ok(await ev('getComputedStyle(document.querySelector("header.top")).display')==='none'&&await ev('getComputedStyle(document.querySelector(".hb-pal")).display')==='none'&&await ev('getComputedStyle(document.querySelector("footer")).display')==='none','focus mode hides site chrome, nav, footer and palette');
 ok(await ev('getComputedStyle(document.getElementById("hb-bars")).display')!=='none'&&await ev('getComputedStyle(document.getElementById("hb-rotlist")).display')!=='none'&&await ev('getComputedStyle(document.getElementById("hb-notesview")).display')!=='none','focus mode shows bars, rotation and notes');
 await ev('(function(){var r=document.getElementById("hb-size");r.value=64;r.dispatchEvent(new Event("input"))})()');ok(await ev('getComputedStyle(document.getElementById("hb-app")).getPropertyValue("--hb-sz").trim()')==='64px','size slider sets slot size');
 await size(760,460);await sleep(150);ok(await ev('document.documentElement.scrollWidth-innerWidth')<=1,'focus mode fits a 760px side window');
 await shot('hotbar-focus.png',900);
 await key('Escape','Escape',27);ok(!(await ev('document.documentElement.classList.contains("hb-focus")')),'Esc exits focus mode');
 await size(1280,900);
 await go('hotbar.html?focus=1');ok(await ev('document.documentElement.classList.contains("hb-focus")'),'?focus=1 opens straight into focus mode (pop-out window)');
 await send('Emulation.setEmulatedMedia',{media:'print'});ok(await ev('getComputedStyle(document.querySelector("header.top")).display')==='none'&&await ev('getComputedStyle(document.querySelector(".hb-pal")).display')==='none','print style hides chrome and palette');
 await send('Emulation.setEmulatedMedia',{media:''});await key('Escape','Escape',27);
 // character sheet
 await go('hotbar.html');await ev('document.getElementById("hb-sheet-t").click()');
 for(let i=0;i<50&&!(await ev('!!window.MNM_HBI&&!!document.querySelector(".hb-gs")'));i++)await sleep(100);
 ok(await ev('document.querySelectorAll(".hb-gs").length')===24,'paper-doll has 24 gear slots');
 const base=await ev('[].map.call(document.querySelectorAll(".hb-tt")[0].tBodies[0].rows,function(r){return [r.cells[0].textContent,r.cells[1].textContent,r.cells[3].textContent]})');
 const DE=HBD.races['Deep Elf'].start.Inquisitor,b0=INQ.builds[0].a;
 ok(base.find(r=>r[0]==='STA')[1]==String(DE.STA+(b0.STA||0))&&base.find(r=>r[0]==='INT')[1]==String(DE.INT+(b0.INT||0)),'base stats = Deep Elf Inquisitor start + '+INQ.builds[0].n+' points (STA '+(DE.STA+(b0.STA||0))+')');
 await ev('document.querySelector(".hb-gs[data-g=\\"Chest\\"]").click()');
 const cnt=await ev('document.querySelectorAll("#hb-ilist .hb-ib").length');ok(cnt>0,'Chest picker lists '+cnt+' Inquisitor chest items');
 const chosen=await ev('(function(){var b=document.querySelector("#hb-ilist .hb-ib");var n=b.getAttribute("data-n");b.click();return n})()');
 await ev('document.querySelector(".hb-gs[data-g=\\"Finger 1\\"]").click()');const chosen2=await ev('(function(){var q=document.getElementById("hb-iq");q.value="";var b=document.querySelector("#hb-ilist .hb-ib");var n=b.getAttribute("data-n");b.click();return n})()');
 const items=await ev('(function(){var o={};MNM_HBI.forEach(function(r){o[r[0]]=r[4]});return o})()');
 const sum={};[chosen,chosen2].forEach(n=>Object.entries(items[n]).forEach(([k,v])=>sum[k]=(sum[k]||0)+v));
 const tot=await ev('(function(){var o={};document.querySelectorAll(".hb-tt tbody tr").forEach(function(r){o[r.cells[0].textContent]=r.cells[r.cells.length-1].textContent});return o})()');
 const lab={str:'STR',sta:'STA',agi:'AGI',dex:'DEX',int:'INT',wis:'WIS',cha:'CHA',ac:'AC',hp:'HP',mana:'Mana',mr:'Magic',fr:'Fire',cr:'Cold',pr:'Poison',dr:'Disease',er:'Electric',cor:'Corruption',hr:'Holy'};
 const baseOf=k=>({str:DE.STR+(b0.STR||0),sta:DE.STA+(b0.STA||0),agi:DE.AGI+(b0.AGI||0),dex:DE.DEX+(b0.DEX||0),int:DE.INT+(b0.INT||0),wis:DE.WIS+(b0.WIS||0),cha:DE.CHA+(b0.CHA||0)})[k]||0;
 const bad=Object.keys(lab).filter(k=>+tot[lab[k]]!==Math.round(((sum[k]||0)+baseOf(k))*10)/10);
 ok(bad.length===0,'totals = base + '+chosen+' + '+chosen2+' ('+JSON.stringify(sum)+')'+(bad.length?' mismatch '+bad.join(','):''));
 ok(await ev('[].some.call(document.querySelectorAll(".hb-eq a"),function(a){return /items\\.html#/.test(a.getAttribute("href"))})'),'equipped items link to drop sources in the Item database');
 const mk=await ev('(function(){var k=Object.keys(window.MNM_MKTI||{});var r=MNM_HBI.filter(function(x){return k.indexOf(x[0])>=0&&/Chest|Ear|Finger|Neck|Head|Primary|Back|Waist/.test(x[1])&&/INQ/.test(x[2])})[0];return r?[r[0],r[1].split(" ")[0]]:null})()');
 if(mk){await ev('document.querySelector(".hb-gs[data-g^=\\"'+mk[1]+'\\"]").click()');await ev('(function(){var q=document.getElementById("hb-iq");q.value='+JSON.stringify(mk[0])+';q.dispatchEvent(new Event("input"));document.querySelector("#hb-ilist .hb-ib").click()})()');
   ok(await ev('[].some.call(document.querySelectorAll(".hb-eq a"),function(a){return /market\\.html#/.test(a.getAttribute("href"))})'),'item with a known price links to the Market ('+mk[0]+')');}
 else ok(true,'no Inquisitor gear item has a market price yet (Market link shown as "no market price")');
 await shotEl('hotbar-charsheet.png','#hb-sheet');
 await go('hotbar.html');ok(await ev('!document.getElementById("hb-sheet").hidden')&&await ev('Object.keys(MNM_HB_API.state().cls.Inquisitor.gear).length')>=2,'sheet toggle and gear persist after reload');
 // 480px
 await size(480,900);await go('hotbar.html');
 ok(await ev('document.documentElement.scrollWidth-innerWidth')<=1,'480px: no horizontal overflow');
 ok(await ev('[].every.call(document.querySelectorAll(".hb-pi"),function(b){return !b.hasAttribute("draggable")})'),'480px: drag is off, tap-to-place instead');
 ok(/Tap an item/.test(await ev('document.getElementById("hb-palcount").textContent')),'480px: tap hint shown');
 await ev('document.getElementById("hb-clear").click()');
 await ev('document.querySelector(".hb-pi[data-i=\\"0\\"]").click()');await ev('document.querySelector(".hb-slot[data-s=\\"ab:3\\"]").click()');ok(await slot('ab:3')===pal[0],'480px: tap palette then tap slot places it');
 await ev('document.getElementById("hb-undo").click()');await ev('document.getElementById("hb-undo").click()');
 await ev('document.getElementById("hb-sheet-t").click()');await sleep(200);ok(await ev('document.documentElement.scrollWidth-innerWidth')<=1,'480px: character sheet open, still no overflow');
 await ev('document.getElementById("hb-sheet-t").click()');
 await shot('hotbar-480.png',2600);
 await ev('document.getElementById("hb-focus-t").click()');ok(await ev('document.documentElement.scrollWidth-innerWidth')<=1,'480px: focus mode, no overflow');
 await key('Escape','Escape',27);
 ok(errs.length===0,'no JS exceptions'+(errs.length?': '+errs.join(' | '):''));
 console.log(passes+' passed, '+fails+' failed');ws.close();chrome.kill();srv.kill();process.exit(fails?1:0);
})().catch(e=>{console.error(e);chrome.kill();srv.kill();process.exit(2)});
