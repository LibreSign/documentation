/* Nextcloud-style footer version chooser for Sphinx and isolated PR previews. */
(() => {
  "use strict";

  document.addEventListener("DOMContentLoaded", async () => {
    const picker = document.getElementById("libresign-release-picker");
    const toggle = document.getElementById("libresign-version-toggle");
    const menu = document.getElementById("libresign-version-menu");
    const list = document.getElementById("libresign-version-list");
    const notice = document.getElementById("libresign-version-notice");
    if (!picker || !toggle || !menu || !list) return;

    const root = picker.dataset.siteRoot || "";
    const current = picker.dataset.version || "main";
    const manual = picker.dataset.manual || "main";
    const validSlug = slug => /^(main|[1-9][0-9]*)$/.test(slug);
    const landing = slug => root + "/" + slug + "/" +
      (manual === "main" ? "" : manual + "/");

    const setOpen = open => {
      menu.hidden = !open;
      picker.classList.toggle("shift-up", open);
      toggle.setAttribute("aria-expanded", String(open));
    };

    toggle.addEventListener("click", () => setOpen(menu.hidden));
    document.addEventListener("click", event => {
      if (!menu.hidden && !picker.contains(event.target)) setOpen(false);
    });
    document.addEventListener("keydown", event => {
      if (event.key === "Escape" && !menu.hidden) {
        setOpen(false);
        toggle.focus();
      }
    });

    // The HTML list is already usable without JavaScript. Refresh after
    // load so partial deployments also advertise newly published majors.
    try {
      const response = await fetch(root + "/versions.json", { cache: "no-store" });
      if (response.ok) {
        const catalog = await response.json();
        const versions = (catalog.versions || []).filter(entry => validSlug(entry.slug));
        const stable = versions.filter(entry => entry.slug !== "main" && entry.status !== "eol");
        const oldest = stable.length
          ? Math.min(...stable.map(entry => Number(entry.slug))).toString()
          : null;
        versions.sort((a, b) => {
          if (a.slug === "main") return -1;
          if (b.slug === "main") return 1;
          return Number(b.slug) - Number(a.slug);
        });
        const rows = [];
        for (const entry of versions) {
          const li = document.createElement("li");
          const link = document.createElement("a");
          const name = document.createElement("span");
          const detail = document.createElement("span");
          link.href = landing(entry.slug);
          link.dataset.versionTarget = entry.slug;
          if (entry.slug === current) link.setAttribute("aria-current", "true");
          name.className = "libresign-version-name";
          name.textContent = entry.slug === "main" ? "main" : "LibreSign " + entry.slug;
          detail.className = "libresign-version-detail";
          detail.textContent = entry.slug === "main" ? "Not released" :
            entry.status === "eol" ? "EOL" :
            entry.status === "current" ? "Latest stable" :
            entry.slug === oldest ? "Oldest documented" :
            "NC " + entry.nextcloud_min +
            (entry.nextcloud_max !== entry.nextcloud_min ? "–" + entry.nextcloud_max : "");
          link.append(name, detail);
          li.appendChild(link);
          rows.push(li);
        }
        if (rows.length) list.replaceChildren(...rows);
      }
    } catch (_) {
      // Server-rendered version links remain available offline.
    }

    list.addEventListener("click", async event => {
      const link = event.target.closest("[data-version-target]");
      if (!link) return;
      const wanted = link.dataset.versionTarget;
      if (!validSlug(wanted)) return;
      if (wanted === current) {
        event.preventDefault();
        setOpen(false);
        return;
      }
      event.preventDefault();
      const prefix = root + "/" + current;
      const suffix = location.pathname.startsWith(prefix + "/")
        ? location.pathname.slice(prefix.length)
        : "/";
      const exact = root + "/" + wanted + suffix;
      let destination = exact;
      try {
        const response = await fetch(exact, { method: "HEAD", cache: "no-store" });
        if (!response.ok) {
          destination = landing(wanted);
          if (notice) {
            notice.textContent = "This page is not available in that version. Opening the manual index.";
          }
        }
      } catch (_) {
        // A failed HEAD must not force navigation to main/ or another major.
        destination = landing(wanted);
      }
      location.assign(destination + location.search +
        (destination === exact ? location.hash : ""));
    });
  });
})();
