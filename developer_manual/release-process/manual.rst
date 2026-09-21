.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Manual procedure and troubleshooting
====================================

The automated workflow is the normal path. Manual commands are useful for diagnostics and recovery, but they must follow the same policy.

Read-only planning
------------------

Download the verified ``release-tool.phar`` version used by ``LibreCodeCoop/github-workflows`` and its SHA-256 file, verify the checksum, then run:

.. code-block:: bash

   php release-tool.phar config:validate --config .nextcloud-release.yml --root . --json
   php release-tool.phar release:plan --config .nextcloud-release.yml --root . --branch stableXX --channel final --mode normal --json

The plan output should identify the previous reachable release tag, exact planning SHA, proposed version, target per-major changelog, milestone and blockers.

Manual equivalent
-----------------

1. Identify the previous reachable release tag from the selected branch.
2. Inspect release activity since that tag and apply the same patch/minor/channel policy.
3. Check open backport blockers for that stable line.
4. Update only the selected per-major changelog and configured version files.
5. Ensure the package build copies that per-major changelog to package-root ``CHANGELOG.md``.
6. Merge the release PR using an authorized maintainer.
7. Revalidate the merged SHA and release-file digests.
8. Rotate the milestone using the same configured policy.
9. Create a GitHub Release draft for the finalized SHA and released changelog section.
10. Publish it and let the existing publisher build/sign/upload the package.
11. Verify publisher success, artifact identity/content and App Store visibility.
12. Synchronize the released section to public documentation only after publication verification.

Recovery rules
--------------

* If planning is stale because the branch advanced, generate a new plan. Do not reuse the stale one.
* If the generated release PR contains files outside the allowed release set, stop and investigate.
* If the release branch advances after the release PR merge, do not create the draft from the old finalized state.
* If publication fails, fix the publisher problem and rerun verification. Do not reinterpret or regenerate release notes.
* If a tag/release points to the wrong commit, repair the GitHub Release/tag identity before publication verification can succeed.
* For security mode, never put advisory-private details in workflow inputs, changelog text, artifacts or public documentation.
