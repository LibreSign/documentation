API Usage
=========

LibreSign exposes endpoints via **REST** and **`OCS (Open Collaboration Services) <https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/index.html>`__**.
This guide focuses on integration flows, with minimal requests and payloads.

Overview
--------

LibreSign APIs are designed for end-to-end signing integrations: request signatures, track signing status, validate signed documents, and integrate signing into external systems.

- **OCS base URL**: ``https://cloud.example.com/ocs/v2.php/apps/libresign/api/v1``
- **Response format**: JSON in OCS envelope (``ocs.meta`` and ``ocs.data``)
- **Versioning**: breaking changes result in a new major version (validate critical flows during upgrades)

Why OCS?
~~~~~~~~

LibreSign runs inside Nextcloud and uses OCS to keep integration behavior consistent with the ecosystem:

- Standard auth behavior (Basic/App Password, Bearer token, session)
- Standard response envelope (``ocs.meta`` + ``ocs.data``)
- Same authentication and permission checks used by other Nextcloud OCS APIs

Guide scope vs reference
~~~~~~~~~~~~~~~~~~~~~~~~

This page is an integration guide (workflow-first).
For exhaustive endpoint schemas and all fields, use :doc:`openapi`.

Core Concepts
-------------

Use this model when designing your integration:

::

    File
    |-- Signers
    |   `-- Sign Request UUID
    |-- Elements
    `-- Status

- **File**: document in the signature workflow (has ``file UUID``).
- **Signer**: actor that signs. Can be an account signer or an external signer.
- **Sign request UUID**: signer-scoped UUID used in ``POST /sign/uuid/{uuid}``.
- **File UUID**: file-scoped UUID used for file-level operations (for example validate endpoints).
- **Elements**: visible signature elements associated with sign requests.
- **Signature workflow**: one file, one or more signers, independent signer sessions.

Account signer vs external signer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Account signer**: identified by Nextcloud account (``method: account``).
- **External signer**: identified by email/other method depending on instance settings.

Why file UUID and sign request UUID are different
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The **file UUID** identifies the shared document workflow.
- The **sign request UUID** identifies one signer session in that workflow.
- Multiple signers interact with the same file independently, each using their own sign request UUID.
- **Terminology**: this guide uses **signature request workflow** for document-level flow and **sign request UUID** for signer-level signing session.

Status lifecycle
----------------

+--------+------------------+----------+
| Status | Meaning          | Terminal |
+========+==================+==========+
| 0      | Draft            | No       |
+--------+------------------+----------+
| 1      | Able to sign     | No       |
+--------+------------------+----------+
| 2      | Partially signed | No       |
+--------+------------------+----------+
| 3      | Signed           | Yes      |
+--------+------------------+----------+
| 4      | Deleted          | Yes      |
+--------+------------------+----------+

Transitions in practice:

- Create signature request: ``0`` or ``1`` (depends on request/config)
- First signer signs: often ``1 -> 2``
- Last required signer signs: ``2 -> 3`` (final signed state)
- Deletion: ``* -> 4`` (terminal for active workflow)

.. note::
    Final states are ``3`` (signed) and ``4`` (deleted).

Quick Start (Account-based signing)
-----------------------------------

Goal: create a sign request, include account signers, sign, and fetch final signed file metadata.

Minimal complete integration flow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create signature request
2. Retrieve signer UUIDs
3. Sign document
4. Track workflow status
5. Fetch signed document metadata

Prerequisites:

- LibreSign enabled in Nextcloud
- Authentication with a user allowed to request signatures
- Account identify method enabled in LibreSign settings
- Signature method available to account signers (for the minimal flow below, ``clickToSign``)

Integration constraints
-----------------------

Server settings that affect behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **File size limits**: controlled by Nextcloud/server limits (for example upload-related configuration).
- **Instance behavior**: identify methods, signature methods, and some transitions depend on Nextcloud/LibreSign admin settings.

API-level constraints
~~~~~~~~~~~~~~~~~~~~~

- **Authentication**: required by default for most operations.
- **Upload input**: request accepts file references such as ``url``, ``nodeId``, ``path``, or ``base64`` according to endpoint contract.
- **Workflow expectations**: create request first, then sign using signer-scoped sign request UUIDs.
- **Signing behavior**: sign operations are signer-session based, not file-UUID based.

Pagination note
~~~~~~~~~~~~~~~

- Large integrations should implement pagination when listing workflows.
- Pagination behavior depends on endpoint implementation and server configuration.
- Do not assume unbounded result sets.

Retry behavior
~~~~~~~~~~~~~~

- ``POST`` operations may not be idempotent.
- Avoid blind retries after unknown outcomes.
- Retry mainly after transport/network failures.
- Before retrying, verify current workflow state (for example with ``GET /file/list?details=1``).

Authentication
--------------

Supported methods:

- **Basic Auth** (App Password or Username/Password)
- **OIDC Access Token** (``Authorization: Bearer <ACCESS_TOKEN>``)
- **Session cookies** (for non-OCS endpoints, may require CSRF token)

