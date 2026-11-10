Documents, signatures, and validation
=====================================

.. _main_screen:

Find your documents
-------------------

Open **LibreSign** in Nextcloud and choose **Files** to see documents and
signature requests available to you. Select a file to inspect its details
and signers. An individual signer can be **pending** or **signed**; do not
assume the entire request is complete merely because one person has signed.

.. _add_signature:

Request signatures
------------------

#. Choose **Request Signatures**. Use **Upload** for a PDF on your device,
   **Choose from Files** for an existing Nextcloud file, or **Upload from
   URL** if your administrator allows it.
#. Review the selected file before asking another person to sign.
#. Use **Search signer** to select a recipient or an allowed identification
   method, including an external email recipient where enabled.
#. Check the signer's name and identification details and select **Save**.
   Repeat for every required signer.
#. Configure the remaining signing steps shown by LibreSign and submit the
   request. Do not consider a draft a delivered invitation.
#. Open the request details in **Files** to see who is still pending.

Available signer identification methods, permissions, delivery channels, and
signing order depend on the administrator's configuration. Use the options
shown for your request rather than assuming every channel is enabled.

.. _sign_invitation:

Sign an invitation
------------------

#. Open the link supplied to you for the signing request; verify its sender
   before entering any personal information.
#. Read the PDF and check that you are the intended signer.
#. Complete any requested identification step. If LibreSign asks for a
   certificate or signature password, follow the instructions for your
   configured signing method.
#. Choose **Sign** or **Sign document** and confirm the operation.
#. Check for the completion message. If other signers remain, the request
   may still be in progress.

If the link is expired, rejected, or requires a method you cannot use,
contact the requester. Do not reuse someone else's invitation.

.. _see_signed_file:

Follow signing progress
-----------------------

Open the document details in **Files** and check the signer list. A signer
marked **pending** has not completed their part; **signed** records a completed
part. The document's overall completion depends on all required signatures
and the configured workflow. Download the final PDF when it becomes available.

.. _validate_document:

Validate a signature
--------------------

#. Open LibreSign's **Validate signature** page.
#. Choose **Upload** to select a PDF, drag and drop a PDF onto the page, or
   choose **From UUID** if you have the document identifier.
#. Run **Validation** and review the results, including certificate and
   signing information shown by the application.
#. Investigate any reported error instead of treating a visual stamp or QR
   code as conclusive proof of validity.

Validation evaluates the available cryptographic and certificate evidence.
It does not, by itself, determine every legal requirement in your jurisdiction.
