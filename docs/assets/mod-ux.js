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
(function(){
var narrowQ=window.matchMedia('(max-width:640px)'),phoneQ=window.matchMedia('(max-width:800px)');
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
var cv=document.getElementById('cg-valid');
if(cv){cv.classList.add('ux-cgv');var vb=document.createElement('button');vb.type='button';vb.className='ux-cgv-btn';vb.setAttribute('aria-expanded','false');vb.setAttribute('aria-controls','cg-valid');
vb.innerHTML='Valid starts for this race <span aria-hidden="true">&#9662;</span>';cv.parentNode.insertBefore(vb,cv);
vb.addEventListener('click',function(){var on=!rb.classList.contains('ux-cgv-open');rb.classList.toggle('ux-cgv-open',on);vb.setAttribute('aria-expanded',on?'true':'false')});}
var mb=document.querySelector('.ux-setup');if(mb)mb.addEventListener('click',function(){setOpen(true)});
}
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
var p=t&&t.closest('.tabpane');if(p&&!p.classList.contains('on')){var b=document.querySelector('.tab[data-tab="'+p.id+'"]');if(b)b.click()}}});
dl.addEventListener('close',function(){ob.focus({preventScroll:true})});
}
})();
(function(){
var de=document.documentElement,root=de.getAttribute('data-root')||'',S=function(){return window.MNM_SEARCH};
function lsGet(k,d){try{var v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(e){return d}}
function lsPut(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function typing(el){el=el||document.activeElement;return !!el&&(/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)||el.isContentEditable)}
var base=new URL(root||'./',location.href).pathname,here=(location.pathname.indexOf(base)===0?location.pathname.slice(base.length):location.pathname.replace(/^\//,''))||'index.html';
if(/\/$/.test(here))here+='index.html';
var KR='mnm-recent',recent=lsGet(KR,[]);if(!Array.isArray(recent))recent=[];
(function(){var h=document.querySelector('main.main h1'),t=(h&&h.textContent.trim())||document.title.replace(/\s+[\u2014-]\s+M&M Quick Codex$/,'');
t=t.replace(/\s+/g,' ').slice(0,90);recent=[{u:here,t:t}].concat(recent.filter(function(r){return r&&r.u&&r.u!==here})).slice(0,12);lsPut(KR,recent)})();
var JUMP=[['Home','index.html'],['Classes','classes/index.html'],['Walkthrough','walkthrough.html'],['Leveling by band','leveling.html'],['Items','items.html'],['Mobs','mobs.html'],['Zones','zones/index.html'],['Spells','spells.html'],['Market prices','market.html'],['Hotbar','hotbar.html'],['Quests','quests.html'],['Changelog','changelog.html']];
var GO={h:'index.html',c:'classes/index.html',w:'walkthrough.html',l:'leveling.html',i:'items.html',m:'mobs.html',z:'zones/index.html',s:'spells.html',k:'market.html',q:'quests.html'};
function href(u,ext){return ext?u:root+u}
window.MNM_UXC={root:root,esc:esc,recent:recent,here:here,JUMP:JUMP,GO:GO,href:href,S:S,lsGet:lsGet,lsPut:lsPut};
var palP=null;
function palLoad(){if(window.MNM_UX_PALI)return Promise.resolve();if(!window.MNM_LOAD)return Promise.reject(new Error('no loader'));
if(!palP)palP=MNM_LOAD('mod-ux-pal.js').then(function(){if(!window.MNM_UX_PALI)throw new Error('palette')},function(e){palP=null;throw e});return palP}
function palFail(from){var sq=document.getElementById('q');if(sq){sq.focus();sq.placeholder='Quick jump could not load (offline?). Search here instead…'}}
function open(from){from=from||document.activeElement;var pb=document.querySelector('.ux-palbtn');if(pb)pb.setAttribute('aria-busy','true');
palLoad().then(function(){if(pb)pb.removeAttribute('aria-busy');window.MNM_UX_PALI.open(from)},function(){if(pb)pb.removeAttribute('aria-busy');palFail(from)})}
function close(){if(window.MNM_UX_PALI)window.MNM_UX_PALI.close()}
function palOpen(){return !!(window.MNM_UX_PALI&&window.MNM_UX_PALI.isOpen())}
window.MNM_UX_PAL={open:open,close:close,load:palLoad};
var topin=document.querySelector('.top .topin'),sf=topin&&topin.querySelector('form.search');
if(topin){var pb=document.createElement('button');pb.type='button';pb.className='ux-palbtn';pb.setAttribute('aria-haspopup','dialog');pb.setAttribute('aria-label','Quick jump (Ctrl+K)');pb.title='Quick jump (Ctrl+K or /)';
pb.innerHTML='<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M13 13l5 5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg><kbd class="ux-palk">Ctrl K</kbd>';
if(sf&&sf.nextSibling)topin.insertBefore(pb,sf.nextSibling);else topin.appendChild(pb);pb.addEventListener('click',function(){open(pb)});
['pointerenter','focus','touchstart'].forEach(function(ev){pb.addEventListener(ev,function(){palLoad().catch(function(){})},{passive:true,once:true})})}
function keysOpen(){var from=document.activeElement;palLoad().then(function(){window.MNM_UX_PALI.keys(from)},function(){})}
window.MNM_UX_KEYS=keysOpen;
var gAt=0;
document.addEventListener('keydown',function(e){
if((e.ctrlKey||e.metaKey)&&!e.altKey&&!e.shiftKey&&(e.key==='k'||e.key==='K')){e.preventDefault();if(palOpen())close();else open();return}
if(e.ctrlKey||e.metaKey||e.altKey||typing(e.target)||document.querySelector('dialog[open]'))return;
if(e.key==='?'){e.preventDefault();keysOpen();return}
if(e.key==='g'){gAt=Date.now();return}
if(gAt&&Date.now()-gAt<1200&&GO[e.key]){e.preventDefault();gAt=0;location.href=root+GO[e.key];return}gAt=0;
if(e.key==='t'){e.preventDefault();window.scrollTo({top:0,behavior:'smooth'})}
});
var CTRL=[['f','#mnm-filter','v'],['gc','main .clsfilter','v'],['gk','main .kindfilter','c'],['gt','main .textfilter','v'],['sm','#sp-mine','c'],['sb','#sp-band','c']]
.map(function(c){return {p:c[0],el:document.querySelector(c[1]),t:c[2]}}).filter(function(c){return c.el});
var tabs=[].slice.call(document.querySelectorAll('main.main table.sortable, main.main table.grid')).filter(function(t){return t.tBodies[0]&&!t.closest('#mob-out,#idb-out')&&(t.classList.contains('sortable')||t.tBodies[0].rows.length>=15)});
var KT='mnm-tbl:'+here,st=lsGet(KT,{});if(!st||typeof st!=='object')st={};
function qpGet(n){var m=location.search.match(new RegExp('[?&]'+n+'=([^&]*)'));return m?decodeURIComponent(m[1].replace(/\+/g,' ')):null}
function writeUrl(){if(!history.replaceState)return;var keep=location.search.replace(/^\?/,'').split('&').filter(function(kv){return kv&&!/^(sort|f|gc|gk|gt|sm|sb)=/.test(kv)});
var add=[];if(st.sort&&Object.keys(st.sort).length)add.push('sort='+Object.keys(st.sort).map(function(i){return i+'.'+st.sort[i]}).join('~'));
CTRL.forEach(function(c){var v=(st.ctl||{})[c.p];if(v)add.push(c.p+'='+encodeURIComponent(v))});
var s=keep.concat(add).join('&');history.replaceState(history.state,'',location.pathname+(s?'?'+s:'')+location.hash)}
function save(){lsPut(KT,st);writeUrl()}
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
function vis(r){return r.style.display!=='none'&&!r.hidden&&!r.classList.contains('fhide')}
var bars=[];
function addBar(t,ti){var rows=t.tBodies[0].rows.length;if(rows<8)return;var host=t.closest('.tw')||t;
var b=document.createElement('div');b.className='ux-tbar';b.innerHTML='<span class="ux-tbar-n" role="status" aria-live="polite"></span><span class="ux-tbar-f"></span><span class="ux-tbar-s"></span><button type="button" class="ux-tbar-r">Reset</button>';
host.parentNode.insertBefore(b,host);b.querySelector('.ux-tbar-r').addEventListener('click',function(){reset(ti)});bars.push([b,t,ti]);
if(window.MutationObserver)new MutationObserver(function(){sched()}).observe(t.tBodies[0],{attributes:true,attributeFilter:['style','class','hidden'],subtree:true,childList:true})}
tabs.forEach(addBar);
window.MNM_UX_TBL=function(t){if(!t||!t.tBodies[0]||t.classList.contains('sortable')||t.tBodies[0].rows.length<15||bars.some(function(x){return x[1]===t}))return;addBar(t,-1);countAll()};
var raf=0;function sched(){if(!raf)raf=requestAnimationFrame(function(){raf=0;countAll()})}
function countAll(){bars.forEach(function(x){var b=x[0],t=x[1],ti=x[2],rs=[].slice.call(t.tBodies[0].rows),n=rs.filter(vis).length,s=st.sort[ti],fl=Object.keys(st.ctl).length;
var txt=n===rs.length?'Showing all '+rs.length+' rows':'Showing '+n+' of '+rs.length+' rows';var nn=b.querySelector('.ux-tbar-n');if(nn.textContent!==txt)nn.textContent=txt;
var th=s&&t.tHead&&t.tHead.rows[0].cells[parseInt(s)];b.querySelector('.ux-tbar-s').textContent=th?'Sorted by '+th.textContent.trim()+(s.slice(-1)==='d'?' (high to low)':' (low to high)'):'';
var fd=CTRL.filter(function(c){return st.ctl[c.p]}).map(function(c){return c.t==='c'?(c.el.closest('label')||{textContent:c.p}).textContent.trim():(c.el.tagName==='SELECT'?(c.el.selectedOptions[0]||{}).textContent:'“'+st.ctl[c.p]+'”')});b.querySelector('.ux-tbar-f').textContent=fd.length?'Filtered: '+fd.join(', '):'';
var r=b.querySelector('.ux-tbar-r');r.disabled=!s&&!fl;r.title=fl?'Clear the filters on this page and this table\u2019s sort':'Back to the original order'})}
function reset(ti){var t=tabs[ti];if(t){var tb=t.tBodies[0];orig[ti].forEach(function(r){tb.appendChild(r)})}if(t&&t.tHead)[].forEach.call(t.tHead.rows[0].cells,function(th){th.removeAttribute('aria-sort');delete th.dataset.dir});delete st.sort[ti];
CTRL.forEach(function(c){if(!ctlVal(c))return;if(c.t==='c'){c.el.checked=false;c.el.dispatchEvent(new Event('change',{bubbles:true}))}else{c.el.value='';c.el.dispatchEvent(new Event('input',{bubbles:true}));c.el.dispatchEvent(new Event('change',{bubbles:true}))}});
st.ctl={};save();countAll()}
countAll();if(fromUrl||Object.keys(st.sort).length||Object.keys(st.ctl).length)save();
var longT=tabs.filter(function(t){return t.tBodies[0].rows.length>=30})[0];
if(longT){var tt=document.createElement('button');tt.type='button';tt.className='ux-totop';tt.hidden=true;tt.setAttribute('aria-label','Back to top');tt.title='Back to top (t)';tt.innerHTML='<span aria-hidden="true">&#8593;</span> Top';
document.body.appendChild(tt);tt.addEventListener('click',function(){var rm=window.matchMedia('(prefers-reduced-motion:reduce)').matches;window.scrollTo({top:0,behavior:rm?'auto':'smooth'});var m=document.getElementById('content');if(m)setTimeout(function(){m.focus({preventScroll:true})},rm?0:400)});
var tick=0,chk=function(){tick=0;var y=window.scrollY,top=longT.getBoundingClientRect().top+y;tt.hidden=!(y>Math.max(600,top+300))};
window.addEventListener('scroll',function(){if(!tick){tick=1;requestAnimationFrame(chk)}},{passive:true});chk()}
})();
(function(){
var de=document.documentElement,root=de.getAttribute('data-root')||'',C=window.MNM_UXC||{};
function lsGet(k,d){try{var v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(e){return d}}
function lsPut(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function slug(s){return String(s||'').toLowerCase().replace(/'/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'')}
function load(f){return window.MNM_LOAD?window.MNM_LOAD(f):Promise.reject(new Error('no loader'))}
function fixh(h){return String(h||'').replace(/(href|src)="\/(?!\/)/g,'$1="'+root)}
var here=C.here||location.pathname.split('/').pop()||'index.html';
var live=document.createElement('div');live.className='ux-vh';live.setAttribute('role','status');live.setAttribute('aria-live','polite');document.body.appendChild(live);
function say(t){live.textContent='';setTimeout(function(){live.textContent=t},30)}
function refilter(){var f=document.getElementById('mnm-filter');if(f&&f.value)f.dispatchEvent(new Event('input'))}
function jumpHash(scope){var id;try{id=decodeURIComponent(location.hash.slice(1))}catch(e){return}if(!id)return;var t=document.getElementById(id);
if(t&&!t.classList.contains('ux-lzid')&&(!scope||scope.contains(t)))t.scrollIntoView()}
var CITY={ailvorith:"Ail'Vorith",'night-harbor':'Night Harbor',faelindral:'Faelindral',underdocks:'Underdocks'};
function cityName(sl){var s=document.getElementById('mnm-city');if(s)for(var i=0;i<s.options.length;i++)if(slug(s.options[i].value)===sl)return s.options[i].value;return CITY[sl]||sl}
function lzSet(el,kind,msg){var h=!kind?'':kind==='none'?'<p>'+msg+'</p>':'<p class="lz-status'+(kind==='err'?' lz-err':'')+'" role="status"'+(kind==='busy'?' aria-busy="true"':'')+'>'+msg+(kind==='err'?' <button type="button" class="ux-retry">Try again</button>':'')+'</p>';
if(el.innerHTML!==h)el.innerHTML=h}
function fillRoute(el){var c=de.getAttribute('data-sc')||'',w=el.parentNode,k=el.getAttribute('data-band'),lab=k.replace('-','\u2013');
if(!c){lzSet(el);return}
if(w.querySelector('.sc-route[data-sc="'+c+'"]')){lzSet(el);return}
if((' '+el.getAttribute('data-cities')+' ').indexOf(' '+c+' ')<0){lzSet(el,'none','<span class="badge unc">unverified</span> No start-city route for '+esc(cityName(c))+' in levels '+lab+': no sourced data yet.');return}
var f='walk-r-'+k+'-'+c+'.js',key=k+'|'+c;if(el._busy===f)return;el._busy=f;
lzSet(el,'busy','Loading the '+esc(cityName(c))+' route for levels '+lab+'\u2026');
load(f).then(function(){el._busy=0;var h=(window.MNM_WTR||{})[key];if(!h)throw new Error('missing '+key);
var t=document.createElement('template');t.innerHTML=fixh(h);var b=t.content.querySelector('.sc-route[data-sc="'+c+'"]');if(!b)throw new Error('missing '+key);
if(!w.querySelector('.sc-route[data-sc="'+c+'"]'))w.insertBefore(b,el);fillRoute(el);refilter();copyIn(b);jumpHash(w)},
function(){el._busy=0;if((de.getAttribute('data-sc')||'')!==c){fillRoute(el);return}lzSet(el,'err','Could not load the '+esc(cityName(c))+' route for levels '+lab+' (offline?).')})}
var lzs=[].slice.call(document.querySelectorAll('.sc-lz[data-band]')),want=[];
if(lzs.length){
var wantIt=function(el){if(want.indexOf(el)<0)want.push(el);fillRoute(el)};
if(window.IntersectionObserver){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){io.unobserve(e.target);wantIt(e.target)}})},{rootMargin:'1200px 0px'});lzs.forEach(function(el){io.observe(el)})}
else lzs.forEach(wantIt);
if(window.MutationObserver)new MutationObserver(function(){want.forEach(fillRoute)}).observe(de,{attributes:true,attributeFilter:['data-sc']});
window.addEventListener('beforeprint',function(){lzs.forEach(wantIt)});
window.MNM_UX_ROUTES={fillAll:function(){lzs.forEach(wantIt)}};
}
function paneLoad(p){if(!p||!p.hasAttribute('data-lz'))return Promise.resolve();if(p._lz)return p._lz;
var f=p.getAttribute('data-lz'),key=f.replace(/^ct-|\.js$/g,''),tb=document.querySelector('.tab[data-tab="'+p.id+'"]'),nm=tb?tb.textContent.trim():'this tab',st=p.querySelector('.ux-lzp');
if(st){st.className='lz-status ux-lzp';st.setAttribute('aria-busy','true');st.textContent='Loading \u201c'+nm+'\u201d\u2026'}
return p._lz=load(f).then(function(){var d=(window.MNM_CT||{})[key],h=d&&d[p.id];if(h==null)throw new Error('missing '+p.id);
p.innerHTML=h;p.removeAttribute('data-lz');[].forEach.call(p.querySelectorAll('table.grid'),function(t){if(window.MNM_UX_TBL)window.MNM_UX_TBL(t)});refilter();copyIn(p);jumpHash(p)},
function(){p._lz=null;var s=p.querySelector('.ux-lzp');if(s){s.removeAttribute('aria-busy');s.className='lz-status lz-err ux-lzp';s.innerHTML='Could not load \u201c'+esc(nm)+'\u201d (offline?). <button type="button" class="ux-retry">Try again</button>'}})}
var lzp=document.querySelectorAll('.tabpane[data-lz]');
if(lzp.length){
var paneOf=function(b){return b&&document.getElementById(b.getAttribute('data-tab'))};
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.tab[data-tab]');if(b)paneLoad(paneOf(b))},true);
['pointerenter','focusin'].forEach(function(ev){document.addEventListener(ev,function(e){var b=e.target.closest&&e.target.closest('.tab[data-tab]');if(b){var p=paneOf(b);if(p&&p.hasAttribute('data-lz'))paneLoad(p)}},true)});
var hashPane=function(){var id;try{id=decodeURIComponent(location.hash.slice(1))}catch(e){return}var t=id&&document.getElementById(id);if(!t||!t.classList.contains('ux-lzid'))return;var p=t.closest('.tabpane');
if(p&&!p.classList.contains('on')){var b=document.querySelector('.tab[data-tab="'+p.id+'"]');if(b)b.click()}else paneLoad(p)};
window.addEventListener('hashchange',hashPane);hashPane();
}
document.addEventListener('click',function(e){var r=e.target.closest&&e.target.closest('.ux-retry');if(!r)return;var l=r.closest('.sc-lz');if(l){fillRoute(l);return}paneLoad(r.closest('.tabpane[data-lz]'))});
function dbPage(o){var els={};o.ctl.forEach(function(c){els[c[0]]=document.getElementById(c[1])});if(!o.ctl.every(function(c){return els[c[0]]})||!o.data)return;
var D=o.data,orig=D.slice(),qEl=els[o.ctl[0][0]],cnt=document.getElementById(o.cnt),K='mnm-db:'+here,P=o.ctl.map(function(c){return c[0]}).concat([o.sp]);
var ss=document.createElement('select');ss.id=o.sp+'-sel';ss.setAttribute('aria-label','Sort results');ss.innerHTML=o.sorts.map(function(s){return '<option value="'+s[0]+'">'+esc(s[1])+'</option>'}).join('');
qEl.parentNode.appendChild(ss);els[o.sp]=ss;
function val(p){var e=els[p];return e.type==='checkbox'?(e.checked?'1':''):(e.value||'')}
function setv(p,v){var e=els[p];if(e.type==='checkbox')e.checked=v==='1';else if(e.tagName==='SELECT'){if([].some.call(e.options,function(x){return x.value===v}))e.value=v}else e.value=v}
function qp(n){var m=location.search.match(new RegExp('[?&]'+n+'=([^&]*)'));return m?decodeURIComponent(m[1].replace(/\+/g,' ')):null}
function sortData(){var k=ss.value,f=o.cmp[k],a=orig.slice();if(f)a.sort(f);for(var i=0;i<a.length;i++)D[i]=a[i]}
function rerun(){qEl.dispatchEvent(new Event('input',{bubbles:true}))}
var st={},h='';try{h=decodeURIComponent(location.hash.slice(1))}catch(e){}
if(P.some(function(p){return qp(p)!==null}))P.forEach(function(p){var v=qp(p);if(v)st[p]=v});
else if(h)st[o.ctl[0][0]]=h;else{st=lsGet(K,{});if(!st||typeof st!=='object')st={}}
P.forEach(function(p){setv(p,st[p]||'')});
var bar=document.createElement('div');bar.className='ux-tbar ux-dbbar';bar.innerHTML='<span class="ux-tbar-f"></span><span class="ux-tbar-s"></span><button type="button" class="ux-tbar-r">Reset</button>';
if(cnt){cnt.parentNode.insertBefore(bar,cnt);bar.insertBefore(cnt,bar.firstChild);cnt.classList.add('ux-tbar-n');cnt.setAttribute('role','status');cnt.setAttribute('aria-live','polite')}
function label(p){var e=els[p];if(e.type==='checkbox'){var l=e.closest('label');return l?l.textContent.trim():p}if(e.tagName==='SELECT')return (e.selectedOptions[0]||{}).textContent||'';return '\u201c'+e.value.trim()+'\u201d'}
function sync(){var cur={},add=[];P.forEach(function(p){var v=val(p);if(p===o.ctl[0][0])v=v.trim();if(v){cur[p]=v;add.push(p+'='+encodeURIComponent(v))}});lsPut(K,cur);
if(history.replaceState){var keep=location.search.replace(/^\?/,'').split('&').filter(function(kv){return kv&&P.indexOf(kv.split('=')[0])<0});var s=keep.concat(add).join('&');
history.replaceState(history.state,'',location.pathname+(s?'?'+s:''))}
var fl=o.ctl.filter(function(c){return cur[c[0]]}).map(function(c){return label(c[0])});
bar.querySelector('.ux-tbar-f').textContent=fl.length?'Filtered: '+fl.join(', '):'';
bar.querySelector('.ux-tbar-s').textContent=cur[o.sp]?'Sorted by '+(ss.selectedOptions[0]||{}).textContent.replace(/^Sort: /,''):'';
var r=bar.querySelector('.ux-tbar-r');r.disabled=!Object.keys(cur).length;r.title='Clear the search, filters and sort'}
ss.addEventListener('change',function(){sortData();rerun()});
P.forEach(function(p){els[p].addEventListener('input',sync);els[p].addEventListener('change',sync)});
bar.querySelector('.ux-tbar-r').addEventListener('click',function(){P.forEach(function(p){setv(p,'')});sortData();rerun();sync();qEl.focus()});
window.addEventListener('hashchange',function(){var x='';try{x=decodeURIComponent(location.hash.slice(1))}catch(e){}if(!x)return;P.forEach(function(p){setv(p,'')});setv(o.ctl[0][0],x);sortData();rerun();sync()});
sortData();rerun();sync();
if(o.copy){var out=document.getElementById(o.out);var add=function(){copyNames(out,o.copy)};add();if(window.MutationObserver)new MutationObserver(add).observe(out,{childList:true})}
}
function byName(a,b){return String(a[0]).localeCompare(String(b[0]))}
function lvl(i,dir){return function(a,b){var x=+a[i]||0,y=+b[i]||0;if(!x!==!y)return x?-1:1;return dir*(x-y)}}
if(document.getElementById('idb-out'))dbPage({data:window.MNM_IDB,cnt:'idb-count',out:'idb-out',sp:'isort',copy:'.idb-it>div:first-child>a.ext',
ctl:[['iq','idb-q'],['is','idb-slot'],['ic','idb-cls'],['il','idb-lvl'],['isrc','idb-src']],
sorts:[['','Sort: wiki order'],['n','Sort: name A\u2013Z'],['l','Sort: level, low to high'],['L','Sort: level, high to low']],cmp:{n:byName,l:lvl(4,1),L:lvl(4,-1)}});
if(document.getElementById('mob-out'))dbPage({data:window.MNM_MOBS,cnt:'mob-count',out:'mob-out',sp:'msort',copy:'tbody td:first-child',
ctl:[['mq','mob-q'],['mn','mob-named'],['ml','mob-lvl'],['md','mob-drop']],
sorts:[['','Sort: default order'],['n','Sort: name A\u2013Z'],['l','Sort: level, low to high'],['L','Sort: level, high to low'],['z','Sort: zone A\u2013Z']],
cmp:{n:byName,l:lvl(1,1),L:lvl(1,-1),z:function(a,b){return String(a[3]).localeCompare(String(b[3]))||byName(a,b)}}});
function copyText(t){if(navigator.clipboard&&window.isSecureContext)return navigator.clipboard.writeText(t).catch(function(){return copyOld(t)});return copyOld(t)}
function copyOld(t){return new Promise(function(ok,no){var a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();
var r=false;try{r=document.execCommand('copy')}catch(e){}a.remove();r?ok():no(new Error('copy'))})}
function copyBtn(t,what){var b=document.createElement('button');b.type='button';b.className='ux-copy';b.setAttribute('data-copy',t);b.setAttribute('aria-label','Copy '+what+': '+t);b.title='Copy \u201c'+t+'\u201d';
b.innerHTML='<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><rect x="5" y="5" width="9" height="9" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3 11V3.5A1.5 1.5 0 0 1 4.5 2H11" fill="none" stroke="currentColor" stroke-width="1.6"/></svg><span class="ux-copy-l">Copy</span>';return b}
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.ux-copy');if(!b)return;e.preventDefault();var t=b.getAttribute('data-copy'),l=b.querySelector('.ux-copy-l');
copyText(t).then(function(){b.classList.add('ok');l.textContent='Copied';say('Copied: '+t)},function(){b.classList.add('bad');l.textContent='Press Ctrl+C';say('Could not copy automatically. Select the text and press Ctrl+C.')})
.then(function(){clearTimeout(b._t);b._t=setTimeout(function(){b.classList.remove('ok','bad');l.textContent='Copy'},1800)})});
function copyIn(scope){[].forEach.call((scope||document).querySelectorAll('main.main code'),function(c){var t=c.textContent.trim();if(!/^\/[a-z]/i.test(t)||t.length>80||c.nextElementSibling&&c.nextElementSibling.classList.contains('ux-copy'))return;
c.parentNode.insertBefore(copyBtn(t,'command'),c.nextSibling)})}
function copyNames(out,sel){[].forEach.call(out.querySelectorAll(sel),function(a){if(a.querySelector('.ux-copy')||a.parentNode.querySelector(':scope>.ux-copy'))return;var bb=a.querySelector(':scope>b'),t=(bb?bb.textContent:a.tagName==='TD'?(a.firstChild&&a.firstChild.nodeType===3?a.firstChild.textContent:''):a.textContent).trim();if(!t)return;
var b=copyBtn(t,'name');if(a.tagName==='TD')a.insertBefore(b,a.querySelector('br'));else a.parentNode.insertBefore(b,a.nextSibling)})}
copyIn(document);
var KF='mnm-favs';function favs(){var f=lsGet(KF,[]);return Array.isArray(f)?f.filter(function(x){return x&&x.u}):[]}
var h1=document.querySelector('main.main h1'),ftitle=h1?h1.textContent.replace(/\s+/g,' ').trim().slice(0,90):document.title;
var star=null,fb=null,fpop=null;
function isFav(){return favs().some(function(f){return f.u===here})}
function favPaint(){var on=isFav(),n=favs().length;if(star){star.setAttribute('aria-pressed',on?'true':'false');star.innerHTML='<span aria-hidden="true">'+(on?'\u2605':'\u2606')+'</span><span class="ux-star-l">'+(on?'Pinned':'Pin')+'</span>';
star.title=on?'Unpin this page from your favorites':'Pin this page to your favorites (shown in the header \u2605 list and Ctrl+K)'}
if(fb){fb.hidden=!n;fb.querySelector('.ux-favn').textContent=n;fb.setAttribute('aria-label','Pinned pages ('+n+')')}
if(fpop&&!fpop.hidden)favList()}
if(h1){star=document.createElement('button');star.type='button';star.className='ux-star';star.setAttribute('aria-label','Pin this page: '+ftitle);h1.appendChild(star);
star.addEventListener('click',function(){var f=favs(),on=f.some(function(x){return x.u===here});f=on?f.filter(function(x){return x.u!==here}):[{u:here,t:ftitle}].concat(f).slice(0,30);lsPut(KF,f);favPaint();say(on?'Unpinned '+ftitle:'Pinned '+ftitle+'. Find it under the star in the header or with Ctrl+K.')})}
var topin=document.querySelector('.top .topin');
function favList(){var f=favs();fpop.innerHTML='<p class="ux-favh">Pinned pages</p>'+(f.length?'<ul>'+f.map(function(x){return '<li><a href="'+esc(root+x.u)+'"'+(x.u===here?' aria-current="page"':'')+'>'+esc(x.t)+'</a></li>'}).join('')+'</ul>':'<p class="dim">Nothing pinned yet.</p>')+'<p class="dim ux-favt">Pin or unpin with the \u2606 next to a page title. Saved in this browser only.</p>'}
function favClose(focus){if(!fpop||fpop.hidden)return;fpop.hidden=true;fb.setAttribute('aria-expanded','false');if(focus)fb.focus()}
if(topin){fb=document.createElement('button');fb.type='button';fb.className='ux-favbtn';fb.setAttribute('aria-expanded','false');fb.setAttribute('aria-controls','ux-favpop');fb.title='Pinned pages';
fb.innerHTML='<span aria-hidden="true">\u2605</span><span class="ux-favn"></span>';
var pb=topin.querySelector('.ux-palbtn');if(pb&&pb.nextSibling)topin.insertBefore(fb,pb.nextSibling);else topin.appendChild(fb);
fpop=document.createElement('div');fpop.id='ux-favpop';fpop.className='ux-favpop';fpop.hidden=true;topin.appendChild(fpop);
fb.addEventListener('click',function(){if(!fpop.hidden){favClose();return}favList();fpop.hidden=false;fb.setAttribute('aria-expanded','true');var a=fpop.querySelector('a');if(a)a.focus()});
document.addEventListener('click',function(e){if(fpop.hidden||e.target.closest('.ux-favpop,.ux-favbtn'))return;favClose()});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!fpop.hidden){favClose(true)}})}
window.addEventListener('storage',function(e){if(e.key===KF)favPaint()});
favPaint();
var cl=[],cln={};(de.getAttribute('data-cl')||'').split(' ').forEach(function(x){var m=x.match(/^(\d{4}-\d\d-\d\d)(?::(\d+))?$/);if(m){cl.push(m[1]);cln[m[1]]=+(m[2]||1)}});
(function(){var today=new Date(),d=today.getFullYear()+'-'+('0'+(today.getMonth()+1)).slice(-2)+'-'+('0'+today.getDate()).slice(-2),prev;
try{prev=sessionStorage.getItem('mnm-visit-prev');if(prev===null){prev=localStorage.getItem('mnm-lastvisit')||'';sessionStorage.setItem('mnm-visit-prev',prev)}localStorage.setItem('mnm-lastvisit',d)}catch(e){return}
if(!prev||!cl.length)return;var seen=lsGet('mnm-new-seen','')||'',since=seen>prev?seen:prev,n=cl.filter(function(x){return x>since}).reduce(function(t,x){return t+cln[x]},0);
var mo=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],nice=function(s){var p=s.split('-');return mo[+p[1]-1]+' '+(+p[2])};
if(/(^|\/)changelog\.html$/.test(here)){lsPut('mnm-new-seen',cl[0]);
[].forEach.call(document.querySelectorAll('main.main table.grid tbody tr'),function(tr){var c=tr.cells[0],m=c&&c.textContent.match(/^([A-Z][a-z]{2}) (\d{1,2}), (\d{4})$/);if(!m)return;
var iso=m[3]+'-'+('0'+(mo.indexOf(m[1])+1)).slice(-2)+'-'+('0'+m[2]).slice(-2);if(iso>prev){var s=document.createElement('span');s.className='ux-newtag';s.textContent='new';s.title='Added since your last visit ('+nice(prev)+')';c.appendChild(document.createTextNode(' '));c.appendChild(s)}});return}
if(!n)return;var cr=document.querySelector('.crumbs');if(!cr)return;
var b=document.createElement('span');b.className='ux-new';b.innerHTML='<a href="'+root+'changelog.html"><span aria-hidden="true">\u2726</span> '+n+' update'+(n>1?'s':'')+' since your last visit ('+nice(prev)+')</a><button type="button" class="ux-new-x" aria-label="Dismiss: '+n+' site updates since your last visit">\u2715</button>';
var v=cr.querySelector('.ver');cr.insertBefore(b,v||null);
b.querySelector('.ux-new-x').addEventListener('click',function(){lsPut('mnm-new-seen',cl[0]);b.remove()})})();
})();
