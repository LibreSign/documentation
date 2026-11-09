.. note::

   **LibreSign 16 on Nextcloud 36:** Subscribe only to the public
   ``OCA\\Libresign\\Events\\SigningRequestCompletedEvent`` when the installed
   application includes it. It implements ``IWebhookCompatibleEvent``
   and exposes contract version 1 with ``eventId``, ``requestUuid``,
   ``requestType`` and ``status``. It represents an aggregate transition
   to ``SIGNED``, not an individual signer action. See the
   :doc:`../webhooks/configuration` and
   :doc:`../webhooks/signing_completion` guides for registration,
   payloads and delivery constraints. Verify actual worker HTTP delivery
   before replacing polling or claiming end-to-end acceptance.
