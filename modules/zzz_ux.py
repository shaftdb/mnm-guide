# UX pass 1 (runs after zz_nav so its stylesheet loads last): design tokens, wider ultrawide layout with a prose measure,
# 44px touch targets + compact sticky mini bar on phones, skip link + :focus-visible rings, control-border contrast,
# prefers-reduced-motion. CSS/JS only: static/mod-ux.css + static/mod-ux.js. Remove by deleting this module.
# NOTE: TEMPLATE goes through str.format, so literal braces are doubled.
TEMPLATE = TEMPLATE.replace('</head>', '<link rel="stylesheet" href="{root}assets/mod-ux.css">\n</head>', 1
    ).replace('<body class="sec-{section}">', '<body class="sec-{section}">\n<a class="skip" href="#content">Skip to content</a>', 1
    ).replace('<main class="main">', '<main class="main" id="content" tabindex="-1">', 1
    ).replace('</body>', '<script src="{root}assets/mod-ux.js"></script>\n</body>', 1)
