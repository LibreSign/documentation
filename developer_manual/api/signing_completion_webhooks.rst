.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

===================================
Receive signing-completion webhooks
===================================

LibreSign can notify an external system when a document signing request or an
envelope has finished. The notification uses Nextcloud's **Webhook Listeners**
app, so the receiving application can keep its own interface and authentication.

.. note::

   This event is available in LibreSign 16 for Nextcloud 36 (the ``main``
   documentation line). It is not yet available in earlier LibreSign releases.

Configure the webhook
---------------------

1. Enable **Webhook Listeners** on the Nextcloud server. An administrator can
   also run ``sudo -u www-data php occ app:enable webhook_listeners`` from the
   Nextcloud installation directory.
2. Prepare a reachable HTTPS endpoint in the integrating system. Require
   receiver-side authentication and accept JSON ``POST`` requests.
3. Register a Nextcloud webhook using an account authorized to administer
   Webhook Listeners. Set the following fields:

   - **Event**: ``OCA\Libresign\Events\SigningRequestCompletedEvent``
   - **HTTP method**: ``POST``
   - **URI**: the HTTPS address of your receiver
   - **User filter**: empty, to allow background and external signing flows
   - **Event filter**: empty to receive every completed request
   - **Headers/authentication**: configure an authentication header accepted
     by your receiver; do not put secrets in the URI

   The endpoint for registration is
   ``POST /ocs/v2.php/apps/webhook_listeners/api/v1/webhooks``.
   Consult your Nextcloud version's Webhook Listeners administration API
   for the supported registration fields.
4. Ensure Nextcloud background jobs run with the recommended **Cron** mode.
   The Nextcloud server must be able to reach the receiver.

What is sent
------------

Nextcloud sends a JSON body similar to the following:

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

The ``requestType`` is either ``document`` or ``envelope``. The
``requestUuid`` identifies the complete signing request in LibreSign, **not**
one signer's individual invitation. The ``eventId`` remains the same for
repeat notifications about that request; store it to prevent duplicate work.

The notification means the **workflow** reached LibreSign's signed status.
An individual signature or a partially signed request does not trigger
this event. Depending on the signing workflow, a completed request can include
participants who rejected; do not interpret completion as proof that every
invited person signed.

Nextcloud may add its own metadata to the delivery envelope, including
the triggering user when one is available. The LibreSign event does not carry
a document, a file-download link, signer contact information or credentials.
Use the authenticated LibreSign API and the integrator's normal permissions
to retrieve documents or evidence.

Reliability and migration
-------------------------

- Deliveries are performed by Nextcloud background jobs, not in the response
  to a signing request. Configure the receiver to respond with a ``2xx``
  status and process messages idempotently.
- Do not assume a guaranteed delivery time, ordering, or automatic retry of
  unsuccessful HTTP calls. Check Nextcloud logs and reconcile missed events
  through the authenticated LibreSign API.
- The existing LibreSign callback remains available. If both callbacks and
  native webhooks are configured, the external system may receive notifications
  through both mechanisms.
