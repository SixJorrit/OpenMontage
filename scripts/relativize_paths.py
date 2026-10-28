"""Rewrite machine-specific absolute paths to repo-relative ones.

projects/ and media/ live on the shared drive (see link_shared_drive.py), so a
path like /Users/<name>/dev/OpenMontage/projects/x/... only works on one
machine. This script rewrites them so the files work for everyone:

    "/Users/<name>/.../OpenMontage/projects/x/a.png"  -> "projects/x/a.png"
    "/Users/<name>/.../OpenMontage"                   -> "."
    file:///.../projects/x/a.png   (html)             -> ../a.png   (relative to the html)
    file '/.../projects/x/a.mp4'   (ffmpeg concat)    -> file 'a.mp4' (relative to the list)

Repo-relative paths assume the repo root as working directory, which is
already the OpenMontage convention. Paths into the drive's own folder
(.../Mediajungle Projecten/03. Projecten/OpenMontage/...) are handled the same
way, since tools that resolve() a path end up there.

Absolute paths that point anywhere else (a Dropbox, ~/Library/Fonts) cannot be
fixed automatically; they are listed so someone can move the source material.

Usage:
    python scripts/relativize_paths.py --check   # report, exit 1 if fixable paths remain
    python scripts/relativize_paths.py           # rewrite in place
    python scripts/relativize_paths.py projects/expeditie-mj-animatie3
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote, unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TARGETS = ("projects", "media", "docs", "remotion-composer/projects")
TEXT_SUFFIXES = {
    ".json", ".jsonl", ".md", ".txt", ".html", ".htm", ".py", ".yaml", ".yml",
    ".log", ".csv", ".ts", ".tsx", ".js", ".sh", ".srt", ".vtt", ".ass",
}
MAX_BYTES = 50 * 1024 * 1024
# Top-level folders that sit side by side on the drive exactly as in the repo,
# so a ../-relative path between them resolves the same through the symlinks.
SHARED_TOPS = {"projects", "media"}

# No < > in segments, so documented placeholders like /Users/<jij>/ are left alone.
_SEG = r"[^/\"'`<>\n]+"
_USER = r"[^/\s\"'`<>]+"
ROOT_RE = (
    "(?:"
    rf"/Users/{_USER}/Library/CloudStorage/GoogleDrive-{_SEG}/{_SEG}/Mediajungle Projecten/03\. Projecten/OpenMontage"
    f"|{re.escape(str(REPO_ROOT))}"
    rf"|/Users/{_USER}/(?:{_USER}/)*?OpenMontage"
    ")"
)
PLAIN = re.compile(ROOT_RE + r"(?:/|(?=[\"'`\s),\]}]|$))")
FILE_URL = re.compile(r"file://(/[^\"'\s)<>]+)")
CONCAT_LINE = re.compile(r"^(\s*file\s+')([^']+)(')", re.M)
ROOT_FULL = re.compile(ROOT_RE + r"(?:/(.*))?", re.S)
ANY_ABS = re.compile(rf"/Users/{_USER}/[^\"'`\n<>)]*")


def repo_rel(abs_path: str) -> str | None:
    m = ROOT_FULL.fullmatch(abs_path)
    return None if m is None else (m.group(1) or "")


def rel_from(file: Path, target_rel: str) -> str | None:
    """Path to target relative to file's folder, only when it stays on the drive."""
    file_rel = file.relative_to(REPO_ROOT)
    if file_rel.parts[0] not in SHARED_TOPS or Path(target_rel).parts[:1] == ():
        return None
    if Path(target_rel).parts[0] not in SHARED_TOPS:
        return None
    return os.path.relpath(REPO_ROOT / target_rel, (REPO_ROOT / file_rel).parent)


def rewrite(file: Path, text: str) -> tuple[str, int]:
    count = 0

    def concat(m: re.Match) -> str:
        nonlocal count
        target = repo_rel(m.group(2))
        rel = None if target is None else rel_from(file, target)
        if rel is None:
            return m.group(0)
        count += 1
        return m.group(1) + rel + m.group(3)

    def file_url(m: re.Match) -> str:
        nonlocal count
        target = repo_rel(unquote(m.group(1)))
        if target is None:
            return m.group(0)
        if not is_html:
            # Data files (research briefs, checkpoints) just record a source.
            count += 1
            return target or "."
        rel = rel_from(file, target)
        if rel is None:
            return m.group(0)
        count += 1
        return quote(rel, safe="/")

    def plain(m: re.Match) -> str:
        nonlocal count
        count += 1
        return "" if m.group(0).endswith("/") else "."

    is_html = file.suffix in {".html", ".htm"}
    if file.suffix == ".txt":
        text = CONCAT_LINE.sub(concat, text)
    text = FILE_URL.sub(file_url, text)
    # Plain paths inside a file:// URL or concat line we could not make
    # relative are left alone: stripping the root there would break them.
    guarded = []

    def guard(m: re.Match) -> str:
        guarded.append(m.group(0))
        return f"\x00{len(guarded) - 1}\x00"

    text = FILE_URL.sub(guard, text)
    if file.suffix == ".txt":
        text = CONCAT_LINE.sub(guard, text)
    text = PLAIN.sub(plain, text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: guarded[int(m.group(1))], text)
    return text, count


def iter_files(targets: list[str]):
    for target in targets:
        top = REPO_ROOT / target
        if top.is_file():
            yield top
            continue
        if not top.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(top):
            dirnames[:] = [d for d in dirnames if d not in {"node_modules", ".git", "__pycache__"}]
            for name in filenames:
                path = Path(dirpath) / name
                if path.suffix.lower() in TEXT_SUFFIXES and not path.is_symlink():
                    yield path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="*", default=list(DEFAULT_TARGETS),
                        help="mappen of bestanden, relatief aan de repo (default: %(default)s)")
    parser.add_argument("--check", action="store_true", help="alleen rapporteren")
    args = parser.parse_args()

    fixed_files = fixed_paths = 0
    leftovers: Counter[str] = Counter()
    leftover_files: dict[str, set[str]] = {}
    for path in iter_files(args.targets):
        if path.stat().st_size > MAX_BYTES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "/Users/" not in text:
            continue
        new, count = rewrite(path, text)
        rel = str(path.relative_to(REPO_ROOT))
        if count:
            fixed_files += 1
            fixed_paths += count
            if args.check:
                print(f"  {count:4}  {rel}")
            else:
                path.write_text(new, encoding="utf-8")
        for m in ANY_ABS.finditer(new):
            where = re.sub(r"^(/Users/[^/]+/(?:[^/]+/){0,2}).*", r"\1", unquote(m.group(0)))
            leftovers[where] += 1
            leftover_files.setdefault(where, set()).add(rel)

    verb = "te herschrijven" if args.check else "herschreven"
    print(f"{fixed_paths} paden {verb} in {fixed_files} bestanden.")
    if leftovers:
        print("\nAbsolute paden die buiten repo en drive wijzen (handmatig oplossen):")
        for where, n in leftovers.most_common():
            files = sorted(leftover_files[where])
            print(f"  {n:4}x  {where}...  ({len(files)} bestanden, o.a. {files[0]})")
    if args.check and fixed_paths:
        sys.exit(1)


if __name__ == "__main__":
    main()
