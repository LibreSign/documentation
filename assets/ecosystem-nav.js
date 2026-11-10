// SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
// SPDX-License-Identifier: CC-BY-3.0

(() => {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    const hoverMedia = window.matchMedia('(hover: hover) and (pointer: fine)');
    let keyboardNavigation = false;

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Tab' || event.key.startsWith('Arrow')) {
        keyboardNavigation = true;
      }
    });
    document.addEventListener('pointerdown', () => {
      keyboardNavigation = false;
    });

    for (const nav of document.querySelectorAll('.libresign-ecosystem-nav')) {
      const groups = [...nav.querySelectorAll('.libresign-nav-group')];
      const showOnly = (selected) => {
        for (const group of groups) group.open = group === selected;
      };

      for (const group of groups) {
        const summary = group.querySelector('summary');
        if (!summary) continue;

        group.addEventListener('pointerenter', (event) => {
          if (hoverMedia.matches && event.pointerType !== 'touch') showOnly(group);
        });
        summary.addEventListener('click', (event) => {
          event.preventDefault();
          // On desktop, a click must not close the submenu just opened on hover.
          if (hoverMedia.matches && event.detail !== 0) showOnly(group);
          else showOnly(group.open ? null : group);
        });
        group.addEventListener('toggle', () => {
          if (group.open) {
            for (const other of groups) {
              if (other !== group) other.open = false;
            }
          }
        });
      }

      for (const link of nav.querySelectorAll(':scope > a')) {
        link.addEventListener('pointerenter', (event) => {
          if (hoverMedia.matches && event.pointerType !== 'touch') showOnly(null);
        });
      }

      nav.addEventListener('pointerleave', (event) => {
        if (hoverMedia.matches && event.pointerType !== 'touch') showOnly(null);
      });
      nav.addEventListener('focusin', (event) => {
        if (!keyboardNavigation) return;
        const group = event.target.closest('.libresign-nav-group');
        showOnly(group && nav.contains(group) ? group : null);
      });
      nav.addEventListener('focusout', (event) => {
        if (!event.relatedTarget || !nav.contains(event.relatedTarget)) showOnly(null);
      });
      document.addEventListener('pointerdown', (event) => {
        if (!nav.contains(event.target)) showOnly(null);
      });
      document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        const opened = groups.find(group => group.open);
        if (!opened) return;
        event.preventDefault();
        opened.querySelector('summary')?.focus();
        showOnly(null);
      });
    }
  });
})();
