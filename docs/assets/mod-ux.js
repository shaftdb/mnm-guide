// UX pass 1: keeps --hdr-h in sync with the sticky header (desktop sticky offsets / scroll padding) and, on narrow
// screens, swaps the tall header for a compact fixed mini bar (logo mark, search, menu, Setup) once it scrolls away.
(function(){
var top=document.querySelector('.top'),topin=top&&top.querySelector('.topin'),de=document.documentElement,body=document.body;
if(!top||!topin)return;
var narrow=window.matchMedia('(max-width:800px)'),reduce=window.matchMedia('(prefers-reduced-motion:reduce)');
var btn=document.createElement('button');btn.type='button';btn.className='ux-setup';
btn.setAttribute('aria-label','Back to top: class, race, start and level setup');btn.title='Back to top (class / level setup)';
btn.innerHTML='<span aria-hidden="true">&#9881;</span> Setup';
topin.appendChild(btn);
btn.addEventListener('click',function(){body.classList.remove('navopen');window.scrollTo({top:0,behavior:reduce.matches?'auto':'smooth'});
  var c=document.getElementById('mnm-class');if(c)setTimeout(function(){c.focus({preventScroll:true})},reduce.matches?0:400)});
var full=0;
function measure(){if(!body.classList.contains('ux-mini')){top.style.minHeight='';full=top.offsetHeight}
  de.style.setProperty('--hdr-h',(narrow.matches?Math.min(full,72):full)+'px')}
function onScroll(){if(!narrow.matches){if(body.classList.contains('ux-mini')){body.classList.remove('ux-mini');top.style.minHeight='';measure()}return}
  var mini=body.classList.contains('ux-mini'),y=window.scrollY,cut=full-20;
  if(!mini&&y>cut){top.style.minHeight=full+'px';body.classList.add('ux-mini');de.style.setProperty('--mini-h',topin.offsetHeight+'px')}
  else if(mini&&y<cut-40){body.classList.remove('ux-mini');top.style.minHeight=''}}
measure();onScroll();
window.addEventListener('scroll',onScroll,{passive:true});
window.addEventListener('resize',function(){measure();onScroll()});
if(window.ResizeObserver)new ResizeObserver(function(){measure()}).observe(top);
})();
