(function(){var D=window.MNM_IDB||[],root=document.documentElement.getAttribute('data-root')||'';
var q=document.getElementById('idb-q'),sl=document.getElementById('idb-slot'),mc=document.getElementById('idb-cls'),ml=document.getElementById('idb-lvl'),sr=document.getElementById('idb-src'),out=document.getElementById('idb-out'),cnt=document.getElementById('idb-count');
if(!out)return;
var MK=window.MNM_MKTI||{};var K={n:'Named',d:'Drop',q:'Quest',v:'Vendor',c:'Crafted'};
function e(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function sel(){var R=window.MNM_RANGES||{},c=document.getElementById('mnm-class'),r=document.getElementById('mnm-range');return{code:(R.codes||{})[c&&c.value],b:(r&&r.value||'1-60').split('-').map(Number)}}
function go(){var t=q.value.trim().toLowerCase(),s=sl.value,S=sel(),src=sr.value,res=[],n=0;
 for(var i=0;i<D.length;i++){var d=D[i];
  if(s&&(' '+d[2]+' ').indexOf(' '+s+' ')<0)continue;
  if(mc.checked&&S.code&&(' '+d[3]+' ').indexOf(' '+S.code+' ')<0)continue;
  if(ml.checked&&!(d[4]&&d[4]>=S.b[0]&&d[4]<=S.b[1]))continue;
  if(src&&!d[6].some(function(x){return x[0]===src}))continue;
  if(t&&(d[0]+' '+d[2]+' '+d[5]+' '+d[6].map(function(x){return x.join(' ')}).join(' ')).toLowerCase().indexOf(t)<0)continue;
  n++;if(res.length<150)res.push(d);}
 cnt.textContent=n+' items'+(n>150?' (showing first 150, narrow the search)':'');
 out.innerHTML=res.map(function(d){var srcs=d[6].length?d[6].filter(function(x){return !x[6]}).slice(0,6).concat(d[6].filter(function(x){return x[6]}).slice(0,3)).map(function(x){var z=x[3]?(x[4]?' — <a href="'+root+x[4]+'">'+e(x[3])+'</a>':' — '+e(x[3])):'';
   return '<li><span class="tag">'+K[x[0]]+'</span>'+(x[6]?' <a class="tag ext" target="_blank" rel="noopener" href="https://mnm-db.com/">mnm-db</a>':'')+' '+e(x[1])+(x[2]?' (lvl '+e(x[2])+')':'')+z+(x[5]?', '+e(x[5]):'')+'</li>'}).join(''):'<li class="dim">No source on the wiki <span class="badge unc">unverified</span></li>';
  return '<div class="idb-it"><div><a class="ext" target="_blank" rel="noopener" href="'+e(d[1])+'"><b>'+e(d[0])+'</b></a> <span class="dim">'+e(d[2]||'no slot')+(d[4]?' · lvl '+d[4]:'')+'</span>'+(MK[d[0]]?' <a class="idb-mkt" href="'+root+'market.html#'+encodeURIComponent(d[0])+'" title="'+e(MK[d[0]][1]+', seen '+MK[d[0]][2])+'">💰 Market: '+e(MK[d[0]][0])+'</a>':'')+'</div>'+
   (d[7]&&d[7].c?'<div><span class="tag conf">sources differ</span> <span class="dim">'+e(d[7].c.join('; '))+' · <a href="'+root+'source-conflicts.html#item">all conflicts</a></span></div>':'')+(d[5]?'<div class="dim">'+e(d[5])+'</div>':'')+'<div class="dim">'+(d[3]?(d[3].split(' ').length>=18?'All classes':e(d[3])):'classes not listed')+'</div><ul class="tight">'+srcs+'</ul></div>'}).join('');}
[q,sl,mc,ml,sr].forEach(function(x){x.addEventListener('input',go);x.addEventListener('change',go)});
['mnm-class','mnm-range'].forEach(function(id){var x=document.getElementById(id);if(x)x.addEventListener('change',function(){setTimeout(go,0)})});
var h=decodeURIComponent(location.hash.slice(1));if(h)q.value=h;go();})();
