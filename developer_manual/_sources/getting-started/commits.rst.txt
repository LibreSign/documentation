Commits
=======

Conventional commits
++++++++++++++++++++

LibreSign follows the `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`__ specification.  
This makes commit history more readable and allows automatic tools to generate changelogs.

**Commit title format:**

.. code-block:: text

   feat: add button to open files

**Commit description format:**

.. code-block:: text

   Short description of the pull request

   Related issue: #830  
   Type: Feature

   Checklist:
   - [x] Add "Open file" button  
   - [x] Add action to the button  

DCO
+++

LibreSign also requires commits to be signed off with the  
`DCO (Developer Certificate of Origin) <https://developercertificate.org/>`__.

If you see the error message:

``You must sign off your commits with a DCO signoff``

it means your commits are missing the ``Signed-off-by`` line.

Fixing DCO errors and commit messages
-------------------------------------

There are two common issues to fix:

1. Sign off your commits (DCO).  
2. Use the `Conventional Commits <https://www.conventionalcommits.org/>`__ format.

Example: rebasing two commits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Start an interactive rebase for the last 2 commits:

   .. code-block:: bash

      git rebase -i HEAD~2

2. Change ``pick`` to ``edit`` for both commits:

   .. code-block:: text

      edit e49199874 App metadata: Add donation link to appear on Nextcloud appstore
      edit 1ed4561ad doc: add donation links to Github Sponsors and Stripe

3. Amend the first commit:

   .. code-block:: bash

      git commit --amend --signoff

   Change the title from:

   .. code-block:: text

      App metadata: Add donation link to appear on Nextcloud appstore

   To:

   .. code-block:: text

      docs: add donation link to appear on Nextcloud appstore

   Save and close, then continue the rebase:

   .. code-block:: bash

      git rebase --continue

4. Amend the second commit:

   .. code-block:: bash

      git commit --amend --signoff

   Change the title from:

   .. code-block:: text

      doc: add donation links to Github Sponsors and Stripe

   To:

   .. code-block:: text

      docs: add donation links to GitHub Sponsors and Stripe

   Save and close, then continue:

   .. code-block:: bash

      git rebase --continue

5. Push your branch with force (since commit history has changed):

   .. code-block:: bash

      git push --force-with-lease origin patch-2
