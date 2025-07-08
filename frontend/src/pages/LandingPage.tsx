import React from 'react';
import {Button} from '@/components/ui/button';
import {Link} from 'react-router-dom';

export const LandingPage: React.FC = () => {
    return (
        <>
            <div
                className="flex flex-col items-center justify-center min-h-[calc(100vh-64px)] py-12 px-4 sm:px-6 lg:px-8 bg-background text-foreground"> {/* Utilise bg-background et text-foreground */}

                {/* Section Hero */}
                <section className="text-center max-w-4xl mb-12">
                    <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-foreground leading-tight"> {/* Utilise text-foreground */}
                        Trouvez le Logement Idéal au Sénégal.
                    </h1>
                    <p className="mt-4 text-xl text-muted-foreground max-w-2xl mx-auto"> {/* Utilise text-muted-foreground */}
                        Simplifiez la gestion immobilière et la recherche de logement au Sénégal. Que vous soyez
                        propriétaire ou locataire, notre plateforme est conçue pour vous.
                    </p>
                    <div className="mt-8 flex justify-center space-x-4">
                        <Link to="/rooms">
                            {/* Les boutons par défaut de Shadcn UI utilisent déjà primary et primary-foreground */}
                            <Button size="lg"
                                    className="shadow-md transition duration-300"> {/* Supprime les classes de couleur manuelles */}
                                Découvrir les Chambres
                            </Button>
                        </Link>
                        <Link to="/owner/dashboard">
                            {/* Les boutons "outline" utilisent border et foreground */}
                            <Button variant="outline" size="lg"
                                    className="transition duration-300"> {/* Supprime les classes de couleur manuelles */}
                                Espace Propriétaire
                            </Button>
                        </Link>
                    </div>
                </section>

                {/* Section : Comment ça marche ? */}
                <section className="w-full max-w-6xl my-16 p-8 bg-card rounded-lg shadow-xl"> {/* Utilise bg-card */}
                    <h2 className="text-4xl font-bold text-center mb-12 text-foreground"> {/* Utilise text-foreground */}
                        Comment ça marche ?
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
                        {/* Étape 1 */}
                        <div className="flex flex-col items-center text-center">
                            <div
                                className="bg-primary/10 text-primary rounded-full h-16 w-16 flex items-center justify-center text-3xl font-bold mb-4"> {/* Utilise bg-primary/10 et text-primary */}
                                1
                            </div>
                            <h3 className="text-xl font-semibold mb-2">Inscrivez-vous</h3>
                            <p className="text-muted-foreground"> {/* Utilise text-muted-foreground */}
                                Créez votre compte en quelques secondes, que vous cherchiez un logement ou que vous
                                souhaitiez en proposer un.
                            </p>
                        </div>
                        {/* Étape 2 */}
                        <div className="flex flex-col items-center text-center">
                            <div
                                className="bg-primary/10 text-primary rounded-full h-16 w-16 flex items-center justify-center text-3xl font-bold mb-4">
                                2
                            </div>
                            <h3 className="text-xl font-semibold mb-2">Trouvez ou Listez</h3>
                            <p className="text-muted-foreground">
                                Locataires : explorez des annonces détaillées. Propriétaires : listez vos biens
                                facilement.
                            </p>
                        </div>
                        {/* Étape 3 */}
                        <div className="flex flex-col items-center text-center">
                            <div
                                className="bg-primary/10 text-primary rounded-full h-16 w-16 flex items-center justify-center text-3xl font-bold mb-4">
                                3
                            </div>
                            <h3 className="text-xl font-semibold mb-2">Gérez ou Emménagez</h3>
                            <p className="text-muted-foreground">
                                Propriétaires : gérez contrats et paiements. Locataires : réservez et emménagez en toute
                                sérénité.
                            </p>
                        </div>
                    </div>
                </section>

                {/* Section : Bénéfices pour les Propriétaires */}
                <section
                    className="w-full max-w-6xl my-16 p-8 bg-secondary rounded-lg shadow-xl"> {/* Utilise bg-secondary */}
                    <h2 className="text-4xl font-bold text-center mb-10 text-foreground">
                        Pour les Propriétaires
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        <div
                            className="bg-card p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300"> {/* Utilise bg-card */}
                            <h3 className="text-xl font-semibold mb-2">Gestion Simplifiée</h3>
                            <p className="text-muted-foreground">
                                Suivez vos chambres, contrats et locataires depuis un tableau de bord intuitif.
                            </p>
                        </div>
                        <div className="bg-card p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                            <h3 className="text-xl font-semibold mb-2">Suivi des Paiements</h3>
                            <p className="text-muted-foreground">
                                Visualisez facilement les paiements effectués et les impayés pour une gestion financière
                                claire.
                            </p>
                        </div>
                        <div className="bg-card p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                            <h3 className="text-xl font-semibold mb-2">Visibilité Accrue</h3>
                            <p className="text-muted-foreground">
                                Mettez en avant vos biens avec des descriptions riches et des photos/vidéos de haute
                                qualité.
                            </p>
                        </div>
                    </div>
                    <div className="text-center mt-12">
                        <Link to="/owner/dashboard">
                            <Button size="lg" className="shadow-md transition duration-300"> {/* Bouton par défaut */}
                                Démarrez la Gestion de Vos Biens
                            </Button>
                        </Link>
                    </div>
                </section>

                {/* Section : Bénéfices pour les Locataires */}
                <section
                    className="w-full max-w-6xl my-16 p-8 bg-secondary rounded-lg shadow-xl"> {/* Utilise bg-secondary */}
                    <h2 className="text-4xl font-bold text-center mb-10 text-foreground">
                        Pour les Locataires
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        <div
                            className="bg-card p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300"> {/* Utilise bg-card */}
                            <h3 className="text-xl font-semibold mb-2">Recherche Personnalisée</h3>
                            <p className="text-muted-foreground">
                                Filtrez par dimension, nature (meublée/non meublée), prix, et plus encore.
                            </p>
                        </div>
                        <div className="bg-card p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                            <h3 className="text-xl font-semibold mb-2">Visites Faciles</h3>
                            <p className="text-muted-foreground">
                                Prenez rendez-vous directement en ligne pour visiter vos chambres favorites.
                            </p>
                        </div>
                        <div className="bg-card p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300">
                            <h3 className="text-xl font-semibold mb-2">Informations Complètes</h3>
                            <p className="text-muted-foreground">
                                Accédez aux photos, vidéos, descriptions détaillées et coordonnées des propriétaires.
                            </p>
                        </div>
                    </div>
                    <div className="text-center mt-12">
                        <Link to="/rooms">
                            <Button size="lg" className="shadow-md transition duration-300"> {/* Bouton par défaut */}
                                Trouvez Votre Prochain Logement
                            </Button>
                        </Link>
                    </div>
                </section>

                {/* Section Témoignages */}
                <section
                    className="w-full max-w-6xl my-16 p-8 bg-card rounded-lg shadow-xl text-center"> {/* Utilise bg-card */}
                    <h2 className="text-4xl font-bold mb-10 text-foreground">
                        Ce que nos utilisateurs disent
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <blockquote className="p-6 bg-background rounded-lg shadow"> {/* Utilise bg-background */}
                            <p className="text-lg italic text-foreground">
                                "Grâce à Social Logement, j'ai trouvé ma chambre idéale en un rien de temps. Le
                                processus était si simple !"
                            </p>
                            <footer className="mt-4 text-foreground font-semibold">- Fatou D., Locataire</footer>
                        </blockquote>
                        <blockquote className="p-6 bg-background rounded-lg shadow">
                            <p className="text-lg italic text-foreground">
                                "La gestion de mes biens n'a jamais été aussi facile. Le suivi des paiements est un vrai
                                plus pour mon business."
                            </p>
                            <footer className="mt-4 text-foreground font-semibold">- Monsieur Sow, Propriétaire</footer>
                        </blockquote>
                    </div>
                </section>

                {/* Footer */}
                <footer
                    className="w-full py-6 text-center text-muted-foreground border-t border-border mt-12"> {/* Utilise text-muted-foreground et border-border */}
                    <p>&copy; {new Date().getFullYear()} Social Logement. Tous droits réservés.</p>
                </footer>
            </div>

        </>
    );
};
