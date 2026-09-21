Release process
===============

The normal LibreSign release process is driven by GitHub Actions.

The goal is to keep release preparation reviewable while making the technical
steps deterministic and reproducible. A normal release should not require local
release commands.

Normal release flow
-------------------

1. Open **Actions -> Release 10 - Prepare release PR**.
2. Select the target stable branch and keep ``dry_run`` enabled for the first
   run.
3. Review the generated plan: pull requests, version bump, changelog, target
   commit, and milestone.
4. Run **Release 10 - Prepare release PR** again with ``dry_run`` disabled when the plan is
   correct.
5. Review and merge the generated release preparation pull request.
6. Wait for **Release 20 - Finalize preparation** to update the milestone state.
7. Open **Actions -> Release 30 - Prepare draft** and select the same stable branch.
8. Review the generated GitHub Release draft.
9. Review the release title, changelog, description, target commit, and Full
   Changelog link.
10. Click **Publish release** when the draft is ready.
11. Wait for **Release 40 - Build, sign and publish App Store** to finish.
12. Confirm the GitHub release asset and the version in the Nextcloud App Store.

Release 10 - Prepare release PR
-------------------------------

**Release 10 - Prepare release PR** is started manually for one selected stable
branch. It analyzes repository activity since the previous stable release and
resolves the pull requests associated with that release range.

It then:

- verifies the selected stable branch and release state;
- blocks preparation when an open backport pull request is still pending for
  that stable branch, unless the maintainer explicitly overrides that blocker;
- verifies that the matching ``Next Patch (XX)`` milestone exists;
- classifies the release from merged pull request titles, using the same
  Conventional Commit convention required by LibreSign;
- generates the changelog section;
- updates :code:`appinfo/info.xml`, :code:`package.json`, and
  :code:`package-lock.json`;
- creates or updates a scoped release preparation pull request.

The workflow defaults to ``dry_run``. A dry run analyzes the real repository
state but does not create a branch or pull request and does not alter
milestones or releases.

The generated release pull request is limited to:

- :code:`CHANGELOG.md`;
- :code:`appinfo/info.xml`;
- :code:`package.json`;
- :code:`package-lock.json`.

Version numbers
---------------

LibreSign follows :code:`MAJOR.MINOR.PATCH`.

- ``MAJOR`` changes when a new LibreSign release line is created for a new
  Nextcloud/framework generation.
- ``MINOR`` is used when at least one merged pull request included in the
  release has a ``feat`` Conventional Commit title.
- ``PATCH`` is used when the release has new releasable activity but no
  feature pull request. This includes bug fixes, translations, dependency
  updates, documentation, tests, refactors, CI and other maintenance changes.

The pull request title is the release-level classification source. Internal
commits inside a pull request do not change the release type. For example, a
``feat:`` commit inside a pull request titled ``fix:`` does not promote the
release to a minor version.

A feature exceptionally backported to a released stable branch still promotes
that stable line to the next minor version.

Dependency version semantics do not propagate to LibreSign. A dependency
changing from 1.x to 2.x remains a LibreSign patch-level change unless the
LibreSign pull request itself is a feature.

Stable release preparation never infers a major bump from Conventional
Commits. Major releases belong to the new stable branch lifecycle. When a
stable branch has no previous release, the version declared by
``appinfo/info.xml`` identifies the new release line.

Development and prerelease suffixes such as ``-dev``, ``-alpha``,
``-beta`` or ``-rc`` may exist before the first final release. Release
preparation must normalize that prerelease value to the intended final semantic
version instead of treating the branch as invalid.

The generated release files must contain the same version in:

- :code:`appinfo/info.xml`;
- :code:`package.json`;
- :code:`package-lock.json`.

Changelog
---------

The changelog is generated primarily from merged pull requests associated with
the selected release range. Pull request titles are used for Conventional
Commit classification; internal commits inside a pull request are not used to
promote the release type.

Release planning ignores ``skip-changelog`` entries. Dependency-bot pull
requests are not listed one by one: dependency changes are collapsed into a
single changelog item.

Translations are a special case because translation syncs can be direct commits
without a pull request. Release preparation detects translation activity
separately and adds one user-facing translation update entry.

A release containing only translations, dependencies or other maintenance work
is valid and uses a patch version.

The generated changelog remains reviewable in the release preparation pull
request before publication.

Milestones
----------

