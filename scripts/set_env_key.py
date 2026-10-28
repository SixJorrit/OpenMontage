"""Put an API key into .env without it ever showing up on screen or in a chat.

Copy the key (from the password manager), then run:

    python3 scripts/set_env_key.py ELEVENLABS_API_KEY

The value is read from the clipboard, written to .env (mode 600) and the
clipboard is cleared. Only the key name and the value's length are printed,
so it is safe to run from Claude Code with the `!` prefix: the command line
and its output contain no secret.

Run in a normal terminal, the script asks for the value with hidden input
instead (`--prompt` forces that). Non-secret settings can be passed inline:

    python3 scripts/set_env_key.py AZURE_SPEECH_REGION northeurope

Check what is filled in (names only):

    python3 scripts/set_env_key.py --status
"""
from __future__ import annotations

import argparse
import getpass
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"
EXAMPLE_FILE = REPO_ROOT / ".env.example"
NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
LINE_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")


def read_clipboard() -> str:
    if not shutil.which("pbpaste"):
        sys.exit("Geen klembord gevonden (pbpaste). Draai het script in een terminal met --prompt.")
    return subprocess.run(["pbpaste"], capture_output=True, text=True, check=True).stdout


def clear_clipboard() -> None:
    if shutil.which("pbcopy"):
        subprocess.run(["pbcopy"], input="", text=True, check=False)


def ensure_env_file() -> None:
    if not ENV_FILE.exists():
        if EXAMPLE_FILE.exists():
            shutil.copy(EXAMPLE_FILE, ENV_FILE)
        else:
            ENV_FILE.touch()
    os.chmod(ENV_FILE, 0o600)


def known_names() -> set[str]:
    names: set[str] = set()
    for path in (EXAMPLE_FILE, ENV_FILE):
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                m = LINE_RE.match(line)
                if m:
                    names.add(m.group(1))
                elif line.lstrip().startswith("#"):
                    # Some keys are only mentioned in comments (e.g. ATLASCLOUD_API_KEY).
                    names.update(re.findall(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b", line))
    return names


def format_value(value: str) -> str:
    if re.search(r"[\s#'\"]", value):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def write_key(name: str, value: str) -> bool:
    """Replace the first NAME= line (commented or not) or append. Returns True if replaced."""
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    new_line = f"{name}={format_value(value)}"
    replaced = False
    for i, line in enumerate(lines):
        stripped = line.lstrip("# ").strip()
        m = LINE_RE.match(stripped)
        if m and m.group(1) == name:
            lines[i] = new_line
            replaced = True
            break
    if not replaced:
        lines.append(new_line)
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.chmod(ENV_FILE, 0o600)
    return replaced


def status() -> None:
    if not ENV_FILE.exists():
        print(".env bestaat nog niet.")
        return
    filled = []
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        m = LINE_RE.match(line)
        if m and m.group(2).strip().strip("'\""):
            filled.append(m.group(1))
    if not filled:
        print("Nog niets ingevuld in .env.")
        return
    print("Ingevuld in .env:")
    for name in sorted(filled):
        print(f"  {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("name", nargs="?", help="naam van de sleutel, bv. ELEVENLABS_API_KEY")
    parser.add_argument("value", nargs="?", help="alleen voor niet-geheime instellingen zoals een regio")
    parser.add_argument("--prompt", action="store_true", help="vraag de waarde verborgen in de terminal")
    parser.add_argument("--status", action="store_true", help="toon welke sleutels zijn ingevuld (alleen namen)")
    parser.add_argument("--force", action="store_true", help="ook een naam accepteren die niet in .env.example staat")
    args = parser.parse_args()

    if args.status:
        status()
        return
    if not args.name:
        parser.error("geef de naam van de sleutel op, of --status")
    name = args.name.strip()
    if not NAME_RE.match(name):
        sys.exit(f"'{name}' is geen geldige naam (hoofdletters, cijfers en _).")
    if name not in known_names() and not args.force:
        sys.exit(f"{name} staat niet in .env.example. Typfout? Gebruik --force als de naam klopt.")

    from_clipboard = False
    if args.value is not None:
        value = args.value
    elif args.prompt or sys.stdin.isatty():
        value = getpass.getpass(f"Waarde voor {name} (wordt niet getoond): ")
    else:
        value = read_clipboard()
        from_clipboard = True

    value = value.strip()
    if not value:
        sys.exit("Geen waarde gevonden. Kopieer eerst de sleutel naar het klembord.")
    if "\n" in value or "\r" in value:
        sys.exit("Op het klembord staat meer dan één regel; kopieer alleen de sleutel zelf.")

    ensure_env_file()
    replaced = write_key(name, value)
    if from_clipboard:
        clear_clipboard()
    action = "bijgewerkt" if replaced else "toegevoegd"
    note = " Klembord gewist." if from_clipboard else ""
    print(f"{name} {action} in .env ({len(value)} tekens).{note}")


if __name__ == "__main__":
    main()
