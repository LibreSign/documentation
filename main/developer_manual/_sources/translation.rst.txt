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

Translator hints in application source
--------------------------------------

This section is for developers changing translatable strings in the LibreSign
application. Translators do not need to edit source files: they can continue
working in Transifex as described above.

LibreSign follows the
`Nextcloud localization guide <https://docs.nextcloud.com/server/stable/developer_manual/basics/front-end/l10n.html>`__
for translation extraction. The following conventions apply to LibreSign source
code:

- Translate complete, meaningful messages using ``t()`` or ``n()``. Do not
  construct a sentence by concatenating individually translated fragments.
- Add a concise ``TRANSLATORS`` comment when a string's purpose, terminology,
  placeholders, or workflow context could be unclear. Place the comment
  immediately before the corresponding translation call.
- Write the marker **without a colon**: ``// TRANSLATORS Explanation`` in
  TypeScript, JavaScript, and PHP, or ``<!-- TRANSLATORS Explanation -->`` in
  Vue templates. Nextcloud also accepts a colon, but LibreSign deliberately
  uses one consistent style.
- Provide **one context comment for each relevant translation**, not several
  consecutive comments for one string. A repeated message at a different call
  site can have its own hint.
- Keep separate ``t()`` or ``n()`` calls on separate source lines, particularly
  in conditional expressions. Nextcloud's extraction tooling cannot associate
  an independent preceding hint with the second call on the same line.
- Explain placeholders such as ``{count}`` or ``%s`` when necessary, and
  preserve their spelling in translated strings.
- Do not edit generated files under ``l10n/``; they are managed through the
  translation synchronization workflow.

For example, give the document approver's action and an ordinary signer's
action distinct comments and translation calls:

.. code-block:: typescript

   if (isApprover) {
       // TRANSLATORS An authorized reviewer signs a submitted document to record its approval.
       return t('libresign', 'Sign and approve document')
   }
   // TRANSLATORS An ordinary signer digitally signs a document without recording an approval.
   return t('libresign', 'Sign document')

In a Vue template, the same convention applies:

.. code-block:: html

   <!-- TRANSLATORS Action to start reviewing a submitted document before approving it. -->
   <NcButton>{{ t('libresign', 'Review and approve') }}</NcButton>

Avoid assigning a single hint to both alternatives of a same-line conditional:

.. code-block:: typescript

   // Avoid: the second translation has no independent context comment.
   return isApprover ? t('libresign', 'Approve') : t('libresign', 'Sign')

The LibreSign repository enforces structural checks through
``npm run lint:translator-hints``, which is also included in ``npm run lint``.
The checker rejects colon-prefixed markers, consecutive hints for one
translation, and multiple LibreSign translation calls on one source line.
Run ``npm run test:translator-hints`` to test the checker itself.
