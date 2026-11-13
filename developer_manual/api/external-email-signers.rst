External email signers: integration
===================================

**Applicable release:** LibreSign |LibreSignRelease| on Nextcloud |NextcloudRelease|.
The exact source commit and contract hash are published as
`pinned OpenAPI provenance <openapi.provenance.json>`_.
The path /api/v1 is the API protocol version, not the LibreSign major version.

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

The request structure is selected for this documentation release. Use only
the version-specific fixture below with the cURL/Bash or PHP clients.
The version selector is mandatory.

The runnable clients and matching fixture are kept in this documentation
branch (not in another release's source):

* `Bash client (flow.sh) <https://github.com/LibreSign/documentation/blob/main/examples/external-email-signers/flow.sh>`_
* `PHP client (flow.php) <https://github.com/LibreSign/documentation/blob/main/examples/external-email-signers/flow.php>`_
* `LibreSign main fixture (request-main.json) <https://github.com/LibreSign/documentation/blob/main/examples/external-email-signers/request-main.json>`_

Clone the **matching documentation branch**, then work in the examples
directory (Git required):

.. code-block:: bash

   git clone --depth 1 --branch main https://github.com/LibreSign/documentation.git
   cd documentation/examples/external-email-signers

Keep the clients and their ``request-*.json`` fixtures together. Consult this
release's :doc:`openapi` and its pinned `OpenAPI JSON <openapi.json>`_ when
adapting the request to a real integration.

For a ready-to-import n8n workflow, see the `shared LibreSign + n8n guide
<https://github.com/LibreSign/documentation/blob/a7b772cf579fcbd734810661f6e2104bd8444e6a/examples/n8n/README.md>`_. It uses a single external signer, explicit invitation,
bounded OCS polling, automatic WebDAV discovery and authenticated download
from the default LibreSign folder. Select this LibreSign release in the
workflow configuration: versions 13/14 use ``mandatory: 1``; versions
15/development use ``requirement: "required"``. Native completion events
belong to the development documentation and are not required by polling.
Confirm that this release meets the OCS and WebDAV prerequisites before
using the shared workflow. The pinned link keeps its README and relative
JSON workflow at the same immutable revision.
Do not replace release-specific cURL/PHP fixtures with development payloads.

.. include:: _external-email-signers-release.inc

The scripts POST /request-signature,
verify ocs.meta and retain ocs.data.id (LibreSign file ID) and
ocs.data.uuid (document UUID). notify: 0 disables initial auto-invites;
the scripts explicitly POST /notify/signers with the returned file ID:

.. code-block:: json

   {"fileId": 123, "signers": [{"email": "signer@example.test"}]}

A processed notification request is not proof of email delivery.
Do not send duplicate invitations. Use an actual test inbox.

Run the examples **only on a disposable test installation**, never on a
production service. Prerequisites are HTTPS, the LibreSign release described
by this page installed on a compatible Nextcloud, email delivery to a
controlled test inbox, enabled email identification/signing methods, and a
signing certificate engine. The requesting Nextcloud account needs permission
to request signatures and access to the relevant Files folder. Create a
revocable **App Password** for this dedicated account under Nextcloud's
**Personal settings > Security**. Do not share it with the external signer.

For Bash, install Bash, cURL, jq and GNU ``stat`` (Linux). For PHP, use
PHP 8.1+ with the cURL extension. From the cloned examples directory, set
the common variables below; ``PDF_PATH`` must be an **absolute path** to a
valid, synthetic PDF, and the signer email must be a deliverable test inbox
you control (replace all illustrative values):

.. code-block:: bash

   export NC_BASE_URL=https://your-test-nextcloud.example.org
   export NC_USER=integration-user
   export PDF_PATH=/absolute/path/to/synthetic.pdf
   export SIGNER_EMAIL=signer@your-controlled-test-domain.example.org

Use **one** client for ``start``, not both: each invocation creates a new
signature request and can send a new invitation.

For **Bash**, keep the App Password in a private ``netrc`` file whose
``machine`` matches the host in ``NC_BASE_URL``:

.. code-block:: text

   machine your-test-nextcloud.example.org
     login integration-user
     password YOUR_NEXTCLOUD_APP_PASSWORD

.. code-block:: bash

   export NC_NETRC="$HOME/.config/libresign-integration.netrc"
   umask 077
   mkdir -p "$HOME/.config"
   touch "$NC_NETRC"
   chmod 600 "$NC_NETRC"
   ${EDITOR:-vi} "$NC_NETRC"  # enter the netrc contents shown above
   bash flow.sh start

For **PHP instead**, provide the App Password privately, not as a literal
shell command argument or a checked-in file:

.. code-block:: bash

   read -r -s -p "Nextcloud App Password: " NC_APP_PASSWORD; echo
   export NC_APP_PASSWORD
   php flow.php start

Keep the resulting ``fileId`` and ``fileUuid``; the scripts do not sign
on the external person's behalf. Clear ``NC_APP_PASSWORD`` from the
shell environment when finished with the PHP client.

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
   bash flow.sh check  # or: php flow.php check

GET /file/validate/file_id/{fileId} enforces file access and returns
available validation data. Public /file/validate/uuid/{uuid} is
restricted by the private-validation policy, not unrestricted evidence
access. Validation output is not a guaranteed standalone audit dossier.

.. code-block:: bash

   export FILE_ID=ID_RETURNED_BY_START
   bash flow.sh validate  # or: php flow.php validate

The OCS specification has no generic binary GET /file/download/{id}.
The public LibreSign PDF viewer is governed by validation privacy, not
a general backend download authorization. Discover the actual signed
file path in the integrator's readable Nextcloud Files folder, using
authenticated WebDAV PROPFIND if necessary. Then use WebDAV GET:

.. code-block:: text

   /remote.php/dav/files/<integration-user>/<encoded-signed-PDF-path>

Neither a LibreSign file ID, nodeId, signedNodeId nor sign-request UUID
is a WebDAV path. After confirming the workflow is signed, locate the actual
PDF in **Nextcloud Files** with the same authorized integration account (or
use authenticated WebDAV PROPFIND to find the file's path). Set the full URL
with URL-encoded path segments and a private local destination; replace this
illustrative path with the real authorized location:

.. code-block:: bash

   export SIGNED_DAV_URL="$NC_BASE_URL/remote.php/dav/files/$NC_USER/Signed%20Documents/synthetic.pdf"
   export SIGNED_OUTPUT="$HOME/signed-synthetic.pdf"
   bash flow.sh retrieve  # or: php flow.php retrieve

Both clients require the App Password again for later commands (the Bash
client reads ``NC_NETRC``; the PHP client reads ``NC_APP_PASSWORD``).
Verify the downloaded PDF signature and certificate chain independently.
Do not bypass file permissions or query LibreSign database tables directly.

Ordering, release differences, errors and security
--------------------------------------------------

Use separate signers[] records and signingOrder when ordered signing
is configured. Sequential recipients are activated in order; parallel
signers can act independently. files[] can create envelopes when enabled.
The specific supported request options for this LibreSign release are
documented above. Do not copy parameters from other major versions.

Typical errors: 401 authentication; 403 file permission; 404 missing
or inaccessible resource; 412 missing OCS header where enforced; 422
validation or policy violation (inspect ocs.data.message/errors).
Main notifications also document 500/502 for failed/unconfirmed
transport; older contracts differ. POST is not generally idempotent:
check for existing workflows before retrying after a timeout.

Protect invitation links, App Passwords, signer metadata and PDFs.
Poll with backoff; native webhooks require a separately verified
LibreSign event contract for the deployed Nextcloud version.

Validate browser signing, SMTP delivery and certificate trust on the target
installation before relying on the integration. Contract checks alone do
not establish operational compatibility.

Consult the OpenAPI reference beside this page for exact schemas.
