(function(){var P=window.MNM_PLAN,root=document.documentElement.getAttribute('data-root')||'';if(!P)return;
var picks=document.getElementById('pl-picks'),band=document.getElementById('pl-band'),out=document.getElementById('pl-out'),sel=[];
function e(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var names=Object.keys(P.classes);
picks.innerHTML=names.map(function(c){return '<button type="button" class="pl-b" data-c="'+e(c)+'">'+e(c)+'</button>'}).join('');
band.innerHTML=P.bands.map(function(b){return '<option>'+b[0]+'</option>'}).join('');
try{var r=localStorage.getItem('mnm-range');if(r)band.value=r;var c0=localStorage.getItem('mnm-class');if(c0&&P.classes[c0])sel=[c0];}catch(x){}
picks.addEventListener('click',function(ev){var b=ev.target.closest('.pl-b');if(!b)return;var c=b.getAttribute('data-c'),i=sel.indexOf(c);
 if(i>=0)sel.splice(i,1);else if(sel.length<6)sel.push(c);go();});
document.getElementById('pl-clear').onclick=function(){sel=[];go()};band.onchange=go;
function go(){picks.querySelectorAll('.pl-b').forEach(function(b){b.classList.toggle('on',sel.indexOf(b.getAttribute('data-c'))>=0)});
 if(sel.length<2){out.innerHTML='<p class="dim">Pick at least 2 classes ('+sel.length+' picked).</p>';return;}
 var roles={},util={};sel.forEach(function(c){var C=P.classes[c];C.roles.forEach(function(r){(roles[r]=roles[r]||[]).push(c)});Object.keys(C.util).forEach(function(u){(util[u]=util[u]||[]).push([c,C.util[u]])})});
 var notes=[],lo=+band.value.split('-')[0];
 if(!roles.tank)notes.push('No dedicated tank: a pet class or hybrid has to hold aggro, so pull singles.');
 if(!roles.healer)notes.push('No healer: rest more between pulls and keep to even or lower con mobs.');
 if(!util['Slow'])notes.push('No slow found in the spell lists: named and higher-con mobs hit harder.');
 if(!util['Mez / mesmerize']&&sel.length>=3)notes.push('No mez found: adds are dangerous, so pull carefully in dungeons.');
 if(sel.length===2&&roles.tank&&roles.healer)notes.push('Tank plus healer is the classic duo core.');
 if(sel.length===2&&roles.pet)notes.push('A pet acts as a third body for a duo.');
 if(!util['Resurrect'])notes.push('No resurrect found: plan for corpse runs.');
 var html='<h2>Roles <span class="badge strat">strategy</span></h2><ul class="tight">'+sel.map(function(c){return '<li><a href="'+root+P.classes[c].url+'">'+e(c)+'</a>: '+e(P.classes[c].role)+'</li>'}).join('')+'</ul>';
 html+='<h2>Verdict <span class="badge strat">strategy</span></h2><ul class="tight">'+(notes.length?notes.map(function(n){return '<li>'+e(n)+'</li>'}).join(''):'<li>Covers tank, heals, slow and crowd control.</li>')+'</ul>';
 html+='<h2>Utility <span class="badge fact">fact</span></h2><div class="tw"><table class="grid"><thead><tr><th>Utility</th><th>Who (first match, lvl)</th></tr></thead><tbody>'+P.utils.map(function(u){var w=util[u];
  return '<tr class="'+(w?'':'pl-miss')+'"><td>'+e(u)+'</td><td>'+(w?w.map(function(x){return e(x[0])+': '+e(x[1][0])+' (L'+x[1][1]+')'+(x[1][1]>lo+5?' <span class="dim">later</span>':'')}).join('<br>'):'<b>missing</b>')+'</td></tr>'}).join('')+'</tbody></table></div>';
 var B=P.bands.filter(function(b){return b[0]===band.value})[0];
 html+='<h2>Zones for '+e(band.value)+' <span class="badge fact">fact</span></h2><p class="dim">Zones whose wiki mob tables have camps in this range, most camps first.'+(sel.length>=3?' Dungeons are marked; they suit groups of 3 or more <span class="badge strat">strategy</span>.':'')+'</p><ul class="tight">'+(B&&B[1].length?B[1].map(function(z){return '<li><a href="'+root+z[1]+'">'+e(z[0])+'</a> <span class="dim">(zone lvl '+e(z[2])+', '+z[3]+' camps)'+(z[4]?' · dungeon':'')+'</span></li>'}).join(''):'<li class="dim">No wiki camps in this range.</li>')+'</ul>';
 out.innerHTML=html;}
go();})();
