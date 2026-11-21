.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

=======================================
External signing with native webhooks
=======================================

This guide follows an **existing external application** that keeps its own
interface and authentication. It creates a LibreSign signing request for
a person **without a Nextcloud account**, controls the invitation, receives
a signed-workflow event, then retrieves the final PDF with authorization.

.. important::

   Webhook Listeners delivers **JSON event metadata**, not the signed PDF.
   Configure an authenticated receiver in Nextcloud. Retrieve documents
   separately using credentials authorized for the signing request.

1. Prepare the Nextcloud environment
------------------------------------

Enable Webhook Listeners and configure Nextcloud's **Cron** background
jobs. Ensure the server can reach the receiver over HTTPS and can deliver
e-mail.

As in Nextcloud's official documentation, these ``occ`` examples specify
subcommands without an installation-specific wrapper:

.. code-block:: console

   occ app:enable webhook_listeners
   occ background:cron

Use the Nextcloud CLI appropriate to your installation and privileges, as
explained in :doc:`configuration`. Selecting Cron mode does **not** schedule
``cron.php``: configure an actual scheduler and confirm that background jobs
run, following the Nextcloud guidance linked there.

For testing, use an SMTP capture server such as Mailpit. Use a dedicated
Nextcloud integration account with an App Password and only the permissions
needed to create requests and access its own PDFs.

2. Register the native completion event
---------------------------------------

An authorized **Nextcloud administrator** registers a webhook subscription
using Webhook Listeners' own OCS API, not LibreSign's signing API.

.. code-block:: bash

   export NC_URL="https://cloud.example.test"
   export NC_ADMIN="nextcloud-admin"
   export NC_ADMIN_APP_PASSWORD="<from-secret-manager>"
   export RECEIVER_URL="https://integrator.example.test/webhooks/libresign"
   export RECEIVER_SECRET="<random-per-receiver-secret>"

   curl --fail-with-body -sS \
     -u "$NC_ADMIN:$NC_ADMIN_APP_PASSWORD" \
     -H "OCS-APIRequest: true" \
     -H "Accept: application/json" \
     --data-urlencode "httpMethod=POST" \
     --data-urlencode "uri=$RECEIVER_URL" \
     --data-urlencode 'event=OCA\Libresign\Events\SigningRequestCompletedEvent' \
     --data-urlencode "authMethod=header" \
     --data-urlencode "authData[X-LibreSign-Webhook-Token]=$RECEIVER_SECRET" \
     "$NC_URL/ocs/v2.php/apps/webhook_listeners/api/v1/webhooks"

Inspect both HTTP status and ``ocs.meta.statuscode``. The receiver must
reject requests without the expected secret. Leave ``userIdFilter`` unset
for external signers, because the incoming wrapper's ``user`` can be null.
Exact administrative fields and authentication modes depend on the installed
Nextcloud Webhook Listeners version; see :doc:`configuration`.

3. Create the request without an initial invitation
---------------------------------------------------

Authenticate as the **integration requester**, not the signer. Prepare a
base64-encoded PDF and replace the sample ``<BASE64_PDF_BYTES>`` value.
The signer's e-mail is an identity method, not a Nextcloud username.

.. code-block:: bash

   export NC_USER="integration-account"
   export NC_APP_PASSWORD="<from-secret-manager>"
   export API="$NC_URL/ocs/v2.php/apps/libresign/api/v1"

   curl --fail-with-body -sS \
     -u "$NC_USER:$NC_APP_PASSWORD" \
     -H "OCS-APIRequest: true" \
     -H "Content-Type: application/json" \
     -H "Accept: application/json" \
     -d '{
       "name": "External contract",
       "file": {"name": "contract.pdf", "base64": "<BASE64_PDF_BYTES>"},
       "status": 1,
       "signers": [{
         "displayName": "External signer",
         "notify": 0,
         "identifyMethods": [{
           "method": "email",
           "value": "signer@example.test",
           "requirement": "required"
         }]
       }]
     }' \
     "$API/request-signature"

Capture the returned file ``id`` and workflow ``uuid``. Confirm the
request is ``Able to sign`` (status 1) before inviting anyone.
With ``notify: 0``, LibreSign does not send the initial invitation.
Verify the absence of an invitation in the test mail transport.

4. Send the invitation explicitly
---------------------------------

Send it using LibreSign's authenticated endpoint:

