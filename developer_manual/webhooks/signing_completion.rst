.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

==============================
Signing workflow completed
==============================

**Event:** ``OCA\Libresign\Events\SigningRequestCompletedEvent``

When it is emitted
------------------

This event indicates that the signing **workflow** for a document or envelope
has reached LibreSign's completed status. It is not emitted for an individual
signer completing one step while the overall request is still partially
signed. An envelope completes when its overall signing workflow reaches the
completed state, rather than when an individual file is signed.

Completion is not evidence that every invited participant signed: policy may
allow a workflow to finish after a signer rejects. Inspect the final workflow
and evidence using the authenticated LibreSign API when that distinction
matters to your system.

Received body
-------------

After registering the event as described in :doc:`configuration`, the receiver
gets Nextcloud's event wrapper. This is a synthetic example; ``user`` can be
``null`` when no Nextcloud user session is active.

.. code-block:: json

   {
     "event": {
       "class": "OCA\\Libresign\\Events\\SigningRequestCompletedEvent",
       "contractVersion": 1,
       "eventId": "libresign.workflow.completed.v1:4ce5a91a-3f2c-4cf0-b4a3-8baad19ac82f",
       "requestUuid": "4ce5a91a-3f2c-4cf0-b4a3-8baad19ac82f",
       "requestType": "envelope",
       "status": "completed"
     },
     "user": null,
     "time": 1794170000
   }

``requestUuid`` identifies the whole signing request, not an individual
signer's invitation UUID. ``requestType`` is ``document`` or ``envelope``.
``contractVersion`` is the version of this event's data contract, not a
LibreSign release number. ``eventId`` is a stable correlation/deduplication
key for this request, not a unique identifier of each HTTP delivery attempt.

Use the same ``eventId`` to avoid repeated processing of duplicate deliveries.
If a completed workflow is later reopened, check its current status before
acting on a new notification with the same identifier.

The event delivers metadata only; it does not contain a signed PDF or grant
file-download permissions. The LibreSign event data does not contain signer
email addresses, private file URLs, document contents or credentials.
Nextcloud may include information about the current user in its outer
``user`` field. Retrieve signed documents and evidence separately using
authenticated, authorized LibreSign and Nextcloud file operations.
