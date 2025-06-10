Contribution Guide
==================

Overview
-------------

About LibreSign repository
^^^^^^^^^^^^^^^^^^^^^^^^^^

The LibreSign repository is a collaborative platform where developers can contribute to the LibreSign project. It is designed to facilitate contributions from developers of all skill levels, whether they are new to the project or experienced contributors.

This guide provides an overview of how to contribute to the LibreSign repository, including the process for submitting changes, reviewing contributions, and best practices for collaboration.

Contributing to the LibreSign repository. Access the repository at `LibreSign <https://github.com/LibreSign/libresign/>`__


Forms of contribution
^^^^^^^^^^^^^^^^^^^^^

Translating LibreSign
+++++++++++++++++++++


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

2 - Go to the "Issues" tab.

    .. figure:: images/issue_screen.png
     :alt: Main screen.

    * 1 - Issue tab
    * 2 - Look and search for existing issues
    * 3 - Create a new issue, here you can request a new feature


Reposting bugs
++++++++++++++

Reporting bugs in LibreSign is essential for maintaining the quality and reliability of the application. If you encounter a bug, please follow these steps to report it effectively:

1 - Access the LibreSign repository at `LibreSign <https://github.com/LibreSign/libresign/>`__
2 - Go to the "Issues" tab.

    .. figure:: images/issue_screen.png
     :alt: Main screen.

    * 1 - Issue tab
    * 2 - Look and search for existing issues
    * 3 - Create a new issue, here you can report a bug


Write code
++++++++++++

When contributing code to LibreSign, it is important to follow best practices to ensure the quality and maintainability of the codebase. Here are some guidelines to keep in mind:
- Write clear and concise code that is easy to understand.
- Follow the coding standards and conventions used in the project.

Follow these steps to write code:

1 - Access the LibreSign repository at `LibreSign <https://github.com/LibreSign/libresign/>`__

2 - Go to the "Issue" tab.

    .. figure:: images/issue_screen.png
     :alt: Main screen.

    * 1 - Code tab
    * 2 - Look and search for existing code. And if you want to contribute to a specific part of the code, you can search for it here.
    * 3 - If the issue no exist, feel free to create a new issue and let's to discuss about it.

3 - Choose an issue to work.

    .. figure:: images/choose_issue_screen.png
     :alt: Main screen.
    * 1 - Go to "Labels".
    * 2 - Search for "good first issue" to find issues that are suitable for new contributors.
    * 3 - Click on the "good first issue" and you will see the issues.

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
    
        If you see the error message "You must sign off your commits with a DCO signoff", it means that you need to add a signoff to your commit message. You can do this by adding the following line to your commit message:
        
        .. code-block:: text

            Signed-off-by: Your Email(example@email.com) <
        
        In your local branch, run:

        .. code-block:: bash

            git rebase HEAD~2 --signoff <

        Force push your changes to overwrite the branch

        .. code-block:: bash

            git push --force-with-lease origin <branch_name>