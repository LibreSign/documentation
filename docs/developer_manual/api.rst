API
===

.. autosummary::
   :toctree: generated

.. redoc::
   :spec-url: https://libresign.github.io/api/openapi.yaml
   :embed:

.. raw:: html

   <link rel="stylesheet" href="swagger-ui.css" />
   <script src="swagger-ui-bundle.js"></script>
   <script src="swagger-ui-standalone-preset.js"></script>
   <div id="swagger-ui"></div>
   <script>
      window.onload = () => {
         const ui = SwaggerUIBundle({
            url: 'https://raw.githubusercontent.com/LibreSign/libresign/refs/heads/main/openapi.json',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
               SwaggerUIBundle.presets.apis,
               SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
         });
      };
   </script>
