// SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
// SPDX-License-Identifier: CC-BY-3.0
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const workflow = JSON.parse(fs.readFileSync(new URL('./libresign-external-signature.json', import.meta.url), 'utf8'));
const nodes = new Map(workflow.nodes.map(n => [n.name, n]));
const code = (name, input, references = {}, extras = {}) => {
  const items = (Array.isArray(input) ? input : [input]).map(json => ({ json }));
  const $input = { first: () => items[0], all: () => items };
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
  maxSearchFolders: 50, maxAttempts: 3, waitSeconds: 5,
  pdfBase64: 'JVBERi0xLjQKc3ludGhldGlj' };
const created = { fileId: 17, fileUuid: 'synthetic-uuid' };
const row = status => ({ ocs: { meta: { status: 'ok' },
  data: { data: [{ id: 17, uuid: 'synthetic-uuid', status, nodeId: 100 }] } } });

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
  assert.equal(http.length, 6);
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
test('request validation rejects placeholders and unbounded WebDAV discovery', async () => {
  for (const bad of [
    { baseUrl: 'http://nc.example.test' },
    { baseUrl: 'https://nextcloud.example.invalid' },
    { signerEmail: 'signer@example.invalid' },
    { maxSearchFolders: 0 },
    { maxSearchFolders: 251 },
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
  const signed = (await code('Reconcile file state', row(3), ref(2)))[0].json;
  assert.equal(signed.signed, true);
  assert.equal(signed.sourceNodeId, 100);
  await assert.rejects(code('Reconcile file state', row(1), ref(3)));
  await assert.rejects(code('Reconcile file state', row(4), ref(1)));
  await assert.rejects(code('Reconcile file state', row(9), ref(1)));
  await assert.rejects(code('Reconcile file state', { ocs: { meta: { status: 'ok' },
    data: { data: [{ id: 17, uuid: created.fileUuid, status: 3 }] } } }, ref(1)));
  await assert.rejects(code('Reconcile file state', { ocs: { meta: { status: 'ok' }, data: { data: [] } } }, ref(1)));
});
const davRoot = '/remote.php/dav/files/integration-user/LibreSign/';
const folderHref = davRoot + '2026-11-11_Synthetic%20service%20agreement/';
const davFile = (href, fileid, size = 659) => ({
  'd:href': href,
  'd:propstat': { 'd:status': 'HTTP/1.1 200 OK', 'd:prop': {
    'oc:fileid': String(fileid), 'd:getcontenttype': 'application/pdf',
    'd:getcontentlength': String(size),
  } },
});
const davFolder = (files) => ({ 'd:multistatus': { 'd:response': [
  { 'd:href': folderHref, 'd:propstat': { 'd:status': 'HTTP/1.1 200 OK',
    'd:prop': { 'oc:fileid': '99', 'd:resourcetype': { 'd:collection': '' } } } },
  ...files,
] } });
const source = davFile(folderHref + 'synthetic.pdf', 100);
const final = davFile(folderHref + 'synthetic.signed_1.pdf', 101, 47799);
const davRefs = { 'Prepare request': config, 'Reconcile file state': { sourceNodeId: 100 } };

test('PROPFIND nodes use the same credential and parse WebDAV XML', () => {
  const http = workflow.nodes.filter(n => n.type === 'n8n-nodes-base.httpRequest');
  const dav = http.filter(n => n.parameters.method === 'PROPFIND');
  assert.equal(dav.length, 2);
  for (const n of dav) {
    const p = n.parameters;
    assert.equal(p.genericAuthType, 'httpBasicAuth');
    assert.equal(p.contentType, 'raw');
    assert.equal(p.rawContentType, 'application/xml');
    assert(p.body.includes('oc:fileid'));
    assert(p.headerParameters.parameters.some(x => x.name === 'Depth' && x.value === '1'));
    assert.equal(p.options.redirect.redirect.followRedirects, false);
  }
  assert.equal(nodes.get('Parse folder XML').type, 'n8n-nodes-base.xml');
  assert.equal(nodes.get('Parse file XML').type, 'n8n-nodes-base.xml');
});

test('WebDAV discovery accepts only bounded, direct, same-root folders', async () => {
  const folders = { 'd:multistatus': { 'd:response': [
    { 'd:href': davRoot }, { 'd:href': folderHref },
    { 'd:href': davRoot + 'foreign.pdf' },
    { 'd:href': '/remote.php/dav/files/another-user/LibreSign/other/' },
    { 'd:href': davRoot + '%2e%2e/' },
  ] } };
  const found = await code('Choose folders', folders, { 'Prepare request': config }, { URL: undefined });
  assert.equal(found.length, 1);
  assert.equal(found[0].json.folderHref, folderHref);
  await assert.rejects(code('Choose folders', folders, { 'Prepare request': { ...config, maxSearchFolders: 0 } }));
  await assert.rejects(code('Choose folders', { 'd:multistatus': { 'd:response': [
    { 'd:href': folderHref }, { 'd:href': folderHref },
  ] } }, { 'Prepare request': config }));
  await assert.rejects(code('Choose folders', { 'd:multistatus': { 'd:response': [
    { 'd:href': folderHref }, { 'd:href': davRoot + 'second/' },
  ] } }, { 'Prepare request': { ...config, maxSearchFolders: 1 } }));
  const unsafe = (await code('Choose folders', { 'd:multistatus': { 'd:response': [
    { 'd:href': davRoot + '../' }, { 'd:href': davRoot + '%2e%2e/' },
    { 'd:href': folderHref },
  ] } }, { 'Prepare request': config }));
  assert.equal(unsafe.length, 1);
  assert.equal(unsafe[0].json.folderHref, folderHref);
});

test('download path is learned from original oc:fileid and one authorized PDF sibling', async () => {
  const output = (await code('Resolve signed PDF', [davFolder([source, final])], davRefs, { URL: undefined }))[0].json;
  assert.equal(output.signedDavHref, final['d:href']);
  assert.equal(output.sourceNodeId, 100);
  assert.equal(output.candidateCount, 1);
  const download = nodes.get('Download signed PDF').parameters;
  assert(download.url.includes('signedDavHref'));
  assert(!download.url.includes('signedPdfPath'));
});

test('WebDAV discovery rejects wrong identity, missing signature, and ambiguous sibling', async () => {
  const r = name => code('Resolve signed PDF', [davFolder(name)], davRefs, { URL: undefined });
  await assert.rejects(r([source]));
  await assert.rejects(r([final]));
  await assert.rejects(r([source, final, davFile(folderHref + 'unexpected.pdf', 105, 1200)]));
  await assert.rejects(code('Resolve signed PDF', [davFolder([source, final])],
    { ...davRefs, 'Reconcile file state': { sourceNodeId: 200 } }));
  await assert.rejects(r([source, davFile(folderHref + '%2e%2e.pdf', 101, 50)]));
  await assert.rejects(r([source, davFile(folderHref + '../unexpected.pdf', 101, 50)]));
});

test('API and WebDAV requests retain authorization boundaries and no guessed endpoint', () => {
  const get = nodes.get('Get file state').parameters;
  assert(get.url.includes('/file/list'));
  assert(get.queryParameters.parameters.some(p => p.name === 'fileIds[]'));
  assert(nodes.get('Invite signer once').parameters.url.includes('/notify/signers'));
  assert(nodes.get('Create request').parameters.url.includes('/request-signature'));
  assert(nodes.get('List LibreSign folders').parameters.url.includes('remote.php/dav/files'));
  assert(nodes.get('Inspect folder files').parameters.url.includes('folderHref'));
  assert.equal(JSON.stringify(workflow).includes('/file/download/'), false);
  assert.equal(JSON.stringify(workflow).includes('signedPdfPath'), false);
});
