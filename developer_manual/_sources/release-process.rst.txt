Release process
===============

Resuming the steps:

1. Identify the next version number of all releases.
2. Collect and validate PRs from the commits since the previous release.
3. Create the changelog for all branches that will be released.
    Write entries in :code:`CHANGELOG.md` on :code:`main`, then backport to stable branches.
4. Verify version consistency across configuration files (:code:`appinfo/info.xml`, :code:`package.json`, :code:`package-lock.json`).
5. Apply the required release changes in the codebase.

    .. note::
        You can use the :code:`[skip ci]` tag in the commit message to skip the CI checks for the backport PRs to make the process faster.

    .. important::

        Release PRs must stay strictly scoped to the release itself.
        Do not mix release automation, workflow, Release Drafter, refactor,
        or any other maintenance changes in the same PR.
        The allowed changes in a release PR are the changelog section and the
        version bumps required for that release.

6. Open a pull request to :code:`main` with the release preparation changes.
7. After CI passes and the PR is merged, backport the changes to the stable branches to be released.
8. After the backport PRs are merged, perform a smoke test on all supported browsers.
9. Create the GitHub release for the oldest stable version in the cycle first.
10. Verify the GitHub Action for that release finished successfully and wait until the version is visible in the Nextcloud App Store.
11. Repeat the same publication and validation flow for the next newer stable version, one by one.
12. Announce the release in the Telegram channel.

.. important::

    When publishing more than one stable release in the same cycle, never
    create the newer tag before the older release is fully published.
    The required order is:

    1. publish the oldest stable release
    2. wait for the GitHub Action to succeed
    3. confirm the version is visible on https://apps.nextcloud.com/apps/libresign/
    4. only then publish the next newer stable release

.. note::

    If you automate release creation with :code:`gh release create` or
    :code:`gh release edit`, prefer loading the notes from a file instead of
    inlining multiline markdown in the shell command. This avoids escaping
    issues in backticks, parentheses, and links.

Version numbers
---------------

- The version number follows **MAJOR.MINOR.PATCH**.
- ``MAJOR`` aligns with the supported Nextcloud Server version.
- ``MINOR`` is used for LibreSign feature releases.
- ``PATCH`` is used for bug fixes or small improvements.

Milestones
----------

Every PR must be assigned to a milestone.

- PRs targeting :code:`main` must use the current **major milestone** for the
    Nextcloud server version supported by :code:`appinfo/info.xml` on :code:`main`.
- PRs targeting stable branches must use the corresponding **patch milestone**
    for that server major, using the branch :code:`appinfo/info.xml` version as the
    source of truth.

Examples with the current branch model:

- :code:`main` with :code:`14.0.0-dev.*` maps to :code:`Next Major (34)`.
- :code:`stable33` maps to :code:`Next Patch (33)`.
- :code:`stable32` maps to :code:`Next Patch (32)`.

.. important::

        A PR without milestone is not ready for review or merge.
        Before opening or updating a release PR, confirm the milestone is correct.

Identifying the previous release tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before starting the changelog, you need to identify the previous release tag for each stable branch:

.. code-block:: bash

    # List all tags sorted by version (newest first)
    git tag -l "v*" --sort=-version:refname | head -20

    # Or find the last tag for a specific branch
    git describe --tags --abbrev=0 stable22

This tag will be used in the commit log range when collecting PRs (e.g., ``v12.2.0..stable22``).

.. important::

    The tag range is only the **raw input** for the changelog. On stable branches,
    it is possible to merge backports of already published hotfixes after the tag
    was created. Because of that, always cross-check the raw compare output with
    the existing published sections in :code:`CHANGELOG.md` and exclude entries
    that already shipped in previous patch releases.

Collecting PRs and changelog entries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each release, collect merged PRs since the previous release tag.

**Method 1: git log (recommended)**

.. code-block:: bash

    # Collect all merge commits from previous tag to stable branch
    git log --oneline --merges --first-parent <previous-tag>..stable<XX>

    # Example for stable33 since v13.0.0
    git log --oneline --merges --first-parent v13.0.0..stable33

    # Output format: merge commits with PR references (Merge pull request #XXXX)

To get PR numbers with backport titles directly (faster changelog drafting):

.. code-block:: bash

        # Example: from merge commit of previous release to stable branch head
        for c in $(git rev-list --reverse --merges --first-parent <release-merge-commit>..stable<XX>); do
            pr=$(git show -s --format='%s' "$c" | sed -E 's/^Merge pull request #([0-9]+).*/\1/')
            title=$(git show -s --format='%b' "$c" | head -n 1)
            printf '%s|%s\n' "$pr" "$title"
        done

**Method 2: GitHub CLI (gh)**

.. code-block:: bash

    # List merged PRs between two tags/branches
    gh pr list -B stable33 -S "merged:>$(git log -1 --format=%ai <previous-tag>)" --json number,title,mergedAt

    # Or search for PRs merged after a specific date
    gh pr list -B stable33 --state merged --search "merged:>=2025-02-01" --json number,title

