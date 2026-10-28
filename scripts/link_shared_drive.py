"""Link projects/ and media/ to the shared Mediajungle drive.

Final products (project workspaces, renders, posters, exports) live on the
shared Google Drive, not in git. Everyone has that drive at a different
absolute path (the mount contains their own e-mail address, and macOS may say
"Gedeelde drives" instead of "Shared drives"). This script finds it and
creates two git-ignored symlinks in the repo root:

    projects -> <drive>/Mediajungle Projecten/03. Projecten/OpenMontage/projects
    media    -> <drive>/Mediajungle Projecten/03. Projecten/OpenMontage/media

After that, everything refers to repo-relative paths (projects/<id>/...,
media/...) and works the same on every machine.

Usage:
    python scripts/link_shared_drive.py            # detect and link
    python scripts/link_shared_drive.py --status   # show where the links point

Override detection by setting OPENMONTAGE_SHARED_DIR (in the shell or in
.env) to the OpenMontage folder on the drive.
"""
from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_SUBPATH = Path("Mediajungle Projecten") / "03. Projecten" / "OpenMontage"
LINKS = ("projects", "media")


def env_override() -> str | None:
    value = os.environ.get("OPENMONTAGE_SHARED_DIR")
    if value:
        return value
    env_file = REPO_ROOT / ".env"
    if not env_file.is_file():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        key, sep, val = line.strip().partition("=")
        if sep and key.strip() == "OPENMONTAGE_SHARED_DIR":
            return val.strip().strip("'\"") or None
    return None


def find_shared_dir() -> Path:
    override = env_override()
    if override:
        path = Path(override).expanduser()
        if not path.is_dir():
            sys.exit(f"OPENMONTAGE_SHARED_DIR bestaat niet: {path}")
        return path

    candidates = []
    for drives in ("Shared drives", "Gedeelde drives"):
        pattern = str(Path.home() / "Library" / "CloudStorage" / "GoogleDrive-*" / drives)
        candidates += [Path(p) / SHARED_SUBPATH for p in glob.glob(pattern)]
    found = [c for c in candidates if c.is_dir()]
    if len(found) == 1:
        return found[0]
    if not found:
        sys.exit(
            "Kon de gedeelde drive niet vinden. Staat Google Drive for desktop aan en\n"
            f"zie je '{SHARED_SUBPATH}' in Finder? Zet anders OPENMONTAGE_SHARED_DIR in .env."
        )
    listing = "\n  ".join(str(f) for f in found)
    sys.exit(f"Meerdere kandidaten gevonden; kies er een via OPENMONTAGE_SHARED_DIR in .env:\n  {listing}")


def link(name: str, target: Path) -> None:
    here = REPO_ROOT / name
    target.mkdir(parents=True, exist_ok=True)
    if here.is_symlink():
        if Path(os.readlink(here)) == target:
            print(f"  ok       {name} -> {target}")
            return
        here.unlink()
    elif here.is_dir():
        if any(here.iterdir()):
            sys.exit(
                f"{name}/ is een gewone map met inhoud. Verplaats de inhoud naar\n"
                f"  {target}\nen draai dit script opnieuw."
            )
        here.rmdir()
    elif here.exists():
        sys.exit(f"{name} bestaat al en is geen map of link; ruim het eerst op.")
    here.symlink_to(target, target_is_directory=True)
    print(f"  linked   {name} -> {target}")


def status() -> None:
    for name in LINKS:
        here = REPO_ROOT / name
        if here.is_symlink():
            state = "ok" if here.exists() else "KAPOT"
            print(f"  {state:8} {name} -> {os.readlink(here)}")
        elif here.is_dir():
            print(f"  LOKAAL   {name}/ is een gewone map (niet gedeeld)")
        else:
            print(f"  ONTBREEKT {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--status", action="store_true", help="alleen tonen, niets wijzigen")
    args = parser.parse_args()
    if args.status:
        status()
        return
    shared = find_shared_dir()
    print(f"Gedeelde map: {shared}")
    for name in LINKS:
        link(name, shared / name)


if __name__ == "__main__":
    main()
