import React from 'react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';

export const HomePage: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-64px)] py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200">

            {/* Section Hero - Inchangée, elle est déjà top ! */}
            <section className="text-center max-w-4xl mb-12">
                <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-gray-900 dark:text-white leading-tight">
                    Trouvez le Logement Idéal au Sénégal.
                </h1>
                <p className="mt-4 text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                    Simplifiez la gestion immobilière et la recherche de logement au Sénégal. Que vous soyez propriétaire ou locataire, notre plateforme est conçue pour vous.
                </p>
                <div className="mt-8 flex justify-center space-x-4">
                    <Link to="/rooms">
                        <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-md transition duration-300">
                            Découvrir les Chambres
                        </Button>
                    </Link>
                    <Link to="/dashboard"> {/* Ce lien mènera à l'espace propriétaire, à développer */}
                        <Button variant="outline" size="lg" className="border-blue-600 text-blue-600 hover:bg-blue-50 dark:hover:bg-gray-800 transition duration-300">
                            Espace Propriétaire
                        </Button>
                    </Link>
                </div>
            </section>

            {/* Nouvelle Section : Comment ça marche ? */}
            <section className="w-full max-w-6xl my-16 p-8 bg-white dark:bg-gray-800 rounded-lg shadow-xl">
                <h2 className="text-4xl font-bold text-center mb-12 text-gray-900 dark:text-white">
                    Comment ça marche ?
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
                    {/* Étape 1 */}
                    <div className="flex flex-col items-center text-center">
                        <div className="bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-200 rounded-full h-16 w-16 flex items-center justify-center text-3xl font-bold mb-4">
                            1
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Inscrivez-vous</h3>
                        <p className="text-gray-600 dark:text-gray-300">
                            Créez votre compte en quelques secondes, que vous cherchiez un logement ou que vous souhaitiez en proposer un.
                        </p>
                    </div>
                    {/* Étape 2 */}
                    <div className="flex flex-col items-center text-center">
                        <div className="bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-200 rounded-full h-16 w-16 flex items-center justify-center text-3xl font-bold mb-4">
                            2
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Trouvez ou Listez</h3>
                        <p className="text-gray-600 dark:text-gray-300">
                            Locataires : explorez des annonces détaillées. Propriétaires : listez vos biens facilement.
                        </p>
                    </div>
                    {/* Étape 3 */}
                    <div className="flex flex-col items-center text-center">
                        <div className="bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-200 rounded-full h-16 w-16 flex items-center justify-center text-3xl font-bold mb-4">
                            3
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Gérez ou Emménagez</h3>
                        <p className="text-gray-600 dark:text-gray-300">
                            Propriétaires : gérez contrats et paiements. Locataires : réservez et emménagez en toute sérénité.
                        </p>
                    </div>
                </div>
            </section>

            {/* Nouvelle Section : Bénéfices pour les Propriétaires */}
            <section className="w-full max-w-6xl my-16 p-8 bg-blue-50 dark:bg-blue-950 rounded-lg shadow-xl">
                <h2 className="text-4xl font-bold text-center mb-10 text-gray-900 dark:text-white">
                    Pour les Propriétaires
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                        <h3 className="text-xl font-semibold mb-2">Gestion Simplifiée</h3>
                        <p className="text-gray-600 dark:text-gray-300">
                            Suivez vos chambres, contrats et locataires depuis un tableau de bord intuitif.
                        </p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                        <h3 className="text-xl font-semibold mb-2">Suivi des Paiements</h3>
                        <p className="text-gray-600 dark:text-gray-300">
                            Visualisez facilement les paiements effectués et les impayés pour une gestion financière claire.
                        </p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                        <h3 className="text-xl font-semibold mb-2">Visibilité Accrue</h3>
                        <p className="text-gray-600 dark:text-gray-300">
                            Mettez en avant vos biens avec des descriptions riches et des photos/vidéos de haute qualité.
                        </p>
                    </div>
                </div>
                <div className="text-center mt-12">
                    <Link to="/dashboard">
                        <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg shadow-md transition duration-300">
                            Démarrez la Gestion de Vos Biens
                        </Button>
                    </Link>
                </div>
            </section>

            {/* Nouvelle Section : Bénéfices pour les Locataires */}
            <section className="w-full max-w-6xl my-16 p-8 bg-green-50 dark:bg-green-950 rounded-lg shadow-xl">
                <h2 className="text-4xl font-bold text-center mb-10 text-gray-900 dark:text-white">
                    Pour les Locataires
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                        <h3 className="text-xl font-semibold mb-2">Recherche Personnalisée</h3>
                        <p className="text-gray-600 dark:text-gray-300">
                            Filtrez par dimension, nature (meublée/non meublée), prix, et plus encore.
                        </p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                        <h3 className="text-xl font-semibold mb-2">Visites Faciles</h3>
                        <p className="text-gray-600 dark:text-gray-300">
                            Prenez rendez-vous directement en ligne pour visiter vos chambres favorites.
                        </p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                        <h3 className="text-xl font-semibold mb-2">Informations Complètes</h3>
                        <p className="text-gray-600 dark:text-gray-300">
                            Accédez aux photos, vidéos, descriptions détaillées et coordonnées des propriétaires.
                        </p>
                    </div>
                </div>
                <div className="text-center mt-12">
                    <Link to="/rooms">
                        <Button size="lg" className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-lg shadow-md transition duration-300">
                            Trouvez Votre Prochain Logement
                        </Button>
                    </Link>
                </div>
            </section>

            {/* Section Témoignages (Placeholder pour le futur) */}
            <section className="w-full max-w-6xl my-16 p-8 bg-white dark:bg-gray-800 rounded-lg shadow-xl text-center">
                <h2 className="text-4xl font-bold mb-10 text-gray-900 dark:text-white">
                    Ce que nos utilisateurs disent
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <blockquote className="p-6 bg-gray-50 dark:bg-gray-700 rounded-lg shadow">
                        <p className="text-lg italic text-gray-700 dark:text-gray-200">
                            "Grâce à Social Logement, j'ai trouvé ma chambre idéale en un rien de temps. Le processus était si simple !"
                        </p>
                        <footer className="mt-4 text-gray-800 dark:text-gray-100 font-semibold">- Fatou D., Locataire</footer>
                    </blockquote>
                    <blockquote className="p-6 bg-gray-50 dark:bg-gray-700 rounded-lg shadow">
                        <p className="text-lg italic text-gray-700 dark:text-gray-200">
                            "La gestion de mes biens n'a jamais été aussi facile. Le suivi des paiements est un vrai plus pour mon business."
                        </p>
                        <footer className="mt-4 text-gray-800 dark:text-gray-100 font-semibold">- Monsieur Sow, Propriétaire</footer>
                    </blockquote>
                </div>
            </section>

            {/* Ajoute un footer simple */}
            <footer className="w-full py-6 text-center text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 mt-12">
                <p>&copy; {new Date().getFullYear()} Social Logement. Tous droits réservés.</p>
            </footer>
        </div>
    );
};

