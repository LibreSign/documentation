.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

Release tool and consumer configuration
=======================================

LibreSign release policy is executed by the versioned ``release-tool.phar`` distributed by ``LibreCodeCoop/release-tool``.
The LibreSign workflow pins the public Release Tool Actions to an immutable commit from a published release. Those Actions resolve the same repository ``VERSION`` and verify the published PHAR SHA-256 checksum before execution. Do not replace the immutable Action pin or verified PHAR with a floating ``latest`` reference.

Local installation
------------------

For diagnostics or manual recovery, download the same ``release-tool.phar`` and ``release-tool.phar.sha256`` release pinned by the LibreSign release workflow.
Verify the checksum before running the PHAR:

.. code-block:: bash

   sha256sum --check release-tool.phar.sha256
   php release-tool.phar --version

The reported version must match the Release Tool version associated with the immutable Action commit used by the workflow.

Consumer configuration
----------------------

LibreSign keeps its release configuration in ``.nextcloud-release.yml``. The configuration is validated by the release tool before planning or mutation.

The main sections are:

``repository`` and ``app``
   Repository identity, app id and main branch.

``branches``
   Stable branch naming pattern and release-line mapping.

``version``
   Authoritative version source, mirrors and Git tag prefix.

``history``
   How the previous released baseline is selected.

``changelog``
   Per-major source path and the package-root changelog destination.

``milestones``
   Stable and prerelease milestone naming templates.

``authorization``
   Minimum repository permissions required to start mutating preparation and to merge a generated release PR.

``package``
   Package build command plus required and forbidden archive paths used by artifact validation.

``publication``
   Existing publisher workflow, expected GitHub Release asset name and Nextcloud App Store API used by post-publication verification.

Validation
----------

Validate the configuration without changing repository state:

.. code-block:: bash

   php release-tool.phar config:validate \
       --config .nextcloud-release.yml \
       --root . \
       --json

Unknown keys and invalid values fail closed. Repository-specific behavior should be expressed through this configuration or a release-tool adapter, not copied into workflow YAML.
