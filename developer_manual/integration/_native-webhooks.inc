.. note::

   **Development line (LibreSign 16 / Nextcloud 36):** The application source
   now implements the aggregate ``SigningRequestCompletedEvent`` using
   Nextcloud's ``IWebhookCompatibleEvent``. It represents a document or
   envelope workflow changing to ``SIGNED``, not each individual signature.
   This is a source-level contract; verify installed event availability,
   Nextcloud worker HTTP delivery and receiver authentication before use.
   The administrator and payload reference is maintained specifically in
   `LibreSign 16's Webhooks guide
   <https://github.com/LibreSign/documentation/blob/main/versioned/16/developer_manual/webhooks/index.rst>`_.
