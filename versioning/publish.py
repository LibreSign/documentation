"""Atomic Pages assembly: a version update cannot erase sibling versions."""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

from versioning.build import legacy_redirects
from versioning.seo import apply_seo

ROOT = Path(__file__).resolve().parent.parent


def assemble(built: Path, destination: Path, selected: str,
             existing: Path | None = None) -> dict:
    incoming = json.loads((built / "versions.json").read_text())
    if destination.exists():
        raise ValueError("Destination must not exist (assembly must be atomic)")
    if selected == "all":
        for entry in incoming["versions"]:
            if not (built / entry["slug"] / "index.html").is_file():
                raise ValueError(f"Missing built version: {entry['slug']}")
        shutil.copytree(built, destination)
        output_catalog = incoming
    else:
        if existing is None or not (existing / "versions.json").is_file():
            raise ValueError("Partial publication requires existing versioned Pages")
        current = json.loads((existing / "versions.json").read_text())
        old_versions = {e["slug"]: e for e in current["versions"]}
        new_versions = {e["slug"]: e for e in incoming["versions"]}
        if selected not in new_versions:
            raise ValueError(f"Unknown requested version: {selected}")
        if not (built / selected / "index.html").is_file():
            raise ValueError(f"Selected version was not built: {selected}")
        for slug in old_versions:
            if not (existing / slug / "index.html").is_file():
                raise ValueError(f"Existing Pages release is missing: {slug}")
        shutil.copytree(existing, destination,
                        ignore=shutil.ignore_patterns(".git"))
        shutil.rmtree(destination / selected, ignore_errors=True)
        shutil.copytree(built / selected, destination / selected)
        old_versions[selected] = new_versions[selected]
        entries = sorted(old_versions.values(), key=lambda v:
                         (v["slug"] != "main", -(int(v["slug"]) if v["slug"] != "main" else 0)))
        stable = [e for e in entries if e["slug"] != "main" and e["status"] != "eol"]
        latest = max(stable, key=lambda v: int(v["slug"]), default=None)
        for entry in entries:
            if entry["status"] in ("current", "previous"):
                entry["status"] = (
                    "current" if latest is not None and
                    entry["slug"] == latest["slug"] else "previous"
                )
        output_catalog = {**incoming, "versions": entries,
                          "current_stable": latest["slug"] if latest else None}
        (destination / "versions.json").write_text(
            json.dumps(output_catalog, indent=2) + "\n", encoding="utf-8"
        )
        for filename in ("home.css", "ecosystem-nav.css", "ecosystem-footer.css", "ecosystem-nav.js", "scroll-navigation.js", "home-theme.js", "logo.png"):
            candidate = built / filename
            if candidate.is_file():
                shutil.copy2(candidate, destination / filename)
        legacy_redirects(destination, output_catalog["current_stable"])
    (destination / "CNAME").write_text("docs.libresign.coop\n", encoding="utf-8")
    (destination / ".nojekyll").touch()
    apply_seo(destination, output_catalog, preview=bool(os.environ.get("LIBRESIGN_PREVIEW_PR")))
    return output_catalog


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--built", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--existing", type=Path)
    parser.add_argument("--version", default="all")
    args = parser.parse_args()
    assemble(args.built, args.destination, args.version, args.existing)


if __name__ == "__main__":
    main()
