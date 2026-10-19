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
// ---------------------------------------------------------------- UX pass 2
(function(){
var narrowQ=window.matchMedia('(max-width:640px)'),phoneQ=window.matchMedia('(max-width:800px)');
// ---- "My setup": one-row summary of the top-bar pickers on phones; tap to open the full pickers
var rb=document.getElementById('mnm-rangebar'),rin=rb&&rb.querySelector('.rangebar-in');
if(rb&&rin){
  rin.id=rin.id||'ux-rb-in';
  var sb=document.createElement('button');sb.type='button';sb.className='ux-mysetup';sb.setAttribute('aria-expanded','false');sb.setAttribute('aria-controls',rin.id);
  sb.innerHTML='<span class="ux-ms-l">My setup</span><span class="ux-ms-v"></span><span class="ux-ms-c" aria-hidden="true">&#9662;</span>';
  rb.insertBefore(sb,rin);
  var val=function(id,txt){var e=document.getElementById(id);if(!e)return '';if(txt){var o=e.selectedOptions&&e.selectedOptions[0];return o?o.textContent.replace(/\s*\((not for|unverified)[^)]*\)\s*$/,''):''}return e.value||''};
  var sum=function(){var ts=document.getElementById('mnm-ts-sum'),parts=[val('mnm-class'),val('mnm-race'),val('mnm-city'),val('mnm-range',1),ts?ts.textContent:''].filter(Boolean);
    sb.querySelector('.ux-ms-v').textContent=parts.join(' · ');sb.title='My setup: '+parts.join(', ')+'. Tap to change.'};
  var setOpen=function(on){rb.classList.toggle('ux-open',on);sb.setAttribute('aria-expanded',on?'true':'false')};
  sb.addEventListener('click',function(){setOpen(!rb.classList.contains('ux-open'))});
  document.addEventListener('change',function(e){if(e.target&&e.target.closest&&e.target.closest('#mnm-rangebar'))setTimeout(sum,0)},true);
  var tsum=document.getElementById('mnm-ts-sum');if(tsum&&window.MutationObserver)new MutationObserver(sum).observe(tsum,{childList:true,characterData:true,subtree:true});
  sum();setTimeout(sum,0);window.addEventListener('load',sum);
  window.MNM_UX_SETUP=setOpen;
  // 'Valid starts' line behind a disclosure on phones
  var cv=document.getElementById('cg-valid');
  if(cv){cv.classList.add('ux-cgv');var vb=document.createElement('button');vb.type='button';vb.className='ux-cgv-btn';vb.setAttribute('aria-expanded','false');vb.setAttribute('aria-controls','cg-valid');
    vb.innerHTML='Valid starts for this race <span aria-hidden="true">&#9662;</span>';cv.parentNode.insertBefore(vb,cv);
    vb.addEventListener('click',function(){var on=!rb.classList.contains('ux-cgv-open');rb.classList.toggle('ux-cgv-open',on);vb.setAttribute('aria-expanded',on?'true':'false')});}
  // pass-1 mini-bar Setup button: also open the pickers
  var mb=document.querySelector('.ux-setup');if(mb)mb.addEventListener('click',function(){setOpen(true)});
}
// ---- "On this page": sticky button on phones that opens a sheet of the page's sections
var links=[].slice.call(document.querySelectorAll('.right .box.toc a[href^="#"]')).map(function(a){return [a.getAttribute('href'),a.textContent]});
if(links.length<2){links=[].slice.call(document.querySelectorAll('main.main h2[id]')).map(function(h){return ['#'+h.id,h.textContent]});if(links.length<3)links=[]}
if(links.length&&window.HTMLDialogElement){
  var ob=document.createElement('button');ob.type='button';ob.className='ux-otp';ob.setAttribute('aria-haspopup','dialog');ob.innerHTML='<span aria-hidden="true">&#9776;</span> On this page';
  var dl=document.createElement('dialog');dl.className='ux-sheet';dl.setAttribute('aria-labelledby','ux-sheet-h');
  dl.innerHTML='<div class="ux-sheet-hd"><h2 id="ux-sheet-h">On this page</h2><button type="button" class="ux-sheet-x" aria-label="Close">&#10005;</button></div><ul>'+
    links.map(function(l){var e=document.createElement('span'),d=document.createElement('textarea');d.innerHTML=l[1];e.textContent=d.value;return '<li><a href="'+l[0].replace(/"/g,'&quot;')+'">'+e.innerHTML+'</a></li>'}).join('')+'</ul>';
  document.body.appendChild(ob);document.body.appendChild(dl);document.body.classList.add('ux-has-otp');
  ob.addEventListener('click',function(){dl.showModal();var a=dl.querySelector('a');if(a)a.focus()});
  dl.querySelector('.ux-sheet-x').addEventListener('click',function(){dl.close()});
  dl.addEventListener('click',function(e){if(e.target===dl)dl.close();var a=e.target.closest('a');if(a){dl.close();var id=decodeURIComponent(a.getAttribute('href').slice(1)),t=document.getElementById(id);
    // open the tab holding the target (class guides), then jump
    var p=t&&t.closest('.tabpane');if(p&&!p.classList.contains('on')){var b=document.querySelector('.tab[data-tab="'+p.id+'"]');if(b)b.click()}}});
  dl.addEventListener('close',function(){ob.focus({preventScroll:true})});
}
})();
