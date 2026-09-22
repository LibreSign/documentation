.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Preparing a release
===================

Start the **Prepare release** workflow in ``LibreSign/libresign``.

The workflow builds a read-only release plan first. The plan identifies the previous reachable release tag, exact planning SHA, release activity, proposed version, changelog target, milestone state and open backport blockers.

Inputs
------

``branch``
   Stable branch to release.

``ref``
   Optional exact commit or ref for reproducing or recovering a known planning state.

``version``
   Optional explicit version override. Branch/version consistency is still validated.

``channel``
   ``alpha``, ``beta``, ``rc`` or ``final``.

``ignore_open_backport``
   Explicit override for a matching open backport blocker. It is never implied automatically.

``create_follow_up_milestone``
   Whether a follow-up milestone should be created during the post-merge transition.

Security fixes
--------------

Security is classified per pull request, not per release.

A pull request that fixes a security issue must have a public-safe Conventional Commit title and the ``security`` label. The release tool places that pull request under the ``Security`` changelog category while preserving all other public release activity normally.

Do not put advisory-private details in the pull request title, changelog text, workflow inputs, artifacts or public documentation. The advisory remains the source for private vulnerability details until disclosure.

Generated PR
------------

The preparation PR is deterministic and may change only the configured release files: the per-major changelog plus the version source and mirrors.

For LibreSign these are the per-major changelog, ``appinfo/info.xml``, ``package.json`` and ``package-lock.json``.

The selected stable branch is authoritative for the release. For a stable release, the exact released changelog section is synchronized back to the aggregate history on ``main`` without copying the stable version files into ``main``.
