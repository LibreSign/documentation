// SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
// SPDX-License-Identifier: CC-BY-3.0

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const script = readFileSync(new URL('../../assets/version-switcher.js', import.meta.url), 'utf8');

async function changeVersion({ root, current, path, wanted, exists }) {
  const requests = [];
  let ready;
  let destination;
  const picker = {
    value: current,
    options: [],
    handlers: {},
    closest: () => ({ dataset: { version: current, siteRoot: root } }),
    replaceChildren() { this.options = []; },
    appendChild(option) { this.options.push(option); },
    addEventListener(name, callback) { this.handlers[name] = callback; }
  };
  const notice = { textContent: '' };
  const document = {
    addEventListener(name, callback) { if (name === 'DOMContentLoaded') ready = callback(); },
    getElementById(id) {
      return id === 'libresign-version-select' ? picker : notice;
    },
    createElement() { return { value: '', textContent: '' }; }
  };
  const fetch = async (url, options) => {
    requests.push(url);
    if (url === root + '/versions.json') {
      return { ok: true, json: async () => ({ versions: [
        { slug: '15', status: 'current', nextcloud_min: 35, nextcloud_max: 35 },
        { slug: '14', status: 'previous', nextcloud_min: 34, nextcloud_max: 34 },
        { slug: '13', status: 'previous', nextcloud_min: 33, nextcloud_max: 33 },
        { slug: 'main', status: 'development', nextcloud_min: 36, nextcloud_max: 36 }
      ] }) };
    }
    assert.equal(options.method, 'HEAD');
    return { ok: exists };
  };
  const location = {
    pathname: path,
    search: '?source=review',
    hash: '#sample',
    assign(url) { destination = url; }
  };
  vm.runInNewContext(script, { document, fetch, location });
  await ready;
  picker.value = wanted;
  await picker.handlers.change();
  return { destination, requests, notice: notice.textContent, options: picker.options };
}

test('production version switch preserves an existing page', async () => {
  const result = await changeVersion({
    root: '', current: '15', path: '/15/developer_manual/api/openapi.html',
    wanted: '14', exists: true
  });
  assert.equal(result.destination, '/14/developer_manual/api/openapi.html?source=review#sample');
  assert.equal(result.requests[0], '/versions.json');
});

test('preview version switch never navigates to production origin', async () => {
  const base = '/site-preview/docs-preview/pr-126';
  const result = await changeVersion({
    root: base, current: '15', path: base + '/15/developer_manual/api/openapi.html',
    wanted: '13', exists: true
  });
  assert.equal(result.destination, base + '/13/developer_manual/api/openapi.html?source=review#sample');
  assert.deepEqual(result.requests, [base + '/versions.json', base + '/13/developer_manual/api/openapi.html']);
  assert.equal(result.options.length, 4);
});

test('missing page falls back to same manual inside preview', async () => {
  const base = '/site-preview/docs-preview/pr-126';
  const result = await changeVersion({
    root: base, current: 'main', path: base + '/main/developer_manual/api/guide-api.html',
    wanted: '15', exists: false
  });
  assert.equal(result.destination, base + '/15/developer_manual/?source=review#sample');
  assert.match(result.notice, /unavailable/);
});
