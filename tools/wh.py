import json,re
from bs4 import BeautifulSoup
def clean(x): return re.sub(r'\s+',' ',x.get_text(' ',strip=True)).strip()
def html_tables(html):
    """[(heading, rows)] for every innermost-ish data table in rendered HTML, with nearest preceding heading."""
    s=BeautifulSoup(html,'html.parser'); out=[]
    for t in s.find_all('table'):
        rows=[]
        for tr in t.find_all('tr'):
            if tr.find_parent('table') is not t: continue
            cells=[c for c in tr.find_all(['th','td']) if c.find_parent('tr') is tr]
            if any(c.find('table') for c in cells): continue
            rows.append([clean(c) for c in cells])
        h=t.find_previous(['h1','h2','h3','h4'])
        out.append((clean(h).replace('[edit]','').strip() if h else '',rows))
    return out