To list milestones with current GitHub CLI versions, prefer the API endpoint:

.. code-block:: bash

    gh api repos/LibreSign/libresign/milestones?state=all\&per_page=100

**Important: Mapping backports to original PRs**

When collecting PR data for a release, you may encounter backport PRs. These should be mapped to the original PR for proper documentation:

- **Backport PRs** are created with a naming pattern like: ``Backport: fix: ...`` or on a backport branch
- Look at the PR description or linked issues to find the **original PR number**
- In the changelog, use the **backport PR number** (specific to the branch) but reference both

Also exclude PRs that are only part of the release process itself, for example:

- release-drafter alignment or release housekeeping PRs
- follow-up lockfile repair PRs whose only purpose is to fix the backport branch
- hotfix PRs that already generated a published patch release section

Example for handling backports:

- Original PR on main: #6944 "fix: docmdp first signature allow"
- Backport PR on stable33: #6944 (same in this case) or #6945 on stable32
- In changelog, list: ``#6944 fix: docmdp first signature allow`` (use the stable branch specific PR number)

Defining release version numbers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to Milestones in the LibreSign repository:

    https://github.com/LibreSign/libresign/milestones

2. Identify what is the next patch version to be released.
3. Look the closed items to identify if we have new features,

    1. If is a major release, increment with :code:`1` the :code:`MAJOR` version and reset :code:`MINOR` and :code:`PATCH`.

    .. note::
        We only create a major release when is created a new stable branch for a new Nextcloud major version.

    2. To new features, increment with :code:`1` the ``MINOR`` version and reset ``PATCH`` to ``0``.
    3. To bug fixes, increment the ``PATCH`` version.

.. note::

    The Release Drafter workflow can help by pre-filling the draft version from
    the stable branch history, but the final version decision is still validated
    during the changelog curation step.

Stable branches
---------------

Each **stable branch** in LibreSign corresponds to a specific Nextcloud **MAJOR** version.

For example: ``stable21`` is compatible with Nextcloud 21.

Changelog format
----------------

The :code:`CHANGELOG.md` file uses a specific format to document releases. Follow this pattern:

