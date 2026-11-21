Install and initialize LibreSign
================================

Prerequisites
-------------

Use a supported Nextcloud instance and the matching LibreSign release. The
application declares compatibility in its ``appinfo/info.xml``; this site's
release selector distinguishes LibreSign versions from Nextcloud versions.
Use an administrator account and plan for adequate disk space and network
access if the application must download signing dependencies.

Install the app
---------------

#. Open Nextcloud's **Apps** administration page.
#. Search for **LibreSign** and install or enable the release offered for
   your compatible Nextcloud version.
#. Open the LibreSign administration settings and inspect **Configuration
   check** for resources requiring attention.
#. In **Dependencies**, use **Download binaries** if prompted, then
   **Validate setup** to check the installation. The operation can take time
   and requires server resources.
#. Configure the certificate engine and the **Root certificate data**
   appropriate to your organization. For the OpenSSL engine, the root
   certificate form asks for a **Common Name (CN)** and allows generating a
   root certificate when the installation requires it.
#. Resolve remaining configuration errors before sending real invitations.

The location and presentation of some settings differ between LibreSign
releases; see :doc:`configuration`. Do not regenerate an existing production
root certificate merely to repeat initial setup.

Check the installation
----------------------

Open LibreSign with a permitted user account. In a test environment, create
a request, complete its supported signing method, and open **Validate
signature** on the result. A successful installation check is not equivalent
to verifying mail delivery, external identity providers, or production
certificate policy; exercise those separately when enabled.
