<!--
SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
-->

# Contributing to LibreSign documentation

This repository contains LibreSign's public user, administrator, and developer
documentation. Choose the manual for your reader: `user_manual/`,
`admin_manual/`, or `developer_manual/`. The `main/` directory provides
top-level navigation. Follow the existing manual structure and write about the
product or procedure, not the history of implementing a change. Explain concepts
before advanced details, link to existing explanations instead of duplicating
them, verify internal links and cross-references, and use examples without real
personal or customer data.

## Build and review your change

From the repository root, install Python 3.13 and the dependencies from the root
`requirements.txt` in a virtual environment. For example:

```sh
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -r requirements.txt
```

Build every manual whose rendered pages you changed before opening a pull
request. The root `Makefile` provides `make main`, `make user`, `make admin`,
`make dev`, and `make all`. If `make` is unavailable, use the same Sphinx commands
as the [Documentation CI workflow](.github/workflows/docs.yml):

```sh
sphinx-build main _build/main
sphinx-build user_manual _build/user_manual
sphinx-build admin_manual _build/admin_manual
sphinx-build -W developer_manual _build/developer_manual
```

Run the affected command(s), not necessarily all four; CI builds all four. The
developer manual is built with warnings treated as errors. Open the resulting
HTML page under `_build/` and check headings, lists, code blocks, images, links,
cross-references, spacing, and layout.

## Version-scoped integration documentation

The published version selector does not by itself make prose compatible with
an older LibreSign release. The build discovers application releases from
`appinfo/info.xml`, pins each source commit and publishes that commit's
`openapi.json`. The exact LibreSign/Nextcloud versions are available in
Sphinx as `|LibreSignRelease|` and `|NextcloudRelease|`.

The source layout deliberately has three different scopes:

- `developer_manual/` describes the development (`main`) application.
- `versioned/base/` contains only claims verified across the published
  stable releases. Do not copy development-only behavior into this base.
- `versioned/<major>/` overrides stable content when a release differs.
  The existing version build overlays files; do not change its discovery
  or hardcode version numbers in workflow scripts.

For the external-email-signers guide, each supported application line has
a reviewed `examples/external-email-signers/request-<slug>.json` and a
`_external-email-signers-release.inc` in its own source directory.
The Sphinx include extension `.inc` prevents these snippets from being
treated as additional standalone manual pages. The CLI clients refuse
to choose a fixture implicitly: `LIBRESIGN_DOC_LINE` selects a reviewed
release explicitly. When a new release is discovered, add its reviewed
fixture and overlay rather than inheriting an older identity schema.

The Documentation CI gate validates the actual nested request fields
and example JSON against **that version's pinned OpenAPI**, checks
guarded controller and Playwright source files from the **same pinned
application commit**, and rejects unknown/new releases without reviewed
examples. It does not assert that browser signing, SMTP or certificate
verification passed in a live environment. Record those executions
separately when performed. Changes to an API contract must be made in
the LibreSign application repository and regenerated there; do not
modify the pinned JSON inside the documentation repository.

## Pull request evidence

Link the relevant issue. For every changed or newly added **rendered
documentation page**, attach a screenshot of that page's rendered output to the
pull request. For a long page, use multiple focused screenshots that keep the
changed content and its surrounding context readable. For responsive or UI
examples, use the viewport relevant to the documented workflow. Screenshots
support review; they do not replace the source files or automated checks. Do
not add an image to the documentation source solely to satisfy this requirement.

If a pull request changes only non-rendered tooling, CI, dependencies, or other
files that do not affect a documentation page, write `Not applicable` in the PR
screenshot section and explain why. Never include credentials, tokens, private
documents, real personal or customer data, or other sensitive information in
screenshots.

Keep each pull request focused on one documentation concern. Review the rendered
output and complete the PR checklist before requesting review.

## Developer Certificate of Origin

Sign off each commit to certify the [Developer Certificate of Origin](https://developercertificate.org/).
With your Git name and email configured, use `git commit -s -m "Your message"`.
The resulting `Signed-off-by: Name <email>` trailer must identify you; use an
email associated with your GitHub account if you want GitHub to attribute it.
