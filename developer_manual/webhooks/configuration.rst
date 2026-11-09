.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

============================
Configure webhook deliveries
============================

Native LibreSign webhooks use Nextcloud's **Webhook Listeners** application.
A Nextcloud administrator registers a receiving HTTPS endpoint and selects
which event class should trigger it. A separate receiver application can keep
its own authentication and user interface.

Prerequisites
-------------

- LibreSign must include the event you want to subscribe to. See the event
  reference pages for availability and payloads.
- Enable **Webhook Listeners** in Nextcloud. On an installation where the
  web-server account is ``www-data``, an administrator can run:

  .. code-block:: console

     sudo -u www-data php occ app:enable webhook_listeners

- Configure Nextcloud background jobs in **Cron** mode and allow the server to
  reach the receiver over HTTPS.
- Provide a receiver that accepts JSON requests, authenticates the sender,
  and can process duplicate messages safely.

Register a listener
-------------------

Use Nextcloud's Webhook Listeners administration API, not LibreSign's signing
API, to create the subscription:

.. code-block:: text

   POST /ocs/v2.php/apps/webhook_listeners/api/v1/webhooks

Authenticate as an administrator authorized to manage Webhook Listeners, using
an App Password where supported and the ``OCS-APIRequest: true`` header.
The registration fields include:

- ``httpMethod``: use ``POST``.
- ``uri``: HTTPS URL of the receiver; do not include credentials in the URL.
- ``event``: the fully qualified event name shown on its reference page.
- ``eventFilter``: omit or use an empty filter to accept every occurrence, or
  define a filter supported by your Nextcloud version.
- ``userIdFilter``: leave unset for events initiated by external signers or
  background jobs, where no Nextcloud user may be in the current session.
- ``headers``, ``authMethod`` and ``authData``: configure the authentication
  mechanism supported by your installed Webhook Listeners version. Use a
  dedicated receiver credential and keep it outside source control.

For the complete request schema, permission rules and available authentication
modes, consult your installed Nextcloud Webhook Listeners API documentation.
Each release of Nextcloud controls these administrative fields independently.

Delivery and recovery
---------------------

Webhook Listeners schedules HTTP delivery through Nextcloud background jobs.
A successful signing operation does not mean the HTTP request has already
reached the receiver. Return a ``2xx`` response when an event is accepted and
store an event-specific idempotency key when the event provides one.

Do not assume exactly-once delivery, guaranteed ordering or automatic retry
of failed HTTP requests. Inspect the Nextcloud log and the receiver log when
notifications are missing. Reconcile the current workflow using authenticated
LibreSign API operations and the permissions of the integrating account.
Never use a webhook payload as authorization to download a signed file.

Event availability
------------------

Event pages describe the version and precise workflow condition for each
subscription. Do not assume that an event documented for the development
line exists on an older installed LibreSign version.
