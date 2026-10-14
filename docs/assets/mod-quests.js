(function(){var m=document.getElementById('qh-mine'),k=document.getElementById('qh-kind');if(!m)return;
function go(){var c=(document.getElementById('mnm-class')||{}).value||'';document.querySelectorAll('details.qh').forEach(function(d){var cl=d.getAttribute('data-cls'),ks=' '+d.getAttribute('data-k')+' ';
 d.classList.toggle('qhide',(m.checked&&cl&&('|'+cl+'|').indexOf('|'+c+'|')<0)||(k.value&&ks.indexOf(' '+k.value+' ')<0));});}
m.onchange=go;k.onchange=go;var s=document.getElementById('mnm-class');if(s)s.addEventListener('change',function(){setTimeout(go,0)});go();})();
