# -*- coding: utf-8 -*-
"""Retakeronde 4: goedgekeurde drafts afmaken op 1080p (bytedance/seedance-2.5/draft-complete, go Jorrit 2026-10-12).
Per unit: clip-1080.mp4 (origineel) + clip.mp4 (1280x720 lanczos, werkkopie voor montage); draft.mp4 blijft bewaard.
    PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/complete4.py [unit ...]"""
import json, pathlib, subprocess, sys, time, concurrent.futures as cf
sys.path.insert(0, str(pathlib.Path.cwd()))
from tools import atlas_client
V = pathlib.Path("projects/expeditie-mj-animatie3/assets/video/units")
UNITS = [a for a in sys.argv[1:]] or ["g04w", "g05u", "g22b", "g23d", "g11u", "g25b", "g16v"]
key = atlas_client.get_api_key()
def run(u):
    D = V / u; log = json.load(open(D / "log.json")); did = log["draft_id"]; t0 = time.time()
    try:
        pid = atlas_client.submit(atlas_client.GENERATE_VIDEO_ENDPOINT, {"model": "bytedance/seedance-2.5/draft-complete", "draft_id": did}, key)
        log["complete"] = {"prediction_id": pid}; (D / "log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1)); print(f"{u}: ingediend {pid}", flush=True)
        data = atlas_client.poll(pid, key, interval=8.0, timeout=3000.0); log["complete"]["source_url"] = data["outputs"][0]
        atlas_client.download(data["outputs"][0], D / "clip-1080.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(D / "clip-1080.mp4"), "-vf", "scale=1280:720:flags=lanczos,fps=24", "-c:v", "libx264", "-crf", "14",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(D / "clip.mp4")], check=True)
        pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,r_frame_rate,codec_name", "-show_entries", "format=duration",
                             "-of", "json", str(D / "clip-1080.mp4")], capture_output=True, text=True).stdout
        log["complete"]["probe"] = json.loads(pr); log["complete"]["success"] = True
    except Exception as e:
        log.setdefault("complete", {})["success"] = False; log["complete"]["error"] = str(e)[:600]
    log["complete"]["seconds"] = round(time.time() - t0); (D / "log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1))
    print(f"{u}: {'klaar' if log['complete']['success'] else 'FOUT ' + log['complete']['error'][:200]} ({log['complete']['seconds']}s)", flush=True)
    return log["complete"]["success"]
with cf.ThreadPoolExecutor(4) as ex: ok = list(ex.map(run, UNITS))
print("ALLES KLAAR", sum(ok), "/", len(ok))
