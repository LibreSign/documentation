Contributing to LibreSign
==================

Overview
--------

Welcome
^^^^^^^^^^^^^^^^^^^^^^^^^^


We really appreciate everyone who would like to contribute to the LibreSign project! There are many ways to contribute, including writing code, filing issues on GitHub, helping people, assisting in triaging, reproducing, or fixing bugs that people have filed, and enhancing our documentation. Also giving a star to the project is a really good way to help and donate.

Contributing to the LibreSign repository. Access the repository at `LibreSign <https://github.com/LibreSign/libresign/>`__


Forms of contribution
^^^^^^^^^^^^^^^^^^^^^

Translating LibreSign
+++++++++++++++++++++

  - How translate LibreSign at Transifex
  - Add and/or change texts at LibreSign code using the L10N libraries. Would be good point to Nextcloud developer documentation at this point.
  - A quick instructions about how the translated text will go back to LibreSign repository
  - A warning talking that the l10n can't be changed


Setup environment
+++++++++++++++++

  Will be necessary move part of https://github.com/LibreSign/libresign/blob/main/CONTRIBUTING.md to here and add a comment ato CONTRIBUTING.md pointing to here about the environment
  - Prerequirements
    - PHP version
      - Why use the minimum PHP version. We can't send a code using features that only works at newest version of PHP. LibreSign need to be compatible with minimum PHP version accepted by relative Nextcloud server version
      - how to set the PHP version at LibreCode environment
    - Node version and where is possible to check the place that have this information (package.json)
    - Other not mandatory dependencies but important to have and explain that the LibreCode 
    Nextcloud docker environment already have the follow dependencies.
      - poppler-utils
      - locale charmap as UTF-8 at operational system

Branch policies
+++++++++++++++

    - Expose about main and stable branches
    - Explain that the development is at main branch of LibreSign
    - Creating branch and suggestion about branch nomenclature

Commits
+++++++

    - Conventional commits
        - Comments about conventional commits exposing a bit why we use this
        - possible issues about Conventional commits
    - DCO.
        - Expose why we use DCO.
        - Fixing possible issues about DCO    
    - Pull request
        - How to open
            - Instructions about destination branch
            - Possible issues about conventional commits and DCO and point to this documentation at the point that explain about this

Requesting features
+++++++++++++++++++

To request a new feature in LibreSign, you can open an issue in the repository. Provide a clear description of the feature you would like to see, including any relevant details or use cases. This helps the development team understand the request and prioritize it accordingly.

When submitting a feature request, consider the following:
- Be specific about the feature you want.
- Explain why the feature is important or how it will benefit users.
- Provide examples or use cases if possible.
- Check if a similar feature request already exists to avoid duplicates.

Follow these steps to request a feature:

1 - Access the LibreSign repository at `LibreSign <https://github.com/LibreSign/libresign/>`__

2 - Go to the `"Issues" <https://github.com/LibreSign/libresign/issues/>`__ tab.

    .. figure:: images/issue_screen.png
     :alt: Main screen.

    * 1 - Issue tab
    * 2 - Look and search for existing issues
    * 3 - Create a new issue, here you can request a new feature


Reposting bugs
++++++++++++++

Reporting bugs in LibreSign is essential for maintaining the quality and reliability of the application. If you encounter a bug, please follow these steps to report it effectively:

1 - Access the LibreSign repository at `LibreSign <https://github.com/LibreSign/libresign/>`__
2 - Go to the `"Issues" <https://github.com/LibreSign/libresign/issues/>`__ tab.

    .. figure:: images/issue_screen.png
     :alt: Main screen.

    * 1 - Issue tab
    * 2 - Look and search for existing issues
    * 3 - Create a new issue, here you can report a bug


Write code
++++++++++

When contributing code to LibreSign, it is important to follow best practices, ensure the quality and maintainability of the codebase. Here are some guidelines to keep in mind:
- Write clear and concise code that is easy to understand.
- Follow the coding standards and conventions used in the project.

