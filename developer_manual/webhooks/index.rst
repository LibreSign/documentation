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

**Documentation scope:** LibreSign |LibreSignRelease| on Nextcloud
|NextcloudRelease| (development line). The exact application revision is
available through the :doc:`../api/openapi` provenance information. Webhooks
configured in Nextcloud are not equivalent to LibreSign's existing per-request
callback.

.. note::

   Native signing-completion webhooks are planned for LibreSign 16 on Nextcloud
   36. They are **not available in LibreSign 13, 14 or 15**. This development
   documentation applies only to installations that include the new event.

.. toctree::
   :maxdepth: 1

   configuration
   signing_completion

The existing LibreSign callback continues to work independently. When an
integration enables both mechanisms, it must handle notifications from each
without assuming they have identical delivery formats or timing.
