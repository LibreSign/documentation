Updating
========

It is recommended to periodically update both Nextcloud and LibreSign in your local environment to ensure compatibility.

Updating Nextcloud
------------------

- First, check if there are any local modifications in your Nextcloud repository:

  .. code-block:: bash

     cd path/to/nextcloud
     git status

  .. note::
     If there are uncommitted changes, resolve them (commit, stash, or discard) before pulling updates.  
     This avoids conflicts when updating from the master branch.

- Pull the latest changes from the Nextcloud **master** branch:

  .. code-block:: bash

     git pull origin master

- After pulling, the ``3rdparty`` folder may be outdated. In that case, run:

  .. code-block:: bash

     git submodule update --init --recursive

Updating LibreSign
------------------

- Before starting a new task, always make sure your local ``main`` branch is up to date with the upstream repository:

  .. code-block:: bash

     cd path/to/libresign
     git checkout main
     git pull upstream main

- Then create your feature or fix branch from the updated ``main``.
