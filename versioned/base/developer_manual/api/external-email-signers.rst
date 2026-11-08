External email signers: integration
===================================

An existing system may retain its own interface and authentication while
its backend creates LibreSign signature requests. An external signer may
sign in LibreSign without a Nextcloud account.

Authentication and identity are separate
----------------------------------------

The integrator uses a dedicated Nextcloud account authorized to request
signatures, over HTTPS. HTTP Basic with a revocable Nextcloud App Password
and the OCS-APIRequest: true header is supported. OpenAPI also declares
bearer authentication, but external OAuth/OIDC tokens only work if the
deployed Nextcloud server validates them for a mapped, permitted account.
SSO may create a Nextcloud browser session; it is not automatically an
OCS service credential. Never send integrator credentials to the signer.

External signers are identified by email. Enable the email identify
method and an allowed signing method (clickToSign or emailToken) in the
effective LibreSign policies. The latter uses a separate emailed code.
Receipt of an invitation is not strong legal identity verification.
Administrators also must configure mail delivery, a signing certificate
engine, writable storage, requester permissions, validation privacy,
and any mandatory identity-document or visible signature policies.

Create and invite with OCS v1
-----------------------------

All four documented release lines use this OCS prefix:

.. code-block:: text

   https://cloud.example.com/ocs/v2.php/apps/libresign/api/v1

The companion examples in examples/external-email-signers contain
request.json, flow.sh (bash/curl/jq/base64) and flow.php (PHP 8.1+
with ext-curl). They use this synthetic request:

.. code-block:: json

   {
     "name": "Synthetic service agreement", "status": 1,
     "file": {"name": "synthetic.pdf", "base64": "REPLACE_WITH_BASE64"},
     "signers": [{"displayName": "External Test Signer", "notify": 0,
       "identifyMethods": [{"method": "email",
         "value": "signer@example.test", "mandatory": 1}]}]
   }

Replace the PDF with synthetic bytes and the reserved example.test
mailbox with an inbox you control. The scripts POST /request-signature,
verify ocs.meta and retain ocs.data.id (LibreSign file ID) and
ocs.data.uuid (document UUID). notify: 0 disables initial auto-invites;
the scripts explicitly POST /notify/signers with the returned file ID:

.. code-block:: json

   {"fileId": 123, "signers": [{"email": "signer@example.test"}]}

A processed notification request is not proof of email delivery.
Do not send duplicate invitations. Use an actual test inbox.

.. code-block:: bash

   export NC_BASE_URL=https://cloud.example.com
   export NC_USER=integration-user
   export PDF_PATH=./synthetic.pdf
   export SIGNER_EMAIL=signer@controlled-mailbox.example
   # cURL: use a private netrc file (mode 0600) with App Password
   export NC_NETRC="$HOME/.config/libresign-integration.netrc"
   ./flow.sh start
   # PHP: obtain the App Password from private environment
   export NC_APP_PASSWORD=provided-by-secret-manager
   php flow.php start

The signer receives an individual invitation link, opens the public
signing browser page and completes the configured identification and
signature checks without Nextcloud login. A file UUID differs from the
signer's sign-request UUID; never generate or disclose a genuine link.

Poll, validate and retrieve
---------------------------

Use the integrator identity to GET /file/list?details=1; find the
saved file UUID in the paginated ocs.data.data array. Common statuses:
0 draft; 1 ready; 2 partially signed; 3 signed; 4 deleted. Check all
required signers and envelope children before marking completion.

.. code-block:: bash

   export FILE_UUID=UUID_RETURNED_BY_START
   ./flow.sh check
   php flow.php check

GET /file/validate/file_id/{fileId} enforces file access and returns
available validation data. Public /file/validate/uuid/{uuid} is
restricted by the private-validation policy, not unrestricted evidence
access. Validation output is not a guaranteed standalone audit dossier.

.. code-block:: bash

   export FILE_ID=ID_RETURNED_BY_START
   ./flow.sh validate
   php flow.php validate

The OCS specification has no generic binary GET /file/download/{id}.
The public LibreSign PDF viewer is governed by validation privacy, not
a general backend download authorization. Discover the actual signed
file path in the integrator's readable Nextcloud Files folder, using
authenticated WebDAV PROPFIND if necessary. Then use WebDAV GET:

.. code-block:: text

   /remote.php/dav/files/<integration-user>/<encoded-signed-PDF-path>

Neither a LibreSign file ID, nodeId, signedNodeId nor sign-request UUID
is a WebDAV path. Both scripts support retrieve with SIGNED_DAV_URL
and SIGNED_OUTPUT set to a private output path. Verify the downloaded
PDF signature and certificate chain independently. Do not bypass file
permissions or query LibreSign database tables directly.

Ordering, release differences, errors and security
--------------------------------------------------

Use separate signers[] records and signingOrder when ordered signing
is configured. Sequential recipients are activated in order; parallel
signers can act independently. files[] can create envelopes when enabled.
The 13 and 14 request OpenAPI contracts declare signatureFlow values
parallel and ordered_numeric; 15 and main do not declare that request
property. Use effective server policy instead of sending undocumented
parameters. Do not claim main-only features exist in stable versions.

Typical errors: 401 authentication; 403 file permission; 404 missing
or inaccessible resource; 412 missing OCS header where enforced; 422
validation or policy violation (inspect ocs.data.message/errors).
Main notifications also document 500/502 for failed/unconfirmed
transport; older contracts differ. POST is not generally idempotent:
check for existing workflows before retrying after a timeout.

Protect invitation links, App Passwords, signer metadata and PDFs.
Poll with backoff; native webhooks require a separately verified
LibreSign event contract for the deployed Nextcloud version.

Runtime evidence on main includes Playwright
sign-envelope-unauthenticated-visible-signature.spec.ts,
sign-email-token-unauthenticated.spec.ts, multi-signer-sequential.spec.ts,
and multi-signer-parallel.spec.ts. These do not prove stable-branch
behavior unless rerun there. Static contract checks do not prove
SMTP, guest browser signing or certificate trust.

Consult the OpenAPI reference beside this page for exact schemas.
