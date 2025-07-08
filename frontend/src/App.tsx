import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from "@/context/AuthContext.tsx";
import { AppRoutes } from '@/routes/AppRoutes.tsx'; // Importez votre nouveau fichier de routes

function App() {
    return (
        <Router>
            <AuthProvider>
                <main className="container mx-auto p-4">
                    <AppRoutes />
                </main>
            </AuthProvider>
        </Router>
    );
}

export default App;