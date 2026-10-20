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
  // UX pass 7: "Show N more" past the first 150 (Items) / 200 (Mobs) results; the added rows fill from the same pieces as you scroll
  this.shown=o.limit;this.more=document.createElement('p');this.more.className='ux-more';this.more.hidden=true;
  this.more.innerHTML='<button type="button" class="ux-more-b"></button> <span class="dim ux-more-n"></span>';
  o.out.parentNode.insertBefore(this.more,o.out.nextSibling);
  this.more.querySelector('button').addEventListener('click',function(){self.showMore()});
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
  this.shown=o.limit;var part=t&&!T;o.cnt.textContent=o.count(all.length)+(part?' (names so far)':'');this.part=part;
  this.st.hidden=!part;
  if(part)this.st.innerHTML=this.textFail?'<span class="lz-status lz-err">Full-text search could not load (offline?), so only names are matched.</span> <button type="button" class="ux-retry">Try again</button>':'<span class="lz-status" aria-busy="true">Loading the full search (stats, drops, zones)\u2026</span>';
  if(this.io)this.io.disconnect();
  o.out.innerHTML=o.shell(res);
  this.watch(o.out.querySelectorAll('.ux-dbp[data-id]'));this.moreUpd()};
Engine.prototype.watch=function(ph){var self=this,o=this.o;
  [].forEach.call(ph,function(el){var f=self.full(+el.getAttribute('data-id'));if(f)o.fill(el,f,self);else if(self.io)self.io.observe(el);else self.want(el)})};
Engine.prototype.moreUpd=function(){var o=this.o,n=(o.out.mnmRows||[]).length,left=n-this.shown;this.more.hidden=left<=0;if(left<=0)return;
  var k=Math.min(o.limit,left),w=o.what;this.more.querySelector('button').textContent='Show '+k+' more';
  this.more.querySelector('button').setAttribute('aria-label','Show '+k+' more '+w+'s ('+this.shown+' of '+n+' shown)');
  this.more.querySelector('.ux-more-n').textContent=this.shown+' of '+n+' shown'};
