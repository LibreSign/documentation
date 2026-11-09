<!--
SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
-->

# LibreSign documentation

Source for the [LibreSign public documentation](https://docs.libresign.coop/),
built with Sphinx. The site provides separate manuals for stable LibreSign
majors (`/13/`, `/14/`, `/15/`) and development (`/main/`).

- **Edit content:** use RST in `developer_manual/`, `user_manual/` or
  `admin_manual/`. The `versioned/base/` directory holds stable foundations;
  `versioned/<major>/` holds overrides. Shared development-to-stable sections
  are listed in `versioned/shared.json`. Adding a page never requires editing
  Python build or screenshot scripts.
- **Contribute:** open a PR. CI checks Sphinx, links, OpenAPI provenance and
  version isolation. Review the navigable preview, including any unpublished
  release pages under `/_review/`; screenshots are not required.
- **Maintain releases:** see the
  [maintainer guide](docs/maintainers/versioning.md) for local builds,
  deployment, previews, backports and lifecycle metadata.

Canonical release history and API sources remain in
[LibreSign/libresign](https://github.com/LibreSign/libresign).
