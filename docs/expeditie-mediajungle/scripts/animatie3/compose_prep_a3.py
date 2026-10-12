# -*- coding: utf-8 -*-
"""Animatie 3 — draft-montage voorbereiden (patroon compose_prep_v3 van de redo).
Per shot: video-trim (+ deterministische hertiming als de ratio buiten de band viel), audio-mix van
Seedance-clipaudio (alleen mensloze shots) + beds (per scene doorlopend, cumulatieve bronoffset, loop) + filmtake
op de gemeten mondstart + accenten. Schrijft remotion-composer/public/expeditie-mj-a3/<shot>.mp4, remotion_props.json
en draft_label_windows.json. Audioketen v2: vaste gains naar doelniveaus (LVL), stemmen uit lines/film.
    PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/compose_prep_a3.py [draftnr]
"""
import json, os, pathlib, subprocess, sys

PROJ = pathlib.Path("projects/expeditie-mj-animatie3")
V = PROJ / "assets/video/units"; N = PROJ / "assets/audio/lines/norm"; P = PROJ / "assets/audio/lines/parts"; SFX = PROJ / "assets/audio/sfx"
A2 = pathlib.Path("projects/expeditie-mj-animatie2-v2")
OUT = pathlib.Path("remotion-composer/public/expeditie-mj-a3"); OUT.mkdir(parents=True, exist_ok=True)
DRAFT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
FPS = 24
# Audioketen v2 (2026-10-12): elke bron krijgt een vaste gain = doelniveau - gemeten integrale luidheid (LUFS).
# Stemmen: assets/audio/lines/film (44,1k, gain per spreker, ~-16). Daarna één masterpass in render_draft.py.
FILM = PROJ / os.environ.get("A3_FILM", "assets/audio/lines/film")   # v4: A3_FILM=assets/audio/lines/film-v4
LVL = {"bed_under": -32.0, "bed_solo": -26.0, "clip_solo": -23.5, "second_bed": -3.0,
       "accent": {"sfx-owl": -24, "sfx-monkeys": -24, "sfx-snake": -24, "sfx-bear": -24, "sfx-camera-flash": -22, "sfx-reward-pop": -20}}
_lufs_path = PROJ / "artifacts/lufs_cache.json"
_lufs = json.load(open(_lufs_path)) if _lufs_path.exists() else {}
def lufs(path, start=None, end=None):
    key = f"{path}|{start}|{end}"
    if key not in _lufs:
        cmd = ["ffmpeg", "-nostats", "-hide_banner"] + (["-ss", f"{start:.3f}", "-to", f"{end:.3f}"] if start is not None else []) + ["-i", str(path), "-vn", "-af", "ebur128", "-f", "null", "-"]
        err = subprocess.run(cmd, capture_output=True, text=True).stderr
        v = float([l for l in err.splitlines() if l.strip().startswith("I:")][-1].split()[1])
        _lufs[key] = v if v > -70 else -70.0
        _lufs_path.write_text(json.dumps(_lufs, indent=1))
    return _lufs[key]
# Route L: per shot het gekozen lipsyncmodel (units/<unit>/lipsync-<model>/out.mp4 + log.json met insert_s).
# Dialoogshots krijgen dan de Seedance-achtergrond zonder kloonstem (Demucs, units/<unit>/stems/background.wav) op
# eenheidsgain: de verhouding tussen Seedance-sfeer en stem blijft zoals Seedance hem maakte; beds alleen als dunne laag.
import os
LIPSYNC = json.loads(os.environ.get("A3_LIPSYNC", "{}"))
ONLY = set(filter(None, os.environ.get("A3_ONLY", "").split(",")))   # alleen deze shots; props worden dan niet geschreven
BG_GAIN_DB = 0.0
def film_vo(path): return FILM / pathlib.Path(path).name.replace("-lead6", "")

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())

def ratio_info(unit):
    f = V / unit / "ratio.json"
    if not f.exists(): return None
    r = json.load(open(f))
    return r if r.get("ratio") else None

