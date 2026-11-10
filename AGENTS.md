<!--
SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
-->

# Agent guidance

## Purpose

This repository owns public human documentation for LibreSign.

## Boundaries

- LibreSign application code lives in `LibreSign/libresign`.
- Canonical release history/changelog data lives only in `LibreSign/libresign/docs/changelogs/changelog-<major>.md`; do not duplicate it here.
- Document public behavior, operator procedures, architecture intended for maintainers and recovery/troubleshooting.
- Do not copy implementation details that are better maintained next to the source code.
- Generated Sphinx output must not be committed unless the repository explicitly tracks that output.

## Documentation structure

Keep changes in the appropriate manual:

- `user_manual/`;
- `admin_manual/`;
- `developer_manual/`;
- `main/` for top-level navigation.

## Release parity (required for every documentation change)

Before writing, correcting, or backporting a feature description, API example,
configuration instruction, rendered example, or troubleshooting step:

1. **Identify the target LibreSign release(s).** A Nextcloud major, an OCS
   `/api/v1` path, or a successful build does not identify the LibreSign feature
   version. Use the dynamically discovered application manifest and the exact
   `app_commit` / `app_version` / Nextcloud compatibility from `versions.json`
   and the published `openapi.provenance.json`.
2. **Check behavior against each targeted release, not just `main`.** Read the
   matching pinned `openapi.json` and application controllers, services,
   policies/permissions, configuration, and relevant tests at that commit.
   Check nested required request fields, types/enums, responses, authentication,
   feature availability, signing state and error cases. OpenAPI shape alone
   does not prove runtime behavior; the presence of a test is not proof it ran.
3. **Choose the release branch deliberately.** The `main` branch is
   development; `stableNN` contains the complete documentation for LibreSign
   major NN. Do not mix Nextcloud major numbers with LibreSign major numbers.
   Changes to multiple versions require explicit backports and verification
   against the corresponding application contract.
4. **Verify executable examples per release.** Use the correct version-specific
   fixtures and checks; never make older guides silently use a newer payload.
   For ordinary RST pages, do not add Python tests that enumerate page paths,
   assert editorial wording or mirror the documentation tree. The existing
   Sphinx, link, OpenAPI and multiversion build checks validate those changes.
   Add focused regression coverage only when executable contracts or the
   documentation tooling itself change. Do not weaken existing contract checks.
5. **Review versioned links and surrounding pages.** Avoid silently linking
   older manuals to `/main/`, `/latest/`, or moving source-branch URLs when
   claiming version-specific support. Inspect related pages across all three
   manuals and the affected stable releases; preserve redirects when moving
   URLs. Check old and new releases after changing shared content.
6. **Validate and report evidence.** Build affected Sphinx manuals, run
   versioned contract/provenance checks and relevant runtime tests where
   feasible, and inspect the navigable PR preview, including any unreleased
   release-specific pages under `/_review/`. State explicitly which releases,
   scenarios, and behaviors are verified versus untested. Green Sphinx/CI
   checks are not proof of real signing, SMTP, policies, or file permissions.

Each release branch contains complete `main/`, `user_manual/`, `admin_manual/`
and `developer_manual/` source directories. There is no `versioned/base` or
per-file overlay mechanism. The central publishing tool checks out the exact
documentation branch and pins the application OpenAPI separately. A missing
stable documentation branch must fail rather than inherit development prose.
For authoring instructions read [CONTRIBUTING.md](CONTRIBUTING.md).
Application source and API changes belong to `LibreSign/libresign`.

## Quality gates

Build the affected Sphinx manuals. Pull requests should pass the Documentation workflow; developer documentation is built with warnings treated as errors.

Every rendered documentation change must be accessible through the PR preview.
Reviewers use the published HTML, not mandatory screenshots. Sphinx, links,
OpenAPI provenance and release-specific checks remain required; do not weaken
these checks to make an inaccurate page look compatible.

## Licensing

Preserve the documentation-specific Creative Commons licensing and existing SPDX conventions. Do not silently relicense documentation under the application/code license.

## Safety

Do not publish secrets, private security-advisory content or personal data in examples, screenshots or release documentation.
