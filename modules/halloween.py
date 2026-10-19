# NOTE: TEMPLATE goes through str.format, so literal braces are doubled.
# Seasonal Halloween theme ("Caves of Irem"). Single build flag: set HALLOWEEN = False to remove it after the season
# (static/mod-halloween.css/.js are then still copied but never linked; delete them too for a full revert).
HALLOWEEN = True
if HALLOWEEN:
    TEMPLATE = TEMPLATE.replace('</head>', '<link rel="stylesheet" href="{root}assets/mod-halloween.css">\n'
        '<script>try{{if(localStorage.getItem("mnm-halloween")!=="off")document.documentElement.classList.add("halloween")}}catch(e){{document.documentElement.classList.add("halloween")}}</script>\n</head>', 1
        ).replace('</body>', '<script src="{root}assets/mod-halloween.js"></script>\n</body>', 1)
