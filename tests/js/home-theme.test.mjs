// SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
// SPDX-License-Identifier: CC-BY-3.0

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../../assets/home-theme.js', import.meta.url), 'utf8');

function mount(storage = new Map(), storageAllowed = true, buttonExists = true) {
  const events = {};
  const attributes = {};
  const button = {
    hidden: true,
    attributes: {},
    title: '',
    handlers: {},
    setAttribute(key, value) { this.attributes[key] = value; },
    addEventListener(name, callback) { this.handlers[name] = callback; }
  };
  const document = {
    documentElement: {
      setAttribute(key, value) { attributes[key] = value; },
      getAttribute(key) { return attributes[key]; }
    },
    getElementById(id) {
      return id === 'themeSwitcher' && buttonExists ? button : null;
    },
    addEventListener(name, callback) { events[name] = callback; }
  };
  const localStorage = {
    getItem(key) {
      if (!storageAllowed) throw new Error('Storage blocked');
      return storage.get(key) ?? null;
    },
    setItem(key, value) {
      if (!storageAllowed) throw new Error('Storage blocked');
      storage.set(key, value);
    }
  };
  vm.runInNewContext(source, { document, localStorage });
  return {
    attributes, storage, button,
    ready() { events.DOMContentLoaded(); },
    click() { button.handlers.click(); },
    get theme() { return attributes['data-theme']; }
  };
}

test('default matches Sphinx manual dark mode and is applied before DOM ready', () => {
  const site = mount();
  assert.equal(site.theme, 'dark');
  assert.equal(site.storage.get('theme'), 'dark');
  site.ready();
  assert.equal(site.button.hidden, false);
  assert.equal(site.button.attributes['aria-pressed'], 'true');
  assert.equal(site.button.title, 'Switch to light mode');
});

test('saved light preference is shared with the manuals', () => {
  const storage = new Map([['theme','light']]);
  const site = mount(storage);
  assert.equal(site.theme, 'light');
  site.ready();
  assert.equal(site.button.attributes['aria-pressed'], 'false');
  site.click();
  assert.equal(site.theme, 'dark');
  assert.equal(storage.get('theme'), 'dark');
  const nextPage = mount(storage);
  assert.equal(nextPage.theme, 'dark');
  nextPage.ready();
  nextPage.click();
  assert.equal(nextPage.theme, 'light');
  assert.equal(storage.get('theme'), 'light');
});

test('saved dark preference displays light-mode action first', () => {
  const site = mount(new Map([['theme','dark']]));
  site.ready();
  assert.equal(site.button.title, 'Switch to light mode');
  site.click();
  assert.equal(site.theme, 'light');
  assert.equal(site.button.title, 'Switch to dark mode');
});

test('missing or invalid stored preference follows Sphinx fallback', () => {
  assert.equal(mount(new Map()).theme, 'dark');
  assert.equal(mount(new Map([['theme','other']])).theme, 'light');
});

test('blocked storage does not break the accessible toggle', () => {
  const site = mount(new Map(), false);
  assert.equal(site.theme, 'dark');
  site.ready();
  site.click();
  assert.equal(site.theme, 'light');
  assert.equal(site.button.attributes['aria-pressed'], 'false');
});

test('theme initialization works even when button is absent', () => {
  const site = mount(new Map([['theme','light']]), true, false);
  site.ready();
  assert.equal(site.theme, 'light');
});
