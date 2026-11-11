<!-- SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
     SPDX-License-Identifier: CC-BY-3.0 -->

# Versioning and publication of LibreSign documentation

The public source is deliberately simple: **one complete documentation branch
per LibreSign major**, following the Nextcloud documentation convention.

## Where to edit

| Target | Git branch | Source path |
| --- | --- | --- |
| Next LibreSign version | `main` | `user_manual/`, `admin_manual/`, `developer_manual/` |
| LibreSign 15 | `stable15` | Same paths |
| LibreSign 14 | `stable14` | Same paths |
| LibreSign 13 | `stable13` | Same paths |

For a future stable release `NN`, create `stableNN`. The documentation branch
name is the **LibreSign major**, not the Nextcloud major; the application
repository uses a different naming convention (`stable35` for LibreSign 15).
Each source branch contains its complete manual, without shared-directory
inheritance or `versioned/base` overlays. **Edit on GitHub** links to the
matching branch and file, not to a generated or inherited source.

Ordinary RST contributions do not require Python changes. Add a page to the
section's `index.rst` toctree, build with Sphinx and open a PR against the
right branch. Backport changes explicitly when they apply to older releases.

## What the central build does

`main` contains the publishing tool and site-wide assets. It:

1. Discovers released application branches and the development branch from
   `LibreSign/libresign`, verifying `appinfo/info.xml` compatibility.
2. Pins the application commit and OpenAPI SHA for **each** released version.
3. Fetches the matching documentation `stableNN` branch and pins its Git SHA.
   Missing branches cause an error; the build never substitutes development
   documentation for a stable release.
4. Builds each branch's manuals using the current common Sphinx theme and
   navigation. The published URLs remain `/13/`, `/14/`, `/15/`, `/main/` etc.
5. Validates links, API provenance, signing examples, redirects and the output
   of all other versions before deploying atomically to Pages.

The moving aliases follow Nextcloud's documentation convention: `/latest/`
redirects to the unreleased `/main/`, while `/stable/` redirects to the
latest published stable major from `versions.json.current_stable`. Both
support deep HTML paths, including `/stable/developer_manual/api/openapi.html`.
The matching `openapi.json` and `openapi.provenance.json` are also available
under each alias. Publish updates the aliases atomically on full and partial
releases. For reproducible integrations, pin the exact numeric version and
confirm the OpenAPI provenance: these aliases can change on release.

Stable application releases are discovered dynamically, not maintained in a
fixed list. EOL dates and policy remain in `versioning/lifecycle.json`.
The API version is always taken from the application manifest, not from the
Nextcloud release number or a guessed API URL.

## Validate a change locally

On the branch containing the publishing tool (`main`):

```sh
python -m pip install -r requirements.txt openapi-spec-validator==0.7.2
python -m unittest discover -s tests -v
node --test tests/js/*.test.mjs
python -m versioning.build --output _build
python -m versioning.verify --output _build
python -m versioning.publish --built _build --destination _publish
python -m versioning.verify --output _publish
```

The build requires read-only Git access to the LibreSign application and
this documentation repository. All released application versions must have
an existing documentation source branch before CI can publish them.

When editing a `stableNN` documentation branch, the CI builds its local
manuals with Sphinx warnings treated as errors. It does **not** regenerate
all public releases; the publication workflow on `main` does that.

## PR previews

The main-branch PR workflow builds a complete isolated candidate on
`https://libresign.github.io/site-preview/docs-preview/pr-<number>/`.
Development documentation already exists at `/main/`; it is not duplicated
in a fake stable version under `/_review/NN/`. The `/_review/` index links to
the actual development manual and its preview. The separate preview origin is
never the production domain. PRs from forks are deployed only by the
privileged workflow after static-artifact inspection.

The sticky preview comment includes stable and development entry links.
A successful preview does not authorize a merge.

## Release procedure

1. Review and approve the application release manifest and its OpenAPI.
2. Freeze approved documentation for the release in `main`.
3. Create a DCO-signed documentation branch `stableNN` from that snapshot,
   **before** publishing the application's newly released major in the site.
4. Update the `main` documentation for the next development cycle as needed.
5. Run the central build and verify its HTML pages, exact API provenance,
   correct GitHub edit links, and version selector.
6. Deploy via `Deploy Sphinx Docs` after review.

To fix an older release, backport the documentation change to its `stableNN`
branch. The central scheduled workflow sees both application and documentation
updates; for faster updates, run `workflow_dispatch` with `version: NN`.
Partial publication replaces only the selected release and preserves all
others. Full publication validates every version before deployment. Existing
unversioned URLs remain pinned through `versioning/legacy-routes.json`;
they must not be redirected silently to a newer API or a different release.

GitHub Pages deployments are serialized. Publishing unreleased material to
`docs.libresign.coop` requires an explicitly authorized release process.
