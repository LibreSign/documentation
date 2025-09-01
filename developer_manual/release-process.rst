Release process
===============

Resuming the steps:

1. Identify the next version number of all releases.
2. Create the changelog of all branches that will be released.
    You will need to create the changelog in the :code:`CHANGELOG.md` file from the :code:`main` branch and then backport it to the stable branches.
3. Make the necessary changes into the codebase to prepare the release.

    .. note::
        You can use the :code:`[skip ci]` tag in the commit message to skip the CI checks for the backport PRs to make the process faster.

4. Create a pull request to the `main` branch with the changes that you made.
5. After the CI finish with success and the PR is merged, backport the changes to the stable branches that will be released.
6. After the backport PRs are merged, create the releases in GitHub.
7. Verify that the GitHub Action that creates the packages and publish them in the Nextcloud App Store finish with success.
8. Announce the release in the Telegram channel.

Version numbers
---------------

- The version number follows **MAJOR.MINOR.PATCH**.
- ``MAJOR`` aligns with the supported Nextcloud Server version.
- ``MINOR`` is used for LibreSign feature releases.
- ``PATCH`` is used for bug fixes or small improvements.

1. Go to Milestones in the LibreSign repository:

    https://github.com/LibreSign/libresign/milestones

2. Identify what is the next patch version to be released.
3. Look the closed items to identify if we have new features,

    1. If is a major release, increment with :code:`1` the :code:`MAJOR` version and reset :code:`MINOR` and :code:`PATCH`.

    .. note::
        We only create a major release when is created a new stable branch for a new Nextcloud major version.

    2. To new features, increment with :code:`1` the ``MINOR`` version and reset ``PATCH`` to ``0``.
    3. To bug fixes, increment the ``PATCH`` version.

Stable branches
---------------

Each **stable branch** in LibreSign corresponds to a specific Nextcloud **MAJOR** version.

For example: ``stable21`` is compatible with Nextcloud 21.

Release checklist
-----------------

A new release starts by creating a GitHub issue with one of the following titles:

.. code-block:: plain

    🚀 Release todo v20.1.9
    🚀 Release todo v20.1.9 and v21.1.8

In the body, paste and adapt the following template. Replace placeholders
with the correct values as you progress through the steps.

