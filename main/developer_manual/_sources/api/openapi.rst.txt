OCS OpenAPI — versioned contract
==================================

This page renders the OpenAPI definition **bundled with this exact
documentation version**, not the moving ``main`` branch. The application
commit and branch are recorded alongside the published JSON.

`Download this version's OpenAPI JSON <openapi.json>`_.

.. raw:: html

   <p id="libresign-openapi-provenance" aria-live="polite">Loading source revision…</p>
   <link rel="stylesheet" href="../swagger-ui/swagger-ui.css" />
   <script src="../swagger-ui/swagger-ui-bundle.js"></script>
   <script src="../swagger-ui/swagger-ui-standalone-preset.js"></script>
   <div id="swagger-ui"></div>
   <script>
      document.addEventListener("DOMContentLoaded", async () => {
         const source = document.getElementById("libresign-openapi-provenance");
         try {
            const response = await fetch("openapi.provenance.json");
            if (!response.ok) throw new Error("Provenance unavailable");
            const provenance = await response.json();
            source.replaceChildren();
            const lead = document.createTextNode(
               "LibreSign " + provenance.app_version +
               " · branch " + provenance.branch + " · source "
            );
            const link = document.createElement("a");
            link.href = provenance.source_url;
            link.textContent = provenance.app_commit;
            link.rel = "noopener noreferrer";
            source.append(lead, link);
         } catch (error) {
            source.textContent = "OpenAPI provenance unavailable; contract not verified.";
         }
         if (typeof SwaggerUIBundle !== "function") {
            source.append(document.createTextNode(" · Swagger UI could not load."));
            return;
         }
         SwaggerUIBundle({
            url: "openapi.json",
            dom_id: "#swagger-ui",
            deepLinking: true,
            presets: [
               SwaggerUIBundle.presets.apis,
               SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout"
         });
      });
   </script>
