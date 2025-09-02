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
-   **Bug fixes**:

    -   If a fix affects **all supported versions**, implement it in ``main`` and backport it to the relevant stable branches.
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

Target branches for contributions
---------------------------------

-   **New features / improvements**:

    -   Create a branch from ``main``.
    -   Open a PR to ``main``.

-   **Bug fix affecting all supported versions**:

    -   Create a branch from ``main``.
    -   Open a PR to ``main``.
    -   Backport to all affected stable branches.

-   **Bug fix specific to a stable**:

    -   Create a branch from that stable branch.
    -   Open a PR to the same stable branch.

Bugfixes and backports
----------------------
If a bug fix also needs to be applied to an older release line, it must be **backported**.  
Backporting means applying the same change to another branch (Git calls this *cherry-picking*).

Automatic backport
^^^^^^^^^^^^^^^^^^
If the cherry-pick applies cleanly and only small conflicts need to be resolved, the `backport bot <https://github.com/nextcloud/backportbot>`_ can be used.

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
