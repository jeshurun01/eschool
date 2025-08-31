# eSchool - Système de Gestion Scolaire

eSchool est un système complet de gestion scolaire développé avec Django 5.2. Il permet de gérer tous les aspects d'un établissement scolaire : élèves, enseignants, notes, présences, finances, communication, etc.

## 🚀 Fonctionnalités Principales

### 👥 Gestion des Utilisateurs
- **Système d'authentification avancé** avec Django Allauth
- **Rôles multiples** : Élève, Parent, Enseignant, Administrateur, Personnel financier
- **Profils personnalisés** selon le rôle
- **Gestion des permissions** granulaire

### 🎓 Module Académique
- **Années scolaires** et périodes (trimestres/semestres)
- **Niveaux et classes** avec capacités
- **Matières** avec coefficients
- **Emplois du temps** interactifs
- **Gestion des présences** avec justifications
- **Système de notation** flexible
- **Bulletins de notes** automatisés

### 💰 Module Financier
- **Types de frais** configurables
- **Facturation automatisée**
- **Gestion des paiements** multi-méthodes
- **Système de bourses** avec demandes
- **Suivi des dépenses** de l'école
- **Gestion de la paie** du personnel
- **Rapports financiers** détaillés

### 💬 Module Communication
- **Annonces** ciblées par audience
- **Messagerie interne** individuelle et de groupe
- **Partage de ressources** pédagogiques
- **Système de notifications** en temps réel
- **Templates d'e-mails** personnalisables

## 🛠️ Technologies Utilisées

- **Backend** : Django 5.2.5, Python 3.12+
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **Frontend** : HTML5, Tailwind CSS, Alpine.js, HTMX
- **Authentification** : Django Allauth
- **API** : Django REST Framework
- **Gestionnaire de paquets** : uv
- **Cache** : Redis
- **Tâches asynchrones** : Celery
- **PDF** : ReportLab
- **Images** : Pillow

## 📋 Prérequis

- Python 3.12 ou supérieur
- uv (gestionnaire de paquets Python moderne)
- Redis (pour le cache et Celery)
- PostgreSQL (pour la production)

## 🚀 Installation

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd eschool
```

### 2. Initialiser l'environnement avec uv
```bash
# Créer l'environnement virtuel
uv venv

# Installer les dépendances
uv sync

# Installer les dépendances de développement
uv sync --extra dev
```

### 3. Configuration
```bash
# Copier le fichier d'environnement
cp .env.example .env

# Modifier les variables d'environnement selon vos besoins
nano .env
```

### 4. Base de données
```bash
# Créer les migrations
uv run python manage.py makemigrations

# Appliquer les migrations
uv run python manage.py migrate

# Créer un superutilisateur
uv run python manage.py createsuperuser
```

### 5. Démarrer le serveur
```bash
uv run python manage.py runserver
```

L'application sera accessible à l'adresse : http://127.0.0.1:8000

## 📁 Structure du Projet

```
eschool/
├── core/                   # Configuration principale Django
│   ├── settings.py        # Paramètres de l'application
│   ├── urls.py           # URLs principales
│   └── api_urls.py       # URLs de l'API REST
├── accounts/              # Gestion des utilisateurs
│   ├── models.py         # Modèles User, Student, Teacher, Parent
│   ├── views.py          # Vues de gestion des comptes
│   └── admin.py          # Interface d'administration
├── academic/              # Module académique
│   ├── models.py         # Classes, matières, notes, présences
│   ├── views.py          # Vues académiques
│   └── admin.py          # Administration académique
├── finance/               # Module financier
│   ├── models.py         # Factures, paiements, bourses
│   ├── views.py          # Vues financières
│   └── admin.py          # Administration financière
├── communication/         # Module communication
│   ├── models.py         # Messages, annonces, ressources
│   ├── views.py          # Vues communication
│   └── admin.py          # Administration communication
├── templates/             # Templates HTML
│   ├── base.html         # Template de base
│   └── accounts/         # Templates des comptes
├── static/               # Fichiers statiques (CSS, JS, images)
├── media/                # Fichiers médias uploadés
└── requirements files    # Dépendances (pyproject.toml, uv.lock)
```

## 🔧 Configuration

### Variables d'environnement (.env)

```ini
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
USE_POSTGRESQL=False
DB_NAME=eschool
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Internationalisation
LANGUAGE_CODE=fr
TIME_ZONE=Africa/Kinshasa

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

## 👤 Utilisateurs par Défaut

Après l'installation, vous pouvez créer des utilisateurs avec différents rôles :

- **Super Administrateur** : Accès complet au système
- **Administrateur** : Gestion de l'école
- **Personnel Financier** : Gestion des finances
- **Enseignant** : Gestion des classes et notes
- **Parent** : Suivi des enfants
- **Élève** : Consultation des notes et informations

## 🔐 Sécurité

- Authentification par e-mail obligatoire
- Vérification d'e-mail activée
- Système de permissions granulaire
- Protection CSRF activée
- Sécurisation des uploads de fichiers
- Hashage sécurisé des mots de passe

## 📊 Administration

L'interface d'administration Django est accessible à `/admin/` et permet :

- Gestion complète de tous les modèles
- Filtres et recherches avancées
- Actions en lot
- Export de données
- Logs d'activité

## 🔄 API REST

L'API REST est disponible à `/api/v1/` et fournit :

- Endpoints pour tous les modèles principaux
- Authentification par token
- Pagination automatique
- Filtres et tris
- Documentation automatique

## 🚀 Déploiement

### Production avec Docker
```bash
# À venir - Configuration Docker
```

### Variables de production
```bash
DEBUG=False
USE_POSTGRESQL=True
REDIS_URL=redis://your-redis-server:6379/1
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

## 🧪 Tests

```bash
# Lancer tous les tests
uv run pytest

# Tests avec couverture
uv run pytest --cov=.

# Tests d'une application spécifique
uv run pytest accounts/tests.py
```

## 📝 Développement

### Code Style
Le projet utilise :
- **Black** pour le formatage
- **isort** pour l'organisation des imports
- **flake8** pour le linting

```bash
# Formatter le code
uv run black .

# Organiser les imports
uv run isort .

# Vérifier le style
uv run flake8
```

### Contribuer

1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changes (`git commit -m 'Add AmazingFeature'`)
4. Poussez la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation
- Contactez l'équipe de développement

## 🎯 Roadmap

### Version 1.1
- [ ] Module de bibliothèque
- [ ] Gestion des événements
- [ ] Système de notifications push
- [ ] Application mobile (React Native)

### Version 1.2
- [ ] Modules de santé
- [ ] Gestion du transport scolaire
- [ ] Système de badges et récompenses
- [ ] Intégration avec des APIs externes

### Version 2.0
- [ ] Intelligence artificielle pour l'analyse des performances
- [ ] Système de recommandations personnalisées
- [ ] Tableaux de bord avancés avec analytics
- [ ] Intégration avec des plateformes d'apprentissage en ligne

---

Développé avec ❤️ pour moderniser la gestion scolaire en République Démocratique du Congo.
