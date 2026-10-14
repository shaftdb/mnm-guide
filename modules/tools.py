# Community tools module: /tools.html - spell timer, XP/hr calculator, camp notepad (all browser-local)
def _tools_page():
    return ('<link rel="stylesheet" href="/assets/mod-tools.css">'
            '<p>Small helpers that run in your browser. Everything you enter is saved only in this browser (localStorage); nothing is sent anywhere. '
            'The tools use only the numbers you type in <span class="badge strat">strategy</span>. They hold no game data.</p>'
            '<h2 id="timer">Spell timer</h2><p class="dim">Add a timer for a buff, debuff or respawn. Type the duration as seconds or m:ss. Timers keep counting after a reload.</p>'
            '<div class="tl-row"><input id="tm-name" placeholder="Spell or camp (e.g. Slow on named)" aria-label="Timer name"><input id="tm-dur" placeholder="m:ss" size="6" aria-label="Duration"><button type="button" id="tm-add">Start</button></div>'
            '<ul id="tm-list" class="tl-list"></ul>'
            '<h2 id="xp">XP per hour</h2><p class="dim">Read your XP bar percentage at the start and now. The calculator gives XP %/hr and time to level.</p>'
            '<div class="tl-row"><label>Start % <input id="xp-a" type="number" step="0.1" min="0" max="100"></label><label>Now % <input id="xp-b" type="number" step="0.1" min="0"></label>'
            '<label>Levels gained <input id="xp-l" type="number" min="0" value="0"></label><label>Minutes <input id="xp-m" type="number" min="1"></label>'
            '<button type="button" id="xp-start">Start clock</button></div><p id="xp-out" class="tl-out"></p>'
            '<h2 id="notes">Camp notepad</h2><p class="dim">Notes per camp (spawn times, pull spots, who\'s camping). Saves as you type.</p>'
            '<div class="tl-row"><input id="np-camp" placeholder="Camp name" aria-label="Camp name"><button type="button" id="np-add">Add camp</button></div><div id="np-list"></div>'
            '<script src="/assets/mod-tools.js"></script>')
_tl_prev_bc = build_content
def build_content():
    _tl_prev_bc()
    add_page('tools.html', 'Tools: timer, XP/hr, camp notes', body_html=_tools_page(), section='tools', desc='Spell timer, XP per hour calculator and camp notepad')
NAV.insert(len(NAV) - 1, ('Tools', '/tools.html', 'tools'))
