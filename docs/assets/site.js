(function(){
var root=document.documentElement.getAttribute('data-root')||'';
// ---------- tabs
document.addEventListener('click',function(e){var b=e.target.closest('.tab');if(!b)return;var id=b.getAttribute('data-tab'),wrap=b.closest('.tabs');
wrap.querySelectorAll('.tab').forEach(function(x){x.classList.toggle('on',x===b)});wrap.querySelectorAll('.tabpane').forEach(function(p){p.classList.toggle('on',p.id===id)});});
// ---------- search
var idx=window.MNM_INDEX||[],q=document.getElementById('q'),res=document.getElementById('qres'),sel=-1,idxP=null,idxErr=0;
// search-index.js is loaded on first use (focus, typing, / or ?q=) through the shared loader (UX pass 2)
function needIdx(){if(idx.length||idxP||!window.MNM_LOAD)return;idxP=MNM_LOAD('search-index.js').then(function(){idx=window.MNM_INDEX||[];if(q&&(q.value||document.activeElement===q))show()},function(){idxErr=1;idxP=null;if(q&&q.value)show()})}
function norm(s){return (s||'').toLowerCase()}
function search(term){term=norm(term).trim();if(term.length<2)return[];var words=term.split(/\s+/),out=[];
for(var i=0;i<idx.length;i++){var it=idx[i],t=norm(it.t),x=norm(it.x),sc=0,ok=true;
for(var w=0;w<words.length;w++){var wd=words[w];var ti=t.indexOf(wd),xi=x.indexOf(wd);if(ti<0&&xi<0){ok=false;break}
sc+=(ti===0?60:ti>0?30:0)+(xi>=0?5:0)}
if(ok){if(t===term)sc+=100;if(it.u.indexOf('#')<0)sc+=4;if(it.e)sc-=3;out.push([sc,it])}}
out.sort(function(a,b){return b[0]-a[0]});return out.slice(0,25).map(function(o){return o[1]})}
function snippet(x,term){var w=norm(term).split(/\s+/)[0],i=norm(x).indexOf(w);if(i<0)return'';var s=x.substr(Math.max(0,i-50),140);return '…'+s.replace(new RegExp('('+w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>')+'…'}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function show(){var term=q.value;needIdx();if(!idx.length&&term.length>1){res.innerHTML=idxErr?'<a class="lz-status lz-err">Search index could not load (offline?). Try again in a moment.</a>':'<a class="lz-status" aria-busy="true">Loading search index…</a>';res.hidden=false;if(idxErr){idxErr=0}return}
var r=search(term);sel=-1;if(!r.length){res.innerHTML=term.length>1?'<a>No matches</a>':'';res.hidden=term.length<2;return}
res.innerHTML=r.map(function(it){return '<a href="'+(it.e?it.u:root+it.u)+'"'+(it.e?' target="_blank" rel="noopener"':'')+'>'+esc(it.t)+'<small>'+esc(it.s)+(it.x?' · '+snippet(esc(it.x),term):'')+'</small></a>'}).join('');res.hidden=false}
if(q){q.addEventListener('input',show);q.addEventListener('focus',function(){needIdx();show()});q.addEventListener('pointerdown',needIdx);
q.addEventListener('keydown',function(e){var as=res.querySelectorAll('a[href]');if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();sel=Math.max(0,Math.min(as.length-1,sel+(e.key==='ArrowDown'?1:-1)));as.forEach(function(a,i){a.classList.toggle('sel',i===sel)})}
else if(e.key==='Enter'){var a=as[sel>=0?sel:0];if(a)location.href=a.href}else if(e.key==='Escape'){res.hidden=true}});
document.addEventListener('click',function(e){if(!e.target.closest('.search'))res.hidden=true});
document.addEventListener('keydown',function(e){if(e.key==='/'&&document.activeElement.tagName!=='INPUT'){e.preventDefault();q.focus()}});
var pq=(location.search.match(/[?&]q=([^&]*)/)||[])[1];if(pq){q.value=decodeURIComponent(pq.replace(/\+/g,' '));show()}}
// ---------- item tooltips
var tips=window.MNM_ITEMS||null,tip=document.getElementById('tip'),tipA=null,tipE=null;
// item-tips.js is loaded on the first item hover (UX pass 2); the tooltip says so while it loads
function needTips(){if(tips||!window.MNM_LOAD)return;MNM_LOAD('item-tips.js').then(function(){tips=window.MNM_ITEMS||{};if(tipA&&tipE)showTip(tipA,tipE)},function(){if(tipA){tip.innerHTML='<div class="lz-status lz-err">Item stats could not load (offline?)</div>';}})}
function place(e){var w=tip.offsetWidth,h=tip.offsetHeight,x=e.clientX+16,y=e.clientY+14;if(x+w>innerWidth-8)x=e.clientX-w-16;if(y+h>innerHeight-8)y=innerHeight-h-8;tip.style.left=x+'px';tip.style.top=y+'px'}
function showTip(a,e){if(!tips&&!window.MNM_LOAD)tips={};if(!tips){tip.innerHTML='<div class="lz-status" aria-busy="true">Loading item stats…</div>';tip.hidden=false;place(e);needTips();return}var d=tips[a.getAttribute('data-i')];if(!d){tip.hidden=true;return}
tip.innerHTML='<div class="tn">'+esc(d[0])+'</div>'+(d[1]?'<div class="tf">'+esc(d[1])+'</div>':'')+'<div>Slot: '+esc(d[2]||'?')+'</div><div class="ts">'+esc(d[3]||'No stats listed on wiki')+'</div><div class="tc">Class: '+esc(d[4])+'</div>'+(d[5]?'<div>Weight '+esc(d[5])+'</div>':'')+'<div class="ta">'+d[6].map(esc).join('<br>')+'<br>wiki page edited '+esc(d[7]||'?')+'</div>';tip.hidden=false;place(e)}
document.addEventListener('mouseover',function(e){var a=e.target.closest('.itm[data-i]');if(!a)return;tipA=a;tipE={clientX:e.clientX,clientY:e.clientY};showTip(a,e)});
document.addEventListener('mousemove',function(e){if(!tip.hidden){tipE={clientX:e.clientX,clientY:e.clientY};place(e)}});
document.addEventListener('mouseout',function(e){if(e.target.closest('.itm[data-i]')){tip.hidden=true;tipA=null}});
// ---------- table sorting
document.querySelectorAll('table.sortable th').forEach(function(th){th.title='Click to sort';th.tabIndex=0;th.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();th.click()}});th.addEventListener('click',function(){var t=th.closest('table'),i=[].indexOf.call(th.parentNode.children,th),tb=t.tBodies[0],rows=[].slice.call(tb.rows),dir=th.dataset.dir==='a'?'d':'a';th.dataset.dir=dir;
[].forEach.call(th.parentNode.children,function(o){if(o!==th){o.removeAttribute('aria-sort');delete o.dataset.dir}});th.setAttribute('aria-sort',dir==='a'?'ascending':'descending');
rows.sort(function(a,b){var x=(a.cells[i]||{}).textContent||'',y=(b.cells[i]||{}).textContent||'',nx=parseFloat(x.replace(/[^\d.-]/g,'')),ny=parseFloat(y.replace(/[^\d.-]/g,''));var c=(!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y);return dir==='a'?c:-c});rows.forEach(function(r){tb.appendChild(r)})})});
// ---------- gear filters
function applyFilters(){var cs=document.querySelector('.clsfilter'),kf=document.querySelector('.kindfilter'),tf=document.querySelector('.textfilter');
var c=cs?cs.value:'',hideNamed=kf&&kf.checked,t=tf?tf.value.toLowerCase():'';
document.querySelectorAll('table.gear tbody tr, table.filt-text tbody tr').forEach(function(r){var ok=true;var dc=r.getAttribute('data-c');
if(c&&dc!==null&&(' '+dc+' ').indexOf(' '+c+' ')<0)ok=false;
if(hideNamed&&r.getAttribute('data-k')&&r.getAttribute('data-k').indexOf('named')>=0&&!/quest|vendor|crafted|drop/.test(r.getAttribute('data-k').replace('named','')))ok=false;
if(t&&r.textContent.toLowerCase().indexOf(t)<0)ok=false;r.style.display=ok?'':'none'})}
document.querySelectorAll('.clsfilter,.kindfilter,.textfilter').forEach(function(el){el.addEventListener('input',applyFilters);el.addEventListener('change',applyFilters)});
if(document.querySelector('.clsfilter'))applyFilters();
})();

