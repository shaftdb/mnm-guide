"""Resize downloaded wiki images (raw/img) into docs/img/maps and write data/images.json (credits)."""
import json,os,re
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta=json.load(open(os.path.join(ROOT,'raw','img','_meta.json')))
out={}
for name,m in meta.items():
    src=os.path.join(ROOT,'raw','img',name.replace(' ','_'))
    if not os.path.exists(src): continue
    slug=re.sub(r'[^a-z0-9]+','-',os.path.splitext(name)[0].lower()).strip('-')
    im=Image.open(src); im.load()
    if im.mode in('RGBA','LA','P'):
        bg=Image.new('RGB',im.size,(20,16,12)); im=im.convert('RGBA'); bg.paste(im,mask=im.split()[-1]); im=bg
    else: im=im.convert('RGB')
    for suf,mx,q in (('',2400,82),('-thumb',640,78)):
        c=im.copy(); c.thumbnail((mx,mx),Image.LANCZOS)
        c.save(os.path.join(ROOT,'docs','img','maps',slug+suf+'.jpg'),quality=q,optimize=True,progressive=True)
    out[name.replace('_',' ')]={'file':'img/maps/'+slug+'.jpg','thumb':'img/maps/'+slug+'-thumb.jpg','author':m.get('user'),'uploaded':(m.get('ts') or '')[:10],'source':m['page'],'orig_w':m.get('w'),'orig_h':m.get('h')}
    print(name,'ok')
json.dump(out,open(os.path.join(ROOT,'data','images.json'),'w'),indent=1)
