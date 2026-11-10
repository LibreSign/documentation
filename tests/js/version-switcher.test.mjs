// SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
// SPDX-License-Identifier: CC-BY-3.0

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const script = readFileSync(new URL('../../assets/version-switcher.js', import.meta.url), 'utf8');

class Element {
  constructor(tag = 'div') {
    this.tag = tag;
    this.dataset = {};
    this.children = [];
    this.attributes = {};
    this.handlers = {};
    this.hidden = false;
    this.parent = null;
    this.classList = {
      active: false,
      toggle: (name, value) => {
        if (name === 'shift-up') this.classList.active = value;
      }
    };
  }
  addEventListener(name, callback) { this.handlers[name] = callback; }
  setAttribute(name, value) { this.attributes[name] = value; }
  append(...children) {
    for (const child of children) {
      this.children.push(child);
      child.parent = this;
    }
  }
  appendChild(child) { this.append(child); }
  replaceChildren(...children) {
    this.children = [];
    this.append(...children);
  }
  closest(selector) {
    if (selector === '[data-version-target]' && this.dataset.versionTarget) return this;
    return this.parent?.closest(selector) || null;
  }
  contains(other) {
    return other === this || this.children.some(child => child.contains(other));
  }
  focus() { this.focused = true; }
}

async function mount({ root = '', current = '15', manual = 'developer_manual', path,
                       wanted, exists = true, fetchFails = false }) {
  const requests = [];
  let destination;
  const picker = new Element('nav');
  picker.dataset = { version: current, siteRoot: root, manual };
  const toggle = new Element('button');
  const menu = new Element('div');
  menu.hidden = true;
  const list = new Element('ul');
  const notice = new Element('p');
  picker.append(toggle, menu);
  menu.append(list);
  const elements = {
    'libresign-release-picker': picker,
    'libresign-version-toggle': toggle,
    'libresign-version-menu': menu,
    'libresign-version-list': list,
    'libresign-version-notice': notice
  };
  const document = {
    handlers: {},
    addEventListener(name, callback) { this.handlers[name] = callback; },
    getElementById(id) { return elements[id] ?? null; },
    createElement(tag) { return new Element(tag); }
  };
  const entries = [
    { slug: '15', status: 'current', nextcloud_min: 35, nextcloud_max: 35 },
    { slug: '14', status: 'previous', nextcloud_min: 34, nextcloud_max: 34 },
    { slug: '13', status: 'previous', nextcloud_min: 33, nextcloud_max: 33 },
    { slug: 'main', status: 'development', nextcloud_min: 36, nextcloud_max: 36 }
  ];
  const fetch = async (url, options) => {
    requests.push(url);
    if (url === root + '/versions.json') {
      if (fetchFails) throw new Error('offline');
      return { ok: true, json: async () => ({ versions: entries }) };
    }
    assert.equal(options.method, 'HEAD');
    return { ok: exists };
  };
  const location = {
    pathname: path ?? root + '/' + current + '/' + manual + '/api/openapi.html',
    search: '?source=review',
    hash: '#sample',
    assign(url) { destination = url; }
  };
  vm.runInNewContext(script, { document, fetch, location });
  await document.handlers.DOMContentLoaded();
  async function select(slug) {
    const li = list.children.find(row => row.children[0].dataset.versionTarget === slug);
    assert.ok(li, 'option exists for ' + slug);
    let prevented = false;
    await list.handlers.click({
      target: li.children[0],
      preventDefault() { prevented = true; }
    });
    return prevented;
  }
  return {
    picker, toggle, menu, list, notice, requests, document,
    select, getDestination: () => destination
  };
}

test('upcoming development comes first; stable support labels are clear', async () => {
  const ui = await mount({});
  const links = ui.list.children.map(li => li.children[0]);
  assert.deepEqual(links.map(a => a.dataset.versionTarget), ['main', '15', '14', '13']);
  assert.equal(links[1].attributes['aria-current'], 'true');
  assert.equal(links[0].children[1].textContent, 'Not released');
  assert.equal(links[1].children[1].textContent, 'Latest stable');
  assert.equal(links[3].children[1].textContent, 'Oldest documented');
});

test('menu starts collapsed, opens on click and closes with Escape', async () => {
  const ui = await mount({});
  assert.equal(ui.menu.hidden, true);
  ui.toggle.handlers.click();
  assert.equal(ui.menu.hidden, false);
  assert.equal(ui.toggle.attributes['aria-expanded'], 'true');
  assert.equal(ui.picker.classList.active, true);
  ui.document.handlers.keydown({ key: 'Escape' });
  assert.equal(ui.menu.hidden, true);
  assert.equal(ui.toggle.attributes['aria-expanded'], 'false');
  assert.equal(ui.toggle.focused, true);
});

test('production switch preserves existing deep page and anchor', async () => {
  const ui = await mount({});
  ui.toggle.handlers.click();
  assert.equal(await ui.select('14'), true);
  assert.equal(ui.getDestination(), '/14/developer_manual/api/openapi.html?source=review#sample');
  assert.deepEqual(ui.requests, ['/versions.json', '/14/developer_manual/api/openapi.html']);
});

test('preview switch stays in same PR origin', async () => {
  const root = '/site-preview/docs-preview/pr-126';
  const ui = await mount({ root });
  await ui.select('13');
  assert.equal(ui.getDestination(), root + '/13/developer_manual/api/openapi.html?source=review#sample');
});

test('missing development-only page falls back to target manual without obsolete anchor', async () => {
  const root = '/site-preview/docs-preview/pr-126';
  const ui = await mount({
    root, current: 'main', exists: false,
    path: root + '/main/developer_manual/api/guide-api.html'
  });
  await ui.select('15');
  assert.equal(ui.getDestination(), root + '/15/developer_manual/?source=review');
  assert.match(ui.notice.textContent, /not available/);
});

test('manual index fallback still works when catalog fetch is unavailable', async () => {
  const ui = await mount({ fetchFails: true });
  // Static links are rendered by Sphinx even if the catalog endpoint fails.
  assert.equal(ui.requests[0], '/versions.json');
  assert.equal(ui.list.children.length, 0);
  ui.toggle.handlers.click();
  assert.equal(ui.menu.hidden, false);
  ui.document.handlers.click({ target: new Element('body') });
  assert.equal(ui.menu.hidden, true);
});
