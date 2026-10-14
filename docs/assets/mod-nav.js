(function(){var gs=[].slice.call(document.querySelectorAll('.mainnav .ng'));
function set(g,o){g.classList.toggle('open',o);g.querySelector('.ngb').setAttribute('aria-expanded',o?'true':'false');}
gs.forEach(function(g){var b=g.querySelector('.ngb');
 b.addEventListener('click',function(e){e.stopPropagation();var o=!g.classList.contains('open');gs.forEach(function(x){if(x!==g)set(x,false)});set(g,o);if(o&&e.detail===0){var a=g.querySelector('.ngm a');if(a)a.focus();}});
 g.addEventListener('keydown',function(e){var as=[].slice.call(g.querySelectorAll('.ngm a')),i=as.indexOf(document.activeElement);
  if(e.key==='Escape'){set(g,false);b.focus();}
  else if(e.key==='ArrowDown'){e.preventDefault();set(g,true);(as[i+1]||as[0]).focus();}
  else if(e.key==='ArrowUp'){e.preventDefault();set(g,true);(as[i-1]||as[as.length-1]).focus();}});
 g.addEventListener('focusout',function(e){if(!g.contains(e.relatedTarget)&&window.innerWidth>800)set(g,false);});});
document.addEventListener('click',function(){if(window.innerWidth>800)gs.forEach(function(g){set(g,false)});});
var on=document.querySelector('.mainnav .ng.on');if(on&&window.innerWidth<=800)set(on,true);})();