def bed(naam, vol, groep, fade_in=None, bron_off=0.0):
    return (naam, vol, fade_in, groep, bron_off)

# (shot, unit/bron, in, out|None=rest van clip, clipaudio ('keep'|'drop'), beds, vo:(file, at_s|'ratio'), accent:(file, at_s, vol)|None)
# at_s='ratio' = mondstart uit ratio.json (offset); bij ratio buiten band wordt de video hertimed met 1/ratio.
REWARD_POP_S = 1.30      # in 5C: Jorrit 2026-10-12 "wachten tot de wijzer rond is" -> na de klok-wipe van 30 f (1,25 s); burst + pop-geluid samen
FLASH_S = 3.6            # 2C: flitsmoment; na bekijken van g05t bijstellen
# 3AB: dierengeluiden op de blikken (film-seconden binnen het shot); na bekijken van g24 bijstellen
LOOKS_3AB = [("sfx-owl", 6.4), ("sfx-monkeys", 7.0), ("sfx-snake", 7.6), ("sfx-bear", 8.2)]

SHOTS = [
 ("shot_0A", str(A2 / "assets/video/units/g01/clip.mp4"), 0.0, 1.75, "keep", [], None, None),   # Jorrit 2026-10-12: bij inzoomen groeien er bomen bij (vanaf ~1,5 s) -> afgeknipt; intro wordt later vervangen
 ("shot_1A", "g01r", 0.0, 7.9, "keep", [bed("amb-garage-day", 0.25, "S1")], None, None),
 ("shot_1B", "g02t", 0.0, None, "drop", [bed("amb-garage-day", 0.45, "S1")], (N / "s01.wav", "ratio"), None),
 ("shot_1C", "g20", 0.0, None, "drop", [bed("amb-garage-day", 0.45, "S1")], (N / "s01b.wav", "ratio"), None),
 ("shot_2A", "g03r", 2.4, 7.4, "keep", [bed("amb-jungle-golden", 0.25, "S2")], None, None),
 ("shot_2B", "g04w", 0.0, 4.6, "keep", [bed("amb-jungle-golden", 0.25, "S2")], None, None),
 ("shot_2C", "g05u", 0.0, 5.6, "keep", [bed("amb-jungle-golden", 0.25, "S2")], None, None),   # Jorrit 2026-10-12: flitsgeluid weg (nieuwe 2C heeft geen zichtbare flits)
 ("shot_2D", "g21", 0.0, 3.8, "keep", [bed("amb-jungle-golden", 0.25, "S2"), bed("sfx-game-blips", 0.25, "GAME")], None, None),
 ("shot_2E", "g22b", 0.0, 3.8, "keep", [bed("amb-dusk-clearing", 0.25, "S3", 0.5)], None, None),
 ("shot_2F", "g23d", 0.0, 3.8, "keep", [bed("amb-dusk-clearing", 0.25, "S3")], None, None),
 ("shot_3AB", "g24", 0.0, None, "drop", [bed("amb-dusk-clearing", 0.40, "S3"), bed("amb-night-creatures", 0.30, "NIGHT")], (P / "s02p12.wav", "ratio"), None),
 ("shot_3D", "g09r", 0.0, 3.6, "keep", [bed("amb-dusk-clearing", 0.30, "S3"), bed("amb-night-creatures", 0.35, "NIGHT")], (P / "s02p3.wav", 0.5), None),
 ("shot_4A", "g10t", 0.0, None, "drop", [bed("amb-dusk-clearing", 0.45, "S3"), bed("sfx-game-blips", 0.20, "GAME")], (N / "s03.wav", "ratio"), None),
 ("shot_4B", "g11u", 0.0, None, "drop", [bed("amb-dusk-clearing", 0.45, "S3"), bed("sfx-game-blips", 0.35, "GAME")], (N / "s04.wav", "ratio"), None),
 ("shot_4C", "g12", 0.0, 2.0, "drop", [bed("amb-dusk-clearing", 0.40, "S3"), bed("sfx-game-blips", 0.5, "GAME")], None, None),
 ("shot_4D", "g13s", 0.0, None, "drop", [bed("amb-dusk-clearing", 0.45, "S3")], (N / "s05.wav", "ratio"), None),
 ("shot_4F", "g14w", 0.0, None, "drop", [bed("amb-dusk-clearing", 0.45, "S3")], (P / "s06p1.wav", "ratio"), None),
 ("shot_4G5A", "g25b", 0.0, 11.6, "keep", [bed("amb-dusk-clearing", 0.30, "S3")], (P / "s06p2.wav", 0.3), None),
 ("shot_5B", "g16v", 0.0, None, "drop", [bed("amb-dusk-clearing", 0.45, "S3")], (P / "s07p1.wav", "ratio"), None),
 ("shot_5C", "g17t", 0.0, 3.9, "keep", [bed("amb-dusk-clearing", 0.30, "S3")], (P / "s07p2.wav", 0.4), (str(SFX / "sfx-reward-pop.mp3"), REWARD_POP_S, 0.9)),
 ("shot_5D", "g18w", 0.0, 2.5, "drop", [bed("amb-dusk-clearing", 0.45, "S3")], (N / "s08.wav", "ratio"), None),  # kort afgesneden vóór de herhaalde mondbeweging (ratio 1,49); fade valt eroverheen
]
REWARD_CENTER = [0.88, 0.70]   # [x,y] fractie van het beeld waar de tent popt; na bekijken bijstellen
NO_RETIME = {"shot_5D"}
# gratis reparaties: inzoom (breedtefractie, x-offset, y-offset) om artefacten uit beeld te snijden
ZOOM = {"shot_1C": (0.74, 0.245, 0.02)}   # 1C: door Seedance geplakt MJ-logo linksboven   # mond herhaalt de regel: niet hertimen maar kort afsnijden
# Overgangen (Jorrit 2026-10-12, "a la Star Wars"): klassieke wipes; het volgende shot begint `frames` eerder en overlapt.
TRANSITIONS = {   # v2 (Jorrit: trager, dikkere rand die de overgang volgt): gloeiende band in logo-geel op de wipegrens
 "shot_2B": {"type": "band", "direction": "from-right", "frames": 26, "band": 30},   # 2A -> 2B, mee met de rijrichting
 "shot_5B": {"type": "band", "direction": "from-left", "frames": 24, "band": 30},    # 4G5A -> 5B, tegengesteld
 "shot_5C": {"type": "bandclock", "frames": 30, "band": 26},                          # 5B -> 5C, klok met gloeiende wijzer
 "shot_5D": {"type": "band", "direction": "from-right", "frames": 20, "band": 26},   # 5C -> 5D
}
# subtielere looks (Jorrit "moet toch subtieler"): A3_TR_LOOK=line|shadow|none, A3_TR_BAND=px, A3_TR_OPACITY
for t in TRANSITIONS.values():   # vaste keuze Jorrit 2026-10-12: variant B, zachte schaduwrand 70 px
    t["look"] = "shadow"; t["band"] = 70; t["opacity"] = 1.0
