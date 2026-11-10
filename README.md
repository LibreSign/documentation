<!-- SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
     SPDX-License-Identifier: CC-BY-3.0 -->

# LibreSign documentation

Public manuals: **https://docs.libresign.coop**.

The documentation follows Nextcloud's **one branch per version** pattern:

| Branch | LibreSign documentation |
| --- | --- |
| `main` | Next release, in development |
| `stable15` | LibreSign 15 |
| `stable14` | LibreSign 14 |
| `stable13` | LibreSign 13 |

For a new release, use `stableNN`, where NN is the **LibreSign major** (not the
Nextcloud server major). Each branch contains complete `user_manual/`,
`admin_manual/` and `developer_manual/` sources. There are no `versioned/`
source overlays and no per-page Python tests to update.

**To edit a page:** choose the LibreSign version on the website, select
**Edit on GitHub**, update the RST file and open a PR to the **same branch**.
For a new page, add it to the section's `index.rst` (`.. toctree::`).
For changes applying to multiple versions, backport explicitly.

See [CONTRIBUTING.md](CONTRIBUTING.md) for everyday editing and
[docs/maintainers/versioning.md](docs/maintainers/versioning.md) for the
publication process, API contracts and new releases.

The build dynamically discovers released LibreSign majors and pins their
OpenAPI contracts to their exact application commits. Releases are never
inferred from a documentation branch alone.
