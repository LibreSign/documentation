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
    createElement(name) { return new Element(name); },
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
      this.classList = {
        names: new Set(),
        add(name) { this.names.add(name); },
        remove(name) { this.names.delete(name); },
        contains(name) { return this.names.has(name); },
      };
      this.style = {
        values: {},
        setProperty(name, value) { this.values[name] = value; },
      };
    }
    setAttribute(name, value) { (this.attributes ||= {})[name] = value; }
    appendChild(child) { child.parent = this; (this.children ||= []).push(child); }
    getBoundingClientRect() {
      if (this.kind === 'nav') return { left: 50, top: 20, width: 520, height: 40 };
      if (this.kind === 'summary') {
        return { left: 140 + 100 * this.parent.index, top: 55, width: 98, height: 35 };
      }
      if (this.kind === 'menu') {
        return { left: 140 + 100 * this.parent.index, top: 100,
          width: 225 + 20 * this.parent.index, height: 140 + 35 * this.parent.index };
      }
      return { left: 0, top: 0, width: 0, height: 0 };
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
      if (name === 'summary') return this.summary;
      if (name === '.libresign-nav-menu') return this.menu;
      throw new Error('Unexpected selector: ' + name);
    }
    querySelectorAll(name) {
      if (name === '.libresign-nav-group') return groups;
      if (name === ':scope > a') return links;
      throw new Error('Unexpected selector: ' + name);
    }
    focus() { document.activeElement = this; }
  }
  const nav = new Element('nav');
  const groups = Array.from({ length: 3 }, (_, index) => {
    const group = new Element('group', nav);
    group.index = index;
    group.summary = new Element('summary', group);
    group.menu = new Element('menu', group);
    group.link = new Element('a', group.menu);
    return group;
  });
  const links = [new Element('a', nav)];
  const outside = new Element('outside');
  const window = {
    handlers: {},
    addEventListener(name, fn) { this.handlers[name] = fn; },
    matchMedia() { return { matches: hover, addEventListener() {} }; },
  };
  vm.runInNewContext(script, { document, window });
  document.emit('DOMContentLoaded');
  return { document, groups, nav, links, outside, surface: nav.children[0], window };
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

test('shared surface travels and resizes between desktop menus without opening two', () => {
  const { groups, surface } = mount(true);
  assert.equal(surface.attributes['aria-hidden'], 'true');
  groups[0].emit('pointerenter', { pointerType: 'mouse' });
  assert.equal(surface.classList.contains('is-visible'), true);
  assert.equal(surface.style.transform, 'translate3d(90px, 80px, 0)');
  assert.equal(surface.style.width, '225px');
  assert.equal(surface.style.height, '140px');
  groups[1].emit('pointerenter', { pointerType: 'mouse' });
  assert.deepEqual(openGroups(groups), [1]);
  assert.equal(surface.style.transform, 'translate3d(190px, 80px, 0)');
  assert.equal(surface.style.width, '245px');
  assert.equal(surface.style.height, '175px');
  assert.equal(surface.style.values['--arrow-x'], '49px');
});

test('surface hides outside and updates when resizing an open menu', () => {
  const { groups, surface, nav, window } = mount(true);
  groups[2].emit('pointerenter', { pointerType: 'mouse' });
  assert.equal(surface.classList.contains('is-visible'), true);
  window.handlers.resize();
  assert.equal(surface.style.height, '210px');
  nav.emit('pointerleave', { pointerType: 'mouse' });
  assert.equal(surface.classList.contains('is-visible'), false);
});

test('touch mode does not show the animated surface', () => {
  const { groups, surface } = mount(false);
  groups[0].summary.emit('click', { detail: 1 });
  assert.equal(groups[0].open, true);
  assert.equal(surface.classList.contains('is-visible'), false);
});
