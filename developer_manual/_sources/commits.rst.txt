Commits
=======

Conventional commits
++++++++++++++++++++

If you want to know more about `Convertional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`__, you can read the documentation.

About the title of the commit, you should use the following format:

                .. code-block:: bash

                    feat:my pull request <

About the description of the commit, you should use the following format:

                .. code-block:: bash

                    Pull Request Description

                    Related Issue

                    Issue Number: #830

                    Pull Request Type

                    - Feature

                    Pull request checklist

                    - [X] Add button "Open file"
                    - [x] Add action to the button <


DCO
+++

If you want to know more about `DCO(Developer Certidicate of Origin) <https://developercertificate.org/>`__, you can read the documentation.


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