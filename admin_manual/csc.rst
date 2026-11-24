..
   SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
   SPDX-License-Identifier: CC-BY-3.0

CSC external signing (experimental)
===================================

.. warning::

   This guide covers the **unreleased experimental CSC v1 synthetic
   laboratory** on the LibreSign development branch. It does not describe a
   production-ready personal signing provider, a qualified certificate,
   CSC 2.2, or a feature available in LibreSign 13, 14, or 15.

Overview and security model
---------------------------

The administrator configures one or more external-signing *integration
instances*. An instance identifies a CSC driver, a service endpoint, an
enabled state, and optional write-only secrets. An enabled instance is not
automatically an eligible signing method. A signer must still be authorized
for a particular LibreSign signature request, and the provider must separately
authorize use of its private key.

For the initial laboratory, an operator must independently pin the **exact**
synthetic HTTPS endpoint and the **SHA-256 fingerprint** of the synthetic
signing certificate. The configured integration must match both pins, be
enabled, and have **no administrator access token or other secret**. A
shared administrative token is never evidence of the signer's consent.

Production CSC credentials remain blocked until the provider proves
individual authentication and operation-bound signature authorization
(for example, a signer-authorized SAD). Laboratory tests do not establish
certificate-path trust or the legal identity of a person.

Prerequisites
-------------

* Use a LibreSign development build containing both the external signing
  backend and signer interface. The experimental feature is disabled by
  default.
* Install the SignerPHP CSC adapter shipped with the tested application
  dependency lock. The driver catalog reports whether its adapter is
  installed; this does not imply that a provider is configured.
* Use an administrator-approved synthetic CSC test provider with a public
  **HTTPS DNS name**. Private addresses, IP-literal endpoints, local DNS
  suffixes, redirects, credentials in URLs, and query strings are not
  supported by the configured remote transport.
* The Nextcloud system configuration must **not** enable
  ``allow_local_remote_servers``, and must keep ``dns_pinning`` enabled.
  Review changes to these global security settings with the Nextcloud
  operator; do not weaken them for CSC.
* Obtain the synthetic certificate fingerprint from the controlled test
  laboratory by a separate trusted channel. It must be lowercase hexadecimal
  SHA-256 (64 characters), not a subject name or an identifier entered by
  the signer.

The internal loopback HTTP CSC fixture is intended for automated tests
only. It is not an operator-configurable replacement for the HTTPS endpoint
requirement.

Enable and configure the laboratory
-----------------------------------

Enable the application-level feature gate as the Nextcloud web-server user:

.. code-block:: console

   ./occ config:app:set libresign experimental_features --type boolean --value true

This **global LibreSign experimental gate** is separate from the
**enabled/disabled state of each CSC integration instance**. Both must permit
the operation. Turning off the experimental gate hides the corresponding
administrative and signer-facing experimental endpoints without affecting
traditional LibreSign signature methods.

Have the Nextcloud system operator set the exact laboratory endpoint and
certificate pin in the Nextcloud system configuration:

.. code-block:: php

   // Example entries in Nextcloud config/config.php; replace both values.
   'libresign_csc_synthetic_lab_url' => 'https://csc-lab.example.org/csc',
   'libresign_csc_synthetic_lab_certificate_sha256' => 'replace-with-64-lowercase-hex-digits',

The examples above are **placeholders**, not usable credentials or a
trusted laboratory. They deliberately do not name a production signing
provider. The configured CSC service URL must be byte-for-byte identical
to the operator-pinned URL.

In the LibreSign administration interface, open **External signing
providers**, select the **Cloud Signature Consortium (CSC)** driver, and
create an integration with a descriptive name and the pinned HTTPS URL.
Do not supply an access token for the synthetic laboratory. Save and then
enable the instance. Each instance has its own identifier and optimistic
revision, so an administrator can manage multiple instances of one driver.

Secret handling and administrative lifecycle
--------------------------------------------

