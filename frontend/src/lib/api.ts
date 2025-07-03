// frontend/src/lib/api.ts

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

// Fonction utilitaire pour récupérer le CSRF token d'un cookie (copie du AuthContext)
function getCsrfToken() {
    const name = "csrf_access_token";
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop()?.split(';').shift();
    }
    return null;
}

export async function authenticatedFetch(endpoint: string, options: RequestInit = {}) {
    const config: RequestInit = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string>), // Assure le type correct
        },
        credentials: 'include',
    };

    const method = options.method?.toUpperCase() || 'GET';
    // Ajoute le CSRF token pour les méthodes qui le nécessitent
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        const csrfToken = getCsrfToken();
        if (csrfToken) {
            // S'assure que headers est un objet mutable
            (config.headers as Record<string, string>)['X-CSRF-TOKEN'] = csrfToken;
        } else {
            console.warn(`CSRF token missing for ${method} request to ${endpoint}. This might cause an authentication error.`);
            // Optionnel: lancer une erreur ou gérer l'état d'authentification ici
        }
    }

    const response = await fetch(`${BACKEND_URL}/api/${endpoint}`, config);

    if (!response.ok) {
        // ... (gestion des erreurs, redirection si 401/403) ...
        const errorData = await response.json().catch(() => ({ message: `HTTP error! Status: ${response.status}` }));
        throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
    }

    return response.json();
}