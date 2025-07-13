import {useEffect} from "react";

export default function LodgerDashboardPage() {
    useEffect(() => {
        console.log("LodgerDashboardPage")
    }, []);
    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4">Tableau de bord du locataire</h1>
            <p>Bienvenue sur votre tableau de bord, où vous pouvez gérer vos contrats et paiements.</p>
        </div>
    );
}
