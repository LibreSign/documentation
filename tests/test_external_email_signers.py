"""Regression tests for cross-version external email signature docs."""
import copy
import json
import unittest
from pathlib import Path

from versioning.external_contract import PREFIX, validate_external_sample

ROOT = Path(__file__).resolve().parents[1]


class GuestSigningContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(
            (ROOT / "examples/external-email-signers/request.json").read_text()
        )
        cls.spec = {
            "components": {"schemas": {"NewSigner": {"properties": {
                "displayName": {}, "notify": {}, "identifyMethods": {},
            }}}},
            "paths": {
                PREFIX + "/request-signature": {"post": {
                    "requestBody": {"content": {"application/json": {"schema": {
                        "properties": {field: {} for field in cls.fixture},
                    }}}},
                }},
                PREFIX + "/notify/signers": {"post": {}},
                PREFIX + "/file/list": {"get": {}},
                PREFIX + "/file/validate/file_id/{fileId}": {"get": {}},
                PREFIX + "/sign/uuid/{uuid}": {"post": {}},
            },
        }
        cls.spec["paths"][PREFIX + "/request-signature"]["post"]["requestBody"][
            "content"]["application/json"]["schema"]["properties"][
            "signers"] = {"items": {"$ref": "#/components/schemas/NewSigner"}}

    def test_common_sample_matches_declared_operations(self):
        validate_external_sample(self.spec, self.fixture)

    def test_removed_signing_operation_is_rejected(self):
        spec = copy.deepcopy(self.spec)
        del spec["paths"][PREFIX + "/sign/uuid/{uuid}"]
        with self.assertRaisesRegex(ValueError, "Missing guest-signing"):
            validate_external_sample(spec, self.fixture)

    def test_unknown_request_property_is_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["nonexistentField"] = True
        with self.assertRaisesRegex(ValueError, "absent"):
            validate_external_sample(self.spec, fixture)

    def test_unknown_signer_property_is_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["signers"][0]["nonexistentField"] = True
        with self.assertRaisesRegex(ValueError, "signer fields"):
            validate_external_sample(self.spec, fixture)

    def test_real_email_or_duplicate_notification_is_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["signers"][0]["notify"] = 1
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_external_sample(self.spec, fixture)
        fixture["signers"][0]["notify"] = 0
        fixture["signers"][0]["identifyMethods"][0]["value"] = "real@example.com"
        with self.assertRaisesRegex(ValueError, "real email"):
            validate_external_sample(self.spec, fixture)


if __name__ == "__main__":
    unittest.main()
