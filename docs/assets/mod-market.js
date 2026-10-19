// Market page: searchable/sortable price table, vendor values per weight, money camps, start-city money notes (data: window.MNM_MKT)
(function(){var M=window.MNM_MKT;if(!M)return;var root=document.documentElement.getAttribute('data-root')||'';
function e(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function $(id){return document.getElementById(id)}
var SRC={};M.sources.forEach(function(s){SRC[s[0]]=s});
var CR={high:3,medium:2,low:1},LB={FACT:'<span class="badge fact">fact</span>',UNVERIFIED:'<span class="badge unc">unverified</span>',STRATEGY:'<span class="badge strat">strategy</span>'};
var TODAY=new Date();function age(d){var t=Date.parse(d+'T12:00:00');return isNaN(t)?'':Math.max(0,Math.round((TODAY-t)/864e5))}
function fmt(cp){if(cp==null)return'';var g=Math.floor(cp/1e4),s=Math.floor(cp%1e4/100),c=cp%100,o=[];if(g)o.push(g+' gp');if(s)o.push(s+' sp');if(c||!o.length)o.push(c+' cp');return o.join(' ')}
function ilink(r){var nm=e(r.i);if(r.db)return '<a href="'+root+'items.html#'+encodeURIComponent(r.db)+'">'+nm+'</a>'+(r.wu?' <a class="ext dim" target="_blank" rel="noopener" href="'+e(r.wu)+'" title="Wiki page">wiki</a>':'');return nm}
function mlink(m,z){return '<a href="'+root+'mobs.html#'+encodeURIComponent(m)+'">'+e(m)+'</a>'}
function zlink(z,u){return u?'<a href="'+root+u+'">'+e(z)+'</a>':e(z)}
function conf(c){return '<span class="mkt-conf mkt-'+c+'">'+c+'</span>'}
var R=M.rows,qi=$('mkt-q'),qk=$('mkt-k'),qc=$('mkt-c'),qs=$('mkt-s');
Object.keys(M.kinds).forEach(function(k){if(R.some(function(r){return r.k===k}))qk.insertAdjacentHTML('beforeend','<option value="'+k+'">'+e(M.kinds[k])+'</option>')});
R.map(function(r){return r.sv}).filter(function(v,i,a){return v&&a.indexOf(v)===i}).sort().forEach(function(v){qs.insertAdjacentHTML('beforeend','<option>'+e(v)+'</option>')});
function sorter(st){return function(a,b){var k=st.k,x=a[k],y=b[k];if(k==='c'){x=CR[x];y=CR[y]}if(k==='k'){x=M.kinds[x];y=M.kinds[y]}if(k==='s'){x=SRC[x][1];y=SRC[y][1]}
 if(x==null||x==='')return 1;if(y==null||y==='')return -1;var r=(typeof x==='number'&&typeof y==='number')?x-y:String(x).localeCompare(String(y));return st.d*r||a.i.localeCompare(b.i)}}
function wireSort(tid,st,draw){var ths=document.querySelectorAll('#'+tid+' th[data-s]');ths.forEach(function(th){th.querySelector('button').addEventListener('click',function(){var k=th.getAttribute('data-s');st.d=st.k===k?-st.d:((k==='cp'||k==='d'||k==='c'||k==='pw'||k==='w')?-1:1);st.k=k;
 ths.forEach(function(o){o.removeAttribute('aria-sort')});th.setAttribute('aria-sort',st.d>0?'ascending':'descending');draw()})})}
var S1={k:'i',d:1};
function draw1(){var t=qi.value.trim().toLowerCase(),k=qk.value,c=qc.value,s=qs.value;
 var L=R.filter(function(r){if(k&&r.k!==k)return false;if(s&&r.sv!==s)return false;if(c==='high'&&r.c!=='high')return false;if(c==='medium'&&CR[r.c]<2)return false;if(c==='low'&&r.c!=='low')return false;
  if(t&&(r.i+' '+r.sv+' '+r.wh+' '+r.n+' '+SRC[r.s][1]+' '+r.dr.map(function(d){return d[0]+' '+d[1]}).join(' ')).toLowerCase().indexOf(t)<0)return false;return true}).sort(sorter(S1));
 $('mkt-count').textContent=L.length+' of '+R.length+' observations';
 $('mkt-b').innerHTML=L.length?L.map(function(r){var a=age(r.d),old=(r.k==='player_ask'||r.k==='player_bid')&&a>7;
  return '<tr'+(old?' class="mkt-old"':'')+'><td data-l="Item">'+ilink(r)+(r.wh?'<div class="dim">'+e(r.wh)+'</div>':'')+(r.n?'<div class="dim mkt-n">'+e(r.n)+'</div>':'')+'</td>'+
   '<td data-l="Price" class="mkt-nw"><b>'+e(r.p)+'</b>'+(r.cx?'':'')+(r.sv?'<div class="dim">'+e(r.sv)+'</div>':'')+'</td><td data-l="Type">'+e(M.kinds[r.k])+'</td>'+
   '<td data-l="Source"><a class="ext" target="_blank" rel="noopener" href="'+e(r.u)+'" title="'+e(SRC[r.s][4])+'">'+e(SRC[r.s][1])+'</a> '+(LB[r.l]||'')+'</td>'+
   '<td data-l="Seen"><span class="mkt-nw">'+e(r.d)+'</span><div class="dim">'+(a===''?'':a===0?'today':a===1?'1 day ago':a+' days ago')+(old?' · listing likely expired':'')+(r.ck?' · rechecked '+e(r.ck):'')+'</div></td><td data-l="Confidence">'+conf(r.c)+'</td></tr>'}).join(''):'<tr><td colspan="6" class="dim">Nothing matches. No price is sourced for that search.</td></tr>'}
[qi,qk,qc,qs].forEach(function(x){x.addEventListener('input',draw1);x.addEventListener('change',draw1)});
function fromHash(){var h=decodeURIComponent(location.hash.slice(1));if(h&&!/^(prices|vendor|money|money-cities|sources)$/.test(h)){qi.value=h;return true}}fromHash();window.addEventListener('hashchange',function(){if(fromHash()){draw1();var p=document.getElementById('prices');p&&p.scrollIntoView()}});
wireSort('mkt-t',S1,draw1);var so=$('mkt-sort');so.addEventListener('change',function(){var v=so.value.split(':');S1.k=v[0];S1.d=+v[1];document.querySelectorAll('#mkt-t th[data-s]').forEach(function(o){o.removeAttribute('aria-sort');if(o.getAttribute('data-s')===S1.k)o.setAttribute('aria-sort',S1.d>0?'ascending':'descending')});draw1()});draw1();
// vendor values
var V=R.filter(function(r){return r.k==='vendor_buys'}).map(function(r){var o=Object.assign({},r);o.pw=(r.w>0)?Math.round(r.cp/r.w):null;return o}),S2={k:'pw',d:-1};
function draw2(){$('mkt-vb').innerHTML=V.slice().sort(sorter(S2)).map(function(r){var dr=r.dr.slice(0,3).map(function(d){return mlink(d[0])+(d[1]?' ('+zlink(d[1],d[2])+')':'')}).join(', ');
  return '<tr><td data-l="Item">'+ilink(r)+(r.wh?'<div class="dim">'+e(r.wh)+'</div>':'')+'</td><td data-l="Vendor pays"><b>'+e(r.p)+'</b></td><td data-l="Weight">'+(r.w==null?'<span class="dim">not sourced</span>':e(r.w))+'</td>'+
   '<td data-l="Per 1.0 wt">'+(r.pw==null?'<span class="dim">—</span>':fmt(r.pw)+(r.pw>=100?' <span class="mkt-keep">keep</span>':''))+'</td><td data-l="Drops from">'+(dr||'<span class="dim">'+(r.n?e(r.n):'no drop source on the wiki')+'</span>')+(r.dr.length>3?' <span class="dim">+'+(r.dr.length-3)+' more</span>':'')+'</td>'+
   '<td data-l="Seen">'+e(r.d)+' '+conf(r.c)+'</td></tr>'}).join('')}
wireSort('mkt-v',S2,draw2);draw2();
// camps
$('mkt-camps').innerHTML=M.camps.map(function(c){return '<details class="mkt-camp"><summary><span class="mkt-band">'+e(c.b)+'</span> <b>'+e(c.c)+'</b> · '+e(c.z)+' '+(LB[c.l]||'')+'</summary><div class="mkt-cb">'+
  '<p>Zone: '+zlink(c.z,c.zu)+(c.z2?' and '+zlink(c.z2,c.z2u):'')+(c.m.length?' · Mobs: '+c.m.map(function(m){return mlink(m[0])}).join(', '):'')+'</p><ul class="tight">'+
  c.it.map(function(i){return '<li>'+(i.db?'<a href="'+root+'items.html#'+encodeURIComponent(i.db)+'">'+e(i.i)+'</a>':e(i.i))+': <b>'+e(i.p)+'</b>'+(i.here.length?' <span class="dim">· drops here: '+i.here.map(function(m){return mlink(m)}).join(', ')+'</span>':' <span class="dim">· drops here: not on the wiki</span>')+'</li>'}).join('')+
  '</ul>'+(c.n?'<p class="dim">'+e(c.n)+'</p>':'')+'</div></details>'}).join('');
// open the first camp so the section is not all closed
var fc=document.querySelector('.mkt-camp');if(fc)fc.open=true;
$('mkt-cities').innerHTML=M.cities.map(function(c){var wl=root+'walkthrough.html?city='+encodeURIComponent(c.city)+(c.race?'&race='+encodeURIComponent(c.race):'');
  return '<details class="mkt-camp"'+(c.city==="Ail'Vorith"?' open':'')+'><summary><b>'+e(c.city)+'</b> <span class="dim">'+(c.money.length?c.money.length+' notes':'no sourced data yet')+'</span></summary><div class="mkt-cb">'+
  (c.money.length?'<ul class="tight">'+c.money.map(function(m){return '<li>'+(LB[m.l]||'')+' '+e(m.t)+(m.s.length?' <span class="dim">['+m.s.map(function(s){return '<a class="ext" target="_blank" rel="noopener" href="'+e(s[1])+'">'+e(s[0])+'</a>'}).join('; ')+']</span>':'')+'</li>'}).join('')+'</ul>':'<p class="dim">No sourced data yet for this city.</p>')+
  '<p><a href="'+wl+'">Open the '+e(c.city)+' walkthrough</a></p></div></details>'}).join('');
})();
