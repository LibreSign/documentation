// SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
// SPDX-License-Identifier: CC-BY-3.0

(() => {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('.libresign-scroll-header');
    if (!header) return;

    const desktop = window.matchMedia('(min-width: 769px)');
    let previousY = Math.max(0, window.scrollY || 0);
    let distance = 0;

    const reveal = () => header.classList.remove('is-hidden');
    const update = () => {
      const currentY = Math.max(0, window.scrollY || 0);
      const step = currentY - previousY;
      previousY = currentY;
      header.classList.toggle('is-scrolled', currentY > 12);

      // Don't hide the navigation near the top or while it is being used.
      if (!desktop.matches || currentY < Math.max(160, header.offsetHeight * 1.5) ||
          header.contains(document.activeElement) ||
          header.querySelector('.libresign-nav-group[open], .libresign-nav-shell.is-open')) {
        distance = 0;
        reveal();
        return;
      }
      if (Math.abs(step) < 1) return;
      if (step * distance < 0) distance = 0;
      distance = Math.max(-100, Math.min(100, distance + step));

      if (distance >= 24) {
        header.classList.add('is-hidden');
        distance = 0;
      } else if (distance <= -18) {
        reveal();
        distance = 0;
      }
    };

    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    desktop.addEventListener?.('change', update);
    header.addEventListener('focusin', reveal);
    document.addEventListener('keydown', event => {
      if (['Tab', 'ArrowUp', 'ArrowDown', 'PageUp', 'Home', 'Escape'].includes(event.key)) {
        reveal();
      }
    });
    update();
  });
})();
