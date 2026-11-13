**Release:** LibreSign |LibreSignRelease|, Nextcloud |NextcloudRelease|.
**Executable request template:** ``request-14.json``.
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
             "mandatory": 1
           }
         ]
       }
     ]
   }

Select the documentation line before running either client:

.. code-block:: bash

   export LIBRESIGN_DOC_LINE=14

This release requires the integer ``mandatory`` on an email identify method;
``requirement`` is not part of this release's declared identity schema.
Its ``POST /request-signature`` accepts ``signatureFlow`` with values
``parallel`` and ``ordered_numeric``. Supply signer ``signingOrder`` when
the configured flow is ordered.

The cited browser tests belong to application branch ``stable34``;
the exact source commit used in this build is in the linked provenance:

* `Guest signing and visible signature <https://github.com/LibreSign/libresign/blob/stable34/playwright/e2e/sign-envelope-unauthenticated-visible-signature.spec.ts>`_
* `Unauthenticated email-token signing <https://github.com/LibreSign/libresign/blob/stable34/playwright/e2e/sign-email-token-unauthenticated.spec.ts>`_
* `Sequential signing <https://github.com/LibreSign/libresign/blob/stable34/playwright/e2e/multi-signer-sequential.spec.ts>`_
