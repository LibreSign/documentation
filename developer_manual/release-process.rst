.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Release process
===============

The normal LibreSign release path is driven from the **Prepare release** GitHub Actions workflow.

The reusable policy and contracts live in ``LibreCodeCoop/release-tool`` and orchestration lives in ``LibreCodeCoop/github-workflows``. ``LibreSign/libresign`` carries the consumer configuration and repository-specific packaging rules.

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
10. After verification succeeds, release history is synchronized to this documentation repository through a generated PR.

There are only two semantic human release gates: merging the generated release PR and publishing the generated GitHub Release draft.

.. toctree::
   :maxdepth: 2

   release-process/preparing
   release-process/versioning
   release-process/milestones
   release-process/publishing
   release-process/manual
