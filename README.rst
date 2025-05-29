=======================
LibreSign Documentation
=======================

Documentation is published on `<https://docs.libresign.coop>`_.
To edit it yourself, you need to tinker a bit with Git and Sphinx.
See the `Style Guide <https://github.com/nextcloud/documentation/blob/master/style_guide.rst>`_ for formatting and style conventions.

Manuals
-------

This repository hosts three manuals:

* **Users' Manual**
* **Administration Manual**
* **Developers Manual**

Please wrap lines at 80 characters.

Spelling and Capitalization Conventions
---------------------------------------

* Nextcloud
* LibreSign

License
-------

All documentation in this repository is licensed under the Creative Commons
Attribution 3.0 Unported license (`CC BY 3.0`_).

.. _CC BY 3.0: https://creativecommons.org/licenses/by/3.0/deed.en_US

Style
-----

Source files are written using the `Sphinx Documentation Generator
<https://www.sphinx-doc.org/en/master/>`_. The syntax follows the `reStructuredText
<http://docutils.sourceforge.net/rst.html>`_ style, and can also be edited
from GitHub.

Structure
---------

Of course, think about structure. Keep in mind that we try NOT to move or rename
pages once they are created! Lots of external sources link to our documentation,
including the indexing by search engines of course. So once you create a page with a certain
name, it has to stay in that location and with that name. Think of it as API stability
- we have to ensure things stay as they are as much as possible. Renaming or moving
is only allowed in exceptional circumstances and only when a redirect is put in place.

Editing
-------

Contributing to the documentation requires a GitHub account.

To edit a document, you can edit the .rst files on your local system, or work
directly on GitHub. The latter is only suitable for small fixes and improvements
because substantial editing efforts can better be controlled on your local PC.

The best way is to install a complete Sphinx build environment and work on your
local PC or using the docker-compose that stay at home folder of this repository.
You will be able to make your own local builds, which is the fastest
and best way to preview for errors. Sphinx will report syntax errors, missing
images, and formatting errors. The GitHub preview is not complete and misses
many mistakes. Create a new branch against the main, make your edits, then push
your new branch to GitHub and open a new PR.

To edit on GitHub, fork the repository (see top-right of the screen, under
your username). You will then be able to make changes easily. Once done,
you can create a pull request and get the changes reviewed and back into
the official repository.

When editing either on your own local PC or on GitHub, be sure to sign of
commits, to certify adherence to the Developer Certificate of Origin,
see https://github.com/probot/dco . Your commit messages need to have,
the name and email address of the contributor.

  Signed-off-by: Awesome Contributor <awesome.contributor@reach.me>

If using the command line and your name and email are configured, you can use

  git commit -s -m 'Commit message'

In both settings be sure that your email address matches that in your GitHub profile,
which if you have privacy enabled will be github.username@users.noreply.github.com


Building
--------

Building HTML
=============

Using pipenv
^^^^^^^^^^^^

1. Install ``pipenv`` - https://pipenv.readthedocs.io/en/latest/
2. Change into the environment: ``pipenv shell``
3. Install the dependencies ``pip install -r docs/requirements.txt``
4. Now you can use ``make ...`` to build all the stuff - for example ``make html`` to build the HTML flavor of all manuals
   The build assets will be put into the individual documentation subdirectories like ``developer_manual/_build/html/com``

To change into this environment you need to run ``pipenv shell`` to launch the shell and to exit you can use either ``exit`` or ``Ctrl`` + ``D``.

Using venv
^^^^^^^^^^

1. Install ``python3-venv``
2. Only once: Create a venv (typically inside this repository): ``python -m venv venv``
3. Activate the environment (inside this repository): ``source venv/bin/activate``
4. Install the dependencies ``pip install -r docs/requirements.txt``
5. Now you can use ``make ...`` to build all the stuff - for example ``make html`` to build the HTML flavor of all manuals
   The build assets will be put into the individual documentation subdirectories like ``developer_manual/_build/html/com``

Autobuilding
^^^^^^^^^^^^

When editing the documentation installing ``sphinx-autobuild`` though pip can be helpful. This will watch file changes and automatically reload the html preview:

1. Install ``pip install sphinx-autobuild``
2. Enter the documentation section ``cd user_manual``
3. Watch for file changes ``make SPHINXBUILD=sphinx-autobuild html``
4. Open http://127.0.0.1:8000 in the browser and start editing

Using the VSCode DevContainer
=============================

This repository contains a full-featured `VSCode DevContainer <https://code.visualstudio.com/docs/devcontainers/containers>`_.
You can use it in your local development environment or via `GitHub Codespaces <https://github.com/features/codespaces>`_.
Just open the container an use one of the commands from above to build the project. For example ``make`` to build the full
documentation. You can also use ``make SPHINXBUILD=sphinx-autobuild html``
in combination with `port forwarding <https://code.visualstudio.com/docs/devcontainers/containers#_forwarding-or-publishing-a-port>`_
to  watch file changes and automatically reload the html preview.

Usign docker
============
You can also use the `docker-compose.yml` file to build the documentation using
Docker. This is useful if you want to avoid installing Python and its
dependencies on your local machine.

1. Make sure you have Docker and Docker Compose installed.
2. Open a terminal and navigate to the root directory of the repository.
3. Run the following command to build the documentation:

   ``docker-compose up``

   This will build the HTML documentation and place it in the `volumes/html` directory.
   And also will start a HTTP server and you can access the documentation at `http://localhost:8000`.

4. To stop the server, press `Ctrl+C` in the terminal.


.. _CC BY 3.0: https://creativecommons.org/licenses/by/3.0/deed.en_US
.. _`Xcode command line tools`: https://stackoverflow.com/questions/9329243/xcode-install-command-line-tools

This README was based on the `Nextcloud documentation <https://github.com/nextcloud/documentation/blob/master/README.rst>`_.