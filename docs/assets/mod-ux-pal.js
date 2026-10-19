(function(){var C=window.MNM_UXC;if(!C||window.MNM_UX_PALI)return;
var root=C.root,esc=C.esc,recent=C.recent,here=C.here,JUMP=C.JUMP,GO=C.GO,href=C.href,S=C.S,lsGet=C.lsGet;
var pal=null,inp,list,stat,act=-1,opts=[],opener=null,lastQ=null;
function kind(it){if(it.e)return 'Wiki';if(/^item\b/i.test(it.s))return 'Items';if(/spells/i.test(it.s))return 'Spells';return 'Pages'}
function build(){if(pal)return;
pal=document.createElement('dialog');pal.className='ux-pal';pal.setAttribute('aria-labelledby','ux-pal-h');
pal.innerHTML='<div class="ux-pal-hd"><h2 id="ux-pal-h" class="ux-vh">Quick jump</h2><span class="ux-pal-ico" aria-hidden="true">&#9906;</span>'+
'<input id="ux-pal-q" type="search" autocomplete="off" spellcheck="false" placeholder="Jump to a page, class, zone, item…" role="combobox" aria-expanded="true" aria-controls="ux-pal-list" aria-autocomplete="list" aria-label="Quick jump: type to search">'+
'<button type="button" class="ux-pal-x" aria-label="Close">&#10005;</button></div>'+
'<p class="ux-pal-st" id="ux-pal-st" role="status" aria-live="polite"></p><ul id="ux-pal-list" class="ux-pal-list" role="listbox" aria-label="Results"></ul>'+
'<p class="ux-pal-ft dim"><kbd>&uarr;</kbd><kbd>&darr;</kbd> move · <kbd>Enter</kbd> open · <kbd>Esc</kbd> close · <kbd>?</kbd> all shortcuts</p>';
document.body.appendChild(pal);inp=pal.querySelector('input');list=pal.querySelector('ul');stat=pal.querySelector('.ux-pal-st');
inp.addEventListener('input',render);
inp.addEventListener('keydown',function(e){if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();mv(e.key==='ArrowDown'?1:-1)}
else if(e.key==='Home'&&e.ctrlKey){e.preventDefault();setAct(0)}else if(e.key==='End'&&e.ctrlKey){e.preventDefault();setAct(opts.length-1)}
else if(e.key==='Enter'){e.preventDefault();var o=opts[act>=0?act:0];if(o)openOpt(o)}
else if(e.key==='Escape'){e.preventDefault();close()}});
pal.addEventListener('keydown',function(e){if(e.key!=='Tab')return;var f=[inp,pal.querySelector('.ux-pal-x')];var i=f.indexOf(document.activeElement);e.preventDefault();f[(i+(e.shiftKey?-1:1)+f.length)%f.length].focus()});
pal.querySelector('.ux-pal-x').addEventListener('click',close);
pal.addEventListener('click',function(e){if(e.target===pal){close();return}var li=e.target.closest('[role=option]');if(li)openOpt(li)});
pal.addEventListener('close',function(){if(opener&&opener.focus)opener.focus({preventScroll:true});opener=null});
if(S())S().onUpdate(function(){if(pal.open)render(1)});
}
function setAct(i){act=Math.max(-1,Math.min(opts.length-1,i));opts.forEach(function(o,j){o.setAttribute('aria-selected',j===act?'true':'false');o.classList.toggle('on',j===act)});
if(act>=0){inp.setAttribute('aria-activedescendant',opts[act].id);opts[act].scrollIntoView({block:'nearest'})}else inp.removeAttribute('aria-activedescendant')}
function mv(d){setAct(act<0?(d>0?0:opts.length-1):(act+d+opts.length)%opts.length)}
function openOpt(o){var u=o.getAttribute('data-href');if(!u)return;if(o.getAttribute('data-ext')){window.open(u,'_blank','noopener');close();return}location.href=u;close()}
function item(i,t,u,sub,ext){return '<li role="option" id="ux-pal-o'+i+'" aria-selected="false" data-href="'+esc(u)+'"'+(ext?' data-ext="1"':'')+'><span class="ux-pal-t">'+esc(t)+(ext?' <span aria-hidden="true">&#8599;</span>':'')+'</span>'+(sub?'<span class="ux-pal-s">'+esc(sub)+'</span>':'')+'</li>'}
function group(n,h){return '<li role="presentation" class="ux-pal-g" aria-hidden="true">'+esc(n)+'</li>'+h}
function render(keep){var t=inp.value.trim(),h=[],n=0,cur=act;
var fv=lsGet('mnm-favs',[]);if(!Array.isArray(fv))fv=[];
if(t.length<2){if(fv.length)h.push(group('Pinned',fv.slice(0,12).map(function(r){return item(n++,'\u2605 '+r.t,href(r.u),r.u.replace(/\.html$/,'').replace(/\/index$/,'/'))}).join('')));
var rc=recent.filter(function(r){return r.u!==here&&!fv.some(function(f){return f.u===r.u})}).slice(0,8);
if(rc.length)h.push(group('Recently viewed',rc.map(function(r){return item(n++,r.t,href(r.u),r.u.replace(/\.html$/,'').replace(/\/index$/,'/'))}).join('')));
h.push(group('Jump to',JUMP.map(function(j){return item(n++,j[0],href(j[1]),'')}).join('')));
stat.textContent=t.length?'Type at least 2 letters to search.':((fv.length?'Pinned pages, ':'')+(rc.length?'recently viewed pages and main sections.':'main sections.')).replace(/^./,function(c){return c.toUpperCase()})+(fv.length?'':' Tip: star a page (\u2606 next to its title) to pin it here.');
}else{var s=S(),lt=t.toLowerCase();
var fv2=fv.filter(function(r){return r.t.toLowerCase().indexOf(lt)>=0}).slice(0,4);
if(fv2.length)h.push(group('Pinned',fv2.map(function(r){return item(n++,'\u2605 '+r.t,href(r.u),r.u)}).join('')));
var rc2=recent.filter(function(r){return r.t.toLowerCase().indexOf(lt)>=0}).slice(0,3);
if(rc2.length)h.push(group('Recently viewed',rc2.map(function(r){return item(n++,r.t,href(r.u),r.u)}).join('')));
var jm=JUMP.filter(function(j){return j[0].toLowerCase().indexOf(lt)>=0});
if(!s){stat.textContent='Search is not available on this page.'}
else if(!s.ready()){if(s.failed()){stat.textContent='The search index could not load (offline?). Close and try again.';stat.classList.add('lz-err')}else{stat.textContent='Loading search index…';s.load()}
if(jm.length)h.push(group('Jump to',jm.map(function(j){return item(n++,j[0],href(j[1]),'')}).join('')))}
else{stat.classList.remove('lz-err');s.loadText();var seenU={},r=s.search(t,60).filter(function(it){var k=it.u+'|'+it.t;if(seenU[k]||seenU[it.u])return false;seenU[k]=seenU[it.u]=1;return true}).slice(0,40),g={},order=['Pages','Spells','Items','Wiki'];
r.forEach(function(it){(g[kind(it)]=g[kind(it)]||[]).push(it)});
order.forEach(function(k){if(g[k])h.push(group(k,g[k].slice(0,k==='Pages'?14:8).map(function(it){return item(n++,it.t,href(it.u,it.e),(it.fz?'close match · ':'')+it.s,it.e)}).join('')))});
stat.textContent=n?(n+' result'+(n>1?'s':'')+(s.full()?'':' (titles; full text still loading)')):'No matches for “'+t+'”'+(s.full()?'':' in titles yet; full text still loading…')}}
list.innerHTML=h.join('');opts=[].slice.call(list.querySelectorAll('[role=option]'));setAct(keep===1&&t===lastQ?Math.min(cur,opts.length-1):(t.length>=2&&opts.length?0:-1));lastQ=t}
function open(from){build();if(pal.open){inp.focus();inp.select();return}opener=from||document.activeElement;var sq=document.getElementById('q');
inp.value=(sq&&sq.value&&document.activeElement===sq)?sq.value:'';if(sq)sq.blur();var r=document.getElementById('qres');if(r)r.hidden=true;
if(S())S().load();pal.showModal();render();inp.focus()}
function close(){if(pal&&pal.open)pal.close()}
var keys=null;
function keysOpen(from){if(!keys){keys=document.createElement('dialog');keys.className='ux-keys';keys.setAttribute('aria-labelledby','ux-keys-h');
var row=function(k,d){return '<tr><th scope="row">'+k+'</th><td>'+d+'</td></tr>'};
keys.innerHTML='<div class="ux-sheet-hd"><h2 id="ux-keys-h">Keyboard shortcuts</h2><button type="button" class="ux-sheet-x" aria-label="Close">&#10005;</button></div><table class="ux-keys-t"><tbody>'+
row('<kbd>Ctrl</kbd> <kbd>K</kbd> or <kbd>/</kbd>','Quick jump: search pages, classes, zones, items; recently viewed')+row('<kbd>?</kbd>','Show this list')+row('<kbd>Esc</kbd>','Close a dialog, menu or search results')+
row('<kbd>&uarr;</kbd> <kbd>&darr;</kbd> <kbd>Enter</kbd>','Move through results and open one')+row('<kbd>Tab</kbd> then <kbd>Enter</kbd> on a table header','Sort that column (press again to reverse)')+
Object.keys(GO).map(function(k){var j=JUMP.filter(function(x){return x[1]===GO[k]})[0];return row('<kbd>g</kbd> <kbd>'+k+'</kbd>','Go to '+esc(j?j[0]:GO[k]))}).join('')+
row('<kbd>t</kbd>','Back to top')+'</tbody></table><p class="dim ux-keys-n">Shortcuts are ignored while you type in a box. On touch screens use the search button in the header.</p>';
document.body.appendChild(keys);var x=keys.querySelector('.ux-sheet-x');x.addEventListener('click',function(){keys.close()});
keys.addEventListener('click',function(e){if(e.target===keys)keys.close()});
keys.addEventListener('keydown',function(e){if(e.key==='Tab'){e.preventDefault();x.focus()}});
keys.addEventListener('close',function(){if(keys._op&&keys._op.focus)keys._op.focus({preventScroll:true})})}
if(keys.open)return;keys._op=from||document.activeElement;keys.showModal();keys.querySelector('.ux-sheet-x').focus()}
window.MNM_UX_PALI={open:open,close:close,isOpen:function(){return !!(pal&&pal.open)},keys:keysOpen};
})();