.. code-block:: markdown

    <!-- 1. Replace "20.1.9" with the version number e.g. "12.2.4" -->
    <!-- Replace "20.1.8" with the previous version number e.g. "12.2.3" -->
    <!-- 2. Replace "stable20" with the LibreSign minor branch name e.g. "stable22" -->
    ## 💺 Preparation
    - [ ] Check there are no pending backports:
        - [ ] https://github.com/LibreSign/libresign/labels/backport-request
    - [ ] Check all milestones don't have priority issues still open
        <!-- Add above the link of milestone that will be involved in this release process -->
        <!-- Get branches/versions to release from https://github.com/LibreSign/libresign/milestones -->
        - [ ] https://github.com/LibreSign/libresign/milestone/<!-- put here the milestone ID e.g. 318 -->
        - [ ] https://github.com/LibreSign/libresign/milestone/<!-- put here the milestone ID e.g. 319 -->
    - [ ] Check there are no important PRs open against the branch
        <!-- Add above the link with correct base branch of stables that will be involved in this release process -->
        <!-- Get branches/versions to release from https://github.com/LibreSign/libresign/milestones -->
        - [ ] https://github.com/LibreSign/libresign/pulls?q=is%3Apr+is%3Aopen+base%3Astable20
        - [ ] https://github.com/LibreSign/libresign/pulls?q=is%3Apr+is%3Aopen+base%3Astable22
    - [ ] List all PRs that will be added to the changelog
        - [ ] Go to https://github.com/LibreSign/libresign/releases/new
        - [ ] At the tag field, type the next version number, e.g. `v20.1.9`
        - [ ] Select the base branch, e.g. `stable20`
        - [ ] Click at the button to **Generate release notes**
    - [ ] Go to the main branch, pull the latest changes and create a new branch called `chore/changelog`
    - [ ] Add the changelog entries to the `CHANGELOG.md` file, following the pattern used in the file.
    - [ ] Make this to all releases that will be done in this process.
    - [ ] Create a PR against `main` branch at the `CHANGELOG.md` file with the changelog of all milestones that are subject to the release. Look the pattern used in the file and follow it.
        You can use the :code:`[skip ci]` tag in the commit message to skip the CI checks for the backport PRs to make the process faster.
        ```
        name suggestions to commit and pull request:
        chore(release): Changelog for 20.1.9
        chore(release): Changelog for 20.1.9 and 20.1.8
        ```
    - [ ] Merge the PR
    <!-- Duplicate the follow steps for each version that will be released, starting with the oldest version. -->
    <!-- Pay attention to start with the **oldest** version here, so the appstore and github releases show the newest version as "Last release" and them. -->
    <!-- Replace "XX" with the Nextcloud stable branch number e.g. "22" for "stable22" -->
    <!-- 1. Replace "20.1.9" with the version number e.g. "12.2.4" -->
    <!-- Replace "20.1.8" with the previous version number e.g. "12.2.3" -->
    <!-- 2. Replace "stable20" with the LibreSign minor branch name e.g. "stable22" -->
    ## 🚀 v20.1.9
    - [ ] Backport the changelog from main to the stable branches
        - [ ] <!-- Add link to PR here -->
    <!-- At the backport PR, do the following steps: -->
    - [ ] Remove changelog entries in `CHANGELOG.md` of higher versions
    - [ ] Bump the version in `appinfo/info.xml`
    - [ ] Bump the version in `package.json` and in `package-lock.json`. The following command will return a new version name, make sure it matches what you expect:
    ```sh
    # Make sure the printed version matches the info.xml version
    npm version --no-git-tag-version $(xmllint --xpath '/info/version/text()' appinfo/info.xml)
    ```
    - [ ] Merge the backport
    - [ ] Do a quick smoke test signing documents with:
        - [ ] Chrome
        - [ ] Edge
        - [ ] Firefox
        - [ ] Safari
    - [ ] Create the new milestone
        - [ ] Rename milestone `💚 Next Patch (XX)` to `v20.1.9` in https://github.com/LibreSign/libresign/milestones
        Unless last release of the stable branch:
        - [ ] Create a follow up milestone for `💚 Next Patch (XX)` (Due date in ~4 weeks, ~4 days for beta/RC)
        - [ ] Move all open PRs and issues from milestone `v20.1.9` to `💚 Next Patch (XX)`: https://github.com/LibreSign/libresign/issues?q=is%3Aissue%20state%3Aopen%20milestone%3Av20.1.9
        - [ ] Move all open PRs and issues from milestone `v20.1.9` to `💚 Next Patch (XX)`: https://github.com/LibreSign/libresign/issues?q=is%3Apr%20state%3Aopen%20milestone%3Av20.1.9
        - [ ] Close the `v20.1.9` milestone
    - [ ] Archive all issues and PRs that were merged in this release
        - [ ] https://github.com/orgs/LibreSign/projects/2/views/4
    - [ ] Create a new release
        - [ ] Prepare a (pre-)release in https://github.com/LibreSign/libresign/releases/new?tag=v20.1.9&target=stable20
        - [ ] Make sure that chosen tag is v20.1.9, target is stable20, and previous tag is v20.1.8
        - [ ] Add the content of respective `CHANGELOG.md` section from merged PR
        - [ ] Use the **Generate release notes** button and wrap the output result into
        ```
        ## What's Changed
        <!-- Add the content of the changelog section here -->

        Milestone: [v20.1.9](<!-- Add the link to the closed milestone here -->)
        **Full Changelog**: https://github.com/LibreSign/libresign/compare/v20.1.8...v20.1.9?closed=1
    - [ ] Publish release
    - [ ] Check that the GitHub Action started: https://github.com/LibreSign/libresign/actions
    - [ ] Ensure that the GitHub Action finished successfully: https://github.com/LibreSign/libresign/actions
    - [ ] Post the changelog in [💬 LibreSign team public 👥](https://t.me/LibreSign)
