Release process
===============

The release process will start creating an issue using one of the following name suggestions:

.. code-block:: plain

    Release process for v20.1.9
    Release process for v20.1.9 and v20.1.8

To the body, add the following template. Read all and replace the placeholders with the correct values.

.. code-block:: markdown

    <!-- CASE SENSITIVE replace the following strings in the template -->
    <!-- 1. Replace "20.1.9" with the version number e.g. "12.2.4" -->
    <!-- Replace "20.1.8" with the previous version number e.g. "12.2.3" -->
    <!-- 2. Replace "stable30" with the LibreSign minor branch name e.g. "stable22" -->
    <!-- 3. Replace "20" with the LibreSign version e.g. "12" for "stable22" -->
    <!-- 4. Replace CASE SENSITIVE "XX" with the Nextcloud stable branch number e.g. "22" for "stable22" -->
    ## 💺 Preparation
    - [ ] Check there are no pending backports:
    - [ ] https://github.com/LibreSign/libresign/labels/backport-request
    - [ ] Check all milestones don't have priority issues still open
        <!-- Add above the link of stables that will be involved in this release process -->
        <!-- Get branches/versions to release from https://github.com/LibreSign/libresign/milestones -->
        - [ ] https://github.com/LibreSign/libresign/milestone/318
        - [ ] https://github.com/LibreSign/libresign/milestone/319
    - [ ] Check there are no important PRs open against the branch
        <!-- Add above the link with correct base branch of stables that will be involved in this release process -->
        <!-- Get branches/versions to release from https://github.com/LibreSign/libresign/milestones -->
        - [ ] https://github.com/LibreSign/libresign/pulls?q=is%3Apr+is%3Aopen+base%3Astable30
        - [ ] https://github.com/LibreSign/libresign/pulls?q=is%3Apr+is%3Aopen+base%3Astable31
    - [ ] List all PRs that will be added to the changelog
        <!-- List the content to add at the pull request using the follow command and pay attention to replace the milestone name and the version number:

            gh pr list --repo LibreSign/libresign --state merged -S "milestone:\"Next Patch (30)\" " -L 100
        -->
    - [ ] Create a PR against main branch at the `CHANGELOG.md` file with the changelog of all milestones that are subject to the release. Look the pattern used in the file and follow it.
        <!-- name suggestions to commit and pull request:
            chore(release): Changelog for 20.1.9
            chore(release): Changelog for 20.1.9 and 20.1.8
        -->
        - [ ] <!-- Add link to PR here -->
    - [ ] Merge the PR
    <!-- Duplicate the follow steps for each version that will be released, starting with the oldest version. -->
    <!-- Pay attention to start with the **oldest** version here, so the appstore and github releases show the newest version as "Last release" and them. -->
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
    - [ ] Create a new release
        - [ ] Prepare a (pre-)release in https://github.com/LibreSign/libresign/releases/new?tag=v20.1.9&target=stable30
        - [ ] Make sure that chosen tag is v20.1.9, target is stable30, and previous tag is v20.1.8
        - [ ] Add the content of respective `CHANGELOG.md` section from merged PR
        - [ ] Use the **Generate release notes** button and wrap the output result into
        ```
        ## What's Changed
        <!-- Add the content of the changelog section here -->

        Milestone: [v20.1.9]<!-- Add the link to the closed milestone here -->
        **Full Changelog**: https://github.com/LibreSign/libresign/compare/v20.1.9...v20.1.8
    - [ ] Publish release
    - [ ] Check that the GitHub Action started: https://github.com/LibreSign/libresign/actions
    - [ ] Ensure that the GitHub Action finished successfully: https://github.com/LibreSign/libresign/actions
    - [ ] Post the changelog in [💬 LibreSign team public 👥](https://t.me/LibreSign)
