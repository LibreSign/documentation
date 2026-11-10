"""Discover LibreSign documentation lines from pinned application revisions.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REPOSITORY = "LibreSign/libresign"
GIT_URL = f"https://github.com/{REPOSITORY}.git"
RAW_URL = f"https://raw.githubusercontent.com/{REPOSITORY}"
BRANCH_RE = re.compile(r"^refs/heads/stable(\d+)$")
RELEASE_RE = re.compile(r"^(\d+)\.\d+\.\d+$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_source(commit: str, path: str) -> bytes:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Application source must use a full commit SHA")
    request = urllib.request.Request(
        f"{RAW_URL}/{commit}/{path}", headers={"User-Agent": "LibreSign-documentation-build"}
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read()


def remote_refs() -> dict[str, str]:
    result = subprocess.run(
        ["git", "ls-remote", "--heads", GIT_URL], check=True, text=True,
        capture_output=True, timeout=90,
    )
    refs = {}
    for line in result.stdout.splitlines():
        sha, ref = line.split("\t")
        if ref == "refs/heads/main" or BRANCH_RE.fullmatch(ref):
            refs[ref.removeprefix("refs/heads/")] = sha
    if "main" not in refs:
        raise ValueError("The application main branch could not be resolved")
    return refs


def manifest_info(xml: bytes) -> dict:
    root = ET.fromstring(xml)
    version = root.findtext("version")
    dependency = root.find("./dependencies/nextcloud")
    if not version or dependency is None:
        raise ValueError("LibreSign manifest has no version or Nextcloud dependency")
    minimum, maximum = dependency.get("min-version"), dependency.get("max-version")
    if not minimum or not maximum:
        raise ValueError("LibreSign manifest must declare Nextcloud min/max versions")
    return {"version": version, "nextcloud_min": int(minimum), "nextcloud_max": int(maximum)}


def operations(contract: dict) -> set[tuple[str, str]]:
    methods = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
    return {
        (path, method.lower())
        for path, item in contract.get("paths", {}).items()
        if isinstance(item, dict)
        for method in item
        if method.lower() in methods
    }


def validate_contract(contract: dict) -> None:
    if not str(contract.get("openapi", "")).startswith("3."):
        raise ValueError("Expected OpenAPI 3.x")
    if not isinstance(contract.get("paths"), dict) or not operations(contract):
        raise ValueError("OpenAPI document has no operations")


def discover(policy: dict, refs: dict[str, str] | None = None,
             fetch=fetch_source) -> tuple[dict, dict[str, bytes]]:
    """Snapshot each eligible branch at an immutable git SHA before building.

    The Nextcloud floor prevents publishing unsupported historical majors.
    New stable branches are admitted by their manifest, not by a hardcoded
    mapping to a LibreSign major. Pre-release manifests are not auto-published.
    """
    refs = remote_refs() if refs is None else refs
    floor = int(policy["minimum_nextcloud"])
    lifecycle = policy.get("lifecycle", {})
    entries, contracts = [], {}
    for branch, sha in sorted(refs.items(), key=lambda item: item[0]):
        if branch != "main":
            match = re.fullmatch(r"stable(\d+)", branch)
            if not match or int(match.group(1)) < floor:
                continue
        manifest_xml = fetch(sha, "appinfo/info.xml")
        manifest = manifest_info(manifest_xml)
        ver = manifest["version"]
        if branch != "main":
            release = RELEASE_RE.fullmatch(ver)
            if not release:
                # A future line only becomes public when its manifest is a release.
                continue
            major = release.group(1)
            branch_nc = int(branch.removeprefix("stable"))
            if not manifest["nextcloud_min"] <= branch_nc <= manifest["nextcloud_max"]:
                raise ValueError(f"{branch} does not match Nextcloud dependency in manifest")
            if int(major) <= 0:
                raise ValueError(f"Invalid application major: {ver}")
            slug = major
        else:
            slug = "main"
        if slug in contracts:
            raise ValueError(f"More than one application branch publishes LibreSign {slug}")
        raw = fetch(sha, "openapi.json")
        contract = json.loads(raw)
        validate_contract(contract)
        entry = {
            "slug": slug, "branch": branch, "app_commit": sha,
            "app_version": ver, "nextcloud_min": manifest["nextcloud_min"],
            "nextcloud_max": manifest["nextcloud_max"],
            "manifest_sha256": sha256(manifest_xml),
            "openapi_sha256": sha256(raw),
            "source_url": f"https://github.com/{REPOSITORY}/blob/{sha}/openapi.json",
            "eol_date": lifecycle.get(slug, {}).get("eol_date"),
        }
        if lifecycle.get(slug, {}).get("status") == "eol":
            entry["status"] = "eol"
        elif slug == "main":
            entry["status"] = "development"
        else:
            entry["status"] = "previous"
        entries.append(entry)
        contracts[slug] = raw
    stable = [entry for entry in entries if entry["slug"] != "main"]
    if not stable:
        raise ValueError("No versioned stable application branches were discovered")
    current = max((entry for entry in stable if entry["status"] != "eol"),
                  key=lambda e: int(e["slug"]), default=None)
    if current:
        current["status"] = "current"
    entries.sort(key=lambda e: (e["slug"] != "main", -(int(e["slug"]) if e["slug"] != "main" else 0)))
    catalog = {
        "schema": 1, "application_repository": REPOSITORY,
        "current_stable": current["slug"] if current else None, "versions": entries,
    }
    return catalog, contracts


def load_policy(root: Path) -> dict:
    return json.loads((root / "versioning/lifecycle.json").read_text(encoding="utf-8"))


def get_version(catalog: dict, slug: str) -> dict:
    return next(e for e in catalog["versions"] if e["slug"] == slug)
