# -*- coding: utf-8 -*-
"""Uitsnede-lipsync (voorstel 1, akkoord Jorrit 2026-10-12): alleen het gezicht van de spreker, alleen het spreekvenster.
  1. prep  : gezicht volgen (template-matching op een vast gelaatsdeel, gladgestreken), vierkante uitsnede per frame,
             opgeschaald naar 512x512, voor [start-marge, eind+marge]; bijbehorend audiovenster. Plus een identiteitstest:
             de onbewerkte uitsnede terugplakken moet het origineel opleveren (controle op de geometrie).
  2. submit: uitsnede + audio naar Atlas (sync/lipsync-v3 of veed/lipsync), gefactureerd per seconde van het venster.
  3. paste : alleen de mond (zacht ellipsmasker) terug in het origineel, in- en uitgefaded op het spreekvenster.
Config per shot in CROP_CFG. Gebruik:
    lipsync: crop_lipsync.py <shot> prep|submit <model>|paste <model> [--dry-run]"""
import json, pathlib, subprocess, sys, time, numpy as np, cv2
sys.path.insert(0, str(pathlib.Path.cwd()))
PROJ = pathlib.Path("projects/expeditie-mj-animatie3"); V = PROJ / "assets/video/units"
import os
W, H, FPS = 1280, 720, 24
S = int(os.environ.get("A3_S", 1024))   # uitsnede-resolutie naar het model; terugplakken leest altijd op S
# anker = (x, y, w, h) gelaatsdeel op anker_t; mond = (dx, dy, ax, ay) t.o.v. ankerorigine; box = zijde van de uitsnede;
# box_off = (dx, dy) middelpunt uitsnede t.o.v. ankerorigine; audio = filmregel; at = start regel in de clip
CROP_CFG = {
 "3AB": {"unit": "g24", "anchor_t": 8.5, "anchor": (770, 280, 180, 110), "mouth": (75, 125, 52, 40), "box": 340, "box_off": (90, 90), "audio": None, "at": 6.0},
 "4B":  {"unit": "g11u", "anchor_t": 2.5, "anchor": (400, 290, 110, 45), "mouth": (55, 85, 30, 18), "box": 300, "box_off": (58, 20), "audio": None, "at": None},
 "1B":  {"unit": "g02t", "anchor_t": 1.20, "anchor": (400, 255, 115, 50), "mouth": (52, 107, 34, 22), "box": 300, "box_off": (57, 50), "audio": None, "at": None},
 "1C":  {"unit": "g20",  "anchor_t": 2.85, "anchor": (670, 240, 95, 35),  "mouth": (52, 50, 18, 12),  "box": 230, "box_off": (60, 15), "audio": None, "at": None},
 "4A":  {"unit": "g10t", "anchor_t": 2.57, "anchor": (765, 275, 140, 50), "mouth": (57, 83, 28, 22),  "box": 340, "box_off": (70, 25), "audio": None, "at": None},
 "4D":  {"unit": "g13s", "anchor_t": 2.81, "anchor": (450, 195, 95, 55),  "mouth": (50, 95, 28, 18),  "box": 300, "box_off": (30, 45), "audio": None, "at": None,
         "extra_anchors": [(1.0, (480, 225, 100, 60), (47, 97))]},   # profiel
 "4F":  {"unit": "g14w", "anchor_t": 2.30, "anchor": (490, 215, 85, 45),  "mouth": (41, 67, 22, 14),  "box": 230, "box_off": (30, 30), "audio": None, "at": None},
 "5B":  {"unit": "g16v", "anchor_t": 2.0, "anchor": (585, 255, 70, 30), "mouth": (32, 42, 14, 9), "box": 160, "box_off": (35, 13), "audio": None, "at": None},
 "5D":  {"unit": "g18w", "anchor_t": 1.10, "anchor": (335, 195, 100, 45), "mouth": (49, 84, 26, 16),  "box": 260, "box_off": (45, 55), "audio": None, "at": None},
}
MODELS = {"sync3": ("sync/lipsync-v3", 0.22, {"sync_mode": "cut_off"}), "veed": ("veed/lipsync", 0.013, {})}
MARGIN, FADE = 0.5, 0.15
SHARPEN = {"sync3": 0.0, "veed": 0.3}   # unsharp-mask-sterkte op de teruggeplakte mond (Veed levert een gladdere mond)
import os
if os.environ.get("A3_SHARPEN"): SHARPEN.update(json.loads(os.environ["A3_SHARPEN"]))
shot, step = sys.argv[1], sys.argv[2]; cfg = CROP_CFG[shot]; U = V / cfg["unit"]; D = U / ("crop-lipsync" + os.environ.get("A3_DIR", "-1024")); D.mkdir(exist_ok=True)
cfg_file = D / "cfg.json"
if cfg_file.exists(): cfg.update({k: v for k, v in json.load(open(cfg_file)).items() if k in ("audio", "at")})
# Regel: de filmregel begint waar Seedance' eigen mond begint (eerste woord kloonstem, Azure, units/<u>/sync.json).
# Les 3AB: regel op 7,0s terwijl de mond pas op 7,87s opengaat (camera rijdt in tot ~7,5s) -> "mond 1 s te laat".
if cfg.get("at") in (None, "mouth") and (U / "sync.json").exists():
    cfg["at"] = json.load(open(U / "sync.json"))["pairs"][0]["clip_t0"]
    # past de regel niet meer in de clip vanaf de mondstart, dan zo veel eerder beginnen dat hij er precies in past
    if cfg.get("audio"):
        _cd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(U / "clip.mp4")], capture_output=True, text=True).stdout)
        _ad = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(cfg["audio"])], capture_output=True, text=True).stdout)
        cfg["at"] = round(min(cfg["at"], _cd - _ad - 0.05), 3)
