"""Check the guest-email integration sample against each version's OpenAPI.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import json
from pathlib import Path

PREFIX = "/ocs/v2.php/apps/libresign/api/{apiVersion}"
REQUIRED = {
    ("post", "/request-signature"),
    ("post", "/notify/signers"),
    ("get", "/file/list"),
    ("get", "/file/validate/file_id/{fileId}"),
    ("post", "/sign/uuid/{uuid}"),
}
SHARED_FIELDS = {"name", "status", "file", "signers"}
REQUIRED_SIGNER_FIELDS = {"displayName", "notify", "identifyMethods"}
REQUIRED_IDENTITY_FIELDS = {"method", "value", "mandatory"}


def validate_external_sample(spec: dict, fixture: dict) -> None:
    paths = spec.get("paths", {})
    for method, path in REQUIRED:
        if method not in paths.get(PREFIX + path, {}):
            raise ValueError(f"Missing guest-signing API operation: {method} {path}")
    operation = paths[PREFIX + "/request-signature"]["post"]
    schema = operation["requestBody"]["content"]["application/json"]["schema"]
    fields = set(schema.get("properties", {}))
    if not SHARED_FIELDS.issubset(fields):
        raise ValueError("Required common request properties are not in OpenAPI")
    if not set(fixture).issubset(fields):
        raise ValueError("Fixture has request properties absent from the versioned contract")
    signer = fixture["signers"][0]
    signer_ref = schema["properties"]["signers"]["items"]["$ref"].split("/")[-1]
    signer_fields = set(spec["components"]["schemas"][signer_ref].get("properties", {}))
    if not REQUIRED_SIGNER_FIELDS.issubset(signer_fields) or not set(signer).issubset(signer_fields):
        raise ValueError("Fixture signer fields do not match OpenAPI")
    method_item = signer["identifyMethods"][0]
    if not REQUIRED_IDENTITY_FIELDS.issubset(method_item):
        raise ValueError("Fixture does not describe an email identifier")
    if method_item["method"] != "email" or method_item["mandatory"] != 1:
        raise ValueError("Expected mandatory synthetic email identifier")
    if fixture["file"].get("base64") != "REPLACE_WITH_BASE64":
        raise ValueError("Fixture must not store real document bytes")
    if not fixture["signers"][0].get("notify") == 0:
        raise ValueError("Example must not automatically send duplicate invitations")
    if fixture["signers"][0]["identifyMethods"][0]["value"] != "signer@example.test":
        raise ValueError("Fixture must not contain a real email address")


def validate_site_external_samples(site: Path, repository: Path) -> list[str]:
    """Validate independently bundled OpenAPI JSON for every published version."""
    fixture = json.loads((repository / "examples/external-email-signers/request.json").read_text())
    catalog = json.loads((site / "versions.json").read_text())
    found = []
    for entry in catalog["versions"]:
        slug = entry["slug"]
        path = site / slug / "developer_manual/api/openapi.json"
        validate_external_sample(json.loads(path.read_text()), fixture)
        guide = site / slug / "developer_manual/api/external-email-signers.html"
        if not guide.is_file():
            raise ValueError(f"Missing rendered external signing guide: {slug}")
        html = guide.read_text()
        for operation in ("/request-signature", "/notify/signers", "/file/list"):
            if operation not in html:
                raise ValueError(f"Missing documented operation in {slug}: {operation}")
        found.append(slug)
    return found
