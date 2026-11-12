.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

.. _integration-architecture:

Integration architecture: choose a pattern
==========================================

This section is for architects integrating LibreSign into an **existing**
application. LibreSign is free and open-source software; deploying it does not
require a commercial service. Optional hosting, support and third-party
delivery gateways are separate from the LibreSign API. Your application may
retain its UI, authentication and business workflow.

You are reading the guide for LibreSign |LibreSignRelease| on Nextcloud
|NextcloudRelease|. Concepts here apply to the available release line; **the
OpenAPI contract is version-specific**. Confirm each request shape in
:doc:`../api/openapi` before implementing it.

Start with your constraint
--------------------------

.. list-table:: Integration decision matrix
   :header-rows: 1
   :widths: 18 20 19 24 19

   * - Situation
     - Preferred approach
     - Benefit
     - Risk or limitation
     - Requirements
   * - Existing product must keep its UI and login
     - Product backend orchestrates LibreSign via authenticated OCS requests
     - No Nextcloud UI migration
     - Backend credentials are powerful; signer actions still need signer authority
     - Authorized Nextcloud principal; API and storage access
   * - Signers already have Nextcloud accounts
     - Account identification; use their own login/session or approved token
     - Reuses account identity and access policies
     - Product login alone is not proof of a Nextcloud signer session
     - Mapped account; enabled signing method
   * - Signer has no Nextcloud account
     - Email identification and LibreSign-controlled public signing invitation
     - No Nextcloud account provisioned for the signer
     - Invitation possession and email verification policies must be protected
     - Email method, approved verification flow, delivery
   * - Internal and external signers share a document
     - Mixed signer identification in one request or envelope
     - One auditable workflow with distinct signer identities
     - Different tokens, signing order and completion states
     - All selected identify methods and policies enabled
   * - Your product owns message delivery
     - Defer invitations with signer ``notify: 0``; trigger LibreSign notifications later or use a verified integrator delivery flow
     - Controlled delivery timing and branding
     - No generic invitation-link retrieval contract is proven; never derive a URL from a UUID
     - Permitted requester, validated delivery flow and secure secrets
   * - External service needs completion signals
     - Poll authorized OCS file status; use a native completion event only where this release publishes one
     - Reliable reconciliation, with optional lower-latency signals
     - Native events are version-gated and HTTP delivery needs deployment testing
     - Authorized status reader and, optionally, Nextcloud Webhook Listeners

Read the relevant guide
-----------------------

.. toctree::
   :maxdepth: 2

   application
   identity
   lifecycle
   deployment

- :doc:`application` — retain the product UI; choose account, external, or
  mixed signers; orchestrate without impersonation.
- :doc:`identity` — distinguish Nextcloud accounts, App Passwords, OAuth2,
  OIDC and SSO.
- :doc:`lifecycle` — notification ownership, state reconciliation, native
  webhook readiness and authorized document retrieval.
- :doc:`deployment` — infrastructure, permissions, certificates, policy
  decisions and go-live checks.
- :doc:`../api/external-email-signers` — version-specific, runnable email-signer
  integration with fixture selection and authorized PDF retrieval.
- :doc:`../api/openapi` — the **actual API schema for this release**, including
  required properties and supported responses.
- `n8n importable signing workflow <https://github.com/LibreSign/documentation/blob/a7b772cf579fcbd734810661f6e2104bd8444e6a/examples/n8n/README.md>`_ — one external email
  signer, App Password authentication, bounded OCS polling and automatic
  WebDAV discovery and authenticated download in the default LibreSign
  folder. The shared example selects the request schema for LibreSign
  13/14 (``mandatory``) or 15/development (``requirement``). The discovery
  step was exercised only on LibreSign 15.0.12; versions 13, 14 and
  development still require runtime verification. Native completion
  events are documented only for development; the workflow uses OCS polling.

Contract and ownership boundaries
---------------------------------

**Practical API integration is already documented** in
:doc:`../api/external-email-signers`, with examples and tests pinned to each
published LibreSign release. Use that guide for requests, mail invitations,
status polling, validation and authenticated WebDAV download.

**Native webhook support is release-dependent.** Consult :doc:`lifecycle`
for the event availability on this release and the release-specific Webhooks
manual where one exists. A compiled application event or passing unit test
alone does not prove successful outbound HTTP delivery.

No recommendation here requires direct database access, credential sharing
with a signer, or disabling Nextcloud authorization. Use supported OCS and
Nextcloud file APIs instead.

For details of Nextcloud's request transport, see the
`Nextcloud OCS API overview <https://docs.nextcloud.com/server/stable/developer_manual/client_apis/OCS/ocs-api-overview.html>`_.
