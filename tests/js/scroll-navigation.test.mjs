// SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
// SPDX-License-Identifier: CC-BY-3.0

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const script = readFileSync(new URL('../../assets/scroll-navigation.js', import.meta.url), 'utf8');

function mount({ desktop = true, initialY = 0, focused = false } = {}) {
  const listeners = {};
  const headerEvents = {};
  const headerClasses = new Set();
  const header = {
    offsetHeight: 80,
    classList: {
      add: name => headerClasses.add(name),
      remove: name => headerClasses.delete(name),
      toggle: (name, flag) => flag ? headerClasses.add(name) : headerClasses.delete(name),
    },
    focusTarget: {},
    contains: element => element === header.focusTarget,
    querySelector: name => {
      assert.equal(name, '.libresign-nav-group[open]');
      return header.hasOpenMenu ? {} : null;
    },
    addEventListener: (name, fn) => { headerEvents[name] = fn; },
    hasOpenMenu: false,
  };
  const document = {
    activeElement: focused ? header.focusTarget : {},
    querySelector: name => {
      assert.equal(name, '.libresign-scroll-header');
      return header;
    },
    addEventListener: (name, fn) => { listeners['document:' + name] = fn; },
  };
  const media = { matches: desktop, addEventListener: (name, fn) => { listeners['media:' + name] = fn; } };
  const window = {
    scrollY: initialY,
    matchMedia: () => media,
    addEventListener: (name, fn) => { listeners['window:' + name] = fn; },
  };
  vm.runInNewContext(script, { document, window });
  listeners['document:DOMContentLoaded']();
  const scroll = y => {
    window.scrollY = y;
    listeners['window:scroll']();
  };
  return {
    header, document, media, scroll, window,
    has: name => headerClasses.has(name),
    emit: (name, evt = {}) => listeners[name]?.(evt),
    focus: () => headerEvents.focusin(),
  };
}

test('desktop hides after meaningful downward scroll and reveals going up', () => {
  const state = mount();
  state.scroll(200);
  assert.equal(state.has('is-hidden'), true);
  state.scroll(185);
  assert.equal(state.has('is-hidden'), true);
  state.scroll(181);
  assert.equal(state.has('is-hidden'), false);
  assert.equal(state.has('is-scrolled'), true);
});

test('small scroll changes are ignored and returning to top reveals header', () => {
  const state = mount({ initialY: 220 });
  state.scroll(221);
  state.scroll(223);
  assert.equal(state.has('is-hidden'), false);
  state.scroll(260);
  assert.equal(state.has('is-hidden'), true);
  state.scroll(0);
  assert.equal(state.has('is-hidden'), false);
  assert.equal(state.has('is-scrolled'), false);
});

test('scrolling does not hide a focused header or an open dropdown', () => {
  const state = mount({ initialY: 250, focused: true });
  state.scroll(400);
  assert.equal(state.has('is-hidden'), false);
  state.document.activeElement = {};
  state.header.hasOpenMenu = true;
  state.scroll(510);
  assert.equal(state.has('is-hidden'), false);
  state.header.hasOpenMenu = false;
  state.scroll(550);
  assert.equal(state.has('is-hidden'), true);
  state.focus();
  assert.equal(state.has('is-hidden'), false);
});

test('touch-sized layout never hides header and recovers after resize', () => {
  const state = mount({ desktop: false });
  state.scroll(300);
  assert.equal(state.has('is-hidden'), false);
  state.media.matches = true;
  state.scroll(400);
  assert.equal(state.has('is-hidden'), true);
  state.media.matches = false;
  state.emit('media:change');
  assert.equal(state.has('is-hidden'), false);
});

test('keyboard traversal reveals a hidden navigation header', () => {
  const state = mount();
  state.scroll(400);
  assert.equal(state.has('is-hidden'), true);
  state.emit('document:keydown', { key: 'Tab' });
  assert.equal(state.has('is-hidden'), false);
});
