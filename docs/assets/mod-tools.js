(function(){function L(k,d){try{return JSON.parse(localStorage.getItem('mnm-tools-'+k))||d}catch(e){return d}}function S(k,v){try{localStorage.setItem('mnm-tools-'+k,JSON.stringify(v))}catch(e){}}
function e(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function $(i){return document.getElementById(i)}
// spell timer
var T=L('timers',[]);function dur(s){s=String(s).trim();var m=s.match(/^(\d+):(\d{1,2})$/);return m?(+m[1]*60+ +m[2]):(+s||0)}
function fmt(s){s=Math.max(0,Math.round(s));return Math.floor(s/60)+':'+('0'+s%60).slice(-2)}
function drawT(){var now=Date.now();$('tm-list').innerHTML=T.map(function(t,i){var left=(t.end-now)/1000;return '<li class="'+(left<=0?'tl-done':left<10?'tl-soon':'')+'"><b>'+e(t.n)+'</b> <span class="tl-left">'+(left<=0?'done':fmt(left))+'</span> <button type="button" data-r="'+i+'">↻</button> <button type="button" data-x="'+i+'">✕</button></li>'}).join('')||'<li class="dim">No timers.</li>';}
$('tm-add').onclick=function(){var d=dur($('tm-dur').value);if(!d)return;T.push({n:$('tm-name').value||'Timer',d:d,end:Date.now()+d*1000});S('timers',T);drawT();};
$('tm-list').onclick=function(ev){var r=ev.target.getAttribute('data-r'),x=ev.target.getAttribute('data-x');if(r!==null){T[r].end=Date.now()+T[r].d*1000}if(x!==null){T.splice(+x,1)}S('timers',T);drawT();};
setInterval(drawT,1000);drawT();
// xp/hr
var X=L('xp',{});['a','b','l','m'].forEach(function(k){if(X[k]!==undefined)$('xp-'+k).value=X[k];});
function xp(){var a=+$('xp-a').value,b=+$('xp-b').value,l=+$('xp-l').value||0,m=+$('xp-m').value;X={a:$('xp-a').value,b:$('xp-b').value,l:$('xp-l').value,m:$('xp-m').value,t0:X.t0};S('xp',X);
 if(!m||$('xp-a').value===''||$('xp-b').value===''){$('xp-out').textContent='Enter start %, now % and minutes.';return;}
 var gained=l*100+b-a,ph=gained/m*60;$('xp-out').innerHTML='Gained <b>'+gained.toFixed(1)+'%</b> of a level in '+m+' min = <b>'+ph.toFixed(1)+'% per hour</b>'+(ph>0?' · next level in about <b>'+fmt((100-b)/ph*3600).replace(/^(\d+):/,function(_,mm){return Math.floor(mm/60)+'h '+(mm%60)+'m '})+'</b>':'');}
['a','b','l','m'].forEach(function(k){$('xp-'+k).addEventListener('input',xp)});
$('xp-start').onclick=function(){X.t0=Date.now();if($('xp-b').value!=='')$('xp-a').value=$('xp-b').value;$('xp-l').value=0;xp();};
setInterval(function(){if(X.t0){$('xp-m').value=Math.max(1,Math.round((Date.now()-X.t0)/60000));xp();}},15000);if(X.t0)$('xp-m').value=Math.max(1,Math.round((Date.now()-X.t0)/60000));xp();
// notepad
var N=L('notes',[]);function drawN(){$('np-list').innerHTML=N.map(function(c,i){return '<div class="tl-note"><div><b>'+e(c.n)+'</b> <span class="dim">'+e(c.u||'')+'</span> <button type="button" data-d="'+i+'">Delete</button></div><textarea data-i="'+i+'" rows="3" aria-label="Notes for '+e(c.n)+'">'+e(c.t||'')+'</textarea></div>'}).join('')||'<p class="dim">No camps yet.</p>';}
$('np-add').onclick=function(){var n=$('np-camp').value.trim();if(!n)return;N.unshift({n:n,t:'',u:new Date().toLocaleString()});$('np-camp').value='';S('notes',N);drawN();};
$('np-list').addEventListener('input',function(ev){var i=ev.target.getAttribute('data-i');if(i!==null){N[i].t=ev.target.value;N[i].u=new Date().toLocaleString();S('notes',N);}});
$('np-list').addEventListener('click',function(ev){var d=ev.target.getAttribute('data-d');if(d!==null&&confirm('Delete notes for '+N[d].n+'?')){N.splice(+d,1);S('notes',N);drawN();}});drawN();})();
