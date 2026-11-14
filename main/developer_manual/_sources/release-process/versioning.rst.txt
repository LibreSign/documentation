.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Versioning and prereleases
==========================

LibreSign versions follow ``MAJOR.MINOR.PATCH``. The app major tracks the supported Nextcloud major used by the corresponding stable line.

Normal version selection is derived from release activity since the previous reachable release tag. Feature-level activity advances the minor line; fixes and maintenance advance the patch line. Translation-only activity does not create a feature bump.

An explicit version override is supported for recovery or deliberate release decisions, but the release tool validates it against the selected branch and configured release files.

Prerelease channels
-------------------

``alpha`` and ``beta`` are prerelease channels for incomplete release lines. ``rc`` is a release candidate. ``final`` is the normal stable publication.

The selected channel is carried through the release contracts and determines whether the generated GitHub Release is marked as a prerelease.

Per-major changelogs
--------------------

Canonical release text lives in ``docs/changelogs/changelog-<major>.md`` in ``LibreSign/libresign``. Each major has its own file, avoiding conflicts between stable branches.

For packaging, the selected per-major file is copied to package-root ``CHANGELOG.md``. The package does not fetch this documentation repository.

GitHub Release notes are derived from the same released section. The changelog itself is maintained only in ``LibreSign/libresign``; this documentation repository does not duplicate it.
