"""Trailer v1: animatie 2 (film) + LinkedIn-kaarttour (map) + eindkaart. 1280x720/24, ~49 s."""
import subprocess, pathlib
from PIL import Image, ImageDraw, ImageFont
ROOT=pathlib.Path("/Users/jorrit/dev/OpenMontage"); P=ROOT/"projects/expeditie-mediajungle-trailer"
FILM=ROOT/"projects/expeditie-mj-animatie2-v2/renders/expeditie-mediajungle-animatie-2-v2.mp4"
MAP=P/"src/linkedin-rondje.mp4"; MUSIC=ROOT/"remotion-composer/public/expeditie-mj/music-v2.mp3"
LOGO=ROOT/"docs/expeditie-mediajungle/references/logo-expeditie-mj-2000.png"
FONT="/Users/jorrit/Library/Fonts/Baloo2-ExtraBold.ttf"; FONT2="/Users/jorrit/Library/Fonts/Baloo2-SemiBold.ttf"
W,H,FPS=1280,720,24
# (source, start, end, overlay-text or None)
SEG=[("film",0.0,3.2,None),("film",6.3,12.4,None),("film",15.6,17.4,None),("film",39.1,44.6,None),
     ("map",3.0,6.5,"Tien missies"),("map",18.0,21.5,"Eén doorlopende verhaallijn"),
     ("film",46.9,54.4,None),("film",55.6,60.8,None),
     ("map",48.0,51.5,"Elke beloning ontgrendelt\nde volgende missie"),
     ("film",61.6,68.3,None),("film",69.6,75.0,"HOLD"),("card",0,5.5,None)]
def text_png(text, path, size=64):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img); f=ImageFont.truetype(FONT,size)
    lines=text.split("\n"); lh=int(size*1.15); total=lh*len(lines); y=H-140-total
    for ln in lines:
        w=d.textlength(ln,font=f); x=(W-w)/2
        d.text((x,y),ln,font=f,fill="#F5C518",stroke_width=6,stroke_fill="#4A2C17"); y+=lh
    img.save(path)
def card_png(path):
    img=Image.new("RGB",(W,H),"#04202c"); d=ImageDraw.Draw(img)
    logo=Image.open(LOGO).convert("RGBA"); lw=620; logo=logo.resize((lw,int(logo.height*lw/logo.width)),Image.LANCZOS)
    img.paste(logo,((W-lw)//2,90),logo)
    f=ImageFont.truetype(FONT,44); f2=ImageFont.truetype(FONT2,30)
    t1="Gratis onderdeel van het Mediajungle Educatieplatform"; t2="Vraag een vrijblijvende demo aan op mediajungle.eu"
    y=90+logo.height+40
    d.text(((W-d.textlength(t1,font=f))/2,y),t1,font=f,fill="#F5C518"); d.text(((W-d.textlength(t2,font=f2))/2,y+70),t2,font=f2,fill="#d5ebe5")
    img.save(path)
B=P/"build"; card_png(B/"card.png")
inputs=["-i",str(FILM),"-i",str(MAP),"-loop","1","-t","5.5","-framerate",str(FPS),"-i",str(B/"card.png"),"-i",str(MUSIC)]
fc=[]; vlabels=[]; alabels=[]; t=0.0; bed_hi=[]; ov=[]; n_text=0; extra_inputs=[]
for i,(src,s,e,txt) in enumerate(SEG):
    d=e-s
    if src=="film" and txt=="HOLD":
        hold=1.2; txt=None
        fc.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,scale={W}:{H},fps={FPS},format=yuv420p,tpad=stop_mode=clone:stop_duration={hold},fade=t=out:st={d+hold-0.6}:d=0.6[v{i}]")
        fc.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.15,apad=pad_dur={hold},afade=t=out:st={d+hold-0.8}:d=0.8[a{i}]")
        d+=hold
    elif src=="film":
        fc.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,scale={W}:{H},fps={FPS},format=yuv420p[v{i}]")
        fc.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.15,afade=t=out:st={d-0.18}:d=0.18[a{i}]")
    elif src=="map":
        fc.append(f"[1:v]trim={s}:{e},setpts=PTS-STARTPTS,scale={W}:{H},fps={FPS},format=yuv420p[v{i}]")
        fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{d}[a{i}]"); bed_hi.append((t,t+d))
        if txt:
            pth=B/f"text{n_text}.png"; text_png(txt,pth); n_text+=1
            ov.append((str(pth),t+0.4,t+d-0.2))
    else:
        fc.append(f"[2:v]trim=0:{d},setpts=PTS-STARTPTS,scale={W}:{H},fps={FPS},format=yuv420p,fade=t=in:d=0.5,fade=t=out:st={d-0.8}:d=0.8[v{i}]")
        fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{d}[a{i}]"); bed_hi.append((t,t+d))
    vlabels.append(f"[v{i}]"); alabels.append(f"[a{i}]"); t+=d
TOTAL=t
fc.append("".join(vlabels)+f"concat=n={len(SEG)}:v=1:a=0[vcat]")
fc.append("".join(alabels)+f"concat=n={len(SEG)}:v=0:a=1[acat]")
# text overlays with fades
cur="[vcat]"
for k,(pth,a,b) in enumerate(ov):
    inputs+=["-loop","1","-framerate",str(FPS),"-t",f"{b-a:.3f}","-i",pth]
    idx=4+k
    fc.append(f"[{idx}:v]format=rgba,fade=t=in:d=0.3:alpha=1,fade=t=out:st={b-a-0.3:.3f}:d=0.3:alpha=1,setpts=PTS+{a:.3f}/TB[t{k}]")
    fc.append(f"{cur}[t{k}]overlay=0:0:eof_action=pass:enable='between(t,{a:.3f},{b:.3f})'[vo{k}]"); cur=f"[vo{k}]"
# music bed: hoog onder map/eindkaart, laag onder film (film heeft eigen muziek+VO)
expr="0.12"
for (a,b) in bed_hi:
    expr=f"if(between(t,{a:.2f},{b:.2f}),0.55,{expr})"
fc.append(f"[3:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,volume='{expr}':eval=frame,afade=t=out:st={TOTAL-1.2:.2f}:d=1.2[bed]")
fc.append("[acat][bed]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
out=P/"renders/expeditie-trailer-v3.mp4"
cmd=["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fc),"-map",cur,"-map","[aout]","-c:v","libx264","-preset","slow","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",str(out)]
subprocess.run(cmd,check=True); print("done",out,f"{TOTAL:.1f}s")