OIDC considerations:

- OIDC support depends on Nextcloud instance configuration.
- Identity providers may vary across deployments.
- Validate provider configuration and token requirements with instance administrators.

.. note::
    Prefer using an **App Password** for Basic Auth (and **Access Tokens** for OIDC).
    App Password is safer than your regular password and usually performs better.

    To create an App Password in Nextcloud:

    - Log in to the Nextcloud web interface.
    - Click your avatar.
    - Open **Personal settings** > **Security**.
    - At the bottom of the page, create an app password.
    - You can revoke it later without changing your main password.

Request conventions
-------------------

- Include header ``OCS-APIRequest: true`` in all OCS calls
- For requests with body, include ``Content-Type: application/json``

Reusable shell variables
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

        export BASE_URL="https://cloud.example.com"
        export API_BASE="$BASE_URL/ocs/v2.php/apps/libresign/api/v1"
        export AUTH="username:app-password"

Guide: Account-based signing workflow
-------------------------------------

Sequence diagram
~~~~~~~~~~~~~~~~

::

    Client App
        |
        | POST /request-signature
        v
    LibreSign
        |
        | returns file UUID + file id
        v
    Client App
        |
        | GET /file/list?details=1
        | (extract signer sign request UUIDs)
        v
    Signer account
        |
        | POST /sign/uuid/{sign_request_uuid}
        v
    LibreSign
        |
        | file status -> signed
        v
    Client App
        |
        | GET /file/list?details=1&status[]=3
        v
    Signed workflow detected

1. Create signature request with minimal payload
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Intent: create one file workflow and attach signers.

.. code-block:: bash

        curl -sS -u "$AUTH" \
            -H "Accept: application/json" \
            -H "Content-Type: application/json" \
            -H "OCS-APIRequest: true" \
            -X POST "$API_BASE/request-signature" \
            -d '{
                "name": "Contract A",
                "file": { "url": "https://example.com/contract-a.pdf" },
                "signers": [
                    {
                        "identifyMethods": [
                            { "method": "account", "value": "signer1", "mandatory": 1 }
                        ]
                    },
                    {
                        "identifyMethods": [
                            { "method": "account", "value": "signer2", "mandatory": 1 }
                        ]
                    }
                ]
            }'

Minimal response example:

.. code-block:: json

        {
            "ocs": {
                "meta": {
                    "status": "ok",
                    "statuscode": 200,
                    "message": "OK"
                },
                "data": {
                    "id": 123,
                    "uuid": "f3f5c9d4-6f4e-4d0a-a8ce-7db35a5f9d27",
                    "status": 1,
                    "statusText": "able to sign"
                }
            }
        }

Important fields from response:

- ``ocs.data.id`` (LibreSign file id)
- ``ocs.data.uuid`` (file UUID)

2. Get signer UUIDs for each account signer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Intent: retrieve signer-specific sessions used by the sign endpoint.

