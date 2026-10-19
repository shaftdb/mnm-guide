// UX pass 6: Items and Mobs databases from a compact index (idb-index.js / mdb-index.js, loaded with the page) plus
// on-demand pieces: the full search text (idb-text.js / mdb-text.js) on the first typed search, and the full rows
// (idb-c-<n>.js / mdb-c-<n>.js, 100 rows each) when a result nears the screen, for CSV export, or for printing.
// Replaces mod-items.js / mod-mobs.js on those two pages only when the build split succeeded (modules/zzz_ux.py).
// Same markup, filters and limits as before; mod-ux.js (dbPage) still adds sort, URL params, memory, toolbar, CSV, copy.
(function(){
var de=document.documentElement,root=de.getAttribute('data-root')||'';
function e(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function load(f){return window.MNM_LOAD?window.MNM_LOAD(f):Promise.reject(new Error('no loader'))}
// ---- shared engine
function Engine(o){var self=this;this.o=o;this.ch={};this.textP=null;this.textFail=false;this.T=null;this.io=null;
  this.st=document.createElement('p');this.st.className='ux-dbst';this.st.hidden=true;this.st.setAttribute('role','status');
  o.cnt.parentNode.insertBefore(this.st,o.cnt.nextSibling);
  this.st.addEventListener('click',function(ev){if(ev.target.closest('.ux-retry')){self.textFail=false;self.go()}});
  o.out.addEventListener('click',function(ev){var b=ev.target.closest('.ux-retry');if(!b)return;var el=b.closest('[data-id]');if(el){self.want(el,1)}});
  if(window.IntersectionObserver)this.io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){self.io.unobserve(x.target);self.want(x.target)}})},{rootMargin:'700px 0px'});
}
Engine.prototype.chunk=function(i){var o=this.o,self=this;if(o.store()[i])return Promise.resolve(o.store()[i]);if(this.ch[i])return this.ch[i];
  return this.ch[i]=load(o.pfx+i+'.js').then(function(){var c=o.store()[i];if(!c)throw new Error('missing '+o.pfx+i);return c},function(err){delete self.ch[i];throw err})};
Engine.prototype.full=function(id){var c=this.o.store()[Math.floor(id/this.o.X.n)];return c?this.o.rowsOf(c)[id%this.o.X.n]:null};
Engine.prototype.want=function(el,retry){var self=this,id=+el.getAttribute('data-id'),f=this.full(id);if(f){this.o.fill(el,f,this);return Promise.resolve()}
  var s=el.querySelector('.ux-dbp-st');if(s){s.className='lz-status ux-dbp-st';s.setAttribute('aria-busy','true');s.textContent=this.o.busy}
  return this.chunk(Math.floor(id/this.o.X.n)).then(function(){var g=self.full(id);if(g&&el.classList.contains('ux-dbp'))self.o.fill(el,g,self)},
   function(){var s=el.querySelector('.ux-dbp-st');if(s){s.removeAttribute('aria-busy');s.className='lz-status lz-err ux-dbp-st';s.innerHTML=e(self.o.fail)+' <button type="button" class="ux-retry">Try again</button>'}})};
Engine.prototype.fillAll=function(){var self=this;return Promise.all([].map.call(this.o.out.querySelectorAll('.ux-dbp[data-id]'),function(el){return self.want(el).catch(function(){})}))};
Engine.prototype.text=function(){var o=this.o,self=this;if(this.T)return Promise.resolve(this.T);if(this.textP)return this.textP;
  return this.textP=load(o.textFile).then(function(){var X=window[o.textVar];if(!X)throw new Error('missing '+o.textFile);
    var w=X.w,T=new Array(o.rows.length),byId={};o.rows.forEach(function(r){byId[o.id(r)]=r});
    X.r.forEach(function(t,id){var r=byId[id],s=r?o.base(r):'';s+=' '+t[0];for(var k=1;k<t.length;k++)s+=' '+w[t[k]];T[id]=s.toLowerCase()});
    self.T=T;self.textFail=false;return T},function(err){self.textP=null;self.textFail=true;throw err})};
