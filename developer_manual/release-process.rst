Release process
===============

The normal LibreSign release process is driven by GitHub Actions.

The goal is to keep release preparation reviewable while making the technical
steps deterministic and reproducible. A normal release should not require local
release commands.

Normal release flow
-------------------

1. Open **Actions -> Prepare release PR**.
2. Select the target stable branch and keep ``dry_run`` enabled for the first
   run.
3. Review the generated plan: pull requests, version bump, changelog, target
   commit, and milestone.
4. Run **Prepare release PR** again with ``dry_run`` disabled when the plan is
   correct.
5. Review and merge the generated release preparation pull request.
6. Wait for **Finalize release preparation** to update the milestone state.
7. Open **Actions -> Prepare stable release** and select the same stable branch.
8. Review the generated GitHub Release draft.
9. Review the release title, changelog, description, target commit, and Full
   Changelog link.
10. Click **Publish release** when the draft is ready.
11. Wait for **Build, sign and publish App Store release** to finish.
12. Confirm the GitHub release asset and the version in the Nextcloud App Store.

Prepare release PR
------------------

**Prepare release PR** analyzes commits since the previous stable release and
resolves the pull requests associated with those commits.

It then:

- verifies that the stable branch version still matches its latest release tag;
- blocks preparation while ``backport-request`` pull requests are pending;
- verifies that the matching ``Next Patch (XX)`` milestone exists;
- classifies the release as patch or minor;
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

- ``MAJOR`` aligns with the supported Nextcloud Server version.
- ``MINOR`` is used when the release contains features.
- ``PATCH`` is used for fixes and maintenance changes.

Stable release preparation never infers a major bump. A ``major`` label or a
breaking conventional-commit marker causes preparation to fail because major
versions are part of the new stable branch lifecycle.

The generated release files must contain the same version in:

- :code:`appinfo/info.xml`;
- :code:`package.json`;
- :code:`package-lock.json`.

Changelog
---------

The changelog is generated from pull requests associated with commits since the
previous release tag.

Release planning ignores ``skip-changelog`` entries and dependency-bot pull
requests. Dependency changes are collapsed into a single changelog item and
translation updates are represented as a single user-facing entry.

The generated changelog remains reviewable in the release preparation pull
request before publication.

Milestones
----------

Each stable branch maps to its ``Next Patch (XX)`` milestone.

After the generated release pull request is merged, **Finalize release
preparation**:

1. verifies that the release pull request changed only the allowed release
   files;
2. renames ``Next Patch (XX)`` to the released version;
3. creates the next ``Next Patch (XX)`` milestone when the stable branch remains
   supported;
4. moves remaining open issues and pull requests to the new milestone;
5. closes the release milestone.

For the final release of a stable branch, select ``final_stable_release`` in
**Prepare release PR**. No follow-up patch milestone is created and
finalization fails if the release milestone still contains open items.

Prepare stable release
----------------------

**Prepare stable release** runs after the release preparation pull request has
been merged and its milestone has been finalized.

It verifies version consistency and the changelog, performs the frontend and
App Store package preflight, and creates or updates a GitHub Release draft only
after those checks pass.

The draft is pinned to the exact commit that passed preflight. Re-running the
workflow updates the same draft instead of creating a competing release.

Publishing
----------

A maintainer reviews the draft and explicitly clicks **Publish release**.

Publishing triggers **Build, sign and publish App Store release**, which is
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

Release automation tests
------------------------

Release planning rules are implemented outside workflow YAML so they can be
tested independently.

The repository validates release automation with:

- PHPUnit tests for version bumping, changelog categories, exclusions, and
  stable-release rules;
- ``actionlint`` and ShellCheck for release workflow syntax and embedded shell;
- ``dry_run`` in **Prepare release PR** for integration checks against real
  repository history without changing GitHub state.

Run the planner tests locally with:

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
4. rerun **Prepare stable release** from the corrected branch state.

Do not rerun a workflow tied to an obsolete tag. The tag must point to the
corrected commit.

Nightly releases
----------------

Nightly releases are independent from stable publication.

Future automation
-----------------

After this process has been validated through real release cycles, **Prepare
release PR** can gain a weekly schedule. Scheduled execution should create or
update release preparation pull requests only; final publication remains an
explicit maintainer action.

.. code-block:: text

   Prepare release PR
           |
         review
           |
         merge
           |
   Finalize release preparation
           |
   Prepare stable release
           |
   GitHub Release draft
           |
      human review
           |
     Publish release
           |
   Build, sign and publish App Store release
