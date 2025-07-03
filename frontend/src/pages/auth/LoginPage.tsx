// frontend/src/pages/LoginPage.tsx

import React, { useState } from 'react';
import { Link } from 'react-router-dom'; // Retiré useNavigate car le contexte le gère
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/context/AuthContext';

const LoginPage: React.FC = () => {
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);
    const { login } = useAuth(); // Utilise la fonction login du contexte

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await login(email, password); // Appel à la fonction login du contexte
            // La redirection est gérée dans le contexte
        } catch (error) {
            // L'erreur est déjà toastée dans le contexte
            console.error("Login component error:", error); // Log d'erreur pour le débogage
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-[calc(100vh-64px)] p-4">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold">Connexion</CardTitle>
                    <CardDescription>Connectez-vous à votre compte</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleLogin} className="grid gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="votre@email.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="password">Mot de passe</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="********"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? "Connexion en cours..." : "Se connecter"}
                        </Button>
                    </form>
                    <div className="mt-4 text-center text-sm">
                        Vous n'avez pas de compte ?{' '}
                        <Link to="/register" className="underline">
                            Inscrivez-vous
                        </Link>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default LoginPage;