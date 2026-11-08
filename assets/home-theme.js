/* Keep the homepage theme in sync with sphinx_rtd_dark_mode manual pages.
 * Both use localStorage.theme with values "light" or "dark".
 * The internal Sphinx theme defaults to dark until the user chooses light.
 */
(() => {
  "use strict";

  const preference = () => {
    try {
      const saved = localStorage.getItem("theme");
      if (saved === null) {
        localStorage.setItem("theme", "dark");
        return "dark";
      }
      return saved === "dark" ? "dark" : "light";
    } catch (_) {
      // Browsers that block storage can still switch during this page view.
      return "dark";
    }
  };

  // Runs in <head> before the stylesheet to prevent a light/dark flash.
  document.documentElement.setAttribute("data-theme", preference());

  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("themeSwitcher");
    if (!toggle) return;
    toggle.hidden = false;

    const sync = () => {
      const dark = document.documentElement.getAttribute("data-theme") === "dark";
      toggle.setAttribute("aria-pressed", String(dark));
      toggle.title = dark ? "Switch to light mode" : "Switch to dark mode";
    };

    sync();
    toggle.addEventListener("click", () => {
      const dark = document.documentElement.getAttribute("data-theme") === "dark";
      const next = dark ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try {
        localStorage.setItem("theme", next);
      } catch (_) {
        // Keep the on-page state usable without browser storage.
      }
      sync();
    });
  });
})();
