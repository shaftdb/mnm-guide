// UX pass 1: keeps --hdr-h in sync with the sticky header (desktop sticky offsets / scroll padding) and, on narrow
// screens, swaps the tall header for a compact fixed mini bar (logo mark, search, menu, Setup) once it scrolls away.
(function(){
var top=document.querySelector('.top'),topin=top&&top.querySelector('.topin'),de=document.documentElement,body=document.body;
if(!top||!topin)return;
var narrow=window.matchMedia('(max-width:800px)'),reduce=window.matchMedia('(prefers-reduced-motion:reduce)');
var btn=document.createElement('button');btn.type='button';btn.className='ux-setup';
btn.setAttribute('aria-label','Back to top: class, race, start and level setup');btn.title='Back to top (class / level setup)';
btn.innerHTML='<span aria-hidden="true">&#9881;</span> Setup';
topin.appendChild(btn);
btn.addEventListener('click',function(){body.classList.remove('navopen');window.scrollTo({top:0,behavior:reduce.matches?'auto':'smooth'});
  var c=document.getElementById('mnm-class');if(c)setTimeout(function(){c.focus({preventScroll:true})},reduce.matches?0:400)});
var full=0;
function measure(){if(!body.classList.contains('ux-mini')){top.style.minHeight='';full=top.offsetHeight}
  de.style.setProperty('--hdr-h',(narrow.matches?Math.min(full,72):full)+'px')}
function onScroll(){if(!narrow.matches){if(body.classList.contains('ux-mini')){body.classList.remove('ux-mini');top.style.minHeight='';measure()}return}
  var mini=body.classList.contains('ux-mini'),y=window.scrollY,cut=full-20;
  if(!mini&&y>cut){top.style.minHeight=full+'px';body.classList.add('ux-mini');de.style.setProperty('--mini-h',topin.offsetHeight+'px')}
  else if(mini&&y<cut-40){body.classList.remove('ux-mini');top.style.minHeight=''}}
measure();onScroll();
window.addEventListener('scroll',onScroll,{passive:true});
window.addEventListener('resize',function(){measure();onScroll()});
if(window.ResizeObserver)new ResizeObserver(function(){measure()}).observe(top);
})();
// ---------------------------------------------------------------- UX pass 2
(function(){
var narrowQ=window.matchMedia('(max-width:640px)'),phoneQ=window.matchMedia('(max-width:800px)');
// ---- "My setup": one-row summary of the top-bar pickers on phones; tap to open the full pickers
var rb=document.getElementById('mnm-rangebar'),rin=rb&&rb.querySelector('.rangebar-in');
if(rb&&rin){
  rin.id=rin.id||'ux-rb-in';
  var sb=document.createElement('button');sb.type='button';sb.className='ux-mysetup';sb.setAttribute('aria-expanded','false');sb.setAttribute('aria-controls',rin.id);
  sb.innerHTML='<span class="ux-ms-l">My setup</span><span class="ux-ms-v"></span><span class="ux-ms-c" aria-hidden="true">&#9662;</span>';
  rb.insertBefore(sb,rin);
  var val=function(id,txt){var e=document.getElementById(id);if(!e)return '';if(txt){var o=e.selectedOptions&&e.selectedOptions[0];return o?o.textContent.replace(/\s*\((not for|unverified)[^)]*\)\s*$/,''):''}return e.value||''};
  var sum=function(){var ts=document.getElementById('mnm-ts-sum'),parts=[val('mnm-class'),val('mnm-race'),val('mnm-city'),val('mnm-range',1),ts?ts.textContent:''].filter(Boolean);
    sb.querySelector('.ux-ms-v').textContent=parts.join(' · ');sb.title='My setup: '+parts.join(', ')+'. Tap to change.'};
  var setOpen=function(on){rb.classList.toggle('ux-open',on);sb.setAttribute('aria-expanded',on?'true':'false')};
  sb.addEventListener('click',function(){setOpen(!rb.classList.contains('ux-open'))});
  document.addEventListener('change',function(e){if(e.target&&e.target.closest&&e.target.closest('#mnm-rangebar'))setTimeout(sum,0)},true);
  var tsum=document.getElementById('mnm-ts-sum');if(tsum&&window.MutationObserver)new MutationObserver(sum).observe(tsum,{childList:true,characterData:true,subtree:true});
  sum();setTimeout(sum,0);window.addEventListener('load',sum);
  window.MNM_UX_SETUP=setOpen;
  // 'Valid starts' line behind a disclosure on phones
  var cv=document.getElementById('cg-valid');
  if(cv){cv.classList.add('ux-cgv');var vb=document.createElement('button');vb.type='button';vb.className='ux-cgv-btn';vb.setAttribute('aria-expanded','false');vb.setAttribute('aria-controls','cg-valid');
    vb.innerHTML='Valid starts for this race <span aria-hidden="true">&#9662;</span>';cv.parentNode.insertBefore(vb,cv);
    vb.addEventListener('click',function(){var on=!rb.classList.contains('ux-cgv-open');rb.classList.toggle('ux-cgv-open',on);vb.setAttribute('aria-expanded',on?'true':'false')});}
  // pass-1 mini-bar Setup button: also open the pickers
  var mb=document.querySelector('.ux-setup');if(mb)mb.addEventListener('click',function(){setOpen(true)});
}
// ---- "On this page": sticky button on phones that opens a sheet of the page's sections
var links=[].slice.call(document.querySelectorAll('.right .box.toc a[href^="#"]')).map(function(a){return [a.getAttribute('href'),a.textContent]});
if(links.length<2){links=[].slice.call(document.querySelectorAll('main.main h2[id]')).map(function(h){return ['#'+h.id,h.textContent]});if(links.length<3)links=[]}
if(links.length&&window.HTMLDialogElement){
  var ob=document.createElement('button');ob.type='button';ob.className='ux-otp';ob.setAttribute('aria-haspopup','dialog');ob.innerHTML='<span aria-hidden="true">&#9776;</span> On this page';
  var dl=document.createElement('dialog');dl.className='ux-sheet';dl.setAttribute('aria-labelledby','ux-sheet-h');
  dl.innerHTML='<div class="ux-sheet-hd"><h2 id="ux-sheet-h">On this page</h2><button type="button" class="ux-sheet-x" aria-label="Close">&#10005;</button></div><ul>'+
    links.map(function(l){var e=document.createElement('span'),d=document.createElement('textarea');d.innerHTML=l[1];e.textContent=d.value;return '<li><a href="'+l[0].replace(/"/g,'&quot;')+'">'+e.innerHTML+'</a></li>'}).join('')+'</ul>';
  document.body.appendChild(ob);document.body.appendChild(dl);document.body.classList.add('ux-has-otp');
  ob.addEventListener('click',function(){dl.showModal();var a=dl.querySelector('a');if(a)a.focus()});
  dl.querySelector('.ux-sheet-x').addEventListener('click',function(){dl.close()});
  dl.addEventListener('click',function(e){if(e.target===dl)dl.close();var a=e.target.closest('a');if(a){dl.close();var id=decodeURIComponent(a.getAttribute('href').slice(1)),t=document.getElementById(id);
    // open the tab holding the target (class guides), then jump
    var p=t&&t.closest('.tabpane');if(p&&!p.classList.contains('on')){var b=document.querySelector('.tab[data-tab="'+p.id+'"]');if(b)b.click()}}});
  dl.addEventListener('close',function(){ob.focus({preventScroll:true})});
}
})();
// ---------------------------------------------------------------- UX pass 3
(function(){
var de=document.documentElement,root=de.getAttribute('data-root')||'',S=function(){return window.MNM_SEARCH};
function lsGet(k,d){try{var v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(e){return d}}
function lsPut(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function typing(el){el=el||document.activeElement;return !!el&&(/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)||el.isContentEditable)}
var base=new URL(root||'./',location.href).pathname,here=(location.pathname.indexOf(base)===0?location.pathname.slice(base.length):location.pathname.replace(/^\//,''))||'index.html';
if(/\/$/.test(here))here+='index.html';
// ---- recently viewed pages (#6): localStorage mnm-recent, newest first, max 12
var KR='mnm-recent',recent=lsGet(KR,[]);if(!Array.isArray(recent))recent=[];
(function(){var h=document.querySelector('main.main h1'),t=(h&&h.textContent.trim())||document.title.replace(/\s+[\u2014-]\s+M&M Quick Codex$/,'');
  t=t.replace(/\s+/g,' ').slice(0,90);recent=[{u:here,t:t}].concat(recent.filter(function(r){return r&&r.u&&r.u!==here})).slice(0,12);lsPut(KR,recent)})();
// ---- quick-jump palette (#1, #19): Ctrl+K / Cmd+K / '/' / header search button
var JUMP=[['Home','index.html'],['Classes','classes/index.html'],['Walkthrough','walkthrough.html'],['Leveling by band','leveling.html'],['Items','items.html'],['Mobs','mobs.html'],['Zones','zones/index.html'],['Spells','spells.html'],['Market prices','market.html'],['Hotbar','hotbar.html'],['Quests','quests.html'],['Changelog','changelog.html']];
var GO={h:'index.html',c:'classes/index.html',w:'walkthrough.html',l:'leveling.html',i:'items.html',m:'mobs.html',z:'zones/index.html',s:'spells.html',k:'market.html',q:'quests.html'};
function href(u,ext){return ext?u:root+u}
function kind(it){if(it.e)return 'Wiki';if(/^item\b/i.test(it.s))return 'Items';if(/spells/i.test(it.s))return 'Spells';return 'Pages'}
var pal=null,inp,list,stat,act=-1,opts=[],opener=null,lastQ=null;
function build(){if(pal)return;
  pal=document.createElement('dialog');pal.className='ux-pal';pal.setAttribute('aria-labelledby','ux-pal-h');
  pal.innerHTML='<div class="ux-pal-hd"><h2 id="ux-pal-h" class="ux-vh">Quick jump</h2><span class="ux-pal-ico" aria-hidden="true">&#9906;</span>'+
   '<input id="ux-pal-q" type="search" autocomplete="off" spellcheck="false" placeholder="Jump to a page, class, zone, item…" role="combobox" aria-expanded="true" aria-controls="ux-pal-list" aria-autocomplete="list" aria-label="Quick jump: type to search">'+
   '<button type="button" class="ux-pal-x" aria-label="Close">&#10005;</button></div>'+
   '<p class="ux-pal-st" id="ux-pal-st" role="status" aria-live="polite"></p><ul id="ux-pal-list" class="ux-pal-list" role="listbox" aria-label="Results"></ul>'+
   '<p class="ux-pal-ft dim"><kbd>&uarr;</kbd><kbd>&darr;</kbd> move · <kbd>Enter</kbd> open · <kbd>Esc</kbd> close · <kbd>?</kbd> all shortcuts</p>';
  document.body.appendChild(pal);inp=pal.querySelector('input');list=pal.querySelector('ul');stat=pal.querySelector('.ux-pal-st');
  inp.addEventListener('input',render);
  inp.addEventListener('keydown',function(e){if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();mv(e.key==='ArrowDown'?1:-1)}
    else if(e.key==='Home'&&e.ctrlKey){e.preventDefault();setAct(0)}else if(e.key==='End'&&e.ctrlKey){e.preventDefault();setAct(opts.length-1)}
    else if(e.key==='Enter'){e.preventDefault();var o=opts[act>=0?act:0];if(o)openOpt(o)}
    else if(e.key==='Escape'){e.preventDefault();close()}});
  pal.addEventListener('keydown',function(e){if(e.key!=='Tab')return;var f=[inp,pal.querySelector('.ux-pal-x')];var i=f.indexOf(document.activeElement);e.preventDefault();f[(i+(e.shiftKey?-1:1)+f.length)%f.length].focus()});
  pal.querySelector('.ux-pal-x').addEventListener('click',close);
  pal.addEventListener('click',function(e){if(e.target===pal){close();return}var li=e.target.closest('[role=option]');if(li)openOpt(li)});
  pal.addEventListener('close',function(){if(opener&&opener.focus)opener.focus({preventScroll:true});opener=null});
  if(S())S().onUpdate(function(){if(pal.open)render(1)});
}
function setAct(i){act=Math.max(-1,Math.min(opts.length-1,i));opts.forEach(function(o,j){o.setAttribute('aria-selected',j===act?'true':'false');o.classList.toggle('on',j===act)});
  if(act>=0){inp.setAttribute('aria-activedescendant',opts[act].id);opts[act].scrollIntoView({block:'nearest'})}else inp.removeAttribute('aria-activedescendant')}
function mv(d){setAct(act<0?(d>0?0:opts.length-1):(act+d+opts.length)%opts.length)}
function openOpt(o){var u=o.getAttribute('data-href');if(!u)return;if(o.getAttribute('data-ext')){window.open(u,'_blank','noopener');close();return}location.href=u;close()}
function item(i,t,u,sub,ext){return '<li role="option" id="ux-pal-o'+i+'" aria-selected="false" data-href="'+esc(u)+'"'+(ext?' data-ext="1"':'')+'><span class="ux-pal-t">'+esc(t)+(ext?' <span aria-hidden="true">&#8599;</span>':'')+'</span>'+(sub?'<span class="ux-pal-s">'+esc(sub)+'</span>':'')+'</li>'}
function group(n,h){return '<li role="presentation" class="ux-pal-g" aria-hidden="true">'+esc(n)+'</li>'+h}
function render(keep){var t=inp.value.trim(),h=[],n=0,cur=act;
  if(t.length<2){var rc=recent.filter(function(r){return r.u!==here}).slice(0,8);
    if(rc.length)h.push(group('Recently viewed',rc.map(function(r){return item(n++,r.t,href(r.u),r.u.replace(/\.html$/,'').replace(/\/index$/,'/'))}).join('')));
    h.push(group('Jump to',JUMP.map(function(j){return item(n++,j[0],href(j[1]),'')}).join('')));
    stat.textContent=t.length?'Type at least 2 letters to search.':(rc.length?'Recently viewed pages and main sections.':'Main sections. Type to search everything.');
  }else{var s=S(),lt=t.toLowerCase();
    var rc2=recent.filter(function(r){return r.t.toLowerCase().indexOf(lt)>=0}).slice(0,3);
    if(rc2.length)h.push(group('Recently viewed',rc2.map(function(r){return item(n++,r.t,href(r.u),r.u)}).join('')));
    var jm=JUMP.filter(function(j){return j[0].toLowerCase().indexOf(lt)>=0});
    if(!s){stat.textContent='Search is not available on this page.'}
    else if(!s.ready()){if(s.failed()){stat.textContent='The search index could not load (offline?). Close and try again.';stat.classList.add('lz-err')}else{stat.textContent='Loading search index…';s.load()}
      if(jm.length)h.push(group('Jump to',jm.map(function(j){return item(n++,j[0],href(j[1]),'')}).join('')))}
    else{stat.classList.remove('lz-err');s.loadText();var seenU={},r=s.search(t,60).filter(function(it){var k=it.u+'|'+it.t;if(seenU[k]||seenU[it.u])return false;seenU[k]=seenU[it.u]=1;return true}).slice(0,40),g={},order=['Pages','Spells','Items','Wiki'];
      r.forEach(function(it){(g[kind(it)]=g[kind(it)]||[]).push(it)});
      order.forEach(function(k){if(g[k])h.push(group(k,g[k].slice(0,k==='Pages'?14:8).map(function(it){return item(n++,it.t,href(it.u,it.e),(it.fz?'close match · ':'')+it.s,it.e)}).join('')))});
      stat.textContent=n?(n+' result'+(n>1?'s':'')+(s.full()?'':' (titles; full text still loading)')):'No matches for “'+t+'”'+(s.full()?'':' in titles yet; full text still loading…')}}
  list.innerHTML=h.join('');opts=[].slice.call(list.querySelectorAll('[role=option]'));setAct(keep===1&&t===lastQ?Math.min(cur,opts.length-1):(t.length>=2&&opts.length?0:-1));lastQ=t}
function open(from){build();if(pal.open){inp.focus();inp.select();return}opener=from||document.activeElement;var sq=document.getElementById('q');
  inp.value=(sq&&sq.value&&document.activeElement===sq)?sq.value:'';if(sq)sq.blur();var r=document.getElementById('qres');if(r)r.hidden=true;
  if(S())S().load();pal.showModal();render();inp.focus()}
function close(){if(pal&&pal.open)pal.close()}
window.MNM_UX_PAL={open:open,close:close};
// header button (touch + discoverability)
var topin=document.querySelector('.top .topin'),sf=topin&&topin.querySelector('form.search');
if(topin){var pb=document.createElement('button');pb.type='button';pb.className='ux-palbtn';pb.setAttribute('aria-haspopup','dialog');pb.setAttribute('aria-label','Quick jump (Ctrl+K)');pb.title='Quick jump (Ctrl+K or /)';
  pb.innerHTML='<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M13 13l5 5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg><kbd class="ux-palk">Ctrl K</kbd>';
  if(sf&&sf.nextSibling)topin.insertBefore(pb,sf.nextSibling);else topin.appendChild(pb);pb.addEventListener('click',function(){open(pb)})}
// ---- keyboard shortcuts + '?' overlay (#5)
var keys=null;
function keysOpen(){if(!keys){keys=document.createElement('dialog');keys.className='ux-keys';keys.setAttribute('aria-labelledby','ux-keys-h');
  var row=function(k,d){return '<tr><th scope="row">'+k+'</th><td>'+d+'</td></tr>'};
  keys.innerHTML='<div class="ux-sheet-hd"><h2 id="ux-keys-h">Keyboard shortcuts</h2><button type="button" class="ux-sheet-x" aria-label="Close">&#10005;</button></div><table class="ux-keys-t"><tbody>'+
   row('<kbd>Ctrl</kbd> <kbd>K</kbd> or <kbd>/</kbd>','Quick jump: search pages, classes, zones, items; recently viewed')+row('<kbd>?</kbd>','Show this list')+row('<kbd>Esc</kbd>','Close a dialog, menu or search results')+
   row('<kbd>&uarr;</kbd> <kbd>&darr;</kbd> <kbd>Enter</kbd>','Move through results and open one')+row('<kbd>Tab</kbd> then <kbd>Enter</kbd> on a table header','Sort that column (press again to reverse)')+
   Object.keys(GO).map(function(k){var j=JUMP.filter(function(x){return x[1]===GO[k]})[0];return row('<kbd>g</kbd> <kbd>'+k+'</kbd>','Go to '+esc(j?j[0]:GO[k]))}).join('')+
   row('<kbd>t</kbd>','Back to top')+'</tbody></table><p class="dim ux-keys-n">Shortcuts are ignored while you type in a box. On touch screens use the search button in the header.</p>';
  document.body.appendChild(keys);var x=keys.querySelector('.ux-sheet-x');x.addEventListener('click',function(){keys.close()});
  keys.addEventListener('click',function(e){if(e.target===keys)keys.close()});
  keys.addEventListener('keydown',function(e){if(e.key==='Tab'){e.preventDefault();x.focus()}});
  keys.addEventListener('close',function(){if(keys._op&&keys._op.focus)keys._op.focus({preventScroll:true})})}
  if(keys.open)return;keys._op=document.activeElement;keys.showModal();keys.querySelector('.ux-sheet-x').focus()}
window.MNM_UX_KEYS=keysOpen;
var gAt=0;
document.addEventListener('keydown',function(e){
  if((e.ctrlKey||e.metaKey)&&!e.altKey&&!e.shiftKey&&(e.key==='k'||e.key==='K')){e.preventDefault();if(pal&&pal.open)close();else open();return}
  if(e.ctrlKey||e.metaKey||e.altKey||typing(e.target)||document.querySelector('dialog[open]'))return;
  if(e.key==='?'){e.preventDefault();keysOpen();return}
  if(e.key==='g'){gAt=Date.now();return}
  if(gAt&&Date.now()-gAt<1200&&GO[e.key]){e.preventDefault();gAt=0;location.href=root+GO[e.key];return}gAt=0;
  if(e.key==='t'){e.preventDefault();window.scrollTo({top:0,behavior:'smooth'})}
});
// ---- tables (#2, #3, #12, #14): remember sorts and filters per page (localStorage mnm-tbl:<page>) and mirror them in
// the URL (?sort=<table>.<col><a|d>, filters below). Other params (?class=&race=&city=, ?server=, #hb=, ?focus=1) are kept.
var CTRL=[['f','#mnm-filter','v'],['gc','main .clsfilter','v'],['gk','main .kindfilter','c'],['gt','main .textfilter','v'],['sm','#sp-mine','c'],['sb','#sp-band','c']]
  .map(function(c){return {p:c[0],el:document.querySelector(c[1]),t:c[2]}}).filter(function(c){return c.el});
var tabs=[].slice.call(document.querySelectorAll('main.main table.sortable, main.main table.grid')).filter(function(t){return t.tBodies[0]&&(t.classList.contains('sortable')||t.tBodies[0].rows.length>=15)});
var KT='mnm-tbl:'+here,st=lsGet(KT,{});if(!st||typeof st!=='object')st={};
function qpGet(n){var m=location.search.match(new RegExp('[?&]'+n+'=([^&]*)'));return m?decodeURIComponent(m[1].replace(/\+/g,' ')):null}
function writeUrl(){if(!history.replaceState)return;var keep=location.search.replace(/^\?/,'').split('&').filter(function(kv){return kv&&!/^(sort|f|gc|gk|gt|sm|sb)=/.test(kv)});
  var add=[];if(st.sort&&Object.keys(st.sort).length)add.push('sort='+Object.keys(st.sort).map(function(i){return i+'.'+st.sort[i]}).join('~'));
  CTRL.forEach(function(c){var v=(st.ctl||{})[c.p];if(v)add.push(c.p+'='+encodeURIComponent(v))});
  var s=keep.concat(add).join('&');history.replaceState(history.state,'',location.pathname+(s?'?'+s:'')+location.hash)}
function save(){lsPut(KT,st);writeUrl()}
// restore: URL first, then this browser
var us=qpGet('sort'),fromUrl=us!==null||CTRL.some(function(c){return qpGet(c.p)!==null});
if(fromUrl){st={sort:{},ctl:{}};if(us)us.split('~').forEach(function(x){var m=x.match(/^(\d+)\.(\d+)([ad])$/);if(m)st.sort[m[1]]=m[2]+m[3]});CTRL.forEach(function(c){var v=qpGet(c.p);if(v)st.ctl[c.p]=v})}
st.sort=st.sort||{};st.ctl=st.ctl||{};
var orig=tabs.map(function(t){return [].slice.call(t.tBodies[0].rows)});
function ctlVal(c){return c.t==='c'?(c.el.checked?'1':''):(c.el.value||'')}
CTRL.forEach(function(c){var v=st.ctl[c.p];if(v==null)return;if(c.t==='c'){if(c.el.checked!==(v==='1')){c.el.checked=v==='1';c.el.dispatchEvent(new Event('change',{bubbles:true}))}}
  else if(c.el.tagName==='SELECT'&&![].some.call(c.el.options,function(o){return o.value===v})){delete st.ctl[c.p]}
  else if(c.el.value!==v){c.el.value=v;c.el.dispatchEvent(new Event('input',{bubbles:true}));c.el.dispatchEvent(new Event('change',{bubbles:true}))}
});
CTRL.forEach(function(c){c.el.addEventListener('input',function(){upd(c)});c.el.addEventListener('change',function(){upd(c)})});
function upd(c){var v=ctlVal(c);if(v)st.ctl[c.p]=v;else delete st.ctl[c.p];save();countAll()}
function sortTo(ti,spec){var t=tabs[ti],m=String(spec).match(/^(\d+)([ad])$/);if(!t||!m)return false;var th=t.tHead&&t.tHead.rows[0]&&t.tHead.rows[0].cells[+m[1]];if(!th||!t.classList.contains('sortable'))return false;
  th.click();if(m[2]==='d'&&th.dataset.dir!=='d')th.click();return true}
var restoring=1;Object.keys(st.sort).forEach(function(i){if(!sortTo(+i,st.sort[i]))delete st.sort[i]});restoring=0;
tabs.forEach(function(t,ti){if(!t.classList.contains('sortable')||!t.tHead)return;[].forEach.call(t.tHead.rows[0].cells,function(th,ci){th.addEventListener('click',function(){if(restoring)return;
  setTimeout(function(){st.sort[ti]=ci+(th.dataset.dir==='d'?'d':'a');save();countAll()},0)})})});
// toolbar: "Showing X of Y rows" + reset
function vis(r){return r.style.display!=='none'&&!r.hidden&&!r.classList.contains('fhide')}
var bars=[];
tabs.forEach(function(t,ti){var rows=t.tBodies[0].rows.length;if(rows<8)return;var host=t.closest('.tw')||t;
  var b=document.createElement('div');b.className='ux-tbar';b.innerHTML='<span class="ux-tbar-n" role="status" aria-live="polite"></span><span class="ux-tbar-f"></span><span class="ux-tbar-s"></span><button type="button" class="ux-tbar-r">Reset</button>';
  host.parentNode.insertBefore(b,host);b.querySelector('.ux-tbar-r').addEventListener('click',function(){reset(ti)});bars.push([b,t,ti]);
  if(window.MutationObserver)new MutationObserver(function(){sched()}).observe(t.tBodies[0],{attributes:true,attributeFilter:['style','class','hidden'],subtree:true,childList:true})});
var raf=0;function sched(){if(!raf)raf=requestAnimationFrame(function(){raf=0;countAll()})}
function countAll(){bars.forEach(function(x){var b=x[0],t=x[1],ti=x[2],rs=[].slice.call(t.tBodies[0].rows),n=rs.filter(vis).length,s=st.sort[ti],fl=Object.keys(st.ctl).length;
  var txt=n===rs.length?'Showing all '+rs.length+' rows':'Showing '+n+' of '+rs.length+' rows';var nn=b.querySelector('.ux-tbar-n');if(nn.textContent!==txt)nn.textContent=txt;
  var th=s&&t.tHead&&t.tHead.rows[0].cells[parseInt(s)];b.querySelector('.ux-tbar-s').textContent=th?'Sorted by '+th.textContent.trim()+(s.slice(-1)==='d'?' (high to low)':' (low to high)'):'';
  var fd=CTRL.filter(function(c){return st.ctl[c.p]}).map(function(c){return c.t==='c'?(c.el.closest('label')||{textContent:c.p}).textContent.trim():(c.el.tagName==='SELECT'?(c.el.selectedOptions[0]||{}).textContent:'“'+st.ctl[c.p]+'”')});b.querySelector('.ux-tbar-f').textContent=fd.length?'Filtered: '+fd.join(', '):'';
  var r=b.querySelector('.ux-tbar-r');r.disabled=!s&&!fl;r.title=fl?'Clear the filters on this page and this table\u2019s sort':'Back to the original order'})}
function reset(ti){var t=tabs[ti],tb=t.tBodies[0];orig[ti].forEach(function(r){tb.appendChild(r)});if(t.tHead)[].forEach.call(t.tHead.rows[0].cells,function(th){th.removeAttribute('aria-sort');delete th.dataset.dir});delete st.sort[ti];
  CTRL.forEach(function(c){if(!ctlVal(c))return;if(c.t==='c'){c.el.checked=false;c.el.dispatchEvent(new Event('change',{bubbles:true}))}else{c.el.value='';c.el.dispatchEvent(new Event('input',{bubbles:true}));c.el.dispatchEvent(new Event('change',{bubbles:true}))}});
  st.ctl={};save();countAll()}
countAll();if(fromUrl||Object.keys(st.sort).length||Object.keys(st.ctl).length)save();
// back-to-top on pages with a long table (#14)
var longT=tabs.filter(function(t){return t.tBodies[0].rows.length>=30})[0];
if(longT){var tt=document.createElement('button');tt.type='button';tt.className='ux-totop';tt.hidden=true;tt.setAttribute('aria-label','Back to top');tt.title='Back to top (t)';tt.innerHTML='<span aria-hidden="true">&#8593;</span> Top';
  document.body.appendChild(tt);tt.addEventListener('click',function(){var rm=window.matchMedia('(prefers-reduced-motion:reduce)').matches;window.scrollTo({top:0,behavior:rm?'auto':'smooth'});var m=document.getElementById('content');if(m)setTimeout(function(){m.focus({preventScroll:true})},rm?0:400)});
  var tick=0,chk=function(){tick=0;var y=window.scrollY,top=longT.getBoundingClientRect().top+y;tt.hidden=!(y>Math.max(600,top+300))};
  window.addEventListener('scroll',function(){if(!tick){tick=1;requestAnimationFrame(chk)}},{passive:true});chk()}
})();
