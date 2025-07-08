import React, {useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {useAuth} from "@/context/AuthContext.tsx";


const RegisterPage: React.FC = () => {
    const [username, setUsername] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [phone, setPhone] = useState<string>('');
    const [cni, setCni] = useState<string>('');
    const [role, setRole] = useState<string>('locataire');
    const [loading, setLoading] = useState<boolean>(false);
    const navigate = useNavigate();
    const {register} = useAuth(); // Utilise la fonction register du contexte

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        const userData = {
            nom_utilisateur: username,
            email,
            mot_de_passe: password,
            telephone: phone || null,
            cni: cni || null,
            role,
        };

        try {
            const success = await register(userData); // Appel à la fonction register du contexte
            if (success) {
                navigate('/login'); // Redirige si l'inscription a réussi
            }
        } catch (error) {
            console.error("Register component error:", error); // Log d'erreur pour le débogage
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-[calc(100vh-64px)] p-4">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold">Inscription</CardTitle>
                    <CardDescription>Créez votre compte pour commencer</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleRegister} className="grid gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="username">Nom d'utilisateur</Label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Votre nom d'utilisateur"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
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
                        <div className="grid gap-2">
                            <Label htmlFor="phone">Téléphone (Optionnel)</Label>
                            <Input
                                id="phone"
                                type="tel"
                                placeholder="Votre numéro de téléphone"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="cni">CNI (Optionnel)</Label>
                            <Input
                                id="cni"
                                type="text"
                                placeholder="Numéro de CNI"
                                value={cni}
                                onChange={(e) => setCni(e.target.value)}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="role">Je suis un(e)</Label>
                            <Select value={role} onValueChange={setRole}>
                                <SelectTrigger id="role">
                                    <SelectValue placeholder="Sélectionnez un rôle"/>
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="locataire">Locataire</SelectItem>
                                    <SelectItem value="proprietaire">Propriétaire</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? "Inscription en cours..." : "S'inscrire"}
                        </Button>
                    </form>
                    <div className="mt-4 text-center text-sm">
                        Vous avez déjà un compte ?{' '}
                        <Link to="/login" className="underline">
                            Connectez-vous
                        </Link>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default RegisterPage;