// ---------- Class + level-range selector (sticky bar on every page) + page filter
(function(){
var R=window.MNM_RANGES; if(!R||!R.order) return;
var KR='mnm-range', KC='mnm-class';
var root=document.documentElement.getAttribute('data-root')||'';
var selR=document.getElementById('mnm-range'), selC=document.getElementById('mnm-class');
var qiLink=document.getElementById('mnm-range-qi'), mount=document.getElementById('mnm-quickinfo');
function get(k,ok,d){try{var v=localStorage.getItem(k);if(v&&ok(v))return v;}catch(e){}return d;}
function put(k,v){try{localStorage.setItem(k,v);}catch(e){}}
var cur=get(KR,function(v){return R.order.indexOf(v)>=0},R.default);
var cls=get(KC,function(v){return R.classes.indexOf(v)>=0},R.defaultClass||R.classes[0]);
function fix(h){return String(h).replace(/(href|src)="\/(?!\/)/g,'$1="'+root);}
if(selR) selR.innerHTML=R.order.map(function(k){return '<option value="'+k+'"'+(k===cur?' selected':'')+'>'+(R.labels[k]||k)+'</option>'}).join('');
if(selC) selC.innerHTML=R.classes.map(function(c){return '<option'+(c===cls?' selected':'')+'>'+c+'</option>'}).join('');
function render(){
  if(qiLink) qiLink.href=mount?'#mnm-quickinfo':root+'index.html#mnm-quickinfo';
  var Q=window.MNM_QUICK; if(!mount||!Q) return;
  var p=Q.panels[cls+'|'+cur];
  // UX pass 2: quick-data.js is split; load this class's panels (and this band's start-city route) on demand
  var L=Q.lazy,need=[];if(L&&window.MNM_LOAD){if(!p&&L.cls&&L.cls[cls])need.push(L.cls[cls]);if(L.band&&L.band[cur]&&!(cur in Q.route)&&(!p||p.indexOf('<!--sc-route')>=0))need.push(L.band[cur]);}
  if(need.length){var want=cls+'|'+cur;var st=mount.querySelector('.lz-status');if(!st){st=document.createElement('p');st.className='lz-status';st.setAttribute('role','status');mount.insertBefore(st,mount.firstChild)}
   st.textContent='Loading Quick info for '+cls+' · '+(R.labels[cur]||cur)+'…';st.classList.remove('lz-err');mount.setAttribute('aria-busy','true');
   Promise.all(need.map(function(f){return MNM_LOAD(f)})).then(function(){mount.removeAttribute('aria-busy');if(cls+'|'+cur===want)render()},function(){mount.removeAttribute('aria-busy');st.textContent='Quick info for '+cls+' could not load (offline?). Change class or levels to retry.';st.classList.add('lz-err')});return}
  if(!p) return;
  mount.innerHTML='<div class="qi-head"><h2 style="margin-top:0">Quick info · '+cls+' · '+(R.labels[cur]||cur)+'</h2>'+
   '<p class="dim">Change class or levels in the bar at the top (remembered in this browser). <a href="'+root+String(R.urls[cls]).replace(/^\//,'')+'">Full '+cls+' guide</a></p></div>'+fix(p).replace('<!--sc-route-->','<div class="qi-sec sc-qi">'+fix((Q.route||{})[cur]||'')+'</div>').replace('<!--sc-route-nh-->','<div class="qi-sec sc-qi">'+fix((Q.routenh||{})[cur]||'')+'</div>');
  var f=document.getElementById('mnm-filter'); if(f&&f.value) f.dispatchEvent(new Event('input'));
  try{document.dispatchEvent(new CustomEvent('mnm:quick'))}catch(e){}
}
function marks(){
  var b=cur.split('-').map(Number), code=(R.codes||{})[cls];
  document.querySelectorAll('[data-lo]').forEach(function(el){var lo=+el.getAttribute('data-lo'),hi=+el.getAttribute('data-hi');
    el.classList.toggle('inband',!!lo&&lo<=b[1]&&hi>=b[0]);});
  document.querySelectorAll('[data-cls]').forEach(function(el){el.classList.toggle('clsok',('|'+el.getAttribute('data-cls')+'|').indexOf('|'+cls+'|')>=0);});
  document.querySelectorAll('table.dloot tbody tr').forEach(function(tr){var c=(tr.getAttribute('data-c')||'').split(' ');tr.classList.toggle('clsok',!!code&&c.indexOf(code)>=0);});
}
marks();
if(selR) selR.addEventListener('change',function(){cur=selR.value;put(KR,cur);render();marks();});
if(selC) selC.addEventListener('change',function(){cls=selC.value;put(KC,cls);render();marks();});
render();
// page filter: hides list items, table rows, paragraphs and blocks that don't match
var f=document.getElementById('mnm-filter'), main=document.querySelector('main.main');
if(f&&main){f.addEventListener('input',function(){
  var t=f.value.trim().toLowerCase();
  main.querySelectorAll('li,tbody tr,p,.camp,details,.call,.qi-sec,.dcard,.zcard').forEach(function(el){
    if(!t){el.classList.remove('fhide');return;}
    el.classList.toggle('fhide',el.textContent.toLowerCase().indexOf(t)<0);
  });
  // keep containers visible if any child matches
  if(t) main.querySelectorAll('.qi-sec,details,.call,.camp,.dcard,.zcard').forEach(function(el){
    if(el.querySelector('li:not(.fhide),tbody tr:not(.fhide),p:not(.fhide)')) el.classList.remove('fhide');
  });
});}
})();
