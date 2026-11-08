/* Version chooser for all Sphinx manuals; safe in production and PR previews. */
(() => {
  "use strict";
  document.addEventListener("DOMContentLoaded", async () => {
    const picker = document.getElementById("libresign-version-select");
    if (!picker) return;
    const wrapper = picker.closest("[data-version]");
    const current = wrapper?.dataset.version || "main";
    const root = wrapper?.dataset.siteRoot || "";
    const notice = document.getElementById("libresign-version-notice");

    // The catalog and all versions must stay inside the same preview, if any.
    try {
      const response = await fetch(root + "/versions.json", { cache: "no-store" });
      if (response.ok) {
        const catalog = await response.json();
        picker.replaceChildren();
        for (const entry of catalog.versions || []) {
          const option = document.createElement("option");
          option.value = entry.slug;
          if (entry.slug === "main") {
            option.textContent = "main (development)";
          } else {
            let label = "LibreSign " + entry.slug + " / Nextcloud " + entry.nextcloud_min;
            if (entry.nextcloud_max !== entry.nextcloud_min) label += "-" + entry.nextcloud_max;
            if (entry.status === "eol") label += " (EOL)";
            if (entry.status === "current") label += " (current)";
            option.textContent = label;
          }
          picker.appendChild(option);
        }
        picker.value = current;
      }
    } catch (_) {
      // Keep the server-rendered options if the catalog request fails.
    }

    picker.addEventListener("change", async () => {
      const wanted = picker.value;
      if (!/^(main|[1-9][0-9]*)$/.test(wanted)) return;
      const currentPrefix = root + "/" + current;
      const suffix = location.pathname.startsWith(currentPrefix + "/")
        ? location.pathname.slice(currentPrefix.length)
        : "/";
      const samePage = root + "/" + wanted + suffix;
      let destination = samePage;
      try {
        const response = await fetch(samePage, { method: "HEAD", cache: "no-store" });
        if (!response.ok) {
          const manual = suffix.match(/^\/(user_manual|admin_manual|developer_manual)\//);
          destination = root + "/" + wanted + (manual ? "/" + manual[1] + "/" : "/");
          if (notice) {
            notice.textContent = "This page is unavailable in that release. Opening its manual index.";
          }
        }
      } catch (_) {
        // The origin may not support HEAD; keep the exact target in that case.
      }
      location.assign(destination + location.search + location.hash);
    });
  });
})();
