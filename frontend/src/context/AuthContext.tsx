// frontend/src/context/AuthContext.tsx

import { createContext, useState, useContext, type ReactNode, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

interface User {
    id: number;
    role: string;
    email: string;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isAdmin: boolean;
    isProprietaire: boolean;
    isLocataire: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (userData: any) => Promise<boolean>; // Ajout de la fonction register
    logout: () => Promise<void>;
    checkAuthStatus: () => Promise<void>; // Pour vérifier le statut d'authentification au chargement
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

function getCsrfToken() {
    const name = "csrf_access_token"; // C'est le nom par défaut du cookie CSRF de Flask-JWT-Extended
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        const token = parts.pop()?.split(';').shift();
        console.log("DEBUG: CSRF Token found in cookie:", token); // Pour débogage
        return token;
    }
    return null;
}


export const AuthProvider = ({ children }: { children:ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loadingAuth, setLoadingAuth] = useState<boolean>(true);
    const navigate = useNavigate();

    const checkAuthStatus = useCallback(async () => {
        setLoadingAuth(true);
        try {
            const response = await fetch(`${BACKEND_URL}/api/protected`, {
                method: 'GET',
                credentials: 'include', // <--- ASSUREZ-VOUS QUE C'EST BIEN LÀ !
            });

            console.log("CheckAuthStatus response:", response); // Log pour débogage

            if (response.ok) {
                const data = await response.json();
                // Assurez-vous que le backend renvoie bien user_id, role, email ici
                setUser({ id: data.user_id, role: data.role, email: data.email }); // Mettez à jour le user state
            } else if (response.status === 401 || response.status === 403) {
                setUser(null);
                console.log("Non authentifié ou session expirée.");
            } else {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
        } catch (error) {
            console.error("Erreur lors de la vérification de l'auth:", error);
            setUser(null);
        } finally {
            setLoadingAuth(false);
        }
    }, []);

    useEffect(() => {
        checkAuthStatus();
    }, [checkAuthStatus]);

    const login = async (email: string, password: string) => {
        try {
            const response = await fetch(`${BACKEND_URL}/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, mot_de_passe: password }),
                credentials: 'include',
            });

            console.log("Login response:", response); // Ce log est toujours utile

            const data = await response.json();

            if (response.ok) {
                setUser({ id: data.user_id, role: data.role, email: data.email });
                toast.success("Connexion réussie", { description: `Bienvenue, ${data.role} !` });
                navigate('/');
            } else {
                throw new Error(data.message || "Erreur lors de la connexion.");
            }
        } catch (error: any) {
            console.error("Erreur login:", error);
            toast.error("Échec de la connexion", { description: error.message || "Une erreur inattendue est survenue." });
            throw error;
        }
    };

    const register = async (userData: any): Promise<boolean> => {
        try {
            const csrfToken = getCsrfToken(); // Récupère le CSRF token
            const headers: HeadersInit = { 'Content-Type': 'application/json' };
            if (csrfToken) {
                headers['X-CSRF-TOKEN'] = csrfToken; // Ajoute l'en-tête CSRF
            }

            const response = await fetch(`${BACKEND_URL}/api/register`, {
                method: 'POST',
                headers: headers, // Utilisez les en-têtes avec le CSRF
                body: JSON.stringify(userData),
                credentials: 'include',
            });

            const data = await response.json();
            if (response.ok) {
                toast.success("Inscription réussie", { description: data.message });
                return true;
            } else {
                throw new Error(data.message || "Une erreur est survenue lors de l'inscription.");
            }
        } catch (error: any) {
            console.error("Erreur inscription:", error);
            toast.error("Échec de l'inscription", { description: error.message || "Une erreur inattendue est survenue." });
            return false;
        }
    };

    const logout = async () => {
        try {
            const csrfToken = getCsrfToken(); // Récupère le CSRF token pour le logout
            const headers: HeadersInit = {};
            if (csrfToken) {
                headers['X-CSRF-TOKEN'] = csrfToken;
            }

            const response = await fetch(`${BACKEND_URL}/api/logout`, {
                method: 'POST',
                headers: headers, // Ajoute l'en-tête CSRF
                credentials: 'include',
            });

            if (response.ok) {
                setUser(null);
                toast.info("Déconnexion", { description: "Vous avez été déconnecté." });
                navigate('/login');
            } else {
                throw new Error("Échec de la déconnexion.");
            }
        } catch (error: any) {
            console.error("Erreur logout:", error);
            toast.error("Erreur de déconnexion", { description: error.message || "Une erreur inattendue est survenue." });
        }
    };

    const isAuthenticated = !!user;
    const isAdmin = user?.role === 'admin';
    const isProprietaire = user?.role === 'proprietaire';
    const isLocataire = user?.role === 'locataire';

    if (loadingAuth) {
        return <div className="flex justify-center items-center h-screen text-lg">Chargement de l'authentification...</div>;
    }

    return (
        <AuthContext.Provider value={{ user, isAuthenticated, isAdmin, isProprietaire, isLocataire, login, register, logout, checkAuthStatus }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};