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

- The PHP version must match the minimum required by the current Nextcloud **master** branch.  
- You can verify this in the ``composer.json`` of the Nextcloud server:  
  `Nextcloud Server composer.json <https://github.com/nextcloud/server/blob/master/composer.json>`__  
  (see the ``config.platform.php`` entry).  
- At the time of writing this documentation, the minimum required version is **8.1**.  
- Docker image suggestion: ``php-fpm``  

Node.js
+++++++

- The Node.js version must match the engine required by the current Nextcloud **master** branch.  
- You can verify this in the ``package.json`` of the Nextcloud server:  
  `Nextcloud Server package.json <https://github.com/nextcloud/server/blob/master/package.json>`__  
  (see the ``engines.node`` entry).  
- At the time of writing this documentation, the required version is **^22.0.0** (with npm **^10.5.0**).  

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

After running the Docker setup, check if Nextcloud is available at ``http://localhost``.  
If it is not, run ``docker ps`` and look for the ``nextcloud`` container (or ``ghcr.io/juliushaertl/nextcloud-dev-php**``).  
If you cannot find it, the setup likely failed; please repeat the previous step.

Once Nextcloud is running, go to the setup folder and locate ``volumes/nextcloud/apps-extra``.  
Clone the LibreSign repository into this folder .

.. code-block:: bash

    git clone https://github.com/LibreCodeCoop/libresign.git
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
