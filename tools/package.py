#!/usr/bin/env python3
"""
Reproducible packaging for Living Weather (Phase 4).

Builds the distribution zips from the source tree into dist/:
  LivingWeather-v0.1.0.zip           (required deliverable; Atmospheric)
  LivingWeather-Stormy-v0.1.0.zip    (optional preset)
  LivingWeather-StormDuration-v0.1.0.zip (experimental addon)

Each zip contains exactly one top-level modlet folder ready to drop into
the game's Mods directory, plus player-facing README/CHANGELOG copies.
Records the SHA256 of every artifact into dist/SHA256SUMS.txt.

NOTE for the public-prototype release: the release asset
LivingWeather-v0.1.0.zip must remain byte-identical to the frozen
v0.1.0-freeze build. If you re-run packaging after ANY file change,
verify the new checksums and the release hash match before distributing.
"""

import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MODLETS = {
    "LivingWeather": {
        "src": ROOT / "LivingWeather",
        "name": "LivingWeather-v0.1.0.zip",
    },
    "LivingWeather-Stormy": {
        "src": ROOT / "OptionalPresets" / "LivingWeather-Stormy",
        "name": "LivingWeather-Stormy-v0.1.0.zip",
    },
    "LivingWeather-StormDuration": {
        "src": ROOT / "OptionalPresets" / "LivingWeather-StormDuration",
        "name": "LivingWeather-StormDuration-v0.1.0.zip",
    },
}

ZIP_README = (ROOT / "assets" / "zip_README.md").read_text(encoding="utf-8")
ZIP_CHANGELOG = (ROOT / "assets" / "zip_CHANGELOG.md").read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def build(modlet_folder: str, spec: dict) -> Path:
    src = spec["src"]
    out = DIST / spec["name"]
    stage = DIST / "_stage" / modlet_folder
    if stage.parent.exists():
        shutil.rmtree(stage.parent)
    shutil.copytree(src, stage)
    (stage / "README.md").write_text(ZIP_README, encoding="utf-8")
    (stage / "CHANGELOG.md").write_text(ZIP_CHANGELOG, encoding="utf-8")
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(stage.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(stage.parent))
    shutil.rmtree(stage.parent)
    return out


def main():
    DIST.mkdir(exist_ok=True)
    hashes = []

    for folder, spec in MODLETS.items():
        out = build(folder, spec)

        checksum = sha256(out)
        hashes.append((out.name, out.stat().st_size, checksum))

        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
            expected = {
                f"{folder}/ModInfo.xml",
                f"{folder}/Config/biomes.xml",
                f"{folder}/README.md",
                f"{folder}/CHANGELOG.md",
            }
            assert all(n in names for n in expected), names
            assert not any(n.startswith(("/", "\\")) or ".." in n for n in names)
        print(f"built {out.name}")

    sums = DIST / "SHA256SUMS.txt"
    with open(sums, "w", encoding="utf-8") as fh:
        for name, size, digest in hashes:
            fh.write(f"{digest}  {name} ({size} bytes)\n")
    print(f"wrote {sums}")


if __name__ == "__main__":
    main()
    sys.exit(0)
