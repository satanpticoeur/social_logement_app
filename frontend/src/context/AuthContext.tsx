import {createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState} from 'react';
import {toast} from 'sonner';
import {useNavigate} from 'react-router-dom';

interface User {
    id: number;
    nom_utilisateur: string;
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
    register: (userData: Record<string, unknown>) => Promise<boolean>;
    logout: () => Promise<void>;
    checkAuthStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

function getCsrfToken() {
    const name = "csrf_access_token";
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop()?.split(';').shift();
    }
    return null;
}

export const AuthProvider = ({children}: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loadingAuth, setLoadingAuth] = useState<boolean>(true);
    const navigate = useNavigate();

    const checkAuthStatus = useCallback(async () => {
        setLoadingAuth(true);
        try {
            const response = await fetch(`${BACKEND_URL}/api/auth/protected`, {
                method: 'GET',
                credentials: 'include',
            });


            if (response.ok) {
                const data = await response.json();
                setUser({id: data.user_id, nom_utilisateur: data.nom_utilisateur, role: data.role, email: data.email});

                if (window.location.pathname === '/login' || window.location.pathname === '/register') {
                    if (data.role === 'locataire') {
                        navigate('/locataire/dashboard');
                    } else if (data.role === 'proprietaire') {
                        navigate('/owner/dashboard');
                    } else if (data.role === 'admin') {
                        navigate('/admin/dashboard');
                    } else {
                        navigate('/');
                    }
                }
            } else if (response.status === 401 || response.status === 403) {
                setUser(null);
            } else {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
        } catch (error: unknown) {
            console.error("Erreur lors de la vérification de l'auth:", error);
            setUser(null);
        } finally {
            setLoadingAuth(false);
        }
    }, []);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const login = useCallback(async (email: string, password: string) => {
        try {
            const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, mot_de_passe: password}),
                credentials: 'include',
            });


            const data = await response.json();

            if (response.ok) {
                setUser({id: data.user_id, nom_utilisateur: data.nom_utilisateur, role: data.role, email: data.email});
                toast.success("Connexion réussie", {description: `Bienvenue, ${data.role} !`});
                if (data.role === 'locataire') {
                    return navigate('/lodger/dashboard');
                } else if (data.role === 'proprietaire') {
                    return navigate('/owner/dashboard');
                }else {
                    return navigate('/');
                }
            } else {
                throw new Error(data.message || "Erreur lors de la connexion.");
            }
        } catch (error: unknown) {
            console.error("Erreur login:", error);
            const errorMessage = error instanceof Error ? error.message : "Une erreur inattendue est survenue.";
            toast.error("Échec de la connexion", {description: errorMessage});
            throw error;
        }
    }, [navigate]);

    const register = useCallback(async (userData: Record<string, unknown>): Promise<boolean> => {
        try {
            const csrfToken = getCsrfToken();
            const headers: HeadersInit = {'Content-Type': 'application/json'};
            if (csrfToken) {
                headers['X-CSRF-TOKEN'] = csrfToken;
            }

            const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(userData),
                credentials: 'include',
            });

            const data = await response.json();
            if (response.ok) {
                toast.success("Inscription réussie", {description: data.message});
                return true;
            } else {
                throw new Error(data.message || "Une erreur est survenue lors de l'inscription.");
            }
        } catch (error: unknown) {
            console.error("Erreur inscription:", error);
            const errorMessage = error instanceof Error ? error.message : "Une erreur inattendue est survenue.";
            toast.error("Échec de l'inscription", {description: errorMessage});
            return false;
        }
    }, []);

    const logout = useCallback(async () => {
        try {
            const csrfToken = getCsrfToken();
            const headers: HeadersInit = {};
            if (csrfToken) {
                headers['X-CSRF-TOKEN'] = csrfToken;
            }

            const response = await fetch(`${BACKEND_URL}/api/auth/logout`, {
                method: 'POST',
                headers: headers,
                credentials: 'include',
            });

            if (response.ok) {
                setUser(null);
                toast.info("Déconnexion", {description: "Vous avez été déconnecté."});
                navigate('/login');
            } else {
                throw new Error("Échec de la déconnexion.");
            }
        } catch (error: unknown) {
            console.error("Erreur logout:", error);
            const errorMessage = error instanceof Error ? error.message : "Une erreur inattendue est survenue.";
            toast.error("Erreur de déconnexion", {description: errorMessage});
        }
    }, [navigate]);

    const isAuthenticated = !!user;
    const isAdmin = user?.role === 'admin';
    const isProprietaire = user?.role === 'proprietaire';
    const isLocataire = user?.role === 'locataire';

    const authContextValue = useMemo(() => ({
        user,
        isAuthenticated,
        isAdmin,
        isProprietaire,
        isLocataire,
        login,
        register,
        logout,
        checkAuthStatus
    }), [user, isAuthenticated, isAdmin, isProprietaire, isLocataire, login, register, logout, checkAuthStatus]); // Dépendances importantes


    if (loadingAuth) {
        return <div className="flex justify-center items-center h-screen text-lg">Chargement de
            l'authentification...</div>;
    }

    return (
        <AuthContext.Provider value={authContextValue}>
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