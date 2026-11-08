<!--
SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
-->

# LibreSign documentation

Source for the [LibreSign public documentation](https://docs.libresign.coop/),
built with Sphinx. The site provides separate manuals for stable LibreSign
majors (`/13/`, `/14/`, `/15/`) and development (`/main/`).

- **Edit content:** `main/` contains development manuals; `versioned/base/`
  contains release-safe foundations, with changes for individual major lines
  in `versioned/<major>/`.
- **Contribute:** open a PR. CI checks Sphinx, links, OpenAPI provenance and
  version isolation. A navigable preview link is posted on the PR.
- **Maintain releases:** see the
  [maintainer guide](docs/maintainers/versioning.md) for local builds,
  deployment, previews, backports and lifecycle metadata.

Canonical release history and API sources remain in
[LibreSign/libresign](https://github.com/LibreSign/libresign).