def run(c): subprocess.run(["ffmpeg", "-v", "error", "-y", *c], check=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())
def read_frames(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
def track(frames):
    # meerdere ankers mogelijk (cfg["extra_anchors"]: [(anchor_t, (x,y,w,h), (mond_dx, mond_dy))]) voor hoofden die draaien;
    # per beeld wint het anker met de hoogste score; de positie wordt omgerekend naar de oorsprong van het hoofdanker,
    # zodat pos + cfg["mouth"][:2] altijd het mondpunt is.
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    specs = [(cfg["anchor_t"], cfg["anchor"], cfg["mouth"][:2])] + list(cfg.get("extra_anchors", []))
    tpls = []
    for at_, (TX, TY, TW, TH), (mdx, mdy) in specs:
        R = max(TW, TH); tpls.append((gray[int(at_ * FPS)][TY:TY + TH, TX:TX + TW], (max(0, TX - R), max(0, TY - R), min(W, TX + TW + R), min(H, TY + TH + R)),
                                      (mdx - cfg["mouth"][0], mdy - cfg["mouth"][1])))
    pos, sc = [], []
    for g in gray:
        best = None
        for tpl, (x0, y0, x1, y1), (ox, oy) in tpls:
            r = cv2.matchTemplate(g[y0:y1, x0:x1], tpl, cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(r)
            if best is None or mx > best[0]: best = (mx, (x0 + loc[0] + ox, y0 + loc[1] + oy))
        pos.append(best[1]); sc.append(best[0])
    a = np.array(pos, float); k = 7; pad = np.pad(a, ((k // 2, k // 2), (0, 0)), mode="edge")
    return np.stack([np.convolve(pad[:, c], np.ones(k) / k, mode="valid") for c in range(2)], 1), np.array(sc)
def box_at(p):
    B = cfg["box"]; cx, cy = p[0] + cfg["box_off"][0], p[1] + cfg["box_off"][1]
    x = int(round(min(max(cx - B / 2, 0), W - B))); y = int(round(min(max(cy - B / 2, 0), H - B))); return x, y, B
def window():
    ad = dur(cfg["audio"]); a = max(0.0, cfg["at"] - MARGIN); b = min(dur(U / "clip.mp4"), cfg["at"] + ad + MARGIN); return a, b, ad
def write_video(frames, path, size):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)
    for f in frames: p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close(); p.wait()

if step == "prep":
    assert cfg["audio"], "eerst audio + at zetten in crop-lipsync/cfg.json"
    fr = read_frames(U / "clip.mp4"); pos, sc = track(fr); a, b, ad = window(); i0, i1 = int(round(a * FPS)), int(round(b * FPS))
    crops, boxes = [], []
    for i in range(i0, min(i1, len(fr))):
        x, y, B = box_at(pos[i]); boxes.append((x, y, B)); crops.append(cv2.resize(fr[i][y:y + B, x:x + B], (S, S), interpolation=cv2.INTER_LANCZOS4))
    if os.environ.get("A3_FREEZE"):
        # Optie 1 (Jorrit 2026-10-12, test 1C+4B): originele mond stilzetten zodat Sync 3 het ritme alleen uit de stem haalt.
        # Rustbeeld = beeld met de lichtste (meest gesloten) mond; dat mondgebied wordt per beeld met de mond mee verschoven
        # en met een zachte rand over de uitsnede gelegd. Gebied = union-masker van de vorige Sync 3-run (wat Sync 3 aanraakt), anders ovaal.
        write_video(crops, D / "crop-orig.mp4", (S, S))
        dx, dy, ax, ay = cfg["mouth"]
        mc = [((pos[i0 + k][0] + dx - b[0]) * S / b[2], (pos[i0 + k][1] + dy - b[1]) * S / b[2]) for k, b in enumerate(boxes)]
        sc_ = S / boxes[0][2]
        grays = [cv2.cvtColor(c, cv2.COLOR_BGR2GRAY).astype(np.float32) for c in crops]
        def mouth_open(k):   # gesloten mond: geen donkere opening en geen tanden -> weinig pixels ver onder/boven de mediane huidtint
            mm = np.zeros((S, S), np.uint8); cv2.ellipse(mm, (int(mc[k][0]), int(mc[k][1])), (max(4, int(ax * sc_ * 0.8)), max(4, int(ay * sc_ * 0.8))), 0, 0, 360, 1, -1)
            v = grays[k][mm > 0]; med = np.median(v); return float(((v < 0.6 * med) | (v > 1.35 * med)).mean())
        opn = np.array([mouth_open(k) for k in range(len(crops))])
        closed = np.nonzero(opn <= np.percentile(opn, float(os.environ.get("A3_FREEZE_PCT", 20))))[0]
        top = slice(int(S * 0.15), int(S * 0.5))   # houding vergelijken op het bovenste deel van het gezicht (ogen/bril/haar)
        def sim(a, b):
            x, y = grays[a][top].ravel(), grays[b][top].ravel(); x = x - x.mean(); y = y - y.mean()
            return float((x * y).sum() / (np.sqrt((x * x).sum() * (y * y).sum()) + 1e-6))
        nearest = []
        for k in range(len(crops)):
            cand = sorted(closed, key=lambda c: abs(c - k))[:8]
            sc_best = max(cand, key=lambda c: sim(k, c) - 0.004 * abs(c - k))
            nearest.append(int(sc_best) if sim(k, sc_best) >= float(os.environ.get("A3_FREEZE_SIM", 0.75)) else None)
        kref = int(closed[np.argmin(opn[closed])])
        prev_u = U / cfg["unit"] / "crop-lipsync-1024" / "union-mask-sync3.png"
        if prev_u.exists():
            fm = cv2.imread(str(prev_u), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0
            fm = cv2.resize(fm, (S, S)); fm = cv2.dilate((fm > 0.3).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))).astype(np.float32)
            # masker is hoofd-relatief t.o.v. de mediane mondpositie; per beeld verschuiven naar de eigen mondpositie
            base = (float(np.median([m[0] for m in mc])), float(np.median([m[1] for m in mc])))
        else:
            fm = np.zeros((S, S), np.float32); base = mc[kref]
            cv2.ellipse(fm, (int(base[0]), int(base[1] + ay * sc_ * 0.5)), (int(ax * sc_ * 1.9), int(ay * sc_ * 2.6)), 0, 0, 360, 1.0, -1)
        fm = cv2.GaussianBlur(fm, (0, 0), 10)
        frozen = []; orig = [c.astype(np.float32) for c in crops]
        for k in range(len(crops)):
            kr = nearest[k]
            if kr is None: frozen.append(crops[k]); continue   # geen bronbeeld met dezelfde houding: origineel laten
            tx, ty = mc[k][0] - mc[kr][0], mc[k][1] - mc[kr][1]
            refk = cv2.warpAffine(orig[kr], np.float32([[1, 0, tx], [0, 1, ty]]), (S, S), borderMode=cv2.BORDER_REPLICATE)
            mk = cv2.warpAffine(fm, np.float32([[1, 0, mc[k][0] - base[0]], [0, 1, mc[k][1] - base[1]]]), (S, S))[..., None]
            frozen.append((crops[k].astype(np.float32) * (1 - mk) + refk * mk).astype(np.uint8))
        crops = frozen; cv2.imwrite(str(D / "freeze-ref.png"), crops[kref])
        print(f"   bevroren: {len(closed)} gesloten beelden als bron, {len(set(n for n in nearest if n is not None))} gebruikt, {sum(n is None for n in nearest)} beelden ongemoeid; strakste {kref} ({(i0 + kref) / FPS:.2f} s)")
    write_video(crops, D / "crop.mp4", (S, S))
    ms = int(round((cfg["at"] - a) * 1000))
    run(["-i", str(cfg["audio"]), "-af", f"adelay={ms}|{ms},apad=whole_dur={b - a:.3f}", "-t", f"{b - a:.3f}", "-ar", "44100", "-ac", "1", str(D / "crop-audio.wav")])
    json.dump({"window": [a, b], "at": cfg["at"], "audio": str(cfg["audio"]), "frames": [i0, i0 + len(boxes)], "boxes": boxes, "track_score_min": float(sc[i0:i1].min()), "track_score_median": float(np.median(sc[i0:i1]))}, open(D / "prep.json", "w"))
    # identiteitstest: crop terug naar boxgrootte en terugplakken zonder masker -> verschil met origineel
    errs = []
    for k, (x, y, B) in enumerate(boxes):
        back = cv2.resize(crops[k], (B, B), interpolation=cv2.INTER_AREA); errs.append(np.abs(back.astype(int) - fr[i0 + k][y:y + B, x:x + B].astype(int)).mean())
    print(f"{shot}: venster {a:.2f}-{b:.2f}s ({b - a:.2f}s), box {cfg['box']}px -> {S}px, tracking-score min {sc[i0:i1].min():.2f} / mediaan {np.median(sc[i0:i1]):.2f}, identiteitsfout {np.mean(errs):.2f}")
    for m, (mid, rate, _) in MODELS.items(): print(f"   kosten {m}: ${rate * (b - a):.2f}")
    # controlebeeld: box + mondellips op 4 frames
    sheet = []
    for k in np.linspace(0, len(boxes) - 1, 4).astype(int):
        f = fr[i0 + k].copy(); x, y, B = boxes[k]; p = pos[i0 + k]; dx, dy, ax, ay = cfg["mouth"]
        cv2.rectangle(f, (x, y), (x + B, y + B), (255, 0, 0), 2); cv2.ellipse(f, (int(p[0] + dx), int(p[1] + dy)), (ax, ay), 0, 0, 360, (0, 255, 0), 2)
        sheet.append(cv2.resize(f[max(0, y - 40):min(H, y + B + 40), max(0, x - 40):min(W, x + B + 40)], (300, 300)))
    cv2.imwrite(str(D / "prep-check.png"), np.hstack(sheet))

elif step == "submit":
    from tools import atlas_client
    m = sys.argv[3]; mid, rate, extra = MODELS[m]; pj = json.load(open(D / "prep.json")); a, b = pj["window"]
    log = {"shot": shot, "model": mid, "window": [a, b], "est_cost_usd": round(rate * (b - a), 2)}
    print(json.dumps(log))
    if "--dry-run" in sys.argv: raise SystemExit(0)
    key = atlas_client.get_api_key(); t0 = time.time()
    log["video_url"] = atlas_client.upload_media(D / "crop.mp4", key); log["audio_url"] = atlas_client.upload_media(D / "crop-audio.wav", key)
    log["prediction_id"] = pid = atlas_client.submit(atlas_client.GENERATE_VIDEO_ENDPOINT, {"model": mid, "video_url": log["video_url"], "audio_url": log["audio_url"], **extra}, key)
    (D / f"log-{m}.json").write_text(json.dumps(log, indent=1)); print("ingediend:", pid, flush=True)
    data = atlas_client.poll(pid, key, interval=5.0, timeout=1800.0); log["source_url"] = data["outputs"][0]; log["seconds"] = round(time.time() - t0)
    atlas_client.download(log["source_url"], D / f"out-{m}.mp4"); (D / f"log-{m}.json").write_text(json.dumps(log, indent=1))
    print("klaar:", D / f"out-{m}.mp4", f"{log['seconds']}s", flush=True)

elif step == "paste":
    m = sys.argv[3]; src = D / ("crop.mp4" if m == "identity" else f"out-{m}.mp4")
    pj = json.load(open(D / "prep.json")); a, b = pj["window"]; i0 = pj["frames"][0]; boxes = pj["boxes"]
    fr = read_frames(U / "clip.mp4").copy(); pos, score = track(fr)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vf", f"fps={FPS},scale={S}:{S}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    ls = np.frombuffer(raw, np.uint8).reshape(-1, S, S, 3)
    ad = dur(cfg["audio"]); s0, s1 = cfg["at"], cfg["at"] + ad; dx, dy, ax, ay = cfg["mouth"]
    MASK_MODE = os.environ.get("A3_MASK", "union"); DIFF_T = float(os.environ.get("A3_DIFF_T", 10)); DIL = int(os.environ.get("A3_DIL", 9)); FEATHER = float(os.environ.get("A3_FEATHER", 3.0))
    prev_a = None; ghost = []; union = None
    uf = os.environ.get("A3_UNION_FROM")
    if MASK_MODE == "union" and uf:   # masker van een ander model hergebruiken (bv. Seedance-verfijning op de Veed-mond)
        union = cv2.imread(str(D / f"union-mask-{uf}.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0
    elif MASK_MODE == "union":
        acc = np.zeros((S, S), np.float32)
        for k, (x, y, B) in enumerate(boxes):
            i = i0 + k
            if i >= len(fr) or k >= len(ls): break
            t = i / FPS
            if not (s0 <= t <= s1) or score[i] < 0.6: continue
            o512 = cv2.resize(fr[i][y:y + B, x:x + B], (S, S), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
            d = np.abs(cv2.GaussianBlur(ls[k].astype(np.float32), (0, 0), 2) - cv2.GaussianBlur(o512, (0, 0), 2)).max(2)
            acc = np.maximum(acc, (d > DIFF_T).astype(np.float32) * (1.0 if acc.sum() == 0 else 1.0))
        # alleen het grootste samenhangende gebied rond de mond houden (ruis elders weg)
        n_, lab, st, _ = cv2.connectedComponentsWithStats((acc > 0).astype(np.uint8))
        mcx, mcy = int(np.median([pos[i0 + k][0] + dx - b[0] for k, b in enumerate(boxes)]) * S / boxes[0][2]), int(np.median([pos[i0 + k][1] + dy - b[1] for k, b in enumerate(boxes)]) * S / boxes[0][2])
        keep = lab[min(max(mcy, 0), S - 1), min(max(mcx, 0), S - 1)]
        u = (lab == keep).astype(np.uint8) if keep > 0 else (acc > 0).astype(np.uint8)
        u = cv2.morphologyEx(u, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
        u = cv2.dilate(u, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (DIL * 2, DIL * 2))).astype(np.float32)
        # bovengrens: niets boven de neus (ogen/bril blijven origineel); zachte overgang van 1,4*ay naar 0,9*ay boven de mond
        ays = ay * S / boxes[0][2]; yy = np.arange(S, dtype=np.float32)[:, None]
        u *= np.clip((yy - (mcy - 1.4 * ays)) / (0.5 * ays), 0, 1)
        union = cv2.GaussianBlur(u, (0, 0), FEATHER * 2.5)
        cv2.imwrite(str(D / f"union-mask-{m}.png"), (union * 255).astype(np.uint8))
    for k, (x, y, B) in enumerate(boxes):
        i = i0 + k
        if i >= len(fr) or k >= len(ls): break
        t = i / FPS; gate = float(np.clip((t - (s0 - FADE)) / FADE, 0, 1) * np.clip(((s1 + FADE) - t) / FADE, 0, 1))
        gate *= float(np.clip((score[i] - 0.55) / 0.15, 0, 1))   # gezicht kwijt (camerabeweging, wegdraaien) -> origineel laten staan
        if gate <= 0: continue
        back = cv2.resize(ls[k], (B, B), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)   # AREA kostte ~30% scherpte (gemeten)
        amt = SHARPEN.get(m, 0.0)
        if amt: back = np.clip(back + amt * (back - cv2.GaussianBlur(back, (0, 0), 1.2)), 0, 255)
        lip = float(os.environ.get("A3_LIP", 0.8 if m.startswith("veed") else 0))
        if lip:   # gerichte lipnaslijping: alleen een band rond de mond (lipranden, onderlip), grovere straal
            lb = np.zeros((B, B), np.float32); lcx, lcy = int(pos[i][0] + dx - x), int(pos[i][1] + dy - y)
            cv2.ellipse(lb, (lcx, lcy + int(ay * 0.15)), (int(ax * 1.05), int(ay * 1.0)), 0, 0, 360, 1.0, -1); lb = cv2.GaussianBlur(lb, (0, 0), ax * 0.2)[..., None]
            back = np.clip(back + lip * lb * (back - cv2.GaussianBlur(back, (0, 0), float(os.environ.get("A3_LIP_SIGMA", 2.0)))), 0, 255)
        cx, cy = int(pos[i][0] + dx - x), int(pos[i][1] + dy - y)
        reg0 = fr[i][y:y + B, x:x + B].astype(np.float32)
        DET = float(os.environ.get("A3_DETAIL", 1.0 if m.startswith("veed") else 0))
        if DET:
            # detailoverdracht: grove vorm/schaduw van het model, fijn detail van het (scherpe) origineel waar beide
            # op grove schaal overeenkomen (huid onder de onderlip, kin in rust); waar de mond echt anders staat blijft modeldetail
            sg = float(os.environ.get("A3_DETAIL_SIGMA", 2.5)); kk = float(os.environ.get("A3_DETAIL_K", 12.0))
            lowV = cv2.GaussianBlur(back, (0, 0), sg); lowO = cv2.GaussianBlur(reg0, (0, 0), sg)
            agr = np.exp(-(cv2.GaussianBlur(np.abs(lowV - lowO).max(2), (0, 0), 2.0) / kk) ** 2)[..., None] * DET
            back = np.clip(lowV + agr * (reg0 - lowO) + (1 - agr) * (back - lowV), 0, 255)
        dif = np.abs(cv2.GaussianBlur(back, (0, 0), 1.5) - cv2.GaussianBlur(reg0, (0, 0), 1.5)).max(2)
        if MASK_MODE == "union":
            msk = cv2.resize(union, (B, B), interpolation=cv2.INTER_LINEAR) * gate * float(np.clip((score[i] - 0.55) / 0.15, 0, 1))
            ghost.append(float((msk * (1 - msk) * dif).sum() / max((msk * (1 - msk)).sum(), 1e-6)))
        elif MASK_MODE == "ellipse":
            msk = np.zeros((B, B), np.float32); cv2.ellipse(msk, (cx, cy), (ax, ay), 0, 0, 360, 1.0, -1)
            msk = cv2.GaussianBlur(msk, (0, 0), max(ax, ay) * 0.25) * gate
            ghost.append(float((msk * (1 - msk) * dif).sum() / max((msk * (1 - msk)).sum(), 1e-6)))
        else:
            # overeenstemmingsmasker: alfa = 1 overal waar het model het beeld veranderde (mond, kaak, kin), binnen een
            # onderste-gezichtsgebied; de zachte overgang valt daardoor alleen waar origineel en uitvoer gelijk zijn (geen geest).
            roi = np.zeros((B, B), np.float32); cv2.ellipse(roi, (cx, cy + int(ay * 0.6)), (int(ax * 1.9), int(ay * 2.4)), 0, 0, 360, 1.0, -1)
            core = np.zeros((B, B), np.float32); cv2.ellipse(core, (cx, cy), (int(ax * 0.8), int(ay * 0.8)), 0, 0, 360, 1.0, -1)
            chg = ((dif > DIFF_T) & (roi > 0)).astype(np.uint8)
            chg = cv2.dilate(chg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (DIL, DIL))).astype(np.float32)
            a = np.maximum(chg, core) * roi
            a = cv2.GaussianBlur(a, (0, 0), FEATHER)
            prev_a = a if prev_a is None or prev_a.shape != a.shape else np.maximum(a, 0.5 * prev_a)   # temporeel stabiel
            msk = np.clip(prev_a, 0, 1) * gate; prev_a = a
            ghost.append(float((msk * (1 - msk) * dif).sum() / max((msk * (1 - msk)).sum(), 1e-6)))
        reg = fr[i][y:y + B, x:x + B].astype(np.float32)
        fr[i][y:y + B, x:x + B] = (reg * (1 - msk[..., None]) + back * msk[..., None]).astype(np.uint8)
    tag = os.environ.get("A3_TAG", ""); out = D / f"composite-{m}{tag}.mp4"; write_video(fr, out, (W, H))
    print("composiet:", out, f"| masker {MASK_MODE}" + (f", geest-energie in overgang {np.mean(ghost):.2f}" if ghost else ""))
