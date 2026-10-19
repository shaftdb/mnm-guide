// Race + Starting City selectors (top bar; localStorage mnm-race / mnm-city; URL ?class=&race=&city=), character-creation tailoring, walkthrough renderer.
(function(){
var G=window.MNM_CG; if(!G) return;
var root=document.documentElement.getAttribute('data-root')||'';
var selC=document.getElementById('mnm-class'), selR=document.getElementById('mnm-race'), selT=document.getElementById('mnm-city'), selL=document.getElementById('mnm-range');
function get(k){try{return localStorage.getItem(k)}catch(e){return null}}
function put(k,v){try{localStorage.setItem(k,v)}catch(e){}}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function rel(u){return root+String(u).replace(/^\//,'')}
function scslug(s){return String(s||'').toLowerCase().replace(/'/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'')}
// start-city route HTML holds every city; keep only the given city's block (shown regardless of the html[data-sc] CSS)
function scFor(h,city){if(!h)return '';var d=document.createElement('div');d.innerHTML=fixh(h);var sl=scslug(city);
  d.querySelectorAll('.sc-route').forEach(function(e){if(e.getAttribute('data-sc')===sl)e.classList.add('sc-on');else e.remove()});
  d.querySelectorAll('.sc-pick').forEach(function(e){e.remove()});
  if(!d.querySelector('.sc-route'))return '<p>'+badge('unverified')+' No start-city route for '+esc(city||'?')+' in this level range: no sourced data yet.</p>';return d.innerHTML}
function fixh(h){return String(h||'').replace(/(href|src)="\/(?!\/)/g,'$1="'+root);}
function qp(n){var m=location.search.match(new RegExp('[?&]'+n+'=([^&]*)'));return m?decodeURIComponent(m[1].replace(/\+/g,' ')):null}
function cls(){return (selC&&selC.value)||get('mnm-class')||'Fighter'}
function races(c){return Object.keys(G.combos[c]||{}).sort(function(a,b){return (G.large.indexOf(a)>=0)-(G.large.indexOf(b)>=0)||a.localeCompare(b)})}
function cities(c,r){return ((G.combos[c]||{})[r])||[]}
function defRace(c){var rs=races(c).filter(function(r){return G.large.indexOf(r)<0});return rs.indexOf('Human')>=0?'Human':(rs[0]||races(c)[0]||'')}
var race=null, city=null, fromUrl=false;
// URL first (share links), then localStorage
var uc=qp('class'), ur=qp('race'), ut=qp('city');
if(uc&&selC&&G.combos[uc]&&selC.value!==uc){selC.value=uc;put('mnm-class',uc);fromUrl=true;setTimeout(function(){selC.dispatchEvent(new Event('change'))},0);}
function pick(){var c=cls();var rs=races(c);
  var r=race||get('mnm-race'); if(rs.indexOf(r)<0) r=defRace(c); race=r;
  var cs=cities(c,r); var t=city||get('mnm-city'); if(cs.indexOf(t)<0) t=cs[0]||''; city=t;}
if(ur){race=ur;fromUrl=true} if(ut){city=ut;fromUrl=true}
pick();
// ---- validity: every playable race and every city is listed; invalid ones are disabled with a visible reason
var ALLR=(G.playable||Object.keys(G.races)).slice().sort(function(a,b){return (G.large.indexOf(a)>=0)-(G.large.indexOf(b)>=0)||a.localeCompare(b)});
function classesFor(r){return Object.keys(G.combos).filter(function(c){return (G.combos[c]||{})[r]}).sort()}
function classesForCity(r,t){return Object.keys(G.combos).filter(function(c){return cities(c,r).indexOf(t)>=0}).sort()}
function lst(a){return a.length?a.join(', '):'none'}
function raceWhy(c,r){var cs=classesFor(r);return r+': not available as '+c+(cs.length?'; '+r+' can be '+lst(cs):'; not playable in Early Access')}
function cityWhy(c,r,t){var cs=classesForCity(r,t);return t+': not available for '+r+' '+c+(cs.length?'; available for '+r+' '+lst(cs):'; not available for any '+r+' class')}
function noteFor(c,r,t){return (G.notes||{})[c+'|'+r+'|'+t]}
function fill(){var c=cls(),ok=races(c),okc=cities(c,race);
  if(selR) selR.innerHTML=ALLR.map(function(r){var lg=G.large.indexOf(r)>=0,v=ok.indexOf(r)>=0;
    var t=v?(lg?'Large race: a valid option, but this Codex never defaults to or recommends it':''):raceWhy(c,r);
    return '<option value="'+esc(r)+'"'+(r===race?' selected':'')+(v?'':' disabled aria-disabled="true"')+(t?' title="'+esc(t)+'"':'')+'>'+esc(r)+(lg&&v?' (large race)':'')+(v?'':' (not for '+esc(c)+')')+'</option>'}).join('')||'<option value="">(no wiki data)</option>';
  if(selT) selT.innerHTML=G.cities.map(function(t){var v=okc.indexOf(t)>=0,n=noteFor(c,race,t);
    return '<option value="'+esc(t)+'"'+(t===city?' selected':'')+(v?'':' disabled aria-disabled="true"')+' title="'+esc(v?(n?t+': '+n[1]:t+': valid for '+race+' '+c):cityWhy(c,race,t))+'">'+esc(t)+(v?(n?' (unverified)':''):' (not for '+esc(race)+' '+esc(c)+')')+'</option>'}).join('');
  valid();}
var VB=document.getElementById('cg-valid');
function valid(){if(!VB)return;var c=cls(),r=race,okc=cities(c,r);
  var per=G.cities.map(function(t){var cs=classesForCity(r,t);return cs.length?'<b>'+esc(t)+'</b> ('+(cs.length===classesFor(r).length?'all '+cs.length+' classes':cs.length+': '+esc(cs.join(', ')))+')':null}).filter(Boolean);
  var badR=ALLR.filter(function(x){return races(c).indexOf(x)<0}),badT=G.cities.filter(function(t){return okc.indexOf(t)<0});
  var n=okc.map(function(t){return noteFor(c,r,t)}).filter(Boolean);
  VB.innerHTML='<span class="cg-vl"><span class="cg-vk">Valid starts for '+esc(r||'?')+':</span> '+(per.join(' · ')||'none on the wiki table')+'.</span> '+
   '<span class="cg-vl cg-vcur">'+esc(r+' '+c)+': '+(okc.length?esc(okc.join(', ')):'no start')+(n.length?' <span class="badge unc">unverified</span>':'')+'.</span> '+
   ((badR.length||badT.length)?'<details class="cg-why"><summary>Why are some options greyed out?</summary><ul>'+
     badT.map(function(t){return '<li>'+esc(cityWhy(c,r,t))+'.</li>'}).join('')+badR.map(function(x){return '<li>'+esc(raceWhy(c,x))+'.</li>'}).join('')+
     n.map(function(x){return '<li>'+esc(x[1])+'</li>'}).join('')+
     '<li class="dim">Source: wiki start-city table rev '+esc((G.audit||{}).rev||'')+', re-checked '+esc((G.audit||{}).checked||'')+'.</li></ul></details>':'');}
function url(){if(!history.replaceState)return;var s=location.search.replace(/^\?/,'').split('&').filter(function(kv){return kv&&!/^(class|race|city)=/.test(kv)});
  s.push('class='+encodeURIComponent(cls()),'race='+encodeURIComponent(race),'city='+encodeURIComponent(city));
  history.replaceState(null,'',location.pathname+'?'+s.join('&')+location.hash);}
function save(){put('mnm-race',race);put('mnm-city',city);}
function changed(writeUrl){save();if(writeUrl)url();document.dispatchEvent(new CustomEvent('mnm-chargen',{detail:{cls:cls(),race:race,city:city}}));apply();}
fill(); save(); if(fromUrl&&!uc) url(); if(fromUrl&&uc) setTimeout(url,0);
if(selR) selR.addEventListener('change',function(){race=selR.value;city=null;pick();fill();changed(true)});
if(selT) selT.addEventListener('change',function(){city=selT.value;changed(true)});
if(selC) selC.addEventListener('change',function(){setTimeout(function(){pick();fill();changed(/[?&](race|city)=/.test(location.search))},0)});
if(selL) selL.addEventListener('change',function(){setTimeout(apply,0)});
window.MNM_CHARGEN={get:function(){return {cls:cls(),race:race,city:city}}};

// ---- character-creation section tailoring
function tailor(){document.querySelectorAll('[data-cg-race]').forEach(function(el){var on=el.getAttribute('data-cg-race')===race;
  el.classList.toggle('cg-sel',on); if(el.getAttribute('data-cg-only')||el.classList.contains('cg-res')) el.hidden=!on;});}
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.cg-ts-apply');if(!b)return;
  try{localStorage.setItem('mnm-trades',b.getAttribute('data-ts'))}catch(x){}var m=b.parentNode.querySelector('.cg-ts-msg');if(m)m.textContent='Saved to your Trades picker. Reloading…';setTimeout(function(){location.reload()},400);});

// ---- walkthrough
var W=window.MNM_WT, mount=document.getElementById('cg-walk'), wtFail=0;
function band(){var v=(selL&&selL.value)||get('mnm-range')||'11-15';return v}
function bl(k){return k.split('-').map(Number)}
function badge(l){l=String(l||'unverified').toUpperCase();var c=l==='FACT'?'fact':l==='STRATEGY'?'strat':'unc';return '<span class="badge '+c+'">'+esc(l.toLowerCase())+'</span>'}
// walkHTML: the one walkthrough renderer (walkthrough.html and the class-page Quick info summary). opt (optional) collects the per-band parts.
function walkHTML(c,race,city,k,opt){var code=W.codes[c],C=W.cities[city],R=W.races[race]||{},b=bl(k);
  if(!C)return '<p>'+badge('unverified')+' No sourced data yet for '+esc(race)+' '+esc(c)+' starting in '+esc(city||'(no start)')+': this start has no wiki start-city data. Pick another race or start in the top bar.</p>';
  var h=[];var dist=C.dist;
  function dz(z){return dist[z]==null?99:dist[z]}
  h.push('<div class="cg-head"><h2 style="margin-top:0">'+esc(race)+' '+esc(c)+' · starting in <a class="ext" target="_blank" rel="noopener" href="'+esc(C.u)+'">'+esc(city)+'</a></h2>'+
   '<p class="dim">'+(noteFor(c,race,city)?badge('unverified')+' '+esc(noteFor(c,race,city)[1]):badge('fact')+' Valid on the wiki start-city table'+((G.deities[c+'|'+race+'|'+city]||[]).length?' for deities: '+esc(G.deities[c+'|'+race+'|'+city].join(', ')):'')+'.')+' Change class, race, start or levels in the top bar.'+
   (G.chargen[c]?' · <a href="'+rel(G.chargen[c])+'#chargen">'+esc(c)+' character creation</a>':'')+'</p></div>');
  // faction / race risks
  var risk=[];
  if(R.al) risk.push('<li>'+badge('fact')+' '+esc(race)+' faction alignment on the wiki: <b>'+esc(R.al)+'</b>.</li>');
  if(R.note) risk.push('<li>'+badge('fact')+' Race page note: '+esc(R.note)+'</li>');
  Object.keys(W.cities).forEach(function(t){if(W.cities[t].faq) risk.push('<li>'+badge('fact')+' <b>'+esc(t)+'</b> (official FAQ): '+esc(W.cities[t].faq)+'</li>')});
  if(R.al==='Evil') risk.push('<li>'+badge('unverified')+' How other cities treat an evil race: see <b>Faction, KoS and when it is safe to travel</b> in the start-city box above. Where that box has no notes for your race and city: no sourced data yet. The FAQ says factions "will begin to matter much more".</li>');
  if(C.home.length) risk.push('<li>'+badge('fact')+' Home-city factions on the wiki: '+C.home.map(esc).join(', ')+'. Their "lowered by" lists are flagged in each level range below.</li>');
  h.push(rtHTML('h','',city));
  h.push('<details class="call" open><summary><b>Faction risks for this race and city (wiki faction pages)</b></summary><ul class="tight">'+risk.join('')+'</ul></details>');
  // level 1 start
  var st=W.walk[c+'|'+city]||[];
  var tr=(C.tr||{})[c]||[];
  // quest class field mixes codes (SHD) and names (Druid, Shadow Knight): match either
  function qFor(q){return q[4]==='ALL'||q[4]==='ANY'||q[4].split(' ').indexOf(code)>=0||(' '+q[4]+' ').indexOf(' '+c+' ')>=0}
  var sq=W.quests.filter(function(q){return q[2]===city&&(q[3]==null||q[3]<=2)&&qFor(q)&&/starter|class/i.test(q[0])});
  var s1=st.map(function(s){return '<li>'+badge(s.label)+' '+esc(s.text)+'</li>'});
  if(!st.length){
    s1.push('<li>'+(tr.length?badge('fact')+' Class trainer in '+esc(city)+': '+tr.map(function(t){return '<b>'+esc(t.npc)+'</b>'+(t.where?' ('+esc(t.where)+')':'')}).join(', '):badge('unverified')+' No '+esc(c)+' trainer listed on the wiki '+esc(city)+' page: no sourced data yet.')+'</li>');
    s1.push(sq.length?'<li>'+badge('fact')+' Starter / class quests here: '+sq.map(function(q){return '<a class="ext" target="_blank" rel="noopener" href="'+esc(q[1])+'">'+esc(q[0])+'</a>'}).join(', ')+'. Step lists: <a href="'+rel('/quest-helper.html')+'">quest helper</a>.</li>':'<li>'+badge('unverified')+' No '+esc(c)+' starter quest for '+esc(city)+' in the wiki data: no sourced data yet.</li>');
  }
  h.push('<h2 id="wt-start">Level 1: first steps in '+esc(city)+'</h2><ol class="cg-steps">'+s1.join('')+'</ol>');
  // bands
  W.bands.forEach(function(B){var bb=bl(B[0]),lo=bb[0],hi=bb[1],cur=B[0]===k;
    var zs=Object.keys(W.zones).filter(function(z){var Z=W.zones[z];return Z.lo!=null&&Z.lo<=hi&&Z.hi>=lo&&dz(z)<99}).sort(function(a,b){return dz(a)-dz(b)||W.zones[a].lo-W.zones[b].lo}).slice(0,5);
    var o=[];
    o.push(rtHTML('r',B[0],city));
    o.push('<h3>Nearby zones by wiki connections '+badge('strategy')+'</h3>'+(zs.length?'<ul class="tight">'+zs.map(function(z){var Z=W.zones[z];return '<li><a href="'+rel(Z.u)+'">'+esc(z)+'</a>'+(Z.dg?' (dungeon)':'')+' <span class="dim">lvl '+Z.lo+'–'+Z.hi+(Z.est?' (from mob levels)':'')+(Z.hi-Z.lo>=30?', wide range: check the camps below':'')+' · '+(dz(z)===0?'your start city':dz(z)+' zone hop'+(dz(z)>1?'s':'')+' away on the wiki connections')+'</span></li>'}).join('')+'</ul><p class="dim">Nearest zones whose wiki level range overlaps '+lo+'–'+hi+'. Move on when the next range’s zones start to overlap your level.</p>':'<p>'+badge('unverified')+' No zone with a wiki level range for '+lo+'–'+hi+' is connected to '+esc(city)+' in the zone data yet.</p>'));
    var camps=[];zs.forEach(function(z){W.zones[z].camps.forEach(function(m){var n=(String(m[1]).match(/\d+/g)||[]).map(Number);if(n.length&&n[0]<=hi&&n[n.length-1]>=lo)camps.push('<li><b class="tt-mob">'+esc(m[0])+'</b> (lvl '+esc(m[1])+') · <a href="'+rel(W.zones[z].u)+'">'+esc(z)+'</a>'+(m[2]?' <span class="dim">loot: '+esc(m[2])+'</span>':'')+'</li>')})});
    o.push('<h3>Named camps '+badge('fact')+'</h3>'+(camps.length?'<ul class="tight">'+camps.slice(0,8).join('')+'</ul>':'<p class="dim">No named mobs with a wiki level in this range in those zones.</p>'));
    var qs=W.quests.filter(function(q){return zs.indexOf(q[2])>=0&&q[3]!=null&&q[3]>=lo&&q[3]<=hi&&qFor(q)});
    o.push('<h3>Quests '+badge('fact')+'</h3>'+(qs.length?'<ul class="tight">'+qs.slice(0,10).map(function(q){return '<li><a class="ext" target="_blank" rel="noopener" href="'+esc(q[1])+'">'+esc(q[0])+'</a> <span class="dim">'+esc(q[2])+' · min lvl '+q[3]+(q[5]?' · '+esc(q[5]):'')+'</span></li>'}).join('')+'</ul>':'<p class="dim">No quests with a wiki minimum level in '+lo+'–'+hi+' in those zones for '+esc(c)+'.</p>'));
    var sp=(W.spells[c]||[]).filter(function(s){return s[1]>=lo&&s[1]<=hi});
    o.push('<h3>Spells and abilities to buy or train '+badge('fact')+'</h3>'+(sp.length?'<ul class="tight cg-sp">'+sp.map(function(s){return '<li>L'+s[1]+' <b>'+esc(s[0])+'</b> <span class="dim">'+esc(s[2])+'</span></li>'}).join('')+'</ul><p class="dim">Buy each one when you reach its level'+(tr.length?' (trainer: '+esc(tr[0].npc)+')':'')+'. "Vendor" spells come from your class vendor; others from the listed source.</p>':'<p class="dim">No '+esc(c)+' spells with a wiki level in this range.</p>'));
    var g=(W.gear[c]||[]).map(function(i){return W.items[i]}).filter(function(it){return it[3]>=lo&&it[3]<=hi});
    g.sort(function(a,b){var da=Math.min.apply(null,a[5].map(dz).concat([99])),db=Math.min.apply(null,b[5].map(dz).concat([99]));return da-db||b[6]-a[6]||b[3]-a[3]});
    var seen={},gp=[];g.forEach(function(it){var s=it[2].split(',')[0];if(seen[s]||gp.length>=8)return;seen[s]=1;var d=Math.min.apply(null,it[5].map(dz).concat([99]));
      gp.push('<li>'+esc(it[2])+': <a class="ext" target="_blank" rel="noopener" href="'+esc(it[1])+'">'+esc(it[0])+'</a> <span class="dim">lvl '+it[3]+' · '+esc(it[4])+(it[5].length?' · '+esc(it[5].join(', '))+(d<99?' ('+(d===0?'start city':d+' away')+')':''):'')+'</span></li>')});
    o.push('<h3>Gear upgrades '+badge('fact')+'</h3>'+(gp.length?'<ul class="tight">'+gp.join('')+'</ul><p class="dim">One wiki item per slot, nearest to '+esc(city)+' first. Full list: <a href="'+rel(W.gearurl[c])+'">'+esc(c)+' gear by level</a>.</p>':'<p class="dim">No '+esc(c)+' items with a wiki level in this range.</p>'));
    var rep=[],warn=[];zs.forEach(function(z){var Z=W.zones[z];Z.fr.forEach(function(f){if(f[1].length)rep.push('<li><b>'+esc(f[0])+'</b>: kill '+f[1].map(esc).join(', ')+' in '+esc(z)+'</li>')});
      Z.fl.forEach(function(f){if(C.home.indexOf(f[0])>=0)warn.push('<li>'+badge('fact')+' '+(f[1].length?'Killing '+f[1].map(esc).join(', '):'Activity')+' in '+esc(z)+' <b>lowers '+esc(f[0])+'</b> (your home-city faction).</li>')})});
    o.push('<h3>Rep and faction '+badge('fact')+'</h3>'+(warn.length?'<ul class="tight cg-warn">'+warn.join('')+'</ul>':'')+(rep.length?'<ul class="tight">'+rep.slice(0,6).join('')+'</ul>':'<p class="dim">No faction gains listed on the wiki for mobs in these zones.</p>')+'<p class="dim">From the wiki faction pages (<a href="'+rel('/faction-guide.html')+'">faction guide</a>).</p>');
    if(opt)opt.bands[B[0]]={lo:lo,hi:hi,label:B[1],zs:zs,camps:camps,qs:qs,html:o.join('')};
    h.push('<details id="wt-b-'+B[0]+'" class="cg-band'+(cur?' cg-cur':'')+'"'+(cur||location.hash==='#wt-b-'+B[0]?' open':'')+'><summary><b>Levels '+esc(B[1])+'</b>'+(cur?' <span class="dim">(your level range)</span>':'')+'</summary>'+o.join('')+'</details>');
  });
  var nh=W.nh[c];
  if(nh) h.push('<h2 id="wt-nh">Starting near Night Harbor</h2><p>'+badge('fact')+' '+esc(nh.summary)+'</p><ul>'+nh.cities.map(function(x){return '<li><b>'+esc(x.city)+'</b>: '+esc(x.distance)+' <i>'+esc(x.inq)+'</i></li>'}).join('')+'</ul><p>'+badge('strategy')+' '+esc(nh.best)+'</p><p class="dim">'+badge('unverified')+' '+esc(nh.caveat)+'</p>');
  if(opt){opt.C=C;opt.st=st;opt.tr=tr;opt.sq=sq;opt.s1=s1;opt.dz=dz;}
  return h.join('');}
// ---- UX pass 3: the start-city route (per band) and city overview are split per city and loaded when a band is shown
// (walk-r-<band>-<city>.js / walk-h-<city>.js, map in W.lazy). Unsplit data (no W.lazy) renders exactly as before.
function rtData(kind,k,city){var L=W.lazy,sl=scslug(city);
  if(!L)return kind==='h'?(W.schead||''):((W.route||{})[k]||'');
  if(kind==='h'){var hs=L.schead||{};if(!Object.keys(hs).length)return '';if(!hs[sl])return '<div></div>';var v=(W.schead_c||{})[sl];return v==null?null:v}
  var b=(L.route||{})[k];if(!b)return '';if(!b[sl])return '<div></div>';var r=(W.route||{})[k+'|'+sl];return r==null?null:r}
function rtFile(kind,k,city){var L=W.lazy||{},sl=scslug(city);return kind==='h'?(L.schead||{})[sl]:((L.route||{})[k]||{})[sl]}
function rtHTML(kind,k,city){var d=rtData(kind,k,city);if(d!==null)return scFor(d,city);
  return '<div class="wt-slot" data-kind="'+kind+'" data-k="'+esc(k)+'" data-city="'+esc(city)+'"><p class="lz-status" role="status" aria-busy="true">Loading the '+esc(city)+' start-city '+(kind==='h'?'overview':'route for levels '+esc(k.replace('-','\u2013')))+'…</p></div>'}
function fillSlots(box){if(!box||!W||!W.lazy)return;box.querySelectorAll('.wt-slot').forEach(function(sl){
  if(sl.getAttribute('data-busy')||sl.closest('details:not([open]),[hidden]'))return;
  var kind=sl.getAttribute('data-kind'),k=sl.getAttribute('data-k'),c=sl.getAttribute('data-city'),f=rtFile(kind,k,c);
  var done=function(){if(!sl.isConnected)return;var h=rtHTML(kind,k,c);if(/wt-slot/.test(h)){fail();return}var t=document.createElement('div');t.innerHTML=h;sl.replaceWith.apply(sl,[].slice.call(t.childNodes))};
  var fail=function(){if(!sl.isConnected)return;sl.removeAttribute('data-busy');sl.innerHTML='<p class="lz-status lz-err" role="alert">'+badge('unverified')+' The '+esc(c)+' start-city '+(kind==='h'?'overview':'route for levels '+esc(k.replace('-','\u2013')))+' did not load (offline?). <button type="button" class="wt-retry">Try again</button></p>'};
  if(!f||!window.MNM_LOAD){fail();return}
  sl.setAttribute('data-busy','1');MNM_LOAD(f).then(done,fail)})}
document.addEventListener('toggle',function(e){var d=e.target;if(d&&d.tagName==='DETAILS'&&d.open)fillSlots(d)},true);
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.wt-retry');if(!b)return;var sl=b.closest('.wt-slot');if(!sl)return;
  sl.removeAttribute('data-busy');sl.innerHTML='<p class="lz-status" role="status" aria-busy="true">Loading…</p>';fillSlots(sl.parentNode)});
function walk(){if(!mount)return;if(!W){if(wtFail)mount.innerHTML='<p class="lz-status lz-err">'+badge('unverified')+' Walkthrough data did not load (offline?). Reload to retry.</p>';return}mount.innerHTML=walkHTML(cls(),race,city,band());fillSlots(mount);}
// ---- class pages: Quick info walkthrough summary for the selected band (reuses walkHTML; never falls back to another city's route)
function setBand(k){if(selL){selL.value=k;selL.dispatchEvent(new Event('change'))}else{put('mnm-range',k);apply()}}
function qwalk(el){var c=el.getAttribute('data-class'),k=band(),notes=[],r=race,t=city;
  if(!W){if(wtFail)el.innerHTML='<p class="lz-status lz-err">'+badge('unverified')+' Walkthrough data did not load (offline?): no sourced data shown. Reload to retry.</p>';return}
  if(!(G.combos[c]||{})[r]){var d=defRace(c);notes.push(badge('unverified')+' Your Race pick ('+esc(r||'none')+') cannot be a '+esc(c)+' on the wiki start-city table, so this shows '+esc(d)+'. Pick a race under <a href="#best-races">Best races for '+esc(c)+'</a>.');r=d}
  var cs=cities(c,r);if(cs.indexOf(t)<0){notes.push(badge('unverified')+' '+esc(t||'Your start')+' is not a valid start for a '+esc(r)+' '+esc(c)+', so this shows '+esc(cs[0]||'no start')+'.');t=cs[0]||''}
  var opt={bands:{}},full=walkHTML(c,r,t,k,opt),B=opt.bands[k],idx=W.bands.map(function(x){return x[0]}).indexOf(k),nx=W.bands[idx+1];
  var fp=rel('/walkthrough.html')+'?class='+encodeURIComponent(c)+'&race='+encodeURIComponent(r)+'&city='+encodeURIComponent(t);
  var h=['<div class="qw-head"><h3>New character: '+esc(r)+' '+esc(c)+' · '+esc(t||'?')+' · levels '+esc(B?B.label:k.replace('-','\u2013'))+'</h3>'+
    '<p class="dim">Follows Race, Start and Levels in the top bar. <a class="qw-full" href="'+fp+'#wt-b-'+esc(k)+'">Open full page</a></p></div>'];
  notes.forEach(function(n){h.push('<p class="qw-note">'+n+'</p>')});
  if(!opt.C||!B){h.push(full||'<p>'+badge('unverified')+' No sourced data yet for this band.</p>');el.innerHTML=h.join('');return}
  var qr=rtHTML('r',k,t);if(qr)h.push('<div class="qw-route">'+qr+'</div>');
  var lo=B.lo,hi=B.hi,dz=opt.dz,starter=lo<=10&&B.zs.length&&dz(B.zs[0])===0,li=[];
  if(starter){
    h.push('<p class="qw-tag">'+badge('strategy')+' Starter area: '+esc(t)+'</p>');
    var steps=opt.st.length?opt.st.filter(function(s){return s.lvl==null||(s.lvl>=lo&&s.lvl<=hi)}).map(function(s){var x=String(s.text);return '<li>'+badge(s.label)+' '+esc(x.length>170?x.slice(0,x.lastIndexOf(' ',165))+'…':x)+'</li>'}):(lo===1?opt.s1:[]);
    if(steps.length)h.push('<b>First steps from spawn</b><ol class="tight qw-steps">'+steps.slice(0,4).join('')+'</ol>');
    li.push('<li>'+(opt.tr.length?badge('fact')+' Trainer: '+opt.tr.map(function(x){return '<b>'+esc(x.npc)+'</b>'+(x.where?' ('+esc(x.where)+')':'')}).join(', '):badge('unverified')+' Trainer in '+esc(t)+': no sourced data yet')+'</li>');
    li.push(opt.sq.length?'<li>'+badge('fact')+' Starter / class quests: '+opt.sq.map(function(q){return '<a class="ext" target="_blank" rel="noopener" href="'+esc(q[1])+'">'+esc(q[0])+'</a>'}).join(', ')+'</li>':'<li>'+badge('unverified')+' Starter / class quest for '+esc(c)+' in '+esc(t)+': no sourced data yet</li>');
    B.qs.filter(function(q){return !opt.sq.some(function(x){return x[0]===q[0]})}).slice(0,3).forEach(function(q){li.push('<li>'+badge('fact')+' Quest: <a class="ext" target="_blank" rel="noopener" href="'+esc(q[1])+'">'+esc(q[0])+'</a> <span class="dim">'+esc(q[2])+' · min lvl '+q[3]+'</span></li>')});
    h.push('<b>Key quests and trainer</b><ul class="tight">'+li.join('')+'</ul>');
  }else{
    var pv=W.bands[idx-1]&&opt.bands[W.bands[idx-1][0]];
    h.push('<p class="qw-tag">'+badge('strategy')+' Beyond the starter area'+(pv&&pv.zs.length?', continuing from '+esc(pv.zs[0]):'')+'</p>');
    h.push('<b>Where to go</b>'+(B.zs.length?'<ul class="tight">'+B.zs.slice(0,3).map(function(z){var Z=W.zones[z];return '<li><a href="'+rel(Z.u)+'">'+esc(z)+'</a> <span class="dim">lvl '+Z.lo+'\u2013'+Z.hi+' · '+(dz(z)===0?'your start city':dz(z)+' hop'+(dz(z)>1?'s':'')+' from '+esc(t))+'</span></li>'}).join('')+'</ul>':'<p>'+badge('unverified')+' No sourced data yet: no zone with a wiki level range for '+lo+'\u2013'+hi+' is connected to '+esc(t)+'.</p>'));
  }
  h.push('<b>Camps</b>'+(B.camps.length?'<ul class="tight">'+B.camps.slice(0,4).join('')+'</ul>':'<p class="dim">No sourced named camps for '+lo+'\u2013'+hi+' near '+esc(t)+' yet.</p>'));
  var nb=nx&&opt.bands[nx[0]];
  h.push('<p class="qw-next"><b>Next up:</b> '+(nx?'<button type="button" class="qw-band" data-band="'+esc(nx[0])+'">Levels '+esc(nx[1])+'</button> '+(nb&&nb.zs.length?'→ '+esc(nb.zs[0]):'<span class="dim">no sourced zone yet</span>'):'this is the last level range')+'</p>');
  var open=el.getAttribute('data-open')==='1';
  h.push('<button type="button" class="qw-toggle" aria-expanded="'+open+'">'+(open?'Hide full walkthrough':'Show full walkthrough')+'</button>');
  h.push('<div class="qw-more"'+(open?'':' hidden')+'>'+(open?B.html+'<p class="qw-bands"><b>Other level ranges:</b> '+W.bands.map(function(x){return x[0]===k?'<b>'+esc(x[1])+'</b>':'<button type="button" class="qw-band" data-band="'+esc(x[0])+'">'+esc(x[1])+'</button>'}).join(' ')+'</p>':'')+'</div>');
  el.innerHTML=h.join('');fillSlots(el);}
function qwalkAll(){document.querySelectorAll('.cg-qwalk').forEach(qwalk)}
document.addEventListener('click',function(e){var t=e.target.closest&&e.target.closest('.qw-toggle,.qw-band,.rr-use');if(!t)return;
  if(t.classList.contains('qw-toggle')){var el=t.closest('.cg-qwalk');el.setAttribute('data-open',el.getAttribute('data-open')==='1'?'0':'1');qwalk(el);return}
  if(t.classList.contains('qw-band')){setBand(t.getAttribute('data-band'));return}
  // ranking row: set Class (to this page's class) + Race, keep Start valid
  var c=t.getAttribute('data-class'),r=t.getAttribute('data-race');if(!G.combos[c]||!G.combos[c][r])return;
  if(selC&&selC.value!==c){selC.value=c;put('mnm-class',c);selC.dispatchEvent(new Event('change'))}else put('mnm-class',c);
  race=r;city=null;pick();fill();changed(true);
  var m=t.closest('.rr');if(m){var s=m.querySelector('.rr-msg');if(!s){s=document.createElement('p');s.className='rr-msg dim';s.setAttribute('aria-live','polite');m.insertBefore(s,m.children[1])}s.textContent='Race set to '+r+' (Start: '+city+'). The rest of this page now follows that pick.'}});
// open the tab that holds a #hash target (e.g. #best-races on class guides)
function hashTab(){var id=location.hash.slice(1);if(!id)return;var el=document.getElementById(id);if(!el)return;var p=el.closest('.tabpane');
  if(p&&!p.classList.contains('on')){var b=document.querySelector('.tab[data-tab="'+p.id+'"]');if(b){b.click();setTimeout(function(){el.scrollIntoView()},0)}}}
window.addEventListener('hashchange',hashTab);document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="#"]');if(a)setTimeout(hashTab,0)});hashTab();
function apply(){tailor();walk();qwalkAll();}
apply();
document.addEventListener('mnm:quick',function(){tailor();qwalkAll();});
// UX pass 2: walk-data.js (~560 KB) is loaded async by the shared loader on pages that show a walkthrough, then rendered
// UX pass 5: on class pages (no #cg-walk) it loads only once a Quick info walkthrough box is actually on screen (its tab open
// and scrolled into view, or printing); the walkthrough page itself still loads it straight away.
if(!W&&(mount||document.querySelector('.cg-qwalk'))){var qws=[].slice.call(document.querySelectorAll('.cg-qwalk')),wtGo=0;
 var wtMsg=function(t,busy){[mount].concat(qws).forEach(function(el){if(el){var p=el.querySelector('p');if(p){p.classList.add('lz-status');p.setAttribute('role','status');if(busy)p.setAttribute('aria-busy','true');p.textContent=t}}})};
 var wtLoad=function(){if(wtGo)return;wtGo=1;wtMsg('Loading the new-character walkthrough…',1);
  if(window.MNM_LOAD)MNM_LOAD('walk-data.js').then(function(){W=window.MNM_WT;apply()},function(){wtFail=1;apply()});else{wtFail=1;apply()}};
 if(mount||!window.IntersectionObserver)wtLoad();
 else{wtMsg('The new-character walkthrough loads when you scroll to it.');
  var wtIO=new IntersectionObserver(function(es){if(es.some(function(e){return e.isIntersecting})){wtIO.disconnect();wtLoad()}},{rootMargin:'0px'});
  qws.forEach(function(el){wtIO.observe(el)});window.addEventListener('beforeprint',wtLoad);window.MNM_WT_LOAD=wtLoad}}
})();
