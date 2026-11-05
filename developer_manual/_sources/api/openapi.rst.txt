OCS OpenAPI
===========

.. raw:: html

   <link rel="stylesheet" href="/developer_manual/swagger-ui/swagger-ui.css" />
   <script src="/developer_manual/swagger-ui/swagger-ui-bundle.js"></script>
   <script src="/developer_manual/swagger-ui/swagger-ui-standalone-preset.js"></script>
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
