/* Version chooser for all Sphinx manuals. No main-branch fallback for stable URLs. */
(() => {
  "use strict";
  document.addEventListener("DOMContentLoaded", async () => {
    const picker = document.getElementById("libresign-version-select");
    if (!picker) return;
    const notice = document.getElementById("libresign-version-notice");
    const current = picker.closest("[data-version]")?.dataset.version || "main";

    // Read the deployed catalog: an independent release deployment must not
    // advertise unpublished revisions of other majors.
    try {
      const response = await fetch("/versions.json", {cache: "no-store"});
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
      // Server-rendered options remain usable without the catalog request.
    }

    picker.addEventListener("change", async () => {
      const wanted = picker.value;
      if (!/^(main|[1-9][0-9]*)$/.test(wanted)) return;
      const match = location.pathname.match(/^\/(main|[1-9][0-9]*)(\/.*)?$/);
      const suffix = match ? (match[2] || "/") : "/";
      const samePage = "/" + wanted + suffix;
      let destination = samePage;
      try {
        const response = await fetch(samePage, {method: "HEAD", cache: "no-store"});
        if (!response.ok) {
          const manual = suffix.match(/^\/(user_manual|admin_manual|developer_manual)\//);
          destination = "/" + wanted + (manual ? "/" + manual[1] + "/" : "/");
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
