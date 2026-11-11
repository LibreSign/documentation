<!-- SPDX-FileCopyrightText: 2026 LibreCode coop and contributors -->
<!-- SPDX-License-Identifier: CC-BY-3.0 -->

# LibreSign + n8n: external signer (C2)

This is an **importable n8n workflow** using public LibreSign OCS v1 requests and
authenticated Nextcloud WebDAV discovery and download. It creates a
**single-document, one-email-signer** request, asks LibreSign to send the
invitation, polls a bounded number of times, then identifies the signed PDF
in the requester's own Nextcloud Files folder. It matches the OCS source
``nodeId`` to WebDAV ``oc:fileid`` and requires **exactly one other PDF in
that folder** before downloading the returned DAV path. No filename guess,
custom n8n node, callback URL, database access, or new LibreSign endpoint is
needed. Ambiguous or inaccessible files stop the workflow.

[Import the workflow](libresign-external-signature.json). For equivalent cURL
and PHP flows, reuse the existing
[`external-email-signers` examples](../external-email-signers/) rather than
copying their implementation. **The JSON contains a small synthetic PDF, but
no account credential or live signer address.**

## Select the installed LibreSign release

`/ocs/v2.php/apps/libresign/api/v1` is the common **protocol prefix**, not
an application major version. The workflow's `Configure` node selects the
following exact request shape:

| Installed LibreSign | `identifyMethods[]` | Completion signal |
| --- | --- | --- |
| 13 or 14 | `mandatory: 1` | OCS polling |
| 15 | `requirement: "required"` | OCS polling |
| Development (`main`) | `requirement: "required"` | OCS polling; optional native events |

