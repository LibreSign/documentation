.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Reusable release tooling
========================

LibreSign is the reference consumer of reusable release tooling:

``LibreCodeCoop/release-tool``
   Release planning, version/changelog policy, state contracts, milestone transitions, history synchronization, draft generation and publication verification.

``LibreCodeCoop/github-workflows``
   Tested GitHub Actions orchestration and managed workflow distribution.

``LibreSign/libresign``
   Consumer configuration, stable branches, changelog/version files, packaging rules and publisher workflow.

Other Nextcloud apps can adopt the same tooling without depending on LibreSign application code.

Adopting it in another app
--------------------------

Use the generic guides maintained with the tooling:

* `Getting started <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/getting-started.md>`_
* `Consumer configuration <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/consumer-configuration.md>`_
* `Release lifecycle <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/release-lifecycle.md>`_
* `GitHub Actions integration <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/github-actions.md>`_
* `GitHub App setup <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/github-app.md>`_
* `Managed workflow synchronization <https://github.com/LibreCodeCoop/github-workflows/blob/main/docs/cross-repository-automation.md>`_

A managed consumer installs ``prepare-release.yml`` and ``sync-workflow-templates.yml`` from the organization workflow catalog. The updater keeps installed workflows current through reviewable pull requests.

The release GitHub App needs Contents and Pull requests read/write access. A GitHub App used for workflow synchronization additionally needs Workflows write access.

The remaining pages in this section describe LibreSign's concrete release process. Generic configuration and GitHub App setup are intentionally not duplicated here.
