.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

============================
Configure webhook deliveries
============================

Native LibreSign webhooks use Nextcloud's **Webhook Listeners** application.
A Nextcloud administrator registers a receiving HTTPS endpoint and selects
which event class should trigger it. A separate receiver application can keep
its own authentication and user interface. The complete procedure, from
creating an external signing request to fetching its PDF, is in
:doc:`external-signing-flow`.

Prerequisites
-------------

Nextcloud documents ``occ`` subcommands independently of the operating
system and installation method. Execute them through the appropriate Nextcloud
administration CLI for your installation, rather than assuming ``sudo``, an
HTTP-user name or a container name. See Nextcloud's
`Using the occ command <https://docs.nextcloud.com/server/stable/admin_manual/occ_command.html>`_,
`Docker instructions <https://github.com/nextcloud/docker#accessing-the-nextcloud-command-line-interface-occ>`_
and `Snap instructions <https://github.com/nextcloud-snap/nextcloud-snap/wiki/OCC-management-console>`_.

- Choose an event class from :doc:`event-catalog`.
- Enable **Webhook Listeners** from the Nextcloud **Apps** administration page,
  or use the Nextcloud command:

  .. code-block:: console

     occ app:enable webhook_listeners

- Select **Cron** mode under Nextcloud background-job settings, or use:

  .. code-block:: console

     occ background:cron

  This only selects the execution mode; it **does not install a scheduler**.
  Configure an actual scheduler to run ``cron.php`` periodically (or use the
  equivalent provided by your installation) and verify jobs execute.
  Follow Nextcloud's
  `background-jobs configuration <https://docs.nextcloud.com/server/stable/admin_manual/configuration_server/background_jobs_configuration.html>`_.

- Allow the Nextcloud server to reach the receiver over HTTPS.
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
