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
      const shell = nav.closest('.libresign-nav-shell');
      const toggle = shell?.querySelector('.libresign-nav-toggle');
      const isCompact = () => !!toggle && toggle.getClientRects().length > 0;
      const groups = [...nav.querySelectorAll('.libresign-nav-group')];
      // A single surface transitions its position and size between submenus.
      // The native details elements retain keyboard and touch behavior.
      const surface = document.createElement('div');
      surface.className = 'libresign-nav-surface';
      surface.setAttribute('aria-hidden', 'true');
      nav.appendChild(surface);
      nav.classList.add('libresign-nav-animated');

      const moveSurface = (group) => {
        if (!group || !hoverMedia.matches || isCompact()) {
          surface.classList.remove('is-visible');
          return;
        }
        const menu = group.querySelector('.libresign-nav-menu');
        const trigger = group.querySelector('summary');
        if (!menu || !trigger) return;

        const bounds = menu.getBoundingClientRect();
        const container = nav.getBoundingClientRect();
        const anchor = trigger.getBoundingClientRect();
        if (!bounds.width || !bounds.height) return;

        surface.style.width = `${bounds.width}px`;
        surface.style.height = `${bounds.height}px`;
        surface.style.transform = `translate3d(${bounds.left - container.left}px, ${bounds.top - container.top}px, 0)`;
        const arrowX = Math.max(15, Math.min(bounds.width - 15,
          anchor.left + anchor.width / 2 - bounds.left));
        surface.style.setProperty('--arrow-x', `${arrowX}px`);
        surface.classList.add('is-visible');
      };
      const showOnly = (selected) => {
        for (const group of groups) group.open = group === selected;
        moveSurface(selected);
      };

      const closeCompact = (restoreFocus = false) => {
        if (!shell?.classList.contains('is-open')) return;
        shell.classList.remove('is-open');
        toggle?.setAttribute('aria-expanded', 'false');
        showOnly(null);
        if (restoreFocus) toggle?.focus();
      };
      toggle?.addEventListener('click', () => {
        const willOpen = !shell.classList.contains('is-open');
        shell.classList.toggle('is-open', willOpen);
        toggle.setAttribute('aria-expanded', String(willOpen));
        showOnly(null);
      });

      for (const group of groups) {
        const summary = group.querySelector('summary');
        if (!summary) continue;

        group.addEventListener('pointerenter', (event) => {
          if (hoverMedia.matches && !isCompact() && event.pointerType !== 'touch') showOnly(group);
        });
        summary.addEventListener('click', (event) => {
          event.preventDefault();
          // On desktop, a click must not close the submenu just opened on hover.
          if (hoverMedia.matches && !isCompact() && event.detail !== 0) showOnly(group);
          else showOnly(group.open ? null : group);
        });
        group.addEventListener('toggle', () => {
          if (group.open) {
            for (const other of groups) {
              if (other !== group) other.open = false;
            }
            moveSurface(group);
          }
        });
      }

      for (const link of nav.querySelectorAll(':scope > a')) {
        link.addEventListener('pointerenter', (event) => {
          if (hoverMedia.matches && !isCompact() && event.pointerType !== 'touch') showOnly(null);
        });
      }

      nav.addEventListener('pointerleave', (event) => {
        if (hoverMedia.matches && !isCompact() && event.pointerType !== 'touch') showOnly(null);
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
        if (!shell?.contains(event.target)) {
          showOnly(null);
          closeCompact();
        }
      });
      document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        const opened = groups.find(group => group.open);
        if (!opened && !shell?.classList.contains('is-open')) return;
        event.preventDefault();
        if (isCompact()) {
          closeCompact(true);
        } else {
          opened?.querySelector('summary')?.focus();
          showOnly(null);
        }
      });
      shell?.addEventListener('focusout', (event) => {
        if (!event.relatedTarget || !shell.contains(event.relatedTarget)) closeCompact();
      });
      window.addEventListener('resize', () => {
        if (!isCompact()) closeCompact();
        moveSurface(groups.find(group => group.open));
      });
      hoverMedia.addEventListener?.('change', () => moveSurface(groups.find(group => group.open)));
    }
  });
})();
