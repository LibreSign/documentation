.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

.. _integration-lifecycle:

Notifications, completion and document recovery
===============================================

Choose **one owner** for invitation delivery, but always reconcile the
document-level state before applying the business system's final status.

Notification ownership
----------------------

**LibreSign delivers invitations (default)**
   Let the configured LibreSign channels notify signers. This is safest when
   the integrator has no verified way to obtain the correct, per-signer
   invitation URL. Email, activity and optional gateways depend on server
   settings and policy. A request being accepted does not prove the recipient
   received the message.

**The integrator controls when LibreSign sends**
   On creation, set ``notify: 0`` on each relevant ``NewSigner`` to suppress
   initial automatic invitations. Then invoke ``POST /notify/signers`` as the
   authenticated requester, as demonstrated in
   :doc:`../api/external-email-signers`. **LibreSign**, not the integrator,
   still sends the invitation with its authorized signer link.

**The integrator sends its own message**
   This is a separate, conditional design. Only send a signing URL if the
   installed release offers a **verified, authorized** way to obtain that
   signer's invitation. The reviewed OpenAPI does not establish a generic
   invitation-link retrieval endpoint. Never construct links from file IDs or
   signer UUIDs, or share Nextcloud credentials. If no such contract has been
   verified, use LibreSign's delivery endpoint instead.

**LibreSign sends on demand**
   The authenticated requester can invoke ``POST /notify/signers`` for
   selected signers on an existing, open request; LibreSign verifies requester
   permissions. The supported body has ``fileId`` and ``signers``. For example:

.. code-block:: json

   {
     "fileId": 123,
     "signers": [{"email": "signer@example.test"}]
   }

The transport's acknowledgement is **not** delivery confirmation. Avoid blind
retries that could duplicate messages. Notification status endpoints differ
between releases; verify them in :doc:`../api/openapi`. Optional gateway
integrations, such as WhatsApp via Two-Factor Gateway where supported, are
separate services and are not bundled delivery guarantees.

What counts as complete?
------------------------

.. list-table:: File-level status values
   :header-rows: 1
   :widths: 14 24 62

   * - Value
     - Name
     - Business interpretation
   * - ``0``
     - Draft
     - The request is not ready for signing.
   * - ``1``
     - Able to sign
     - At least one required signing action remains.
   * - ``2``
     - Partially signed
     - Some actions may be complete; do not issue the final document.
   * - ``3``
     - Signed
     - Candidate final state for the **specified file**; confirm scope and authorized retrieval.
   * - ``4``
     - Deleted
     - Not a successful signing result; reconcile as terminated.

Other statuses and signer rejection states may be version- or policy-specific:
consult :doc:`../api/openapi` and do not silently map an unknown state to
``3``. A completed workflow is not proof that every invited signer signed:
under some policies a rejection may coexist with final workflow completion.
An individual signer action is not necessarily the completion of the entire
file **or envelope**. For envelopes, check the
parent and required child file results, not just the first child.

.. code-block:: text

   Draft -> Able to sign -> Partially signed -> Signed (file/envelope complete)
                              |
                              +----> more signer actions pending
   Deleted / rejected / invalid / unknown -> explicit exception handling

Polling and reconciliation
--------------------------

``GET /file/list`` with ``details=1`` and a specific ``fileIds[]``
filter is available on all documented release lines. Its response is
authorization-filtered, so a missing record is **not** proof of deletion.

.. code-block:: bash

   export API_BASE="https://cloud.example.com/ocs/v2.php/apps/libresign/api/v1"
   export NC_USER="integration-account"
   export NC_APP_PASSWORD="<retrieve-from-secret-manager>"
   export FILE_ID="123"

   curl --fail-with-body -sS \
     -u "$NC_USER:$NC_APP_PASSWORD" \
     -H "OCS-APIRequest: true" \
     -H "Accept: application/json" \
     "$API_BASE/file/list?details=1&fileIds%5B%5D=$FILE_ID"

Check ``ocs.meta``, locate the intended ``ocs.data.data[]`` item, and
inspect its ``status``, ``nodeType``, ``files`` and signer fields as
available to the caller. Use bounded retries, backoff and periodic full
reconciliation. Treat timeouts and ``404``/``403``/empty results distinctly.

Native webhooks: version-specific completion events
---------------------------------------------------

Nextcloud's `Webhook Listeners <https://docs.nextcloud.com/server/stable/admin_manual/webhook_listeners/index.html>`_
app can subscribe to compatible application events. Feature availability and
the event class are tied to the **installed LibreSign release**, not simply to
the Nextcloud version or the OCS ``/api/v1`` path.

.. include:: _native-webhooks.inc

Even when a release supports a completion event, the Nextcloud worker sends
HTTP asynchronously. Do not assume exactly-once delivery, ordering or retries.
Authenticate the receiver, deduplicate received events, then reconcile the
current workflow with the requester's authorized OCS identity. A webhook
notification never authorizes a PDF download on its own.

Recover the final PDF and evidence
----------------------------------

Use the LibreSign API to identify the completed **file or envelope** and
Nextcloud's authenticated file interfaces to retrieve bytes **only under an
account with file read/download rights**. The OCS listing reports workflow
metadata, not a universal anonymous PDF-download entitlement. For an
authorized path already known to the account, the standard Nextcloud WebDAV
download is:

.. code-block:: bash

   # Substitute the real, URL-encoded path visible to NC_USER.
   curl --fail-with-body -sS \
     -u "$NC_USER:$NC_APP_PASSWORD" \
     -o signed-document.pdf \
     "https://cloud.example.com/remote.php/dav/files/$NC_USER/Contracts/signed.pdf"

Do **not** assume the original path now refers to the final signed revision:
resolve the actual completed file/node and current access rights on the
installed release before downloading it. Signed-node metadata and public
validation URLs are not substitutes for requester authorization. Do not
confuse a public verification result with the signed document or a complete
evidence archive.

Use authenticated ``GET /file/validate/file_id/{fileId}`` with file-read
permissions for validation metadata. The UUID validation route has separate
privacy restrictions and is **not** unrestricted access to evidence.
Availability of audit logs, certificate chain, timestamps, revocation proof
or downloadable evidence packages depends on the installed version, selected
signing method and configured providers. Do not promise a single evidence-download endpoint
that is absent from :doc:`../api/openapi`.

See :doc:`../api/external-email-signers` for the executable
``SIGNED_DAV_URL`` / ``SIGNED_OUTPUT`` retrieval flow, and
`Nextcloud WebDAV file operations <https://docs.nextcloud.com/server/stable/developer_manual/client_apis/WebDAV/basic.html>`_
for path discovery. Neither a LibreSign UUID nor a signed-node ID is a WebDAV
path. Review :doc:`deployment` for access and retention checks.
