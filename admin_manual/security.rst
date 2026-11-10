Security and trust
==================

Protect signing credentials
---------------------------

Restrict administrator access to certificate configuration and any signing
keys. Protect backups and limit access to credentials; do not copy private
keys into public reports or screenshots. Keep Nextcloud, LibreSign, and the
underlying TLS configuration maintained.

Certificate lifecycle
---------------------

LibreSign's **Root certificate data** interface provides a root certificate
configuration. The OpenSSL engine explicitly warns that **Regenerate root
certificate** invalidates existing signing keys. Treat regeneration as a
planned key lifecycle or recovery operation, not as ordinary maintenance.
Prepare and test a recovery and validation plan before changing a trust
anchor used by existing documents.

Signers and access
------------------

Review which accounts may create requests and which identification methods
are available to external signers. A signing invitation is sensitive: avoid
publishing the link or including it in a public issue. Test the separation
between request owner, intended signer, and unrelated users when configuring
external access.

Validation and compliance
-------------------------

Provide recipients with a way to validate signed PDFs. Technical signature
validation and certificate status do not by themselves prove legal compliance
in every jurisdiction or that a signer's identity was established to a
particular assurance level. Document applicable organizational rules
separately from the application's cryptographic capabilities.
