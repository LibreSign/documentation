.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

=======================
LibreSign event catalog
=======================

LibreSign provides signing-workflow events through Nextcloud's
**Webhook Listeners** app. An administrator can subscribe to any event
listed below by its fully qualified PHP class name. The subscription
is managed by Nextcloud and delivered asynchronously by its background
jobs. All six classes implement
``OCP\EventDispatcher\IWebhookCompatibleEvent``.

Available events
----------------

All classes use the ``OCA\Libresign\Events`` namespace.

.. list-table:: Webhook-compatible events
   :header-rows: 1
   :widths: 38 62

   * - Class name
     - When it is emitted
   * - ``SigningRequestReadyEvent``
     - A document or envelope is created ready to sign, or its workflow
       moves from draft to ready. Repeated updates to the ready state do
       not generate another event.
   * - ``SignerSignedWebhookEvent``
     - One signer completes a signature for a document. An envelope
       containing multiple documents can produce an event per signed
       document, all associated with the same envelope request.
   * - ``SignerRejectedWebhookEvent``
     - A signer's rejection is persisted, once per business rejection,
       regardless of how many identification methods are configured.
       The payload indicates whether the workflow was canceled.
   * - ``SigningRequestCompletedEvent``
     - The document or parent envelope reaches its completed state.
       Partial signatures alone do not generate a completion event.
       A workflow may complete even if a signer rejected, depending on
       its rejection policy.
   * - ``SigningRequestCanceledEvent``
     - A rejection causes the document or parent envelope's workflow
       to enter the canceled state. This does not represent the removal
       of an individual signer.
   * - ``NotificationDeliveryStatusChangedEvent``
     - A notification submission attempt receives a persisted outcome
       from the configured channel adapter. This does not establish
       that a recipient received or read the message.

Event payloads
--------------

The serialized ``event`` object of every LibreSign webhook contains:

- ``contractVersion``: version of the event's JSON contract (``1``).
- ``eventId``: stable identifier for deduplicating repeated deliveries.
- ``requestUuid``: identifier of the signing workflow or parent envelope.
- ``requestType``: ``document`` or ``envelope``.

Each event also provides these fields:

.. list-table:: Event-specific fields
   :header-rows: 1
   :widths: 38 62

   * - Class name
     - Additional fields
   * - ``SigningRequestReadyEvent``
     - ``status: "ready_to_sign"``.
   * - ``SignerSignedWebhookEvent``
     - ``status: "signed"``, ``documentUuid``, ``signerId``.
   * - ``SignerRejectedWebhookEvent``
     - ``status: "rejected"``, ``documentUuid``, ``signerId``,
       ``workflowCanceled`` (boolean).
   * - ``SigningRequestCompletedEvent``
     - ``status: "completed"``.
   * - ``SigningRequestCanceledEvent``
     - ``status: "canceled"``.
   * - ``NotificationDeliveryStatusChangedEvent``
     - ``deliveryId``, ``channel``, ``state``, ``attempt``.

For workflow events, ``eventId`` is derived from the request UUID and
transition. Signer events use deterministic identifiers associated with
the persisted signing or rejection action. Notification delivery events
identify the delivery record, attempt and outcome. Do not rely on the
arrival order or assume that a delivery occurs exactly once.

The notification ``state`` can be ``accepted``,
``temporary_failure``, ``permanent_failure``, ``failed``,
``unknown`` or ``canceled``. In particular, ``accepted`` means that
the channel adapter accepted the submission, **not** that an email or
other message reached its recipient. Pending and in-progress attempts
are not published as outcome events.

Receiving events securely
-------------------------

Subscribe to the complete class name, for example:

``OCA\Libresign\Events\SigningRequestCompletedEvent``

Webhook Listeners sends the event through Nextcloud's JSON wrapper.
The receiver must authenticate each request, associate ``requestUuid``
with a workflow it is authorized to handle and deduplicate by
``eventId``. Individual signer events expose a numeric ``signerId``
and ``documentUuid`` for correlation, but not invitation links or
bearer-style signing tokens.

Webhooks contain neither the signed PDF nor credentials granting access
to it. Retrieve and validate signed documents separately using an
authorized LibreSign/Nextcloud account. Configure working Cron jobs to
process asynchronous deliveries.

See :doc:`configuration` for subscriptions and receiver authentication,
:doc:`signing_completion` for a complete event body, and
:doc:`external-signing-flow` for the signing and PDF-retrieval workflow.

``occ webhook_listeners:list`` lists **registered subscriptions** on a
Nextcloud installation; it is not a complete catalog of event classes.
