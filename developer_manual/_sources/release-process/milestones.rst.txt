.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Milestones and backports
========================

Stable releases use the configured ``Next Patch (<Nextcloud major>)`` milestone. Release candidates use the configured RC milestone policy.

Before preparation, the release plan checks matching open backport work. A blocker stops preparation unless the maintainer explicitly selected ``ignore_open_backport``.

After the release PR is merged, the workflow revalidates the merged state before any milestone mutation. It then renames/closes the released milestone, moves remaining open work when required, and optionally creates the next milestone.

The account that merged the generated release PR must satisfy ``authorization.merge_min_permission`` from ``.nextcloud-release.yml``. The triggering actor for preparation must satisfy ``authorization.prepare_min_permission``.

These permission checks happen before mutating stages. Mutations use short-lived GitHub App installation tokens scoped to the repository and stage.
