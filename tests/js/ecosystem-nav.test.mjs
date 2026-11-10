// SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
// SPDX-License-Identifier: CC-BY-3.0

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const script = readFileSync(new URL('../../assets/ecosystem-nav.js', import.meta.url), 'utf8');

function mount(hover) {
  const document = {
    handlers: {},
    activeElement: null,
    addEventListener(name, fn) {
      (this.handlers[name] ||= []).push(fn);
    },
    querySelectorAll(name) {
      assert.equal(name, '.libresign-ecosystem-nav');
      return [nav];
    },
    emit(name, event = {}) {
      for (const fn of this.handlers[name] || []) fn(event);
    },
  };

  class Element {
    constructor(kind, parent = null) {
      this.kind = kind;
      this.parent = parent;
      this.handlers = {};
      this.open = false;
    }
    addEventListener(name, fn) { (this.handlers[name] ||= []).push(fn); }
    emit(name, options = {}) {
      const event = { target: this, preventDefault() { this.prevented = true; }, ...options };
      for (const fn of this.handlers[name] || []) fn(event);
      return event;
    }
    contains(node) {
      for (let here = node; here; here = here.parent) if (here === this) return true;
      return false;
    }
    closest(selector) {
      assert.equal(selector, '.libresign-nav-group');
      for (let here = this; here; here = here.parent) {
        if (here.kind === 'group') return here;
      }
      return null;
    }
    querySelector(name) {
      assert.equal(name, 'summary');
      return this.summary;
    }
    querySelectorAll(name) {
      if (name === '.libresign-nav-group') return groups;
      if (name === ':scope > a') return links;
      throw new Error('Unexpected selector: ' + name);
    }
    focus() { document.activeElement = this; }
  }
  const nav = new Element('nav');
  const groups = Array.from({ length: 3 }, () => {
    const group = new Element('group', nav);
    group.summary = new Element('summary', group);
    group.link = new Element('a', group);
    return group;
  });
  const links = [new Element('a', nav)];
  const outside = new Element('outside');
  vm.runInNewContext(script, {
    document,
    window: { matchMedia() { return { matches: hover }; } }
  });
  document.emit('DOMContentLoaded');
  return { document, groups, nav, links, outside };
}

function openGroups(groups) {
  return groups.map((group, i) => group.open ? i : null).filter(i => i !== null);
}

test('desktop opens on hover, switches groups and closes on leaving navigation', () => {
  const { groups, nav, links } = mount(true);
  groups[0].emit('pointerenter', { pointerType: 'mouse' });
  assert.deepEqual(openGroups(groups), [0]);
  groups[1].emit('pointerenter', { pointerType: 'mouse' });
  assert.deepEqual(openGroups(groups), [1]);
  const click = groups[1].summary.emit('click', { detail: 1 });
  assert.equal(click.prevented, true);
  assert.deepEqual(openGroups(groups), [1]);
  links[0].emit('pointerenter', { pointerType: 'mouse' });
  assert.deepEqual(openGroups(groups), []);
  groups[2].emit('pointerenter', { pointerType: 'mouse' });
  nav.emit('pointerleave', { pointerType: 'mouse' });
  assert.deepEqual(openGroups(groups), []);
});

test('touch uses click and never leaves two groups open', () => {
  const { groups, nav, document } = mount(false);
  groups[0].emit('pointerenter', { pointerType: 'touch' });
  assert.deepEqual(openGroups(groups), []);
  document.emit('pointerdown', { target: groups[0].summary });
  nav.emit('focusin', { target: groups[0].summary });
  groups[0].summary.emit('click', { detail: 1 });
  assert.deepEqual(openGroups(groups), [0]);
  groups[1].summary.emit('click', { detail: 1 });
  assert.deepEqual(openGroups(groups), [1]);
  groups[1].summary.emit('click', { detail: 1 });
  assert.deepEqual(openGroups(groups), []);
});

test('outside pointer closes submenu; clicking inside does not', () => {
  const { document, outside, groups } = mount(false);
  groups[0].summary.emit('click', { detail: 1 });
  document.emit('pointerdown', { target: groups[0].link });
  assert.deepEqual(openGroups(groups), [0]);
  document.emit('pointerdown', { target: outside });
  assert.deepEqual(openGroups(groups), []);
});

test('keyboard Tab opens focused group and Escape closes and restores focus', () => {
  const { groups, nav, document, outside } = mount(true);
  document.emit('keydown', { key: 'Tab' });
  nav.emit('focusin', { target: groups[0].summary });
  assert.deepEqual(openGroups(groups), [0]);
  nav.emit('focusin', { target: groups[1].summary });
  assert.deepEqual(openGroups(groups), [1]);
  const escaped = { key: 'Escape', preventDefault() { this.prevented = true; } };
  document.emit('keydown', escaped);
  assert.equal(escaped.prevented, true);
  assert.equal(document.activeElement, groups[1].summary);
  assert.deepEqual(openGroups(groups), []);
  nav.emit('focusout', { relatedTarget: outside });
  assert.deepEqual(openGroups(groups), []);
});

test('native details toggle and pointer focus do not reopen closed menus', () => {
  const { groups, nav, document, outside } = mount(true);
  groups[0].open = true;
  groups[1].open = true;
  groups[1].emit('toggle');
  assert.deepEqual(openGroups(groups), [1]);
  document.emit('pointerdown', { target: groups[1].summary });
  nav.emit('focusin', { target: groups[0].summary });
  assert.deepEqual(openGroups(groups), [1]);
  document.emit('pointerdown', { target: outside });
  assert.deepEqual(openGroups(groups), []);
});
