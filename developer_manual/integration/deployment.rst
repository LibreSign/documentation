.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

.. _integration-deployment:

Infrastructure, administration and policy preflight
===================================================

Treat installation, signing permissions, identity, transport and cryptographic
policy as separate checks. A working Nextcloud login is not evidence that the
LibreSign signer workflow can complete.

.. list-table:: Deployment and integration prerequisites
   :header-rows: 1
   :widths: 18 15 42 25

   * - Item
     - Classification
     - Required condition
     - Failure mode
   * - Version compatibility
     - Required
     - Nextcloud release supported by this LibreSign line; deployed OpenAPI matches the running app
     - Invalid routes or request shapes
   * - LibreSign enablement and signing backend
     - Required
     - Enabled app and functional certificate/signing engine under the chosen policy
     - Requests cannot be completed as signed PDFs
   * - HTTPS and trusted public instance URL
     - Required for production
     - TLS, correct reverse-proxy configuration and reachable invitation links
     - Credentials or signer tokens exposed; broken links
   * - Requester account and permissions
     - Required for OCS creation
     - Authenticated Nextcloud principal allowed to request signatures; readable source and output location
     - 401/403/422; inaccessible results
   * - Signer identification and signature methods
     - Required per use case
     - Enabled account and/or email identification; compatible verification and signing method
     - Signer cannot verify identity or complete action
   * - Notification transport
     - Conditional
     - Mail or configured gateway if LibreSign delivers invitations; otherwise verified integrator delivery
     - Lost invites and retries
   * - Background processing
     - Operational requirement
     - Nextcloud scheduled jobs and any configured LibreSign delivery workers function reliably
     - Delayed reminders, retry or recovery
   * - OAuth2, OIDC and SSO
     - Optional
     - Configure only if selected for that identity design
     - Tokens accepted by IdP but rejected by Nextcloud
   * - Native Webhook Listeners
     - Optional, version-gated
     - LibreSign 16/Nextcloud 36 completion event where installed; verify the receiver and worker HTTP delivery
     - Missing, ambiguous or duplicate events
   * - TSA, CRL, additional trust anchors
     - Conditional
     - Configure when required by legal/certificate policy; verify endpoint access and retention
     - Incomplete timestamp or revocation evidence

Administrative questions to settle first
----------------------------------------

- Which Nextcloud user can initiate a request? Which groups or policies limit
  this privilege? Can that same identity read the final signed node?
- Which identification methods (account, email) and signature methods are
  enabled? Are external invitations allowed under this instance's policies?
- Is the signer sequence parallel or ordered? Is the request one file or an
  envelope? Who decides that the complete business operation has succeeded?
- Who sends invitations, reminders and errors? What happens if delivery is
  accepted but not received? Where are retries and deduplication recorded?
- Which certificate/signing engine and validation trust chain are configured?
  Are timestamping and revocation requirements mandatory for this use case?
- What is the retention and download authorization policy for signed PDFs and
  available validation/evidence artifacts?

Production smoke checks
-----------------------

1. Confirm the actual app release and Nextcloud compatibility before copying
   requests from :doc:`../api/openapi`. Pay particular attention to
   ``NewSigner.identifyMethods`` field differences across release lines.
2. Verify an authenticated requester can list **only its own authorized**
   workflows, then create a test request with the correct policy and input.
3. Exercise the actual account or external signer identity challenge.
   Confirm that a different signer cannot reuse another signer's permission.
4. Test pending, partial, signed, rejected/deleted and unknown results;
   check envelope children independently. A completed request may include
   a permitted rejection; inspect signer evidence and business requirements.
5. Verify the final signed PDF can be fetched by an authorized account
   and **cannot** be fetched by an unauthorized one. Preserve audit metadata
   only to the extent exposed by the installed contract.
6. Test transport interruption, duplicate polling results, invitation
   expiry and notification-delivery failures without automatic double sends.

Nextcloud's `background-job guidance <https://docs.nextcloud.com/server/stable/admin_manual/configuration_server/background_jobs_configuration.html>`_
recommends scheduled cron execution for reliable server work.
For runnable signed-document retrieval and email-signing prerequisites, see
:doc:`../api/external-email-signers`. Confirm exact request structures in
:doc:`../api/openapi` and the installed server policies. Optional commercial
support and external notification gateways are distinct from LibreSign's
free software and its core signing functionality.

Direct database access, hidden Nextcloud permissions and unverified webhook
event names are **not** supported integration shortcuts.
