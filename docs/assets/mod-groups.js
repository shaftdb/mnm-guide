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
 if(picked.length<2){out.innerHTML='<p class="dim">Pick at least 2 classes (3 for a trio). Your picks are remembered in this browser and saved in the page link.</p>';return}
 var m=cov(picked),bars=['✗','◐','●'],html='';
 html+='<div class="gb-tools"><button type="button" id="gb-share">Copy share link</button><button type="button" id="gb-copy">Copy setup as text</button></div>';
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
 if(trio.length===3){var base=score(cov(trio)),best=names.filter(function(c){return trio.indexOf(c)<0}).map(function(c){var mm=cov(trio.concat([c]));return [c,score(mm)-base+(G.classes[c].solo?0.5:0),mm]}).sort(function(a,b){return b[1]-a[1]}).slice(0,3);
  html+='<h3>Suggested 4th <span class="badge strat">strategy</span></h3><ol>'+best.map(function(b){var gain=G.caps.filter(function(k){return b[2][k[0]]>cov(trio)[k[0]]}).map(function(k){return k[1]});return '<li><b>'+e(b[0])+'</b>: adds '+e(gain.join(', ')||'depth')+(G.classes[b[0]].solo?' · strong soloist, so it can catch up alone (O)':'')+'</li>'}).join('')+'</ol>'}
 html+='<p class="dim">Class pages: '+picked.map(function(c){return '<a href="'+root+G.classes[c].page+'">'+e(c)+'</a> (<a class="ext" target="_blank" rel="noopener" href="'+e(G.classes[c].url)+'">official</a>)'}).join(', ')+'</p>';
 out.innerHTML=html;
 document.getElementById('gb-share').onclick=function(){copy(location.href,this)};
 document.getElementById('gb-copy').onclick=function(){copy(st.c.map(function(c,i){return c?(i===3?'4th: ':'')+(st.r[i]?st.r[i]+' ':'')+c:''}).filter(Boolean).join(' / ')+' — '+location.href,this)};}
window.addEventListener('hashchange',function(){if(fromHash()){drawSlots();go()}});
drawSlots();go();})();
