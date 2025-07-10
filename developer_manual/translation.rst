Translation
===========

Transifex
+++++++++

* 1. Access the link to start translating: `LibreSign at Transifex <https://app.transifex.com/nextcloud/nextcloud/libresign>`__
* 2. If you do not have an account, accesse Transifex to create one or login.

L10N libraries
++++++++++++++

LibreSign uses the L10n libraries from Nextcloud. You can find the documentation for these libraries at `Nextcloud L10N <https://github.com/nextcloud-libraries/nextcloud-l10n>`__.

    .. note::
        L10n can't be changed.

How the way to translate works with Transifex
+++++++++++++++++++++++++++++++++++++++++++++

The LibreSign repository is connected to Transifex, so you can translate the application directly from there. The translations are automatically updated in the repository.

* 1. Origin file(example: en.po) is versioned in the repository.
* 2. The transifex sincronization and extracted this file.
* 3. Translaters can translate the file in Transifex.
* 4. Transifex send the translated file to the repository(as PR).

