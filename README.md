# 🏡 Gestion des locations (API Flask + Frontend React)

Bienvenue dans l'application de Gestion des locations ! Ce projet est un MVP comprenant un backend API développé avec Flask et un frontend web interactif construit avec React. Il est conçu pour faciliter la gestion des propriétés, des locations, des contrats et des paiements pour les propriétaires et les locataires.

## Table des Matières

1.  [Aperçu du Projet](#1-aperçu-du-projet)
2.  [Fonctionnalités Clés](#2-fonctionnalités-clés)
3.  [Technologies Utilisées](#3-technologies-utilisées)
4.  [Configuration de l'Environnement](#4-configuration-de-lenvironnement)
    - [Prérequis](#prérequis)
    - [Installation](#installation)
    - [Configuration de la Base de Données](#configuration-de-la-base-de-données)
    - [Variables d'Environnement](#variables-denvironnement)
5.  [Lancement de l'Application](#5-lancement-de-l'application)

---

## 1. Aperçu du Projet

Ce projet est une plateforme de Gestion des locations, composée de :

- **Backend (API)** : Une API RESTful construite avec Flask, gérant la logique métier, la persistance des données (propriétés, chambres, utilisateurs, contrats, paiements, etc.) et l'authentification sécurisée via JWT.
- **Frontend (Application Web)** : Une interface utilisateur dynamique développée avec React, permettant aux utilisateurs d'interagir avec le backend, de visualiser les données et d'effectuer des opérations de Gestion des locations.

## 2. Fonctionnalités Clés

### Côté Locataire

- Recherche et consultation de chambres disponibles avec filtres avancés.
- Processus de location d'une chambre, incluant la génération automatique de contrats et d'échéanciers de paiement.
- Accès à ses contrats de location et suivi des paiements.
- Signalement de problèmes et suivi de leur résolution.
- Prise de rendez-vous pour visiter des chambres.

### Côté Propriétaire

- Gestion complète des propriétés (Maisons) : ajout, modification, suppression.
- Gestion des chambres associées à chaque propriété : ajout, modification, gestion de la disponibilité.
- Consultation des contrats de location de ses propriétés.
- Suivi et mise à jour des paiements des locataires.
- Gestion des rendez-vous de visite.
- Consultation et gestion des problèmes signalés par les locataires.

### Général

- Authentification utilisateur sécurisée (locataire, propriétaire).
- Navigation et affichage conditionnels basés sur les rôles utilisateur.

## 3. Technologies Utilisées

### Backend (API Flask)

- **Python 3.9+**
- **Flask**: Framework web.
- **Flask-SQLAlchemy**: ORM pour l'interaction avec la base de données.
- **Flask-JWT-Extended**: Gestion de l'authentification JWT.
- **Flask-Bcrypt**: Hashing des mots de passe.
- **python-dotenv**: Gestion des variables d'environnement.

### Frontend (React App)

- **Node.js (LTS recommandée)**
- **React.js**: Bibliothèque JavaScript pour la construction d'interfaces utilisateur.
- **Vite**: Outil de build rapide (alternative à Create React App).
- **React Router DOM**: Pour la navigation côté client.
- **Fetch API**: Pour les requêtes HTTP vers l'API backend.
- **NPM**: Gestionnaire de paquets.
- **Gestion d'état**: React Context API.
- **UI Framework**: Tailwind CSS .
- **Bibliothèque de composant**: Shadcn-UI & Origin-UI

### Base de Données

- **SQLite**: Base de données légère pour le développement local.

## 4. Configuration de l'Environnement

### Prérequis

- **Python 3.9+** (pour le backend)
- **Node.js (version 18 ou supérieure recommandée)** (pour le frontend)
- **npm** ou **Yarn** (pour le frontend)

### Installation

1.  **Clonez le dépôt du projet :**

    ```bash
    git clone <URL_DE_VOTRE_DEPOT_MONOREPO>
    cd <NOM_DU_DOSSIER_RACINE_DU_PROJET>
    ```

    _(Si votre projet est un monorepo avec le frontend et le backend dans des sous-dossiers, par exemple `backend/` et `frontend/`)_

2.  **Installation des dépendances du Backend :**

    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate   # Windows
    pip install -r requirements.txt
    cd .. # Retour à la racine du projet
    ```

3.  **Installation des dépendances du Frontend :**
    ```bash
    cd frontend
    npm install # ou yarn install
    cd .. # Retour à la racine du projet
    ```

### Configuration de la Base de Données

- **Pour SQLite (développement, backend) :**
  Aucune configuration supplémentaire n'est nécessaire si vous utilisez `SQLALCHEMY_DATABASE_URI="sqlite:///app.db"` par défaut dans votre `.env` backend. Le fichier sera créé automatiquement.

### Variables d'Environnement

Créez deux fichiers `.env` distincts :

1.  **`backend/.env`** (pour l'API Flask) :

    ```
    FLASK_APP=app
    FLASK_ENV=development  # Ou 'production'
    SECRET_KEY='votre_clé_secrète_backend_unique_et_forte'
    JWT_SECRET_KEY='votre_clé_secrète_jwt_backend_unique_et_forte'
    SQLALCHEMY_DATABASE_URI="sqlite:///app.db"
    ```

2.  **`frontend/.env`** (pour l'application React) :
    ```
    # URL de base de votre API Flask
    VITE_API_BASE_URL=http://localhost:5000/api
    # Ou pour la production:
    # VITE_API_BASE_URL=[https://api.votre-domaine.com/api](https://api.votre-domaine.com/api)
    ```
    _(Note: Si vous utilisez Create React App, le préfixe sera `REACT_APP_`au lieu de`VITE*`)*

**N'oubliez pas de remplacer toutes les valeurs des clés secrètes et les URL par vos propres configurations.**

## 5. Lancement de l'Application

Pour lancer l'application complète (backend et frontend) pour le développement :

1.  **Lancez le Backend (API Flask) :**
    Ouvrez un premier terminal à la racine de votre projet.

    ```bash
    cd backend
    source venv/bin/activate # ou venv\Scripts\activate pour Windows
    python # Entrez dans l'interpréteur Python
    >>> from app import db, create_app
    >>> app = create_app()
    >>> with app.app_context():
    ...     db.create_all() # Crée les tables si elles n'existent pas (première fois ou après modifications de modèles)
    # Quittez l'interpréteur Python (Ctrl+D sur Linux/macOS, Ctrl+Z puis Entrée sur Windows)
    flask run
    ```

    L'API sera accessible sur `http://127.0.0.1:5000`.

2.  **Lancez le Frontend (Application React) :**
    Ouvrez un second terminal à la racine de votre projet.
    ```bash
    cd frontend
    npm run dev # ou yarn dev
    ```
    L'application React sera accessible dans votre navigateur à l'adresse (généralement) : `http://localhost:5173`.

Vous avez maintenant votre backend API et votre frontend React en cours d'exécution, prêts pour le développement et les tests !
