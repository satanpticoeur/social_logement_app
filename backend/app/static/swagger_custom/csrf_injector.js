(function () {
    function getCookie() {
        const name = "csrf_access_token";
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop()?.split(';').shift();
        }
        return null;
    }

    const csrfCookieName = 'csrf_access_token';
    const csrfHeaderName = 'X-CSRF-TOKEN';
    const csrfToken = getCookie();

    const CustomCsrfPlugin = () => ({
        requestInterceptor: (request) => {
            if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(request.method.toUpperCase())) {
                const csrfToken = getCookie();
                if (csrfToken && !request.headers[csrfHeaderName]) {
                    request.headers[csrfHeaderName] = csrfToken;
                    console.log(`[CSRF Plugin] Injected ${csrfHeaderName}: ${csrfToken}`);
                } else {
                    console.warn('[CSRF Plugin] Token CSRF manquant ou déjà présent');
                }
            }

            // 🔥 Obligatoire pour que le cookie soit réellement envoyé
            request.withCredentials = true;

            return request;
        }
    });


    // Attente que SwaggerUIBundle soit chargé
    const intervalId = setInterval(() => {
        if (typeof SwaggerUIBundle !== 'undefined') {
            clearInterval(intervalId);

            SwaggerUIBundle({
                url: "/api/swagger.json", // Adapté à ton app Flask
                dom_id: "#swagger-ui",
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [CustomCsrfPlugin],
                layout: "StandaloneLayout",
                requestInterceptor: (request) => {
                    request.withCredentials = true;
                    return request;
                },

            });

            console.log('[Swagger CSRF] Swagger UI initialized with CSRF plugin.');
        }
    }, 100);
})();
