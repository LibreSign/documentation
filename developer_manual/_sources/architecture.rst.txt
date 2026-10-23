.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

Architecture and code map
=========================

LibreSign is a Nextcloud application. This page is the canonical starting point
for understanding where responsibilities live before changing code.

Use the application repository as the source of truth for current class names,
APIs and implementation details:

`LibreSign/libresign <https://github.com/LibreSign/libresign>`_.

Repository map
--------------

The main application areas are:

``lib/``
   PHP backend code. Controllers expose HTTP/OCS behavior, services contain
   application logic and orchestration, database classes persist application
   state, and handlers contain specialized signing/certificate behavior.

``src/``
   Vue and TypeScript frontend code.

``tests/php/Unit/``
   Isolated PHP unit tests.

``tests/php/Api/`` and ``tests/php/Integration/``
   PHPUnit tests that exercise a bootstrapped Nextcloud runtime.

``tests/integration/``
   Behat behavior/integration scenarios and their support code.

``src/tests/``
   Frontend unit tests.

``playwright/``
   Browser/end-to-end test support where present in the current application
   repository.

``appinfo/``
   Nextcloud application metadata and route/configuration declarations.

``3rdparty/``
   Scoped third-party dependencies. Follow the instructions in that directory
   before changing it.

Responsibility boundaries
-------------------------

Backend enforcement
~~~~~~~~~~~~~~~~~~~

Permissions, validation, policy resolution and other security-sensitive
business rules must be enforced by the backend. Frontend checks may improve the
user experience, but they are not an authorization boundary.

Generated and vendored content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Do not edit generated translations, generated API/type output or vendored
dependencies as if they were normal source files. Change their source contract
and regenerate them using the workflow documented by the application
repository.

Signing and document integrity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changes affecting document signing, PDF validation, certificates, cryptographic
policy, authorization or persisted audit state require focused regression and
negative tests at the affected trust boundary.

Nextcloud integration
~~~~~~~~~~~~~~~~~~~~~

Prefer public Nextcloud OCP APIs and the repository's existing integration
patterns. Before introducing a workaround for an upstream change, verify the
supported Nextcloud version and current upstream contract.

Where to go next
----------------

- :doc:`getting-started/development-environment/index` for setting up a
  development runtime.
- :doc:`getting-started/tests` for testing and validation.
- :doc:`development-workflow` for the normal issue-to-pull-request workflow.
- :doc:`api/index` for the public API.
- :doc:`release-process` for release operations.
