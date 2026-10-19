(function(){var D=window.MNM_MOBS||[],U=window.MNM_IURL||{},root=document.documentElement.getAttribute('data-root')||'';
var q=document.getElementById('mob-q'),nm=document.getElementById('mob-named'),ml=document.getElementById('mob-lvl'),md=document.getElementById('mob-drop'),out=document.getElementById('mob-out'),cnt=document.getElementById('mob-count');if(!out)return;
function e(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function il(n){return window.MNM_ITEMPAGE?'<a href="'+root+'items.html#'+encodeURIComponent(n)+'">'+e(n)+'</a>':'<a class="ext" target="_blank" rel="noopener" href="'+e(U[n]||'#')+'">'+e(n)+'</a>'}
function go(){var t=q.value.trim().toLowerCase(),r=(document.getElementById('mnm-range')||{}).value||'1-60',b=r.split('-').map(Number),res=[],n=0;
 for(var i=0;i<D.length;i++){var d=D[i];if(nm.checked&&!d[5])continue;if(ml.checked&&!(d[1]&&d[1]>=b[0]&&d[1]<=b[1]))continue;if(md.checked&&!d[8].length&&!(d[10]&&d[10].m))continue;
  if(t&&(d[0]+' '+d[3]+' '+d[6]+' '+d[7]+' '+d[8].join(' ')+' '+d[9].join(' ')+' '+((d[10]||{}).m||[]).map(function(m){return m[0]}).join(' ')).toLowerCase().indexOf(t)<0)continue;n++;if(res.length<200)res.push(d);}
 cnt.textContent=n+' mobs'+(n>200?' (showing first 200)':'');
 out.innerHTML='<div class="tw"><table class="grid"><thead><tr><th>Mob</th><th>Lvl</th><th>Zone</th><th>Drops</th></tr></thead><tbody>'+res.map(function(d){
  var x=d[10]||{},M='<a class="ext" target="_blank" rel="noopener" href="https://mnm-db.com/">mnm-db</a>';
  return '<tr><td>'+(d[5]?'<b>'+e(d[0])+'</b> <span class="tag">named</span>':e(d[0]))+(x.q?' <span class="tag">quest NPC</span>':'')+(x.s?' <span class="tag">'+M+' only</span>':'')+(x.p?' <a class="ext dim" target="_blank" rel="noopener" href="'+e(x.p)+'" title="Wiki mob page">wiki</a>':'')+(d[6]?'<br><span class="dim">'+e(d[6])+'</span>':'')+
  (x.c?'<br><span class="tag conf" title="'+e(x.c.join('\n'))+'">sources differ</span> <span class="dim">'+e(x.c.join('; '))+'</span>':'')+'</td><td>'+e(d[2]||'?')+(x.e?'<br><span class="dim">'+M+': '+e(x.e)+'</span>':'')+'</td><td><a href="'+root+d[4]+'">'+e(d[3])+'</a>'+(d[7]?'<br><span class="dim">'+e(d[7])+'</span>':'')+'</td><td>'+
  (d[8].map(il).concat(d[9].map(e)).join(', ')||'<span class="dim">none recorded</span>')+(x.m?'<br><span class="dim">Seen ('+M+', drops/corpses): '+x.m.map(function(m){return (window.MNM_ITEMPAGE?il(m[0]):e(m[0]))+' '+e(m[1])}).join(', ')+'</span>':'')+'</td></tr>'}).join('')+'</tbody></table></div>';}
[q,nm,ml,md].forEach(function(x){x.addEventListener('input',go);x.addEventListener('change',go)});var s=document.getElementById('mnm-range');if(s)s.addEventListener('change',function(){setTimeout(go,0)});
var h=decodeURIComponent(location.hash.slice(1));if(h)q.value=h;go();})();
