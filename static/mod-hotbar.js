// Hotbar planner (/hotbar.html). Data: window.MNM_HB (hotbar-data.js), lazily window.MNM_HBI (hotbar-items.js) + MNM_MKTI (market-items.js).
// Reads the shared top-bar pickers (#mnm-class, #mnm-race, #mnm-range) and listens for their changes; never edits picker code.
// State: localStorage 'mnm-hotbar' (per class); share link #hb=<deflate-raw base64url>; JSON import/export; undo stack.
(function(){
'use strict';
var H=window.MNM_HB,app=document.getElementById('hb-app');if(!H||!app)return;
var root=document.documentElement.getAttribute('data-root')||'',R=window.MNM_RANGES||{};
var KEY='mnm-hotbar',BARS={ab:'Ability bar',hb:'Hotbar',au:'Aura bar'},AB_N=10,HB_N=12,AU_N=10;
var KIND={s:'Spell',i:'Innate ability',a:'Aura',k:'Skill',t:'Trait ability',c:'Clicky item',m:'Macro'};
var DEFKEYS={ab:['1','2','3','4','5','6','7','8','9','0'],hb:['⇧1','⇧2','⇧3','⇧4','⇧5','⇧6','⇧7','⇧8','⇧9','⇧0','⇧-','⇧='],au:['⌃1','⌃2','⌃3','⌃4','⌃5','⌃6','⌃7','⌃8','⌃9','⌃0']};
var KEYNAME=function(k){return String(k||'').replace('⇧','Shift+').replace('⌃','Ctrl+')};
function $(id){return document.getElementById(id)}
function e(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function lsGet(k){try{return localStorage.getItem(k)}catch(x){return null}}
function lsPut(k,v){try{localStorage.setItem(k,v)}catch(x){}}
function clone(o){return JSON.parse(JSON.stringify(o))}
var CATL={};H.cats.forEach(function(c){CATL[c[0]]=c[1]});
// ---------------------------------------------------------------- pickers (read only)
var selC=$('mnm-class'),selR=$('mnm-race'),selL=$('mnm-range');
function cls(){var v=(selC&&selC.value)||lsGet('mnm-class');return H.classes[v]?v:(R.defaultClass||'Fighter')}
function race(){var v=(selR&&selR.value)||lsGet('mnm-race')||'';return H.races[v]?v:''}
function band(){var v=(selL&&selL.value)||lsGet('mnm-range')||R.default||'11-15';var b=v.split('-').map(Number);return b.length===2&&b[0]?b:[11,15]}
// ---------------------------------------------------------------- state
var S=load();
function blankLayout(n,k){return{n:n,k:k,ab:new Array(AB_N).fill(null),hb:[],au:new Array(AU_N).fill(null),keys:{ab:DEFKEYS.ab.slice(),hb:[],au:DEFKEYS.au.slice()},rot:'',notes:'',why:{}}}
function load(){var s=null;try{s=JSON.parse(lsGet(KEY)||'null')}catch(x){}
  if(!s||s.v!==1)s={v:1,prefs:{},cls:{},macros:[]};
  s.prefs=Object.assign({size:48,strict:true,pages:2,sheet:false,future:false},s.prefs||{});s.cls=s.cls||{};s.macros=s.macros||[];return s}
function save(){lsPut(KEY,JSON.stringify(S))}
function pages(){return Math.max(1,Math.min(10,+S.prefs.pages||2))}
function fixLayout(L){L.ab=(L.ab||[]).slice(0,AB_N);while(L.ab.length<AB_N)L.ab.push(null);L.au=(L.au||[]).slice(0,AU_N);while(L.au.length<AU_N)L.au.push(null);
  L.hb=L.hb||[];L.keys=L.keys||{};L.keys.ab=L.keys.ab||DEFKEYS.ab.slice();L.keys.au=L.keys.au||DEFKEYS.au.slice();L.keys.hb=L.keys.hb||[];
  for(var p=0;p<pages();p++){L.hb[p]=(L.hb[p]||[]).slice(0,HB_N);while(L.hb[p].length<HB_N)L.hb[p].push(null);if(!L.keys.hb[p])L.keys.hb[p]=p===0?DEFKEYS.hb.slice():new Array(HB_N).fill('')}
  L.why=L.why||{};return L}
function CS(){var c=cls();if(!S.cls[c]){var o={cur:'solo',L:{},gear:{},build:0,level:null};
    [['solo','Solo'],['group','Group'],['raid','Raid']].forEach(function(x){o.L[x[0]]=blankLayout(x[1],x[0])});S.cls[c]=o;
    ['solo','group','raid'].forEach(function(k){applySuggest(o.L[k],k)});save()}
  var o=S.cls[c];if(!o.L[o.cur])o.cur=Object.keys(o.L)[0];Object.keys(o.L).forEach(function(k){fixLayout(o.L[k])});o.gear=o.gear||{};return o}
function LY(){var o=CS();return o.L[o.cur]}
function level(){var b=band(),o=CS(),l=+o.level;if(!l||l<b[0]||l>b[1])l=b[1];return l}
// ---------------------------------------------------------------- undo
var undo=[];
function snap(){undo.push(JSON.stringify({c:cls(),s:S.cls[cls()],m:S.macros}));if(undo.length>60)undo.shift();$('hb-undo').disabled=false}
function doUndo(){var u=undo.pop();if(!u){msg('Nothing to undo.');return}var x=JSON.parse(u);if(x.all){S=JSON.parse(x.all)}else{if(x.s)S.cls[x.c]=x.s;else delete S.cls[x.c];S.macros=x.m}save();$('hb-undo').disabled=!undo.length;msg('Undone.');render()}
// ---------------------------------------------------------------- entries
function C(){return H.classes[cls()]}
function tpicks(){var r=race();return (C().tpick||[]).map(function(p){return p[1][r]||p[0]})}
function rcode(){var r=H.races[race()];return r?r.code:''}
function spellOf(n){var sp=C().spells;for(var i=0;i<sp.length;i++)if(sp[i][0]===n)return sp[i];return null}
function traitOf(n){for(var i=0;i<H.traits.length;i++)if(H.traits[i][0]===n)return H.traits[i];return null}
function clickyOf(n){for(var i=0;i<H.clicky.length;i++)if(H.clicky[i][0]===n)return H.clicky[i];return null}
function isAuraEntry(en){return en&&(en.t==='a'||(en.t==='t'&&(en.n==='Hide'||en.n==='Sneak'))||((en.t==='s'||en.t==='i')&&(en.n==='Hide'||en.n==='Sneak')))}
function fits(bar,en){if(!en)return true;if(!S.prefs.strict)return true;
  if(bar==='au')return isAuraEntry(en);
  if(bar==='ab')return (en.t==='s'||en.t==='i')&&!isAuraEntry(en);
  return (en.t==='k'||en.t==='t'||en.t==='c'||en.t==='m')&&!isAuraEntry(en)}
function whyNot(bar,en){if(bar==='ab')return 'Only memorized spells and abilities go on the ability bar (official New Player Guide). Turn off "M&M bar rules" below to place anything anywhere.';
  if(bar==='au')return 'The aura bar holds auras and Hide/Sneak (patch 0.20.25.0).';
  return 'The hotbar holds skills, trait abilities, macros and clicky items; spells and abilities must be memorized on the ability bar (official New Player Guide).'}
function bestBar(en){return isAuraEntry(en)?'au':(en.t==='s'||en.t==='i')?'ab':'hb'}
function entryLevel(en){if(en.t==='s'||en.t==='i'||en.t==='a'){var sp=spellOf(en.n);return sp?sp[1]:0}if(en.t==='k'){var k=C().skills.filter(function(x){return x[0]===en.n})[0];return k?k[1]:0}return 0}
function valid(en){if(!en)return false;if(en.t==='s'||en.t==='i'||en.t==='a')return !!spellOf(en.n);if(en.t==='t')return !!traitOf(en.n);if(en.t==='c')return !!clickyOf(en.n);if(en.t==='k')return C().skills.some(function(x){return x[0]===en.n});return en.t==='m'}
function abbr(n){var w=String(n).replace(/[^A-Za-z0-9' ]/g,' ').split(/\s+/).filter(Boolean);var r=/^(I|II|III|IV|V|VI|VII|VIII|IX|X)$/;var last=w.length>1&&r.test(w[w.length-1])?w.pop():'';
  return (w.length===1?w[0].slice(0,2):w.slice(0,2).map(function(x){return x[0]}).join('')).toUpperCase()+(last?'<small>'+last+'</small>':'')}
function tipHtml(en){var t='<b>'+e(en.n)+'</b> <span class="hb-tk">'+e(KIND[en.t]||'')+'</span>';
  if(en.t==='s'||en.t==='i'||en.t==='a'){var sp=spellOf(en.n);if(sp)t+='<div>Level '+(sp[1]||'? (not on wiki)')+' · Cost: '+e(sp[2]==='Innate'?'innate (no mana listed)':sp[2]?(isNaN(+sp[2])?sp[2]:sp[2]+' mana'):'not listed')+'</div><div>Source: '+e(sp[3]||'not listed')+(sp[4]?' · school '+e(sp[4]):'')+' (wiki '+e(cls())+' spell list)</div><div class="hb-td">'+e(sp[5]||'No description on the wiki.')+'</div>'+(sp[7].length?'<div class="hb-tc">Tags (keyword match): '+sp[7].map(function(c){return e(CATL[c])}).join(', ')+'</div>':'')}
  else if(en.t==='t'){var tr=traitOf(en.n);if(tr)t+='<div>'+e(tr[4])+' · race '+e(tr[1])+' · class '+e(tr[2])+'</div><div class="hb-td">'+e(tr[3])+'</div><div>Source: wiki Template:Traits</div>'}
  else if(en.t==='c'){var ci=clickyOf(en.n);if(ci)t+='<div>Slot '+e(ci[2]||'?')+'</div><div class="hb-td">'+e(ci[3])+'</div><div>Source: wiki item page</div>'}
  else if(en.t==='k')t+='<div>Skill from the Skills tab (wiki class skill list). Whether this skill is a clickable button in game is not documented <span class="badge unc">unverified</span>.</div>';
  else if(en.t==='m')t+='<div><code>'+e(en.c||'')+'</code></div><div>Your macro (runs slash commands).</div>';
  return t}
// ---------------------------------------------------------------- suggestions (STRATEGY; only real spells from the class list)
var TPL={tank:{solo:['nuke','nuke','threat','dot','snare','heal','stun','buff','debuff','buff'],group:['threat','threat','nuke','stun','debuff','heal','buff','buff','snare','cure'],raid:['threat','threat','stun','debuff','buff','buff','heal','cure','nuke','rez']},
 healer:{solo:['nuke','dot','heal','snare','slow','buff','buff','pet','debuff','cure'],group:['heal','heal','heal','cure','slow','buff','buff','rez','debuff','nuke'],raid:['heal','heal','heal','cure','cure','buff','buff','rez','slow','debuff']},
 cc:{solo:['nuke','dot','mez','slow','snare','pet','buff','debuff','heal','stun'],group:['mez','mez','slow','debuff','stun','buff','buff','nuke','snare','cure'],raid:['mez','slow','debuff','buff','buff','buff','stun','cure','nuke','heal']},
 pet:{solo:['pet','nuke','dot','snare','heal','buff','debuff','slow','stun','cure'],group:['pet','dot','nuke','slow','debuff','snare','buff','heal','stun','cure'],raid:['pet','dot','nuke','debuff','buff','buff','slow','cure','heal','snare']},
 dps:{solo:['nuke','nuke','dot','snare','stun','heal','buff','buff','debuff','slow'],group:['nuke','nuke','nuke','dot','stun','debuff','buff','buff','snare','heal'],raid:['nuke','nuke','dot','debuff','buff','buff','stun','cure','heal','snare']}};
var ROLEWHY={tank:{solo:'Solo tank: damage first so pulls die fast, then threat and survival.',group:'Group tank: holding threat comes first, then interrupts and debuffs.',raid:'Raid tank: threat and interrupts, plus buffs and a cure for long fights.'},
 healer:{solo:'Solo healer: you need damage to kill, so it comes first, with a heal and a snare to stay safe.',group:'Group healer: heals first, then cures, slows and buffs.',raid:'Raid healer: several heal lines and cures; damage last.'},
 cc:{solo:'Solo crowd control: damage plus mez/slow to handle adds.',group:'Group crowd control: mez and slow first, damage last.',raid:'Raid support: control, slows and buffs.'},
 pet:{solo:'Pet class: keep the pet spell memorized, then damage and a snare.',group:'Pet class in a group: pet, damage over time and debuffs.',raid:'Pet class in a raid: pet, damage and buffs.'},
 dps:{solo:'Damage dealer solo: damage first, then a snare and a self-heal if you have one.',group:'Damage dealer in a group: damage first, then interrupts and debuffs.',raid:'Damage dealer in a raid: damage, debuffs, buffs and a cure.'}};
function lineKey(n){return n.replace(/\s+(I|II|III|IV|V|VI|VII|VIII|IX|X)$/,'').replace(/^(Minor|Lesser|Greater|Major|Superior)\s+/,'')}
function suggest(kind,lvl,cz,rc){var c=H.classes[cz],rk=c.rk,tpl=(TPL[rk]||TPL.dps)[kind]||TPL[rk].solo,avail={},out={ab:[],au:[],hb:[],why:{},rot:[]};
  c.spells.forEach(function(sp){if(!sp[1]||sp[1]>lvl)return;var k=lineKey(sp[0]);if(!avail[k]||avail[k][1]<sp[1])avail[k]=sp});
  var list=Object.keys(avail).map(function(k){return avail[k]}).sort(function(a,b){return b[1]-a[1]||a[0].localeCompare(b[0])}),used={};
  tpl.forEach(function(cat){if(out.ab.length>=AB_N)return;var sp=list.filter(function(s){return !used[s[0]]&&!s[8]&&s[7].indexOf(cat)>=0})[0];if(!sp)return;used[sp[0]]=1;
    var i=out.ab.length;out.ab.push({t:sp[6]==='i'?'i':'s',n:sp[0]});out.why['ab:'+i]=CATL[cat]+' (level '+sp[1]+'): '+sp[5].split(/(?<=\.)\s/)[0];out.rot.push(DEFKEYS.ab[i]+' '+sp[0]+' — '+CATL[cat])});
  list.forEach(function(sp){if(out.ab.length>=AB_N||used[sp[0]]||sp[8])return;used[sp[0]]=1;var i=out.ab.length;out.ab.push({t:sp[6]==='i'?'i':'s',n:sp[0]});out.why['ab:'+i]='Newest ability at your level that the role rules did not pick (level '+sp[1]+').'});
  list.filter(function(s){return s[8]}).slice(0,AU_N).forEach(function(sp,i){out.au.push({t:sp[6],n:sp[0]});out.why['au:'+i]='Aura bar: '+sp[0]+' (level '+sp[1]+'). Auras, Hide and Sneak sit on the aura bar (patch 0.20.25.0).'});
  H.traits.forEach(function(t){if(t[4]!=='Racial Combat Abilities')return;if(rc&&(t[1]+',').indexOf(rc)<0)return;if(!rc)return;
    if(t[0]==='Hide'||t[0]==='Sneak'){if(out.au.length<AU_N){out.why['au:'+out.au.length]='Your racial '+t[0]+' sits on the aura bar (patch 0.20.25.0).';out.au.push({t:'t',n:t[0]})}return}
    out.why['hb:0:'+out.hb.length]='Your racial active ('+race()+'); trait abilities are hotbar skills (patch 0.20.25.0).';out.hb.push({t:'t',n:t[0]})});
  tpicks().forEach(function(p){var t=traitOf(p);if(!t||t[4]==='Racial Combat Abilities'||out.hb.some(function(x){return x.n===p}))return;
    if(t[1]!=='Any'&&rc&&t[1].indexOf(rc)<0)return;out.why['hb:0:'+out.hb.length]='Active of '+p+', this Codex\'s trait pick for '+cz+' (Character creation). Only if you took that trait.';out.hb.push({t:'t',n:p})});
  if(kind==='solo'){out.why['hb:0:'+out.hb.length]='/corpse drags your corpse (official New Player Guide).';out.hb.push({t:'m',n:'Corpse',c:'/corpse'})}
  else{out.why['hb:0:'+out.hb.length]='/consent group lets your group drag your corpse (patch 0.20.25.0).';out.hb.push({t:'m',n:'Consent group',c:'/consent group'})}
  out.role=(ROLEWHY[rk]||ROLEWHY.dps)[kind]||'';out.lvl=lvl;return out}
function applySuggest(L,kind){var k=(kind==='group'||kind==='raid')?kind:'solo',cz=cls(),c=H.classes[cz],g=suggest(k,level(),cz,rcode());fixLayout(L);
  L.ab=g.ab.concat(new Array(AB_N).fill(null)).slice(0,AB_N);L.au=g.au.concat(new Array(AU_N).fill(null)).slice(0,AU_N);L.hb[0]=g.hb.concat(new Array(HB_N).fill(null)).slice(0,HB_N);
  for(var p=1;p<L.hb.length;p++)L.hb[p]=new Array(HB_N).fill(null);
  L.why=g.why;L.role=g.role;L.slvl=g.lvl;L.rot=g.rot.join('\n');L.notes=(k==='solo'?c.nsolo:c.ngroup)||'';L.nsrc=1}
// ---------------------------------------------------------------- rendering
var armed=null,keysMode=false;
function slotEntry(id){var L=LY(),p=id.split(':');if(p[0]==='hb')return (L.hb[+p[1]]||[])[+p[2]]||null;return L[p[0]][+p[1]]||null}
function setSlot(id,en){var L=LY(),p=id.split(':');if(p[0]==='hb')L.hb[+p[1]][+p[2]]=en;else L[p[0]][+p[1]]=en}
function keyOf(id){var L=LY(),p=id.split(':');return p[0]==='hb'?(L.keys.hb[+p[1]]||[])[+p[2]]||'':L.keys[p[0]][+p[1]]||''}
function setKey(id,v){var L=LY(),p=id.split(':');if(p[0]==='hb')L.keys.hb[+p[1]][+p[2]]=v;else L.keys[p[0]][+p[1]]=v}
function slotHtml(id,label){var en=slotEntry(id),k=keyOf(id),ok=en&&valid(en),lv=ok?entryLevel(en):0,hi=ok&&lv>level(),why=LY().why[id];
  var cl='hb-slot'+(en?' full k-'+en.t:'')+(en&&!ok?' bad':'')+(hi?' hi':'')+(armed&&!fits(id.split(':')[0],armed.e)?' nofit':'');
  var al=label+', key '+(KEYNAME(k)||'none')+', '+(en?en.n+(en&&!ok?' (not in this class list)':'')+(hi?' (above your level)':''):'empty');
  return '<div class="hb-cell"><button type="button" class="'+cl+'" data-s="'+id+'"'+(en?' draggable="true"':'')+' aria-label="'+e(al)+'"'+(why?' data-why="'+e(why)+'"':'')+'>'+
    '<span class="hb-ic">'+(en?abbr(en.n):'')+'</span><span class="hb-n">'+(en?e(en.n):'<span class="dim">empty</span>')+'</span>'+(keysMode?'':'<span class="hb-k">'+e(k)+'</span>')+'</button>'+
    (keysMode?'<input class="hb-kin" data-s="'+id+'" value="'+e(k)+'" maxlength="8" aria-label="Keybind for '+e(label)+'">':'')+'</div>'}
function barHtml(bar,n,title,note,page){var emp=true;for(var j=0;j<n;j++){if(slotEntry(page!=null?bar+':'+page+':'+j:bar+':'+j))emp=false}
  var h='<div class="hb-bar hb-'+bar+(emp&&(bar==='au'||page>0)?' empty':'')+'" data-bar="'+bar+'"'+(page!=null?' data-page="'+page+'"':'')+'><div class="hb-bt">'+title+(note?' <span class="hb-bn">'+note+'</span>':'')+'</div><div class="hb-row" role="group" aria-label="'+e(title.replace(/<[^>]+>/g,''))+'">';
  for(var i=0;i<n;i++){var id=page!=null?bar+':'+page+':'+i:bar+':'+i;h+=slotHtml(id,title.replace(/<[^>]+>/g,'')+' slot '+(i+1))}return h+'</div></div>'}
function renderBars(){var L=LY(),h=barHtml('ab',AB_N,'Ability bar','10 memorized <span class="badge fact">fact</span>');
  for(var p=0;p<pages();p++)h+=barHtml('hb',HB_N,'Hotbar'+(pages()>1?' page '+(p+1):''),p===0?'12 keys <span class="badge fact">fact</span>':'pages <span class="badge unc">unverified</span>',p);
  h+=barHtml('au',AU_N,'Aura bar','Ctrl+1–0 <span class="badge fact">fact</span>');
  $('hb-bars').innerHTML=h;
  $('hb-ftitle').textContent=cls()+' · '+L.n+' · level '+level()+(race()?' · '+race():'');
  var rot=(L.rot||'').split('\n').map(function(x){return x.trim()}).filter(Boolean);
  if(!rot.length)rot=L.ab.map(function(en,i){return en?(L.keys.ab[i]||'')+' '+en.n:null}).filter(Boolean);
  $('hb-rotlist').innerHTML=rot.length?rot.map(function(x){return '<li>'+e(x)+'</li>'}).join(''):'<li class="dim">Nothing yet: place abilities or write steps.</li>';
  $('hb-notesview').innerHTML=L.notes?e(L.notes).replace(/\n/g,'<br>')+(L.nsrc&&L.notes===(L.k==='solo'?C().nsolo:C().ngroup)?' <span class="badge strat">strategy</span> <span class="dim">(Codex class notes)</span>':''):'<span class="dim">No notes.</span>';
  if(document.activeElement!==$('hb-rot'))$('hb-rot').value=L.rot||'';if(document.activeElement!==$('hb-notes'))$('hb-notes').value=L.notes||'';
  var w=Object.keys(L.why||{}).filter(function(id){return slotEntry(id)});
  $('hb-why').innerHTML=w.length?'<details'+(innerWidth>700?' open':'')+'><summary><span class="badge strat">strategy</span> Why these picks'+(L.slvl?' (suggested at level '+L.slvl+')':'')+'</summary>'+(L.role?'<p>'+e(L.role)+'</p>':'')+'<ul class="tight">'+w.map(function(id){var en=slotEntry(id);return '<li><b>'+e(keyOf(id)||id)+' '+e(en.n)+'</b>: '+e(L.why[id])+'</li>'}).join('')+'</ul><p class="dim">Picked by keyword rules from your class\'s wiki spell list (highest rank you have of each line). Not a tested rotation.</p></details>':''}
function renderLayouts(){var o=CS(),ks=Object.keys(o.L).sort(function(a,b){var r={solo:0,group:1,raid:2};return (r[a]!=null?r[a]:3)-(r[b]!=null?r[b]:3)});
  $('hb-layout').innerHTML=ks.map(function(k){return '<option value="'+e(k)+'"'+(k===o.cur?' selected':'')+'>'+e(o.L[k].n)+(o.L[k].k!=='custom'?'':' (custom)')+'</option>'}).join('');
  if(document.activeElement!==$('hb-lname'))$('hb-lname').value=LY().n;$('hb-del').disabled=LY().k!=='custom'}
function palItems(){var c=C(),lv=level(),rc=rcode(),q=$('hb-q').value.trim().toLowerCase(),kd=$('hb-kind').value,fut=$('hb-future').checked,out=[];
  c.spells.forEach(function(sp){var en={t:sp[6],n:sp[0]};out.push({en:en,lv:sp[1],grp:sp[8]?'a':sp[6],txt:sp[0]+' '+sp[5],lock:sp[1]>lv,cost:sp[2]})});
  c.skills.forEach(function(s){out.push({en:{t:'k',n:s[0]},lv:s[1],grp:'h',txt:s[0]+' skill',lock:s[1]>lv})});
  H.traits.forEach(function(t){var okR=t[1]==='Any'||(rc&&(', '+t[1]+',').indexOf(' '+rc+',')>=0)||(!rc),okC=t[2]==='Any'||(', '+t[2]+',').indexOf(' '+c.code+',')>=0;if(!okR||!okC)return;
    var racial=t[4]==='Racial Combat Abilities';if(racial&&!rc)return;out.push({en:{t:'t',n:t[0]},lv:0,grp:(t[0]==='Hide'||t[0]==='Sneak')?'a':'h',txt:t[0]+' '+t[3]+' trait',note:racial?'your racial':(tpicks().indexOf(t[0])>=0?'Codex trait pick':'if you took this trait')})});
  S.macros.forEach(function(m){out.push({en:{t:'m',n:m.n,c:m.c},lv:0,grp:'h',txt:m.n+' '+m.c+' macro',note:'macro'})});
  var gear=Object.keys(CS().gear).map(function(k){return CS().gear[k]});
  H.clicky.forEach(function(ci){var mine=(' '+ci[1]+' ').indexOf(' '+c.code+' ')>=0;if(!mine)return;var eq=gear.indexOf(ci[0])>=0;if(!eq&&kd!=='h'&&!q)return;out.push({en:{t:'c',n:ci[0]},lv:0,grp:'h',txt:ci[0]+' '+ci[3]+' clicky item',note:eq?'equipped clicky':'clicky item'})});
  return out.filter(function(x){if(kd&&x.grp!==kd)return false;if(!fut&&x.lock)return false;if(q&&x.txt.toLowerCase().indexOf(q)<0)return false;return true})}
var PAL=[];
function renderPalette(){PAL=palItems();var lv=level();var mob=narrow();
  $('hb-palcount').textContent=PAL.length+' shown for '+cls()+' at level '+lv+(race()?' ('+race()+')':'')+'. '+(mob?'Tap an item, then tap a slot.':'Drag onto a slot, or click it then click a slot.');
  $('hb-palette').innerHTML=PAL.map(function(x,i){var en=x.en,on=armed&&!armed.from&&armed.e.t===en.t&&armed.e.n===en.n;
    return '<button type="button" class="hb-pi k-'+en.t+(x.lock?' lock':'')+(on?' armed':'')+'" role="option" aria-selected="'+(on?'true':'false')+'" data-i="'+i+'"'+(x.lock||mob?'':' draggable="true"')+(x.lock?' aria-disabled="true"':'')+
      ' aria-label="'+e(en.n+', '+(KIND[en.t]||'')+(x.lv?', level '+x.lv:'')+(x.cost&&!isNaN(+x.cost)?', '+x.cost+' mana':'')+(x.lock?', above your level':''))+'">'+
      '<span class="hb-ic">'+abbr(en.n)+'</span><span class="hb-pn">'+e(en.n)+'</span><span class="hb-pm">'+(x.lv?'L'+x.lv:'')+(x.cost&&!isNaN(+x.cost)?' · '+e(x.cost)+'m':x.cost==='Innate'?' · innate':'')+(x.note?' · '+e(x.note):'')+'</span></button>'}).join('')||'<p class="dim">Nothing matches.</p>'}
function lvlNote(){var b=band(),l=level();$('hb-level').min=b[0];$('hb-level').max=b[1];$('hb-level').value=l;
  $('hb-lvlnote').textContent='Levels '+b[0]+'–'+b[1]+' from the top bar; abilities above level '+l+' are locked. Change Levels in the top bar for other ranges.'}
function render(){renderLayouts();lvlNote();renderBars();renderPalette();if(!$('hb-sheet').hidden)renderSheet();
  $('hb-pages').value=pages();$('hb-strict').checked=!!S.prefs.strict;$('hb-future').checked=!!S.prefs.future;app.style.setProperty('--hb-sz',(+S.prefs.size||48)+'px');$('hb-size').value=S.prefs.size||48;
  $('hb-keys').setAttribute('aria-pressed',keysMode?'true':'false');app.classList.toggle('hb-armed',!!armed);
  if(armed){var st=document.querySelectorAll('.hb-slot');st.forEach(function(b){b.classList.toggle('nofit',!fits(b.getAttribute('data-s').split(':')[0],armed.e))})}}
function msg(t,bad){var m=$('hb-msg');m.textContent=t;m.classList.toggle('bad',!!bad)}
function narrow(){return window.matchMedia&&matchMedia('(max-width: 600px)').matches}
// ---------------------------------------------------------------- actions
function place(id,en,from){var bar=id.split(':')[0];if(!fits(bar,en)){msg('Can\'t put '+en.n+' on the '+BARS[bar]+'. '+whyNot(bar,en),true);return false}
  if(entryLevel(en)>level()){msg(en.n+' is level '+entryLevel(en)+', above your level '+level()+'.',true);return false}
  snap();var prev=slotEntry(id);
  if(from&&from!==id){if(prev&&!fits(from.split(':')[0],prev)){setSlot(from,null)}else setSlot(from,prev);var L=LY();if(L.why[from]||L.why[id]){var w=L.why[from];L.why[from]=L.why[id];L.why[id]=w;if(!L.why[from])delete L.why[from];if(!L.why[id])delete L.why[id]}}
  else{if(LY().why[id])delete LY().why[id];
    // a memorized ability lives in one ability-bar slot at a time
    if(bar==='ab'){LY().ab.forEach(function(x,i){if(x&&x.t===en.t&&x.n===en.n&&('ab:'+i)!==id)LY().ab[i]=null})}}
  setSlot(id,clone(en));save();armed=null;msg('Placed '+en.n+' on '+BARS[bar]+' key '+(KEYNAME(keyOf(id))||'(no key)')+'.');render();focusSlot(id);return true}
function clearSlot(id){var en=slotEntry(id);if(!en)return;snap();setSlot(id,null);delete LY().why[id];save();msg('Cleared '+en.n+'.');render();focusSlot(id)}
function arm(en,from){armed={e:clone(en),from:from||null};var bar=bestBar(en);msg('Picked up '+en.n+'. '+(narrow()?'Tap':'Click or press Enter on')+' a slot on the '+BARS[bar]+' to place it'+(from?' (or Delete to clear)':'')+'; Esc cancels.');render();
  if(!from){var L=LY(),t=null;if(bar==='hb'){for(var p=0;p<L.hb.length&&!t;p++)for(var i=0;i<HB_N;i++)if(!L.hb[p][i]){t='hb:'+p+':'+i;break}if(!t)t='hb:0:0'}
    else{var a=L[bar];for(var j=0;j<a.length;j++)if(!a[j]){t=bar+':'+j;break}if(!t)t=bar+':0'}return t}return null}
function disarm(){if(!armed)return false;armed=null;msg('Cancelled.');render();return true}
function focusSlot(id){var b=document.querySelector('.hb-slot[data-s="'+id+'"]');if(b)b.focus()}
// palette events
var pal=$('hb-palette');
pal.addEventListener('click',function(ev){var b=ev.target.closest('.hb-pi');if(!b)return;var x=PAL[+b.getAttribute('data-i')];if(!x)return;
  if(x.lock){msg(x.en.n+' is level '+x.lv+', above your level '+level()+'.',true);return}
  if(armed&&!armed.from&&armed.e.n===x.en.n&&armed.e.t===x.en.t){disarm();return}
  var t=arm(x.en);if(ev.detail===0&&t)focusSlot(t)});
pal.addEventListener('keydown',function(ev){var b=ev.target.closest('.hb-pi');if(!b)return;var bs=[].slice.call(pal.querySelectorAll('.hb-pi')),i=bs.indexOf(b);
  if(ev.key==='ArrowDown'||ev.key==='ArrowRight'){ev.preventDefault();(bs[i+1]||b).focus()}else if(ev.key==='ArrowUp'||ev.key==='ArrowLeft'){ev.preventDefault();(bs[i-1]||b).focus()}
  else if(ev.key==='Home'){ev.preventDefault();bs[0].focus()}else if(ev.key==='End'){ev.preventDefault();bs[bs.length-1].focus()}});
pal.addEventListener('dragstart',function(ev){var b=ev.target.closest('.hb-pi');if(!b)return;var x=PAL[+b.getAttribute('data-i')];if(!x||x.lock){ev.preventDefault();return}
  ev.dataTransfer.setData('text/plain',JSON.stringify({e:x.en}));ev.dataTransfer.effectAllowed='copy';drag={e:x.en};app.classList.add('hb-dragging')});
pal.addEventListener('dragover',function(ev){if(drag&&drag.from){ev.preventDefault()}});
pal.addEventListener('drop',function(ev){if(drag&&drag.from){ev.preventDefault();var f=drag.from;drag=null;clearSlot(f)}});
// slot events
var bars=$('hb-bars'),drag=null;
function readDrag(ev){if(drag)return drag;try{return JSON.parse(ev.dataTransfer.getData('text/plain'))}catch(x){return null}}
bars.addEventListener('click',function(ev){var b=ev.target.closest('.hb-slot');if(!b||keysMode&&ev.target.closest('.hb-kin'))return;var id=b.getAttribute('data-s');
  if(armed){place(id,armed.e,armed.from);return}var en=slotEntry(id);if(en){arm(en,id);focusSlot(id)}});
bars.addEventListener('keydown',function(ev){var b=ev.target.closest('.hb-slot');if(!b)return;var id=b.getAttribute('data-s');
  if(ev.key==='Delete'||ev.key==='Backspace'){ev.preventDefault();if(armed&&armed.from===id)armed=null;clearSlot(id);return}
  var mv={ArrowLeft:[0,-1],ArrowRight:[0,1],ArrowUp:[-1,0],ArrowDown:[1,0]}[ev.key];if(!mv)return;ev.preventDefault();
  var rows=[].slice.call(bars.querySelectorAll('.hb-row')),row=b.closest('.hb-row'),ri=rows.indexOf(row),cells=[].slice.call(row.querySelectorAll('.hb-slot')),ci=cells.indexOf(b);
  if(mv[1]){ci=(ci+mv[1]+cells.length)%cells.length;cells[ci].focus()}else{ri=Math.max(0,Math.min(rows.length-1,ri+mv[0]));var cs=rows[ri].querySelectorAll('.hb-slot');(cs[Math.min(ci,cs.length-1)]).focus()}});
bars.addEventListener('dragstart',function(ev){var b=ev.target.closest('.hb-slot');if(!b)return;var id=b.getAttribute('data-s'),en=slotEntry(id);if(!en){ev.preventDefault();return}
  drag={e:en,from:id};ev.dataTransfer.setData('text/plain',JSON.stringify(drag));ev.dataTransfer.effectAllowed='move';app.classList.add('hb-dragging')});
bars.addEventListener('dragover',function(ev){var b=ev.target.closest('.hb-slot');if(!b)return;var d=drag;if(d&&!fits(b.getAttribute('data-s').split(':')[0],d.e))return;ev.preventDefault();b.classList.add('over')});
bars.addEventListener('dragleave',function(ev){var b=ev.target.closest('.hb-slot');if(b)b.classList.remove('over')});
bars.addEventListener('drop',function(ev){var b=ev.target.closest('.hb-slot');if(!b)return;ev.preventDefault();var d=readDrag(ev);drag=null;app.classList.remove('hb-dragging');if(!d||!d.e)return;place(b.getAttribute('data-s'),d.e,d.from||null)});
document.addEventListener('dragend',function(){drag=null;app.classList.remove('hb-dragging');document.querySelectorAll('.hb-slot.over').forEach(function(x){x.classList.remove('over')})});
bars.addEventListener('change',function(ev){var i=ev.target.closest('.hb-kin');if(!i)return;snap();setKey(i.getAttribute('data-s'),i.value.trim());save();msg('Keybind saved.')});
// tooltip
var tip=$('hb-tip');
function showTip(el){var en=null,why='';if(el.classList.contains('hb-pi')){var x=PAL[+el.getAttribute('data-i')];if(x)en=x.en}else{en=slotEntry(el.getAttribute('data-s'));why=el.getAttribute('data-why')||''}
  if(!en){tip.hidden=true;return}tip.innerHTML=tipHtml(en)+(why?'<div class="hb-tw"><span class="badge strat">strategy</span> '+e(why)+'</div>':'');tip.hidden=false;
  var r=el.getBoundingClientRect(),w=Math.min(340,innerWidth-16);tip.style.maxWidth=w+'px';var x0=Math.min(Math.max(8,r.left+scrollX),scrollX+innerWidth-w-8);tip.style.left=x0+'px';
  var y=r.bottom+scrollY+6;if(r.bottom+tip.offsetHeight+12>innerHeight)y=r.top+scrollY-tip.offsetHeight-6;tip.style.top=Math.max(scrollY+4,y)+'px'}
app.addEventListener('mouseover',function(ev){var el=ev.target.closest('.hb-pi,.hb-slot');if(el)showTip(el)});
app.addEventListener('mouseout',function(ev){if(ev.target.closest('.hb-pi,.hb-slot'))tip.hidden=true});
app.addEventListener('focusin',function(ev){var el=ev.target.closest('.hb-pi,.hb-slot');if(el&&!narrow())showTip(el);else tip.hidden=true});
// global keys
document.addEventListener('keydown',function(ev){var tag=(ev.target.tagName||'').toLowerCase(),typing=tag==='input'||tag==='textarea'||tag==='select';
  if(ev.key==='Escape'){if(!$('hb-picker').hidden){closePicker();return}if(disarm())return;if(document.documentElement.classList.contains('hb-focus')){setFocus(false);return}}
  if((ev.ctrlKey||ev.metaKey)&&!ev.shiftKey&&(ev.key==='z'||ev.key==='Z')&&!typing){ev.preventDefault();doUndo()}});
// toolbar
$('hb-layout').addEventListener('change',function(){CS().cur=$('hb-layout').value;save();armed=null;render()});
$('hb-lname').addEventListener('change',function(){var v=$('hb-lname').value.trim().slice(0,24);if(!v)return;snap();LY().n=v;save();renderLayouts();renderBars()});
$('hb-new').addEventListener('click',function(){snap();var o=CS(),n=Object.keys(o.L).filter(function(k){return o.L[k].k==='custom'}).length+1,id='c'+Date.now().toString(36);
  o.L[id]=fixLayout(blankLayout('Custom '+n,'custom'));o.cur=id;save();msg('New custom layout. Name it in the Name box.');render();$('hb-lname').focus()});
$('hb-del').addEventListener('click',function(){var o=CS();if(LY().k!=='custom')return;snap();var n=LY().n;delete o.L[o.cur];o.cur='solo';save();msg('Deleted '+n+'. Undo brings it back.');render()});
$('hb-suggest').addEventListener('click',function(){snap();applySuggest(LY(),LY().k);save();msg('Filled '+LY().n+' with the suggested '+(LY().k==='custom'?'solo':LY().k)+' layout for level '+level()+'.');render()});
$('hb-undo').addEventListener('click',doUndo);
$('hb-clear').addEventListener('click',function(){snap();var L=LY();L.ab=L.ab.map(function(){return null});L.au=L.au.map(function(){return null});L.hb=L.hb.map(function(p){return p.map(function(){return null})});L.why={};L.rot='';save();msg('Cleared '+L.n+'. Undo brings it back.');render()});
$('hb-keys').addEventListener('click',function(){keysMode=!keysMode;render();if(keysMode){var i=document.querySelector('.hb-kin');if(i)i.focus()}});
$('hb-level').addEventListener('change',function(){var b=band(),v=Math.round(+$('hb-level').value)||b[1];v=Math.max(b[0],Math.min(b[1],v));CS().level=v;save();render()});
$('hb-pages').addEventListener('change',function(){var v=Math.max(1,Math.min(10,Math.round(+$('hb-pages').value)||1));snap();S.prefs.pages=v;Object.keys(CS().L).forEach(function(k){var L=CS().L[k];L.hb=L.hb.slice(0,v);L.keys.hb=L.keys.hb.slice(0,v);fixLayout(L)});save();render()});
$('hb-q').addEventListener('input',renderPalette);$('hb-kind').addEventListener('change',renderPalette);
$('hb-future').addEventListener('change',function(){S.prefs.future=$('hb-future').checked;save();renderPalette()});
$('hb-strict').addEventListener('change',function(){S.prefs.strict=$('hb-strict').checked;save();render()});
$('hb-rot').addEventListener('input',function(){LY().rot=$('hb-rot').value;save();renderBars()});
$('hb-notes').addEventListener('input',function(){LY().notes=$('hb-notes').value;LY().nsrc=0;save();renderBars()});
$('hb-macro').addEventListener('submit',function(ev){ev.preventDefault();var n=$('hb-mname').value.trim(),c=$('hb-mcmd').value.trim();if(!n||!c){msg('A macro needs a label and a command.',true);return}
  snap();S.macros.push({n:n.slice(0,24),c:c.slice(0,200)});save();$('hb-mname').value='';$('hb-mcmd').value='';msg('Macro '+n+' added to the palette (Hotbar items).');renderPalette()});
// ---------------------------------------------------------------- focus mode
function setFocus(on){document.documentElement.classList.toggle('hb-focus',on);$('hb-focus-t').setAttribute('aria-pressed',on?'true':'false');tip.hidden=true;
  if(on){var f=document.querySelector('.hb-slot');if(f)f.focus();msg('Focus mode: Esc exits.')}else $('hb-focus-t').focus()}
$('hb-focus-t').addEventListener('click',function(){setFocus(!document.documentElement.classList.contains('hb-focus'))});
$('hb-focus-x').addEventListener('click',function(){setFocus(false)});
$('hb-size').addEventListener('input',function(){S.prefs.size=+$('hb-size').value;app.style.setProperty('--hb-sz',S.prefs.size+'px');save()});
$('hb-pop').addEventListener('click',function(){window.open(location.pathname+'?focus=1','mnmhotbar','width=760,height=460')});
$('hb-print').addEventListener('click',function(){window.print()});
window.addEventListener('storage',function(ev){if(ev.key===KEY){S=load();render()}});
// ---------------------------------------------------------------- character sheet
var itemsReady=null;
function loadScript(src){return new Promise(function(res){var s=document.createElement('script');s.src=root+src;s.onload=res;s.onerror=res;document.head.appendChild(s)})}
function needItems(){if(!itemsReady)itemsReady=Promise.all([window.MNM_HBI?0:loadScript('assets/hotbar-items.js'),window.MNM_MKTI?0:loadScript('assets/market-items.js')]).then(function(){IDX={};(window.MNM_HBI||[]).forEach(function(r){IDX[r[0]]=r})});return itemsReady}
var IDX=null,STATS=[['str','STR'],['sta','STA'],['agi','AGI'],['dex','DEX'],['int','INT'],['wis','WIS'],['cha','CHA']],OTHER=[['ac','AC'],['hp','HP'],['mana','Mana'],['hp_regen','HP regen'],['mana_regen','Mana regen'],['haste','Haste %'],['spell_haste','Spell haste %']],
 RES=[['mr','Magic'],['fr','Fire'],['cr','Cold'],['pr','Poison'],['dr','Disease'],['er','Electric'],['cor','Corruption'],['hr','Holy']];
var STL={};STATS.concat(OTHER,RES).forEach(function(x){STL[x[0]]=x[1]});
function slotList(){var o=[];H.gear.forEach(function(g){for(var i=1;i<=g[1];i++)o.push([g[1]>1?g[0]+' '+i:g[0],g[0],g[2]])});return o}
function itemStats(r){var st=r[4]||{};return Object.keys(st).map(function(k){return (STL[k]||k)+' '+(st[k]>0?'+':'')+st[k]}).join(', ')+(r[10]?(Object.keys(st).length?', ':'')+'DMG/DLY '+r[10]:'')+(r[11]?' · '+r[11]:'')}
function srcText(r){var s=[];(r[6]||[]).forEach(function(d){s.push((d[0]||'drop')+(d[3]?' (lvl '+d[3]+')':'')+(d[1]?' — '+(d[2]?'<a href="'+root+d[2]+'">'+e(d[1])+'</a>':e(d[1])):''))});if(r[7])s.push('Quest: '+e(r[7]));if(r[8])s.push('Vendor');if(r[9])s.push('Crafted');return s.join('; ')||'<span class="dim">no source on the wiki</span>'}
function baseStats(){var c=cls(),rr=H.races[race()],b=C().builds[+CS().build||0],st=rr&&rr.start&&rr.start[c];if(!st)return null;var o={};Object.keys(st).forEach(function(k){o[k.toLowerCase()]=st[k]+((b&&b.a&&b.a[k])||0)});return o}
function renderSheet(){var o=CS(),c=C();
  $('hb-build').innerHTML=c.builds.length?c.builds.map(function(b,i){return '<option value="'+i+'"'+(i===(+o.build||0)?' selected':'')+'>'+e(b.n)+' ('+Object.keys(b.a).map(function(k){return '+'+b.a[k]+' '+k}).join(', ')+')</option>'}).join(''):'<option value="0">No builds for this class yet</option>';
  if(!IDX){$('hb-doll').innerHTML='<p class="dim">Loading item data…</p>';needItems().then(renderSheet);return}
  var MK=window.MNM_MKTI||{},h='';
  var groups=[['Armor',slotList().filter(function(s){return ['Primary','Secondary','Range','Ammo','Belt'].indexOf(s[1])<0})],['Weapons & held',slotList().filter(function(s){return ['Primary','Secondary','Range','Ammo'].indexOf(s[1])>=0})],['Belt',slotList().filter(function(s){return s[1]==='Belt'})]];
  groups.forEach(function(g){h+='<div class="hb-dg"><h3>'+g[0]+'</h3><div class="hb-dgrid">'+g[1].map(function(s){var nm=o.gear[s[0]],r=nm&&IDX[nm];
    return '<button type="button" class="hb-gs'+(nm?' full':'')+'" data-g="'+e(s[0])+'" data-sl="'+e(s[1])+'" aria-label="'+e(s[0]+': '+(nm||'empty'))+'"><span class="hb-gl">'+e(s[0])+(s[2]!=='FACT'?' <span class="badge unc" title="Two of this slot is an assumption">?</span>':'')+'</span><span class="hb-gn">'+(nm?e(nm):'<span class="dim">empty</span>')+'</span>'+(r?'<span class="hb-gst">'+e(itemStats(r))+'</span>':'')+'</button>'}).join('')+'</div></div>'});
  $('hb-doll').innerHTML=h;
  var base=baseStats(),gear={},eq=[];Object.keys(o.gear).forEach(function(k){var r=IDX[o.gear[k]];if(!r)return;eq.push([k,r]);var st=r[4]||{};Object.keys(st).forEach(function(s){gear[s]=(gear[s]||0)+st[s]})});
  function n(v){return v?(Math.round(v*10)/10):0}
  var t='<h3>Totals</h3>'+(base?'':'<p class="dim">No sourced starting stats for '+e(race()||'this race')+' as '+e(cls())+', so only gear is counted.</p>')+'<table class="grid hb-tt"><thead><tr><th>Stat</th><th>Base</th><th>Gear</th><th>Total</th></tr></thead><tbody>'+
    STATS.map(function(x){var b=base?base[x[0]]||0:0;return '<tr><td>'+x[1]+'</td><td>'+(base?b:'—')+'</td><td>'+(gear[x[0]]?'+'+n(gear[x[0]]):'0')+'</td><td><b>'+n(b+(gear[x[0]]||0))+'</b></td></tr>'}).join('')+
    OTHER.map(function(x){return '<tr><td>'+x[1]+'</td><td>—</td><td>'+n(gear[x[0]])+'</td><td><b>'+n(gear[x[0]])+'</b></td></tr>'}).join('')+'</tbody></table>'+
    '<table class="grid hb-tt"><thead><tr><th>Resist</th><th>Gear total</th></tr></thead><tbody>'+RES.map(function(x){return '<tr><td>'+x[1]+'</td><td><b>'+n(gear[x[0]])+'</b></td></tr>'}).join('')+'</tbody></table>'+
    '<p class="dim">Base = '+e(race()||'race')+' starting stats for '+e(cls())+' + build points (wiki race page'+(H.races[race()]&&H.races[race()].url?', <a class="ext" target="_blank" rel="noopener" href="'+e(H.races[race()].url)+'">'+e(race())+'</a>':'')+'). HP, Mana, AC and resists count gear only.</p>';
  if(eq.length)t+='<h3>Equipped</h3><ul class="hb-eq">'+eq.map(function(x){var r=x[1],m=MK[r[0]];return '<li><b>'+e(x[0])+':</b> <a class="ext" target="_blank" rel="noopener" href="'+e(r[5])+'">'+e(r[0])+'</a> <span class="dim">'+e(itemStats(r))+'</span><br>'+
     (m?'<a href="'+root+'market.html#'+encodeURIComponent(r[0])+'" title="'+e(m[1]+', seen '+m[2])+'">💰 Market: '+e(m[0])+'</a> · ':'<span class="dim">no market price</span> · ')+'<a href="'+root+'items.html#'+encodeURIComponent(r[0])+'">Drop sources</a>: '+srcText(r)+'</li>'}).join('')+'</ul>';
  $('hb-totals').innerHTML=t}
var pick=null;
function openPicker(g,sl){pick={g:g,sl:sl};var p=$('hb-picker');p.hidden=false;p.innerHTML='<div class="hb-ph"><b>'+e(g)+'</b> <button type="button" class="hb-px" aria-label="Close item picker">✕</button></div>'+
  '<input type="search" id="hb-iq" placeholder="Search '+e(sl)+' items for '+e(cls())+'…" aria-label="Search items for '+e(g)+'"> <label><input type="checkbox" id="hb-ilv" checked> Only items found at or below level '+level()+' (items with no level on the wiki stay listed)</label>'+
  (CS().gear[g]?' <button type="button" id="hb-iclr">Remove '+e(CS().gear[g])+'</button>':'')+'<p id="hb-icount" class="dim"></p><ul id="hb-ilist" class="hb-ilist"></ul>';
  $('hb-iq').addEventListener('input',listItems);$('hb-ilv').addEventListener('change',listItems);if($('hb-iclr'))$('hb-iclr').addEventListener('click',function(){equip(null)});listItems();$('hb-iq').focus()}
function closePicker(){$('hb-picker').hidden=true;var g=pick&&pick.g;pick=null;if(g){var b=document.querySelector('.hb-gs[data-g="'+g+'"]');if(b)b.focus()}}
function listItems(){var code=C().code,q=$('hb-iq').value.trim().toLowerCase(),lv=$('hb-ilv').checked?level():0,res=[];
  (window.MNM_HBI||[]).forEach(function(r){if((' '+r[1]+' ').indexOf(' '+pick.sl+' ')<0)return;if((' '+r[2]+' ').indexOf(' '+code+' ')<0)return;if(lv&&r[3]&&r[3]>lv)return;if(q&&(r[0]+' '+itemStats(r)).toLowerCase().indexOf(q)<0)return;res.push(r)});
  res.sort(function(a,b){var sa=Object.keys(a[4]).length,sb=Object.keys(b[4]).length;return (b[3]||0)-(a[3]||0)||sb-sa||a[0].localeCompare(b[0])});
  $('hb-icount').textContent=res.length+' '+pick.sl+' items usable by '+cls()+(res.length>60?' (first 60; search to narrow)':'');
  $('hb-ilist').innerHTML=res.slice(0,60).map(function(r){return '<li><button type="button" class="hb-ib" data-n="'+e(r[0])+'"><b>'+e(r[0])+'</b>'+' <span class="dim">'+(r[3]?'lvl '+r[3]:'level ?')+'</span><br><span class="hb-ist">'+e(itemStats(r)||'no stats on the wiki')+'</span></button></li>'}).join('')||'<li class="dim">No items for this slot and class.</li>'}
function equip(nm){snap();if(nm)CS().gear[pick.g]=nm;else delete CS().gear[pick.g];save();msg(nm?'Equipped '+nm+' in '+pick.g+'.':'Removed item from '+pick.g+'.');var g=pick.g;$('hb-picker').hidden=true;pick=null;renderSheet();renderPalette();var b=document.querySelector('.hb-gs[data-g="'+g+'"]');if(b)b.focus()}
$('hb-sheet').addEventListener('click',function(ev){var g=ev.target.closest('.hb-gs');if(g){openPicker(g.getAttribute('data-g'),g.getAttribute('data-sl'));return}var ib=ev.target.closest('.hb-ib');if(ib){equip(ib.getAttribute('data-n'));return}if(ev.target.closest('.hb-px'))closePicker()});
$('hb-build').addEventListener('change',function(){snap();CS().build=+$('hb-build').value;save();renderSheet()});
$('hb-gclear').addEventListener('click',function(){snap();CS().gear={};save();msg('Gear cleared. Undo brings it back.');renderSheet();renderPalette()});
function setSheet(on){$('hb-sheet').hidden=!on;$('hb-sheet-t').setAttribute('aria-pressed',on?'true':'false');S.prefs.sheet=on;save();if(on)renderSheet()}
$('hb-sheet-t').addEventListener('click',function(){setSheet($('hb-sheet').hidden);if(!$('hb-sheet').hidden)$('hb-sheet').scrollIntoView({block:'start'})});
// ---------------------------------------------------------------- share / import / export
function b64u(bytes){var s='';for(var i=0;i<bytes.length;i++)s+=String.fromCharCode(bytes[i]);return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
function ub64(s){s=s.replace(/-/g,'+').replace(/_/g,'/');while(s.length%4)s+='=';var b=atob(s),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return u}
function payload(){var o=CS();return{v:1,c:cls(),r:race(),l:level(),cur:o.cur,L:o.L,g:o.gear,b:o.build||0,m:S.macros,p:pages()}}
function encode(obj){var raw=new TextEncoder().encode(JSON.stringify(obj));if(!window.CompressionStream)return Promise.resolve('j'+b64u(raw));
  var cs=new Blob([raw]).stream().pipeThrough(new CompressionStream('deflate-raw'));return new Response(cs).arrayBuffer().then(function(b){return 'z'+b64u(new Uint8Array(b))})}
function decode(code){code=String(code||'').trim();var m=code.match(/hb=([A-Za-z0-9_-]+)/);if(m)code=m[1];var t=code[0],body=code.slice(1);
  if(t==='j')return Promise.resolve(JSON.parse(new TextDecoder().decode(ub64(body))));
  if(t==='z'){var ds=new Blob([ub64(body)]).stream().pipeThrough(new DecompressionStream('deflate-raw'));return new Response(ds).text().then(JSON.parse)}
  return Promise.reject(new Error('not a hotbar share code'))}
function shareUrl(){return encode(payload()).then(function(c){return location.origin+location.pathname+'#hb='+c})}
function applyShared(d){if(!d||d.v!==1||!H.classes[d.c]||!d.L)throw new Error('bad data');var cur=cls();
  if(selC&&d.c!==cur){selC.value=d.c;lsPut('mnm-class',d.c);selC.dispatchEvent(new Event('change'))}
  snapFor(d.c);S.cls[d.c]={cur:d.L[d.cur]?d.cur:Object.keys(d.L)[0],L:d.L,gear:d.g||{},build:d.b||0,level:d.l||null};if(d.p)S.prefs.pages=d.p;
  (d.m||[]).forEach(function(m){if(m&&m.n&&!S.macros.some(function(x){return x.n===m.n&&x.c===m.c}))S.macros.push({n:String(m.n).slice(0,24),c:String(m.c||'').slice(0,200)})});
  var b=band();if(d.l&&selL&&(d.l<b[0]||d.l>b[1])){var k=(R.order||[]).filter(function(k){var x=k.split('-').map(Number);return d.l>=x[0]&&d.l<=x[1]})[0];if(k){selL.value=k;lsPut('mnm-range',k);selL.dispatchEvent(new Event('change'))}}
  save();render()}
function snapFor(c){undo.push(JSON.stringify({c:c,s:S.cls[c]||null,m:S.macros}));$('hb-undo').disabled=false}
$('hb-copy').addEventListener('click',function(){shareUrl().then(function(u){$('hb-codebox').hidden=false;$('hb-codebox').value=u;var done=function(){msg('Share link copied ('+u.length+' characters).')};
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(u).then(done,function(){$('hb-codebox').select();msg('Copy the link from the box.')});else{$('hb-codebox').select();msg('Copy the link from the box.')}})});
$('hb-code').addEventListener('click',function(){encode(payload()).then(function(c){$('hb-codebox').hidden=false;$('hb-codebox').value=c;$('hb-codebox').select();msg('Share code shown ('+c.length+' characters).')})});
$('hb-codeform').addEventListener('submit',function(ev){ev.preventDefault();decode($('hb-codein').value).then(function(d){applyShared(d);msg('Loaded the shared '+d.c+' layouts. Undo reverts.')}).catch(function(){msg('That is not a valid share code.',true)})});
$('hb-export').addEventListener('click',function(){var blob=new Blob([JSON.stringify({type:'mnm-hotbar',exported:new Date().toISOString(),state:S},null,1)],{type:'application/json'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='mnm-hotbar-'+new Date().toISOString().slice(0,10)+'.json';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},500);msg('Exported all classes\' layouts as JSON.')});
function importText(txt){var d=JSON.parse(txt);var st=d&&d.type==='mnm-hotbar'?d.state:d;
  if(st&&st.v===1&&st.cls&&typeof st.cls==='object'){undo.push(JSON.stringify({all:JSON.stringify(S)}));$('hb-undo').disabled=false;
    S=st;S.prefs=Object.assign({size:48,strict:true,pages:2,sheet:false,future:false},S.prefs||{});S.macros=S.macros||[];save();render();return 'all'}
  if(st&&st.v===1&&st.L){applyShared(st);return st.c}throw new Error('bad')}
$('hb-import').addEventListener('change',function(){var f=this.files&&this.files[0];if(!f)return;var rd=new FileReader();rd.onload=function(){try{var r=importText(rd.result);msg(r==='all'?'Imported all layouts from '+f.name+'.':'Imported '+r+' layouts from '+f.name+'.')}catch(x){msg('Could not import: not a Hotbar planner JSON file.',true)}$('hb-import').value=''};rd.readAsText(f)});
window.MNM_HB_API={encode:encode,decode:decode,importText:importText,state:function(){return S},undo:doUndo,suggest:suggest};
// ---------------------------------------------------------------- picker changes + boot
function onPick(){armed=null;setTimeout(render,0)}
[selC,selR,selL].forEach(function(s){if(s)s.addEventListener('change',onPick)});
document.addEventListener('mnm-chargen',onPick);
function fromHash(){var hm=location.hash.match(/hb=([A-Za-z0-9_-]+)/);if(!hm)return;
  decode(hm[1]).then(function(d){applyShared(d);msg('Loaded the shared '+d.c+' layouts from the link. Undo reverts to yours.');if(history.replaceState)history.replaceState(null,'',location.pathname+location.search)}).catch(function(){msg('The link\'s hotbar code could not be read.',true)})}
window.addEventListener('hashchange',fromHash);
render();if(S.prefs.sheet)setSheet(true);
if(/[?&]focus=1/.test(location.search))setFocus(true);
fromHash();
})();