if os.environ.get("A3_TR_LOOK"):
    for t in TRANSITIONS.values():
        t["look"] = os.environ["A3_TR_LOOK"]; t["band"] = int(os.environ.get("A3_TR_BAND", t["band"])); t["opacity"] = float(os.environ.get("A3_TR_OPACITY", 1))
if os.environ.get("A3_NO_TRANSITIONS"): TRANSITIONS = {}
BLING_S = 6.9            # in 1A (nieuwe 1A: jeep staat stil rond 7s); na bekijken van g01r bijstellen

bed_cursor = {}
def bed_filter(idx, b, d, target):
    naam, vol, fade_in, groep, bron_off = b
    key = (groep, naam); off = bed_cursor.get(key, bron_off); bed_cursor[key] = off + d
    gain = target - lufs(SFX / f"{naam}.mp3")
    flt = f"[{idx}:a]aloop=loop=-1:size=2147483647,atrim={off:.3f}:{off + d:.3f},asetpts=PTS-STARTPTS,volume={gain:.2f}dB"
    if fade_in is not None: flt += f",afade=t=in:st=0:d={fade_in:.2f}"
    return flt + ",aresample=44100,pan=stereo|c0=c0|c1=c0"

frames = []; labels = []; report = []; vo_win = {}
# REGEL (Jorrit 2026-10-12): niet praten tijdens een overgang.
#  - volgend shot met lipsync: wipe zo kort dat hij 0,10 s vóór de mondstart klaar is (min. 12 frames);
#  - volgend shot zonder lipsync: regel schuift naar 0,10 s na de wipe (SHIFT_VO);
#  - vorig shot: de wipe begint pas 0,12 s na het einde van de regel; anders wordt het laatste beeld vastgehouden (in de loop).
SHOT_IDS = [x[0] for x in SHOTS]; NEXT_TR = {}; SHIFT_VO = {}
def _lips_at(sid):
    lp = LIPSYNC.get(sid)
    if lp and lp.startswith("crop"):
        unit = next(x[1] for x in SHOTS if x[0] == sid); dk = lp.split(":", 1)[0]
        return json.load(open(V / unit / ("crop-lipsync" + dk[4:]) / "prep.json"))["at"]
    return None