// all rows matching the controls; with the search text not loaded yet, a query matches the index fields (names) only
Engine.prototype.go=function(){var o=this.o,self=this,t=o.q.value.trim().toLowerCase(),D=o.rows,all=[],res=[],T=this.T,F=o.filter();
  if(t&&!T&&!this.textFail&&!this.textP)this.text().then(function(){self.go()},function(){self.go()});
  for(var i=0;i<D.length;i++){var d=D[i];if(!F(d))continue;
    if(t&&(T?T[o.id(d)]:o.base(d).toLowerCase()).indexOf(t)<0)continue;all.push(d);if(res.length<o.limit)res.push(d)}
  o.out.mnmRows=all;
  var part=t&&!T;o.cnt.textContent=o.count(all.length)+(part?' (names so far)':'');
  this.st.hidden=!part;
  if(part)this.st.innerHTML=this.textFail?'<span class="lz-status lz-err">Full-text search could not load (offline?), so only names are matched.</span> <button type="button" class="ux-retry">Try again</button>':'<span class="lz-status" aria-busy="true">Loading the full search (stats, drops, zones)\u2026</span>';
  if(this.io)this.io.disconnect();
  o.out.innerHTML=o.shell(res);
  var ph=o.out.querySelectorAll('.ux-dbp[data-id]');
  [].forEach.call(ph,function(el){var f=self.full(+el.getAttribute('data-id'));if(f)o.fill(el,f,self);else if(self.io)self.io.observe(el);else self.want(el)})};
// full rows for every current match (CSV export): waits for the search text when a query is typed, then the pieces
Engine.prototype.allFull=function(){var self=this,o=this.o,t=o.q.value.trim();
  var p=t&&!this.T?this.text().then(function(){self.go()}):Promise.resolve();
  return p.then(function(){var rows=o.out.mnmRows||[],need={};rows.forEach(function(r){need[Math.floor(o.id(r)/o.X.n)]=1});
    return Promise.all(Object.keys(need).map(function(c){return self.chunk(+c)})).then(function(){return rows.map(function(r){return self.full(o.id(r))})})})};
function wire(E,ctl){var o=E.o;ctl.forEach(function(x){x.addEventListener('input',function(){E.go()});x.addEventListener('change',function(){E.go()})});
  window.addEventListener('beforeprint',function(){E.fillAll()});
  window.MNM_UXDB={go:function(){E.go()},fillAll:function(){return E.fillAll()},full:function(){return E.allFull()},text:function(){return E.text()},engine:E};
  var h='';try{h=decodeURIComponent(location.hash.slice(1))}catch(x){}if(h)o.q.value=h;E.go()}
