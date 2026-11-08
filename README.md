<!--
SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
-->

# LibreSign documentation

Public documentation is published at https://docs.libresign.coop, with stable
release lines under `/13/`, `/14/`, `/15/` and development under `/main/`.

The application repository [LibreSign/libresign](https://github.com/LibreSign/libresign)
owns the canonical changelogs and API source. This repository owns Sphinx manuals,
version selection and publication. Do not copy changelogs into this repository.

## Versioned documentation

Each build resolves all relevant application branches to **immutable commit SHAs**
and reads `appinfo/info.xml` and `openapi.json` from each SHA. The manifest
defines the LibreSign major and compatible Nextcloud range. New lines are
discovered automatically, provided their manifests contain a stable release
version. No `main` OpenAPI URL is used for a stable version.

Stable manual content resides under `versioned/base/` with optional overlays
in `versioned/<major>/`. These are deliberately separate from the developer
documentation on `main`; never copy unverified development workflows into
older lines. Version-specific additions go into the appropriate major overlay.

`versioning/lifecycle.json` is the **explicit** EOL metadata. Unknown dates
must remain null. Previous release != automatically EOL. No commercial support
commitment is implied by this documentation.

## Local development

Install `requirements.txt` and `openapi-spec-validator==0.7.2`, then:

```shell
python -m unittest discover -s tests -v
python -m versioning.build --output _build
python -m versioning.verify --output _build
python -m versioning.publish --built _build --destination _publish
python -m versioning.verify --output _publish
```

Use `python -m http.server 8765 --directory _publish` to preview the pages.

## Publication during releases and backports

1. Merge the LibreSign application release/backport and confirm its
   `appinfo/info.xml` compatibility and generated `openapi.json` are correct.
2. Add version-specific manual updates to `versioned/<major>/` if necessary.
   Never copy the development guide as a substitute for reviewing behavior.
3. Open a documentation PR and run the `Documentation` workflow, including
   schema checks, cross-version tests, links and screenshots.
4. After documentation changes are reviewed and merged, the `Deploy Sphinx
   Docs` workflow runs automatically for the full site. For a targeted
   refresh, run the workflow manually with `version: <major>` or
   `version: main`. Automated release tooling can send a repository dispatch
   with event `libresign-documentation-release` or
   `libresign-documentation-backport`, passing `client_payload.version`.
5. The scheduled daily refresh also incorporates backports and new application
   release manifests without needing a cross-repository GitHub token.
6. A partial deployment first checks out the existing `gh-pages` tree and
   **replaces only the selected version**. It refuses to publish if the old
   version catalog or previous releases are absent. Full-site publication
   builds and verifies every version before changing Pages.
7. Check each published URL and the `openapi.provenance.json` next to its
   `openapi.json`. Confirm `/main/` remains labelled development.
   Old, unversioned URLs redirect to the current stable counterpart.

**Concurrency:** deployment runs are serialized by a workflow concurrency
group. Existing published lines must never be dropped from a partial publish.

## Scope and licensing

User, administrator and developer manuals retain their documentation-specific
Creative Commons licensing and existing SPDX notices. The source application
has its own license.
