(function(){var M=window.MNM_CREF,root=document.documentElement.getAttribute('data-root')||'';if(!M)return;
var sel=document.getElementById('mnm-class');function cur(){var v;try{v=localStorage.getItem('mnm-class')}catch(e){}return (sel&&sel.value)||v||'Shaman'}
var S=M.Shaman,kinds=['overview','spells','leveling','gear','quickinfo'];
function rel(u){return root+u.replace(/^\//,'')}
function relink(){var c=cur(),T=M[c]||S;
 document.querySelectorAll('nav a, .box.nav a, a[data-cg]').forEach(function(a){var k=a.getAttribute('data-cg');
  if(!k){var h=a.getAttribute('href')||'';kinds.forEach(function(x){if(h===rel(S[x]))k=x});if(!k)return;a.setAttribute('data-cg',k);}
  a.setAttribute('href',rel(T[k]));});}
relink();
var mk=document.querySelector('.cpage'),here=null;
if(!mk){var p=location.pathname;kinds.forEach(function(x){if(S[x]!=='/index.html#mnm-quickinfo'&&p.slice(-S[x].length)===S[x])here={k:x,c:'Shaman'}})}else here={k:mk.getAttribute('data-cpage'),c:mk.getAttribute('data-ccls')};
if(here&&here.c!==cur()&&M[cur()]){var b=document.createElement('div');b.className='call note';b.innerHTML='<p>This page is for <b>'+here.c+'</b>. Your class picker is set to <b>'+cur()+'</b>: <a href="'+rel(M[cur()][here.k])+'">open the '+cur()+' version</a>.</p>';var m=document.querySelector('main.main');if(m)m.insertBefore(b,m.firstChild);}
if(sel)sel.addEventListener('change',function(){relink();if(here&&M[sel.value]){var t=M[sel.value][here.k];if(t)location.href=rel(t);}});})();