Each stable branch maps to its ``Next Patch (XX)`` milestone.

After the generated release pull request is merged, **Release 20 - Finalize
preparation**:

1. verifies that the release pull request changed only the allowed release
   files;
2. renames ``Next Patch (XX)`` to the released version;
3. creates the next ``Next Patch (XX)`` milestone when the stable branch remains
   supported;
4. moves remaining open issues and pull requests to the new milestone;
5. closes the release milestone.

Milestones are rotated for every normal patch-line release. For the final
release of a stable branch, the maintainer explicitly selects that no follow-up
``Next Patch (XX)`` milestone should be created.

The Nextcloud Server Maintenance and Release Schedule is the normal source for
stable lifecycle/EOL information. The workflow does not decide EOL
automatically because LibreSign may intentionally maintain a line longer, for
example under an enterprise support commitment.

Release 30 - Prepare draft
--------------------------

**Release 30 - Prepare draft** runs after the release preparation pull request has
been merged and its milestone has been finalized.

It verifies version consistency and the changelog, performs the frontend and
App Store package preflight, and creates or updates a GitHub Release draft only
after those checks pass.

The draft is pinned to the exact commit that passed preflight. Re-running the
workflow updates the same draft instead of creating a competing release.

Publishing
----------

A maintainer reviews the draft and explicitly clicks **Publish release**.

Publishing triggers **Release 40 - Build, sign and publish App Store**, which is
derived from the Nextcloud organization workflow. It performs the final build,
signs the package, attaches the release asset, and publishes the version to the
Nextcloud App Store.

Multiple stable releases
------------------------

When several stable branches are released in the same cycle, process the oldest
supported stable first. Do not publish the next stable release until the
previous one has completed successfully and is visible in the App Store.

Security releases
-----------------

Security advisories should be published only after all fixed versions referenced
by the advisory are publicly available.

Release automation implementation
---------------------------------

The release workflows are intentionally thin. Release-specific rules and GitHub
operations live in :code:`scripts/release/` and are exposed through
:code:`scripts/release/release.php`.

The workflow files are sequenced by name so their order is visible in GitHub and
IDEs:

.. code-block:: text

   release-00-tests.yml
   release-10-prepare-pr.yml
   release-20-finalize-preparation.yml
   release-30-prepare-draft.yml
   release-40-publish-appstore.yml

The numeric gaps are intentional, allowing future stages to be inserted without
renaming every workflow.

The App Store publisher remains derived from the Nextcloud organization
template. The release CLI owns LibreSign-specific release policy and state
transitions, while GitHub Actions primarily orchestrates checked-in commands and
third-party actions.

Release automation tests
------------------------

Release planning rules are implemented outside workflow YAML so they can be
tested independently.

The repository validates the release CLI and workflow orchestration with:

- PHPUnit tests for version bumping, changelog categories, exclusions, release
  file mutation, Git/GitHub command composition, draft handling, and milestone
  rules;
- ``actionlint`` and ShellCheck for release workflow syntax and embedded shell;
- ``dry_run`` in **Release 10 - Prepare release PR** for integration checks against real
  repository history without changing GitHub state.

Run the release automation tests locally with:

.. code-block:: bash

   composer install --working-dir=vendor-bin/phpunit
   composer test:release

A local ``act`` run can help while developing workflow orchestration, but it is
not treated as authoritative because it does not completely reproduce GitHub
events, permissions, or API behavior.

Recovery and exceptional releases
---------------------------------

If a release must be recreated after a publication fix:

1. delete the incorrect GitHub release;
2. delete the incorrect tag;
3. confirm the exact stable branch commit to publish;
4. rerun **Release 30 - Prepare draft** from the corrected branch state.

Do not rerun a workflow tied to an obsolete tag. The tag must point to the
corrected commit.

Nightly releases
----------------

Nightly releases are independent from stable publication.

Future automation
-----------------

After this process has been validated through real release cycles, **Release 10 -
Prepare release PR** can gain a weekly schedule. Scheduled execution should create or
update release preparation pull requests only; final publication remains an
explicit maintainer action.

.. code-block:: text

   Release 10 - Prepare release PR
           |
         review
           |
         merge
           |
   Release 20 - Finalize preparation
           |
   Release 30 - Prepare draft
           |
   GitHub Release draft
           |
      human review
           |
     Publish release
           |
   Release 40 - Build, sign and publish App Store
