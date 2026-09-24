Testing
=======

LibreSign includes multiple test suites (see ``.github/workflows`` for CI jobs).  
Below are the most relevant for day-to-day development and how to run them locally.

.. admonition:: Tips

   - Keep your local branches rebased and dependencies up to date to reduce noise in lints and type checks.
   - Tests and CI are also part of the documentation, check ``.github/workflows`` and the ``tests`` folder for usage examples.

Unit tests
----------

Run a specific unit test (filter by class, method, or pattern):

.. code-block:: bash

   composer test:unit -- --filter MyClassTest

.. note::
   The double dash ``--`` is required to pass arguments to the script
   ``test:unit`` (and not to Composer itself).

Running the entire unit suite locally may take a while. Prefer filtering by the
tests you added or modified.

Integration tests (Behat)
-------------------------

Integration tests live under ``tests/integration``. To run them:

1. Install dependencies inside that folder:

   .. code-block:: bash

      cd tests/integration
      composer install

2. Run a specific scenario (example):

   .. code-block:: bash

      runuser -u www-data -- vendor/bin/behat --xdebug features/account/me.feature:5

   The example above executes the scenario that **starts at line 5** of
   ``features/account/me.feature``.

Static analysis
---------------

**PHPCS** (coding style):

.. code-block:: bash

   composer cs:fix

**Psalm** (type analysis):

.. code-block:: bash

   composer psalm

Update Psalm baseline (only when appropriate):

.. code-block:: bash

   composer psalm:update-baseline

JavaScript linters
------------------

**ESLint** and **Stylelint**:

.. code-block:: bash

   npm run lint:fix
   npm run stylelint:fix