Engine.prototype.showMore=function(){var o=this.o,all=o.out.mnmRows||[],add=all.slice(this.shown,this.shown+o.limit);if(!add.length)return;
  var box=o.box(),mark=box.children.length;box.insertAdjacentHTML('beforeend',o.rowsHTML(add));this.shown+=add.length;
  this.watch([].slice.call(box.children,mark).filter(function(el){return el.classList.contains('ux-dbp')&&el.hasAttribute('data-id')}));
  var n=all.length;o.cnt.textContent=n+' '+o.what+'s'+(this.shown<n?' (showing '+this.shown+')':'')+(this.part?' (names so far)':'');
  this.moreUpd();try{o.out.dispatchEvent(new CustomEvent('ux-db-more',{bubbles:true}))}catch(x){}
  if(this.more.hidden){var f=box.children[mark]&&box.children[mark].querySelector('a,button');if(f)f.focus()}};
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
    what:'item',box:function(){return iout},rowsHTML:function(res){return this.shell(res)},
    shell:function(res){return res.map(function(d){return '<div class="idb-it ux-dbp" data-id="'+d[1]+'"><div><a class="ext" target="_blank" rel="noopener"><b>'+e(d[0])+'</b></a> <span class="dim">'+e(slot(d)||'no slot')+(d[4]?' \u00b7 lvl '+d[4]:'')+'</span>'+
      (MK[d[0]]?' <a class="idb-mkt" href="'+root+'market.html#'+encodeURIComponent(d[0])+'" title="'+e(MK[d[0]][1]+', seen '+MK[d[0]][2])+'">\ud83d\udcb0 Market: '+e(MK[d[0]][0])+'</a>':'')+' <button type="button" class="ux-cmp-b" data-cmp="'+e(d[0])+'" aria-pressed="false">Compare</button></div><p class="lz-status ux-dbp-st">Details load as you scroll.</p></div>'}).join('')},
    fill:function(el,d){el.classList.remove('ux-dbp');var a=el.querySelector('a.ext');if(a&&d[1])a.href=d[1];var s=el.querySelector('.ux-dbp-st');if(s)s.remove();
      var srcs=d[6].length?d[6].filter(function(x){return !x[6]}).slice(0,6).concat(d[6].filter(function(x){return x[6]}).slice(0,3)).map(function(x){var z=x[3]?(x[4]?' \u2014 <a href="'+root+x[4]+'">'+e(x[3])+'</a>':' \u2014 '+e(x[3])):'';
        return '<li><span class="tag">'+K[x[0]]+'</span>'+(x[6]?' <a class="tag ext" target="_blank" rel="noopener" href="https://mnm-db.com/">mnm-db</a>':'')+' '+mob(x)+(x[2]?' (lvl '+e(x[2])+')':'')+z+(x[5]?', '+e(x[5]):'')+'</li>'}).join(''):'<li class="dim">No source on the wiki <span class="badge unc">unverified</span></li>';
      el.insertAdjacentHTML('beforeend',(d[7]&&d[7].c?'<div><span class="tag conf">sources differ</span> <span class="dim">'+e(d[7].c.join('; '))+' \u00b7 <a href="'+root+'source-conflicts.html#item">all conflicts</a></span></div>':'')+(d[5]?'<div class="dim">'+e(d[5])+'</div>':'')+
        '<div class="dim">'+(d[3]?(d[3].split(' ').length>=18?'All classes':e(d[3])):'classes not listed')+'</div><ul class="tight">'+srcs+'</ul>')}});
  wire(E,[q,sl,mc,ml,sr]);
  // ---- UX pass 7: compare two items side by side (#8). Site data only: the two full rows from the same pieces, listed values
  // shown as they are (stats split at their commas so the same stat lines up; no sums or differences are calculated).
  // Picks: localStorage mnm-cmp and ?cmp=<name>|<name> (shareable); a third pick replaces the oldest.
  (function(){var CK='mnm-cmp',picks=[],byN={},dlg=null;
    (window.MNM_IDB||[]).forEach(function(d){if(!(d[0] in byN))byN[d[0]]=d[1]});
    try{picks=JSON.parse(localStorage.getItem(CK)||'[]')}catch(x){picks=[]}
    var qc=(location.search.match(/[?&]cmp=([^&]*)/)||[])[1];if(qc){try{picks=decodeURIComponent(qc.replace(/\+/g,' ')).split('|')}catch(x){}}
    if(!Array.isArray(picks))picks=[];picks=picks.filter(function(n,i){return typeof n==='string'&&n in byN&&picks.indexOf(n)===i}).slice(-2);
    var bar=document.createElement('div');bar.className='ux-cmpbar';bar.setAttribute('role','region');bar.setAttribute('aria-label','Item comparison');iout.parentNode.insertBefore(bar,iout);
    var say=document.createElement('p');say.className='ux-vh';say.setAttribute('role','status');bar.parentNode.insertBefore(say,bar);
    function save(){try{localStorage.setItem(CK,JSON.stringify(picks))}catch(x){}
      if(history.replaceState){var keep=location.search.replace(/^\?/,'').split('&').filter(function(kv){return kv&&kv.split('=')[0]!=='cmp'});
        if(picks.length)keep.push('cmp='+encodeURIComponent(picks.join('|')));history.replaceState(history.state,'',location.pathname+(keep.length?'?'+keep.join('&'):'')+location.hash)}}
    function paint(){[].forEach.call(iout.querySelectorAll('.ux-cmp-b'),function(b){var on=picks.indexOf(b.getAttribute('data-cmp'))>=0;b.setAttribute('aria-pressed',on?'true':'false');b.textContent=on?'\u2713 Comparing':'Compare'});
      bar.hidden=!picks.length;if(!picks.length){bar.innerHTML='';return}
      bar.innerHTML='<span class="ux-cmpbar-l">Compare:</span> '+picks.map(function(n){return '<span class="ux-cmp-chip">'+e(n)+'<button type="button" class="ux-cmp-x" data-cmp="'+e(n)+'" aria-label="Remove '+e(n)+' from the comparison">\u2715</button></span>'}).join(' ')+
        (picks.length===2?' <button type="button" class="ux-cmp-open">Compare side by side</button>':' <span class="dim">Pick one more item.</span>')+' <button type="button" class="ux-cmp-clr">Clear</button>'}
    function toggle(n,from){var i=picks.indexOf(n),msg;if(i>=0){picks.splice(i,1);msg='Removed '+n+' from the comparison.'}
      else{picks.push(n);msg='Added '+n+' to the comparison.';if(picks.length>2)msg+=' It replaces '+picks.shift()+'.'}
      save();paint();say.textContent=msg;if(picks.length===2&&i<0)open(from)}
    function stats(t){var o=[],k={};String(t||'').split(/,\s*/).forEach(function(x){x=x.trim();if(!x)return;var m=x.match(/^(.*?)\s*[+-]?\d[\d.]*%?$/),key=(m&&m[1]?m[1]:x).toLowerCase();if(key in k)key+='#'+o.length;k[key]=x;o.push(key)});return {o:o,k:k}}
    function cell(v){return v==null||v===''?'<span class="dim">\u2014</span>':v}
    function srcs(d){var K={n:'Named',d:'Drop',q:'Quest',v:'Vendor',c:'Crafted'};return d[6].length?'<ul class="tight">'+d[6].map(function(x){return '<li><span class="tag">'+(K[x[0]]||e(x[0]))+'</span>'+(x[6]?' <span class="tag">mnm-db</span>':'')+' '+e(x[1])+(x[2]?' (lvl '+e(x[2])+')':'')+(x[3]?' \u2014 '+e(x[3]):'')+(x[5]?', '+e(x[5]):'')+'</li>'}).join('')+'</ul>':'<span class="dim">No source on the wiki</span>'}
    function table(A,B){var rows=[],sa=stats(A[5]),sb=stats(B[5]),keys=sa.o.slice();sb.o.forEach(function(k){if(keys.indexOf(k)<0)keys.push(k)});
      function row(f,a,b,same){rows.push('<tr'+(same?'':' class="ux-cmp-ne"')+'><th scope="row">'+f+(same?'':'<span class="ux-vh"> (differs)</span>')+'</th><td>'+cell(a)+'</td><td>'+cell(b)+'</td></tr>')}
      row('Slot',e(slotOf(A)),e(slotOf(B)),slotOf(A)===slotOf(B));row('Level',A[4]?e(A[4]):'',B[4]?e(B[4]):'',String(A[4]||'')===String(B[4]||''));
      row('Classes',e(A[3]||'not listed'),e(B[3]||'not listed'),(A[3]||'')===(B[3]||''));
      if(keys.length)keys.forEach(function(k){var a=sa.k[k]||'',b=sb.k[k]||'';row('Stat: '+e(k.replace(/#\d+$/,'')||'other'),e(a),e(b),a===b)});else row('Stats','','',true);
      row('Sources',srcs(A),srcs(B),false);
      var cf=function(d){return d[7]&&d[7].c?'<span class="tag conf">sources differ</span> '+e(d[7].c.join('; ')):''};if(cf(A)||cf(B))row('Sources differ',cf(A),cf(B),cf(A)===cf(B));
      row('Wiki page','<a class="ext" target="_blank" rel="noopener" href="'+e(A[1])+'">'+e(A[0])+'</a>','<a class="ext" target="_blank" rel="noopener" href="'+e(B[1])+'">'+e(B[0])+'</a>',true);
      return '<div class="ux-cmp-tw"><table class="ux-cmp-t"><caption class="ux-vh">'+e(A[0])+' compared with '+e(B[0])+'</caption><thead><tr><th scope="col"><span class="ux-vh">Field</span></th><th scope="col">'+e(A[0])+'</th><th scope="col">'+e(B[0])+'</th></tr></thead><tbody>'+rows.join('')+'</tbody></table></div>'+
        '<p class="dim ux-cmp-n">Listed values from the wiki item pages (and mnm-db where marked), as in the rows above. Rows marked <span class="ux-cmp-key">\u2260</span> differ. <button type="button" class="ux-cmp-swap">Swap columns</button></p>'}
    function slotOf(d){return d[2]||'no slot'}
    function fillDlg(){var ids=picks.map(function(n){return byN[n]}),body=dlg.querySelector('.ux-cmp-body');
      body.innerHTML='<p class="lz-status" aria-busy="true">Loading both items\u2026</p>';
      Promise.all(ids.map(function(id){return E.chunk(Math.floor(id/IX.n))})).then(function(){var A=E.full(ids[0]),B=E.full(ids[1]);if(!A||!B)throw new Error('missing');body.innerHTML=table(A,B)},
        function(){body.innerHTML='<p class="lz-status lz-err">The item details could not load (offline?). <button type="button" class="ux-retry ux-cmp-retry">Try again</button></p>'})}
    function open(from){if(picks.length<2)return;
      if(!dlg){dlg=document.createElement('dialog');dlg.className='ux-cmpdlg';dlg.setAttribute('aria-labelledby','ux-cmp-h');
        dlg.innerHTML='<div class="ux-sheet-hd"><h2 id="ux-cmp-h">Compare items</h2><button type="button" class="ux-sheet-x" aria-label="Close the comparison">\u2715</button></div><div class="ux-cmp-body"></div>';
        document.body.appendChild(dlg);
        dlg.addEventListener('click',function(ev){if(ev.target===dlg||ev.target.closest('.ux-sheet-x')){dlg.close();return}
          if(ev.target.closest('.ux-cmp-swap')){picks.reverse();save();paint();fillDlg();dlg.querySelector('.ux-sheet-x').focus();return}if(ev.target.closest('.ux-cmp-retry'))fillDlg()});
        dlg.addEventListener('close',function(){var o=dlg._op;if(o&&!document.contains(o))o=bar.querySelector('.ux-cmp-open');if(o&&o.focus)o.focus({preventScroll:true})})}
      dlg._op=from||document.activeElement;fillDlg();if(!dlg.open)dlg.showModal();dlg.querySelector('.ux-sheet-x').focus()}
    iout.addEventListener('click',function(ev){var b=ev.target.closest('.ux-cmp-b');if(b)toggle(b.getAttribute('data-cmp'),b)});
    bar.addEventListener('click',function(ev){var x=ev.target.closest('.ux-cmp-x');if(x){toggle(x.getAttribute('data-cmp'));var n=bar.querySelector('button');if(n)n.focus();else iout.querySelector('.ux-cmp-b')&&iout.querySelector('.ux-cmp-b').focus();return}
      if(ev.target.closest('.ux-cmp-open'))open(ev.target.closest('.ux-cmp-open'));if(ev.target.closest('.ux-cmp-clr')){picks=[];save();paint();say.textContent='Comparison cleared.';var f=iout.querySelector('.ux-cmp-b');if(f)f.focus()}});
    var mo=window.MutationObserver&&new MutationObserver(paint);if(mo)mo.observe(iout,{childList:true});iout.addEventListener('ux-db-more',paint);
    paint();if(picks.length===2&&qc)setTimeout(function(){open(bar.querySelector('.ux-cmp-open'))},0);
    window.MNM_UX_CMP={picks:function(){return picks.slice()},open:function(){open(bar.querySelector('.ux-cmp-open'))},toggle:toggle};
  })();
  ['mnm-class','mnm-range'].forEach(function(id){var x=document.getElementById(id);if(x)x.addEventListener('change',function(){setTimeout(function(){E.go()},0)})});
})()}
// ---- Mobs
var mout=document.getElementById('mob-out'),MX=window.MNM_MDBX;
if(mout&&MX){(function(){
  var q=document.getElementById('mob-q'),nm=document.getElementById('mob-named'),ml=document.getElementById('mob-lvl'),md=document.getElementById('mob-drop'),cnt=document.getElementById('mob-count'),U={};
  var M='<a class="ext" target="_blank" rel="noopener" href="https://mnm-db.com/">mnm-db</a>';
  function il(n){return window.MNM_ITEMPAGE?'<a class="tt-item" data-item="'+e(n)+'" href="'+root+'items.html#'+encodeURIComponent(n)+'">'+e(n)+'</a>':'<a class="ext" target="_blank" rel="noopener" href="'+e(U[n]||'#')+'">'+e(n)+'</a>'}
  var E=new Engine({X:MX,rows:window.MNM_MOBS,q:q,out:mout,cnt:cnt,pfx:'mdb-c-',textFile:'mdb-text.js',textVar:'MNM_MDBT',limit:200,
    store:function(){return window.MNM_MDBC||{}},rowsOf:function(c){if(c.u)for(var k in c.u)U[k]=c.u[k];return c.r},id:function(d){return d[4]},
    base:function(d){return d[0]+' '+d[3]},busy:'Loading drops\u2026',fail:'Could not load the drops (offline?).',
    count:function(n){return n+' mobs'+(n>200?' (showing first 200)':'')},
    filter:function(){var b=((document.getElementById('mnm-range')||{}).value||'1-60').split('-').map(Number);
      return function(d){if(nm.checked&&!d[5])return false;if(ml.checked&&!(d[1]&&d[1]>=b[0]&&d[1]<=b[1]))return false;if(md.checked&&!(d[6]&1))return false;return true}},
    what:'mob',box:function(){return mout.querySelector('tbody')},rowsHTML:function(res){return this.shell(res).replace(/^[\s\S]*?<tbody>/,'').replace(/<\/tbody>[\s\S]*$/,'')},
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
