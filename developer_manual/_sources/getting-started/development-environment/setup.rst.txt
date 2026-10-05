Setup
=====

.. note::
   If the project does not have an issue for what you want to work on, please create one first.

If you would like to start contributing code, you may wish to begin with our list of good first issues.  
See the respective sections below for further instructions.

Prerequisites
-------------

PHP
+++

Use the PHP version declared by LibreSign's current ``composer.json``
platform configuration and make sure it is also supported by the target
Nextcloud branch.

Do not copy a PHP version from this manual into automation. The repository
manifests and CI matrix are the source of truth and change as supported
Nextcloud versions move forward.

Node.js and npm
+++++++++++++++

Use the Node.js and npm versions declared in LibreSign's current
``package.json`` ``engines`` section.

Do not hard-code the versions from this manual in development tooling. The
application manifest is the source of truth.

Additional dependencies
+++++++++++++++++++++++

- ``poppler-utils``  
- System locale configured with UTF-8 charset  

Setting up Nextcloud
--------------------

This project depends on Nextcloud. To start writing code, you need a working Nextcloud environment.  
We recommend using Docker, but you may use another method if you prefer.  

Suggested setups:

- `LibreCode Coop Setup <https://github.com/LibreCodeCoop/nextcloud-docker-development/>`__  
- `Julius Härtl Nextcloud Setup <https://github.com/juliushaertl/nextcloud-docker-dev/>`__  

.. note::
   If you encounter problems with these setups, please open an issue in the corresponding repository.

When using `LibreCodeCoop/nextcloud-docker-development
<https://github.com/LibreCodeCoop/nextcloud-docker-development/>`__, follow
that repository's current quick-start and hostname documentation. Its shared
development proxy exposes each Compose project through its own
``*.localhost`` HTTPS hostname instead of requiring a fixed application
port.

If the environment does not become ready, use its documented diagnostics and
``docker compose ps``/logs rather than assuming a fixed container name or
URL.

Once Nextcloud is running, go to the setup folder and locate ``volumes/nextcloud/apps-extra``.  
Clone the LibreSign repository into this folder .

.. code-block:: bash

    git clone https://github.com/LibreSign/libresign.git
    cd libresign
    git submodule update --init


Open a bash session in the Nextcloud container:

.. code-block:: bash

    docker compose exec -u www-data nextcloud bash

Inside the container, go to ``apps-extra/libresign`` and run:

.. code-block:: bash

    # Download composer dependencies
    composer install

    # Download JS dependencies
    npm ci

    # Build and watch JS changes
    npm run watch

Configuring LibreSign
---------------------

After setting up the environment and installing LibreSign, open  
``Administration Settings > LibreSign`` in Nextcloud and:

- Click the **Download binaries** button.  
- Once all items show status **successful** (except “root certificate not configured”),  
  continue to the next section to configure the root certificate.


Extra apps
----------

LibreSign also integrates with the following Nextcloud apps:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - **App**
     - **Description**
   * - `guests <https://apps.nextcloud.com/apps/guests>`__
     - Allows inviting guest users to sign documents.
   * - `notifications <https://github.com/nextcloud/notifications>`__
     - Sends notifications about signature requests and updates.
   * - `activity <https://github.com/nextcloud/activity>`__
     - Logs activities such as signature requests and confirmations.
   * - `viewer <https://github.com/nextcloud/viewer>`__
     - Enables PDF viewing inside LibreSign without leaving the app.
   * - `files_pdfviewer <https://apps.nextcloud.com/apps/files_pdfviewer>`__
     - Required in combination with *viewer* for proper PDF rendering.
