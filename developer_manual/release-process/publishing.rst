.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Publishing and verification
============================

After the generated release PR is merged, the workflow produces a finalized release contract from the merged SHA and creates or updates a GitHub Release draft.

Review the draft and use GitHub's **Publish release** action when it is correct. Publishing is the second and final semantic human gate.

Existing publisher
------------------

Publishing the GitHub Release triggers the existing LibreSign package/sign/App Store workflow. The release automation does not duplicate that publisher.

Publication verification
------------------------

After publication, the workflow waits for the existing publisher and validates:

* the GitHub Release is published and still points to the finalized tag/SHA;
* the configured publisher workflow completed successfully for that release;
* the expected release asset exists;
* artifact digest and package contents satisfy the configured package contract;
* the same version is visible in the Nextcloud App Store.

Verification is independently rerunnable. Bounded retries handle eventual consistency only; they do not replace release validation rules.

Release history
---------------

Only after publication verification succeeds does automation create or update the documentation release-history PR.

For security releases, only public-safe released text may reach this step; advisory-private text is never used as public release content.
