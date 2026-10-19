// Start-city routes: mirror the top-bar Start / Race / Class pickers onto <html data-sc / data-scr / data-scc>.
// mod-startcity.css shows only the matching start-city block and hides lines meant for other classes or races.
(function(){
var H=document.documentElement;
function slug(s){return String(s||'').toLowerCase().replace(/'/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'')}
function v(id){var e=document.getElementById(id);return e&&e.value?e.value:''}
function setA(k,val){if(val)H.setAttribute(k,slug(val));else H.removeAttribute(k)}
function sync(){var g=window.MNM_CHARGEN&&window.MNM_CHARGEN.get?window.MNM_CHARGEN.get():{};
  setA('data-sc',v('mnm-city')||g.city);setA('data-scr',v('mnm-race')||g.race);setA('data-scc',v('mnm-class')||g.cls);}
sync();
['mnm-city','mnm-race','mnm-class'].forEach(function(id){var e=document.getElementById(id);if(e)e.addEventListener('change',function(){setTimeout(sync,0)})});
document.addEventListener('change',function(e){if(e.target&&/^mnm-(city|race|class)$/.test(e.target.id))setTimeout(sync,0)},true);
window.addEventListener('mnm-chargen',function(){setTimeout(sync,0)});document.addEventListener('mnm-chargen',function(){setTimeout(sync,0)});
window.addEventListener('pageshow',function(){setTimeout(sync,0)});
// open a linked quest-helper entry (#q-...)
function openHash(){var h=location.hash;if(!/^#q-/.test(h))return;var d=document.getElementById(h.slice(1));if(d&&d.tagName==='DETAILS'){d.open=true;d.scrollIntoView()}}
openHash();window.addEventListener('hashchange',openHash);
window.MNM_SC={sync:sync};
})();