// ---- Items
var iout=document.getElementById('idb-out'),IX=window.MNM_IDBX;
if(iout&&IX){(function(){
  var q=document.getElementById('idb-q'),sl=document.getElementById('idb-slot'),mc=document.getElementById('idb-cls'),ml=document.getElementById('idb-lvl'),sr=document.getElementById('idb-src'),cnt=document.getElementById('idb-count');
  var MK=window.MNM_MKTI||{},K={n:'Named',d:'Drop',q:'Quest',v:'Vendor',c:'Crafted'},KB={n:1,d:2,q:4,v:8,c:16};
  function sel(){var R=window.MNM_RANGES||{},c=document.getElementById('mnm-class'),r=document.getElementById('mnm-range');return{code:(R.codes||{})[c&&c.value],b:(r&&r.value||'1-60').split('-').map(Number)}}
  function slot(d){return IX.slots[d[2]]||''}
  function mob(x){return (x[0]==='n'||x[0]==='d')&&x[1]?'<span class="tt-mob" data-mob="'+e(x[1])+'">'+e(x[1])+'</span>':e(x[1])}
  var E=new Engine({X:IX,rows:window.MNM_IDB,q:q,out:iout,cnt:cnt,pfx:'idb-c-',textFile:'idb-text.js',textVar:'MNM_IDBT',limit:150,
    store:function(){return window.MNM_IDBC||{}},rowsOf:function(c){return c},id:function(d){return d[1]},
    base:function(d){return d[0]+' '+slot(d)},busy:'Loading details\u2026',fail:'Could not load the details (offline?).',
    count:function(n){return n+' items'+(n>150?' (showing first 150, narrow the search)':'')},
    filter:function(){var s=sl.value,S=sel(),src=sr.value,bit=S.code?IX.codes.indexOf(S.code):-2;
      return function(d){if(s&&(' '+slot(d)+' ').indexOf(' '+s+' ')<0)return false;
        if(mc.checked&&S.code&&(bit<0||!(d[3]&(1<<bit))))return false;
        if(ml.checked&&!(d[4]&&d[4]>=S.b[0]&&d[4]<=S.b[1]))return false;
        if(src&&!(d[5]&KB[src]))return false;return true}},
    shell:function(res){return res.map(function(d){return '<div class="idb-it ux-dbp" data-id="'+d[1]+'"><div><a class="ext" target="_blank" rel="noopener"><b>'+e(d[0])+'</b></a> <span class="dim">'+e(slot(d)||'no slot')+(d[4]?' \u00b7 lvl '+d[4]:'')+'</span>'+
      (MK[d[0]]?' <a class="idb-mkt" href="'+root+'market.html#'+encodeURIComponent(d[0])+'" title="'+e(MK[d[0]][1]+', seen '+MK[d[0]][2])+'">\ud83d\udcb0 Market: '+e(MK[d[0]][0])+'</a>':'')+'</div><p class="lz-status ux-dbp-st">Details load as you scroll.</p></div>'}).join('')},
    fill:function(el,d){el.classList.remove('ux-dbp');var a=el.querySelector('a.ext');if(a&&d[1])a.href=d[1];var s=el.querySelector('.ux-dbp-st');if(s)s.remove();
      var srcs=d[6].length?d[6].filter(function(x){return !x[6]}).slice(0,6).concat(d[6].filter(function(x){return x[6]}).slice(0,3)).map(function(x){var z=x[3]?(x[4]?' \u2014 <a href="'+root+x[4]+'">'+e(x[3])+'</a>':' \u2014 '+e(x[3])):'';
        return '<li><span class="tag">'+K[x[0]]+'</span>'+(x[6]?' <a class="tag ext" target="_blank" rel="noopener" href="https://mnm-db.com/">mnm-db</a>':'')+' '+mob(x)+(x[2]?' (lvl '+e(x[2])+')':'')+z+(x[5]?', '+e(x[5]):'')+'</li>'}).join(''):'<li class="dim">No source on the wiki <span class="badge unc">unverified</span></li>';
      el.insertAdjacentHTML('beforeend',(d[7]&&d[7].c?'<div><span class="tag conf">sources differ</span> <span class="dim">'+e(d[7].c.join('; '))+' \u00b7 <a href="'+root+'source-conflicts.html#item">all conflicts</a></span></div>':'')+(d[5]?'<div class="dim">'+e(d[5])+'</div>':'')+
        '<div class="dim">'+(d[3]?(d[3].split(' ').length>=18?'All classes':e(d[3])):'classes not listed')+'</div><ul class="tight">'+srcs+'</ul>')}});
  wire(E,[q,sl,mc,ml,sr]);
  ['mnm-class','mnm-range'].forEach(function(id){var x=document.getElementById(id);if(x)x.addEventListener('change',function(){setTimeout(function(){E.go()},0)})});
})()}
// ---- Mobs
var mout=document.getElementById('mob-out'),MX=window.MNM_MDBX;
if(mout&&MX){(function(){
  var q=document.getElementById('mob-q'),nm=document.getElementById('mob-named'),ml=document.getElementById('mob-lvl'),md=document.getElementById('mob-drop'),cnt=document.getElementById('mob-count'),U={};
  var M='<a class="ext" target="_blank" rel="noopener" href="https://mnm-db.com/">mnm-db</a>';
  function il(n){return window.MNM_ITEMPAGE?'<a href="'+root+'items.html#'+encodeURIComponent(n)+'">'+e(n)+'</a>':'<a class="ext" target="_blank" rel="noopener" href="'+e(U[n]||'#')+'">'+e(n)+'</a>'}
  var E=new Engine({X:MX,rows:window.MNM_MOBS,q:q,out:mout,cnt:cnt,pfx:'mdb-c-',textFile:'mdb-text.js',textVar:'MNM_MDBT',limit:200,
    store:function(){return window.MNM_MDBC||{}},rowsOf:function(c){if(c.u)for(var k in c.u)U[k]=c.u[k];return c.r},id:function(d){return d[4]},
    base:function(d){return d[0]+' '+d[3]},busy:'Loading drops\u2026',fail:'Could not load the drops (offline?).',
    count:function(n){return n+' mobs'+(n>200?' (showing first 200)':'')},
    filter:function(){var b=((document.getElementById('mnm-range')||{}).value||'1-60').split('-').map(Number);
      return function(d){if(nm.checked&&!d[5])return false;if(ml.checked&&!(d[1]&&d[1]>=b[0]&&d[1]<=b[1]))return false;if(md.checked&&!(d[6]&1))return false;return true}},
    shell:function(res){return '<div class="tw"><table class="grid"><thead><tr><th>Mob</th><th>Lvl</th><th>Zone</th><th>Drops</th></tr></thead><tbody>'+res.map(function(d){
      return '<tr class="ux-dbp" data-id="'+d[4]+'"><td>'+(d[5]?'<b>'+e(d[0])+'</b> <span class="tag">named</span>':e(d[0]))+(d[6]&2?' <span class="tag">quest NPC</span>':'')+(d[6]&4?' <span class="tag">'+M+' only</span>':'')+'</td><td>'+e(d[2]||'?')+'</td><td><a href="'+root+d[7]+'">'+e(d[3])+'</a></td><td><span class="lz-status ux-dbp-st">Drops load as you scroll.</span></td></tr>'}).join('')+'</tbody></table></div>'},
    fill:function(tr,d){tr.classList.remove('ux-dbp');var x=d[10]||{},c=tr.cells;
      if(x.p){var lk=' <a class="ext dim" target="_blank" rel="noopener" href="'+e(x.p)+'" title="Wiki mob page">wiki</a>',cb=c[0].querySelector('.ux-copy');if(cb)cb.insertAdjacentHTML('beforebegin',lk);else c[0].insertAdjacentHTML('beforeend',lk)}
      c[0].insertAdjacentHTML('beforeend',(d[6]?'<br><span class="dim">'+e(d[6])+'</span>':'')+(x.c?'<br><span class="tag conf" title="'+e(x.c.join('\n'))+'">sources differ</span> <span class="dim">'+e(x.c.join('; '))+'</span>':''));
      if(x.e)c[1].insertAdjacentHTML('beforeend','<br><span class="dim">'+M+': '+e(x.e)+'</span>');
      if(d[7])c[2].insertAdjacentHTML('beforeend','<br><span class="dim">'+e(d[7])+'</span>');
      c[3].innerHTML=(d[8].map(il).concat(d[9].map(e)).join(', ')||'<span class="dim">none recorded</span>')+(x.m?'<br><span class="dim">Seen ('+M+', drops/corpses): '+x.m.map(function(m){return (window.MNM_ITEMPAGE?il(m[0]):e(m[0]))+' '+e(m[1])}).join(', ')+'</span>':'')}});
  wire(E,[q,nm,ml,md]);
  var s=document.getElementById('mnm-range');if(s)s.addEventListener('change',function(){setTimeout(function(){E.go()},0)});
})()}
})();
