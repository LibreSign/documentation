<!-- SPDX-FileCopyrightText: 2026 LibreCode coop and contributors -->
<!-- SPDX-License-Identifier: CC-BY-3.0 -->

# LibreSign + n8n: external signer (C2)

This is an **importable n8n workflow** using public LibreSign OCS v1 requests and
an authenticated Nextcloud WebDAV download. It creates a **single-document,
one-email-signer** request, asks LibreSign to send the invitation, polls a
bounded number of times, and downloads an **already identified, authorized**
signed PDF. No custom n8n node, callback URL, direct database access, or
new LibreSign endpoint is needed.

[Import the workflow](libresign-external-signature.json). For equivalent cURL
and PHP flows, reuse the existing
[`external-email-signers` examples](../external-email-signers/) rather than
copying their implementation. **The JSON contains a small synthetic PDF, but
no account credential or live signer address.**

## Select the installed LibreSign release

`/ocs/v2.php/apps/libresign/api/v1` is the common **protocol prefix**, not
an application major version. The workflow's `Configure` node selects the
following exact request shape:

| LibreSign | Documentation branch | `identifyMethods[]` | Completion signal |
| --- | --- | --- | --- |
| 13 | [`stable13`](https://github.com/LibreSign/documentation/tree/stable13) | `mandatory: 1` | OCS polling |
| 14 | [`stable14`](https://github.com/LibreSign/documentation/tree/stable14) | `mandatory: 1` | OCS polling |
| 15 | [`stable15`](https://github.com/LibreSign/documentation/tree/stable15) | `requirement: "required"` | OCS polling |
| Development | [`main`](https://github.com/LibreSign/documentation/tree/main) | `requirement: "required"` | OCS polling; optional native events |

Check the [versioned OpenAPI](https://docs.libresign.coop/15/developer_manual/api/openapi.html)
for your *installed* release and the corresponding
[`request-13.json`/`request-14.json`/`request-15.json`/`request-main.json`
fixtures](../external-email-signers/). This example intentionally omits
`callback`, `signatureFlow`, and experimental policy fields.

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
4. For the **final download**, determine the actual signed PDF's *relative*
   path under the integration account's authenticated WebDAV folder.
   Discover it with Nextcloud Files or an authenticated WebDAV `PROPFIND`.
   **Do not assume that the uploaded filename is the signed filename** or
   derive a path from a LibreSign file ID, UUID, node ID, or invitation link.
   When the path is unknown in advance, test request/notification/status first
   and configure the final download only after the path is verified.

## Import and configure

1. In n8n open **Workflows → Import from File** and select
   [`libresign-external-signature.json`](libresign-external-signature.json).
   It is disabled by default and begins with a **Manual Trigger**.
2. Create a **Generic HTTP Basic Auth** credential in n8n: username is the
   Nextcloud integration account; password is its **App Password**. Associate
   *that same credential* with these four HTTP Request nodes: **Create request**,
   **Invite signer once**, **Get file state**, **Download signed PDF**.
   Credentials are deliberately **not** bound or exported in the JSON.
3. Edit only the public parameters in the **Configure** Code node:
   `baseUrl` (HTTPS Nextcloud origin, without `/ocs`), `version` (`13`, `14`,
   `15`, or `main`), `integrationUser`, `signerEmail` (a real **controlled test
   inbox**), `signedPdfPath` (verified path relative to the DAV user root),
   `maxAttempts`, and `waitSeconds`. Replace `pdfBase64` when testing your own
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
  -> file status 3: authorized WebDAV GET using a verified path
  -> file status 4, unknown status, OCS/HTTP error, or timeout: stop
GET  /remote.php/dav/files/USER/VERIFIED-PATH   (authenticated, same HTTPS origin)
  -> binary field signedPdf, PDF header check
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
- The workflow does **not** promise a guaranteed final signed-file path or
  generic `GET /file/download/{id}`: no such universal authorized endpoint
  is established by the reviewed public OpenAPI. Use WebDAV only with file
  read rights and the **verified completed file** path. `GET
  /file/validate/file_id/{fileId}` supplies authorization-checked metadata,
  not a PDF file download or automatic certificate-chain validation.

## Development: optional native event receiver

The `main` development documentation publishes native LibreSign event classes
for Nextcloud **Webhook Listeners**, notably
`OCA\Libresign\Events\SigningRequestCompletedEvent` and
`OCA\Libresign\Events\SigningRequestCanceledEvent`. See the
[event catalog](../../developer_manual/webhooks/event-catalog.rst) and
[configuration](../../developer_manual/webhooks/configuration.rst).

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
contract tests for the export, Code-node success/failure cases, status
transitions and authorization boundary. This tests **our export and logic**,
not n8n runtime import, a live Nextcloud, SMTP delivery, legal identity,
cryptographic signing, or a real WebDAV completion path. Execute that E2E
scenario in a disposable installation before using this in any real workflow.

References: [LibreSign API guide](../../developer_manual/api/external-email-signers.rst),
[integration lifecycle](../../developer_manual/integration/lifecycle.rst),
[n8n HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/),
[n8n Wait](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait/),
[n8n Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/),
[Nextcloud WebDAV](https://docs.nextcloud.com/server/stable/developer_manual/client_apis/WebDAV/basic.html).

**Navigation follow-up, not part of this PR:** once front C finishes editing
its versioned integration landing pages, add a link to this example from the
relevant architecture and external-email-signers guides on `main`,
`stable13`, `stable14`, and `stable15`, using independently reviewed version
links. Do not backport an event receiver to stable branches.
