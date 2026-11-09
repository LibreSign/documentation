"""Verify release-scoped guest-signing docs against pinned OpenAPI and source.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from versioning.catalog import fetch_source

PREFIX = "/ocs/v2.php/apps/libresign/api/{apiVersion}"
REQUIRED_OPERATIONS = {
    ("post", "/request-signature"),
    ("post", "/notify/signers"),
    ("get", "/file/list"),
    ("get", "/file/validate/file_id/{fileId}"),
    ("post", "/sign/uuid/{uuid}"),
}
# Check the same application SHA as the pinned OpenAPI, never a moving branch.
SOURCE_MARKERS = {
    "lib/Controller/RequestSignatureController.php": ("RequireManager", "/request-signature"),
    "lib/Controller/NotifyController.php": ("/notify/signers",),
    "lib/Controller/SignFileController.php": ("RequireSigner", "PublicPage", "/sign/uuid/{uuid}"),
    "lib/Controller/FileController.php": ("/file/list", "RequireFileAccess"),
    "lib/Controller/PageController.php": ("PublicPage", "/p/sign/{uuid}"),
    "lib/Service/NotifyService.php": ("iRequestedSignThisFile",),
    "playwright/e2e/sign-envelope-unauthenticated-visible-signature.spec.ts": ("test(",),
    "playwright/e2e/sign-email-token-unauthenticated.spec.ts": ("test(",),
    "playwright/e2e/multi-signer-sequential.spec.ts": ("test(",),
}
FIXTURE_FOLDER = Path("examples/external-email-signers")
PARTIAL_NAME = "_external-email-signers-release.inc"


def resolve(spec: dict, schema: dict) -> dict:
    """Resolve only local component-schema references used in request bodies."""
    visited: set[str] = set()
    while "$ref" in schema:
        ref = schema["$ref"]
        prefix = "#/components/schemas/"
        if not ref.startswith(prefix) or ref in visited:
            raise ValueError(f"Unsupported/cyclic request schema reference: {ref}")
        visited.add(ref)
        schema = spec["components"]["schemas"][ref[len(prefix):]]
    return schema


def validate_shape(spec: dict, schema: dict, value: Any, location: str) -> None:
    """Reject undocumented nested fields, missing required keys and wrong types.

    This deliberately validates the small concrete sample rather than claiming
    to implement every OpenAPI 3 schema feature. Unsupported schema constructs
    on this sample fail closed instead of silently passing.
    """
    schema = resolve(spec, schema)
    if "allOf" in schema:
        for item in schema["allOf"]:
            validate_shape(spec, item, value, location)
        return
    if "anyOf" in schema or "oneOf" in schema:
        choices = schema.get("anyOf", schema.get("oneOf", []))
        if not any(_shape_is_valid(spec, item, value, location) for item in choices):
            raise ValueError(f"{location}: no supported schema alternative matches")
        return
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{location}: value not in documented enum")
    expected = schema.get("type")
    if isinstance(value, dict):
        if expected not in (None, "object"):
            raise ValueError(f"{location}: expected {expected}, got object")
        properties = schema.get("properties")
        if not isinstance(properties, dict):
            raise ValueError(f"{location}: schema does not document object properties")
        missing = set(schema.get("required", [])) - set(value)
        if missing:
            raise ValueError(f"{location}: missing required properties {sorted(missing)}")
        extra = set(value) - set(properties)
        if extra:
            raise ValueError(f"{location}: undocumented properties {sorted(extra)}")
        for key, child in value.items():
            validate_shape(spec, properties[key], child, f"{location}.{key}")
    elif isinstance(value, list):
        if expected != "array":
            raise ValueError(f"{location}: expected {expected}, got array")
        if "items" not in schema:
            raise ValueError(f"{location}: array items are undocumented")
        for index, item in enumerate(value):
            validate_shape(spec, schema["items"], item, f"{location}[{index}]")
    else:
        type_ok = (
            expected is None
            or expected == "string" and isinstance(value, str)
            or expected == "integer" and isinstance(value, int) and not isinstance(value, bool)
            or expected == "number" and isinstance(value, (int, float)) and not isinstance(value, bool)
            or expected == "boolean" and isinstance(value, bool)
            or value is None and schema.get("nullable", False)
        )
        if not type_ok:
            raise ValueError(f"{location}: value type does not match {expected}")
        if isinstance(value, (int, float)) and "minimum" in schema:
            if value < schema["minimum"]:
                raise ValueError(f"{location}: value is below minimum")


def _shape_is_valid(spec: dict, schema: dict, value: Any, location: str) -> bool:
    try:
        validate_shape(spec, schema, value, location)
    except ValueError:
        return False
    return True


def operation(spec: dict, method: str, path: str) -> dict:
    op = spec.get("paths", {}).get(PREFIX + path, {}).get(method)
    if not isinstance(op, dict):
        raise ValueError(f"Missing guest-signing API operation: {method} {path}")
    return op


def request_schema(op: dict) -> dict:
    try:
        return op["requestBody"]["content"]["application/json"]["schema"]
    except KeyError as error:
        raise ValueError("Expected JSON request schema missing") from error


def expected_identity_field(spec: dict) -> str:
    create = request_schema(operation(spec, "post", "/request-signature"))
    signer = resolve(spec, create["properties"]["signers"]["items"])
    item = resolve(spec, signer["properties"]["identifyMethods"]["items"])
    required = set(item.get("required", []))
    fields = set(item.get("properties", []))
    if {"method", "value", "mandatory"} <= required and "mandatory" in fields:
        return "mandatory"
    if {"method", "value", "requirement"} <= required and "requirement" in fields:
        return "requirement"
    raise ValueError("Unrecognized email identification schema; review this release")


def validate_external_sample(spec: dict, fixture: dict) -> str:
    for method, path in REQUIRED_OPERATIONS:
        operation(spec, method, path)
    identity_field = expected_identity_field(spec)
    validate_shape(spec, request_schema(operation(spec, "post", "/request-signature")),
                   fixture, "request")
    signer = fixture["signers"][0]
    identity = signer["identifyMethods"][0]
    if signer["notify"] != 0:
        raise ValueError("Fixture must not send duplicate automatic invitations")
    if identity["method"] != "email" or identity["value"] != "signer@example.test":
        raise ValueError("Fixture must use a synthetic email identify method")
    if identity_field == "mandatory" and identity["mandatory"] != 1:
        raise ValueError("Old releases require integer mandatory=1")
    if identity_field == "requirement" and identity["requirement"] != "required":
        raise ValueError("New releases require string requirement=required")
    if fixture["file"]["base64"] != "REPLACE_WITH_BASE64":
        raise ValueError("Fixture must not store actual document bytes")
    validate_shape(spec, request_schema(operation(spec, "post", "/notify/signers")),
                   {"fileId": 123, "signers": [{"email": "signer@example.test"}]},
                   "notification")
    # The file-list payload used by both scripts must still expose its data array.
    rsp = operation(spec, "get", "/file/list")["responses"]["200"]
    envelope = resolve(spec, rsp["content"]["application/json"]["schema"])
    ocs = resolve(spec, envelope["properties"]["ocs"])
    data = resolve(spec, ocs["properties"]["data"])
    if "data" not in data.get("properties", {}):
        raise ValueError("The file list no longer declares a data collection")
    return identity_field


def extract_rst_json(partial: str) -> dict:
    lines = partial.splitlines()
    try:
        start = lines.index(".. code-block:: json") + 1
    except ValueError as error:
        raise ValueError("Release section lacks a JSON example") from error
    while start < len(lines) and not lines[start].strip():
        start += 1
    collected = []
    for line in lines[start:]:
        if not line.startswith("   "):
            break
        collected.append(line[3:])
    if not collected:
        raise ValueError("Release JSON block is empty")
    return json.loads("\n".join(collected))


def verify_source_evidence(entry: dict, fetch: Callable[[str, str], bytes] = fetch_source) -> None:
    commit = entry["app_commit"]
    for path, markers in SOURCE_MARKERS.items():
        source = fetch(commit, path).decode("utf-8")
        for marker in markers:
            if marker not in source:
                raise ValueError(f"{entry['slug']}: missing pinned source evidence {path}: {marker}")


def validate_site_external_samples(
    site: Path, repository: Path, fetch: Callable[[str, str], bytes] = fetch_source,
) -> list[str]:
    """Check every built release against its own SHA, example and rendered page.

    A new major with no reviewed fixture/overlay is rejected. Release discovery
    remains dynamic; the gate prevents silently publishing stale examples.
    """
    catalog = json.loads((site / "versions.json").read_text())
    verified = []
    for entry in catalog["versions"]:
        slug = entry["slug"]
        fixture_file = repository / FIXTURE_FOLDER / f"request-{slug}.json"
        partial_file = repository / (
            Path("developer_manual/api") if slug == "main"
            else Path("versioned") / slug / "developer_manual/api"
        ) / PARTIAL_NAME
        if not fixture_file.is_file() or not partial_file.is_file():
            raise ValueError(f"{slug}: missing reviewed fixture or release-specific guide")
        spec_file = site / slug / "developer_manual/api/openapi.json"
        spec = json.loads(spec_file.read_text())
        fixture = json.loads(fixture_file.read_text())
        identity_field = validate_external_sample(spec, fixture)
        partial = partial_file.read_text()
        if f"request-{slug}.json" not in partial or f"LIBRESIGN_DOC_LINE={slug}" not in partial:
            raise ValueError(f"{slug}: documentation does not select its own fixture")
        if entry["branch"] not in partial:
            raise ValueError(f"{slug}: wrong stable-branch evidence link")
        documented = extract_rst_json(partial)
        if documented != fixture:
            raise ValueError(f"{slug}: shown JSON differs from executable fixture")
        if identity_field not in partial:
            raise ValueError(f"{slug}: identify-method contract not described")
        request_fields = request_schema(operation(spec, "post", "/request-signature"))["properties"]
        if "signatureFlow" in request_fields:
            if "accepts" not in partial or "ordered_numeric" not in partial:
                raise ValueError(f"{slug}: ordered signing request options not documented")
        elif "does **not** declare" not in partial:
            raise ValueError(f"{slug}: undocumented signatureFlow field not ruled out")
        html_file = site / slug / "developer_manual/api/external-email-signers.html"
        if not html_file.is_file():
            raise ValueError(f"{slug}: guide is missing from rendered site")
        html = html_file.read_text()
        if entry["app_version"] not in html:
            raise ValueError(f"{slug}: exact application release missing from page")
        for path in ("/request-signature", "/notify/signers", "/file/list"):
            if path not in html:
                raise ValueError(f"{slug}: operation absent from rendered page: {path}")
        verify_source_evidence(entry, fetch=fetch)
        verified.append(slug)
    return verified
