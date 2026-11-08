<?php
/**
 * SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
 * SPDX-License-Identifier: CC-BY-3.0
 *
 * Synthetic LibreSign integration example, PHP 8.1+ with ext-curl.
 * No browser signing is performed by the integration service.
 */
declare(strict_types=1);

$mode = $argv[1] ?? '';
if (!in_array($mode, ['start', 'check', 'validate', 'retrieve'], true)) {
    fwrite(STDERR, "Usage: php flow.php start|check|validate|retrieve\n");
    exit(2);
}
function requiredEnv(string $name): string {
    $value = getenv($name);
    if ($value === false || $value === '') {
        throw new RuntimeException("Missing environment variable: " . $name);
    }
    return $value;
}
function fetchUrl(string $url, string $user, string $password, string $method = 'GET', ?array $json = null): string {
    $handle = curl_init($url);
    if ($handle === false) {
        throw new RuntimeException('Cannot create HTTP handle');
    }
    curl_setopt_array($handle, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_TIMEOUT => 90,
        CURLOPT_HTTPAUTH => CURLAUTH_BASIC,
        CURLOPT_USERPWD => $user . ':' . $password,
        CURLOPT_CUSTOMREQUEST => $method,
        CURLOPT_HTTPHEADER => $json === null
            ? ['OCS-APIRequest: true', 'Accept: application/json']
            : ['OCS-APIRequest: true', 'Accept: application/json', 'Content-Type: application/json'],
    ]);
    if ($json !== null) {
        curl_setopt($handle, CURLOPT_POSTFIELDS, json_encode($json, JSON_THROW_ON_ERROR));
    }
    $body = curl_exec($handle);
    $status = (int)curl_getinfo($handle, CURLINFO_HTTP_CODE);
    $error = curl_error($handle);
    curl_close($handle);
    if ($body === false || $status < 200 || $status >= 300) {
        throw new RuntimeException("HTTP request failed: status $status; $error");
    }
    return $body;
}
function ocs(string $api, string $user, string $password, string $path, string $method = 'GET', ?array $json = null): array {
    $body = fetchUrl($api . $path, $user, $password, $method, $json);
    $response = json_decode($body, true, 512, JSON_THROW_ON_ERROR);
    if (($response['ocs']['meta']['status'] ?? null) !== 'ok' || !isset($response['ocs']['data'])) {
        throw new RuntimeException('OCS application rejected request');
    }
    return $response['ocs']['data'];
}
try {
    $base = rtrim(requiredEnv('NC_BASE_URL'), '/');
    if (!str_starts_with($base, 'https://')) {
        throw new RuntimeException('NC_BASE_URL must use HTTPS');
    }
    $user = requiredEnv('NC_USER');
    $password = requiredEnv('NC_APP_PASSWORD');
    $api = $base . '/ocs/v2.php/apps/libresign/api/v1';
    switch ($mode) {
        case 'start':
            $email = requiredEnv('SIGNER_EMAIL');
            if (str_ends_with($email, '@example.test') || str_ends_with($email, '@example.invalid')) {
                throw new RuntimeException('Use a controlled deliverable test mailbox');
            }
            $pdf = file_get_contents(requiredEnv('PDF_PATH'));
            if ($pdf === false || !str_starts_with($pdf, '%PDF-')) {
                throw new RuntimeException('Unreadable or invalid synthetic PDF');
            }
            $payload = json_decode(file_get_contents(__DIR__ . '/request.json'), true, 512, JSON_THROW_ON_ERROR);
            $payload['file']['base64'] = base64_encode($pdf);
            $payload['signers'][0]['identifyMethods'][0]['value'] = $email;
            $created = ocs($api, $user, $password, '/request-signature', 'POST', $payload);
            $fileId = $created['id'] ?? null;
            $fileUuid = $created['uuid'] ?? null;
            if (!is_int($fileId) || !is_string($fileUuid) || $fileUuid === '') {
                throw new RuntimeException('Creation response lacks a valid file ID/UUID');
            }
            // notify: 0 in request.json prevents an automatic duplicate invitation.
            ocs($api, $user, $password, '/notify/signers', 'POST', [
                'fileId' => $fileId,
                'signers' => [['email' => $email]],
            ]);
            echo json_encode(['fileId' => $fileId, 'fileUuid' => $fileUuid, 'deliveryConfirmed' => false], JSON_PRETTY_PRINT), "\n";
            break;
        case 'check':
            $uuid = requiredEnv('FILE_UUID');
            $list = ocs($api, $user, $password, '/file/list?details=1');
            $matches = array_values(array_filter($list['data'] ?? [], fn(array $row) => ($row['uuid'] ?? null) === $uuid));
            if (!$matches) {
                throw new RuntimeException('File not present on this page or not accessible; check pagination');
            }
            echo json_encode($matches[0], JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR), "\n";
            break;
        case 'validate':
            $id = requiredEnv('FILE_ID');
            if (!ctype_digit($id)) {
                throw new RuntimeException('FILE_ID must be decimal');
            }
            $data = ocs($api, $user, $password, '/file/validate/file_id/' . $id . '?showValidateFile=0');
            $summary = array_intersect_key($data, array_flip(['id', 'uuid', 'status', 'statusText', 'signers', 'messages']));
            echo json_encode($summary, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR), "\n";
            break;
        case 'retrieve':
            $signedUrl = requiredEnv('SIGNED_DAV_URL');
            $prefix = $base . '/remote.php/dav/files/' . rawurlencode($user) . '/';
            if (!str_starts_with($signedUrl, $prefix)) {
                throw new RuntimeException('Signed URL must be under this user\'s verified DAV root');
            }
            $destination = requiredEnv('SIGNED_OUTPUT');
            $bytes = fetchUrl($signedUrl, $user, $password);
            if (!str_starts_with($bytes, '%PDF-')) {
                throw new RuntimeException('DAV file is not a PDF');
            }
            if (file_put_contents($destination, $bytes, LOCK_EX) === false) {
                throw new RuntimeException('Unable to save signed PDF');
            }
            echo "Saved PDF; validate embedded signatures and certificate trust separately.\n";
    }
} catch (Throwable $error) {
    // Never print request bodies, passwords, signed URLs, sign links, or PII.
    fwrite(STDERR, 'Integration failed: ' . $error->getMessage() . "\n");
    exit(1);
}