.. code-block:: bash

   export FILE_ID="123"  # replace with the returned request ID

   curl --fail-with-body -sS \
     -u "$NC_USER:$NC_APP_PASSWORD" \
     -H "OCS-APIRequest: true" \
     -H "Content-Type: application/json" \
     -d '{"fileId":123,"signers":[{"email":"signer@example.test"}]}' \
     "$API/notify/signers"

Replace the example numeric ID in the JSON. This endpoint lets **LibreSign**
send the signer's invitation; it does not provide a contract for extracting
or constructing a secret signing URL. Verify that the explicit request
produced the intended invitation without duplication. An HTTP success
response is not proof of delivery to the recipient.

5. Sign without a Nextcloud session
-----------------------------------

Open the invitation URL in a fresh browser profile **without Nextcloud
authentication**. Complete the signing method permitted by the configured
policy, such as ``clickToSign``. Email-token signing may require a
separate verification e-mail; the authentication policy determines the steps.

For multiple signers, the first signature may leave the document
``Partially signed``. That state is **not** a completion event. For an
envelope, wait for the parent envelope workflow to complete, not merely
one child PDF.

6. Receive, authenticate and correlate the event
------------------------------------------------

Nextcloud queues a ``WebhookCall`` background job. Cron performs an
asynchronous HTTP POST; the event is **not delivered synchronously** by
the signing endpoint. The receiver verifies the configured header, parses
the JSON body, and checks:

- ``event.class`` equals
  ``OCA\Libresign\Events\SigningRequestCompletedEvent``.
- ``event.contractVersion`` equals ``1``.
- ``event.status`` equals ``completed``.
- ``event.requestUuid`` maps to a request controlled by this integrator.
- ``event.eventId`` has not already been processed successfully.

For the JSON shape, including ``requestType`` (``document`` or
``envelope``) and an optional null ``user``, see
:doc:`signing_completion`. Persist the event ID and return a 2xx when
accepted. Do not expect exactly-once delivery, guaranteed ordering, or
automatic retries; run periodic, bounded reconciliation independently.

7. Recover and validate the signed document
-------------------------------------------

The event does not contain the PDF or authorize its download.
Using the **requesting account's** credentials, reconcile the current
state and determine the actual authorized file path:

.. code-block:: bash

   curl --fail-with-body -sS \
     -u "$NC_USER:$NC_APP_PASSWORD" \
     -H "OCS-APIRequest: true" \
     -H "Accept: application/json" \
     "$API/file/list?details=1&fileIds%5B%5D=$FILE_ID"

Check the intended entry's ``status``, ``uuid`` and file/envelope
membership. Resolve the final signed file through the authorized account's
file listing. **Never derive a WebDAV path from the webhook UUID.**

.. code-block:: bash

   export SIGNED_DAV_URL="https://cloud.example.test/remote.php/dav/files/integration-account/Contracts/contract.signed.pdf"

   curl --fail-with-body -sS \
     -u "$NC_USER:$NC_APP_PASSWORD" \
     -o signed-contract.pdf "$SIGNED_DAV_URL"

   pdfsig signed-contract.pdf

The path above is **illustrative**; use the actual authorized path in
your installation. Check the PDF signature's cryptographic validity,
coverage and trust chain separately. Verify that anonymous callers and
other authenticated users **cannot** retrieve the document. Do not
assume that the same HTTP denial status is used by every installation.

8. Handle envelopes and non-completion states
---------------------------------------------

An envelope may remain in Draft after ``POST /request-signature``,
even when status 1 was requested. Read the returned state before
notifying. Where authorized, use ``PATCH /request-signature`` with
the envelope ``uuid`` and ``status: 1`` to make it ready for signing.
The completion event for an envelope has ``requestType: "envelope"``.

When rejection policy ``cancel`` ends the workflow in Canceled
(status 6), it does **not** emit a completion event. Subscribe to
``SigningRequestCanceledEvent`` to handle workflow cancellation and
``SignerRejectedWebhookEvent`` to handle individual rejections.
Reconcile the authoritative state with authenticated API requests.

Integration verification checklist
----------------------------------

1. Register the native event subscription in Nextcloud and secure the
   receiver using the authentication mechanism supported by your installation.
2. Create a request with an external email signer and ``notify: 0``; confirm
   that no invitation is sent before calling ``/notify/signers``.
3. Complete signing in a browser without a Nextcloud session. Verify
   the authenticated HTTP POST from Nextcloud's background-job worker.
4. Match the event's ``requestUuid`` to a request owned by the integrator,
   deduplicate using ``eventId`` and reconcile the current workflow state.
5. Recover and validate the signed PDF using an authorized Nextcloud account.
   Confirm that unrelated and unauthenticated callers cannot download it.
