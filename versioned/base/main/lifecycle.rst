Release lifecycle and extended support
======================================

LibreSign versions are identified by the application's **major version**.
Each published documentation path, such as ``/13/``, corresponds to the
matching stable application branch and its compatible Nextcloud release.
The OpenAPI artifact published with each line comes from the exact application
commit identified on the API page.

``/main/`` is a development snapshot and must not be treated as a stable
release contract. A version selector distinguishes the current stable release
line, earlier lines, and explicitly designated end-of-support (EOL) lines.

**The existence of a stable branch or archived documentation does not guarantee
maintenance, security fixes, or a commercial support commitment.** There is no
implicit EOL date. When project maintainers announce end of support, the
lifecycle metadata must be updated so the version selector marks that line EOL.

Organizations requiring assistance beyond a release's community maintenance
window may seek a separately negotiated extended-support arrangement.
Availability, scope, duration, pricing, and service levels are not promised
by the public project documentation.

The canonical release history is in
`LibreSign/libresign <https://github.com/LibreSign/libresign/releases>`_;
this documentation intentionally does not mirror its changelogs.

Updating versions
-----------------

Release and backport documentation is generated from the actual stable branch,
including ``appinfo/info.xml`` and ``openapi.json``. See the
`documentation repository <https://github.com/LibreSign/documentation>`_
for the repeatable build and publication process.