for sid, t in TRANSITIONS.items():
    if sid not in SHOT_IDS or SHOT_IDS.index(sid) == 0: continue
    la = _lips_at(sid); spec = next(x for x in SHOTS if x[0] == sid)
    if la is not None:
        t["frames"] = max(12, min(t["frames"], int((la - 0.10) * FPS)))
    elif spec[6] and isinstance(spec[6][1], (int, float)) and spec[6][1] < t["frames"] / FPS + 0.10:
        SHIFT_VO[sid] = round(t["frames"] / FPS + 0.10, 3)
    NEXT_TR[SHOT_IDS[SHOT_IDS.index(sid) - 1]] = t["frames"]
for sid, src, t0, t1, clipaudio, beds, vo, accent in SHOTS:
    if ONLY and sid not in ONLY: continue
    unit = None
    if not src.endswith(".mp4"):
        unit = src; src = str(V / unit / "clip.mp4")
    if not pathlib.Path(src).exists():
        print(f"{sid}: BRON ONTBREEKT ({src}) -> overgeslagen"); continue
    clip_d = dur(src)
    retime = 1.0; vo_at = None; tpad = 0.0
    warped = (V / unit / "clip-warped.mp4") if unit else None
    bg = (V / unit / "stems/background.wav") if unit else None
    lips = LIPSYNC.get(sid)
    if lips and vo and lips.startswith("crop"):   # uitsnede-lipsync: "crop:<composiet>" of "crop-1024:<composiet>" (map crop-lipsync[-suffix])
        dk, m = lips.split(":", 1); cd_ = V / unit / ("crop-lipsync" + dk[4:])
        pj = json.load(open(cd_ / "prep.json")); src = str(cd_ / f"composite-{m}.mp4") if m != "none" else str(V / unit / "clip.mp4"); clip_d = dur(src)   # none = origineel beeld, regel op de mondstart
        vo = (pathlib.Path(pj["audio"]), pj["at"]); warped = None; report.append(f"{sid}: uitsnede-lipsync {m}, regel op {pj['at']:.2f}s")
        vs = PROJ / "assets/audio/lines/film-v4-sync" / f"{sid.replace('shot_', '')}.wav"
        if os.environ.get("A3_VO_SYNC") and vs.exists():   # v4-regel per woordgroep op het mondritme gelegd (retime_to_clone.py), clip-relatief
            vo = (vs, 0.0); report.append(f"{sid}: v4-regel op mondritme (film-v4-sync)")
    elif lips and vo:
        lj = json.load(open(V / unit / f"lipsync-{lips}/log.json")); src = str(V / unit / f"lipsync-{lips}/out.mp4"); clip_d = dur(src)
        vo = (vo[0], lj["insert_s"]); warped = None; report.append(f"{sid}: lipsync {lips}, regel op {lj['insert_s']:.2f}s")
    if vo and bg and bg.exists() and clipaudio == "drop": clipaudio = "bg"
    if vo and vo[1] == "ratio" and warped and warped.exists():
        # deterministische lipsync-reparatie (lipsync_warp.py): video al per woordgroep op de opname gelegd
        w = json.load(open(V / unit / "sync-warp.json")); src = str(warped); clip_d = dur(src)
        vo = (vo[0], w["audio_delay"]); report.append(f"{sid}: gewarpt ({w['groups']} woordgroepen), audio op {w['audio_delay']:+.2f}s")
    if vo:
        vo = (vo[0] if (lips and str(lips).startswith("crop")) else film_vo(vo[0]), vo[1])
        vfile, at = vo
        if at == "ratio":
            r = ratio_info(unit)
            if not r: print(f"{sid}: geen ratio.json, mondstart 0.4 aangenomen"); at = 0.4
            else:
                at = r["offset_s"]
                if not r["ratio_ok"] and sid not in NO_RETIME:
                    retime = 1.0 / r["ratio"]; at = at * retime
                    report.append(f"{sid}: ratio {r['ratio']} buiten band -> video hertimed x{retime:.3f}")
        if sid in SHIFT_VO and not lips: at = SHIFT_VO[sid]; report.append(f"{sid}: regel naar {at:.2f}s (na de overgang)")
        vo_at = max(at, 0.0)
        vo_trim = -at if at < 0 else 0.0
    end = t1 if t1 is not None else clip_d - 0.15
    d = (end - t0) * retime
    if vo:
        vo_d = dur(vo[0])
        overflow = vo_at + vo_d + 0.10 - (clip_d - t0) * retime
        tpad = 0.0
        if overflow > 0 and (lips or (warped and warped.exists())):
            tpad = overflow + 0.05; clip_d += tpad   # gewarpte clip: laatste frame vasthouden i.p.v. de audio te verschuiven (sync blijft)
            report.append(f"{sid}: video {tpad:.2f}s verlengd met stilstaand eindframe")
            overflow = 0
        if overflow > 0:
            shift = min(overflow, 0.25); vo_at -= shift
            report.append(f"{sid}: filmtake {shift:.2f}s vervroegd (liep {overflow:.2f}s over het clipeinde)")
            if vo_at < 0:
                vo_trim += -vo_at; vo_at = 0.0
        d = max(d, vo_at + vo_d + 0.35) if t1 is None else d
        d = min(d, (clip_d - t0) * retime)
        if sid in NEXT_TR:
            req = vo_at + vo_d + 0.12 + NEXT_TR[sid] / FPS
            if req > d:
                avail = (dur(src) - t0) * retime                     # echte beelden in de bron vanaf t0
                hold = req - d; tpad = max(tpad, req - avail + 0.02); d = req
                report.append(f"{sid}: laatste beeld {hold:.2f}s vastgehouden zodat de overgang na de regel begint")
    inputs = ["-ss", f"{t0:.3f}", "-to", f"{t0 + d / retime:.3f}", "-i", src]
    zoom = ZOOM.get(sid)
    zf = f"crop=iw*{zoom[0]:.3f}:ih*{zoom[0]:.3f}:iw*{zoom[1]:.3f}:ih*{zoom[2]:.3f},scale=1280:720," if zoom else ""
    tp = f"tpad=stop_mode=clone:stop_duration={tpad:.3f}," if vo and tpad else ""
    fc = [f"[0:v]{zf}{tp}setpts=(PTS-STARTPTS)*{retime:.4f},fps={FPS}[v]"]
    idx = 1; layers = []
    if clipaudio == "keep":
        cg = LVL["clip_solo"] - lufs(src, t0, t0 + d / retime)
        fc.append(f"[0:a]asetpts=PTS-STARTPTS,atempo={min(max(1/retime,0.5),2.0):.4f},volume={cg:.2f}dB,aresample=44100,pan=stereo|c0=c0|c1=c1[base]" if retime != 1.0 else f"[0:a]asetpts=PTS-STARTPTS,volume={cg:.2f}dB,aresample=44100,pan=stereo|c0=c0|c1=c1[base]")
        layers.append("[base]")
    if clipaudio == "bg":
        inputs += ["-ss", f"{t0:.3f}", "-i", str(bg)]
        fc.append(f"[{idx}:a]asetpts=PTS-STARTPTS,volume={BG_GAIN_DB:.1f}dB,aresample=44100[bg]"); layers.append("[bg]"); idx += 1
    for bi, b in enumerate(beds):
        target = (LVL["bed_under"] if vo else LVL["bed_solo"]) - (4.0 if clipaudio == "bg" else 0.0) + (LVL["second_bed"] if bi > 0 else 0.0)
        if b[0] == "sfx-game-blips" and not vo: target = -21.0   # 4C: telefoonscherm in beeld, spelgeluid is het hoofdgeluid
        inputs += ["-i", str(SFX / f"{b[0]}.mp3")]; fc.append(bed_filter(idx, b, d, target) + f"[b{idx}]"); layers.append(f"[b{idx}]"); idx += 1
    if vo:
        inputs += ["-i", str(vo[0])]
        dl = int(round(vo_at * 1000)); tr = f"atrim=start={vo_trim:.3f}," if vo_trim else ""
        fc.append(f"[{idx}:a]{tr}asetpts=PTS-STARTPTS,aresample=44100,pan=stereo|c0=c0|c1=c0,adelay={dl}|{dl}[vo]"); layers.append("[vo]"); idx += 1
    accents = [accent] if accent and not isinstance(accent, list) else (accent or [])
    if sid == "shot_3AB":
        accents = accents + [(str(SFX / f"{n}.mp3"), t, 0.7) for n, t in LOOKS_3AB]
    for ai, (afile, at_s, avol) in enumerate(accents):
        inputs += ["-i", afile]; dd = int(at_s * 1000)
        ag = LVL["accent"].get(pathlib.Path(afile).stem, -24) - lufs(afile)
        fc.append(f"[{idx}:a]atrim=0:3.5,volume={ag:.2f}dB,aresample=44100,pan=stereo|c0=c0|c1=c0,adelay={dd}|{dd}[ac{ai}]"); layers.append(f"[ac{ai}]"); idx += 1
    fc.append(f"{''.join(layers)}amix=inputs={len(layers)}:normalize=0,atrim=0:{d:.3f},apad=whole_dur={d:.3f}[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "44100", "-t", f"{d:.3f}", str(OUT / f"{sid}.mp4")], check=True)
    nf = round(d * FPS); frames.append((sid, nf))
    if vo: vo_win[sid] = (max(vo_at, 0.0), max(vo_at, 0.0) + dur(vo[0]))
    print(f"{sid}: {d:.2f}s ({nf} f){'  VO@' + f'{vo_at:.2f}' if vo else ''}{'  retime x%.3f' % retime if retime != 1 else ''}", flush=True)

if ONLY: raise SystemExit(0)
cursor = 0; starts = {}
for k, (sid, f) in enumerate(frames):
    ov = TRANSITIONS[sid]["frames"] if (k > 0 and sid in TRANSITIONS) else 0
    starts[sid] = cursor - ov; cursor = starts[sid] + f
props = {
    "shots": [{"id": sid, "frames": f, **({"transitionIn": TRANSITIONS[sid]} if (k > 0 and sid in TRANSITIONS) else {})} for k, (sid, f) in enumerate(frames)],
    "music": None, "musicVolume": 0.0, "musicEnvelope": [], "clipDir": "expeditie-mj-a3",   # gevuld door muziekblok hieronder
    "titleWindow": [0, min(101, cursor)], "errorWindow": [0, 0],
    "rewardWindow": [starts["shot_5C"] + round(REWARD_POP_S * FPS), starts["shot_5C"] + round(REWARD_POP_S * FPS) + 42] if "shot_5C" in starts else [0, 0],
    "rewardLabel": "De tent", "rewardCenter": REWARD_CENTER,
    "blingWindow": [starts["shot_1A"] + round(BLING_S * FPS), starts["shot_1A"] + round(BLING_S * FPS) + 54] if "shot_1A" in starts else [0, 0],
    "fadeStart": cursor - 10, "outroFrames": 48,
}
# MUZIEK (Jorrit 2026-10-12 "ga door met muziek"): bed uit gen_music.py, volumecurve uit de montage.
# Doelniveaus van de muziek in de mix (LUFS): warm in titel/rit/aankomst/beloning, ver omlaag zodra iemand praat.
MUSIC = os.environ.get("A3_MUSIC")
if MUSIC:
    import shutil
    msrc = PROJ / "assets/music" / MUSIC; shutil.copy(msrc, pathlib.Path("remotion-composer/public/expeditie-mj") / f"a3-{MUSIC}")
    SEC = [(0.0, 21.0), (21.0, 46.5), (46.5, 94.5), (94.5, 110.5), (110.5, 999)]
    sec_lufs = [lufs(msrc, a, min(b, dur(msrc))) for a, b in SEC]
    T_WARM, T_DRIVE, T_NIGHT, T_ARRIVE, T_REWARD, T_DUCK = -29.0, -29.0, -36.0, -30.0, -26.0, -41.0
    sec_target = [T_WARM, T_DRIVE, T_NIGHT, T_ARRIVE, T_REWARD]
    def gain_at(t, duck):
        k = next(i for i, (a, b) in enumerate(SEC) if a <= t < b)
        return round(10 ** (((T_DUCK if duck else sec_target[k]) - sec_lufs[k]) / 20), 4)
    total_f = cursor + props["outroFrames"]
    # per frame: duck als er binnen [vo_start - 0,35 s, vo_end + 0,25 s] van een shot gesproken wordt
    duck = [False] * total_f
    for sid, (a, b) in vo_win.items():
        f0 = starts[sid] + int((a - 0.35) * FPS); f1 = starts[sid] + int((b + 0.25) * FPS)
        for f in range(max(0, f0), min(total_f, f1)): duck[f] = True
    env_ = []; prev = None
    for f in range(0, total_f, 6):
        g = gain_at(f / FPS, duck[f])
        if g != prev: env_.append([f, g]); prev = g
    # zachte overgangen: punten 8 frames uit elkaar laten lopen (lineaire hellingen in de compositie)
    smooth = []
    for i, (f, g) in enumerate(env_):
        if i and f - smooth[-1][0] < 8: f = smooth[-1][0] + 8
        if i: smooth.append([f - 1, smooth[-1][1]])
        smooth.append([f, g])
    smooth = [[0, 0.0], [8, smooth[0][1]]] + smooth[1:] + [[total_f - 30, smooth[-1][1]], [total_f - 1, 0.0]]
    clean = []
    for f, g in smooth:
        if clean and f <= clean[-1][0]: continue
        clean.append([f, g])
    props.update({"music": f"a3-{MUSIC}", "musicVolume": 0.0, "musicEnvelope": clean})
    report.append(f"muziek {MUSIC}: secties {[round(x, 1) for x in sec_lufs]} LUFS, {len(clean)} envelopepunten")
(PROJ / "artifacts/remotion_props.json").write_text(json.dumps(props, indent=1))
(PROJ / "artifacts/draft_label_windows.json").write_text(json.dumps([{"shot": sid, "start": starts[sid] / FPS, "end": (starts[sid] + f) / FPS} for sid, f in frames], indent=1))
(PROJ / f"artifacts/compose_report_draft{DRAFT}.json").write_text(json.dumps({"draft": DRAFT, "frames": frames, "total_s": cursor / FPS, "retimes": report, "vo_win": vo_win, "starts": starts}, indent=1))
print(f"draft {DRAFT}: {cursor} frames = {cursor / FPS:.2f}s + outro 2s; hertimingen: {report or 'geen'}")
