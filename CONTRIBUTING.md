<!-- SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
     SPDX-License-Identifier: CC-BY-3.0 -->

# Contributing to LibreSign documentation

You can edit the documentation without knowing Python or the site generator.

## Select a version

The branch **is** the LibreSign documentation version:

| Branch | Documentation |
| --- | --- |
| `main` | Next LibreSign release (development) |
| `stable15` | LibreSign 15 |
| `stable14` | LibreSign 14 |
| `stable13` | LibreSign 13 |

New releases follow `stableNN`, where `NN` is the **LibreSign** major, not
Nextcloud's major. The published version selector and **Edit on GitHub** links
should take you to the matching branch automatically.

## Edit one page

1. Open the version and manual you want to change at https://docs.libresign.coop.
2. Select **Edit on GitHub** or browse the corresponding branch.
3. Edit the RST file under `user_manual/`, `admin_manual/` or `developer_manual/`.
4. For a new page, add its name to the section `index.rst` (`.. toctree::`).
5. Create a pull request targeting the **same** branch.
6. Review the HTML preview and fix any Sphinx warnings or broken links.

**No Python test, manual file manifest, or generator change is needed to add a
page.** The CI builds the manual and checks internal links automatically.

## Make a fix available in multiple versions

Correct the newest applicable version first. Backport the same change to each
older `stableNN` branch that needs it (one PR per target branch). Do not assume
that an API operation or configuration option is available in an older release.

API examples must match the pinned application OpenAPI and implementation for
the intended LibreSign version. The documentation builds use the application
manifest and the exact application commit; a Nextcloud version or an OCS
`/api/v1` URL does not establish feature compatibility.

## Preview locally

Install Python and the dependencies in a virtual environment, then run:

```sh
python -m pip install -r requirements.txt
sphinx-build -n -W developer_manual _build/developer_manual
```

Replace `developer_manual` with the manual you changed. The PR workflow also
validates all published releases, API provenance, SEO and links.

Do not rename published pages without preserving their URLs with redirects.
Never put credentials or real customer data into examples.

## New stable LibreSign release

The maintainers create `stableNN` from the approved development (`main`) manual
when the LibreSign application releases that major. Public versions are
discovered from the application manifest, not a hardcoded list in the site.
The branch must exist before the documentation build can publish that release.

## Commit policy

Sign off every commit according to the
[Developer Certificate of Origin](https://developercertificate.org/).
A GitHub verified signature is also required when enforced by the repository.
