Frontend
========

By default, the Nextcloud server repository ships with the frontend already built for production.  
For development purposes, you may want to rebuild it in **development mode**.  
This allows you, for example, to inspect server components using the Vue Devtools browser extension.

Building server for development
-------------------------------

To rebuild the frontend in development mode:

1. Access the Nextcloud container:

   .. code-block:: bash

      docker compose exec -u www-data nextcloud bash

2. Go to the root folder of the Nextcloud server:

   .. code-block:: bash

      cd /var/www/html

3. Install dependencies and build in dev mode:

   .. code-block:: bash

      npm ci && npm run dev

Reverting the server build
--------------------------

If you build the frontend in development mode, you must revert the changes before pulling new updates from the Nextcloud **master** branch.  
Otherwise, you may run into conflicts.

To revert the build:

1. Exit the container.  
2. From your host machine, go to the Nextcloud server root folder.  
3. Remove the ``dist`` folder and restore it from Git:

   .. code-block:: bash

      rm -rf dist
      git checkout -- dist

After pulling the latest changes, you can rebuild the frontend in development mode again if needed.
