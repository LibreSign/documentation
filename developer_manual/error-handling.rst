.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

Error handling
==============

Use these rules when changing PHP exceptions and related API/frontend
behavior. The application repository is the source of truth for actual throw
sites, catch blocks, and consumers.

Choose an exception
-------------------

- Prefer an existing PHP, Nextcloud OCP, or LibreSign exception when it already
  represents the condition.
- Use ``LibresignException`` for an expected LibreSign error converted to an
  API/frontend response. New public typed exceptions must extend it so
  existing catch paths continue to work.
- Introduce a typed subclass for a meaningful condition that callers need to
  distinguish. Do not create a class solely to replace a test assertion.
- Use a semantic code only when a client, frontend, or other caller needs a
  stable programmatic identifier. Define its constant near the producer.
- Never compare exception messages to decide application behavior. Messages
  can change or be translated.

Keep HTTP status separate
-------------------------

- For new HTTP-facing errors, set ``httpStatus:`` explicitly on
  ``LibresignException``. ``InjectionMiddleware`` reads ``getHttpStatus()``.
- Do not use ``getCode()`` as the HTTP status in new code. It identifies a
  semantic error when a consumer needs one.
- For compatibility, ``getHttpStatus()`` still falls back to ``getCode()``
  (or HTTP 422 when the code is ``0``). This legacy rule can propagate invalid
  statuses such as ``1``; do not copy it into new call sites.

.. code-block:: php

   throw new LibresignException(
       message: $message,
       httpStatus: Http::STATUS_UNPROCESSABLE_ENTITY,
   );

Preserve public contracts
-------------------------

Existing exception codes can also drive frontend actions:

- ``SigningErrorHandler`` maps code ``400`` to the create-signing-password
  action. ``PasswordToSignNotDefinedException`` must retain this code until
  its consumers are deliberately migrated.
- ``JSActions::ACTION_SIGN_ID_DOC`` is passed to the frontend through signing
  errors to identify the required identification-document action.

Before migrating a legacy code, follow its throw and catch paths and inspect
consumers such as ``SigningErrorHandler``, ``ErrorPayloadBuilder`` and frontend
action mapping. Preserve messages, response payloads, HTTP/OCS statuses and
frontend actions unless a contract change is explicitly agreed and tested.
Migrate the legacy status fallback separately, with regression tests.

Test observable behavior
------------------------

- Assert meaningful exception types with ``expectException()`` and stable
  consumed semantic codes with ``expectExceptionCode()``.
- Keep message assertions when the text itself is the behavior being tested,
  such as a user-visible fallback or a TSA diagnostic.
- For HTTP/OCS behavior, test the final status and payload, not only the data
  passed to a mocked response builder. For signing, test the action contract.
- Include a negative case showing that an unrelated error is not mistaken for
  the intended one, and a successful control when relevant.
