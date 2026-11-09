"""Regression cases for version-scoped guest-signing examples.

SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
"""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from versioning.external_contract import (
    PREFIX, SOURCE_MARKERS, extract_rst_json, expected_identity_field,
    validate_external_sample, validate_site_external_samples,
    verify_source_evidence,
)

ROOT = Path(__file__).resolve().parents[1]


def sample_spec(identity: str) -> dict:
    method_props = {
        "method": {"type": "string"},
        "value": {"type": "string"},
    }
    if identity == "mandatory":
        method_props["mandatory"] = {"type": "integer", "minimum": 0}
    else:
        method_props["requirement"] = {"$ref": "#/components/schemas/IdentifyMethodRequirement"}
    spec = {
        "components": {"schemas": {
            "IdentifyMethodRequirement": {"type": "string", "enum": ["required", "optional"]},
            "NewFile": {"type": "object", "properties": {
                "name": {"type": "string"}, "base64": {"type": "string"},
            }},
            "NewSigner": {
                "type": "object", "required": ["identifyMethods"],
                "properties": {
                    "displayName": {"type": "string"},
                    "notify": {"type": "integer"},
                    "identifyMethods": {"type": "array", "items": {
                        "type": "object",
                        "required": ["method", "value", identity],
                        "properties": method_props,
                    }},
                },
            },
            "FileListResponse": {"type": "object", "properties": {
                "data": {"type": "array", "items": {"type": "object"}},
            }},
        }},
        "paths": {
            PREFIX + "/request-signature": {"post": {
                "requestBody": {"content": {"application/json": {
                    "schema": {"type": "object", "properties": {
                        "name": {"type": "string"},
                        "status": {"type": "integer"},
                        "file": {"$ref": "#/components/schemas/NewFile"},
                        "signers": {"type": "array", "items": {
                            "$ref": "#/components/schemas/NewSigner",
                        }},
                        **({"signatureFlow": {"type": "string"}} if identity == "mandatory" else {}),
                    }},
                }}},
            }},
            PREFIX + "/notify/signers": {"post": {
                "requestBody": {"content": {"application/json": {
                    "schema": {"type": "object", "required": ["fileId", "signers"],
                        "properties": {
                            "fileId": {"type": "integer"},
                            "signers": {"type": "array", "items": {
                                "type": "object", "required": ["email"],
                                "properties": {"email": {"type": "string"}},
                            }},
                        }},
                }}},
            }},
            PREFIX + "/file/list": {"get": {"responses": {"200": {
                "content": {"application/json": {"schema": {
                    "type": "object", "properties": {"ocs": {
                        "type": "object", "properties": {"data": {
                            "$ref": "#/components/schemas/FileListResponse",
                        }},
                    }},
                }}},
            }}}},
            PREFIX + "/file/validate/file_id/{fileId}": {"get": {}},
            PREFIX + "/sign/uuid/{uuid}": {"post": {}},
        },
    }
    return spec


def fixture(slug: str) -> dict:
    return json.loads(
        (ROOT / "examples/external-email-signers" / f"request-{slug}.json").read_text()
    )


class GuestSigningContractTests(unittest.TestCase):
    def test_each_release_uses_its_actual_identity_contract(self):
        for slug, required in (
            ("13", "mandatory"), ("14", "mandatory"),
            ("15", "requirement"), ("main", "requirement"),
        ):
            with self.subTest(release=slug):
                spec = sample_spec(required)
                self.assertEqual(expected_identity_field(spec), required)
                self.assertEqual(validate_external_sample(spec, fixture(slug)), required)

    def test_legacy_template_is_not_compatible_with_current_contract(self):
        with self.assertRaisesRegex(ValueError, "missing required"):
            validate_external_sample(sample_spec("requirement"), fixture("13"))

    def test_current_template_is_not_compatible_with_legacy_contract(self):
        with self.assertRaisesRegex(ValueError, "missing required"):
            validate_external_sample(sample_spec("mandatory"), fixture("15"))

    def test_missing_nested_required_field_is_rejected(self):
        modern = fixture("15")
        del modern["signers"][0]["identifyMethods"][0]["requirement"]
        with self.assertRaisesRegex(ValueError, "missing required"):
            validate_external_sample(sample_spec("requirement"), modern)

    def test_wrong_requirement_enum_is_rejected(self):
        modern = fixture("15")
        modern["signers"][0]["identifyMethods"][0]["requirement"] = "mandatory"
        with self.assertRaisesRegex(ValueError, "enum"):
            validate_external_sample(sample_spec("requirement"), modern)

    def test_unknown_nested_field_is_rejected(self):
        legacy = fixture("13")
        legacy["signers"][0]["identifyMethods"][0]["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "undocumented"):
            validate_external_sample(sample_spec("mandatory"), legacy)

    def test_removed_signing_operation_is_rejected(self):
        contract = sample_spec("mandatory")
        del contract["paths"][PREFIX + "/sign/uuid/{uuid}"]
        with self.assertRaisesRegex(ValueError, "Missing guest-signing"):
            validate_external_sample(contract, fixture("13"))

    def test_invalid_notification_or_personal_data_is_rejected(self):
        legacy = fixture("13")
        legacy["signers"][0]["notify"] = 1
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_external_sample(sample_spec("mandatory"), legacy)
        legacy["signers"][0]["notify"] = 0
        legacy["signers"][0]["identifyMethods"][0]["value"] = "someone@real.example"
        with self.assertRaisesRegex(ValueError, "synthetic"):
            validate_external_sample(sample_spec("mandatory"), legacy)

    def test_each_rendered_sample_matches_its_executable_fixture(self):
        for slug in ("13", "14", "15", "main"):
            with self.subTest(release=slug):
                directory = (
                    ROOT / "developer_manual/api" if slug == "main"
                    else ROOT / "versioned" / slug / "developer_manual/api"
                )
                panel = (directory / "_external-email-signers-release.inc").read_text()
                self.assertEqual(extract_rst_json(panel), fixture(slug))
                self.assertIn(f"LIBRESIGN_DOC_LINE={slug}", panel)

    def test_pinned_source_provenance_is_checked(self):
        entry = {"slug": "13", "app_commit": "a" * 40}
        observed = []
        def fetched(sha: str, path: str) -> bytes:
            observed.append((sha, path))
            return "\n".join(SOURCE_MARKERS[path]).encode()
        verify_source_evidence(entry, fetch=fetched)
        self.assertEqual(len(observed), len(SOURCE_MARKERS))
        self.assertEqual({sha for sha, _ in observed}, {"a" * 40})

    def test_missing_pinned_source_guard_is_rejected(self):
        entry = {"slug": "13", "app_commit": "a" * 40}
        def incomplete(sha: str, path: str) -> bytes:
            return b"missing implementation" if path.endswith("NotifyService.php") else (
                "\n".join(SOURCE_MARKERS[path]).encode()
            )
        with self.assertRaisesRegex(ValueError, "NotifyService"):
            verify_source_evidence(entry, fetch=incomplete)

    def test_an_unreviewed_future_version_cannot_publish_stale_examples(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "versions.json").write_text(json.dumps({
                "versions": [{"slug": "17", "branch": "stable37", "app_version": "17.0.0"}],
            }))
            with self.assertRaisesRegex(ValueError, "missing reviewed"):
                validate_site_external_samples(site, ROOT, fetch=lambda *_: b"")


if __name__ == "__main__":
    unittest.main()
