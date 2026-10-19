(function(){var K='mnm-halloween',h=document.documentElement;
var b=document.createElement('button');b.type='button';b.className='hw-toggle';
function lbl(){var on=h.classList.contains('halloween');b.textContent=on?'🎃 Irem theme: on':'Irem theme: off';b.setAttribute('aria-pressed',on?'true':'false');b.title='Toggle the seasonal Caves of Irem theme'}
b.onclick=function(){var on=!h.classList.contains('halloween');h.classList.toggle('halloween',on);try{localStorage.setItem(K,on?'on':'off')}catch(e){}lbl()};
lbl();document.body.appendChild(b);})();
