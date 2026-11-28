Developer manual — LibreSign |LibreSignRelease|
===============================================

This is the **release-specific API contract** for LibreSign
|LibreSignRelease| and Nextcloud |NextcloudRelease|. The schema is pinned
to an application commit on the corresponding stable branch. Development-only
API calls and payloads are not presented as features of this release.

Integrate an external application
---------------------------------

- :doc:`integration/index` — choose an integration architecture for an
  existing application.
- :doc:`api/external-email-signers` — follow a release-specific API example
  for inviting an external email signer.
- :doc:`api/openapi` — inspect the OpenAPI schema pinned to this release.

Contribute or develop LibreSign
-------------------------------

Source architecture, coding standards, development environment, tests, and
release engineering follow the project's current development branch. They
are available in the `development and contributor manual
<../../main/developer_manual/index.html>`_. That manual may describe
unreleased functionality. For integrating with LibreSign |LibreSignRelease|,
continue to use the version-specific reference above.

.. toctree::
   :maxdepth: 2
   :caption: Release-specific integration

   api/index
   integration/index