Start with the [stable integration guide](https://docs.libresign.coop/stable/developer_manual/integration/index.html)
and [stable OpenAPI](https://docs.libresign.coop/stable/developer_manual/api/openapi.html).
The `/stable/` alias always follows the **newest released** LibreSign version,
not the version installed on your server. **If your installation is older,
select its exact LibreSign major** on the
[documentation version chooser](https://docs.libresign.coop/) before using
payloads, endpoints or OpenAPI schemas. `/latest/` is the **unreleased**
development documentation, following Nextcloud's convention; it is not a
replacement for stable documentation.

The [version-specific request fixtures](../external-email-signers/)
(`request-13.json`, `request-14.json`, `request-15.json`,
`request-main.json`) remain the source for the matching request body.
This example intentionally omits `callback`, `signatureFlow`, and
experimental policy fields.

## Prerequisites — use a disposable environment

1. An **isolated Nextcloud** installation with the matching LibreSign release,
   correct signing-certificate setup, writable storage, and an email identify
   method plus a permitted signing method (for example `clickToSign`).
   Configure an **inbox you control** or a test-only SMTP sink such as Mailpit.
   Never send this example to real recipients or use production services.
2. An **authorized integration account** that can create signature requests,
   view their state, and read the target signed file in Nextcloud Files.
   Create a revocable **App Password** from Nextcloud **Personal settings →
   Security**. Do not use a signer's credentials or the regular account password.
3. An n8n installation providing the built-in Manual Trigger, Code,
   HTTP Request, Loop Over Items, If, and Wait nodes. No community node,
   npm package, or public incoming webhook is required.
4. For **automatic final download**, the integration account needs to list
   its ``LibreSign/`` folder (the default local LibreSign file location), read
   the request's original PDF, and read the completed PDF. The example uses
   **authenticated WebDAV `PROPFIND`** to identify one eligible PDF sibling.
   It does not construct a filename from any LibreSign ID, UUID or invitation
   link. If the installation uses a custom folder, grants different access,
   or keeps more than one non-source PDF beside the original, discovery will
   stop for review rather than download an arbitrary file.

## Import and configure

1. In n8n open **Workflows → Import from File** and select
   [`libresign-external-signature.json`](libresign-external-signature.json).
   It is disabled by default and begins with a **Manual Trigger**.
2. Create a **Generic HTTP Basic Auth** credential in n8n: username is the
   Nextcloud integration account; password is its **App Password**. Associate
   *that same credential* with all six HTTP Request nodes: **Create request**,
   **Invite signer once**, **Get file state**, **List LibreSign folders**,
   **Inspect folder files**, **Download signed PDF**.
   Credentials are deliberately **not** bound or exported in the JSON.
3. Edit only the public parameters in the **Configure** Code node:
   `baseUrl` (HTTPS Nextcloud origin, without `/ocs`), `version` (`13`, `14`,
   `15`, or `main`), `integrationUser`, `signerEmail` (a real **controlled test
   inbox**), `maxSearchFolders` (limit on the number of request folders scanned,
   default 50, maximum 250), `maxAttempts`, and `waitSeconds`. Replace `pdfBase64` when testing your own
   *synthetic* PDF. The built-in sample is a one-page PDF without personal data.
4. Ensure Nextcloud's email/notification background jobs work. Click **Execute
   Workflow**. Open the controlled mailbox, follow the **LibreSign-issued**
   invitation and complete signing under the installed policy. The n8n run
   awaits the file status; it does **not** impersonate a signer.
5. After success, **Verify PDF bytes** outputs the binary property `signedPdf`
   and metadata including `fileId`, `fileUuid`, `downloadedBytes`, and
   `cryptographicSignatureVerified: false`. Use a separate trusted PDF
   signature verifier; checking `%PDF-` only verifies basic file format.

### What is sent and when

```text
POST /request-signature             (notify: 0; exactly one external email signer)
  -> OCS status + fileId/fileUuid
POST /notify/signers                (one explicit invitation request, not delivery proof)
  -> accepted for processing
GET  /file/list?details=1&fileIds[]=ID   (13/14/15; main uses details=true)
  -> file status 0/1/2: wait and retry, at most maxAttempts
  -> file status 3: authorized WebDAV discovery, then authenticated GET
  -> file status 4, unknown status, OCS/HTTP error, or timeout: stop
PROPFIND /remote.php/dav/files/USER/LibreSign/   (authenticated, Depth: 1)
  -> list request folders; reject unbounded or unsafe paths
PROPFIND /remote.php/dav/files/USER/LibreSign/REQUEST-FOLDER/   (authenticated, Depth: 1)
  -> find the original PDF by comparing OCS source nodeId to DAV oc:fileid
  -> require exactly one other non-empty PDF sibling and keep its actual DAV href
GET  ACTUAL-AUTHORIZED-DAV-HREF   (authenticated, same HTTPS origin)
  -> binary field signedPdf, PDF header check; independent PDF signature verification
```

A `fileId` is **not** the file UUID or a signer-scoped signing UUID. The
`GET /file/list` response is authorization-filtered: a missing row can mean
missing permissions, not deletion. Status `3` is a candidate completion
state for this **single document** only. Do not generalize this example to
envelopes, mixed rejection policies, or multi-signer workflows without also
checking child documents and each required signer.

### Failure behavior and security

- n8n's HTTP Request nodes do **not** follow redirects, do **not** accept
  arbitrary HTTP errors as success, and do **not** automatically retry POSTs.
  A timeout after creation or notification has an **ambiguous outcome**;
  reconcile the existing file ID/UUID before any manual retry.
- HTTP `401` means authentication failure; `403` means insufficient permission;
  `404` may be missing or inaccessible; `412` can indicate the absent
  `OCS-APIRequest: true` header; `422` can indicate policy/input rejection.
  The Code nodes also reject an unsuccessful `ocs.meta.status` even if the
  transport returned HTTP 2xx. Inspect safe error metadata without logging
  App Passwords, invitation URLs, request bodies, or signer PII.
- Polling is bounded (`20 × 30 s` by default; edit the values) and stops with
  an error instead of claiming completion when the budget expires. An actual
  document completion may occur between checks; use independent periodic
  reconciliation in longer-running systems.
- The original and final PDF, exported execution data, metadata, and binary
  may be retained by n8n. Restrict access, configure execution-data pruning,
  and follow your retention policy. Keep n8n's credential encryption key
  protected and revoke credentials when the integration is decommissioned.
- The workflow only lets LibreSign send invitations. `POST /notify/signers`
  being accepted is **not** SMTP delivery or receipt confirmation; do not
  send your own guessed signer URL or blindly re-send notifications.
- The workflow does **not** promise a universal file-ID download endpoint or
  signed filename: no such contract is established in the reviewed LibreSign
  OpenAPI. After checking status ``3``, it lists the **requester's own** DAV
  folder, matches the OCS source node ID to the returned DAV ``oc:fileid``,
  and downloads only an **unambiguous, non-empty PDF sibling** under the same
  folder. It stops when DAV access is denied, the folder cannot be found, the
  root contains more than `maxSearchFolders` subfolders, or there are zero or
  multiple candidate PDFs. This intentionally narrow discovery is **not a
  generalized resolver** for envelope/parallel signers, custom storage, or
  unlimited folders. It does not validate the PDF's cryptographic signature.
  `GET /file/validate/file_id/{fileId}` supplies authorization-checked
  metadata, not a PDF binary or automatic certificate-chain validation.

## Development: optional native event receiver

The `main` development documentation publishes native LibreSign event classes
for Nextcloud **Webhook Listeners**, notably
`OCA\Libresign\Events\SigningRequestCompletedEvent` and
`OCA\Libresign\Events\SigningRequestCanceledEvent`. See the
[development event catalog](https://docs.libresign.coop/latest/developer_manual/webhooks/event-catalog.html) and
[Webhook Listeners configuration](https://docs.libresign.coop/latest/developer_manual/webhooks/configuration.html).

A production-oriented alternative may receive those events with n8n's
**Webhook** node, configured with HTTPS and **Header Auth** or **Basic Auth**
(the receiver secret is an n8n credential, not part of the workflow export).
Authenticate the sender, store/deduplicate `event.eventId`, check
`event.contractVersion`, correlate `event.requestUuid` with a previously
created workflow, then **re-query OCS as the authorized requester** to
confirm the current status before deciding to download. Do not trust arrival
order, assume exactly-once delivery, or treat an event as a PDF access token.
Nextcloud background Cron/worker scheduling must be operational.

**Stable LibreSign 13–15 do not publish that native signing-completion
contract.** This importable example intentionally uses polling on every
release, including `main`, and does not require a proprietary callback.
Event delivery and receiver authentication require separate integration
verification; they are not represented as already tested here.

## Verification and evidence

`node --test examples/n8n/test-workflow.mjs` runs dependency-free, synthetic
contract tests for the export, Code-node success/failure cases, WebDAV
folder and file-ID correlation, ambiguity rejection, status transitions and
authorization boundaries. This tests **the export and its logic**, not n8n
runtime import, a live Nextcloud, SMTP delivery, legal identity, or
cryptographic signing. The discovery and final GET were also executed on a
**disposable Nextcloud 35 / LibreSign 15.0.12 / n8n 2.47.3 installation** with
one already signed synthetic PDF: the 21-node graph successfully retrieved
47,799 PDF bytes through authenticated WebDAV; `pdfsig` independently
confirmed a cryptographically valid signature from the test-only CA. The
creation, invitation, SMTP, external signing and polling were verified on
that installation in a separate earlier run. This is **not** an uninterrupted
end-to-end n8n run nor evidence of runtime compatibility with releases 13, 14,
or development. Revalidate in the target disposable release before using it
for live documents.

References: [LibreSign stable API guide](https://docs.libresign.coop/stable/developer_manual/api/external-email-signers.html),
[stable integration lifecycle](https://docs.libresign.coop/stable/developer_manual/integration/lifecycle.html),
[n8n HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/),
[n8n Wait](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait/),
[n8n Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/),
[Nextcloud WebDAV](https://docs.nextcloud.com/server/stable/developer_manual/client_apis/WebDAV/basic.html).

**Navigation follow-up, not part of this PR:** once front C finishes editing
its versioned integration landing pages, add a link to this example from the
relevant architecture and external-email-signers guides on `main`,
`stable13`, `stable14`, and `stable15`, using independently reviewed version
links. Do not backport an event receiver to stable branches.
