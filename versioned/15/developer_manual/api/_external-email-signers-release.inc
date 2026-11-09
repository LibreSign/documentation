**Release:** LibreSign |LibreSignRelease|, Nextcloud |NextcloudRelease|.
**Executable request template:** ``request-15.json``.
This template is specific to the published application contract.

.. code-block:: json

   {
     "name": "Synthetic service agreement",
     "status": 1,
     "file": {
       "name": "synthetic.pdf",
       "base64": "REPLACE_WITH_BASE64"
     },
     "signers": [
       {
         "displayName": "External Test Signer",
         "notify": 0,
         "identifyMethods": [
           {
             "method": "email",
             "value": "signer@example.test",
             "requirement": "required"
           }
         ]
       }
     ]
   }

Select the documentation line before running either client:

.. code-block:: bash

   export LIBRESIGN_DOC_LINE=15

This release requires ``requirement: "required"`` on an email identify
method, not the old integer ``mandatory``. Its ``POST /request-signature``
does **not** declare ``signatureFlow``: do not send that request field.
Use verified effective server policies and inspect the returned flow.
The signer schema also declares ``geolocationRequired``; do not
assume this option is available in earlier releases.

The cited browser tests belong to application branch ``stable35``;
the exact source commit used in this build is in the linked provenance:

* `Guest signing and visible signature <https://github.com/LibreSign/libresign/blob/stable35/playwright/e2e/sign-envelope-unauthenticated-visible-signature.spec.ts>`_
* `Unauthenticated email-token signing <https://github.com/LibreSign/libresign/blob/stable35/playwright/e2e/sign-email-token-unauthenticated.spec.ts>`_
* `Sequential signing <https://github.com/LibreSign/libresign/blob/stable35/playwright/e2e/multi-signer-sequential.spec.ts>`_

**Evidence limit:** source tests are present; their existence does not
prove that SMTP, browser behavior or PDF signing passed in this deployment.
