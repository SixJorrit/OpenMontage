import sys, numpy as np
from PIL import Image, ImageFilter
W,H=1800,2400
def wall():
    y,x=np.mgrid[0:H,0:W].astype(float)
    base=np.array([236,230,220],float)
    # soft light from top-left, darker to bottom-right
    g=1-0.16*((x/W)*0.6+(y/H)*0.8)
    img=base[None,None,:]*g[...,None]
    rng=np.random.default_rng(3); img+=rng.normal(0,2.2,(H,W,1))
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8),'RGB').filter(ImageFilter.GaussianBlur(0.6))
def mock(poster_path,out):
    bg=wall().convert('RGBA'); P=Image.open(poster_path).convert('RGBA')
    ph=int(H*0.76); pw=int(P.width*ph/P.height); P=P.resize((pw,ph),Image.LANCZOS)
    x=(W-pw)//2; y=int(H*0.11)
    # shadow: soft, offset down-right
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); a=Image.new('L',(pw,ph),110); sh.paste((0,0,0,110),(x+18,y+30),a)
    sh=sh.filter(ImageFilter.GaussianBlur(28))
    # tight contact shadow
    sh2=Image.new('RGBA',(W,H),(0,0,0,0)); sh2.paste((0,0,0,90),(x+4,y+8),Image.new('L',(pw,ph),90)); sh2=sh2.filter(ImageFilter.GaussianBlur(6))
    bg.alpha_composite(sh); bg.alpha_composite(sh2); bg.alpha_composite(P,(x,y))
    bg.convert('RGB').resize((1200,1600),Image.LANCZOS).save(out,quality=92)
for n in (1,2,3,4):
    mock(f"/Users/jorrit/dev/OpenMontage/docs/expeditie-mediajungle/shopify/export/poster-missie-{n}-a2.jpg", f"/Users/jorrit/dev/OpenMontage/docs/expeditie-mediajungle/shopify/export/mockup-missie-{n}-a2-wand.jpg")
print('ok')
