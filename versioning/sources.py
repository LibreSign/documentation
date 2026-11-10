"""Read complete documentation sources from their own version branches.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import io
import re
import subprocess
import tarfile
from pathlib import Path

REPOSITORY = "https://github.com/LibreSign/documentation.git"
MANUALS = ("main", "user_manual", "admin_manual", "developer_manual")


def branch_sources(stage: Path, slug: str, *, repository: Path,
                   expected_commit: str | None = None) -> Path:
    """Pin a documentation branch once, then read all manuals from that SHA.

    No fallback to the development manual is allowed for missing releases.
    Only documentation trees are extracted; tooling is taken from the build PR.
    """
    if slug == "main":
        return repository
    if not re.fullmatch(r"[1-9][0-9]*", slug):
        raise ValueError(f"Invalid LibreSign documentation release: {slug!r}")

    destination = stage / "_branch_sources" / slug
    if destination.is_dir():
        return destination
    branch = f"stable{slug}"
    try:
        subprocess.run(
            ["git", "-C", str(repository), "fetch", "--quiet", "--no-tags",
             "--depth=1", REPOSITORY, f"refs/heads/{branch}"],
            check=True, capture_output=True, text=True, timeout=120,
        )
        revision = subprocess.check_output(
            ["git", "-C", str(repository), "rev-parse", "FETCH_HEAD"],
            text=True, timeout=20,
        ).strip()
        if expected_commit is not None and revision != expected_commit:
            raise ValueError(
                f"{branch} changed during documentation validation: "
                f"expected {expected_commit}, fetched {revision}"
            )
        data = subprocess.check_output(
            ["git", "-C", str(repository), "archive", "--format=tar",
             revision, *MANUALS], timeout=90,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise ValueError(
            f"Missing/unavailable documentation branch {branch}; "
            "publish the release-specific documentation branch before building"
        ) from error

    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
        archive.extractall(destination, filter="data")
    for manual in MANUALS:
        if not (destination / manual / "index.rst").is_file():
            raise ValueError(f"{branch} has no {manual}/index.rst")
    (destination / ".source-commit").write_text(revision + "\n")
    print(f"Documentation {branch} pinned at {revision}")
    return destination
