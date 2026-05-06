API Usage
=========

LibreSign exposes endpoints via **REST** and **`OCS (Open Collaboration Services) <https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/index.html>`__**.
This guide focuses on integration journeys, with minimal requests and payloads.

Overview
--------

- **OCS base URL**: ``https://cloud.example.com/ocs/v2.php/apps/libresign/api/v1``
- **Response format**: JSON in OCS envelope (``ocs.meta`` and ``ocs.data``)
- **Versioning**: breaking changes result in a new major version

Quick Start (Account flow)
--------------------------

Goal: create a sign request, include account signers, sign, and fetch final signed file metadata.

Prerequisites:

- LibreSign enabled in Nextcloud
- Authentication with a user allowed to request signatures
- Account identify method enabled in LibreSign settings
- Signature method available to account signers (for the minimal flow below, ``clickToSign``)

Authentication
--------------

Supported methods:

- **Basic Auth** (App Password or Username/Password)
- **OIDC Access Token** (``Authorization: Bearer <ACCESS_TOKEN>``)
- **Session cookies** (for non-OCS endpoints, may require CSRF token)

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

Workflow: Create, add signers, sign, distribute (Account)
----------------------------------------------------------

1. Create signature request with minimal payload
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This call creates the file workflow and inserts signers.

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

Important fields from response:

- ``ocs.data.id`` (LibreSign file id)
- ``ocs.data.uuid`` (file UUID)

2. Get signer UUIDs for each account signer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each signer signs using its own sign request UUID (not the file UUID).

.. code-block:: bash

        curl -sS -u "$AUTH" \
            -H "Accept: application/json" \
            -H "OCS-APIRequest: true" \
            "$API_BASE/file/list?details=1"

Pick values from:

- ``ocs.data.data[0].signers[*].sign_request_uuid``

3. Sign as each signer account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Authenticate as each signer and call sign endpoint with minimal payload.

.. code-block:: bash

        export SIGNER1_AUTH="signer1:app-password"
        export SIGN_REQUEST_UUID_1="<from-step-2>"

        curl -sS -u "$SIGNER1_AUTH" \
            -H "Accept: application/json" \
            -H "Content-Type: application/json" \
            -H "OCS-APIRequest: true" \
            -X POST "$API_BASE/sign/uuid/$SIGN_REQUEST_UUID_1" \
            -d '{ "method": "clickToSign" }'

Repeat for each signer account.

4. Check when file is fully signed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query files with signed status (``status[]=3``).

.. code-block:: bash

        curl -sS -u "$AUTH" \
            -H "Accept: application/json" \
            -H "OCS-APIRequest: true" \
            "$API_BASE/file/list?details=1&status[]=3"

Useful response fields:

- ``ocs.data.data[*].status`` and ``ocs.data.data[*].statusText``
- ``ocs.data.data[*].file.url``
- ``ocs.data.data[*].file.signedNodeId``

5. Notify participants (optional API-triggered distribution)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Reference: endpoints used in this flow
--------------------------------------

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

Related docs
------------

- See OpenAPI explorer in :doc:`openapi` for full schema and all endpoints.
