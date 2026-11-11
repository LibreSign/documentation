// SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
// SPDX-License-Identifier: CC-BY-3.0
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const workflow = JSON.parse(fs.readFileSync(new URL('./libresign-external-signature.json', import.meta.url), 'utf8'));
const nodes = new Map(workflow.nodes.map(n => [n.name, n]));
const code = (name, input, references = {}, extras = {}) => {
  const $input = { first: () => ({ json: input }) };
  const $ = name => ({
    first: () => ({ json: references[name] }),
    item: { json: references[name] },
  });
  return vm.runInNewContext(
    '(async () => { ' + nodes.get(name).parameters.jsCode + ' })()',
    { $input, $, URL, Number, Error, Array, String, console, ...extras },
    { timeout: 1000 }
  );
};
const config = { baseUrl: 'https://nc.example.test', version: '15',
  integrationUser: 'integration-user', signerEmail: 'signer@controlled.test',
  signedPdfPath: 'Contracts/signed.pdf', maxAttempts: 3, waitSeconds: 5,
  pdfBase64: 'JVBERi0xLjQKc3ludGhldGlj' };
const created = { fileId: 17, fileUuid: 'synthetic-uuid' };
const row = status => ({ ocs: { meta: { status: 'ok' },
  data: { data: [{ id: 17, uuid: 'synthetic-uuid', status }] } } });

test('workflow imports as a connected, manual, inactive graph', () => {
  assert.equal(workflow.active, false);
  assert.equal(nodes.get('Manual trigger').type, 'n8n-nodes-base.manualTrigger');
  assert.equal(nodes.size, workflow.nodes.length);
  const names = [...nodes.keys()];
  const reachable = new Set(['Manual trigger']);
  for (let i = 0; i < names.length; i++) {
    for (const current of [...reachable]) {
      for (const port of workflow.connections[current]?.main ?? [])
        for (const next of port) reachable.add(next.node);
    }
  }
  assert.deepEqual([...reachable].sort(), names.sort());
});
test('export contains no authentication material and does not automatically retry POST', () => {
  assert.equal(workflow.nodes.some(n => n.credentials), false);
  const http = workflow.nodes.filter(n => n.type === 'n8n-nodes-base.httpRequest');
  assert.equal(http.length, 4);
  assert(http.every(n => n.parameters.authentication === 'genericCredentialType'));
  assert(http.every(n => n.parameters.genericAuthType === 'httpBasicAuth'));
  assert(http.every(n => !n.parameters.options?.retry));
  assert(http.every(n => n.parameters.options?.redirect?.redirect?.followRedirects === false));
  assert.equal(JSON.stringify(workflow).includes('callback'), false);
});
test('request payload matches 13/14 vs 15/main versioned identity contracts', async () => {
  for (const version of ['13', '14', '15', 'main']) {
    const out = (await code('Prepare request', { ...config, version }))[0].json.requestBody;
    const identity = out.signers[0].identifyMethods[0];
    assert.equal(identity.method, 'email');
    assert.equal(out.signers[0].notify, 0);
    assert.equal(identity.value, config.signerEmail);
    assert.deepEqual(Object.keys(identity).sort(),
      (['method','value', version === '13' || version === '14' ? 'mandatory' : 'requirement']).sort());
  }
});
test('request validation rejects placeholders and unsafe WebDAV paths', async () => {
  for (const bad of [
    { baseUrl: 'http://nc.example.test' },
    { baseUrl: 'https://nextcloud.example.invalid' },
    { signerEmail: 'signer@example.invalid' },
    { signedPdfPath: '../secret.pdf' },
    { signedPdfPath: 'Contracts//signed.pdf' },
    { maxAttempts: 0 },
  ]) await assert.rejects(code('Prepare request', { ...config, ...bad }));
});
test('request validation works inside n8n Code without global URL', async () => {
  const input = { ...config, baseUrl: 'https://nc.example.test:8443/' };
  const output = (await code('Prepare request', input, {}, { URL: undefined }))[0].json;
  assert.equal(output.baseUrl, 'https://nc.example.test:8443');
  for (const baseUrl of [
    'https://user:pass@nc.example.test',
    'https://nc.example.test/path',
    'https://nc.example.test?x=1',
    'https://nc.example.test:99999',
    'https://nc.example.test:0',
  ]) await assert.rejects(code('Prepare request', { ...input, baseUrl }, {}, { URL: undefined }));
});
test('creation/notification require successful OCS envelope', async () => {
  const response = { ocs: { meta: { status: 'ok' }, data: { id: 17, uuid: created.fileUuid } } };
  const out = (await code('Verify created', response))[0].json;
  assert.equal(out.fileId, 17);
  await assert.rejects(code('Verify created', { ocs: { meta: { status: 'failure' }, data: response.ocs.data } }));
  const notified = (await code('Verify invite accepted', { ocs: { meta: { status: 'ok' }, data: {} } }))[0].json;
  assert.equal(notified.deliveryConfirmed, false);
  await assert.rejects(code('Verify invite accepted', { ocs: { meta: { status: 'failure' }, data: {} } }));
});
test('polling handles pending, terminal, missing, and budget exhaustion', async () => {
  const ref = attempt => ({
    'Verify created': created,
    'Poll attempts': { attempt },
    'Prepare request': config,
  });
  assert.equal((await code('Reconcile file state', row(1), ref(1)))[0].json.signed, false);
  assert.equal((await code('Reconcile file state', row(3), ref(2)))[0].json.signed, true);
  await assert.rejects(code('Reconcile file state', row(1), ref(3)));
  await assert.rejects(code('Reconcile file state', row(4), ref(1)));
  await assert.rejects(code('Reconcile file state', row(9), ref(1)));
  await assert.rejects(code('Reconcile file state', { ocs: { meta: { status: 'ok' }, data: { data: [] } } }, ref(1)));
});
test('file and WebDAV requests use authorization; there is no inferred PDF URL', () => {
  const download = nodes.get('Download signed PDF').parameters;
  assert(download.url.includes('signedPdfPath'));
  assert(download.url.includes('remote.php/dav/files'));
  assert(download.url.includes('encodeURIComponent'));
  assert(download.url.includes('integrationUser'));
  const get = nodes.get('Get file state').parameters;
  assert(get.url.includes('/file/list'));
  assert(get.queryParameters.parameters.some(p => p.name === 'fileIds[]'));
  assert(nodes.get('Invite signer once').parameters.url.includes('/notify/signers'));
  assert(nodes.get('Create request').parameters.url.includes('/request-signature'));
});
