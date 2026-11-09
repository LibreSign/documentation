.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

========
Webhooks
========

Webhooks allow an external system to react to LibreSign events without
replacing its own interface or repeatedly querying LibreSign. Native event
delivery is provided by Nextcloud's **Webhook Listeners** app. Each supported
event has its own reference page, including the point in the workflow that
triggers delivery and the data sent to the receiver.

**Availability:** LibreSign 16 with Nextcloud 36. These native LibreSign
events are **not available in LibreSign 13, 14 or 15**. The exact application
release and source revision are shown in :doc:`../api/openapi`. Nextcloud's
Webhook Listeners app must be enabled and the installed LibreSign release must
include the relevant event.

Native webhooks and the existing LibreSign per-request callback are separate
mechanisms. An integration may receive notifications through both transports.

.. toctree::
   :maxdepth: 1

   configuration
   signing_completion

The existing LibreSign callback continues to work independently. When an
integration enables both mechanisms, it must handle notifications from each
without assuming they have identical delivery formats or timing.
