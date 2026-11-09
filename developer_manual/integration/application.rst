.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

.. _integration-application:

Integrate an existing application without replacing its UI
===========================================================

Keep your application's login, navigation, business record IDs, and document
management interface. Let its **backend** act as the authenticated OCS client;
do not expose its Nextcloud credentials to a browser or signer.

Typical control and signer paths
--------------------------------

.. code-block:: text

   Existing application UI --> Application backend --> Nextcloud OCS / LibreSign
        |                         |                        |
        |                         +-- map business ID <----+-- file UUID / file ID
        |                         +-- reconcile status <---+-- file/list
        |
        +-- account signer ------> Nextcloud-authenticated signing session
        |
        +-- external signer -----> verified LibreSign invitation (no NC account)
                                     |
                                     +--> signer-scoped signing action

The requesting principal creates the workflow, then reads **only** data it
is authorized to access. Each signer acts through their own authorized session
or external-signing challenge. Do not let a backend service account sign
`on behalf of` a person merely because it can create requests.

Choose the signer model
-----------------------

**Nextcloud account signer**
   Use the account identification method for an existing Nextcloud user.
   The user must be able to authenticate as that user and satisfy the chosen
   signing method and policy. SSO may simplify interactive login, but it does
   not make the product's session a Nextcloud API credential.

**External signer without a Nextcloud account**
   Use the enabled email identification and signature method, and let
   LibreSign enforce its invitation/token verification. A public signer can
   complete a permitted signing action without becoming an account holder.
   Public signing access must not be confused with authorization to list or
   download arbitrary Nextcloud files.

**Mixed workflow**
   Use distinct identification entries for each participant; preserve signer
   identity, ordering and document-level completion separately. An envelope
   contains child documents: examine the envelope **and** child file states
   before marking a business transaction completed. Do not infer full
   completion from the first signed child or signer.

API boundary and version differences
------------------------------------

The common OCS prefix is::

   https://cloud.example.com/ocs/v2.php/apps/libresign/api/v1

The requester uses ``POST /request-signature`` and tracks results with
``GET /file/list``. Both operations are present in the reviewed release
schemas. The ``/api/v1`` segment is the protocol version, **not** the LibreSign
major release number. The account and external
identification methods require instance-level configuration.

**The signer identification payload is not identical across releases.**
An ``identifyMethods`` element in LibreSign 13/14 uses ``mandatory``;
in LibreSign 15 and the development line it uses the ``requirement`` enum.
For example, these are **field fragments**, not full request bodies:

.. code-block:: json

   {"method": "email", "value": "signer@example.test", "mandatory": 1}

.. code-block:: json

   {"method": "email", "value": "signer@example.test", "requirement": "required"}

Use only the fragment described by your selected
:doc:`../api/openapi`, inside its ``NewSigner.identifyMethods`` schema.
Do not paste fragments from a newer release into an older integration. The
complete creation, invitation, polling and retrieval examples are maintained
in :doc:`../api/external-email-signers`, where the fixture must match this
release's pinned OpenAPI.

Never construct a signing link from a file UUID. The file UUID identifies a
workflow, while a sign-request UUID identifies an individual signing session.
Treat either identifier as sensitive workflow metadata, not as an authentication
credential to send indiscriminately.

Integration responsibilities
----------------------------

Your product should persist a mapping of its own record ID to LibreSign file
UUID / file ID, reconcile transitions (including cancellation and rejection),
enforce who may retrieve a completed PDF, and record local delivery attempts.
LibreSign enforces its own signer validation, signing policy, PDF creation and
authorization. Client-side checks in your product cannot replace these rules.

Use :doc:`lifecycle` for state reconciliation and notifications,
:doc:`identity` for authentication boundaries, and
:doc:`../api/external-email-signers` for runnable, release-specific examples.
