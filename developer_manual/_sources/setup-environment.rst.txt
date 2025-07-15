Setup environment
=================

Prerequirements
---------------

PHP version
+++++++++++

    * 1. Version: 8.1
    * 2. Docker image: php-fpm
    * 3. We using the minimum version to acepted by relative Nextcloud version, so you can use the same version of Nextcloud that you are using in your production environment.

Node version
++++++++++++

    * 1. Version: 20.0.0
    * 2. Check package.json for more information.

LibreCode Nextcloud docker environment
++++++++++++++++++++++++++++++++++++++

    * 1. Poppler-utils
    * 2. Locale charmap as UTF-8 at operational system


Developing for LibreSign
------------------------

.. note::
    If the project does not have an issue for what you want to do, create an issue first.

If you would prefer to write code, you may wish to start with our list of good first issues for LibreSign. See the respective sections below for further instructions.


Development environment
-----------------------

This project depends on the Nextcloud project, so to start writing code, you will need to set it up. We recommend using Docker for this, but feel free to use another method if you prefer. We suggest these two setups:

 - `LibreCode Coop Setup <https://github.com/LibreCodeCoop/nextcloud-docker-development/ />`__
 - `Julius Härtl Nextcloud Setup <https://github.com/juliusknorr/nextcloud-docker-dev />`__

 .. note::
    If you have any problems with these setups open an issue at corresponding to the project that you select to use.

After executing these Docker setups, wait until it's possible to access localhost. If access is not possible, go to your terminal, run the command docker ps, and then find the "nextcloud" image or "ghcr.io/juliushaertl/nextcloud-dev-php**". Access the address reported from the command output. (If you cannot find the image, you likely encountered a problem running the Docker setup; please return to the previous step.)

To get LibreSign executing go to the folder of the setup that you choose and find the folder called ``volumes/nextcloud/apps-extra`` and clone the LibreSign repository.

Open bash in Nextcloud container with ``docker compose exec -u www-data nextcloud bash``

Inside bash of Nextcloud go to the folder ``apps-extra/libresign`` and then run the commands:

.. code-block:: bash

   # Download composer dependencies
    composer install
   # Download JS dependencies
    npm ci
   # Build and watch JS changes
    npm run watch

To update API Documentation
---------------------------

After Configure the environment

After installing LibreSign, go to ``Administration Settings > LibreSign`` and:

    - Click in the ``Download`` binaries button. When it show status ``successful`` to all items, except ``root certificate not configured``, is time to configure root certificate in the next section.