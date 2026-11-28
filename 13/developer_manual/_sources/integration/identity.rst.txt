.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

.. _integration-identity:

Account integration and authentication choices
===============================================

Distinguish **the person your product has authenticated** from **the
Nextcloud principal authorized to call LibreSign**. Sharing an identity
provider can unify user login, but does not make an arbitrary product session
a valid OCS authentication token.

.. list-table:: Authentication and identity matrix
   :header-rows: 1
   :widths: 18 23 20 22 17

   * - Mechanism
     - Use when
     - Advantage
     - Limit / risk
     - Setup
   * - Nextcloud account and browser session
     - User works interactively within Nextcloud
     - Native account permission checks
     - Not a token for headless server automation
     - Login, allowed account and signing method
   * - App Password with Basic Auth
     - Trusted product backend calls OCS for a dedicated account
     - Revocable per-client credential; simple integration
     - Acts with that account's permissions; cannot represent another signer
     - Account, credential vault, TLS, rotation
   * - Nextcloud Login Flow
     - Product connects an existing Nextcloud user's account
     - User authorizes a revocable client credential
     - Requires interactive initial connection and secure token storage
     - Nextcloud login flow and app-password lifecycle
   * - Nextcloud OAuth2
     - User-delegated API authorization is required
     - Standard bearer-token integration
     - Nextcloud OAuth2 tokens are not scoped to LibreSign alone
     - Registered client, grant flow, secure token storage
   * - OIDC bearer authentication
     - Instance validates provider-issued ID/access tokens for OCS
     - Reuses an organization's identity provider
     - Login SSO alone does not enable API bearer validation
     - Compatible ``user_oidc`` / provider configuration and mapping
   * - SSO for browser login
     - Users open Nextcloud with an existing IdP session
     - Simplified interactive experience
     - Not a service credential or permission bypass
     - SSO backend, stable user IDs, Nextcloud session
   * - External email signer
     - Person must sign without a Nextcloud account
     - Avoids account provisioning
     - Not general API access; token/link exposure matters
     - Email identification, selected signing verification

Security boundaries
-------------------

**Backend-to-backend operations**
   Use a dedicated, least-privileged Nextcloud account with an App Password,
   or a configured OAuth2/OIDC bearer flow supported by that instance. OAuth2
   client tokens and an OIDC IdP's tokens are **not interchangeable**; validate
   the exact token with the deployed Nextcloud API.
   Store credentials server-side. Test the effective permissions using the
   exact account; LibreSign request creation is restricted to authenticated
   users permitted to request signatures.

**Per-user operations**
   When a real Nextcloud account signer must act, use **their** Nextcloud
   authorization context. A service account's access to request metadata is
   not permission to impersonate a signer.

**External signers**
   Do not create Nextcloud accounts solely to satisfy the API client.
   Configure LibreSign's external signer method and verification flow.
   Possession of a valid signer invitation does not grant listing or download
   rights across an account's storage.

**User directory vs authentication**
   LDAP, OIDC provisioning, and SSO can create or map Nextcloud users; this is
   separate from OAuth2 grants, App Passwords, and the LibreSign email signer
   option. Keep immutable user identifiers and lifecycle/deprovisioning
   behavior consistent across systems.

Authenticated OCS request (read-only)
-------------------------------------

The following example uses a revocable App Password; it does not create or
sign any document:

.. code-block:: bash

   export NC_URL="https://cloud.example.com"
   export NC_USER="integration-account"
   export NC_APP_PASSWORD="<retrieve-from-secret-manager>"

   curl --fail-with-body -sS \
     -u "$NC_USER:$NC_APP_PASSWORD" \
     -H "OCS-APIRequest: true" \
     -H "Accept: application/json" \
     "$NC_URL/ocs/v2.php/apps/libresign/api/v1/file/list?details=1"

Verify ``ocs.meta`` and ``ocs.data``, and expect only records visible to
this account. Do not use a normal user's password as an integration secret.

Nextcloud references
--------------------

- `Login Flow <https://docs.nextcloud.com/server/stable/developer_manual/client_apis/LoginFlow/index.html>`_
  (revocable client credentials).
- `OAuth2 <https://docs.nextcloud.com/server/stable/admin_manual/configuration_server/oauth2.html>`_
  (notably: no scoped access in Nextcloud's OAuth2 implementation).
- `OpenID Connect user authentication and bearer validation <https://docs.nextcloud.com/server/stable/admin_manual/configuration_user/user_auth_oidc.html>`_.
- `OCS authentication <https://docs.nextcloud.com/server/stable/developer_manual/client_apis/OCS/ocs-api-overview.html>`_.

See :doc:`../api/external-email-signers` for the actual requester-to-external-
signer workflow, including the permissions required for invitation, validation
and PDF recovery. The example's ``LIBRESIGN_DOC_LINE`` fixture selection
prevents payloads from one release being silently used in another.

Inspect :doc:`../api/openapi` to confirm each LibreSign operation's security
requirements for this particular application release. Avoid database writes
or direct database reads as a substitute for authentication contracts.
