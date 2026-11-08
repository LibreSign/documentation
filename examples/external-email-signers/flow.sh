#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
# SPDX-License-Identifier: CC-BY-3.0
set -euo pipefail
cd "$(dirname "$0")"
mode="${1:-}"
if [[ ! "$mode" =~ ^(start|check|validate|retrieve)$ ]]; then
  echo "Usage: $0 start|check|validate|retrieve" >&2
  exit 2
fi
: "${NC_BASE_URL:?Set HTTPS Nextcloud base URL}"
: "${NC_USER:?Set Nextcloud integration username}"
: "${NC_NETRC:?Set the path to a private curl netrc file (chmod 600)}"
if [[ "$NC_BASE_URL" != https://* ]]; then
  echo "NC_BASE_URL must be HTTPS" >&2; exit 2
fi
if [[ ! -f "$NC_NETRC" ]] || [[ "$(stat -c '%a' "$NC_NETRC")" != 600 ]]; then
  echo "NC_NETRC must exist and have mode 0600" >&2; exit 2
fi
api="${NC_BASE_URL%/}/ocs/v2.php/apps/libresign/api/v1"
ocs() {
  curl --fail-with-body --silent --show-error --netrc-file "$NC_NETRC" \
    --connect-timeout 10 --max-time 90 \
    -H 'OCS-APIRequest: true' -H 'Accept: application/json' "$@"
}
check_response() {
  jq -e '.ocs.meta.status == "ok" and .ocs.data != null' >/dev/null || {
    echo "Unexpected OCS envelope or unsuccessful OCS meta status" >&2
    exit 1
  }
}
case "$mode" in
  start)
    : "${SIGNER_EMAIL:?Use an inbox you control}"
    : "${PDF_PATH:?Use a synthetic PDF on disk}"
    if [[ "$SIGNER_EMAIL" == *"@example.test" || "$SIGNER_EMAIL" == *"@example.invalid" ]]; then
      echo "Replace the reserved synthetic email with a controlled test mailbox" >&2
      exit 2
    fi
    if [[ ! -r "$PDF_PATH" ]] || ! head -c 5 "$PDF_PATH" | grep -aq '^%PDF-'; then
      echo "PDF_PATH must point to a readable PDF" >&2; exit 2
    fi
    pdf64="$(base64 < "$PDF_PATH" | tr -d '\r\n')"
    payload="$(jq -c --arg pdf "$pdf64" --arg email "$SIGNER_EMAIL" \
      '.file.base64=$pdf | .signers[0].identifyMethods[0].value=$email' request.json)"
    result="$(printf '%s' "$payload" | ocs -X POST \
      -H 'Content-Type: application/json' --data-binary @- "$api/request-signature")"
    printf '%s' "$result" | check_response
    file_id="$(printf '%s' "$result" | jq -er '.ocs.data.id | numbers')"
    file_uuid="$(printf '%s' "$result" | jq -er '.ocs.data.uuid | strings')"
    # notify: 0 in the create payload prevents automatic duplicate invitations.
    notification="$(jq -nc --argjson fileId "$file_id" --arg email "$SIGNER_EMAIL" \
      '{fileId:$fileId,signers:[{email:$email}]}')"
    notify_result="$(printf '%s' "$notification" | ocs -X POST \
      -H 'Content-Type: application/json' --data-binary @- "$api/notify/signers")"
    printf '%s' "$notify_result" | check_response
    printf 'Created fileId=%s fileUuid=%s\n' "$file_id" "$file_uuid"
    printf 'Notification accepted for processing; delivery is NOT confirmed.\n'
    ;;
  check)
    : "${FILE_UUID:?Set the file UUID returned by start}"
    result="$(ocs "$api/file/list?details=1")"
    printf '%s' "$result" | check_response
    printf '%s' "$result" | jq -e --arg uuid "$FILE_UUID" \
      '.ocs.data.data[] | select(.uuid == $uuid) | {id,uuid,status,statusText,signers}'
    ;;
  validate)
    : "${FILE_ID:?Set the LibreSign file ID returned by start}"
    result="$(ocs "$api/file/validate/file_id/$FILE_ID?showValidateFile=0")"
    printf '%s' "$result" | check_response
    printf '%s' "$result" | jq '.ocs.data | {id,uuid,status,statusText,signers,messages}'
    ;;
  retrieve)
    : "${SIGNED_DAV_URL:?Set verified signed PDF WebDAV URL}"
    : "${SIGNED_OUTPUT:?Set private output PDF filename}"
    # Reject remote credentials exfiltration by unexpected origins or paths.
    prefix="${NC_BASE_URL%/}/remote.php/dav/files/$NC_USER/"
    if [[ "$SIGNED_DAV_URL" != "$prefix"* ]]; then
      echo "SIGNED_DAV_URL must be under the integration user's Nextcloud DAV root" >&2
      exit 2
    fi
    curl --fail-with-body --silent --show-error --netrc-file "$NC_NETRC" \
      --connect-timeout 10 --max-time 90 \
      --output "$SIGNED_OUTPUT" "$SIGNED_DAV_URL"
    if ! head -c 5 "$SIGNED_OUTPUT" | grep -aq '^%PDF-'; then
      rm -f "$SIGNED_OUTPUT"
      echo "Retrieved content was not a PDF" >&2; exit 1
    fi
    printf 'Saved PDF to %s; verify certificate trust separately.\n' "$SIGNED_OUTPUT"
    ;;
esac
