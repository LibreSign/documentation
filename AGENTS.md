<!--
SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-4.0
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

## Quality gates

Build the affected Sphinx manuals. Pull requests should pass the Documentation workflow; developer documentation is built with warnings treated as errors.

## Licensing

Preserve the documentation-specific Creative Commons licensing and existing SPDX conventions. Do not silently relicense documentation under the application/code license.

## Safety

Do not publish secrets, private security-advisory content or personal data in examples, screenshots or release documentation.