A secret field is write-only: an existing value is reported as configured,
but never returned to the browser. Leave a configured secret blank to
preserve it, enter a replacement to rotate it, or explicitly clear an
optional secret. An instance with any configured secret is **not eligible
for synthetic personal signing**.

Editing, enabling, disabling, and deleting instances use revision checks.
An HTTP 409 conflict can mean that another administrator changed the
instance, or that a signing session is still unresolved. In particular,
an uncertain private-key submission must retain the pinned integration
configuration for reconciliation. Do not delete or rotate an instance to
"clear" an uncertain signing result. Re-read the current instance and
investigate the unresolved session before another administrative operation.

A deleted instance is tombstoned for audit; its endpoint configuration and
encrypted secrets are erased. Deleting an integration is not a way to
cancel an operation already submitted to a remote provider.

Cryptographic scope
-------------------

The experimental subset uses CSC 1.0.4.0-style credential discovery and
remote signing through SignerPHP. The certificate eligibility checks require
a currently valid X.509 certificate with an **RSA public key of at least
2,048 bits**, compatible key usage, **SHA-256**, and
**RSA PKCS#1 v1.5** signing. The tested PDF output profiles are
**PDF Basic** (``pdf-basic``) and **PAdES Baseline B-B**
(``pades-baseline-b``), subject to source PDF/DocMDP restrictions.

These constraints are the *implemented laboratory subset*, not a statement
of full CSC conformance, trust-chain validation, long-term validation,
PAdES B-T/B-LT/B-LTA support, or provider-specific authorization.

Sessions, recovery and uncertain results
----------------------------------------

LibreSign stores the authorized signing session on the server. Its
identity, SignRequest, document revision, certificate, and integration
cannot be substituted by the browser. The relevant states include
preparation, authorization pending, ready, signing pending, signature
received, completing, completed, rejected, expired, failed, and uncertain.

A new HTTP request or PHP process may resume an existing permitted session
after **fresh signer verification**. If a remote ``signHash`` call times out
after it could have been submitted, LibreSign must treat the result as
**uncertain**. An expired lease or a failed HTTP response does not prove
that the provider did not sign. Do not automatically resubmit the
private-key operation, delete the session, or tell the signer to start again.

On a confirmed result, LibreSign must validate the final PDF cryptographically,
check the exact source revision and earlier signatures/DocMDP restrictions,
and publish the result to the original request at most once before showing
success. An uncertain result requires operator/provider reconciliation,
not a "retry" of the private-key operation.

Troubleshooting and validation
------------------------------

* **No CSC option:** check the global feature gate, driver availability,
  integration enabled state, exact operator pin and empty synthetic secret
  set. Traditional LibreSign methods should remain available.
* **No eligible certificate:** check expiry, RSA key size, signing key
  usage, fingerprint pin and laboratory discovery response. Do not
  loosen the certificate checks simply to make the credential appear.
* **HTTP 409 on administration:** refresh the instance revision and
  check for unresolved sessions; do not force deletion.
* **Pending or uncertain:** inspect the server-side session state and
  the test provider's operation ledger. Do not call ``signHash`` again
  merely because a browser or worker timed out.
* **PDF rejected:** check document revision, earlier PDF signatures,
  DocMDP permissions and the cryptographic validator output before
  permitting a publication or success notification.

The source tests for the experimental laboratory use synthetic certificates,
CSC fixtures, real SignerPHP PDF preparation/completion and cryptographic
validation. For release acceptance, additionally run a disposable
Nextcloud end-to-end test with an authenticated signer, an invited guest,
PDF Basic and PAdES B-B, concurrent requests, and restart/reconciliation.
Test data, database, Nextcloud configuration and storage must be isolated
from production. Automated laboratory interoperability **does not**
homologate a real CSC provider.

See the `external signing guide for signers <../user_manual/external_signing.html>`_.
