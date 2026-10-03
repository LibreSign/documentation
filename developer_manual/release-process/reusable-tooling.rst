.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Reusable release tooling
========================

LibreSign is the reference consumer of LibreCode's reusable release tooling.
The reusable pieces are intentionally independent of LibreSign application
code.

``LibreCodeCoop/release-tool``
   Owns release policy, contracts, the PHP/PHAR runtime, release planning,
   changelog/version transitions, draft creation, publication verification and
   the public lifecycle Actions.

``LibreCodeCoop/.github``
   Owns the organization workflow catalog, managed workflow distribution,
   synchronization helpers and organization-level automation.

``LibreSign/libresign``
   Supplies the consumer configuration, stable branches, changelog/version
   files, repository-specific packaging rules and publisher workflow.

The former ``LibreCodeCoop/github-workflows`` repository is retired and should
not be used by new consumers.

Adopting the tooling in another app
-----------------------------------

Start with the generic guides maintained next to Release Tool:

* `Getting started <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/getting-started.md>`_
* `Consumer configuration <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/consumer-configuration.md>`_
* `Release lifecycle <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/release-lifecycle.md>`_
* `GitHub Actions integration <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/github-actions.md>`_
* `GitHub App setup <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/github-app.md>`_
* `Troubleshooting <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/troubleshooting.md>`_

Managed workflow catalog and synchronization documentation belongs to
``LibreCodeCoop/.github``. Consumer repositories should use the current
organization catalog rather than copying orchestration from the retired
``github-workflows`` repository.

The remaining pages in this section describe LibreSign's concrete release
process. Generic Release Tool configuration should stay canonical in the
Release Tool repository instead of being duplicated here.