Follow these steps to write code:

1 - Access the LibreSign repository at `LibreSign <https://github.com/LibreSign/libresign/>`__

2 - Go to the `"Issues" <https://github.com/LibreSign/libresign/issues/>`__ tab.

    .. figure:: images/issue_screen.png
     :alt: Main screen.

    * 1 - Code tab
    * 2 - Look and search for existing code. And if you want to contribute to a specific part of the code, you can search for it here.
    * 3 - If the issue no exist, feel free to create a new issue and let's to discuss about it.

3 - Choose an issue to work.

    .. figure:: images/choose_issue_screen.png
     :alt: Main screen.
    * 1 - Go to `"Labels" <https://github.com/LibreSign/libresign/issues/>`__.
    * 2 - Search for `"good first issue" <https://github.com/LibreSign/libresign/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22/>`__ to find issues that are suitable for new contributors.
    * 3 - Click on the `"good first issue" <https://github.com/LibreSign/libresign/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22/>`__ and you will see the issues.

4 - Read the issue description and attribute yourself to the issue.

    .. figure:: images/catch_issue.png
     :alt: Catch screen.
    * 1 - Let's us know about you will work on this issue, so we can track the progress and avoid duplicate work.
    * 2 - On the rith side, you will see the "Assignees" section. Click on it and select your username to assign yourself to the issue.

5 - Push your code to the repository.

    .. note::
        Before you push your code, it is import to know about good practice with "Convertional Commits" and "DCO(Developer Certidicate of Origin)"

        If you want to know more about "Convertional Commits" and "DCO", you can read the `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`__ and `DCO <https://developercertificate.org/>`__ documentation.

    
    * Possible error envolve DCO
    
        .. figure:: images/dco_error.png
         :alt: DCO error screen.
    
        If you see the error message "``You must sign off your commits with a DCO signoff``", it means that you need to add a signoff to your commit message. You can do this by adding the following line to your commit message:

        There are two things to fix:
        
            * 1. Sign off your commits (for DCO)
            * 2. Use the [Conventional Commits](https://www.conventionalcommits.org) format for commit messages
        
                Considering that you have 2 commits, at your terminal, run:

                .. code-block:: bash

                    git rebase -i HEAD~2 <

                The number 2 is about the quantity of commits ahead you will rebase.
                
                You’ll see your commits listed like this:

                .. code-block:: bash

                    pick e49199874 App metadata: Add donation link to appear on Nextcloud appstore <
                    pick 1ed4561ad doc: add donation links to Github Sponsors and Stripe <
        
                Change both lines from `pick` to `edit`:

                .. code-block:: bash

                    edit e49199874 App metadata: Add donation link to appear on Nextcloud appstore <
                    edit 1ed4561ad doc: add donation links to Github Sponsors and Stripe <

                Save and close the editor.

                Now you'll be editing the first commit. Run:

                .. code-block:: bash

                    git commit --amend --signoff <
                
                When your editor opens, change the first line of the commit message from:

                .. code-block:: bash

                    App metadata: Add donation link to appear on Nextcloud appstore <

                to:

                .. code-block:: bash

                    docs: add donation link to appear on Nextcloud appstore <

                Save and close.

                Then:

                .. code-block:: bash

                    git rebase --continue <

                Now you're on the second commit. Run:

                .. code-block:: bash

                    git commit --amend --signoff <

                Change the first line from:

                .. code-block:: bash

                    doc: add donation links to Github Sponsors and Stripe <

                to: 

                .. code-block:: bash

                    docs: add donation links to GitHub Sponsors and Stripe <

                Save and close.

                Then:

                .. code-block:: bash

                    git rebase --continue <

                After this, you'll complete the rebase flow and be able to push your branch. Since this changes past commits, you’ll need to push with force:

                .. code-block:: bash

                    git push --force-with-lease origin patch-2 <