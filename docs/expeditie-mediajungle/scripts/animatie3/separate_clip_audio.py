# -*- coding: utf-8 -*-
"""Seedance-clipaudio splitsen in stem (kloonstem) en achtergrond (ambiance, sfx, muziek) met Demucs htdemucs_ft,
lokaal en gratis. Zonder torchaudio: audio in/uit via ffmpeg (float32 raw). De achtergrond = drums+bass+other.
    PYTHONPATH=. .venv/bin/python projects/expeditie-mj-animatie3/separate_clip_audio.py <unit> [model]
Schrijft units/<unit>/stems/{vocals.wav, background.wav}."""
import pathlib, subprocess, sys, numpy as np, torch
from demucs.pretrained import get_model
from demucs.apply import apply_model
PROJ = pathlib.Path("projects/expeditie-mj-animatie3"); V = PROJ / "assets/video/units"
unit = sys.argv[1]; name = sys.argv[2] if len(sys.argv) > 2 else "htdemucs_ft"
src = V / unit / "clip.mp4"; out = V / unit / "stems"; out.mkdir(exist_ok=True)
model = get_model(name); model.eval(); sr = model.samplerate
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vn", "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
wav = torch.from_numpy(np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy())
ref = wav.mean(0); mean, std = ref.mean(), ref.std() + 1e-8
dev = "mps" if torch.backends.mps.is_available() else "cpu"
with torch.no_grad():
    sources = apply_model(model, ((wav - mean) / std)[None], device=dev, shifts=2, split=True, overlap=0.25, progress=False)[0]
sources = sources * std + mean
names = model.sources; vi = names.index("vocals")
vocals = sources[vi]; background = sum(sources[i] for i in range(len(names)) if i != vi)
def save(t, p):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(p)],
                   input=t.T.contiguous().numpy().astype(np.float32).tobytes(), check=True)
save(vocals, out / "vocals.wav"); save(background, out / "background.wav")
print(f"{unit}: {name} op {dev}, bronnen {names} -> {out}")
