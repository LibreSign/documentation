Getting started
===============

Choose the path that matches your role. An administrator must install and
configure LibreSign before users can request signatures.

I want to request signatures
----------------------------

#. Sign in to the Nextcloud instance where LibreSign is enabled.
#. Open **LibreSign** and find **Request Signatures** or the request action
   in the **Files** screen.
#. Select a PDF using **Upload**, **Choose from Files**, or **Upload from URL**
   when those options are available to your account.
#. Follow :ref:`add_signature` to add recipients and send the request.

If the request controls are missing, ask your administrator whether your
account is permitted to create requests.

I received a signing invitation
-------------------------------

#. Open the invitation link from the requester and check the document and
   requested identity details before proceeding.
#. Follow the on-screen signing steps. Depending on the configured signing
   method, LibreSign may ask you to define a signature, provide a password,
   upload a certificate, or complete identity verification.
#. Review the confirmation before submitting. See :ref:`sign_invitation`.

External email signers can use the invitation workflow without a Nextcloud
account when that identification method is enabled by the administrator.
Do not forward a personal invitation link to another person.

I want to verify a signed document
----------------------------------

Use :ref:`validate_document` to check a signed PDF or a document UUID. The
validation result must be reviewed; an image of a handwritten signature is not
by itself evidence of a valid digital signature.
