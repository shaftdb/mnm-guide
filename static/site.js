(function(){
var root=document.documentElement.getAttribute('data-root')||'';
// ---------- tabs
document.addEventListener('click',function(e){var b=e.target.closest('.tab');if(!b)return;var id=b.getAttribute('data-tab'),wrap=b.closest('.tabs');
wrap.querySelectorAll('.tab').forEach(function(x){x.classList.toggle('on',x===b)});wrap.querySelectorAll('.tabpane').forEach(function(p){p.classList.toggle('on',p.id===id)});});
// ---------- search
var idx=window.MNM_INDEX||[],q=document.getElementById('q'),res=document.getElementById('qres'),sel=-1;
function norm(s){return (s||'').toLowerCase()}
function search(term){term=norm(term).trim();if(term.length<2)return[];var words=term.split(/\s+/),out=[];
for(var i=0;i<idx.length;i++){var it=idx[i],t=norm(it.t),x=norm(it.x),sc=0,ok=true;
for(var w=0;w<words.length;w++){var wd=words[w];var ti=t.indexOf(wd),xi=x.indexOf(wd);if(ti<0&&xi<0){ok=false;break}
sc+=(ti===0?60:ti>0?30:0)+(xi>=0?5:0)}
if(ok){if(t===term)sc+=100;if(it.u.indexOf('#')<0)sc+=4;if(it.e)sc-=3;out.push([sc,it])}}
out.sort(function(a,b){return b[0]-a[0]});return out.slice(0,25).map(function(o){return o[1]})}
function snippet(x,term){var w=norm(term).split(/\s+/)[0],i=norm(x).indexOf(w);if(i<0)return'';var s=x.substr(Math.max(0,i-50),140);return '…'+s.replace(new RegExp('('+w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>')+'…'}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function show(){var term=q.value,r=search(term);sel=-1;if(!r.length){res.innerHTML=term.length>1?'<a>No matches</a>':'';res.hidden=term.length<2;return}
res.innerHTML=r.map(function(it){return '<a href="'+(it.e?it.u:root+it.u)+'"'+(it.e?' target="_blank" rel="noopener"':'')+'>'+esc(it.t)+'<small>'+esc(it.s)+(it.x?' · '+snippet(esc(it.x),term):'')+'</small></a>'}).join('');res.hidden=false}
if(q){q.addEventListener('input',show);q.addEventListener('focus',show);
q.addEventListener('keydown',function(e){var as=res.querySelectorAll('a[href]');if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();sel=Math.max(0,Math.min(as.length-1,sel+(e.key==='ArrowDown'?1:-1)));as.forEach(function(a,i){a.classList.toggle('sel',i===sel)})}
else if(e.key==='Enter'){var a=as[sel>=0?sel:0];if(a)location.href=a.href}else if(e.key==='Escape'){res.hidden=true}});
document.addEventListener('click',function(e){if(!e.target.closest('.search'))res.hidden=true});
document.addEventListener('keydown',function(e){if(e.key==='/'&&document.activeElement.tagName!=='INPUT'){e.preventDefault();q.focus()}});
var pq=(location.search.match(/[?&]q=([^&]*)/)||[])[1];if(pq){q.value=decodeURIComponent(pq.replace(/\+/g,' '));show()}}
// ---------- item tooltips
var tips=window.MNM_ITEMS||{},tip=document.getElementById('tip');
function place(e){var w=tip.offsetWidth,h=tip.offsetHeight,x=e.clientX+16,y=e.clientY+14;if(x+w>innerWidth-8)x=e.clientX-w-16;if(y+h>innerHeight-8)y=innerHeight-h-8;tip.style.left=x+'px';tip.style.top=y+'px'}
document.addEventListener('mouseover',function(e){var a=e.target.closest('.itm[data-i]');if(!a)return;var d=tips[a.getAttribute('data-i')];if(!d)return;
tip.innerHTML='<div class="tn">'+esc(d[0])+'</div>'+(d[1]?'<div class="tf">'+esc(d[1])+'</div>':'')+'<div>Slot: '+esc(d[2]||'?')+'</div><div class="ts">'+esc(d[3]||'No stats listed on wiki')+'</div><div class="tc">Class: '+esc(d[4])+'</div>'+(d[5]?'<div>Weight '+esc(d[5])+'</div>':'')+'<div class="ta">'+d[6].map(esc).join('<br>')+'<br>wiki page edited '+esc(d[7]||'?')+'</div>';tip.hidden=false;place(e)});
document.addEventListener('mousemove',function(e){if(!tip.hidden)place(e)});
document.addEventListener('mouseout',function(e){if(e.target.closest('.itm[data-i]'))tip.hidden=true});
// ---------- table sorting
document.querySelectorAll('table.sortable th').forEach(function(th){th.title='Click to sort';th.addEventListener('click',function(){var t=th.closest('table'),i=[].indexOf.call(th.parentNode.children,th),tb=t.tBodies[0],rows=[].slice.call(tb.rows),dir=th.dataset.dir==='a'?'d':'a';th.dataset.dir=dir;
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

// ---------- Brewsham level-range selector (embedded data; no fetch; file:// OK)
(function(){
var R=window.MNM_RANGES; if(!R||!R.order) return;
var KEY='mnm-brewsham-range';
var root=document.documentElement.getAttribute('data-root')||'';
var bar=document.getElementById('mnm-rangebar');
var sel=document.getElementById('mnm-range');
var qiLink=document.getElementById('mnm-range-qi');
var mount=document.getElementById('mnm-quickinfo');
var showBar=document.body.classList.contains('sec-home')||document.body.classList.contains('sec-shaman');
if(bar&&showBar) bar.hidden=false; else if(bar) bar.hidden=true;
function fixRoot(html){
  // Rewrite root-absolute href/src for Pages subpath and file:// relative roots
  return String(html).replace(/(href|src)="\/(?!\/)/g, '$1="'+root);
}
function readStored(){
  try{var v=localStorage.getItem(KEY); if(v&&R.panels[v]) return v;}catch(e){}
  return R.default||'11-15';
}
function writeStored(k){ try{localStorage.setItem(KEY,k);}catch(e){} }
function fillSelect(cur){
  if(!sel) return;
  sel.innerHTML=R.order.map(function(k){
    var lab=(R.panels[k]&&R.panels[k].label)||k;
    return '<option value="'+k+'"'+(k===cur?' selected':'')+'>'+lab+'</option>';
  }).join('');
}
function render(k){
  var p=R.panels[k]; if(!p) return;
  if(qiLink) qiLink.href=root+'shaman/quickinfo.html';
  if(!mount) return;
  var head='<div class="qi-head"><h2 style="margin-top:0">Quick info · '+p.label+'</h2>'+
    '<p class="dim" style="margin:.2em 0 .8em">Brewsham · Human Shaman · band '+p.label+
    ' · <a href="'+root+'shaman/leveling.html">Full leveling</a> · <a href="'+root+'shaman/guild-mats.html">Guild mats</a></p></div>';
  mount.setAttribute('data-seed', k);
  mount.innerHTML=head+fixRoot(p.html);
}
var cur=readStored();
fillSelect(cur);
if(sel){
  sel.value=cur;
  sel.addEventListener('change', function(){
    cur=sel.value; writeStored(cur); render(cur);
  });
}
if(qiLink) qiLink.href=root+'shaman/quickinfo.html';
// Always sync mount to stored band (overrides build-time 11-15 seed when needed)
if(mount) render(cur);
})();
