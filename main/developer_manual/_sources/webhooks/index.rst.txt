.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

========
Webhooks
========

Webhooks allow an external system to react to LibreSign events without
replacing its own interface or repeatedly querying LibreSign. Native event
delivery is provided by Nextcloud's **Webhook Listeners** app. The
:doc:`event-catalog` describes supported classes, their triggers and
payload fields.

Webhook Listeners delivers JSON event metadata to a receiver configured in
Nextcloud. Retrieve signed PDFs separately with authorized credentials.

.. toctree::
   :maxdepth: 1

   event-catalog
   configuration
   signing_completion
   external-signing-flow
