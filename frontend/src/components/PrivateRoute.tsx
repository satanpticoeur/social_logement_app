import React from 'react';
import {Navigate} from 'react-router-dom';
import {toast} from 'sonner';
import {useAuth} from "@/context/AuthContext.tsx";

interface PrivateRouteProps {
    children: React.ReactNode;
    allowedRoles?: string[];
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({children, allowedRoles}) => {
    const {isAuthenticated, user} = useAuth();

    if (!isAuthenticated) {
        toast.error("Accès refusé", {
            description: "Veuillez vous connecter pour accéder à cette page.",
        });
        return <Navigate to="/login" replace/>;
    }

    if (allowedRoles && user && !allowedRoles.includes(user.role)) {
        toast.error("Permission refusée", {
            description: "Vous n'avez pas les autorisations nécessaires pour accéder à cette page.",
        });
        return <Navigate to="/" replace/>; // Redirige vers la page d'accueil ou une page d'erreur
    }

    return <>{children}</>;
};

export default PrivateRoute;