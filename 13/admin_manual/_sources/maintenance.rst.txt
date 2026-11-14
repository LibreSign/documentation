Maintain an installation
========================

Before upgrading
----------------

#. Confirm the target LibreSign release is compatible with the installed
   Nextcloud version; do not assume matching numbers refer to the same product.
#. Record the current application and Nextcloud versions, configuration,
   certificate engine, and enabled signing or identification methods.
#. Back up the Nextcloud database, configuration, related files, and the
   certificate material and signing keys required by your deployment.
   Protect these backups according to their sensitivity.
#. Follow Nextcloud's supported application upgrade procedure and consult
   the `LibreSign releases <https://github.com/LibreSign/libresign/releases>`_
   for changes relevant to your target version.
#. Check **Configuration check** after the upgrade; perform a test signing
   and validate its resulting PDF before resuming production activity.

Backups must be recoverable: verify recovery on an isolated system, including
access to the certificate material necessary for previously signed documents.
Do not expose private keys in tickets, logs, or example configurations.

Troubleshooting
---------------

- **Cannot request a signature:** check the user's permissions and the
  allowed identification methods in :doc:`configuration`.
- **Setup is incomplete:** inspect **Configuration check** and
  **Dependencies**, and check Nextcloud's application logs.
- **An invitation was not received:** verify the request status and the
  configured delivery channel; inspect the mail system only if email delivery
  is configured. Avoid resending invitations blindly.
- **Validation fails:** inspect the reported certificate or PDF error, and
  confirm that the signing environment's trust material is still available.

Do not regenerate the root certificate as a generic troubleshooting step.
