.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

Updating vendored dependencies
==============================

LibreSign's scoped PHP dependencies are maintained in the
`LibreSign/3rdparty repository <https://github.com/LibreSign/3rdparty>`_,
not by editing generated files inside the LibreSign application repository.
This is the **maintainer procedure** for updating the ``3rdparty`` Git
submodule in `LibreSign/libresign <https://github.com/LibreSign/libresign>`_.

It applies to pull requests targeting ``main`` or a maintained ``stableXX``
branch of the two **code** repositories. In those repositories ``stableXX``
refers to the Nextcloud major. This differs from documentation branches such
as ``stable15``, which refer to the LibreSign release major; see
:doc:`getting-started/branch-policies`.

Automated update sequence
-------------------------

Use **one source PR and one destination PR** for the same target branch.

1. In `LibreSign/3rdparty pull requests <https://github.com/LibreSign/3rdparty/pulls>`_,
   review the Dependabot version change, ``composer.lock`` and the intended
   target branch. Do not merge yet.

2. As a maintainer with write permission, post this **entire comment** on
   the open 3rdparty PR:

   .. code-block:: text

      /composer-update

   The bot regenerates scoped vendor files and, when needed, commits them
   to the source PR with a GitHub-verified signature and DCO sign-off.
   An acknowledgement (eyes reaction and a status comment with the Actions
   link) is attempted; the status comment is updated with the result.
   A thumbs-up means regeneration **finished**, not that review or CI passed.
   If the command fails, inspect the linked Actions logs before retrying.

3. Wait for the **new source HEAD's** checks to complete, especially
   ``Check vendor changes``, PHP lint and DCO. Confirm there are no failures,
   missing mandatory checks or unexpected changes to generated files.

4. Comment on that **same 3rdparty PR**:

   .. code-block:: text

      /libresign-pr

   The automation checks the source PR and creates a corresponding PR in
   LibreSign, targeting the matching branch and initially pointing its
   ``3rdparty`` gitlink to the **proposed source HEAD**. Inspect the
   created PR, changed files and CI. It is not ready for its final merge yet.

5. Once the 3rdparty PR is approved, **merge the 3rdparty PR first**.
   Record the **actual merged SHA** from that repository, not the Dependabot
   head SHA.

6. On the **linked LibreSign PR**, comment:

   .. code-block:: text

      /update-3rdparty

   The bot updates the ``3rdparty`` gitlink to the **merged source SHA**
   with a new, signed and DCO-compliant commit. Verify that the gitlink
   actually matches the merged SHA and that the updated LibreSign CI runs
   against the new HEAD.

7. After all relevant LibreSign checks and reviews pass, merge the LibreSign
   PR. Verify the branch's final ``3rdparty`` gitlink matches the intended
   3rdparty merged commit.

The commands do **not** merge PRs. They operate on same-repository PR
branches for authorized maintainers; forks are excluded. Do not copy
unreviewed changes across repositories or assume that a green source
check proves LibreSign's signing and certificate integration is safe.
Follow :doc:`getting-started/tests` for the affected test matrix.

When the source PR was merged early
-----------------------------------

Once the merged-source-safe workflow is active in LibreSign/3rdparty, a
maintainer may post ``/libresign-pr`` on an **already merged** source PR.
The workflow resolves the **actual source merge commit SHA**, rather than
depending on the source branch still existing, and generates the Composer
diff relative to the merge's first parent.

This route accepts a two-parent merge commit, verifies that the target
``3rdparty`` gitlink would advance rather than move backward or sideways,
and creates a matching LibreSign PR referencing the **merged SHA directly**.
Do not run ``/update-3rdparty`` again for that same SHA. Review the source
merge commit's signature and matching DCO sign-off separately: green
checks on the source PR head do not prove the merge commit is compliant.
The destination LibreSign PR must pass its own CI and normal review.

If a destination branch or PR already exists, inspect and continue it
instead of creating a duplicate. If this automation is unavailable or
rejects the source (for example, it was squash-merged rather than merged
with two parents), follow the manual update instructions below: create a
**separate, narrowly scoped** LibreSign PR targeting the corresponding
code branch and update only the ``3rdparty`` gitlink to the source merge
SHA. Create a new verified signed/DCO commit, verify LibreSign CI, and do
not reconstruct the source PR, amend reviewed commits or force-push.

Manual update when automation is unavailable
--------------------------------------------

Use a clean, disposable working tree. Follow the 3rdparty
`PHP-Scoper and Composer instructions
<https://github.com/LibreSign/3rdparty#updating-dependencies>`_
to regenerate libraries; do not edit generated ``composer/`` files by hand.

Commit and review changes to the source PR first. On a separate LibreSign
branch, update **only** the submodule reference to the proposed source HEAD,
make a verified signed/DCO commit and open a destination PR. After the
source PR is merged, add a **new** verified signed/DCO commit to the
destination PR pointing to the actual merged SHA. Rerun LibreSign CI and
complete required reviews before merging. Preserve the incremental history
(no ``git commit --amend``, squash or force-push to replace reviewed commits).

Merge commit signatures and DCO
-------------------------------

A successful DCO check on a PR validates the submitted commits, **not**
a separate merge commit created later by GitHub. A green ``Verified`` badge
on a merge commit likewise does not prove the DCO sign-off is present.

When using a GitHub merge method that creates a merge commit, ensure its
message includes a ``Signed-off-by: Name <email>`` trailer matching the
**effective merge-commit author**. Confirm the author's actual name and
email instead of assuming they equal the local Git configuration or bot
identity. Preserve the reviewed, individually signed commits.

After merging **each repository PR**, inspect the actual merge SHA for a
verified cryptographic signature and a DCO trailer matching its author.
If these are missing, stop using the defective merge procedure and correct
it for future merges. Do **not** rewrite protected history to repair
already published merges. For general requirements, see
:doc:`getting-started/commits`.

Troubleshooting
---------------

* **No acknowledgement:** Inspect the issue-comment Actions run on the
  source repository. The reaction API may fail even when the visible
  status comment works; check the workflow log.
* **Regeneration failed:** Inspect the first failing Composer or commit
  verification step. Do not merge without a regenerated, reviewed source
  HEAD. Never disable signature or DCO checks to make an update pass.
* **Source HEAD changed after CI:** Wait for new checks and issue the
  subsequent command only after confirming the revised commit.
* **Destination branch or PR already exists:** Inspect and continue that
  PR rather than creating a duplicate or overwriting its branch.
* **Source PR already merged:** Use ``/libresign-pr`` if the merged-source
  workflow is available; otherwise follow the manual gitlink procedure.
* **Destination checks fail:** Diagnose the LibreSign integration independently
  of the successful 3rdparty Composer checks.

The current workflow definitions live in the code repositories. This page
is the single maintainer-facing source for their **cross-repository sequence**;
repository READMEs and contribution guides should link here rather than
repeat the procedure.
