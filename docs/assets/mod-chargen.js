// Race + Starting City selectors (top bar; localStorage mnm-race / mnm-city; URL ?class=&race=&city=), character-creation tailoring, walkthrough renderer.
(function(){
var G=window.MNM_CG; if(!G) return;
var root=document.documentElement.getAttribute('data-root')||'';
var selC=document.getElementById('mnm-class'), selR=document.getElementById('mnm-race'), selT=document.getElementById('mnm-city'), selL=document.getElementById('mnm-range');
function get(k){try{return localStorage.getItem(k)}catch(e){return null}}
function put(k,v){try{localStorage.setItem(k,v)}catch(e){}}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function rel(u){return root+String(u).replace(/^\//,'')}
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
function fill(){var c=cls();
  if(selR) selR.innerHTML=races(c).map(function(r){var lg=G.large.indexOf(r)>=0;return '<option value="'+esc(r)+'"'+(r===race?' selected':'')+(lg?' title="Large race: a valid option, but this Codex never defaults to or recommends it"':'')+'>'+esc(r)+(lg?' (large race)':'')+'</option>'}).join('')||'<option value="">(no wiki data)</option>';
  if(selT) selT.innerHTML=cities(c,race).map(function(t){return '<option'+(t===city?' selected':'')+'>'+esc(t)+'</option>'}).join('')||'<option value="">(no wiki data)</option>';}
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
var W=window.MNM_WT, mount=document.getElementById('cg-walk');
function band(){var v=(selL&&selL.value)||get('mnm-range')||'11-15';return v}
function bl(k){return k.split('-').map(Number)}
function badge(l){l=String(l||'unverified').toUpperCase();var c=l==='FACT'?'fact':l==='STRATEGY'?'strat':'unc';return '<span class="badge '+c+'">'+esc(l.toLowerCase())+'</span>'}
function walk(){if(!W||!mount)return;var c=cls(),code=W.codes[c],C=W.cities[city],R=W.races[race]||{},k=band(),b=bl(k);
  if(!C){mount.innerHTML='<p>'+badge('unverified')+' No wiki start-city data for '+esc(c)+' / '+esc(race)+'. Pick another race in the top bar.</p>';return;}
  var h=[];var dist=C.dist;
  function dz(z){return dist[z]==null?99:dist[z]}
  h.push('<div class="cg-head"><h2 style="margin-top:0">'+esc(race)+' '+esc(c)+' · starting in <a class="ext" target="_blank" rel="noopener" href="'+esc(C.u)+'">'+esc(city)+'</a></h2>'+
   '<p class="dim">'+badge('fact')+' Valid on the wiki start-city table'+((G.deities[c+'|'+race+'|'+city]||[]).length?' for deities: '+esc(G.deities[c+'|'+race+'|'+city].join(', ')):'')+'. Change class, race, start or levels in the top bar.'+
   (G.chargen[c]?' · <a href="'+rel(G.chargen[c])+'#chargen">'+esc(c)+' character creation</a>':'')+'</p></div>');
  // faction / race risks
  var risk=[];
  if(R.al) risk.push('<li>'+badge('fact')+' '+esc(race)+' faction alignment on the wiki: <b>'+esc(R.al)+'</b>.</li>');
  if(R.note) risk.push('<li>'+badge('fact')+' Race page note: '+esc(R.note)+'</li>');
  Object.keys(W.cities).forEach(function(t){if(W.cities[t].faq) risk.push('<li>'+badge('fact')+' <b>'+esc(t)+'</b> (official FAQ): '+esc(W.cities[t].faq)+'</li>')});
  if(R.al==='Evil') risk.push('<li>'+badge('unverified')+' How Night Harbor guards treat an evil race is not on the wiki yet: no sourced data yet. Travel carefully; the FAQ says factions "will begin to matter much more".</li>');
  if(C.home.length) risk.push('<li>'+badge('fact')+' Home-city factions on the wiki: '+C.home.map(esc).join(', ')+'. Their "lowered by" lists are flagged in each level range below.</li>');
  h.push('<details class="call" open><summary><b>Faction risks for this race and city</b></summary><ul class="tight">'+risk.join('')+'</ul></details>');
  // level 1 start
  var st=W.walk[c+'|'+city]||[];
  var tr=(C.tr||{})[c]||[];
  var s1=st.map(function(s){return '<li>'+badge(s.label)+' '+esc(s.text)+'</li>'});
  if(!st.length){
    s1.push('<li>'+(tr.length?badge('fact')+' Class trainer in '+esc(city)+': '+tr.map(function(t){return '<b>'+esc(t.npc)+'</b>'+(t.where?' ('+esc(t.where)+')':'')}).join(', '):badge('unverified')+' No '+esc(c)+' trainer listed on the wiki '+esc(city)+' page: no sourced data yet.')+'</li>');
    var sq=W.quests.filter(function(q){return q[2]===city&&(q[3]==null||q[3]<=2)&&(q[4]==='ALL'||q[4]==='ANY'||q[4].split(' ').indexOf(code)>=0)&&/starter|class/i.test(q[0])});
    s1.push(sq.length?'<li>'+badge('fact')+' Starter / class quests here: '+sq.map(function(q){return '<a class="ext" target="_blank" rel="noopener" href="'+esc(q[1])+'">'+esc(q[0])+'</a>'}).join(', ')+'. Step lists: <a href="'+rel('/quest-helper.html')+'">quest helper</a>.</li>':'<li>'+badge('unverified')+' No '+esc(c)+' starter quest for '+esc(city)+' in the wiki data: no sourced data yet.</li>');
  }
  h.push('<h2 id="wt-start">Level 1: first steps in '+esc(city)+'</h2><ol class="cg-steps">'+s1.join('')+'</ol>');
  // bands
  W.bands.forEach(function(B){var bb=bl(B[0]),lo=bb[0],hi=bb[1],cur=B[0]===k;
    var zs=Object.keys(W.zones).filter(function(z){var Z=W.zones[z];return Z.lo!=null&&Z.lo<=hi&&Z.hi>=lo&&dz(z)<99}).sort(function(a,b){return dz(a)-dz(b)||W.zones[a].lo-W.zones[b].lo}).slice(0,5);
    var o=[];
    o.push('<h3>Where to go '+badge('strategy')+'</h3>'+(zs.length?'<ul class="tight">'+zs.map(function(z){var Z=W.zones[z];return '<li><a href="'+rel(Z.u)+'">'+esc(z)+'</a>'+(Z.dg?' (dungeon)':'')+' <span class="dim">lvl '+Z.lo+'–'+Z.hi+(Z.est?' (from mob levels)':'')+(Z.hi-Z.lo>=30?', wide range: check the camps below':'')+' · '+(dz(z)===0?'your start city':dz(z)+' zone hop'+(dz(z)>1?'s':'')+' away on the wiki connections')+'</span></li>'}).join('')+'</ul><p class="dim">Nearest zones whose wiki level range overlaps '+lo+'–'+hi+'. Move on when the next range’s zones start to overlap your level.</p>':'<p>'+badge('unverified')+' No zone with a wiki level range for '+lo+'–'+hi+' is connected to '+esc(city)+' in the zone data yet.</p>'));
    var camps=[];zs.forEach(function(z){W.zones[z].camps.forEach(function(m){var n=(String(m[1]).match(/\d+/g)||[]).map(Number);if(n.length&&n[0]<=hi&&n[n.length-1]>=lo)camps.push('<li><b>'+esc(m[0])+'</b> (lvl '+esc(m[1])+') · <a href="'+rel(W.zones[z].u)+'">'+esc(z)+'</a>'+(m[2]?' <span class="dim">loot: '+esc(m[2])+'</span>':'')+'</li>')})});
    o.push('<h3>Named camps '+badge('fact')+'</h3>'+(camps.length?'<ul class="tight">'+camps.slice(0,8).join('')+'</ul>':'<p class="dim">No named mobs with a wiki level in this range in those zones.</p>'));
    var qs=W.quests.filter(function(q){return zs.indexOf(q[2])>=0&&q[3]!=null&&q[3]>=lo&&q[3]<=hi&&(q[4]==='ALL'||q[4]==='ANY'||q[4].split(' ').indexOf(code)>=0)});
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
    h.push('<details class="cg-band'+(cur?' cg-cur':'')+'"'+(cur?' open':'')+'><summary><b>Levels '+esc(B[1])+'</b>'+(cur?' <span class="dim">(your level range)</span>':'')+'</summary>'+o.join('')+'</details>');
  });
  var nh=W.nh[c];
  if(nh) h.push('<h2 id="wt-nh">Starting near Night Harbor</h2><p>'+badge('fact')+' '+esc(nh.summary)+'</p><ul>'+nh.cities.map(function(x){return '<li><b>'+esc(x.city)+'</b>: '+esc(x.distance)+' <i>'+esc(x.inq)+'</i></li>'}).join('')+'</ul><p>'+badge('strategy')+' '+esc(nh.best)+'</p><p class="dim">'+badge('unverified')+' '+esc(nh.caveat)+'</p>');
  mount.innerHTML=h.join('');}
function apply(){tailor();walk();}
apply();
})();
