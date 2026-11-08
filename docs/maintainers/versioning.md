<!--
SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
SPDX-License-Identifier: CC-BY-3.0
-->

# Versioning, previews and publication

This guide is intended for contributors and release maintainers, not as
public API documentation. The root [README](../../README.md) is deliberately
short. Product release histories remain canonical in
[LibreSign/libresign](https://github.com/LibreSign/libresign/releases).

## Source of truth and release boundaries

Each build resolves the application branches to **immutable commit SHAs** and
fetches `appinfo/info.xml` and `openapi.json` from each resolved SHA.
Stable lines are discovered from the manifest, and incompatible Nextcloud
dependencies cause the build to fail. A stable line must never load an API
contract from `main`. Every generated API reference has accompanying
`openapi.json` and `openapi.provenance.json` files.

Maintain `main/` as development documentation and `versioned/base/` as the
release-safe foundation. Use `versioned/<major>/` for material verified
against a specific release. Do not copy unreviewed development flows into
stable manuals. The Sphinx theme and configuration are shared.

The version selector marks `main` as development, the latest supported
stable line as current, and earlier stable lines as previous. EOL status and
dates are explicit entries in `versioning/lifecycle.json`. Never infer an
EOL commitment or commercial support guarantee from branch existence.

## Local build and checks

Use Python 3.12 (as in CI) and install `requirements.txt` plus
`openapi-spec-validator==0.7.2`. Run:

```sh
python -m unittest discover -s tests -v
node --test tests/js/version-switcher.test.mjs
python -m versioning.build --output _build
python -m versioning.verify --output _build
python -m versioning.publish --built _build --destination _publish
python -m versioning.verify --output _publish
python -m http.server 8765 --directory _publish
```

The build needs read-only network access to application Git refs and files.
It fails rather than silently substituting an outdated or main-branch
contract. GitHub Actions additionally uploads screenshots as review evidence.

## Pull request previews

The `Documentation PR Preview` workflow builds the full multiversion
candidate without changing production Pages. The URL pattern is:

```text
https://libresign.github.io/site-preview/docs-preview/pr-<number>/
```

The preview lives on the **isolated preview origin**, in the
`LibreSign/site-preview` repository, under its own `docs-preview/`
namespace. The production domain `docs.libresign.coop` is never used for
unreviewed HTML. A preview banner identifies the PR, and all version
selection, redirects and links stay within the preview prefix.

The workflow authenticates to the preview repository through the existing
organization GitHub App `librecode-workflow-automation`. It requires
`vars.LIBRECODE_WORKFLOW_APP_ID` and
`secrets.LIBRECODE_WORKFLOW_APP_PRIVATE_KEY` (the organization already
distributes these to its repositories). The app token is short-lived and
restricted to `LibreSign/site-preview`; no personal PAT needs copying.

For PRs originating in the documentation repository, the build publishes
the preview and posts a sticky preview link. For forks, the unprivileged
workflow only uploads an HTML artifact; the trusted `workflow_run` consumer
publishes that artifact from the repository default branch. It never
checks out or executes fork code while possessing the deployment token.
Upon closing the PR, the trusted cleanup workflow removes its preview.

The preview action and organization App do not publish stable documentation.
Successful preview CI is **not authorization to merge**.

## Releases and backports

1. Confirm the application release/backport and its manifest and OpenAPI.
2. Review changes to `versioned/<major>/`; keep the stable content bounded
   by the branch's actual capabilities.
3. Open a documentation PR, inspect the navigable preview and the uploaded
   screenshots, and wait for CI checks.
4. After approval and merge, the `Deploy Sphinx Docs` workflow deploys
   the complete site. For a targeted update, dispatch with
   `version: <major>` or `version: main`. The application release
   tooling may send `repository_dispatch` events named
   `libresign-documentation-release` or
   `libresign-documentation-backport` with
   `client_payload.version`.
5. The daily scheduled workflow also discovers new stable application
   branches and captures subsequent backports. Each line is built from a
   pinned commit of its application branch.
6. Partial releases first check out the existing `gh-pages` site and
   **replace only the selected version**; they fail if the old catalog
   or another previously published version is missing. Full releases must
   build every version before deployment.
7. Test each published major/manual URL and its corresponding
   `openapi.provenance.json`. Legacy, unversioned documentation paths
   redirect to the current stable line.

Pages deployments are serialized by workflow concurrency. Their output must
never erase sibling stable versions.