Headless integration (no LibreSign UI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your product does not expose LibreSign pages, keep the flow fully API-driven:

1. Your backend creates the signature request.
2. Your backend calls ``GET /file/list?details=1`` using the authenticated context of the signer.
    Do not call this step only as the requester, because signer session and authorization context may not match the signer action.
3. Your backend maps each business signer to ``sign_request_uuid``.
4. Your backend calls ``POST /sign/uuid/{sign_request_uuid}`` in the same signer context.

In this model, the signer UUID retrieval is mandatory and intentional: it is the signer session identifier required by the sign endpoint.

Why this is required:

- ``POST /sign/uuid/{uuid}`` expects a **sign request UUID**, not a file UUID.
- Each signer has an independent signing session on the same file workflow.
- This separation allows multiple signers to progress independently while sharing one file lifecycle.

.. code-block:: bash

        curl -sS -u "$AUTH" \
            -H "Accept: application/json" \
            -H "OCS-APIRequest: true" \
            "$API_BASE/file/list?details=1"

Minimal response example:

.. code-block:: json

        {
            "ocs": {
                "meta": {
                    "status": "ok",
                    "statuscode": 200,
                    "message": "OK"
                },
                "data": {
                    "data": [
                        {
                            "id": 123,
                            "uuid": "f3f5c9d4-6f4e-4d0a-a8ce-7db35a5f9d27",
                            "status": 1,
                            "signers": [
                                {
                                    "sign_request_uuid": "6e8e3c9f-0ef7-4f24-a9d3-4f5f0a45a3fd"
                                },
                                {
                                    "sign_request_uuid": "e1f3e2c6-c8f2-4fae-9969-d6f8f2f6e6fd"
                                }
                            ]
                        }
                    ]
                }
            }
        }

Pick values from:

- ``ocs.data.data[0].signers[*].sign_request_uuid``

3. Sign as each signer account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Intent: complete signer actions using signer-scoped UUIDs.

.. code-block:: bash

        export SIGNER1_AUTH="signer1:app-password"
        export SIGN_REQUEST_UUID_1="<from-step-2>"

        curl -sS -u "$SIGNER1_AUTH" \
            -H "Accept: application/json" \
            -H "Content-Type: application/json" \
            -H "OCS-APIRequest: true" \
            -X POST "$API_BASE/sign/uuid/$SIGN_REQUEST_UUID_1" \
            -d '{ "method": "clickToSign" }'

Minimal response example:

.. code-block:: json

        {
            "ocs": {
                "meta": {
                    "status": "ok",
                    "statuscode": 200,
                    "message": "OK"
                },
                "data": {
                    "action": 0,
                    "message": "Signed with success"
                }
            }
        }

Repeat for each signer account.

4. Check when file is fully signed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Intent: detect completed workflows.

.. code-block:: bash

        # status[]=3 means signed documents
        curl -sS -u "$AUTH" \
            -H "Accept: application/json" \
            -H "OCS-APIRequest: true" \
            "$API_BASE/file/list?details=1&status[]=3"

Useful response fields:

- ``ocs.data.data[*].status`` and ``ocs.data.data[*].statusText``
- ``ocs.data.data[*].file.url``
- ``ocs.data.data[*].file.signedNodeId``

Tracking strategy note:

- Polling is acceptable for simple integrations.
- Webhook-based tracking is usually preferable in production environments.
- Webhook-focused documentation can be added as a dedicated guide.

Guide: Multi-signer workflow
----------------------------

Sequence diagram
~~~~~~~~~~~~~~~~

::

    Client App
        |
        | POST /request-signature (signer1, signer2, ...)
        v
    LibreSign
        |
        | one file UUID + multiple sign request UUIDs
        v
    Signer1 -> POST /sign/uuid/{uuid1}
    Signer2 -> POST /sign/uuid/{uuid2}
    ...
        |
        v
    LibreSign status: 1 -> 2 -> 3

Each signer uses a different sign request UUID, but all signers update the same file workflow.

Guide: Notification workflow
----------------------------

Sequence diagram
~~~~~~~~~~~~~~~~

::

    Client App
        |
        | POST /notify/signers
        v
    LibreSign
        |
        | dispatches signer notifications
        v
    Signers receive message/channel delivery

5. Notify signers (optional API-triggered distribution)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to explicitly trigger notifications after signing, call:

.. code-block:: bash

        curl -sS -u "$AUTH" \
            -H "Accept: application/json" \
            -H "Content-Type: application/json" \
            -H "OCS-APIRequest: true" \
            -X POST "$API_BASE/notify/signers" \
            -d '{
                "fileId": 123,
                "signers": [
                    { "email": "signer1@domain.test" },
                    { "email": "signer2@domain.test" }
                ]
            }'

.. note::
     This endpoint requires ``fileId`` and signer emails. Use it when you want an explicit notification trigger.

Endpoints used in this guide
----------------------------

- ``POST /request-signature``
- ``GET /file/list?details=1``
- ``POST /sign/uuid/{uuid}``
- ``GET /file/list?details=1&status[]=3``
- ``POST /notify/signers`` (optional)

Alternative account-related endpoints
-------------------------------------

- ``GET /identify-account/search?search=<term>``: search valid account identifiers
- ``GET /account/me``: retrieve authenticated account data
- ``POST /account/signature``: create signer certificate (for password/certificate flows)

Common errors
-------------

``401 Unauthorized``
    Cause: invalid credentials, missing/invalid app password, or unauthenticated request.
    Quick fix: verify auth method and credentials; prefer app password for Basic Auth.

``412 Precondition Failed``
    Cause: missing ``OCS-APIRequest: true`` header in OCS requests.
    Quick fix: always include the header for OCS endpoints.

``400 Bad Request``
    Cause: invalid JSON/payload, missing identify method data, wrong field names.
    Quick fix: send minimal valid payload and validate required fields from OpenAPI.

``404 Not Found``
    Cause: invalid or expired sign request UUID in ``/sign/uuid/{uuid}``.
    Quick fix: refresh signer UUID from ``GET /file/list?details=1`` and retry.

Security considerations
-----------------------

- Prefer app passwords over account passwords for API integrations.
- Use HTTPS only.
- Do not expose sign request UUIDs in public channels.
- Rotate credentials periodically.
- Use least-privilege API accounts/roles when possible.

Related docs
------------

- See OpenAPI explorer in :doc:`openapi` for full schema and all endpoints.
- Behat integration reference (real implementation flows):

    - Account-based signing request (real scenario): `sign/request.feature#L242 <https://github.com/LibreSign/libresign/blob/main/tests/integration/features/sign/request.feature#L242>`__
    - Validation after account-based signing (real scenario): `file/validate.feature#L2 <https://github.com/LibreSign/libresign/blob/main/tests/integration/features/file/validate.feature#L2>`__
    - Multi-signer parallel signing (real scenario): `sign/sequential_signing.feature#L13 <https://github.com/LibreSign/libresign/blob/main/tests/integration/features/sign/sequential_signing.feature#L13>`__
