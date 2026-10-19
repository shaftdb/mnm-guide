// Tradeskill picker (top bar, multi-select, localStorage "mnm-trades"), per-level-range tradeskill guidance, selection filtering, gear badges.
(function(){
var T=window.MNM_TS; if(!T) return;
var root=document.documentElement.getAttribute('data-root')||'', R=window.MNM_RANGES||{};
var KEY=T.key, all=T.skills.map(function(s){return s.s}), defs=T.skills.filter(function(s){return s.d}).map(function(s){return s.s});
var bySlug={}, byName={}; T.skills.forEach(function(s){bySlug[s.s]=s;byName[s.n]=s.s;});
function load(){try{var v=JSON.parse(localStorage.getItem(KEY));if(Array.isArray(v))return v.filter(function(x){return all.indexOf(x)>=0});}catch(e){}return defs.slice();}
function save(){try{localStorage.setItem(KEY,JSON.stringify(sel));}catch(e){}}
var sel=load();
function fix(h){return String(h).replace(/(href|src)="\/(?!\/)/g,'$1="'+root);}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function range(){var r=document.getElementById('mnm-range');var v=r&&r.value;if(!v){try{v=localStorage.getItem('mnm-range')}catch(e){}}return (R.order&&R.order.indexOf(v)>=0)?v:(R.default||'11-15');}
function cls(){var c=document.getElementById('mnm-class');var v=c&&c.value;if(!v){try{v=localStorage.getItem('mnm-class')}catch(e){}}return v||R.defaultClass||'Fighter';}
// ---- menu
var dd=document.getElementById('mnm-ts'), menu=document.getElementById('mnm-ts-menu'), sum=document.getElementById('mnm-ts-sum');
function buildMenu(){if(!menu)return;var h='';
 T.kinds.forEach(function(k){var ss=T.skills.filter(function(s){return s.k===k[0]});if(!ss.length)return;
  h+='<fieldset><legend>'+esc(k[1])+'</legend>'+ss.map(function(s){return '<label><input type="checkbox" value="'+s.s+'"'+(sel.indexOf(s.s)>=0?' checked':'')+'> '+esc(s.n)+(s.x?' <small>(smithing, off by default)</small>':'')+'</label>'}).join('')+'</fieldset>';});
 h+='<div class="ts-btns"><button type="button" data-ts-set="def">Defaults</button><button type="button" data-ts-set="all">All</button><button type="button" data-ts-set="none">None</button></div>';
 menu.innerHTML=h;}
function summary(){if(!sum)return;sum.textContent=!sel.length?'None':sel.length===1?bySlug[sel[0]].n:(sel.length===defs.length&&defs.every(function(x){return sel.indexOf(x)>=0})?'Gathering ('+sel.length+')':sel.length+' trades');
 sum.title=sel.map(function(s){return bySlug[s].n}).join(', ')||'No tradeskills selected';}
if(menu){menu.addEventListener('change',function(e){var i=e.target;if(i.type!=='checkbox')return;var p=sel.indexOf(i.value);if(i.checked&&p<0)sel.push(i.value);if(!i.checked&&p>=0)sel.splice(p,1);
  sel=all.filter(function(x){return sel.indexOf(x)>=0});save();update();});
 menu.addEventListener('click',function(e){var b=e.target.closest('[data-ts-set]');if(!b)return;var m=b.getAttribute('data-ts-set');sel=m==='all'?all.slice():m==='none'?[]:defs.slice();save();buildMenu();update();
document.addEventListener('mnm:quick',function(){filter();mounts();badges();});});}
document.addEventListener('click',function(e){if(dd&&dd.open&&!e.target.closest('#mnm-ts'))dd.open=false;});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&dd)dd.open=false;});
// ---- filtering of tagged content
function on(tags){return String(tags).split(/\s+/).some(function(t){return sel.indexOf(t)>=0});}
function filter(){var showAll=[].some.call(document.querySelectorAll('.ts-showall'),function(c){return c.checked});
 document.querySelectorAll('[data-ts]').forEach(function(el){if(el.classList.contains('ts-page')||el.closest('[data-ts-mount]'))return;el.classList.toggle('tshide',!showAll&&!on(el.getAttribute('data-ts')));});
 var pg=document.querySelector('.ts-page'),ns=document.querySelector('.ts-notsel');if(pg&&ns)ns.hidden=on(pg.getAttribute('data-ts'));}
document.addEventListener('change',function(e){if(e.target.classList&&e.target.classList.contains('ts-showall')){document.querySelectorAll('.ts-showall').forEach(function(c){c.checked=e.target.checked});filter();}});
// ---- UX pass 2: trade-data.js is split; per-skill guidance chunks and the item list load only where a page uses them
var LZ=T.lazy,lzBusy={},lzFail={};
function needBands(){if(!LZ||!window.MNM_LOAD)return [];return sel.filter(function(x){return LZ.bands[x]&&!lzFail[x]&&!Object.prototype.hasOwnProperty.call(T.bands,x+'|'+range())})}
function loadBands(miss){miss.forEach(function(x){if(lzBusy[x])return;lzBusy[x]=1;MNM_LOAD(LZ.bands[x]).then(function(){lzBusy[x]=0;mounts()},function(){lzBusy[x]=0;lzFail[x]=1;mounts()})})}
// ---- per-level-range guidance
function mounts(){var r=range(),lab=(R.labels&&R.labels[r])||r,ms=document.querySelectorAll('[data-ts-mount]');
 if(ms.length){var miss=needBands();if(miss.length){loadBands(miss);ms.forEach(function(m){var b=m.querySelector('.ts-body');if(!b){b=document.createElement('div');b.className='ts-body';m.appendChild(b);}
  b.setAttribute('aria-busy','true');b.innerHTML='<p class="lz-status" role="status">Loading tradeskill guidance for '+esc(miss.map(function(x){return bySlug[x].n}).join(', '))+'…</p>'});return}}
 var failed=sel.filter(function(x){return lzFail[x]});
 document.querySelectorAll('[data-ts-mount]').forEach(function(m){var b=m.querySelector('.ts-body');if(!b){b=document.createElement('div');b.className='ts-body';m.appendChild(b);}b.removeAttribute('aria-busy');
  var h=sel.map(function(s){return T.bands[s+'|'+r]||''}).join('');
  b.innerHTML=fix('<p class="dim">Character levels <b>'+esc(lab)+'</b> · '+(sel.length?sel.length+' tradeskill(s)':'no tradeskills')+' selected.</p>'+(failed.length?'<p class="lz-status lz-err">Could not load guidance for '+esc(failed.map(function(x){return bySlug[x].n}).join(', '))+' (offline?). Reload to retry.</p>':'')+(h||'<p><span class="badge unc">none selected</span> Pick tradeskills in the <b>Trades</b> menu in the top bar.</p>')+T.note);});}
// ---- gear badges
var BADGE_SEL='table.gear a.itm[data-i], ul.gearlist a.itm[data-i], .quickinfo a.itm[data-i]',itBusy=0;
function badges(){if(!T.items){if(LZ&&window.MNM_LOAD&&!itBusy&&document.querySelector(BADGE_SEL)){itBusy=1;MNM_LOAD(LZ.items).then(function(){badges()},function(){itBusy=0})}return}
 var c=cls(),code=(R.codes||{})[c],hi=+range().split('-')[1];
 document.querySelectorAll('.ts-badge').forEach(function(b){b.remove()});
 document.querySelectorAll(BADGE_SEL).forEach(function(a){var d=T.items[a.getAttribute('data-i')];if(!d)return;
  if(code&&d.c.indexOf(code)<0)return; if(d.l!=null&&d.l>hi)return;
  d.e.forEach(function(e){var s=byName[e[0]];if(!s||sel.indexOf(s)<0)return;var sp=document.createElement('span');
   sp.className='ts-badge'+(e[3]?'':' unc');sp.textContent=e[0]+' '+e[1]+(e[2]==='used'?' (used)':'')+(e[3]?'':' ?');
   sp.title=(e[2]==='used'?'Used as a material in a wiki '+e[0]+' recipe (trivial '+e[1]+')':'Made with '+e[0]+' (wiki trivial '+e[1]+')')+(e[3]?' — linked in the wiki recipe table':' — UNVERIFIED: only the item page names the skill; no wiki recipe table links it');
   a.parentNode.insertBefore(sp,a.nextSibling);});});}
function update(){summary();filter();mounts();badges();}
buildMenu();update();
['mnm-range','mnm-class'].forEach(function(id){var el=document.getElementById(id);if(el)el.addEventListener('change',function(){setTimeout(function(){filter();mounts();badges();},0)});});
})();
