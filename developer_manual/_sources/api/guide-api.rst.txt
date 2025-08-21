API Usage
=========

LibreSign exposes endpoints via **REST** and **OCS (Open Collaboration Services)**.

By default, all requests require authentication (Basic Auth, App Password, OIDC, or session cookies) and return JSON responses.

Base URLs
---------

- **OCS**: ``https://cloud.example.com/ocs/v2.php/apps/libresign/api/v1/``

**Versioning**: breaking changes result in a new major version (e.g., ``v2``).

Authentication
--------------

Supported methods:

- **Basic Auth** (App Password or Username/Password)
- **OIDC Access Token** (``Authorization: Bearer <ACCESS_TOKEN>``)
- **Session cookies** (for non-OCS endpoints, may require CSRF token)

.. note::
   Prefer using an **App Password** for Basic Auth. For OIDC, use **Access Tokens**.

.. note::
    Use an application password instead of your regular password.  
    Besides improved security, this also improves performance.  

    To configure one:

    - log into the Nextcloud Web interface
    - click on your avatar,  
    - select *Personal settings*, then *Security*.
    - At the bottom of the page you can create an app password, which can also be revoked later without changing your main password.

Basic Auth (App Password)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    curl -sS -u "username:app-password" \
      -H "Accept: application/json" \
      -H "OCS-APIRequest: true" \
      "https://cloud.example.com/ocs/v2.php/apps/libresign/api/v1/..."

OIDC (Access Token)
~~~~~~~~~~~~~~~~~~~

`Read more <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization/>`__

.. code-block:: bash

    curl -sS \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Accept: application/json" \
      -H "OCS-APIRequest: true" \
      "https://cloud.example.com/ocs/v2.php/apps/libresign/api/v1/..."

Clients
-------

- Requests with a body (:code:`POST`, :code:`PUT`, :code:`PATCH`) must include ``Content-Type: application/json``.

CURL
~~~~

All OCS requests can be tested with :code:`curl` by specifying the request method (:code:`GET`, :code:`POST`, :code:`PATCH`, etc.) and the required headers.

Example:

.. code-block:: bash

    curl --request POST \
        --url http://cloud.example.com/apps/libresign/api/v1/request-signature \
        --header 'Authorization: Basic <base64-credentials>' \
        --header 'Content-Type: application/json' \
        --data '{
            "file": {
                "url": "https://example.com/test.pdf"
            },
            "status": 0,
            "name": "Contract",
            "users": [
                {
                    "email": "a@b.c"
                    "displayName": "User Name"
                }
            ]
        }'
