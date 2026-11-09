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
configuration instruction, screenshot, or troubleshooting step:

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
3. **Choose the source scope deliberately.** `developer_manual/` is the
   development line. `versioned/base/` is for behavior verified in **every**
   published stable line; `versioned/<major>/` overrides it when any stable
   behavior differs. The `main/` directory contains site navigation, not the
   development developer manual. Never copy development-only claims into the
   stable base, or assume newer features were backported. For an unverified
   release, omit or explicitly qualify the claim rather than invent support.
4. **Verify executable examples per release.** Use the correct version-specific
   fixtures and checks; never make older guides silently use a newer payload.
   Add regression coverage for incompatibilities, including negative cases.
   Do not weaken a contract check just to keep inherited prose passing.
5. **Review versioned links and surrounding pages.** Avoid silently linking
   older manuals to `/main/`, `/latest/`, or moving source-branch URLs when
   claiming version-specific support. Inspect related pages across all three
   manuals and the affected stable releases; preserve redirects when moving
   URLs. Check old and new releases after changing shared content.
6. **Validate and report evidence.** Build affected Sphinx manuals, run
   versioned contract/provenance checks and relevant runtime tests where
   feasible, and inspect screenshots of each changed rendered page. State
   explicitly which releases, scenarios, and behaviors are verified versus
   untested. Green Sphinx/CI checks are not proof of real signing, SMTP,
   policies, or file-download permissions.

This repository builds stable versions from `versioned/base/` plus overlays,
not from separate documentation branches as Nextcloud does. Preserve the
existing dynamic discovery and build infrastructure. For authoring details
and the external-email-signers fixture conventions, read
[CONTRIBUTING.md](CONTRIBUTING.md). Application behavior and API contract
changes belong in `LibreSign/libresign` and require a separate change there.

## Quality gates

Build the affected Sphinx manuals. Pull requests should pass the Documentation workflow; developer documentation is built with warnings treated as errors.

For each changed or added rendered documentation page, include a screenshot of
the Sphinx output in the PR. Screenshots are review evidence, not source files;
do not include sensitive information. For tooling-only changes that affect no
rendered page, state `Not applicable` and explain why.

## Licensing

Preserve the documentation-specific Creative Commons licensing and existing SPDX conventions. Do not silently relicense documentation under the application/code license.

## Safety

Do not publish secrets, private security-advisory content or personal data in examples, screenshots or release documentation.
