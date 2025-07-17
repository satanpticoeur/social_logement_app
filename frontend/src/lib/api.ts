// frontend/src/lib/api.ts

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

// Fonction utilitaire pour récupérer le CSRF token d'un cookie
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
    // Crée une copie mutable des headers pour pouvoir les modifier
    const headers: HeadersInit = {
        ...(options.headers as Record<string, string>), // Fusionne les headers passés en options
    };

    // IMPORTANT : Ne PAS définir Content-Type si le corps est un FormData (upload de fichiers)
    // Le navigateur gérera automatiquement le Content-Type: multipart/form-data avec la boundary.
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const config: RequestInit = {
        ...options, // Conserve toutes les autres options (method, body, etc.)
        headers,    // Utilise les headers modifiés ci-dessus
        credentials: 'include', // Important pour les cookies et le CSRF
    };

    const method = options.method?.toUpperCase() || 'GET';
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        const csrfToken = getCsrfToken();
        if (csrfToken) {
            (config.headers as Record<string, string>)['X-CSRF-TOKEN'] = csrfToken;
        } else {
            console.warn(`CSRF token missing for ${method} request to ${endpoint}. This might cause an authentication error.`);
        }
    }

    // Assurez-vous que l'URL est correcte, incluant '/api/'
    const response = await fetch(`${BACKEND_URL}/api/${endpoint}`, config);

    if (!response.ok) {
        let errorData: any;
        try {
            errorData = await response.json();
        } catch {
            // Si la réponse n'est pas un JSON (ex: erreur HTML du serveur), fournir un message générique
            errorData = {message: `Erreur HTTP! Statut: ${response.status}`};
        }
        // Pour les erreurs 401/403, vous pouvez ajouter une logique de redirection ici si nécessaire
        // if (response.status === 401 || response.status === 403) {
        //     // Redirection vers la page de connexion ou gestion de la déconnexion
        //     // Exemple: window.location.href = '/login';
        // }
        throw new Error(errorData.message || `Erreur HTTP! Statut: ${response.status}`);
    }

    // Gère la réponse 204 No Content
    if (response.status === 204) {
        return null; // Retourne null pour indiquer qu'il n'y a pas de contenu
    }

    // Tente de parser la réponse comme JSON pour les autres statuts OK (200, 201, etc.)
    try {
        return await response.json();
    } catch (e) {
        console.error('Erreur de parsing JSON pour l\'URL:', `${BACKEND_URL}/api/${endpoint}`, e);
        throw new Error('La réponse du serveur n\'est pas un JSON valide.');
    }
}