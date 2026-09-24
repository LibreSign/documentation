.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Release process
===============

The normal LibreSign release path is driven from the **Prepare release** GitHub Actions workflow.

Release policy, contracts, the PHP runtime, and the three public lifecycle Actions live in ``LibreCodeCoop/release-tool``. LibreCode's managed workflow catalog and synchronization helper live in ``LibreCodeCoop/.github``. ``LibreSign/libresign`` carries the consumer configuration and repository-specific packaging rules.

Maintainer journey
------------------

1. Run **Prepare release** manually.
2. Select the stable branch to release.
3. Optionally select an exact ref, override the proposed version, choose a prerelease channel, or explicitly ignore a matching open backport blocker.
4. Review the generated release preparation PR.
5. Merge that PR using an account that satisfies the configured merge permission.
6. Review the generated GitHub Release draft.
7. Publish the draft.
8. The existing packaging/signing/App Store workflow runs.
9. Publication verification confirms release identity, publisher run, artifact and App Store visibility.
10. The released changelog remains in ``LibreSign/libresign`` as the single canonical release-history source.

There are only two semantic human release gates: merging the generated release PR and publishing the generated GitHub Release draft.

.. toctree::
   :maxdepth: 2

   release-process/configuration
   release-process/preparing
   release-process/versioning
   release-process/milestones
   release-process/publishing
   release-process/manual
