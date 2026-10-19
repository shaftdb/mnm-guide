(function(){var G=window.MNM_GB,root=document.documentElement.getAttribute('data-root')||'';if(!G)return;
var KEY='mnm-groupbuilder',slots=document.getElementById('gb-slots'),out=document.getElementById('gb-out'),recs=document.getElementById('gb-recs');
var names=Object.keys(G.classes).sort(),N=4,W={tank:3,heal:3,dps:1.5,cc:3,pull:2,buffs:1.5,self:1,sustain:2.5,rez:1.5};
function e(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var st={c:['','','',''],r:['','','','']};
function slug(s){return s.replace(/ /g,'_')}function unslug(s){return decodeURIComponent(s||'').replace(/_/g,' ')}
function fromHash(){var h=location.hash.replace(/^#/,'');if(!/(^|&)g=/.test(h))return false;var p={};h.split('&').forEach(function(kv){var i=kv.indexOf('=');if(i>0)p[kv.slice(0,i)]=kv.slice(i+1)});
 var c=(p.g||'').split('~').map(unslug),r=(p.r||'').split('~').map(unslug);for(var i=0;i<N;i++){st.c[i]=G.classes[c[i]]?c[i]:'';st.r[i]=st.c[i]&&G.classes[c[i]].races.indexOf(r[i])>=0?r[i]:''}return true}
function toHash(){var c=st.c.map(slug).join('~').replace(/~+$/,''),r=st.r.map(slug).join('~').replace(/~+$/,'');return c?'g='+c+(r?'&r='+r:''):''}
function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(x){}var h=toHash();history.replaceState(null,'',location.pathname+location.search+(h?'#'+h:''))}
if(!fromHash()){try{var s=JSON.parse(localStorage.getItem(KEY)||'null');if(s&&s.c)st=s}catch(x){}}
var labels=['Slot 1','Slot 2','Slot 3','Optional 4th'];
function raceOpts(i){var c=st.c[i];if(!c)return '<option value="">(pick a class)</option>';return '<option value="">Any race</option>'+G.classes[c].races.map(function(r){return '<option'+(r===st.r[i]?' selected':'')+' value="'+e(r)+'">'+e(r)+(G.large.indexOf(r)>=0?' (large race, not recommended)':'')+'</option>'}).join('')}
function drawSlots(){slots.innerHTML=labels.map(function(l,i){return '<div class="gb-slot"><label for="gbc'+i+'">'+l+' class</label><select id="gbc'+i+'" data-i="'+i+'" data-k="c"><option value="">—</option>'+names.map(function(n){return '<option'+(n===st.c[i]?' selected':'')+'>'+e(n)+'</option>'}).join('')+'</select><label for="gbr'+i+'">Race</label><select id="gbr'+i+'" data-i="'+i+'" data-k="r">'+raceOpts(i)+'</select></div>'}).join('')}
slots.addEventListener('change',function(ev){var t=ev.target,i=+t.getAttribute('data-i'),k=t.getAttribute('data-k');st[k][i]=t.value;if(k==='c'){st.r[i]='';drawSlots()}go()});
document.getElementById('gb-clear').onclick=function(){st={c:['','','',''],r:['','','','']};drawSlots();go()};
recs.innerHTML=G.recs.map(function(R,j){return '<div class="gb-rec"><h3>'+e(R.name)+'</h3><p>'+R.cls.map(function(c,i){return e(R.races[i]+' '+c)}).join(' · ')+'<br><span class="dim">Best 4th: '+e(R.fourth_race+' '+R.fourth)+'</span></p><p>'+e(R.why)+' <span class="badge strat">strategy</span></p><button type="button" data-j="'+j+'">Load in builder</button></div>'}).join('');
recs.addEventListener('click',function(ev){var b=ev.target.closest('button');if(!b)return;var R=G.recs[+b.getAttribute('data-j')];st={c:R.cls.concat([R.fourth]),r:R.races.concat([R.fourth_race])};drawSlots();go();document.getElementById('builder').scrollIntoView()});
function cov(list){var m={};G.caps.forEach(function(k){m[k[0]]=0});list.forEach(function(c){var S=G.classes[c].sc;for(var k in S)if(S[k]>m[k])m[k]=S[k]});return m}
function score(m){var t=0;for(var k in W)t+=W[k]*m[k];return t}
function moneyRating(list,m){var dps=0;list.forEach(function(c){dps+=G.classes[c].sc.dps});var r=(dps/list.length>=1.6?1:0)+(m.pull>=2?1:0)+(m.self>=2?1:0);return r>=3?2:r>=2?1:0}
function copy(txt,btn){function ok(){var o=btn.textContent;btn.textContent='Copied';setTimeout(function(){btn.textContent=o},1200)}
 if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(txt).then(ok,function(){prompt('Copy:',txt)});else{prompt('Copy:',txt)}}
function go(){save();var picked=st.c.filter(Boolean),trio=st.c.slice(0,3).filter(Boolean);
 if(!picked.length){out.innerHTML='<p class="dim">Pick a class to start. With 1 or 2 picks you get every possible completion ranked best to worst; click one to fill the slots. Picks are remembered in this browser and saved in the page link.</p>';return}
 var m=cov(picked),bars=['✗','◐','●'],html='';
 html+='<div class="gb-tools"><button type="button" id="gb-share">Copy share link</button><button type="button" id="gb-copy">Copy setup as text</button></div>';
 if(trio.length===1)html+=rankList(trio,2);else if(trio.length===2)html+=rankList(trio,1);
 if(picked.length<2){out.innerHTML=html;wire();return}
 html+='<h3>Coverage</h3><div class="tw"><table class="grid gb-cov"><thead><tr><th>Need</th><th>Score</th><th>Covered by (evidence)</th></tr></thead><tbody>'+G.caps.map(function(k){var who=picked.filter(function(c){return G.classes[c].sc[k[0]]>0}).sort(function(a,b){return G.classes[b].sc[k[0]]-G.classes[a].sc[k[0]]});
  return '<tr><td>'+e(k[1])+'</td><td><span class="gb-bar gb-s'+m[k[0]]+'">'+bars[m[k[0]]]+' '+m[k[0]]+'/2</span></td><td>'+(who.length?who.map(function(c){var ev=G.classes[c].ev[k[0]]||[];return '<b>'+e(c)+'</b> '+G.classes[c].sc[k[0]]+'/2'+(ev.length?'<div class="gb-ev">'+ev.slice(0,3).map(function(x){return x[2]==='w'?e(x[0])+' (W, L'+x[1]+')':'“'+e(x[0])+'” (O)'}).join('; ')+'</div>':(k[0]==='dps'?'<div class="gb-ev">official role: '+e(G.classes[c].roles)+' (O)</div>':''))}).join('<br>'):'<b class="gb-s0">gap</b>')+'</td></tr>'}).join('')+'</tbody></table></div>';
 var mr=moneyRating(picked,m);html+='<p>Money farming: <span class="gb-bar gb-s'+mr+'">'+bars[mr]+' '+mr+'/2</span> <span class="badge strat">strategy</span> <span class="dim">(kill speed + safe pulls + run speed and gate; no earn-rate data exists)</span></p>';
 var S=[],Wk=[],Gp=[];
 if(m.tank===2)S.push('Real tank');else if(m.tank===1){Wk.push('Only an off-tank or pet tank: pull singles');}else Gp.push('No tank');
 if(m.heal===2)S.push('Dedicated healer');else Gp.push(m.heal?'Only hybrid or self heals: rest more':'No heals');
 if(m.cc===2)S.push('Hard crowd control');else Wk.push('Little crowd control: adds are dangerous in dungeons');
 if(m.pull===2)S.push('Feign-death or dedicated puller');else Wk.push('No feign-death puller: pulls bring adds');
 if(m.sustain===2)S.push('Mana sustain (regen buff, cannibalize, or drains)');else Wk.push('No mana sustain found: expect med breaks');
 if(m.self===2)S.push('Self-sufficient: own food/water, gate/bind or run speed');else Wk.push('Buys food and water or walks a lot');
 if(!m.rez)Gp.push('No resurrect: plan corpse runs, /consent group');
 var nm=picked.filter(function(c){return G.classes[c].nomana}).length;if(nm)S.push(nm+' class(es) without mana: no med time for them (STRATEGY)');
 html+='<h3>Strengths</h3><ul class="tight">'+S.map(function(x){return '<li>'+e(x)+'</li>'}).join('')+'</ul><h3>Weaknesses</h3><ul class="tight">'+(Wk.length?Wk.map(function(x){return '<li>'+e(x)+'</li>'}).join(''):'<li>None flagged</li>')+'</ul><h3>Gaps</h3><ul class="tight">'+(Gp.length?Gp.map(function(x){return '<li class="gb-warn">'+e(x)+'</li>'}).join(''):'<li>None flagged</li>')+'</ul>';
 var rs=st.r.filter(function(r,i){return r&&st.c[i]});if(rs.length){var cities=null;rs.forEach(function(r){var cs=(G.start[r]||[]).map(function(x){return x.replace(/ \(some\)/,'')});cities=cities?cities.filter(function(x){return cs.indexOf(x)>=0}):cs});
  html+='<h3>Starting city</h3><p>'+(cities&&cities.length?'Shared start: '+e(cities.join(' or ')):'<span class="gb-warn">No shared starting city for these races; meet up after creation.</span>')+' <span class="dim">Race, faith and class decide the start; check the creation map</span> <span class="badge unc">unverified</span></p>';
  if(rs.some(function(r){return G.large.indexOf(r)>=0}))html+='<p class="gb-warn">Large race picked: not recommended for this plan.</p>'}
 if(trio.length===3)html+=rankList(trio,1,true);
 html+='<p class="dim">Class pages: '+picked.map(function(c){return '<a href="'+root+G.classes[c].page+'">'+e(c)+'</a> (<a class="ext" target="_blank" rel="noopener" href="'+e(G.classes[c].url)+'">official</a>)'}).join(', ')+'</p>';
 out.innerHTML=html;wire();}
function wire(){
 document.getElementById('gb-share').onclick=function(){copy(location.href,this)};
 document.getElementById('gb-copy').onclick=function(){copy(st.c.map(function(c,i){return c?(i===3?'4th: ':'')+(st.r[i]?st.r[i]+' ':'')+c:''}).filter(Boolean).join(' / ')+' — '+location.href,this)};}
/* ---- ranked completions (STRATEGY): every pair / third / 4th, best to worst ---- */
var RK=['tank','heal','dps','cc','pull','self'],CAPN={};G.caps.forEach(function(k){CAPN[k[0]]=k[1]});
function defRace(c){var R=G.classes[c].races.filter(function(r){return G.large.indexOf(r)<0});return R.indexOf('Human')>=0?'Human':(R[0]||'')}
function rankScore(list,fourth){var mm=cov(list),t=0,keys=fourth?Object.keys(W):RK;keys.forEach(function(k){t+=W[k]*mm[k]});t+=2*moneyRating(list,mm);return [Math.round(t*10)/10,mm]}
function ranked(base,k,fourth){var cand=names.filter(function(c){return base.indexOf(c)<0}),combos=[],bm=cov(base);
 if(k===1)cand.forEach(function(c){combos.push([c])});else for(var a=0;a<cand.length;a++)for(var b=a+1;b<cand.length;b++)combos.push([cand[a],cand[b]]);
 return combos.map(function(add){var full=base.concat(add),r=rankScore(full,fourth),mm=r[1],solo=add.some(function(c){return G.classes[c].solo});
  var sc=r[0]+(fourth&&solo?0.5:0),keys=RK.concat(['buffs','sustain','rez']);
  var gains=keys.filter(function(x){return mm[x]>bm[x]}).map(function(x){return CAPN[x]+(mm[x]<2?' (partial)':'')});
  var gaps=RK.filter(function(x){return mm[x]===0}).map(function(x){return 'no '+CAPN[x].toLowerCase()}).concat(RK.filter(function(x){return mm[x]===1}).map(function(x){return 'weak '+CAPN[x].toLowerCase()}));
  if(!mm.sustain)gaps.push('no mana sustain');if(!mm.rez)gaps.push('no resurrect');
  var depth=0,backs={};add.forEach(function(c){var S=G.classes[c].sc;for(var x in W){depth+=W[x]*S[x];if(S[x]===2&&bm[x]===2)backs[CAPN[x]]=1}});
  return {add:add,score:sc,tie:score(mm)*1000+depth,gains:gains,backs:Object.keys(backs),gaps:gaps,money:moneyRating(full,mm),solo:solo}})
 .sort(function(x,y){return y.score-x.score||y.tie-x.tie||x.add.join().localeCompare(y.add.join())})}
function rowHTML(R,i,fourth){var lbl=R.add.map(function(c){var r=defRace(c);return e((r?r+' ':'')+c)}).join(' + ');
 return '<li class="gb-row" data-add="'+e(R.add.join('|'))+'"><button type="button" class="gb-pick" aria-label="Fill with '+lbl+'"><span class="gb-rk">#'+(i+1)+'</span> <b>'+lbl+'</b> <span class="gb-sc">'+R.score+'</span></button>'+
  '<div class="gb-why">'+(R.gains.length?'Adds: '+e(R.gains.join(', ')):'Adds no new coverage')+(R.backs.length?' · backs up: '+e(R.backs.join(', ')):'')+' · money '+R.money+'/2'+(R.solo&&fourth?' · strong soloist, can catch up alone (O)':'')+'</div>'+
  '<div class="gb-gap">'+(R.gaps.length?'Gaps: '+e(R.gaps.join(', ')):'No gaps flagged')+'</div></li>'}
function rankList(base,k,fourth){var rs=ranked(base,k,fourth),top=5,what=fourth?'4th':(k===2?'pairs for the other two slots':'thirds');
 var h='<h3 id="gb-sugg">'+(fourth?'Every possible 4th, ranked':'Every possible '+(k===2?'pair':'third')+', ranked')+' <span class="badge strat">strategy</span></h3>'+
  '<p class="gb-ev">'+rs.length+' '+what+', best to worst. Score = weighted coverage of tank, heals, DPS, CC, pulling and self-sufficiency'+(fourth?', plus buffs, low downtime and resurrect':'')+', plus money rating; ties go to the option that backs up more roles (0–2 each, from keyword matches on wiki spells and official class pages, so abilities can be missed or mis-tagged) <span class="badge unc">unverified</span>. Races shown are defaults: Human where allowed, large races skipped. Click a row to fill the slot'+(k===2?'s':'')+'.</p>';
 h+='<ol class="gb-rank">'+rs.slice(0,top).map(function(R,i){return rowHTML(R,i,fourth)}).join('')+'</ol>';
 if(rs.length>top)h+='<details class="gb-more"><summary>Show all '+rs.length+'</summary><ol class="gb-rank" start="'+(top+1)+'">'+rs.slice(top).map(function(R,i){return rowHTML(R,i+top,fourth)}).join('')+'</ol></details>';
 return h}
out.addEventListener('click',function(ev){var li=ev.target.closest('.gb-row');if(!li||ev.target.closest('a'))return;var add=li.getAttribute('data-add').split('|');
 add.forEach(function(c){var lim=st.c.slice(0,3).filter(Boolean).length<3?3:4;for(var i=0;i<lim;i++){if(!st.c[i]){st.c[i]=c;st.r[i]=defRace(c);break}}});
 drawSlots();go();var t=document.getElementById('gb-sugg')||out;t.scrollIntoView({block:'start'})});
window.addEventListener('hashchange',function(){if(fromHash()){drawSlots();go()}});
drawSlots();go();})();
