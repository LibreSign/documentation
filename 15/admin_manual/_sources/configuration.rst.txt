Configure signing
=================

Open **Administration settings** in Nextcloud and find LibreSign. Configuration
is server-owned: users should not be asked to change a system-wide signing
policy to complete a single request.

Signing and identity
--------------------

Review the available signature engine and signing methods before enabling
external signers. The user's available choices can depend on permissions,
identity methods, and policy settings. Test the configured invitation method
with a non-production request before relying on it.

The administrative layout changes across supported releases. In LibreSign 13
and 14, several settings appear as individual controls; LibreSign 15 includes
the Policy Workbench for applicable configuration. Consult the visible
controls in your installed version rather than looking for an identically
named control in every release.

Certificates and dependencies
-----------------------------

- Review **Certificate engine** and **Root certificate data** and the chosen
  trust model before issuing signatures.
- Use **Configuration check** and the **Dependencies** section to diagnose
  an incomplete installation.
- Record the selected certificate policy and secure storage location as part
  of your deployment's operational documentation.

Changing a trust anchor or regenerating a root certificate is not routine
configuration. See :doc:`security` and :doc:`maintenance` first.

For integration and version-pinned API payloads, use the
`developer API reference <../developer_manual/api/index.html>`_.
