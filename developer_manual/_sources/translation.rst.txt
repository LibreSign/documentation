Translation
===========

Transifex
---------

1. Access the link to start translating:

   `LibreSign at Transifex <https://app.transifex.com/nextcloud/nextcloud/libresign>`__
2. If you do not have an account, create one or log in at Transifex.

That’s all translators need to start.

You don’t need to change anything in the codebase to translate LibreSign.

Fixing original strings
-----------------------

If you find an original string that needs to be corrected, locate it in the codebase and send a Pull Request (PR) to the repository with the fix.

Translation workflow with Transifex
-----------------------------------

The LibreSign repository is directly integrated with Transifex. This means you can translate the application in Transifex, and the translations are automatically synchronized with the repository.

Workflow steps:

1. A GitHub bot runs daily to detect new strings in the codebase.
2. All new strings are pushed to Transifex and made available for translation.
3. Translators provide translations directly in Transifex and will be committed to the repository at the next daily run.
4. Transifex sends the translated files back to the repository, placing them into the ``l10n`` folder.
5. You will need to wait the next release to see your translations in the application.