.. code-block:: markdown

    ## 13.2.4 - 2026-04-25
    ### Changed
    - Update translations

    ### Fixes
    - harden signed file validation handling [#7601](https://github.com/LibreSign/libresign/pull/7601)
    - simplify signer tsa and crl validation messaging [#7614](https://github.com/LibreSign/libresign/pull/7614)

    ## 12.4.4 - 2026-04-26
    ### Changed
    - Update translations

    ### Fixes
    - harden signed file validation handling [#7600](https://github.com/LibreSign/libresign/pull/7600)
    - simplify signer tsa and crl validation messaging [#7613](https://github.com/LibreSign/libresign/pull/7613)

**Key format rules:**

- Use semantic versioning: ``MAJOR.MINOR.PATCH``
- Do not include stable branch names in the changelog heading.
- Add the release date: ``YYYY-MM-DD``
- Group changes by type: ``Added``, ``Changed``, ``Fixed``, ``Removed``, etc.
- List PR number with hash: ``#XXXX`` followed by a colon and description
- Use lowercase for descriptions (following conventional commits)
- For backport releases, use the **stable branch-specific PR number** even if it differs from the original
- Always add new entries at the top (most recent first)
- Prefer user-visible changes in the release notes; keep purely internal test/refactor/dependency entries only when they are relevant to support or compatibility.
- Collapse dependency updates into a single changelog item (e.g. ``Bump dependencies``) instead of listing each maintenance PR.
- Always include ``Update translations`` in the release changelog.
- Do not include Dependabot-only commits in the final changelog section.
- Treat GitHub generated release notes as a draft source only; rewrite the final section so it tells the release story instead of listing every backport PR individually.

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
        - [ ] Save this as a draft
    - [ ] Go to the main branch, pull the latest changes and create a new branch called `chore/changelog`
    - [ ] Add the changelog entries to the `CHANGELOG.md` file, following the pattern used in the file.
    - [ ] Make this to all releases that will be done in this process.
    - [ ] Assign the PR to the correct milestone
        - [ ] `main` uses the current `Next Major (XX)` milestone from `appinfo/info.xml`
        - [ ] each stable branch uses its matching `Next Patch (XX)` milestone
    - [ ] Create a PR against `main` branch at the `CHANGELOG.md` file with the changelog of all milestones that are subject to the release. Look the pattern used in the file and follow it.
        The **last commit** of every release PR must include :code:`[skip ci]`.
        This keeps the release train moving and avoids waiting for a full CI cycle
        right before the tag and publication steps.
        Do not use the release PR to change anything beyond changelog and version bumps.
        ```
        name suggestions to commit and pull request:
        chore(release): Changelog for 20.1.9
        chore(release): Changelog for 20.1.9 and 20.1.8
        ```
    - [ ] Merge the PR
    - [ ] **Version consistency check** (before backporting):
        - [ ] Verify :code:`appinfo/info.xml` has the correct version
        - [ ] Run: :code:`npm version --no-git-tag-version $(xmllint --xpath '/info/version/text()' appinfo/info.xml)`
        - [ ] Verify :code:`package.json` and :code:`package-lock.json` were updated correctly
        - [ ] Commit these changes together with the changelog PR if needed
    <!-- Duplicate the follow steps for each version that will be released, starting with the oldest version. -->
    <!-- Pay attention to start with the **oldest** version here, so the appstore and github releases show the newest version as "Last release" and them. -->
    <!-- Do not publish the newer release until the older release workflow is fully finished and validated in the App Store. -->
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
    - [ ] Make sure the final commit of the PR uses :code:`[skip ci]`
    - [ ] Confirm the PR only changes release files: `CHANGELOG.md`, `appinfo/info.xml`, `package.json`, `package-lock.json`
    - [ ] Assign the PR to the matching `Next Patch (XX)` milestone of the stable branch
    - [ ] Merge the backport
    - [ ] **Smoke test** - Sign a document in each supported browser:
        - [ ] Chrome (latest version)
        - [ ] Edge (latest version)
        - [ ] Firefox (latest version)
        - [ ] Safari (latest version)
        - [ ] Verify: Request signing, Add signature, Validate signature in AppStore/File Manager
    - [ ] **Final validation checks**:
        - [ ] Verify version number in :code:`appinfo/info.xml` matches release tag
        - [ ] Verify changelog in :code:`CHANGELOG.md` is correct and properly formatted
        - [ ] Check GitHub Actions status for the merged PR
        - [ ] Review AppStore entries for the stable branch (if available)
    - [ ] Create the new milestone
        - [ ] Rename milestone `💚 Next Patch (XX)` to `v20.1.9` in https://github.com/LibreSign/libresign/milestones
        - [ ] Confirm the milestone was correctly renamed before writing the release body:
        ```sh
        gh api 'repos/LibreSign/libresign/milestones?state=open' --jq '.[] | "\(.number) \(.title)"'
        ```
        Unless last release of the stable branch:
        - [ ] Create a follow up milestone for `💚 Next Patch (XX)` (Due date in ~4 weeks, ~4 days for beta/RC)
        - [ ] Move all open issues from milestone `v20.1.9` to `💚 Next Patch (XX)`: https://github.com/LibreSign/libresign/issues?q=is%3Aissue%20state%3Aopen%20milestone%3Av20.1.9
        - [ ] Move all open PRs from milestone `v20.1.9` to `💚 Next Patch (XX)`: https://github.com/LibreSign/libresign/issues?q=is%3Apr%20state%3Aopen%20milestone%3Av20.1.9
        - [ ] Close the `v20.1.9` milestone
    - [ ] Archive all issues and PRs that were merged in this release
        - [ ] https://github.com/orgs/LibreSign/projects/2/views/4
    - [ ] Create a new release
        - [ ] Confirm the exact commit that will be tagged is the current head of the stable branch:
        ```sh
        git ls-remote origin refs/heads/stable20 | awk '{print $1}'
        ```
        - [ ] Prepare a (pre-)release in https://github.com/LibreSign/libresign/releases/new?tag=v20.1.9&target=stable20
        - [ ] Make sure that chosen tag is v20.1.9, target is stable20, and previous tag is v20.1.8
        - [ ] Add the content of respective `CHANGELOG.md` section from merged PR
        - [ ] In the release body, use the final closed milestone name `v20.1.9` after the milestone rename, never the previous `Next Patch (XX)` name
        - [ ] Use the **Generate release notes** button and wrap the output result into
        ```
        ## What's Changed
        <!-- Add the content of the changelog section here -->

        Milestone: [v20.1.9](<!-- Add the link to the closed milestone here -->?closed=1)
        **Full Changelog**: https://github.com/LibreSign/libresign/compare/v20.1.8...v20.1.9
        ```
    - [ ] Keep `**Full Changelog**` as the last line of the release description.
    - [ ] Publish release
    - [ ] Check that the GitHub Action started: https://github.com/LibreSign/libresign/actions
    - [ ] Ensure that the GitHub Action finished successfully: https://github.com/LibreSign/libresign/actions
    - [ ] **Post-release validation**:
        - [ ] Verify the new version appears in AppStore: https://apps.nextcloud.com/apps/libresign
        - [ ] Check that the package was properly built and published
        - [ ] Verify changelog is visible on GitHub Releases page
        - [ ] Confirm no errors in GitHub Actions logs
    - [ ] If a publication fix is merged after the release tag is created, do not only rerun the old workflow
        - [ ] Delete the GitHub release and the tag
        - [ ] Recreate the tag from the updated stable branch head
        - [ ] Recreate the GitHub release so the workflow checks out the corrected commit
    - [ ] If there is another release to publish in the same cycle, stop here and wait for all checks above to be green before creating the next release tag
    - [ ] Only after the older release is visible and correct on https://apps.nextcloud.com/apps/libresign/, publish the next newer release
    - [ ] Post the changelog in [💬 LibreSign team public 👥](https://t.me/LibreSign)
