Testing
=======

LibreSign has several test layers. Choose the narrowest layer that proves the
behavior you changed, then broaden validation before opening or updating a pull
request.

The application repository is the source of truth for current scripts and CI
jobs. See ``composer.json``, ``package.json``, ``tests/``, ``playwright/`` and
``.github/workflows``.

PHP unit tests
--------------

Unit tests live under ``tests/php/Unit`` and should not depend on a bootstrapped
Nextcloud runtime.

Run the unit suite:

.. code-block:: bash

   composer test:unit

Run a specific class, method or filter:

.. code-block:: bash

   composer test:unit -- --filter CrlServiceTest
   composer test:unit -- --filter testMethodName

The double dash ``--`` separates Composer arguments from PHPUnit arguments.

PHP runtime integration tests
-----------------------------

PHPUnit tests that require a bootstrapped Nextcloud runtime live under
``tests/php/Api`` and ``tests/php/Integration``.

Run them with:

.. code-block:: bash

   composer test:integration

A PHPUnit filter can be forwarded in the same way:

.. code-block:: bash

   composer test:integration -- --filter ClassName

Do not move tests with hidden runtime requirements such as database services,
``AppData`` or configured Nextcloud services into the unit suite merely to make
them faster.

Behat scenarios
---------------

Behavior/integration scenarios live under ``tests/integration`` and have their
own Composer dependencies.

Install them with:

.. code-block:: bash

   composer --working-dir=tests/integration install

Before creating a new step, inspect the existing vocabulary:

.. code-block:: bash

   cd tests/integration
   vendor/bin/behat -dl

Run a feature or a scenario starting at a specific line:

.. code-block:: bash

   vendor/bin/behat features/account/me.feature -v
   vendor/bin/behat features/account/me.feature:5 -v

Behat exercises a running Nextcloud environment and can modify application
state. Prefer the relevant feature or scenario while diagnosing a change.

Frontend unit tests
-------------------

Frontend unit tests live under ``src/tests`` and run with Vitest.

Run the complete frontend unit suite:

.. code-block:: bash

   npm test

Run one test file:

.. code-block:: bash

   npx vitest run src/tests/path/to/spec.ts

Use ``npm run test:coverage`` when coverage output is needed.

Browser/end-to-end tests
------------------------

Browser tests live under ``playwright`` and use Playwright.

Run the configured E2E suite:

.. code-block:: bash

   npm run test:e2e

Run one Playwright test file:

.. code-block:: bash

   npx playwright test playwright/e2e/path/to/spec.ts

These tests require the runtime described by the repository's current
Playwright configuration and CI workflow.

PHP linting, coding style and static analysis
---------------------------------------------

Check PHP syntax:

.. code-block:: bash

   composer lint

Check PHP coding style with PHP-CS-Fixer without changing files:

.. code-block:: bash

   composer cs:check

Apply PHP-CS-Fixer changes:

.. code-block:: bash

   composer cs:fix

Run Psalm:

.. code-block:: bash

   composer psalm

Update the Psalm baseline only when the remaining findings are intentionally
accepted and reviewed:

.. code-block:: bash

   composer psalm:update-baseline

Frontend linting and type checking
----------------------------------

Check ESLint, Stylelint and TypeScript:

.. code-block:: bash

   npm run lint
   npm run stylelint
   npm run ts:check

Apply the available frontend lint fixes:

.. code-block:: bash

   npm run lint:fix
   npm run stylelint:fix

Validation strategy
-------------------

During implementation, run the smallest test that can fail for the behavior
being changed. Before declaring work complete, broaden validation according to
the changed surface and inspect the relevant GitHub Actions results.

A green rerun alone is not evidence that an earlier failure was flaky. Diagnose
the first causal failure before adding retries, sleeps, suppressions or pins.
