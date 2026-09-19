Release process
===============

The normal LibreSign release process is driven from GitHub Actions.

The goal is to keep release preparation reviewable while making publication a
single, reproducible operation. A normal release should not require local
commands.

Normal release flow
-------------------

1. Review the target stable branch and its milestone.
2. Confirm all intended backports are merged.
3. Prepare the release files in the stable branch:
   :code:`CHANGELOG.md`, :code:`appinfo/info.xml`,
   :code:`package.json`, and :code:`package-lock.json`.
4. Merge the release preparation pull request.
5. Open **Actions -> Prepare stable release** in the LibreSign repository.
6. Run the workflow and provide the target stable branch, for example
   :code:`stable35`.
7. Wait for the workflow to finish and review the generated draft release.
8. Review the release title, changelog, description, target commit, and Full Changelog link.
9. Click **Publish release** when the draft is ready.
10. Wait for **Build, sign and publish App Store release** to finish.
11. Confirm the GitHub release asset and the version in the Nextcloud App Store.

The Prepare stable release workflow performs the release checks before creating a draft.
It validates the version files and changelog, builds the frontend, and creates
and verifies the App Store package. Only after these checks pass does it create
a draft GitHub release for human review.

Publishing the draft triggers **Build, sign and publish App Store release**,
which performs the final build, signs the package, attaches the release asset,
and publishes it to the Nextcloud App Store.

.. important::

   A failed preflight build or package verification must not create a release draft.
   The release remains unpublished until a maintainer explicitly reviews the draft
   and clicks **Publish release**.

Version numbers
---------------

LibreSign follows :code:`MAJOR.MINOR.PATCH`.

- ``MAJOR`` aligns with the supported Nextcloud Server version.
- ``MINOR`` is incremented when a release contains user-facing features.
- ``PATCH`` is incremented for fixes and small improvements.

The Prepare stable release workflow uses the version already prepared in the stable branch.
The following files must contain the same version before publication:

- :code:`appinfo/info.xml`
- :code:`package.json`
- :code:`package-lock.json`

Development, alpha, beta, and release-candidate versions are rejected by the
normal release workflow.

Release preparation pull request
--------------------------------

Release preparation remains reviewable through a pull request.

The release pull request must stay strictly scoped to:

- the new :code:`CHANGELOG.md` section;
- the version in :code:`appinfo/info.xml`;
- the version in :code:`package.json`;
- the version in :code:`package-lock.json`.

Do not mix release automation, workflow refactoring, dependency maintenance, or
unrelated fixes into a release preparation pull request.

Changelog
---------

The changelog is the source used for the GitHub release description.

Each release section must follow this format:

.. code-block:: markdown

   ## 15.0.1 - 2026-09-21

   ### Fixed

   - fix signing flow validation [#0000](https://github.com/LibreSign/libresign/pull/0000)

Keep the newest release first.

Prefer user-visible changes. Pure test, refactor, or dependency maintenance
entries should only be included when relevant to users, compatibility, or
support.

Milestones
----------

Every pull request must have the correct milestone before merge.

- PRs targeting :code:`main` use the current ``Next Major (XX)`` milestone.
- PRs targeting a stable branch use the corresponding ``Next Patch (XX)``
  milestone.

Before preparing a release:

1. Review open issues and pull requests in the milestone.
2. Move work that is not part of the release to the next milestone.
3. Rename the release milestone to the final version.
4. Close the milestone after the release contents are final.
5. Create the next patch milestone when the stable branch remains supported.

Multiple stable releases
------------------------

When publishing multiple stable branches in the same release cycle, publish the
oldest supported stable first.

For each branch:

1. run **Prepare stable release**;
2. review the generated draft;
3. publish the draft;
4. wait for **Build, sign and publish App Store release** to succeed;
5. confirm the release in the Nextcloud App Store;
6. only then continue with the next newer stable branch.

Security releases
-----------------

For security releases, publish security advisories only after all fixed
versions referenced by the advisory are publicly available.

Recovery and exceptional releases
---------------------------------

The manual process is reserved for exceptional situations.

If a release must be recreated after a publication fix:

1. delete the incorrect GitHub release;
2. delete the incorrect tag;
3. confirm the exact stable branch commit to publish;
4. rerun **Prepare stable release** from the corrected branch state.

Do not only rerun a workflow tied to an obsolete tag. The tag must point to the
corrected commit.

For an exceptional release that intentionally targets a specific commit instead
of the current stable branch head, document the reason and verify that the
selected commit contains the complete release preparation.

Nightly releases
----------------

Nightly releases are independent from stable publication. They may share build
and packaging implementation with stable releases, but must never be treated as
a stable release.

Future automation
-----------------

The next automation stage is release preparation.

.. code-block:: text

   scheduled or manual preparation
               |
               v
      release preparation PR
               |
            review
               |
             merge
               |
               v
      Actions -> Prepare stable release
               |
               v
        GitHub release draft
               |
          human review
               |
        Publish release
               |
               v
     GitHub + Nextcloud App Store

Once release preparation is reliably automated, a weekly schedule may create or
update release preparation pull requests for supported stable branches. Final
publication should remain explicit until the automated process has been
validated through multiple release cycles.
