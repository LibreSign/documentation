..
   SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
   SPDX-License-Identifier: CC-BY-3.0

External signing with CSC (experimental)
========================================

.. warning::

   External CSC signing currently supports **synthetic test laboratory
   credentials only** in unreleased LibreSign development builds. It does
   not sign with your personal certificate at a production provider or prove
   your real-world identity. Your ordinary LibreSign signing methods are
   unaffected.

When this method is available
-----------------------------

An administrator must have enabled the LibreSign experimental feature,
configured and enabled a matching CSC laboratory integration, and verified
that its synthetic certificate is eligible. The option appears only for
signers and requests the backend permits.

The initial experiment does not offer CSC signing for requests that require
a visible PDF signature field, mandatory geolocation, or identification
document approval. These workflows continue to use their supported
LibreSign signing methods.

Verify that you are the invited signer
--------------------------------------

Open the LibreSign signature-request link and review the document in the
usual signing screen. Select **External signing (experimental)** when it
appears.

* **Nextcloud account:** sign in with the account bound to this signature
  request and choose the account verification method where offered.
* **Guest without a Nextcloud account:** use the email address bound to the
  invitation, request the usual LibreSign verification code, and enter that
  code. The invitation link alone is not sufficient to discover remote
  signing credentials.

The code is checked by LibreSign for the specific request; it is not a
CSC provider credential or remote private-key consent.

Select a synthetic credential and PDF format
--------------------------------------------

After verification, choose an available CSC integration and one of its
eligible **synthetic** certificates. Review the displayed certificate
subject, expiry and SHA-256 fingerprint. LibreSign excludes certificates
that do not satisfy the experiment's required certificate properties.

Choose **PDF Basic** or **PAdES B-B** if offered for the selected
certificate and document. The experimental laboratory uses SHA-256 with
RSA PKCS#1 v1.5 signatures and RSA keys of at least 2,048 bits. Support
is limited by existing PDF signatures and DocMDP permissions.

Select **Prepare external signature**. Preparation binds the server-owned
session to the authorized signer, current request, document revision and
chosen synthetic certificate. It does not yet mean that the document was
signed.

Continue and check the status
-----------------------------

Select **Continue external signing** when offered. During the operation
the interface can show preparation, required authorization, pending
signature, signature received, publication in progress, completion,
rejection, expiry, failure, or an **uncertain** result.

The document is complete only after LibreSign has verified and published
the signed PDF to the original request. A server error or a browser refresh
is **not** proof of signature failure.

Use **Check signing status** to read the existing session. Returning to the
page or using another browser request requires fresh signer verification.
LibreSign must not submit the remote private-key operation a second time
when a previous attempt may already have reached the provider.

If the result is uncertain
--------------------------

An uncertain status means the provider *may already have signed* even if
LibreSign did not receive the HTTP response. **Do not start a new attempt,
request a second certificate operation, or assume that an expired browser
session allows resubmission.** Contact the administrator and provide the
request reference without sharing your verification code. The administrator
must reconcile the remote result and the server-owned session.

If the option is unavailable
----------------------------

The experimental feature may be switched off, your request may be ineligible,
or no eligible synthetic provider or certificate may exist. Do not try
other people's credential identifiers or change the request address; the
server checks the authorized signer independently. Use one of the standard
methods offered for your document or contact the administrator.

For administration, laboratory prerequisites and further troubleshooting,
see the `administrator CSC guide <../admin_manual/csc.html>`_.
