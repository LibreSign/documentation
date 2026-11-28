Branch policies
===============

This document describes the branching model used in LibreSign and how contributions should be targeted.

Branch names
------------

Main
^^^^
The ``main`` branch is the **default development branch** of LibreSign, equivalent to the ``master`` branch in the Nextcloud Server repository.

-   Code in ``main`` represents the **next stable release** of LibreSign, which aligns with the **next stable release** of the Nextcloud Server.
-   Development in ``main`` must follow the `Nextcloud Server Maintenance and Release Schedule <https://github.com/nextcloud/server/wiki/Maintenance-and-Release-Schedule>`_ to ensure compatibility and coordinated releases.
-   New features and general changes are developed in short-lived branches created from ``main`` and merged back through reviewed pull requests.
    They are **not backported** to released stable branches: they reach users with the next LibreSign major release.
-   **Bug fixes**:

    -   If a fix affects **all supported versions**, implement it in ``main`` and backport it to the maintained stable branches.
    -   If a fix is **specific to a single stable line**, implement it only in that stable branch.

-   The ``main`` branch is **not intended for production use**; it contains code under active development for the upcoming release.

Stables
^^^^^^^
Stable branches maintain release lines compatible with a specific **Nextcloud Server** major version.

-   Branch names follow the format ``stableXX``, where ``XX`` is the **MAJOR** version of the supported Nextcloud Server.

    -   Example: ``stable21`` → compatible with Nextcloud 21.

-   Create a new stable branch when a new Nextcloud Server major version is released and LibreSign will support it.
-   **To identify which Nextcloud Server version a stable branch supports**:

    1.  Checkout the branch locally or open it in GitHub.
    2.  Open the file ``appinfo/info.xml``.
    3.  Look for the ``<nextcloud>`` element:

        .. code-block:: xml

            <nextcloud min-version="21" max-version="21" />

        In LibreSign, ``min-version`` and ``max-version`` are always the same number.  
        This number is the MAJOR version of the compatible Nextcloud Server.

Maintained stable branches
^^^^^^^^^^^^^^^^^^^^^^^^^^
A stable branch is maintained while its Nextcloud Server major version is supported, according to the `Nextcloud Server Maintenance and Release Schedule <https://github.com/nextcloud/server/wiki/Maintenance-and-Release-Schedule>`_.

-   Once that Nextcloud Server version reaches **end of life**, the corresponding LibreSign stable branch stops receiving regular backports and releases.
-   Maintaining an end-of-life stable branch is an exception, only when required by a customer support contract.
-   Before requesting a backport, check that every target branch is still maintained.

Target branches for contributions
---------------------------------

-   **New features / improvements**:

    -   Create a branch from ``main``.
    -   Open a PR to ``main``.
    -   Do not backport to released stable branches.

-   **Bug fix affecting all supported versions**:

    -   Create a branch from ``main``.
    -   Open a PR to ``main``.
    -   Backport to all maintained stable branches affected by the bug.

-   **Bug fix specific to a stable**:

    -   Create a branch from that stable branch.
    -   Open a PR to the same stable branch.

-   **Security fix**:

    -   Same flow as a bug fix affecting all supported versions.
    -   Backport to all maintained stable branches with priority over other backports.

-   **Tests, CI, chores, refactors and documentation**:

    -   Create a branch from ``main``.
    -   Open a PR to ``main``.
    -   Do not backport by default. Backport only when a stable branch needs the change to receive a fix or to stay maintainable (for example, a CI workflow that stopped working on that branch).

What is backported
^^^^^^^^^^^^^^^^^^
Released stable branches receive **bug fixes and security fixes only**. Features, improvements and maintenance changes stay in ``main``.

A feature is backported to a released stable branch only by an explicit maintainer decision, recorded in the pull request. This is an exception, not the normal flow.

Bugfixes and backports
----------------------
If a bug fix also needs to be applied to an older release line, it must be **backported**.  
Backporting means applying the same change to another branch (Git calls this *cherry-picking*).

Before requesting a backport:

-   Check that the target branch is still maintained (see `Maintained stable branches`_).
-   Check that the change applies correctly to each target branch. Differences between branches can make the generated backport incomplete or different from the original change, so review the resulting backport before merging it.
-   If the change adds a dependency or raises a runtime requirement (for example, the minimum PHP version), backport it only to the stable branches that satisfy it.

Automatic backport
^^^^^^^^^^^^^^^^^^
If the cherry-pick applies cleanly and only small conflicts need to be resolved, the backport bot can be used.
In LibreSign repositories the bot runs as ``backportbot-libresign`` and accepts the same commands as the `Nextcloud backport bot <https://github.com/nextcloud/backportbot>`_.

Comment on the pull request with the target branch. The bot reads only the first line of each comment, so request one branch per comment:

.. code-block:: text

    /backport to stable34

Then, in a separate comment:

.. code-block:: text

    /backport to stable33

See the `bot usage <https://github.com/nextcloud/backportbot#usage>`_ for available commands.

Manual backport
^^^^^^^^^^^^^^^
For more complex changes, the backport must be done manually:

.. code-block:: bash

    # Switch to the target branch and update it
    git checkout stable25
    git pull origin stable25

    # Create the new backport branch
    git checkout -b fix/foo-stable25

    # Cherry-pick the change from the commit SHA of the original PR in main
    git cherry-pick abc123

    # Resolve any conflicts, commit, and push
    git push origin fix/foo-stable25

    # Open a pull request for the backport

Creating branch
---------------
Follow the convention of naming branches as ``feature/description`` or ``bugfix/description``.
