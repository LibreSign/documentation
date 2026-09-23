.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Reusable release tooling
========================

LibreSign's release process is built on reusable tooling rather than application-specific release scripts.

The implementation is split into three layers:

``LibreCodeCoop/release-tool``
   The deterministic release engine. It owns release planning, version/changelog policy, state contracts, milestone transitions, history synchronization, draft generation and publication verification.

``LibreCodeCoop/github-workflows``
   Thin, tested GitHub Actions orchestration around the release engine.

``LibreSign/libresign``
   A consumer. It supplies ``.nextcloud-release.yml``, version/changelog files, stable branches, packaging rules, publisher workflow and credentials.

This separation is intentional: another Nextcloud app can provide its own consumer configuration and keep its existing package/publish implementation without depending on LibreSign application code.

Why another app might use it
----------------------------

A conventional Nextcloud app release often involves a maintainer checklist:

* select the release branch;
* decide the next version;
* verify pending backports;
* prepare changelog text;
* update version files;
* create or transition milestones;
* create the GitHub release/tag;
* run package/sign/publish steps;
* verify the resulting artifact and App Store entry.

The reusable tooling turns the repeatable parts into deterministic, reviewable contracts while preserving human control over the two important gates:

#. review and merge the generated release preparation pull request;
#. review and publish the generated GitHub Release draft.

The goal is not unattended releases. The goal is to make the same release decision reproducible, auditable and less dependent on maintainer memory.

What a consumer keeps
---------------------

Adopting the tooling does not require replacing project-specific systems.

A consumer can keep:

* its existing package command;
* signing infrastructure;
* App Store credentials;
* smoke-test process;
* publisher workflow;
* stable-branch policy;
* project-specific release checks.

The release tool coordinates those systems around an explicit release plan.

Adoption documentation
----------------------

The generic documentation lives with the tooling:

* `Release Tool getting started <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/getting-started.md>`_
* `Consumer configuration <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/consumer-configuration.md>`_
* `Release lifecycle <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/release-lifecycle.md>`_
* `GitHub Actions integration <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/github-actions.md>`_
* `GitHub App setup <https://github.com/LibreCodeCoop/release-tool/blob/main/docs/github-app.md>`_
* `Shared workflow adoption <https://github.com/LibreCodeCoop/github-workflows/blob/main/docs/release-automation.md>`_

LibreSign's remaining release-process pages document the concrete reference implementation.

Reference consumer
------------------

LibreSign currently uses:

* one stable branch per supported Nextcloud major;
* a changelog per release line;
* GitHub milestones for patch/RC planning;
* an existing app package/sign/publish workflow;
* the Nextcloud App Store as the final distribution channel.

The repository configuration is intentionally visible and reviewable in ``.nextcloud-release.yml`` so maintainers of other apps can compare their own conventions before adopting the tooling.

Security model
--------------

Mutation credentials are not shared between organizations.

The LibreCode GitHub App is part of LibreSign's deployment environment. Maintainers of another organization should create and install their own GitHub App and store its private key as an Actions secret. The generic GitHub App setup guide documents the exact permissions, installation scope, private-key generation and Actions secret configuration.

The reusable actions use short-lived installation tokens and the consumer workflow grants permissions per job.
